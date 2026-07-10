#!/bin/bash

REPO="kyrolabs/awesome-langchain"
PR_NUMBER="437"
LAST_CHECK_FILE="/workspace/.last_pr_comment_id"
LOG_FILE="/workspace/pr_check_log.txt"
CHECK_INTERVAL=3600

echo "=== PR Monitor Started ===" | tee "$LOG_FILE"
echo "Monitoring PR #$PR_NUMBER in $REPO" | tee -a "$LOG_FILE"
echo "Checking every $CHECK_INTERVAL seconds..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

while true; do
    echo "=== Check at $(date) ===" | tee -a "$LOG_FILE"
    
    COMMENTS=$(curl -s "https://api.github.com/repos/$REPO/issues/$PR_NUMBER/comments")
    LAST_ID=$(cat "$LAST_CHECK_FILE" 2>/dev/null || echo "0")
    
    NEW_COMMENTS=$(echo "$COMMENTS" | python3 -c "
import sys,json
comments = json.load(sys.stdin)
new_count = 0
last_id = int('$LAST_ID')
for c in comments:
    if c['id'] > last_id:
        new_count += 1
print(new_count)
")
    
    if [ "$NEW_COMMENTS" -gt 0 ]; then
        echo "✅ NEW REPLY DETECTED! ($NEW_COMMENTS new comment(s))" | tee -a "$LOG_FILE"
        echo "$COMMENTS" | python3 -c "
import sys,json
comments = json.load(sys.stdin)
last_id = int('$LAST_ID')
for c in comments:
    if c['id'] > last_id:
        print(f\"  [{c['created_at']}] @{c['user']['login']}:\")
        body = c['body'].replace('\r', '').strip()
        if len(body) > 300:
            body = body[:300] + '...'
        print(f\"    {body}\")
        print()
" | tee -a "$LOG_FILE"
        echo "PR URL: https://github.com/$REPO/pull/$PR_NUMBER" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    else
        echo "No new replies." | tee -a "$LOG_FILE"
    fi
    
    echo "$COMMENTS" | python3 -c "
import sys,json
comments = json.load(sys.stdin)
if comments:
    print(max(c['id'] for c in comments))
else:
    print(0)
" > "$LAST_CHECK_FILE"

    sleep $CHECK_INTERVAL
done
