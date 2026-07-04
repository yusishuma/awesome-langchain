#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_COMMENT_FILE="/workspace/.last_pr_comment_id"
CURRENT_COMMENTS_FILE="/workspace/.current_pr_comments.json"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking PR #437 comments..."

curl -s "$PR_URL" > "$CURRENT_COMMENTS_FILE"

if [ ! -f "$LAST_COMMENT_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] First check, recording current comment ID..."
    cat "$CURRENT_COMMENTS_FILE" | python3 -c "import sys,json; comments=json.load(sys.stdin); print(comments[-1]['id'] if comments else 0)" > "$LAST_COMMENT_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Current comments:"
    cat "$CURRENT_COMMENTS_FILE" | python3 -c "
import sys, json
comments = json.load(sys.stdin)
if comments:
    for c in comments:
        print(f\"  - {c['user']['login']} at {c['created_at']}: {c['body'][:100]}...\")
else:
    print('  No comments yet')
"
    exit 0
fi

last_id=$(cat "$LAST_COMMENT_FILE")
current_id=$(cat "$CURRENT_COMMENTS_FILE" | python3 -c "import sys,json; comments=json.load(sys.stdin); print(comments[-1]['id'] if comments else 0)")

if [ "$current_id" -gt "$last_id" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] NEW COMMENT FOUND!"
    cat "$CURRENT_COMMENTS_FILE" | python3 -c "
import sys, json
comments = json.load(sys.stdin)
last_id = $last_id
for c in comments:
    if c['id'] > last_id:
        print(f\"\\nAuthor: {c['user']['login']}\")
        print(f\"Time: {c['created_at']}\")
        print(f\"Comment: {c['body']}\")
        print(f\"URL: {c['html_url']}\")
"
    echo "$current_id" > "$LAST_COMMENT_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Notification: New comment detected on PR #437!" | wall
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No new comments yet. Last checked ID: $current_id"
fi

rm "$CURRENT_COMMENTS_FILE"