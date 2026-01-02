#!/usr/bin/env python3
import re
from pathlib import Path

def extract_dropbox_link(filepath):
    """Extract Dropbox link from the top of a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for Dropbox link
    match = re.search(r'https://www\.dropbox\.com/[^\s]+', content)
    if match:
        return match.group(0)
    return None

def add_link_to_file(filepath, link):
    """Add Dropbox link to the top of a file if not already present"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if link already present
    if link in content:
        print(f"    Link already present in {filepath.name}")
        return False
    
    # Add link at the top
    new_content = f"{link}\n\n{content}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"    Added link to {filepath.name}")
    return True

def main():
    base_dir = Path("/workspace/multilingual_fun_lines/actor_lines")
    
    if not base_dir.exists():
        print(f"Error: {base_dir} does not exist")
        return
    
    for actor_dir in sorted(base_dir.iterdir()):
        if not actor_dir.is_dir():
            continue
        
        # Skip English folders (they don't have tag_match files)
        if actor_dir.name.startswith('english_'):
            continue
        
        print(f"\nProcessing {actor_dir.name}:")
        
        # Find the base tag_match file (without _numbered or _annotated)
        base_files = list(actor_dir.glob("new_order_tag_match_*_lines.txt"))
        # Filter out numbered and annotated versions
        base_files = [f for f in base_files if '_numbered' not in f.name and '_annotated' not in f.name]
        
        if not base_files:
            print(f"  No base tag_match file found")
            continue
        
        base_file = base_files[0]
        print(f"  Base file: {base_file.name}")
        
        # Extract Dropbox link
        link = extract_dropbox_link(base_file)
        if not link:
            print(f"  No Dropbox link found in {base_file.name}")
            continue
        
        print(f"  Found link: {link[:60]}...")
        
        # Find numbered and annotated versions
        stem = base_file.stem  # e.g., "new_order_tag_match_de_f_lines"
        numbered_file = actor_dir / f"{stem}_numbered.txt"
        annotated_file = actor_dir / f"{stem}_annotated.txt"
        
        for target_file in [numbered_file, annotated_file]:
            if target_file.exists():
                add_link_to_file(target_file, link)
            else:
                print(f"    File not found: {target_file.name}")

if __name__ == "__main__":
    main()