#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE="/workspace/.last_pr_comment_check"

get_latest_comment() {
    curl -s "$PR_URL" | grep -o '"created_at":"[^"]*"' | tail -1 | cut -d'"' -f4
}

get_all_comments() {
    curl -s "$PR_URL" | python3 -c "
import sys, json
comments = json.load(sys.stdin)
for c in comments:
    print(f\"[{c['created_at']}] @{c['user']['login']}: {c['body'][:100]}...\")
"
}

if [ ! -f "$LAST_CHECK_FILE" ]; then
    echo "首次检查，记录当前最新评论时间..."
    get_latest_comment > "$LAST_CHECK_FILE"
    echo ""
    echo "=== 当前评论列表 ==="
    get_all_comments
    echo ""
    echo "已设置定时检查，每5分钟查询一次新回复..."
    echo "按 Ctrl+C 停止监控"
else
    last_time=$(cat "$LAST_CHECK_FILE")
    current_time=$(get_latest_comment)
    
    if [ "$current_time" != "$last_time" ]; then
        echo ""
        echo "=========================================="
        echo "发现新回复！时间: $current_time"
        echo "=========================================="
        echo ""
        get_all_comments
        echo "$current_time" > "$LAST_CHECK_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 暂无新回复..."
    fi
fi