#!/usr/bin/env python3
"""
Remove tags at end of lines in translated files based on dialogue numbers
that had tags removed in the English version.

Reads from: address_number_removed_tags_end.txt
Applies to: Specified target files (e.g., Hindi translations)
"""

import re
import os
from collections import defaultdict

def parse_removal_log(log_path):
    """
    Parse the removal log file to extract dialogue numbers that had tags removed.
    Returns a dict: {english_file_path: set of dialogue_numbers}
    Also returns a flat set of all dialogue numbers across all files.
    """
    by_file = defaultdict(set)
    all_dialogue_nums = set()
    
    current_file = None
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Check for file header (### /path/to/file.txt)
            if line.startswith('### '):
                current_file = line[4:]
                continue
            
            # Check for dialogue entry (Line X | Dialogue Y | [tag])
            if current_file and line.startswith('Line '):
                # Parse: "Line 33 | Dialogue 12 | [pause]"
                match = re.match(r'Line \d+ \| Dialogue (\d+) \| \[.+\]', line)
                if match:
                    dialogue_num = match.group(1)
                    by_file[current_file].add(dialogue_num)
                    all_dialogue_nums.add(dialogue_num)
    
    return by_file, all_dialogue_nums


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
                # Extract the tag before removing it (for logging)
                tag_match = re.search(r'\[([^\]]+)\]\s*$', line_stripped)
                removed_tag = f"[{tag_match.group(1)}]" if tag_match else None
                
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
    
    # Target files to process
    target_files = [
        "/workspace/multilingual_fun_lines/actor_lines/hindi_male/new_order_tag_match_hi_m_lines_annotated.txt",
        "/workspace/multilingual_fun_lines/actor_lines/hindi_male/new_order_tag_match_hi_m_lines_numbered.txt",
        "/workspace/multilingual_fun_lines/actor_lines/hindi_male/new_order_tag_match_hi_m_lines.txt",
    ]
    
    # Allow overriding log path via command line
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
    
    # Allow additional target files via command line
    if len(sys.argv) > 2:
        target_files = sys.argv[2:]
    
    output_log = "translated_removed_tags.txt"
    
    print(f"Reading removal log from: {log_path}")
    print("-" * 60)
    
    # Parse the English removal log
    if not os.path.exists(log_path):
        print(f"Error: Log file not found: {log_path}")
        return
    
    by_file, all_dialogue_nums = parse_removal_log(log_path)
    
    print(f"Found {len(all_dialogue_nums)} dialogue numbers with removed tags")
    print(f"Dialogue numbers: {sorted(all_dialogue_nums, key=int)[:20]}{'...' if len(all_dialogue_nums) > 20 else ''}")
    print("-" * 60)
    
    # Process each target file
    all_removed = []  # (filepath, file_line_num, dialogue_num, removed_tag)
    
    for filepath in target_files:
        print(f"\nProcessing: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"  WARNING: File not found, skipping")
            continue
        
        removed = process_target_file(filepath, all_dialogue_nums)
        
        for file_line_num, dialogue_num, removed_tag in removed:
            all_removed.append((filepath, file_line_num, dialogue_num, removed_tag))
        
        print(f"  Removed {len(removed)} tags")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Total tags removed from translated files: {len(all_removed)}")
    
    # Count by tag
    tag_counts = {}
    for _, _, _, tag in all_removed:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    if tag_counts:
        print("\nTags removed (sorted by count):")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"  {tag}: {count}")
    
    # Write detailed log
    with open(output_log, 'w', encoding='utf-8') as f:
        f.write("# Tags removed from translated files based on English removal log\n")
        f.write(f"# Source log: {log_path}\n")
        f.write(f"# Total removed: {len(all_removed)}\n")
        f.write("#" + "=" * 59 + "\n\n")
        
        # Summary
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