#!/bin/bash
# Black2 Hash Calculator - Bash Version
# For AI agents on Linux/Mac environments
# 
# Usage:
#   bash calculate_hash.sh <file_path>
#
# Output (JSON format):
#   {"file":"test.txt","size":1024,"sha256":"abc123...","algorithm":"SHA-256"}

if [ -z "$1" ]; then
    echo "Usage: $0 <file_path>"
    echo ""
    echo "Calculate SHA-256 hash for Black2 protocol"
    exit 1
fi

FILE_PATH="$1"

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\":\"File not found: $FILE_PATH\"}"
    exit 1
fi

# Get file size
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null)

# Calculate SHA-256 hash
HASH=$(shasum -a 256 "$FILE_PATH" 2>/dev/null | awk '{print $1}')
if [ -z "$HASH" ]; then
    HASH=$(sha256sum "$FILE_PATH" 2>/dev/null | awk '{print $1}')
fi

if [ -z "$HASH" ]; then
    echo "{\"error\":\"Failed to calculate hash\"}"
    exit 1
fi

# Output JSON
echo "{\"file\":\"$FILE_PATH\",\"size\":$FILE_SIZE,\"sha256\":\"$HASH\",\"algorithm\":\"SHA-256\"}"
