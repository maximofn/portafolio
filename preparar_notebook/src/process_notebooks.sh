#!/bin/bash

# Script to process all notebooks listed in list_posts.md
# Extracts filename from each line and runs preparar_notebook.py

# File containing the list of posts
input_file="../../posts/list_posts.md"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: File $input_file not found!"
    exit 1
fi

# Function to extract filename from ls -la output format
extract_filename() {
    local line="$1"
    # Use awk to get the last field (filename)
    echo "$line" | awk '{print $NF}'
}

# Function to process a single notebook
process_notebook() {
    local notebook_name="$1"
    
    echo "Processing notebook: $notebook_name"
    
    # Execute the python command
    python preparar_notebook.py "../../posts/$notebook_name" \
        --no_check_metadata \
        --no_correct_ortografic_errors \
        --no_translate \
        --yes_convert_to_xml \
        --yes_convert_to_html \
        --no_add_to_json
    
    # Check if the command was successful
    if [ $? -eq 0 ]; then
        echo "✓ Successfully processed: $notebook_name"
    else
        echo "✗ Error processing: $notebook_name"
    fi
    
    echo "----------------------------------------"
}

# Counter for processed files
processed_count=0
total_lines=0

echo "Starting batch processing of notebooks..."
echo "========================================"

# Read the file line by line
while IFS= read -r line; do
    # Skip empty lines
    if [ -z "$line" ]; then
        continue
    fi
    
    # Extract filename from the line
    notebook_name=$(extract_filename "$line")
    
    # Check if it's a .ipynb file
    if [[ "$notebook_name" == *.ipynb ]]; then
        ((total_lines++))
        process_notebook "$notebook_name"
        ((processed_count++))
    else
        echo "Skipping non-notebook file: $notebook_name"
    fi
    
done < "$input_file"

echo "========================================"
echo "Batch processing completed!"
echo "Total notebooks processed: $processed_count"
echo "Total lines read: $total_lines" 