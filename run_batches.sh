#!/bin/bash

# Bash equivalent of run_batches.ps1 for Linux/macOS
# Processes 10 predefined batches from SOCO dataset

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOCO="$ROOT/soco"

# Define all 97 ground-truth pairs grouped into 10 batches of 10 (last = 7)
declare -a BATCH_1=(003 004 005 006 008 010 014 021 015 023 016 024 017 022 030 032 033 034 042 044)
declare -a BATCH_2=(043 251 045 047 048 051 048 059 048 183 048 185 048 257 048 258 049 050 051 059)
declare -a BATCH_3=(051 183 051 185 051 257 051 258 052 053 059 183 059 185 059 257 059 258 061 216)
declare -a BATCH_4=(062 064 069 070 078 079 084 085 086 087 086 153 086 155 086 222 086 242 086 243)
declare -a BATCH_5=(087 153 087 155 087 222 087 242 087 243 089 090 094 098 101 212 103 105 106 111)
declare -a BATCH_6=(107 108 107 112 107 113 108 112 108 113 112 113 117 119 131 133 135 174 136 173)
declare -a BATCH_7=(137 171 140 142 143 145 146 147 148 150 153 155 153 222 153 242 153 243 155 222)
declare -a BATCH_8=(155 242 155 243 158 161 159 250 175 180 181 182 183 185 183 257 183 258 185 257)
declare -a BATCH_9=(185 258 188 190 191 193 195 218 201 209 202 208 211 216 221 224 222 242 222 243)
declare -a BATCH_10=(228 230 232 233 235 237 238 240 242 243 244 246 257 258)

# Array of arrays
declare -a BATCHES=(BATCH_1 BATCH_2 BATCH_3 BATCH_4 BATCH_5 BATCH_6 BATCH_7 BATCH_8 BATCH_9 BATCH_10)

for ((i = 0; i < ${#BATCHES[@]}; i++)); do
    BATCH_NUM=$((i + 1))
    BATCH_TESTS_DIR="$ROOT/batch_tests"
    
    # Create batch_tests directory if it doesn't exist
    mkdir -p "$BATCH_TESTS_DIR"
    
    TEST_DIR="$BATCH_TESTS_DIR/test$BATCH_NUM"
    REPORT_FILE="$BATCH_TESTS_DIR/test${BATCH_NUM}.txt"
    
    echo "=== Batch $BATCH_NUM ==="
    
    # Clear the test dir
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
    fi
    mkdir -p "$TEST_DIR"
    
    # Get the batch array name and collect unique folder IDs
    BATCH_VAR="${BATCHES[$i]}"
    declare -n BATCH_ARRAY="$BATCH_VAR"
    
    # Get unique IDs and sort them
    UNIQUE_IDS=($(printf '%s\n' "${BATCH_ARRAY[@]}" | sort -u))
    
    # Copy folders
    for id in "${UNIQUE_IDS[@]}"; do
        SRC="$SOCO/$id"
        if [ -d "$SRC" ]; then
            cp -r "$SRC" "$TEST_DIR/$id"
        else
            echo "Warning: SOCO folder not found: $SRC"
        fi
    done
    
    echo "  Copied ${#UNIQUE_IDS[@]} folders into test$BATCH_NUM"
    
    # Run the tool
    echo "  Running tool on test$BATCH_NUM ..."
    python -m my_tool "$TEST_DIR" --threshold 50 --mode file --output "$REPORT_FILE" 2>&1
    echo "  Report saved to test${BATCH_NUM}.txt"
    echo ""
done

echo "All batches done."
