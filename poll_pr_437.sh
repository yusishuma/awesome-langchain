#!/bin/bash
# 定时轮询 PR #437 的新评论
# 基线: 已知评论 id 4872113902 (yusishuma 自己的评论)
# 监控目标: 出现非 yusishuma 的新评论 (维护者回复)

LOG="/workspace/pr_437_replies.log"
BASELINE_ID=4872113902
WATCH_USER="yusishuma"
INTERVAL=600  # 10 分钟

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] 轮询启动, 基线评论id=$BASELINE_ID, 间隔=${INTERVAL}s" > "$LOG"

while true; do
  # 拉取 issue comments (PR 评论走 issues API)
  RESP=$(curl -s "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments")
  # 解析并查找 id 大于基线 且 作者非 watch_user 的评论
  NEW=$(echo "$RESP" | python3 -c "
import json,sys
try:
    data=json.load(sys.stdin)
except Exception as e:
    print('PARSE_ERR:', e)
    sys.exit(0)
if isinstance(data,dict):
    print('API_ERR:', data.get('message','unknown'))
    sys.exit(0)
baseline=$BASELINE_ID
for c in data:
    if c['id'] > baseline and c['user']['login'] != '$WATCH_USER':
        print('NEW_REPLY')
        print('id:', c['id'])
        print('author:', c['user']['login'])
        print('created_at:', c['created_at'])
        print('body:', c['body'])
        print('---END---')
")
  if echo "$NEW" | grep -q "NEW_REPLY"; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] 检测到新回复!" >> "$LOG"
    echo "$NEW" >> "$LOG"
    # 也拉取 review comments 以防有 review 上的评论
    RC=$(curl -s "https://api.github.com/repos/kyrolabs/awesome-langchain/pulls/437/comments")
    echo "--- review comments ---" >> "$LOG"
    echo "$RC" | python3 -c "
import json,sys
try:
    data=json.load(sys.stdin)
except: sys.exit(0)
if isinstance(data,list):
    for c in data:
        print('id:', c['id'], 'author:', c['user']['login'], 'at:', c['created_at'])
        print('body:', c['body'][:500])
" >> "$LOG"
  else
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] 暂无新回复 ($NEW)" >> "$LOG"
  fi
  sleep $INTERVAL
done
