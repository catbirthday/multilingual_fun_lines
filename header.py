#!/usr/bin/env python3
import re
import os
from collections import defaultdict
from pathlib import Path

def parse_line(line):
    """Extract line number and tag from a line like '16. [customer_support|professional] ...'"""
    match = re.match(r'^(\d+)\.\s*\[([^\]]+)\]', line.strip())
    if match:
        line_num = int(match.group(1))
        tag = match.group(2)
        return line_num, tag
    return None, None

def ranges_to_string(numbers):
    """Convert a list of numbers to a range string like '1-20, 31-40, 45'"""
    if not numbers:
        return ""
    numbers = sorted(set(numbers))
    ranges = []
    start = end = numbers[0]
    
    for n in numbers[1:]:
        if n == end + 1:
            end = n
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = end = n
    
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")
    
    return ", ".join(ranges)

def generate_header(content_types, professionalism, total_lines):
    """Generate the header comment block"""
    header = """# Use these to select lines by category.
#
# === CONTENT TYPE ===
"""
    for ct in ["dialogue", "general_tags", "simple_tags", "customer_support", "monologue"]:
        if ct in content_types:
            nums = content_types[ct]
            header += f"# {ct}: {ranges_to_string(nums)}  # {len(nums)} lines\n"
    
    header += """#
# === PROFESSIONALISM (customer_support only) ===
"""
    for prof in ["casual", "professional"]:
        if prof in professionalism:
            nums = professionalism[prof]
            header += f"# {prof}: {ranges_to_string(nums)}  # {len(nums)} lines\n"
    
    header += f"""#
# TOTAL: {total_lines} speaker lines
#"""
    return header

def process_file(filepath):
    """Process a single annotated file and fix its header"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    content_types = defaultdict(list)
    professionalism = defaultdict(list)
    total_lines = 0
    
    # Parse all lines to extract tags
    for line in lines:
        line_num, tag = parse_line(line)
        if line_num is not None:
            total_lines = max(total_lines, line_num)
            
            # Handle customer_support with professionalism subtag
            if '|' in tag:
                main_tag, sub_tag = tag.split('|', 1)
                content_types[main_tag].append(line_num)
                professionalism[sub_tag].append(line_num)
            else:
                content_types[tag].append(line_num)
    
    if total_lines == 0:
        print(f"  No numbered lines found in {filepath}")
        return False
    
    # Generate new header
    new_header = generate_header(content_types, professionalism, total_lines)
    
    # Find and replace the old header
    # Look for the block starting with "# Use these" and ending before "# --- "
    header_pattern = r'# Use these.*?(?=\n# ---)'
    
    if re.search(header_pattern, content, re.DOTALL):
        new_content = re.sub(header_pattern, new_header, content, flags=re.DOTALL)
    else:
        # No existing header found, add at the beginning
        new_content = new_header + "\n" + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  Fixed: {filepath}")
    print(f"    Content types: {dict(content_types)}")
    print(f"    Professionalism: {dict(professionalism)}")
    print(f"    Total lines: {total_lines}")
    return True

def main():
    base_dir = Path("/workspace/multilingual_fun_lines/actor_lines")
    
    if not base_dir.exists():
        print(f"Error: {base_dir} does not exist")
        return
    
    # Find all annotated files
    for actor_dir in sorted(base_dir.iterdir()):
        if not actor_dir.is_dir():
            continue
        
        print(f"\nProcessing {actor_dir.name}:")
        
        for filepath in sorted(actor_dir.glob("*_annotated.txt")):
            process_file(filepath)

if __name__ == "__main__":
    main()