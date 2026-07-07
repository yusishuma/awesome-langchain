#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE="/workspace/.last_pr_check"
CURRENT_COMMENTS="/workspace/.current_comments"

echo "=== 检查 PR #437 评论更新 ==="
echo "检查时间: $(date)"
echo ""

curl -s "$PR_URL" -o "$CURRENT_COMMENTS"

COMMENT_COUNT=$(jq '. | length' "$CURRENT_COMMENTS")
echo "当前评论总数: $COMMENT_COUNT"
echo ""

if [ -f "$LAST_CHECK_FILE" ]; then
    LAST_COUNT=$(cat "$LAST_CHECK_FILE")
    if [ "$COMMENT_COUNT" -gt "$LAST_COUNT" ]; then
        echo "🎉 发现新回复！"
        echo ""
        echo "最新评论:"
        jq '.[-1] | "用户: \(.user.login)\n时间: \(.created_at)\n内容:\n\(.body)"' "$CURRENT_COMMENTS" | sed 's/^"//;s/"$//'
        echo ""
    else
        echo "暂无新回复，上次检查时有 $LAST_COUNT 条评论"
    fi
else
    echo "首次检查，当前有 $COMMENT_COUNT 条评论"
    echo ""
    echo "所有评论:"
    jq -r '.[] | "---\n用户: \(.user.login)\n时间: \(.created_at)\n内容:\n\(.body)"' "$CURRENT_COMMENTS"
    echo ""
fi

echo "$COMMENT_COUNT" > "$LAST_CHECK_FILE"
echo "=== 检查完成 ==="