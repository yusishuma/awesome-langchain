#!/bin/bash

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL=3600
LAST_COMMENT_COUNT_FILE="/tmp/pr437_last_count.txt"

echo "=== 定时检查 PR #437 评论状态 ==="
echo "PR: $PR_URL"
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "开始时间: $(date)"
echo "================================="
echo ""

if [ ! -f "$LAST_COMMENT_COUNT_FILE" ]; then
    echo "0" > "$LAST_COMMENT_COUNT_FILE"
fi

while true; do
    echo "[$(date)] 正在检查..."
    
    COMMENT_COUNT=$(curl -s "$PR_URL" 2>/dev/null | grep -o 'comment' | wc -l)
    
    if [ -z "$COMMENT_COUNT" ]; then
        echo "  连接失败，重试中..."
        sleep 60
        continue
    fi
    
    LAST_COUNT=$(cat "$LAST_COMMENT_COUNT_FILE")
    
    if [ "$COMMENT_COUNT" -gt "$LAST_COUNT" ]; then
        echo "  发现新评论！评论数: $LAST_COUNT -> $COMMENT_COUNT"
        echo "  PR链接: $PR_URL"
        echo ""
        
        echo "$COMMENT_COUNT" > "$LAST_COMMENT_COUNT_FILE"
        
        curl -s "$PR_URL" 2>/dev/null | grep -oP '(?<=commented ).*?(?=:)' | head -20
        
        echo ""
        echo "---------------------------------"
    else
        echo "  暂无新评论，当前评论数: $COMMENT_COUNT"
        echo ""
    fi
    
    echo "等待下次检查... ($CHECK_INTERVAL秒)"
    echo "================================="
    echo ""
    
    sleep "$CHECK_INTERVAL"
done