import os
import glob
import re
from collections import defaultdict

# Find all matching files
base_dir = "/workspace/multilingual_fun_lines/actor_lines"
pattern = os.path.join(base_dir, "*/new_order_*_lines_numbered.txt")
found_files = glob.glob(pattern)

# Filter out "original" and "tag_match" versions
found_files = [f for f in found_files if "original" not in f and "tag_match" not in f]

# Regex for tags at end of line
end_tag_pattern = re.compile(r'\[([^\]]+)\]\s*$')

# Track all tags and where they appear
all_tags = defaultdict(list)
tags_by_file = defaultdict(lambda: defaultdict(int))

for filepath in sorted(found_files):
    lang_folder = filepath.split("/")[-2]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n')
            match = end_tag_pattern.search(line)
            if match:
                tag = match.group(1).lower()
                all_tags[tag].append((lang_folder, line_num, line))
                tags_by_file[lang_folder][tag] += 1

# Write results to file
output_path = "/workspace/multilingual_fun_lines/end_of_line_tags_report.txt"

with open(output_path, 'w', encoding='utf-8') as out:
    out.write("=" * 80 + "\n")
    out.write("END-OF-LINE TAGS FOUND\n")
    out.write("=" * 80 + "\n")
    
    out.write(f"\nUnique tags: {len(all_tags)}\n")
    out.write("\nAll tags (sorted by frequency):\n")
    for tag, occurrences in sorted(all_tags.items(), key=lambda x: -len(x[1])):
        out.write(f"  [{tag}]\n")
    
    out.write("\n" + "=" * 80 + "\n")
    out.write("TAGS BY LANGUAGE/FILE\n")
    out.write("=" * 80 + "\n")
    
    for lang in sorted(tags_by_file.keys()):
        tags = tags_by_file[lang]
        total = sum(tags.values())
        out.write(f"\n{lang} ({total} total):\n")
        for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
            out.write(f"  [{tag}]: {count}\n")
    
    out.write("\n" + "=" * 80 + "\n")
    out.write("SAMPLE LINES FOR EACH TAG\n")
    out.write("=" * 80 + "\n")
    
    for tag in sorted(all_tags.keys()):
        out.write(f"\n[{tag}]  :\n")
        for lang, line_num, line_text in all_tags[tag][:3]:
            display = line_text if len(line_text) < 100 else line_text[:97] + "..."
            out.write(f"  {lang}:{line_num} -> {display}\n")
        if len(all_tags[tag]) > 3:
            out.write(f"  ... and {len(all_tags[tag]) - 3} more\n")

print(f"Report saved to: {output_path}")