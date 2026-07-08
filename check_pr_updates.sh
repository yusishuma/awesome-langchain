#!/bin/bash

# PR #437 监控脚本
PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
PR_API="https://api.github.com/repos/kyrolabs/awesome-langchain/pulls/437"
COMMENTS_API="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"

echo "========================================="
echo "PR #437 更新监控 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo ""

# 获取PR基本信息
PR_INFO=$(curl -s "$PR_API")
STATE=$(echo "$PR_INFO" | grep -o '"state":"[^"]*"' | cut -d'"' -f4 | head -1)
TITLE=$(echo "$PR_INFO" | grep -o '"title":"[^"]*"' | cut -d'"' -f4 | head -1)

echo "PR标题: $TITLE"
echo "PR状态: $STATE"
echo ""

# 获取评论数量
COMMENTS=$(curl -s "$COMMENTS_API")
COMMENT_COUNT=$(echo "$COMMENTS" | grep -o '"login"' | wc -l)

echo "评论总数: $COMMENT_COUNT"
echo ""

if [ "$COMMENT_COUNT" -gt 1 ]; then
    echo "最新评论:"
    echo "$COMMENTS" | grep -A 5 '"created_at"' | tail -20
    echo ""
    echo "⚠️  有新的回复! 请查看: $PR_URL"
else
    echo "暂无新回复"
fi

echo ""
echo "PR链接: $PR_URL"
echo "========================================="