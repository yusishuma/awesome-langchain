#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE="/workspace/.last_pr_comment_check"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking PR #437 comments..."

if [ -f "$LAST_CHECK_FILE" ]; then
    last_check=$(cat "$LAST_CHECK_FILE")
    echo "Last check: $last_check"
fi

response=$(curl -s "$PR_URL")
total_comments=$(echo "$response" | grep -o '"id":' | wc -l)

if [ "$total_comments" -gt 1 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] NEW REPLY FOUND! PR #437 now has $total_comments comments."
    echo "Latest comments:"
    echo "$response" | python3 -c "
import json,sys
data=json.load(sys.stdin)
for c in data[-3:]:
    print(f\"[{c['created_at']}] {c['user']['login']}: {c['body'][:100]}...\")
"
    echo "Check PR: https://github.com/kyrolabs/awesome-langchain/pull/437"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No new replies yet. Total comments: $total_comments"
fi

date '+%Y-%m-%d %H:%M:%S' > "$LAST_CHECK_FILE"