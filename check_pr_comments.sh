#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE="/workspace/.last_pr_comment_check"
COMMENT_COUNT_FILE="/workspace/.pr_comment_count"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 正在检查 PR #437 的新评论..."

current_count=$(curl -s "$PR_URL" | jq '. | length')

if [ -f "$COMMENT_COUNT_FILE" ]; then
    previous_count=$(cat "$COMMENT_COUNT_FILE")
else
    previous_count=0
fi

echo "当前评论数: $current_count, 上次检查时: $previous_count"

if [ "$current_count" -gt "$previous_count" ]; then
    echo "=================================================="
    echo "发现新评论！"
    echo "=================================================="
    curl -s "$PR_URL" | jq '.[] | {user: .user.login, time: .created_at, body: .body}'
    echo "=================================================="
    echo "PR 链接: https://github.com/kyrolabs/awesome-langchain/pull/437"
    echo "=================================================="
else
    echo "暂无新评论，继续等待..."
fi

echo "$current_count" > "$COMMENT_COUNT_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$LAST_CHECK_FILE"