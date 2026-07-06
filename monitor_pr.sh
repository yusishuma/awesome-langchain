#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
USER_COMMENT_ID="4872113902"
LOG_FILE="/workspace/pr_check.log"

echo "========================================" >> "$LOG_FILE"
echo "监控启动时间: $(date)" >> "$LOG_FILE"
echo "PR: https://github.com/kyrolabs/awesome-langchain/pull/437" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

while true; do
    echo "检查时间: $(date)" >> "$LOG_FILE"
    
    COMMENTS=$(curl -s "$PR_URL")
    TOTAL_COMMENTS=$(echo "$COMMENTS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    
    echo "总评论数: $TOTAL_COMMENTS" >> "$LOG_FILE"
    
    if [ "$TOTAL_COMMENTS" -gt 1 ]; then
        echo "🎉 发现新回复！" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        echo "$COMMENTS" | python3 -c "
import sys, json
comments = json.load(sys.stdin)
for c in comments:
    if c['id'] != $USER_COMMENT_ID:
        print(f\"作者: {c['user']['login']}\")
        print(f\"时间: {c['created_at']}\")
        print(f\"内容:\")
        print(c['body'])
        print()
" >> "$LOG_FILE"
        echo "========================================" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        
        break
    else
        echo "暂无新回复，继续等待..." >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
    fi
    
    sleep 3600
done

echo "监控结束: $(date)" >> "$LOG_FILE"