#!/bin/bash

BASE_DIR="/workspace/multilingual_fun_lines/actor_lines"

if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Directory $BASE_DIR does not exist"
    exit 1
fi

echo "Starting cleanup..."

for actor_dir in "$BASE_DIR"/*/; do
    dir_name=$(basename "$actor_dir")
    
    if [[ "$dir_name" == english_* ]]; then
        echo "Processing English folder: $dir_name"
        
        # Remove all subdirectories
        echo "  Directories to remove:"
        find "$actor_dir" -mindepth 1 -type d -print
        find "$actor_dir" -mindepth 1 -type d -exec rm -rf {} + 2>/dev/null
        
        # Remove all files that don't have 'new_order' in the name or aren't .txt
        echo "  Files to remove:"
        find "$actor_dir" -maxdepth 1 -type f ! \( -name "*new_order*.txt" \) -print
        find "$actor_dir" -maxdepth 1 -type f ! \( -name "*new_order*.txt" \) -delete
        
    else
        echo "Processing non-English folder: $dir_name"
        
        # Remove all subdirectories
        echo "  Directories to remove:"
        find "$actor_dir" -mindepth 1 -type d -print
        find "$actor_dir" -mindepth 1 -type d -exec rm -rf {} + 2>/dev/null
        
        # Remove files that don't match the allowed patterns
        # Only keep files with "new_order_tag_match" in the name
        echo "  Files to remove:"
        find "$actor_dir" -maxdepth 1 -type f ! -name "new_order_tag_match_*.txt" -print
        find "$actor_dir" -maxdepth 1 -type f ! -name "new_order_tag_match_*.txt" -delete
    fi
done

echo "Cleanup complete!"