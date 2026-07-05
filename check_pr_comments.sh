#!/bin/bash

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
LAST_CHECK_FILE="/tmp/pr_437_last_check.txt"
CHECK_INTERVAL=300

echo "=== Starting PR comment checker ==="
echo "PR: $PR_URL"
echo "Checking every $CHECK_INTERVAL seconds..."
echo ""

get_comment_info() {
    curl -s -L "$PR_URL" 2>/dev/null | grep -o 'commented.*[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}' | sort -r
}

if [ ! -f "$LAST_CHECK_FILE" ]; then
    echo "Initializing..."
    INFO=$(get_comment_info)
    echo "$INFO" > "$LAST_CHECK_FILE"
    LINE_COUNT=$(echo "$INFO" | wc -l)
    echo "  Initial comment count: $LINE_COUNT"
    echo "$INFO"
    echo ""
fi

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking for new comments..."
    
    INFO=$(get_comment_info)
    LINE_COUNT=$(echo "$INFO" | wc -l)
    
    if [ "$LINE_COUNT" -eq 0 ]; then
        echo "  Failed to fetch data, retrying..."
        sleep $CHECK_INTERVAL
        continue
    fi
    
    echo "  Current comment count: $LINE_COUNT"
    
    if [ -f "$LAST_CHECK_FILE" ]; then
        LAST_INFO=$(cat "$LAST_CHECK_FILE")
        LAST_LINE_COUNT=$(echo "$LAST_INFO" | wc -l)
        echo "  Last check count: $LAST_LINE_COUNT"
        
        if [ "$LINE_COUNT" -gt "$LAST_LINE_COUNT" ]; then
            echo ""
            echo "=== NEW COMMENT DETECTED ==="
            echo "  Current: $LINE_COUNT comments"
            echo "  Previous: $LAST_LINE_COUNT comments"
            echo "  PR URL: $PR_URL"
            echo "=== NEW COMMENT DETECTED ==="
            echo ""
            echo "$INFO" > "$LAST_CHECK_FILE"
        else
            echo "  No new comments."
        fi
    else
        echo "$INFO" > "$LAST_CHECK_FILE"
    fi
    
    echo ""
    sleep $CHECK_INTERVAL
done