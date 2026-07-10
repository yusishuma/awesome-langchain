#!/usr/bin/env bash
# 单实例启动器：使用 flock 防止重复启动
LOCK=/workspace/.pr437-monitor.lock
LOG=/workspace/.pr437-monitor.log
PID=/workspace/.pr437-monitor.pid

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "已有实例在运行 (pid=$(cat $PID 2>/dev/null))"
  exit 0
fi
echo $$ > "$PID"
exec /workspace/.pr437-monitor.sh run
