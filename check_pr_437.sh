#!/bin/bash

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
LOG_FILE="/workspace/pr_437_check.log"
LAST_COMMENT_COUNT_FILE="/workspace/pr_437_last_count.txt"

echo "=====================================" >> "$LOG_FILE"
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

PAGE_CONTENT=$(curl -sL "$PR_URL" --max-time 30)

if [ -z "$PAGE_CONTENT" ]; then
    echo "错误: 无法访问PR页面" >> "$LOG_FILE"
    echo "-------------------------------------" >> "$LOG_FILE"
    exit 1
fi

COMMENT_COUNT=$(echo "$PAGE_CONTENT" | grep -o 'commented\|\[yusishuma\]\|\[botbocks\]' | wc -l)

echo "当前评论数: $COMMENT_COUNT" >> "$LOG_FILE"

if [ -f "$LAST_COMMENT_COUNT_FILE" ]; then
    LAST_COUNT=$(cat "$LAST_COMMENT_COUNT_FILE")
    if [ "$COMMENT_COUNT" -eq "$LAST_COUNT" ]; then
        echo "状态: 暂无新回复" >> "$LOG_FILE"
        echo "-------------------------------------" >> "$LOG_FILE"
        exit 0
    elif [ "$COMMENT_COUNT" -gt "$LAST_COUNT" ]; then
        echo "状态: 发现新回复！" >> "$LOG_FILE"
        echo "新增评论数: $((COMMENT_COUNT - LAST_COUNT))" >> "$LOG_FILE"
        echo "请访问: $PR_URL" >> "$LOG_FILE"
        echo "-------------------------------------" >> "$LOG_FILE"
        echo "$COMMENT_COUNT" > "$LAST_COMMENT_COUNT_FILE"
        exit 1
    else
        echo "状态: 评论数减少（可能是页面结构变化）" >> "$LOG_FILE"
        echo "-------------------------------------" >> "$LOG_FILE"
        echo "$COMMENT_COUNT" > "$LAST_COMMENT_COUNT_FILE"
        exit 0
    fi
else
    echo "状态: 首次检查，记录当前评论数" >> "$LOG_FILE"
    echo "$COMMENT_COUNT" > "$LAST_COMMENT_COUNT_FILE"
    echo "-------------------------------------" >> "$LOG_FILE"
    exit 0
fi