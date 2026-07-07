#!/bin/bash

REPO="kyrolabs/awesome-langchain"
PR_NUMBER="437"
LAST_CHECK_FILE="/tmp/pr_${PR_NUMBER}_last_comment"

get_latest_comment() {
    curl -s "https://api.github.com/repos/${REPO}/issues/${PR_NUMBER}/comments" | python3 -c "
import sys, json
comments = json.load(sys.stdin)
if comments:
    latest = max(comments, key=lambda x: x['created_at'])
    print(f\"{latest['created_at']}|{latest['user']['login']}|{latest['body'][:200]}\")
else:
    print(\"NO_COMMENTS\")
"
}

if [ ! -f "$LAST_CHECK_FILE" ]; then
    echo "首次检查，记录当前最新评论..."
    get_latest_comment > "$LAST_CHECK_FILE"
    exit 0
fi

current=$(get_latest_comment)
last=$(cat "$LAST_CHECK_FILE")

if [ "$current" != "$last" ]; then
    echo "========== 检测到新评论！ =========="
    IFS='|' read -r date author body <<< "$current"
    echo "时间: $date"
    echo "作者: $author"
    echo "内容: $body"
    echo "====================================="
    echo "$current" > "$LAST_CHECK_FILE"
else
    echo "暂无新评论 (上次检查: $(date -r "$LAST_CHECK_FILE"))"
fi