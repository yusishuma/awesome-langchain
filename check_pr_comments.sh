#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_COMMENT_FILE="/workspace/.last_pr_comment_id"

echo "=== 检查 PR #437 评论状态 ==="
echo "时间: $(date)"
echo ""

COMMENTS=$(curl -s "$PR_URL")

LATEST_COMMENT_ID=$(echo "$COMMENTS" | grep -o '"id":[0-9]*' | tail -1 | grep -o '[0-9]*')
LATEST_COMMENT_TIME=$(echo "$COMMENTS" | grep -A1 '"created_at"' | tail -1 | cut -d'"' -f4)
LATEST_COMMENT_USER=$(echo "$COMMENTS" | grep -B5 '"created_at"' | grep '"login"' | tail -1 | cut -d'"' -f4)

echo "最新评论信息："
echo "  用户: $LATEST_COMMENT_USER"
echo "  时间: $LATEST_COMMENT_TIME"
echo "  ID: $LATEST_COMMENT_ID"
echo ""

if [ -f "$LAST_COMMENT_FILE" ]; then
    LAST_ID=$(cat "$LAST_COMMENT_FILE")
    if [ "$LATEST_COMMENT_ID" -gt "$LAST_ID" ]; then
        echo "✅ 有新回复！"
        echo "查看地址: https://github.com/kyrolabs/awesome-langchain/pull/437"
        echo "$LATEST_COMMENT_ID" > "$LAST_COMMENT_FILE"
        exit 0
    else
        echo "❌ 暂无新回复"
        exit 1
    fi
else
    echo "首次检查，记录当前最新评论 ID"
    echo "$LATEST_COMMENT_ID" > "$LAST_COMMENT_FILE"
    exit 1
fi