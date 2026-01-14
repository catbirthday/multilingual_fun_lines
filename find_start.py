#!/usr/bin/env python3
"""
Find ALL tags at the START of dialogue lines.
Pattern: "123. [tag] Text here..."

This is for discovery - listing all unique tags that appear at the start of lines.
"""

import re
import glob
import os
from collections import defaultdict


def find_target_files(base_path="/workspace/multilingual_fun_lines/actor_lines"):
    """Find all target files matching the pattern (_lines.txt but not _lines_numbered.txt and not tag_match)."""
    target_files = []
    
    # Search for all *_lines.txt files recursively
    pattern = os.path.join(base_path, "**", "*_lines.txt")
    all_files = glob.glob(pattern, recursive=True)
    
    # Filter out files with "tag_match" in the name or "_lines_numbered" in the name
    for f in all_files:
        basename = os.path.basename(f)
        if "tag_match" not in basename and "_lines_numbered" not in basename:
            target_files.append(f)
    
    return sorted(target_files)


def extract_start_tag(line):
    """
    Extract tag at start of dialogue line if present.
    Pattern: "123. [tag] text..." -> returns "[tag]"
    """
    # Match: number. [something] at the start
    match = re.match(r'^(\d+)\.\s*\[([^\]]+)\]', line)
    if match:
        return f"[{match.group(2)}]"
    return None


def extract_dialogue_number(line):
    """Extract dialogue number from start of line (e.g., '1.', '2.', '376.')"""
    match = re.match(r'^(\d+)\.\s', line)
    if match:
        return match.group(1)
    return None


def process_file(filepath):
    """Process a single file and return list of (file_line_num, dialogue_num, tag) for ALL start tags."""
    found = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for file_line_num, line in enumerate(f, 1):
                line = line.rstrip('\n')
                tag = extract_start_tag(line)
                if tag:
                    dialogue_num = extract_dialogue_number(line)
                    found.append((file_line_num, dialogue_num, tag))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return found


def main():
    import sys
    
    # Allow base path to be passed as command line argument
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "/workspace/multilingual_fun_lines/actor_lines"
    
    output_file = "all_start_tags.txt"
    
    print(f"Searching for files in: {base_path}")
    print(f"Looking for *_lines.txt files (excluding tag_match and _lines_numbered)")
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
    
    # Collect all tags
    all_found = []  # List of (filepath, file_line_num, dialogue_num, tag)
    tag_counts = {}    # Count of each unique tag
    
    for filepath in target_files:
        found = process_file(filepath)
        for file_line_num, dialogue_num, tag in found:
            all_found.append((filepath, file_line_num, dialogue_num, tag))
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Output results
    print(f"\nFound {len(all_found)} total START tags")
    print(f"Unique START tags: {len(tag_counts)}")
    print("-" * 60)
    
    # Print summary of unique tags
    if tag_counts:
        print("\nALL unique START tags (sorted by count):")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"  {tag}: {count} occurrences")
    
    # Write detailed results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# ALL tags at START of dialogue lines\n")
        f.write(f"# Total instances: {len(all_found)}\n")
        f.write(f"# Unique tags: {len(tag_counts)}\n")
        f.write("#" + "=" * 59 + "\n\n")
        
        # Summary section - just the unique tags sorted by count
        f.write("## ALL UNIQUE START TAGS (sorted by count):\n")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            f.write(f"  {tag}: {count}\n")
        f.write("\n" + "=" * 60 + "\n\n")
        
        # Alphabetical list for easy reference
        f.write("## ALL UNIQUE START TAGS (alphabetical):\n")
        for tag in sorted(tag_counts.keys(), key=lambda x: x.lower()):
            f.write(f"  {tag}\n")
        f.write("\n" + "=" * 60 + "\n\n")
        
        # Detailed locations
        f.write("## DETAILED LOCATIONS:\n")
        f.write("# Format: File path | File line | Dialogue # | Tag\n\n")
        
        # Group by file
        by_file = defaultdict(list)
        for filepath, file_line_num, dialogue_num, tag in all_found:
            by_file[filepath].append((file_line_num, dialogue_num, tag))
        
        for filepath in sorted(by_file.keys()):
            f.write(f"### {filepath}\n")
            for file_line_num, dialogue_num, tag in sorted(by_file[filepath]):
                dialogue_str = f"Dialogue {dialogue_num}" if dialogue_num else "N/A"
                f.write(f"  Line {file_line_num} | {dialogue_str} | {tag}\n")
            f.write("\n")
    
    print(f"\nDetailed results written to: {output_file}")


if __name__ == "__main__":
    main()