#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE="/workspace/.last_pr_comment_id"

echo "=== Checking PR #437 comments at $(date) ==="

COMMENTS=$(curl -s "$PR_URL")

if [ -z "$COMMENTS" ]; then
    echo "Failed to fetch comments"
    exit 1
fi

COMMENT_COUNT=$(echo "$COMMENTS" | grep -o '"id"' | wc -l)
echo "Total comments: $COMMENT_COUNT"

LATEST_COMMENT=$(echo "$COMMENTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data:
    latest = data[-1]
    print(f\"Latest comment by {latest['user']['login']} at {latest['created_at']}\")
    print(f\"Body: {latest['body'][:200]}...\")
")

echo "$LATEST_COMMENT"

LATEST_ID=$(echo "$COMMENTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data:
    print(data[-1]['id'])
")

if [ -f "$LAST_CHECK_FILE" ]; then
    LAST_ID=$(cat "$LAST_CHECK_FILE")
    if [ "$LAST_ID" != "$LATEST_ID" ]; then
        echo "========================================"
        echo "NEW COMMENT DETECTED!"
        echo "Previous last ID: $LAST_ID"
        echo "New last ID: $LATEST_ID"
        echo "Check the PR: https://github.com/kyrolabs/awesome-langchain/pull/437"
        echo "========================================"
    else
        echo "No new comments since last check."
    fi
else
    echo "First check. Saving current latest ID."
fi

echo "$LATEST_ID" > "$LAST_CHECK_FILE"

echo ""