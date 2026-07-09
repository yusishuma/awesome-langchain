#!/bin/bash

INTERVAL=3600

echo "Starting PR #437 comment watcher..."
echo "Checking every $INTERVAL seconds..."
echo "Press Ctrl+C to stop."
echo ""

while true; do
    /workspace/check_pr_comments.sh
    sleep $INTERVAL
done