#!/bin/bash
# Polls a GitHub PR conversation page for new comments.

PR_URL="https://github.com/kyrolabs/awesome-langchain/pull/437"
STATE_DIR="/workspace/.pr-watch"
LOG_FILE="$STATE_DIR/changes.log"
HASH_FILE="$STATE_DIR/conversation.hash"
HTML_FILE="$STATE_DIR/pr_page.html"
INTERVAL=600  # 10 minutes

mkdir -p "$STATE_DIR"

log() {
    echo "[$(date -Iseconds)] $*" >> "$LOG_FILE"
}

compute_signature() {
    curl -sL -A "Mozilla/5.0" --max-time 30 "$PR_URL" -o "$HTML_FILE"
    python3 - <<'PY'
import re, hashlib
html = open('/workspace/.pr-watch/pr_page.html', 'r', encoding='utf-8', errors='ignore').read()
ids = re.findall(r'id="issuecomment-(\d+)"', html)
rev = re.findall(r'data-discussion-id="(\d+)"', html)
sig = ",".join(ids) + "|" + ",".join(rev)
h = hashlib.sha256(sig.encode()).hexdigest()[:16]
print(h)
print(f"issue_comments={len(ids)} review_comments={len(rev)} ids={ids}")
PY
}

log "=== Start monitoring: $PR_URL (interval=${INTERVAL}s) ==="
OUT=$(compute_signature)
HASH=$(echo "$OUT" | head -1)
log "Baseline: $OUT"
echo "$HASH" > "$HASH_FILE"

while true; do
    sleep "$INTERVAL"
    OUT=$(compute_signature 2>/dev/null)
    NEW_HASH=$(echo "$OUT" | head -1)
    OLD_HASH=$(cat "$HASH_FILE" 2>/dev/null)
    if [ -z "$NEW_HASH" ]; then
        log "fetch failed, skipping"
        continue
    fi
    if [ "$NEW_HASH" != "$OLD_HASH" ]; then
        log "CHANGE DETECTED ($OLD_HASH -> $NEW_HASH): $OUT"
        echo "$NEW_HASH" > "$HASH_FILE"
        SNAP="$STATE_DIR/page_$(date +%Y%m%d_%H%M%S).html"
        cp "$HTML_FILE" "$SNAP"
        log "Snapshot saved: $SNAP"
    else
        log "no change: $OUT"
    fi
done
