#!/bin/bash

# Ensure we're in a Git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: This script must be run from within a Git repository."
    exit 1
fi

# Function to convert filename to lowercase
to_lowercase() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr '_' '-'
}

# Get all files tracked by Git
git ls-files | while read -r file; do
    lowercase_file=$(to_lowercase "$file")

    # If the file is not already lowercase
    if [ "$file" != "$lowercase_file" ]; then
        # Check if the lowercase version exists
        if [ -f "$lowercase_file" ]; then
            # Remove the uppercase version from Git
            git rm --cached "$file"
            echo "Removed (from Git): $file"
        else
            # Rename the file to lowercase
            git mv -f "$file" "$lowercase_file"
            echo "Renamed: $file -> $lowercase_file"
        fi
    fi
done

# Stage all changes
git add -A

echo "Cleanup complete. Please review the changes with 'git status' before committing."