#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LOG_FILE="/workspace/pr_monitor.log"
USER_LOGIN="yusishuma"
CHECK_INTERVAL=300

echo "[$(date)] Starting PR #437 monitor..." >> "$LOG_FILE"
echo "[$(date)] Checking every $CHECK_INTERVAL seconds" >> "$LOG_FILE"

KNOWN_COMMENTS=$(curl -s -H "Accept: application/vnd.github.v3+json" "$PR_URL" | python3 -c "import sys,json; c=json.load(sys.stdin); print(' '.join([str(x['id']) for x in c]))")
echo "[$(date)] Found $(echo $KNOWN_COMMENTS | wc -w) existing comments" >> "$LOG_FILE"

while true; do
    CURRENT_COMMENTS=$(curl -s -H "Accept: application/vnd.github.v3+json" "$PR_URL")
    COMMENT_COUNT=$(echo "$CURRENT_COMMENTS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
    
    NEW_COMMENTS=$(echo "$CURRENT_COMMENTS" | python3 -c "
import sys,json
c = json.load(sys.stdin)
known = set('$KNOWN_COMMENTS'.split())
new = []
for x in c:
    if str(x['id']) not in known:
        known.add(str(x['id']))
        if x['user']['login'] != '$USER_LOGIN':
            new.append({'author': x['user']['login'], 'time': x['created_at'], 'body': x['body']})
print(json.dumps(new))
")
    
    if [ "$NEW_COMMENTS" != "[]" ]; then
        echo "[$(date)] ALERT: NEW REPLY DETECTED!" >> "$LOG_FILE"
        echo "============================================" >> "$LOG_FILE"
        echo "$NEW_COMMENTS" >> "$LOG_FILE"
        echo "============================================" >> "$LOG_FILE"
        echo "[$(date)] Check PR: https://github.com/kyrolabs/awesome-langchain/pull/437" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        
        KNOWN_COMMENTS=$(echo "$CURRENT_COMMENTS" | python3 -c "import sys,json; c=json.load(sys.stdin); print(' '.join([str(x['id']) for x in c]))")
    else
        echo "[$(date)] No new replies (total: $COMMENT_COUNT)" >> "$LOG_FILE"
    fi
    
    sleep "$CHECK_INTERVAL"
done