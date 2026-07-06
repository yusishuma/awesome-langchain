#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE="/workspace/.last_pr_comment_check"
USER_COMMENT_ID="4872113902"

echo "========================================"
echo "检查时间: $(date)"
echo "PR: https://github.com/kyrolabs/awesome-langchain/pull/437"
echo "========================================"

echo ""
echo "获取最新评论..."
echo ""

COMMENTS=$(curl -s "$PR_URL")
TOTAL_COMMENTS=$(echo "$COMMENTS" | grep -c '"id":')

echo "总评论数: $TOTAL_COMMENTS"
echo ""

if [ "$TOTAL_COMMENTS" -gt 1 ]; then
    echo "🎉 发现新回复！"
    echo ""
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
"
else
    echo "暂无新回复，上次评论仍为你提交的询问消息。"
    echo "继续等待维护者回复..."
fi

echo ""
echo "========================================"
echo ""

echo "$(date)" > "$LAST_CHECK_FILE"