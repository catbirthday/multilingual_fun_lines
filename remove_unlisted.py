#!/usr/bin/env python3
"""
Remove tags at end of lines that are NOT in the allowed list.
Logs all removals to address_number_removed_tags_end.txt

Searches files matching:
  - /workspace/multilingual_fun_lines/actor_lines/english_{I}/new_order_en_{I}_lines_numbered.txt
  - /workspace/multilingual_fun_lines/actor_lines/french_female_2/new_order_fr_f_lines_numbered.txt
  - Similar patterns (numbered.txt but NOT tag_match)
"""

import re
import glob
import os
from collections import defaultdict

# Allowed tags list
ALLOWED_TAGS = {
    "[sighs]", "[exhales]", "[sigh]", "[shaky exhale]", "[exhales heavily]",
    "[soft exhale]", "[sighs heavily]", "[shaky breath]", "[frustrated exhale]",
    "[long exhale]", "[nervous exhale]", "[sharp inhale]", "[exhales sharply]",
    "[sharp exhale]", "[incredulous exhale]", "[heavy sigh]", "[exhales slowly]",
    "[exhales with relief]", "[amused exhale]", "[impressed exhale]", "[heavy exhale]",
    "[hopeful exhale]", "[steadying breath]", "[quiet exhale]", "[measured exhale]",
    "[deep exhale]", "[defeated exhale]", "[dismissive exhale]", "[defensive exhale]",
    "[soft sigh]", "[bitter sigh]", "[labored breathing]", "[resigned sigh]",
    "[peaceful sigh]", "[bitter laugh]", "[nervous laugh]", "[hollow laugh]",
    "[chuckles]", "[laughs]", "[soft chuckle]", "[laugh]", "[soft laugh]",
    "[chuckles softly]", "[laugh loudly]", "[laughs bitterly]", "[chuckle]",
    "[laughs softly]", "[nervous chuckle]", "[rueful laugh]", "[dry chuckle]",
    "[gentle laugh]", "[embarrassed laugh]", "[dry laugh]", "[tired laugh]",
    "[dismissive laugh]", "[quiet laugh]", "[melancholy chuckle]", "[laughs darkly]",
    "[wistful laugh]", "[emotional laugh]", "[defensive laugh]", "[resigned laugh]",
    "[incredulous laugh]", "[determined laugh]", "[cold laugh]", "[chuckles dryly]",
    "[rueful chuckle]", "[laughs gently]", "[laughs quietly]",
    "[exhausted but hopeful laugh]", "[clears throat]", "[sniffle]", "[scoffs]",
    "[sniffles]", "[groans]", "[frustrated grunt]", "[coughs]", "[swallows hard]",
    "[chokes up]", "[soft sob]", "[coughs wetly]", "[soft rumble]", "[clicks tongue]",
    "[defensive grunt]", "[click]", "[disgusted scoff]", "[stifled sob]",
    "[clicking rapidly]", "[snorts]", "[cry]", "[desperate whisper]", "[trailing off]",
    "[trails off]", "[fading slightly]", "[voice cracking]", "[voice breaking]",
    "[voice breaking slightly]", "[voice catching slightly]", "[shaky voice]",
    "[voice shaking slightly]", "[voice wavering]", "[voice shaking]", "[voice cracks]",
    "[breaking slightly]"
}

# Lowercase version for case-insensitive matching
ALLOWED_TAGS_LOWER = {tag.lower() for tag in ALLOWED_TAGS}


def find_target_files(base_path="/workspace/multilingual_fun_lines/actor_lines"):
    """Find all target files matching the pattern (numbered.txt but not tag_match)."""
    target_files = []
    
    # Search for all *_lines_numbered.txt files recursively
    pattern = os.path.join(base_path, "**", "*_lines_numbered.txt")
    all_files = glob.glob(pattern, recursive=True)
    
    # Filter out files with "tag_match" in the name
    for f in all_files:
        if "tag_match" not in os.path.basename(f):
            target_files.append(f)
    
    return sorted(target_files)


def extract_end_tag(line):
    """Extract tag at end of line if present."""
    # Match [something] at the very end of the line (possibly with trailing whitespace)
    match = re.search(r'\[([^\]]+)\]\s*$', line)
    if match:
        return f"[{match.group(1)}]"
    return None


def remove_end_tag(line):
    """Remove tag at end of line and return cleaned line."""
    # Remove [something] at the very end of the line (and any trailing whitespace)
    cleaned = re.sub(r'\s*\[([^\]]+)\]\s*$', '', line)
    return cleaned


def process_file(filepath):
    """
    Process a single file:
    - Find unlisted end tags
    - Remove them from lines
    - Return list of (line_num, tag) for removed tags
    """
    removed = []
    modified_lines = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.rstrip('\n')
            tag = extract_end_tag(line_stripped)
            
            if tag and tag.lower() not in ALLOWED_TAGS_LOWER:
                # Tag is NOT allowed - remove it
                cleaned_line = remove_end_tag(line_stripped)
                modified_lines.append(cleaned_line + '\n')
                removed.append((line_num, tag))
            else:
                # Keep line as-is
                modified_lines.append(line)
        
        # Write back if any changes were made
        if removed:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    
    return removed


def main():
    import sys
    
    # Allow base path to be passed as command line argument
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "/workspace/multilingual_fun_lines/actor_lines"
    
    output_file = "address_number_removed_tags_end.txt"
    
    print(f"Searching for files in: {base_path}")
    print(f"Looking for *_lines_numbered.txt files (excluding tag_match)")
    print("-" * 60)
    
    target_files = find_target_files(base_path)
    
    if not target_files:
        print(f"No target files found in {base_path}")
        print("Checking if directory exists...")
        if not os.path.exists(base_path):
            print(f"Directory does not exist: {base_path}")
        return
    
    print(f"Found {len(target_files)} target files:")
    for f in target_files:
        print(f"  - {f}")
    print("-" * 60)
    
    # Collect all removed tags
    all_removed = []  # List of (filepath, line_num, tag)
    tag_counts = {}   # Count of each unique removed tag
    
    for filepath in target_files:
        removed = process_file(filepath)
        for line_num, tag in removed:
            all_removed.append((filepath, line_num, tag))
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Output results
    print(f"\nRemoved {len(all_removed)} unlisted tags from end of lines")
    print(f"Unique tags removed: {len(tag_counts)}")
    print("-" * 60)
    
    # Print summary of unique tags
    if tag_counts:
        print("\nTags removed (sorted by count):")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"  {tag}: {count} occurrences")
    
    # Write detailed results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Removed tags at end of lines (NOT in allowed list)\n")
        f.write(f"# Total removed: {len(all_removed)}\n")
        f.write(f"# Unique tags: {len(tag_counts)}\n")
        f.write("#" + "=" * 59 + "\n\n")
        
        # Summary section
        f.write("## SUMMARY - Tags removed:\n")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {tag}: {count} occurrences\n")
        f.write("\n" + "=" * 60 + "\n\n")
        
        # Detailed locations
        f.write("## DETAILED LOCATIONS (file, line number, removed tag):\n\n")
        
        # Group by file
        by_file = defaultdict(list)
        for filepath, line_num, tag in all_removed:
            by_file[filepath].append((line_num, tag))
        
        for filepath in sorted(by_file.keys()):
            f.write(f"### {filepath}\n")
            for line_num, tag in sorted(by_file[filepath]):
                f.write(f"  Line {line_num}: {tag}\n")
            f.write("\n")
    
    print(f"\nRemoval log written to: {output_file}")


if __name__ == "__main__":
    main()