#!/usr/bin/env bash
# 监控 kyrolabs/awesome-langchain PR #437 是否有人回复 yusishuma 的评论
set -u

PR_REPO="kyrolabs/awesome-langchain"
PR_NUMBER=437
WATCH_USER="yusishuma"
POLL_INTERVAL="${POLL_INTERVAL:-300}"   # 默认 5 分钟
LOG_FILE="/workspace/.pr437-monitor.log"
STATE_FILE="/workspace/.pr437-monitor.state"
LAST_NOTIFY_FILE="/workspace/.pr437-monitor.lastseen"

GH_TOKEN="${GH_TOKEN:-ghu_ZPwvCLixEBQ3Ad0ye3eTaNtML0fqeE3MselL}"
AUTH_HEADER=(-H "Authorization: token ${GH_TOKEN}" -H "Accept: application/vnd.github.v3+json")

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "[$ts] $*" | tee -a "$LOG_FILE"
}

# 拉取并解析评论：返回按时间排序的 comment JSON 数组
fetch_comments() {
  local kind="$1"   # issue | review
  local url
  if [ "$kind" = "issue" ]; then
    url="https://api.github.com/repos/${PR_REPO}/issues/${PR_NUMBER}/comments?per_page=100"
  else
    url="https://api.github.com/repos/${PR_REPO}/pulls/${PR_NUMBER}/comments?per_page=100"
  fi
  curl -s "${AUTH_HEADER[@]}" "$url"
}

# 计算"我发的评论"中最新一条的 id，作为锚点
my_latest_id() {
  {
    fetch_comments issue | jq -c --arg u "$WATCH_USER" \
      '[.[] | select(.user.login == $u) | .id] | max // 0'
    fetch_comments review | jq -c --arg u "$WATCH_USER" \
      '[.[] | select(.user.login == $u) | .id] | max // 0'
  } | awk 'BEGIN{m=0} {if($1+0>m) m=$1+0} END{print m}'
}

# 合并 issue + review 评论为一个按时间排序的数组
all_comments() {
  {
    fetch_comments issue | jq -c '.[] | {id, user: .user.login, created_at, body, kind: "issue"}'
    fetch_comments review | jq -r '.[]? | empty' >/dev/null  # guard
    fetch_comments review | jq -c '.[] | {id, user: .user.login, created_at, body, kind: "review"}'
  } | jq -s 'sort_by(.created_at)'
}

# 初始化基线（首次运行记录当前所有评论，不告警）
init_baseline() {
  log "初始化基线评论列表..."
  all_comments > "$STATE_FILE"
  my_latest_id > "$LAST_NOTIFY_FILE"
  local cnt
  cnt=$(jq 'length' "$STATE_FILE")
  log "基线已保存：共 $cnt 条评论。我的最新评论 id = $(cat "$LAST_NOTIFY_FILE")"
}

# 检查是否有新回复（别人在我评论之后的回复）
check_replies() {
  local latest_my_id
  latest_my_id=$(cat "$LAST_NOTIFY_FILE" 2>/dev/null || echo 0)

  local current
  current=$(all_comments)
  echo "$current" > "$STATE_FILE.tmp"
  mv "$STATE_FILE.tmp" "$STATE_FILE"

  # 找出 id 大于我最新评论 id 的评论中、作者不是我的新评论
  local replies
  replies=$(echo "$current" | jq -c --argjson mid "$latest_my_id" --arg u "$WATCH_USER" \
    '[.[] | select(.id > $mid) | select(.user.login != $u)]')

  local count
  count=$(echo "$replies" | jq 'length')
  if [ "$count" -gt 0 ]; then
    log "检测到 $count 条新回复："
    echo "$replies" | jq -r '.[] | "  • [\(.created_at)] @\(.user.login) (\(.kind)): \(.body)"'
    log "PR 链接：https://github.com/${PR_REPO}/pull/${PR_NUMBER}"
    # 把 latest_my_id 推进到这些回复之前我的最大评论 id，避免重复告警
    local new_anchor
    new_anchor=$(echo "$current" | jq -r --arg u "$WATCH_USER" \
      '[.[] | select(.user.login == $u)] | map(.id) | max // 0')
    echo "$new_anchor" > "$LAST_NOTIFY_FILE"
  else
    log "无新回复（我的最新评论 id = $latest_my_id，当前总评论 $(echo "$current" | jq 'length') 条）"
  fi
}

case "${1:-run}" in
  init)
    init_baseline
    ;;
  once)
    if [ ! -f "$STATE_FILE" ]; then init_baseline; else check_replies; fi
    ;;
  run)
    if [ ! -f "$STATE_FILE" ]; then init_baseline; fi
    log "开始监控，间隔 ${POLL_INTERVAL} 秒"
    while true; do
      check_replies
      sleep "$POLL_INTERVAL"
    done
    ;;
  *)
    echo "Usage: $0 {init|once|run}" >&2
    exit 1
    ;;
esac
