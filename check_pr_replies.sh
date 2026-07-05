#!/bin/bash

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL=300
LAST_COMMENT_COUNT=0

echo "Starting PR reply monitor for https://github.com/kyrolabs/awesome-langchain/pull/437"
echo "Checking every ${CHECK_INTERVAL} seconds..."
echo ""

fetch_page() {
    curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "$PR_URL"
}

extract_comments() {
    echo "$1" | python3 << 'PYTHON_SCRIPT'
import sys, re

html = sys.stdin.read()

comment_body_pattern = re.compile(r'comment-body')
count = len(comment_body_pattern.findall(html))

print(f'  Detected {count} comment elements')
PYTHON_SCRIPT
}

get_comment_count() {
    echo "$1" | python3 -c "
import sys, re
html = sys.stdin.read()
pattern = re.compile(r'comment-body')
print(len(pattern.findall(html)))
"
}

while true; do
    PAGE=$(fetch_page)
    
    if [ -z "$PAGE" ] || [ "${#PAGE}" -lt 1000 ]; then
        echo "[$(date)] Error: Could not fetch page"
        sleep $CHECK_INTERVAL
        continue
    fi
    
    CURRENT_COUNT=$(get_comment_count "$PAGE")
    
    if [ -z "$CURRENT_COUNT" ] || [ "$CURRENT_COUNT" -eq 0 ]; then
        echo "[$(date)] Error: Could not parse comments"
        sleep $CHECK_INTERVAL
        continue
    fi
    
    if [ "$LAST_COMMENT_COUNT" -eq 0 ]; then
        LAST_COMMENT_COUNT=$CURRENT_COUNT
        echo "[$(date)] Initial check complete"
        extract_comments "$PAGE"
        echo ""
    elif [ "$CURRENT_COUNT" -gt "$LAST_COMMENT_COUNT" ]; then
        echo "[$(date)] ================================================"
        echo "[$(date)] NEW REPLY DETECTED!"
        echo "[$(date)] ================================================"
        extract_comments "$PAGE"
        echo ""
        echo "[$(date)] ================================================"
        LAST_COMMENT_COUNT=$CURRENT_COUNT
    else
        echo "[$(date)] No new replies yet (current: ${CURRENT_COUNT})"
    fi
    
    sleep $CHECK_INTERVAL
done