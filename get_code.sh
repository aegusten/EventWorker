#!/bin/bash

project_dir=$(pwd)

output_file="${project_dir}/getcode.txt"

if [ -f "$output_file" ]; then
  rm "$output_file"
fi

# List of file extensions to include (extensions of the programming languages you want)
include_extensions=("*.py" "*.html" "*.css" ".js")  # Modify this array to include the file types you want

# List of patterns or file types to exclude
exclude_patterns=("*.jpg" "*.jpeg" "*.png" "*.gif" "*.svg" "*.ico" "*.dll" "*.exe" "*.cache" "*.map" "*.json" "*.md")  # Modify this array to exclude file types or patterns you don't want

read_files() {
  for entry in "$1"/*
  do
    if [ -d "$entry" ]; then
      read_files "$entry"
    elif [ -f "$entry" ]; then
      should_ignore=false
      for ignore_pattern in "${exclude_patterns[@]}"; do
        if [[ "$entry" == $ignore_pattern ]]; then
          should_ignore=true
          break
        fi
      done

      if ! $should_ignore; then
        should_include=false
        for include_pattern in "${include_extensions[@]}"; do
          if [[ "$entry" == $include_pattern ]]; then
            should_include=true
            break
          fi
        done

        if $should_include; then
          relative_path=${entry#"$project_dir/"}
          echo "// File: $relative_path" >> "$output_file"
          cat "$entry" >> "$output_file"
          echo "" >> "$output_file"
        fi
      fi
    fi
  done
}

# Call the recursive function starting from the project directory
read_files "$project_dir"

# ------------------------------------------
# Instructions:

# 1. Specify Programming Languages to Include:
#    - Modify the 'include_extensions' array near the top of the script.
#    - Add the file extensions of the programming languages you want to include.
#    - Example: To include Python, PHP, HTML, and CSS files:
#      include_extensions=("*.py" "*.php" "*.html" "*.css")
#    - To include JavaScript files, add "*.js":
#      include_extensions=("*.py" "*.php" "*.html" "*.css" "*.js")

# 2. Specify Files or Patterns to Exclude:
#    - Modify the 'exclude_patterns' array near the top of the script.
#    - Add any file patterns you want to exclude.
#    - Example: To exclude image files and binaries:
#      exclude_patterns=("*.jpg" "*.jpeg" "*.png" "*.gif" "*.dll" "*.exe" "*.cache")
#    - Add or remove patterns as needed.

# 3. How to Run the Script:
#    - Save this script to a file, for example, 'get_code_context.sh'.
#    - Open a terminal and navigate to the directory containing the script.
#    - Make the script executable by running:
#      chmod +x get_code_context.sh
#    - Run the script by executing:
#      ./get_code_context.sh
#    - The script will create a file named 'getcode.txt' in the current directory.
#    - This file will contain the concatenated content of all included files.

# ------------------------------------------
