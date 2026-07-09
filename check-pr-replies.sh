#!/usr/bin/env bash
# check-pr-replies.sh
# 用法: ./check-pr-replies.sh
# 需要: gh CLI 已认证 (gh auth login)
# 推荐搭配 crontab: */30 * * * * /path/to/check-pr-replies.sh >> /tmp/pr-watch.log 2>&1

set -euo pipefail

REPO="kyrolabs/awesome-langchain"
PR=437
STATE_FILE="/tmp/pr-${PR}-last-seen-comments.txt"

# 当前评论数 (含 issue 评论)
CURRENT=$(gh pr view "$PR" --repo "$REPO" --json comments --jq '.comments | length')

# 上次记录的评论数
if [[ -f "$STATE_FILE" ]]; then
  LAST=$(cat "$STATE_FILE")
else
  LAST=0
fi

echo "[$(date '+%F %T')] PR #${PR} comments: ${CURRENT} (last seen: ${LAST})"

if (( CURRENT > LAST )); then
  echo "🔔 检测到新评论！请查看: https://github.com/${REPO}/pull/${PR}"
  # 系统通知 (macOS 示例, Linux 可换 notify-send)
  command -v osascript >/dev/null && osascript -e "display notification \"PR #${PR} 有新评论\" with title \"GitHub Watcher\""
  command -v notify-send >/dev/null && notify-send "GitHub Watcher" "PR #${PR} 有新评论"
fi

echo "$CURRENT" > "$STATE_FILE"
