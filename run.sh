#!/bin/bash

# Bash equivalent of run.ps1 for Linux/macOS
# Usage: ./run.sh <target_folder>

if [ $# -eq 0 ]; then
    echo "Error: Target folder argument required"
    echo "Usage: $0 <target_folder>"
    exit 1
fi

TARGET_FOLDER="$1"

# Check if the folder exists
if [ ! -d "$TARGET_FOLDER" ]; then
    echo "Error: The specified folder '$TARGET_FOLDER' does not exist."
    exit 1
fi

echo "================================================"
echo " Starting Hybrid Code Clone Detection Tool"
echo " Target Folder : $TARGET_FOLDER"
echo " Output File   : final_result.txt"
echo "================================================"
echo ""
echo "[1/2] Initializing environment and loading files..."

# Measure time taken
START_TIME=$(date +%s.%N)

# Run the python tool
python -m my_tool "$TARGET_FOLDER" --output final_result.txt --mode file

END_TIME=$(date +%s.%N)
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)

echo ""
echo "[2/2] Processing finished!"
echo "================================================"
echo " Analysis Complete!"
echo " Time Elapsed : ${ELAPSED}s"
echo " Results successfully saved to: final_result.txt"
echo "================================================"
