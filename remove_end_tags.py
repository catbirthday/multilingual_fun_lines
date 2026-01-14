#!/usr/bin/env python3
"""
Remove tags at end of lines in ALL translated language files based on dialogue numbers
that had tags removed in the English version.

Automatically finds all non-English language folders and processes them.

Reads from: address_number_removed_tags_end.txt
Applies to: All tag_match files in ALL language folders (hindi, french, korean, german, italian, etc.)
"""

import re
import os
import glob
from collections import defaultdict


def parse_removal_log(log_path):
    """
    Parse the removal log file to extract ALL dialogue numbers that had tags removed
    across all English files.
    
    Returns a set of dialogue_numbers (combined from all English files)
    """
    all_dialogue_nums = set()
    
    current_file = None
    is_english_file = False
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Check for file header (### /path/to/english_X/file.txt)
            if line.startswith('### '):
                current_file = line[4:]
                # Check if this is an English file
                is_english_file = '/english_' in current_file
                continue
            
            # Check for dialogue entry (Line X | Dialogue Y | [tag])
            if is_english_file and line.startswith('Line '):
                # Parse: "Line 33 | Dialogue 12 | [pause]"
                match = re.match(r'Line \d+ \| Dialogue (\d+) \| \[.+\]', line)
                if match:
                    dialogue_num = match.group(1)
                    all_dialogue_nums.add(dialogue_num)
    
    return all_dialogue_nums


def find_language_folders(actor_lines_path):
    """
    Find all language folders (non-English) in the actor_lines directory.
    
    Returns list of folder paths
    """
    language_folders = []
    
    if not os.path.exists(actor_lines_path):
        return language_folders
    
    for item in os.listdir(actor_lines_path):
        item_path = os.path.join(actor_lines_path, item)
        if os.path.isdir(item_path):
            # Skip English folders
            if not item.startswith('english_'):
                language_folders.append(item_path)
    
    return sorted(language_folders)


def find_target_files(language_folder):
    """
    Find all tag_match files in the language folder.
    
    Returns list of file paths
    """
    # Look for files matching pattern *tag_match*_lines*.txt
    pattern = os.path.join(language_folder, "*tag_match*lines*.txt")
    all_files = glob.glob(pattern)
    
    return sorted(all_files)


def extract_dialogue_number(line):
    """Extract dialogue number from start of line (e.g., '1.', '2.', '376.')"""
    match = re.match(r'^(\d+)\.\s', line)
    if match:
        return match.group(1)
    return None


def remove_end_tag(line):
    """Remove tag at end of line and return cleaned line."""
    cleaned = re.sub(r'\s*\[([^\]]+)\]\s*$', '', line)
    return cleaned


def has_end_tag(line):
    """Check if line has a tag at the end."""
    return bool(re.search(r'\[([^\]]+)\]\s*$', line))


def get_end_tag(line):
    """Extract the end tag from a line."""
    match = re.search(r'\[([^\]]+)\]\s*$', line)
    if match:
        return f"[{match.group(1)}]"
    return None


def process_target_file(filepath, dialogue_nums_to_remove):
    """
    Process a target file and remove end tags from lines whose dialogue numbers
    are in the removal set.
    
    Returns list of (file_line_num, dialogue_num, removed_tag) for logging.
    """
    removed = []
    modified_lines = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for file_line_num, line in enumerate(lines, 1):
            line_stripped = line.rstrip('\n')
            dialogue_num = extract_dialogue_number(line_stripped)
            
            # Check if this dialogue number should have its end tag removed
            if dialogue_num and dialogue_num in dialogue_nums_to_remove and has_end_tag(line_stripped):
                removed_tag = get_end_tag(line_stripped)
                cleaned_line = remove_end_tag(line_stripped)
                modified_lines.append(cleaned_line + '\n')
                
                if removed_tag:
                    removed.append((file_line_num, dialogue_num, removed_tag))
            else:
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
    
    # Default paths
    log_path = "/workspace/multilingual_fun_lines/address_number_removed_tags_end.txt"
    actor_lines_path = "/workspace/multilingual_fun_lines/actor_lines"
    
    # Parse command line args
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
    if len(sys.argv) > 2:
        actor_lines_path = sys.argv[2]
    
    output_log = "translated_removed_tags.txt"
    
    print(f"Reading removal log from: {log_path}")
    print(f"Actor lines directory: {actor_lines_path}")
    print("=" * 60)
    
    # Check paths exist
    if not os.path.exists(log_path):
        print(f"Error: Log file not found: {log_path}")
        return
    
    if not os.path.exists(actor_lines_path):
        print(f"Error: Actor lines directory not found: {actor_lines_path}")
        return
    
    # Parse the English removal log (combined from all English files)
    all_dialogue_nums = parse_removal_log(log_path)
    
    print(f"Found {len(all_dialogue_nums)} dialogue numbers with removed tags (combined from all English files)")
    sorted_nums = sorted(all_dialogue_nums, key=int)
    print(f"Dialogue numbers: {sorted_nums[:20]}{'...' if len(sorted_nums) > 20 else ''}")
    print("=" * 60)
    
    # Find all language folders
    language_folders = find_language_folders(actor_lines_path)
    
    print(f"Found {len(language_folders)} language folders:")
    for folder in language_folders:
        print(f"  - {os.path.basename(folder)}")
    print("=" * 60)
    
    if not language_folders:
        print("No language folders found!")
        return
    
    # Process each language folder
    all_removed = []  # (filepath, file_line_num, dialogue_num, removed_tag)
    by_language = defaultdict(int)  # Count removals per language
    
    for language_folder in language_folders:
        language_name = os.path.basename(language_folder)
        print(f"\n{'='*60}")
        print(f"Processing: {language_name}")
        print("-" * 60)
        
        target_files = find_target_files(language_folder)
        
        if not target_files:
            print(f"  No tag_match files found, skipping")
            continue
        
        print(f"  Found {len(target_files)} target files:")
        for f in target_files:
            print(f"    - {os.path.basename(f)}")
        
        language_removed_count = 0
        
        for filepath in target_files:
            removed = process_target_file(filepath, all_dialogue_nums)
            
            for file_line_num, dialogue_num, removed_tag in removed:
                all_removed.append((filepath, file_line_num, dialogue_num, removed_tag))
            
            language_removed_count += len(removed)
            print(f"    {os.path.basename(filepath)}: removed {len(removed)} tags")
        
        by_language[language_name] = language_removed_count
        print(f"  Total for {language_name}: {language_removed_count} tags removed")
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total tags removed across all languages: {len(all_removed)}")
    
    print("\nRemovals by language:")
    for lang, count in sorted(by_language.items(), key=lambda x: -x[1]):
        print(f"  {lang}: {count}")
    
    # Count by tag
    tag_counts = {}
    for _, _, _, tag in all_removed:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    if tag_counts:
        print("\nTop 20 tags removed (sorted by count):")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:20]:
            print(f"  {tag}: {count}")
        if len(tag_counts) > 20:
            print(f"  ... and {len(tag_counts) - 20} more unique tags")
    
    # Write detailed log
    with open(output_log, 'w', encoding='utf-8') as f:
        f.write("# Tags removed from ALL translated files based on English removal log\n")
        f.write(f"# Source log: {log_path}\n")
        f.write(f"# Actor lines directory: {actor_lines_path}\n")
        f.write(f"# Total removed: {len(all_removed)}\n")
        f.write(f"# Languages processed: {len(by_language)}\n")
        f.write("#" + "=" * 59 + "\n\n")
        
        # Summary by language
        f.write("## SUMMARY BY LANGUAGE:\n")
        for lang, count in sorted(by_language.items(), key=lambda x: -x[1]):
            f.write(f"  {lang}: {count}\n")
        f.write("\n")
        
        # Summary by tag
        f.write("## SUMMARY - Tags removed:\n")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {tag}: {count}\n")
        f.write("\n" + "=" * 60 + "\n\n")
        
        # Detailed locations
        f.write("## DETAILED LOCATIONS:\n")
        f.write("# Format: File path | File line | Dialogue # | Removed tag\n\n")
        
        # Group by file
        by_file_removed = defaultdict(list)
        for filepath, file_line_num, dialogue_num, tag in all_removed:
            by_file_removed[filepath].append((file_line_num, dialogue_num, tag))
        
        for filepath in sorted(by_file_removed.keys()):
            f.write(f"### {filepath}\n")
            for file_line_num, dialogue_num, tag in sorted(by_file_removed[filepath]):
                f.write(f"  Line {file_line_num} | Dialogue {dialogue_num} | {tag}\n")
            f.write("\n")
    
    print(f"\nDetailed log written to: {output_log}")


if __name__ == "__main__":
    main()