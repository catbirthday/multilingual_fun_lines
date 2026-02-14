#!/usr/bin/env python3
"""
Script to clean up annotated text files:
1. Remove blank lines
2. Merge continuation lines (lines without a number prefix) with their parent numbered line
"""

import sys
import os
import re
import argparse

def is_numbered_line(line):
    """Check if a line starts with a number followed by a period (e.g., '507.' or '1.')"""
    return bool(re.match(r'^\d+\.\s', line.strip()))

def clean_and_merge_lines(input_file, output_file=None):
    """Remove blank lines and merge continuation lines with their numbered parent."""
    if output_file is None:
        output_file = input_file
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_count = len(lines)
    
    # First pass: remove blank lines
    non_blank_lines = [line.rstrip() for line in lines if line.strip()]
    
    # Second pass: merge continuation lines with their parent numbered line
    merged_lines = []
    current_line = None
    
    for line in non_blank_lines:
        if is_numbered_line(line):
            # If we have a previous line, save it
            if current_line is not None:
                merged_lines.append(current_line)
            # Start a new numbered line
            current_line = line
        else:
            # This is a continuation line - merge with current
            if current_line is not None:
                # Add a space separator and append the continuation
                current_line = current_line + ' ' + line
            else:
                # Edge case: continuation line at the start (shouldn't happen, but handle it)
                current_line = line
    
    # Don't forget the last line
    if current_line is not None:
        merged_lines.append(current_line)
    
    # Write back
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in merged_lines:
            f.write(line + '\n')
    
    print(f"Processed {input_file}")
    print(f"  Original lines: {original_count}")
    print(f"  After removing blanks: {len(non_blank_lines)}")
    print(f"  After merging continuations: {len(merged_lines)}")
    print(f"  Total lines removed/merged: {original_count - len(merged_lines)}")

def process_folder(folder_path):
    """Process all .txt files in a folder."""
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        sys.exit(1)
    
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"No .txt files found in '{folder_path}'")
        return
    
    print(f"Found {len(txt_files)} .txt file(s) in '{folder_path}'\n")
    
    for filename in sorted(txt_files):
        filepath = os.path.join(folder_path, filename)
        clean_and_merge_lines(filepath)
        print()  # Add blank line between files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean up annotated text files by removing blank lines and merging continuation lines."
    )
    parser.add_argument(
        "--file", "-f",
        default=None,
        help="Input file to process"
    )
    parser.add_argument(
        "--folder", "-d",
        default=None,
        help="Folder to process (will process all .txt files in the folder)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file (if not specified, input file will be overwritten). Only valid with --file."
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.file and args.folder:
        print("Error: Cannot specify both --file and --folder. Choose one.")
        sys.exit(1)
    
    if not args.file and not args.folder:
        print("Error: Must specify either --file or --folder.")
        sys.exit(1)
    
    if args.folder and args.output:
        print("Error: --output cannot be used with --folder (files are overwritten in place).")
        sys.exit(1)
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        clean_and_merge_lines(args.file, args.output)
    else:
        process_folder(args.folder)
