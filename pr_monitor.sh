#!/bin/bash
# PR监控定时任务脚本
# 建议每4-6小时运行一次

SCRIPT_DIR="/workspace"
LOG_FILE="$SCRIPT_DIR/pr_monitor.log"
PYTHON_SCRIPT="$SCRIPT_DIR/check_pr_status.py"

echo "开始监控 PR #437..." | tee -a "$LOG_FILE"

# 运行Python监控脚本
python3 "$PYTHON_SCRIPT" | tee -a "$LOG_FILE"

echo "检查完成: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"