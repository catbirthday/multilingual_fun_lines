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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean up annotated text files by removing blank lines and merging continuation lines."
    )
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Input file to process"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file (if not specified, input file will be overwritten)"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    
    clean_and_merge_lines(args.file, args.output)
