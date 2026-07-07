#!/bin/bash

INTERVAL=14400

echo "PR #437 监控已启动，每 ${INTERVAL} 秒检查一次..."
echo "日志文件: /workspace/pr_check_logs.txt"

while true; do
    /workspace/check_pr_comments.sh >> /workspace/pr_check_logs.txt 2>&1
    sleep $INTERVAL
done