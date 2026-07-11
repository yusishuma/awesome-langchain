#!/bin/bash

PR_URL="https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE="/workspace/.last_pr_comment_check"
MY_LOGIN="yusishuma"

if [ ! -f "$LAST_CHECK_FILE" ]; then
    echo "0" > "$LAST_CHECK_FILE"
fi

LAST_COMMENT_ID=$(cat "$LAST_CHECK_FILE")

RESPONSE=$(curl -s "$PR_URL")
NEW_COMMENTS=$(echo "$RESPONSE" | grep -o '"id": [0-9]*' | awk '{print $2}' | sort -n)

HAS_NEW_REPLY="false"
NEW_REPLY_DETAILS=""

for COMMENT_ID in $NEW_COMMENTS; do
    if [ "$COMMENT_ID" -gt "$LAST_COMMENT_ID" ]; then
        USER_LOGIN=$(echo "$RESPONSE" | grep -A 20 "\"id\": $COMMENT_ID" | grep -o '"login": "[^"]*"' | head -n 1 | sed 's/"login": "\([^"]*\)"/\1/')
        
        if [ "$USER_LOGIN" != "$MY_LOGIN" ]; then
            HAS_NEW_REPLY="true"
            CREATED_AT=$(echo "$RESPONSE" | grep -A 20 "\"id\": $COMMENT_ID" | grep -o '"created_at": "[^"]*"' | head -n 1 | sed 's/"created_at": "\([^"]*\)"/\1/')
            BODY=$(echo "$RESPONSE" | grep -A 50 "\"id\": $COMMENT_ID" | sed -n '/"body": "/,/"author_association":/p' | head -n 1 | sed 's/"body": "\([^"]*\)"/\1/' | tr '\r\n' ' ')
            NEW_REPLY_DETAILS="$NEW_REPLY_DETAILS\n回复来自 @$USER_LOGIN ($CREATED_AT):\n$BODY\n---"
        fi
        
        if [ "$COMMENT_ID" -gt "$LAST_COMMENT_ID" ]; then
            echo "$COMMENT_ID" > "$LAST_CHECK_FILE"
        fi
    fi
done

if [ "$HAS_NEW_REPLY" = "true" ]; then
    echo "======================================"
    echo "PR #437 收到新回复！"
    echo "时间: $(date)"
    echo "======================================"
    echo -e "$NEW_REPLY_DETAILS"
    echo ""
else
    echo "$(date): 暂无新回复"
fi