#!/bin/bash

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
LAST_HASH_FILE="/tmp/pr437_last_hash.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查 PR #437 评论..."

PAGE_CONTENT=$(curl -s -L "$PR_URL" 2>/dev/null | grep -A 50 'Conversation' | grep -B 5 -A 500 'participants' | head -1000)
CURRENT_HASH=$(echo "$PAGE_CONTENT" | md5sum | cut -d' ' -f1)

if [ ! -f "$LAST_HASH_FILE" ]; then
    echo "$CURRENT_HASH" > "$LAST_HASH_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 初始记录已创建"
    exit 0
fi

LAST_HASH=$(cat "$LAST_HASH_FILE")

if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 发现新评论！"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] PR链接: $PR_URL"
    echo "$CURRENT_HASH" > "$LAST_HASH_FILE"
    
    echo "=== 最新评论摘要 ==="
    echo "$PAGE_CONTENT" | grep -o 'href="/kyrolabs/awesome-langchain/pull/437#issuecomment-[0-9]*"' | head -5
    echo ""
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 暂无新评论"
fi
