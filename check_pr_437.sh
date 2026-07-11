#!/bin/bash
# 监控 https://github.com/kyrolabs/awesome-langchain/pull/437 的回复
# 用户(yusishuma)自己的评论 ID 与时间作为基准

OWNER="kyrolabs"
REPO="awesome-langchain"
PR_NUM="437"
MY_USER="yusishuma"
# 自己那条评论的 ID 和时间
MY_COMMENT_ID="4872113902"
MY_COMMENT_AT="2026-07-03T02:41:16Z"
# 监控状态文件
STATE_FILE="/workspace/.pr437_monitor.state"
# 轮询间隔(秒)
INTERVAL="${PR437_INTERVAL:-300}"

mkdir -p "$(dirname "$STATE_FILE")"
touch "$STATE_FILE"

log() { echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*"; }

check_once() {
  local resp
  resp=$(curl -sS -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${OWNER}/${REPO}/issues/${PR_NUM}/comments?per_page=100")

  # 检查 API 错误
  if echo "$resp" | jq -e 'type == "object" and has("message")' >/dev/null 2>&1; then
    log "API 错误: $(echo "$resp" | jq -r '.message')"
    return 1
  fi

  # 找出 my 评论之后、且不是 my 自己发的评论
  local new_replies
  new_replies=$(echo "$resp" | jq -r --arg me "$MY_USER" --arg since "$MY_COMMENT_AT" --arg myid "$MY_COMMENT_ID" '
    [ .[]
      | select(.created_at > $since)
      | select((.user.login | ascii_downcase) != ($me | ascii_downcase))
      | select((.id | tostring) != $myid)
      | {id, user: .user.login, created_at, body}
    ]')

  local count
  count=$(echo "$new_replies" | jq 'length')
  log "自你评论以来发现 ${count} 条新回复"

  if [ "$count" != "0" ] && [ "$count" != "null" ]; then
    echo "$new_replies" | jq -r '.[] | "─── 新回复 ───\n来自: \(.user)\n时间: \(.created_at)\nID: \(.id)\n内容:\n\(.body)\n"'
    # 记录已通知的 id
    echo "$new_replies" | jq -r '.[].id' | sort -u >> "$STATE_FILE"
  fi
}

# 首次检查
log "开始监控 ${OWNER}/${REPO}#${PR_NUM} (用户 ${MY_USER}, 间隔 ${INTERVAL}s)"
check_once

# 持续轮询
while true; do
  sleep "$INTERVAL"
  check_once || true
done
