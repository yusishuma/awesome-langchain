#!/bin/bash
# Monitor PR #437 at https://github.com/kyrolabs/awesome-langchain/pull/437
# Strategy: scrape the public PR HTML page and detect any NEW comment from a
# user other than "yusishuma". Stop after the first such reply is detected.
#
# Frequency: every INTERVAL_SEC seconds (default 600s = 10 min).
# State: /tmp/pr437_monitor_state    Log: /tmp/pr437_monitor.log

REPO="kyrolabs/awesome-langchain"
PR=437
SELF="yusishuma"
INTERVAL_SEC="${INTERVAL_SEC:-600}"
URL="https://github.com/${REPO}/pull/${PR}"
STATE_FILE="/tmp/pr437_monitor_state"
LOG_FILE="/tmp/pr437_monitor.log"

# Fetch PR HTML to a temp file.
fetch_page() {
  curl -sS -L \
    -H "User-Agent: Mozilla/5.0 (compatible; PR-Monitor/1.0)" \
    -H "Accept: text/html" \
    "$URL" -o "$1"
}

# Parse HTML and print one line per COMMENT (not events):
#   <iso_time>|<login>|<body_excerpt>
parse_comments() {
  python3 - "$1" <<'PY'
import sys, re
path = sys.argv[1]
with open(path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Comments are anchored by permalinks: "issuecomment-<id>" for follow-ups and
# "issue-<id>" for the original PR description. Each anchor sits in an
# <a class="Link--secondary js-timestamp" ...> and the comment author link
# appears earlier in the same TimelineItem.

# Split on either type of permalink anchor.
parts = re.split(
    r'(<a[^>]*id="(?:issuecomment-\d+|issue-\d+)-permalink"[^>]*>)',
    content,
)
# parts[0] is preamble, then alternating [pre, anchor, post, anchor, post, ...]
for i in range(1, len(parts), 2):
    anchor = parts[i]
    # The block we care about starts AFTER the anchor (and is short).
    # But the author link is in the TimelineItem header, which sits BEFORE
    # the anchor. So we look at parts[i-1] (the chunk preceding the anchor).
    head = parts[i-1]
    tail = parts[i+1] if i+1 < len(parts) else ""

    m_time = re.search(r'<relative-time[^>]*datetime="([^"]+)"', anchor)
    if not m_time:
        continue
    iso = m_time.group(1)

    # Find the most recent author link in `head` (within the same TimelineItem).
    # The author link is an <a class="author Link--primary text-bold ..."
    # followed later by href="/<login>">...</a>.
    m_author = None
    for am in re.finditer(
        r'<a\b[^>]*class="[^"]*\bauthor\b[^"]*"[^>]*href="/([A-Za-z0-9-]+)"',
        head,
    ):
        m_author = am
    if not m_author:
        # Some author links have the attributes in opposite order
        for am in re.finditer(
            r'<a\b[^>]*href="/([A-Za-z0-9-]+)"[^>]*class="[^"]*\bauthor\b[^"]*"',
            head,
        ):
            m_author = am
    if not m_author:
        continue
    login = m_author.group(1)

    # Body excerpt: look for the next <td class="d-block comment-body ...">
    # or <div class="comment-body ..."> within the tail.
    body = ""
    m_body = re.search(r'<(?:td|div)[^>]*class="[^"]*\bcomment-body\b[^"]*"[^>]*>(.*?)</(?:td|div)>',
                       tail, re.S)
    if m_body:
        body = re.sub(r"<[^>]+>", " ", m_body.group(1))
        body = re.sub(r"\s+", " ", body).strip()[:240]

    print(f"{iso}|{login}|{body}")
PY
}

# Initialize baseline.
init_baseline() {
  local html; html=$(mktemp)
  fetch_page "$html"
  parse_comments "$html" > "$STATE_FILE.raw"
  rm -f "$html"
  awk -F'|' -v self="$SELF" '$2 != self { print }' "$STATE_FILE.raw" > "$STATE_FILE"
  local cnt; cnt=$(wc -l < "$STATE_FILE" | tr -d ' ')
  echo "[$(date -Iseconds)] Baseline non-self comments: $cnt" | tee -a "$LOG_FILE"
  if [ "$cnt" -gt 0 ]; then
    echo "----- existing non-self comments -----" | tee -a "$LOG_FILE"
    cat "$STATE_FILE" | tee -a "$LOG_FILE"
    echo "-------------------------------------" | tee -a "$LOG_FILE"
  fi
}

# Detect new non-self comments. Echoes 1 on first detection and exits loop.
detect_new() {
  local html; html=$(mktemp)
  fetch_page "$html"
  parse_comments "$html" > "$STATE_FILE.raw.new"
  rm -f "$html"
  awk -F'|' -v self="$SELF" '$2 != self { print }' "$STATE_FILE.raw.new" > "$STATE_FILE.new"

  if ! diff -q "$STATE_FILE" "$STATE_FILE.new" >/dev/null 2>&1; then
    echo "[$(date -Iseconds)] NEW REPLY DETECTED" | tee -a "$LOG_FILE"
    echo "----- All comments on the PR (chronological) -----" | tee -a "$LOG_FILE"
    cat "$STATE_FILE.raw.new" | tee -a "$LOG_FILE"
    echo "--------------------------------------------------" | tee -a "$LOG_FILE"
    echo "PR URL: $URL" | tee -a "$LOG_FILE"
    mv "$STATE_FILE.new" "$STATE_FILE"
    mv "$STATE_FILE.raw.new" "$STATE_FILE.raw"
    return 0
  else
    rm -f "$STATE_FILE.new" "$STATE_FILE.raw.new"
    return 1
  fi
}

# --- Main ---
: > "$LOG_FILE"
echo "[$(date -Iseconds)] Starting PR monitor for $URL (interval=${INTERVAL_SEC}s)" | tee -a "$LOG_FILE"
echo "[$(date -Iseconds)] Excluding self-account: $SELF" | tee -a "$LOG_FILE"
init_baseline

while true; do
  if detect_new; then
    echo "[$(date -Iseconds)] Stopping monitor (reply found)." | tee -a "$LOG_FILE"
    break
  fi
  echo "[$(date -Iseconds)] No new reply. Sleeping ${INTERVAL_SEC}s..." | tee -a "$LOG_FILE"
  sleep "$INTERVAL_SEC"
done
