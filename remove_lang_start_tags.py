import os
import re
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description='Remove tags from tag_match files based on removal log')
parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
args = parser.parse_args()

DRY_RUN = args.dry_run

if DRY_RUN:
    print("=== DRY RUN MODE - No files will be modified ===\n")

# Parse the log file to get dialogue numbers and their source files
log_path = "/workspace/multilingual_fun_lines/start_removed.txt"

# Store: {filepath: [dialogue_nums]}
removals = {}

with open(log_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse entries like: "Dialogue 309 (file line 323) in /path/to/file.txt"
pattern = r'Dialogue (\d+) \(file line \d+\) in ([^\n]+)'
for match in re.finditer(pattern, content):
    dialogue_num = match.group(1)
    filepath = match.group(2).strip()
    
    if filepath not in removals:
        removals[filepath] = []
    removals[filepath].append(dialogue_num)

print(f"Found {sum(len(v) for v in removals.values())} dialogue removals across {len(removals)} files")

def get_tag_match_path(source_path):
    """Find the corresponding tag_match file"""
    directory = os.path.dirname(source_path)
    filename = os.path.basename(source_path)
    
    # Skip if this is already a tag_match file
    if '_tag_match_' in filename:
        return None
    
    # Skip English files (no translated tags)
    if '/english_' in source_path:
        return None
    
    if not os.path.exists(directory):
        return None
    
    # Determine if source is numbered or not
    is_numbered = filename.endswith('_lines_numbered.txt')
    
    # Get the base name pattern
    # e.g., new_order_fr_f_lines_numbered.txt -> new_order, fr_f
    if is_numbered:
        # new_order_fr_f_lines_numbered.txt
        base = filename[:-len('_lines_numbered.txt')]
    else:
        # new_order_fr_f_lines.txt
        base = filename[:-len('_lines.txt')]
    
    # Search for matching tag_match file
    for f in os.listdir(directory):
        # Skip annotated files
        if '_annotated.txt' in f:
            continue
            
        if '_tag_match_' not in f:
            continue
        
        # Match the numbered/non-numbered suffix
        if is_numbered and not f.endswith('_lines_numbered.txt'):
            continue
        if not is_numbered and not f.endswith('_lines.txt'):
            continue
        if not is_numbered and f.endswith('_lines_numbered.txt'):
            continue
        
        # Check if this is the right content match
        # new_order_tag_match_fr_f_lines_numbered.txt -> new_order_fr_f (with _tag_match removed)
        if is_numbered:
            tag_match_base = f[:-len('_lines_numbered.txt')]
        else:
            tag_match_base = f[:-len('_lines.txt')]
        
        # Remove _tag_match to compare
        tag_match_base_clean = tag_match_base.replace('_tag_match', '')
        
        if tag_match_base_clean == base:
            return os.path.join(directory, f)
    
    return None

def remove_start_tag_from_line(line):
    """Remove any tag at the start of a numbered line: '309. [anything] Text' -> '309. Text'"""
    pattern = r'^(\d+)\.\s*\[[^\]]+\]\s*'
    return re.sub(pattern, r'\1. ', line)

# Process each tag_match file
modified_files = 0
total_tags_removed = 0
removal_log = []
skipped_english = 0
skipped_tag_match = 0
not_found = []

for source_path, dialogue_nums in removals.items():
    # Skip English files
    if '/english_' in source_path:
        skipped_english += 1
        continue
    
    # Skip if already a tag_match file
    if '_tag_match_' in source_path:
        skipped_tag_match += 1
        continue
    
    tag_match_path = get_tag_match_path(source_path)
    
    if not tag_match_path:
        not_found.append(source_path)
        continue
    
    if not os.path.exists(tag_match_path):
        not_found.append(f"{source_path} -> {tag_match_path}")
        continue
    
    # Read the tag_match file
    with open(tag_match_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Convert dialogue nums to set for fast lookup
    target_nums = set(dialogue_nums)
    
    modified = False
    new_lines = []
    
    for line in lines:
        original_line = line
        # Check if this line starts with a target dialogue number
        line_match = re.match(r'^(\d+)\.', line)
        if line_match and line_match.group(1) in target_nums:
            new_line = remove_start_tag_from_line(line)
            if new_line != line:
                # Extract the removed tag for logging
                tag_match = re.match(r'^\d+\.\s*\[([^\]]+)\]', line)
                removed_tag = tag_match.group(1) if tag_match else "unknown"
                removal_log.append({
                    'dialogue_num': line_match.group(1),
                    'filepath': tag_match_path,
                    'tag': removed_tag,
                    'original': line.strip(),
                    'new': new_line.strip()
                })
                total_tags_removed += 1
                modified = True
                line = new_line
        new_lines.append(line)
    
    if modified:
        if not DRY_RUN:
            with open(tag_match_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        modified_files += 1
        prefix = "[DRY RUN] Would modify" if DRY_RUN else "Modified"
        print(f"{prefix}: {tag_match_path}")

# Print skipped/not found info
if skipped_english:
    print(f"\nSkipped {skipped_english} English files (no translated tags)")
if skipped_tag_match:
    print(f"Skipped {skipped_tag_match} files that were already tag_match files")
if not_found:
    print(f"\nCould not find tag_match for {len(not_found)} files:")
    for p in not_found[:10]:
        print(f"  {p}")
    if len(not_found) > 10:
        print(f"  ... and {len(not_found) - 10} more")

# Print dry run details
if DRY_RUN and removal_log:
    print("\n=== Changes that would be made ===\n")
    for entry in removal_log[:20]:
        print(f"Dialogue {entry['dialogue_num']} in {entry['filepath']}")
        print(f"  Remove: [{entry['tag']}]")
        print(f"  Before: {entry['original']}")
        print(f"  After:  {entry['new']}\n")
    if len(removal_log) > 20:
        print(f"... and {len(removal_log) - 20} more changes")

# Save log (only if not dry run)
output_log_path = "/workspace/multilingual_fun_lines/tag_match_removed.txt"
if not DRY_RUN and removal_log:
    with open(output_log_path, 'w', encoding='utf-8') as f:
        f.write(f"# Removed {total_tags_removed} tags from tag_match files\n")
        f.write(f"# Based on removals logged in: {log_path}\n\n")
        
        for entry in removal_log:
            f.write(f"Dialogue {entry['dialogue_num']} in {entry['filepath']}\n")
            f.write(f"  Tag: [{entry['tag']}]\n")
            f.write(f"  Original: {entry['original']}\n\n")

# Summary
print(f"\n{'=== DRY RUN SUMMARY ===' if DRY_RUN else '=== SUMMARY ==='}")
action = "Would modify" if DRY_RUN else "Modified"
print(f"{action} {modified_files} tag_match files")
print(f"{'Would remove' if DRY_RUN else 'Removed'} {total_tags_removed} tags total")
if not DRY_RUN and removal_log:
    print(f"Log saved to: {output_log_path}")
elif DRY_RUN:
    print(f"\nRun without --dry-run to apply changes")