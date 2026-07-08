#!/bin/bash

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL=300
LAST_COMMENT_COUNT=0

echo "开始定时检查 PR #437 的新回复..."
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "按 Ctrl+C 停止检查"
echo ""

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 正在检查..."
    
    HTML=$(curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "$PR_URL")
    
    if [ -z "$HTML" ]; then
        echo "获取页面失败，等待重试..."
        sleep $CHECK_INTERVAL
        continue
    fi
    
    COMMENT_COUNT=$(echo "$HTML" | grep -o 'js-comment-body' | wc -l)
    
    if [ $LAST_COMMENT_COUNT -eq 0 ]; then
        echo "当前评论数: $COMMENT_COUNT"
        LAST_COMMENT_COUNT=$COMMENT_COUNT
        
        COMMENT_AUTHORS=$(echo "$HTML" | grep -o 'class="author"[^>]*href="/[^"]*"' | head -20)
        if [ -n "$COMMENT_AUTHORS" ]; then
            echo "评论作者:"
            echo "$COMMENT_AUTHORS" | sed 's/.*href="\/\([^"]*\)".*/  @\1/' | uniq | head -10
        fi
    elif [ $COMMENT_COUNT -gt $LAST_COMMENT_COUNT ]; then
        echo "✓ 发现新回复！评论数从 $LAST_COMMENT_COUNT 增加到 $COMMENT_COUNT"
        echo "建议立即查看: $PR_URL"
        LAST_COMMENT_COUNT=$COMMENT_COUNT
    else
        echo "暂无新回复，当前评论数: $COMMENT_COUNT"
    fi
    
    sleep $CHECK_INTERVAL
done