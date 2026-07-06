#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_ID_FILE="/workspace/.last_pr_comment_id"
LOG_FILE="/workspace/pr_monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

get_comments() {
    curl -s -H "User-Agent: PR-Monitor/1.0" "$PR_URL"
}

init_last_id() {
    if [ ! -f "$LAST_ID_FILE" ]; then
        comments=$(get_comments)
        last_id=$(echo "$comments" | python3 -c "import sys,json; data=json.load(sys.stdin); print(max(c['id'] for c in data))" 2>/dev/null)
        if [ -n "$last_id" ]; then
            echo "$last_id" > "$LAST_ID_FILE"
            log "Initialized with last comment ID: $last_id"
        else
            log "Failed to initialize - no comments found"
        fi
    fi
}

check_replies() {
    comments=$(get_comments)
    current_last_id=$(cat "$LAST_ID_FILE" 2>/dev/null || echo "0")
    
    new_comments=$(echo "$comments" | python3 -c "
import sys,json
data = json.load(sys.stdin)
current_last = $current_last_id
new_items = [c for c in data if c['id'] > current_last]
if new_items:
    for item in new_items:
        print(f\"AUTHOR: {item['user']['login']}\")
        print(f\"TIME: {item['created_at']}\")
        body = item['body'][:500] + '...' if len(item['body']) > 500 else item['body']
        print(f\"CONTENT: {body}\")
        print(f\"URL: {item['html_url']}\")
        print('---')
    print(f\"MAX_ID: {max(c['id'] for c in data)}\")
else:
    print('NO_NEW')
")
    
    if echo "$new_comments" | grep -q "MAX_ID:"; then
        max_id=$(echo "$new_comments" | grep "MAX_ID:" | awk '{print $2}')
        echo "$max_id" > "$LAST_ID_FILE"
        log "=== NEW REPLIES FOUND ==="
        echo "$new_comments" | grep -v "MAX_ID:" >> "$LOG_FILE"
        log "=== END OF NEW REPLIES ==="
        return 0
    elif echo "$new_comments" | grep -q "NO_NEW"; then
        log "No new replies yet"
        return 1
    else
        log "Error checking comments: $new_comments"
        return 1
    fi
}

log "=== PR Comment Monitor Started ==="
log "Monitoring: https://github.com/kyrolabs/awesome-langchain/pull/437"
log "Checking every 30 minutes..."

init_last_id

while true; do
    check_replies
    sleep 1800
done