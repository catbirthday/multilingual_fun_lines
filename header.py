#!/usr/bin/env python3
import re
import os
from collections import defaultdict
from pathlib import Path

# Map section headers to content type tags
SECTION_TO_TAG = {
    'DIALOGUE': 'dialogue',
    'GENERAL_TAGS': 'general_tags',
    'SIMPLE_TAGS': 'simple_tags',
    'CUSTOMER_SUPPORT': 'customer_support',
    'MONOLOGUE': 'monologue',
}

# Mode tags (language modes for non-English files)
MODE_TAGS = {'pure', 'mix', 'en'}

def parse_line_with_inline_tag(line):
    """Extract line number and tag from a line like '16. [customer_support|professional] ...'"""
    match = re.match(r'^(\d+)\.\s*\[([^\]]+)\]', line.strip())
    if match:
        line_num = int(match.group(1))
        tag = match.group(2)
        # Check if this is a content type tag (not a mode tag)
        base_tag = tag.split('|')[0]
        if base_tag not in MODE_TAGS:
            return line_num, tag
    return None, None

def parse_line_number(line):
    """Extract just the line number from a numbered line"""
    match = re.match(r'^(\d+)\.', line.strip())
    if match:
        return int(match.group(1))
    return None

def parse_section_header(line):
    """Extract section name from a header like '# --- DIALOGUE ---'"""
    match = re.match(r'^#\s*---\s*(\w+)(?:\s*\(continued\))?\s*---', line.strip())
    if match:
        section = match.group(1).upper()
        return SECTION_TO_TAG.get(section)
    return None

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

def process_file(filepath, add_inline_tags=False):
    """Process a single annotated file and fix its header.
    
    If add_inline_tags=True, also add content type tags to each line.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    content_types = defaultdict(list)
    professionalism = defaultdict(list)
    total_lines = 0
    
    # First pass: check if file uses inline tags or section headers
    has_inline_tags = False
    has_section_headers = False
    
    for line in lines:
        if parse_section_header(line):
            has_section_headers = True
        line_num, tag = parse_line_with_inline_tag(line)
        if line_num and tag:
            has_inline_tags = True
    
    # Determine file type and parse accordingly
    current_section = None
    line_to_section = {}  # Map line numbers to their content type
    
    if has_inline_tags and not has_section_headers:
        # English-style file with inline tags like [dialogue]
        for line in lines:
            line_num, tag = parse_line_with_inline_tag(line)
            if line_num is not None:
                total_lines = max(total_lines, line_num)
                
                if '|' in tag:
                    main_tag, sub_tag = tag.split('|', 1)
                    content_types[main_tag].append(line_num)
                    professionalism[sub_tag].append(line_num)
                else:
                    content_types[tag].append(line_num)
    else:
        # Non-English file with section headers like # --- DIALOGUE ---
        for line in lines:
            section = parse_section_header(line)
            if section:
                current_section = section
                continue
            
            line_num = parse_line_number(line)
            if line_num is not None and current_section:
                total_lines = max(total_lines, line_num)
                content_types[current_section].append(line_num)
                line_to_section[line_num] = current_section
    
    if total_lines == 0:
        print(f"  No numbered lines found in {filepath}")
        return False
    
    # Generate new header
    new_header = generate_header(content_types, professionalism, total_lines)
    
    # If requested, add inline content type tags to each line
    new_lines = []
    if add_inline_tags and line_to_section:
        current_section = None
        for line in lines:
            section = parse_section_header(line)
            if section:
                current_section = section
                new_lines.append(line)
                continue
            
            line_num = parse_line_number(line)
            if line_num is not None and line_num in line_to_section:
                content_tag = line_to_section[line_num]
                # Check if line already has the content tag
                if f'[{content_tag}]' not in line and f'[{content_tag}|' not in line:
                    # Insert content tag after the line number
                    # Pattern: "1. [mix] text" -> "1. [dialogue] [mix] text"
                    new_line = re.sub(
                        r'^(\d+\.)\s*',
                        rf'\1 [{content_tag}] ',
                        line
                    )
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    
    # Find and replace the old header
    # Look for the block starting with "# Use these" and ending before "# --- "
    header_pattern = r'# Use these.*?(?=\n# ---)'
    
    if re.search(header_pattern, content, re.DOTALL):
        new_content = re.sub(header_pattern, new_header, content, flags=re.DOTALL)
    else:
        # Try alternate pattern for files with different structure
        header_pattern2 = r'# LINE INDEX\n# Use these.*?(?=\n#\n# ---|\n# --- )'
        if re.search(header_pattern2, content, re.DOTALL):
            new_content = re.sub(header_pattern2, f"# LINE INDEX\n{new_header}", content, flags=re.DOTALL)
        else:
            # No existing header found in expected location
            new_content = content
            print(f"  Warning: Could not find header pattern in {filepath}")
    
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
        
        # Determine if this is an English folder
        is_english = actor_dir.name.startswith('english_')
        
        for filepath in sorted(actor_dir.glob("*_annotated.txt")):
            # For non-English files, add inline content type tags
            process_file(filepath, add_inline_tags=not is_english)

if __name__ == "__main__":
    main()