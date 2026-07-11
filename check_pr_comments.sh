#!/bin/bash

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
LAST_COMMENT_FILE="/tmp/pr437_last_comment.txt"

echo "Checking PR #437 for new comments..."

COMMENTS=$(curl -s "$PR_URL" | grep -o 'commented.*[0-9]* [A-Za-z]* [0-9]*' | tail -5)

if [ ! -f "$LAST_COMMENT_FILE" ]; then
    echo "$COMMENTS" > "$LAST_COMMENT_FILE"
    echo "Initial check complete. Comments recorded."
    exit 0
fi

OLD_COMMENTS=$(cat "$LAST_COMMENT_FILE")

if [ "$COMMENTS" != "$OLD_COMMENTS" ]; then
    echo "=== NEW COMMENT DETECTED ==="
    echo "$COMMENTS"
    echo "=== END OF NEW COMMENTS ==="
    echo "$COMMENTS" > "$LAST_COMMENT_FILE"
else
    echo "No new comments found."
fi