#!/bin/bash
LOG_FILE="/workspace/pr_monitor.log"

echo "Starting PR #437 monitoring..." | tee -a "$LOG_FILE"

while true; do
    python3 /workspace/check_pr_comments.py | tee -a "$LOG_FILE"
    sleep 3600
done