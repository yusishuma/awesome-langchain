#!/bin/bash

INTERVAL=3600

echo "=== PR #437 评论监控服务 ==="
echo "开始时间: $(date)"
echo "检查间隔: ${INTERVAL}秒"
echo "按 Ctrl+C 停止"
echo ""

while true; do
    echo "--- 检查中 $(date) ---"
    python3 /workspace/check_pr_comments.py
    echo ""
    sleep $INTERVAL
done