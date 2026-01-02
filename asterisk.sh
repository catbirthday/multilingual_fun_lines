#!/bin/bash
# find_triple_asterisks.sh
# Lists all lines containing 271 in the specified files

BASE_DIR="/workspace/multilingual_fun_lines/actor_lines"

find "$BASE_DIR" -name "new_order_tag_match_*_lines_numbered.txt" -print0 | while IFS= read -r -d '' file; do
    result=$(grep -n '\*\*\*' "$file" 2>/dev/null)
    if [[ -n "$result" ]]; then
        echo "=== $file ==="
        echo "$result"
        echo ""
    fi
done