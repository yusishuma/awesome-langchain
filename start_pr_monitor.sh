#!/bin/bash

echo "启动 PR #437 评论监控..."
echo "监控脚本将每小时检查一次是否有新回复"
echo "按 Ctrl+C 停止监控"

chmod +x /workspace/check_pr_comments.sh

while true; do
    /workspace/check_pr_comments.sh
    echo "--------------------------------------------------"
    echo "下次检查将在 1 小时后进行..."
    sleep 3600
done