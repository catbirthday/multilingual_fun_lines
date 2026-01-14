import os
import re

# Tags that produce no audio or would be removed as silence
SILENT_TAGS = [
    # Silent physical actions
    "nodding",
    "shaking head",
    "leaning forward",
    "stiffening",
    "shifting uncomfortably",
    "wiping eyes",
    "shakily standing",
    "adjusting equipment quietly",
    "stepping back quickly",
    "lowering phone slowly",
    "pressing play",
    "staring at the half-built set",
    "withdrawing",
    "grinning",
    "recognition dawning",
    # Pauses/silence
    "pause",
    "long pause",
    "short pause",
    "thoughtful pause",
]

removed_log = []

def remove_silent_tags_at_start(text, filepath):
    """Remove silent tags only at the start of lines/dialogue"""
    lines = text.split('\n')
    new_lines = []
    
    for file_line_num, line in enumerate(lines, 1):
        original_line = line
        
        for tag in SILENT_TAGS:
            # After line number: "240. [tag] " -> "240. "
            pattern1 = rf'^(\d+)\.\s*\[{re.escape(tag)}\]\s*'
            match1 = re.match(pattern1, line)
            if match1:
                dialogue_num = match1.group(1)
                line = re.sub(pattern1, r'\1. ', line)
                removed_log.append({
                    'dialogue_num': dialogue_num,
                    'file_line': file_line_num,
                    'filepath': filepath,
                    'tag': tag,
                    'original': original_line.strip()
                })
                continue
            
            # At very start of line: "[tag] Text" -> "Text"
            pattern2 = rf'^\[{re.escape(tag)}\]\s*'
            match2 = re.match(pattern2, line)
            if match2:
                line = re.sub(pattern2, '', line)
                removed_log.append({
                    'dialogue_num': None,
                    'file_line': file_line_num,
                    'filepath': filepath,
                    'tag': tag,
                    'original': original_line.strip()
                })
                continue
            
            # After character label: "Character 1: [tag] Text" -> "Character 1: Text"
            pattern3 = rf'^([^:\n]+:\s*)\[{re.escape(tag)}\]\s*'
            match3 = re.match(pattern3, line)
            if match3:
                line = re.sub(pattern3, r'\1', line)
                removed_log.append({
                    'dialogue_num': None,
                    'file_line': file_line_num,
                    'filepath': filepath,
                    'tag': tag,
                    'original': original_line.strip()
                })
                continue
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)

def process_file(filepath):
    """Process a single file and remove silent tags at line starts"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    cleaned = remove_silent_tags_at_start(content, filepath)
    
    if original != cleaned:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        return True
    return False

# Find all relevant .txt files
base_dir = "/workspace/multilingual_fun_lines/actor_lines"
modified_count = 0
total_count = 0

for root, dirs, files in os.walk(base_dir):
    for filename in files:
        if filename.endswith('.txt'):
            filepath = os.path.join(root, filename)
            total_count += 1
            if process_file(filepath):
                modified_count += 1
                print(f"Modified: {filepath}")

# Save removed log
log_path = "/workspace/multilingual_fun_lines/start_removed.txt"
with open(log_path, 'w', encoding='utf-8') as f:
    f.write(f"# Removed {len(removed_log)} silent tags from start of lines\n")
    f.write(f"# Tags removed: {SILENT_TAGS}\n\n")
    
    for entry in removed_log:
        if entry['dialogue_num']:
            f.write(f"Dialogue {entry['dialogue_num']} (file line {entry['file_line']}) in {entry['filepath']}\n")
        else:
            f.write(f"File line {entry['file_line']} in {entry['filepath']}\n")
        f.write(f"  Tag: [{entry['tag']}]\n")
        f.write(f"  Original: {entry['original']}\n\n")

print(f"\nDone! Modified {modified_count}/{total_count} files")
print(f"Removed {len(removed_log)} tags total")
print(f"Log saved to: {log_path}")