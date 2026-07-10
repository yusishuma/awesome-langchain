#!/bin/bash

REPO="kyrolabs/awesome-langchain"
PR_NUMBER="437"
LAST_CHECK_FILE="/workspace/.last_pr_comment_id"

echo "=== Checking PR #$PR_NUMBER in $REPO ==="
echo "Time: $(date)"
echo ""

COMMENTS=$(curl -s "https://api.github.com/repos/$REPO/issues/$PR_NUMBER/comments")
TOTAL_COMMENTS=$(echo "$COMMENTS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

echo "Total comments: $TOTAL_COMMENTS"
echo ""

echo "$COMMENTS" | python3 -c "
import sys,json
comments = json.load(sys.stdin)
for c in comments:
    print(f\"[{c['created_at']}] @{c['user']['login']}:\")
    body = c['body'].replace('\r', '').strip()
    if len(body) > 200:
        body = body[:200] + '...'
    print(f\"  {body}\")
    print()
"

LAST_ID=$(cat "$LAST_CHECK_FILE" 2>/dev/null || echo "0")
NEW_COMMENTS=$(echo "$COMMENTS" | python3 -c "
import sys,json
comments = json.load(sys.stdin)
new_count = 0
last_id = int('$LAST_ID')
for c in comments:
    if c['id'] > last_id:
        new_count += 1
print(new_count)
")

echo "=== Summary ==="
if [ "$NEW_COMMENTS" -gt 0 ]; then
    echo "✅ NEW REPLY DETECTED! ($NEW_COMMENTS new comment(s))"
else
    echo "No new replies yet."
fi

echo "$COMMENTS" | python3 -c "
import sys,json
comments = json.load(sys.stdin)
if comments:
    print(max(c['id'] for c in comments))
else:
    print(0)
" > "$LAST_CHECK_FILE"

echo ""
echo "PR URL: https://github.com/$REPO/pull/$PR_NUMBER"