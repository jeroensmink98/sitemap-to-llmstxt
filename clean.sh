#!/bin/bash

# Remove all .txt files in current directory that contain "llms" in their filename
# This is safer and more accurate than searching file content
find . -maxdepth 1 -type f -name "*llms*.txt" -delete

# Alternative approach using shell globbing (uncomment if you prefer):
# rm -f *llms*.txt