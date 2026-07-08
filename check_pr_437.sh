#!/bin/bash
# 定时检查 PR #437 的新评论
# 记录已知评论ID，仅当有新评论时输出提醒

KNOWN_COMMENT_ID="4872113902"  # 你自己的评论ID
CHECK_INTERVAL=300             # 检查间隔（秒），默认5分钟

echo "=== 开始监控 PR #437 评论 ==="
echo "已知评论ID: $KNOWN_COMMENT_ID"
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

while true; do
    echo "[ $(date '+%Y-%m-%d %H:%M:%S') ] 正在检查..."

    # 获取 issue 级别评论
    COMMENTS=$(curl -s "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments")

    # 解析新评论（排除已知评论）
    NEW_COMMENTS=$(echo "$COMMENTS" | python3 -c "
import json, sys
data = json.load(sys.stdin)
known = '$KNOWN_COMMENT_ID'.split(',')
for c in data:
    cid = str(c['id'])
    if cid not in known:
        author = c['user']['login']
        body = c['body'][:200]
        created = c['created_at']
        print(f'  🆕 新评论!')
        print(f'  作者: {author}')
        print(f'  时间: {created}')
        print(f'  内容: {body}')
        print()
" 2>/dev/null)

    if [ -n "$NEW_COMMENTS" ]; then
        echo "=========================================="
        echo "  ⚠️  检测到新回复！"
        echo "=========================================="
        echo "$NEW_COMMENTS"
        echo "PR链接: https://github.com/kyrolabs/awesome-langchain/pull/437"
        echo "=========================================="
        # 发现新评论后继续监控，不退出
    else
        echo "[ $(date '+%Y-%m-%d %H:%M:%S') ] 暂无新回复"
    fi

    sleep $CHECK_INTERVAL
done
