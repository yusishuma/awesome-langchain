#!/usr/bin/env python3
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pr_check_state.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pr_check.log")
CHECK_INTERVAL = 300  # 5 minutes


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def fetch_comments_api():
    req = urllib.request.Request(API_URL)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "pr-checker")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_comments_html():
    req = urllib.request.Request(PR_URL)
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    req.add_header("Accept", "text/html")
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    pattern = (
        r'id="(issuecomment-(\d+)|pullrequest-(\d+))"[^>]*>'
        r'.*?<a[^>]*class="author[^"]*"[^>]*>(\w+)</a>'
        r'.*?<relative-time[^>]*datetime="([^"]+)"[^>]*>'
        r'.*?comment-body[^>]*>(.*?)</(?:td|div)>'
    )
    matches = re.findall(pattern, html, re.DOTALL)

    comments = []
    for full_id, issue_id, pr_id, author, dt_str, body_html in matches:
        cid = int(issue_id) if issue_id else int(pr_id)
        body = re.sub(r'<[^>]+>', '', body_html).strip()
        body = re.sub(r'\n{3,}', '\n\n', body)
        comments.append({
            "id": cid,
            "user": {"login": author},
            "created_at": dt_str,
            "body": body
        })

    return sorted(comments, key=lambda c: c["id"])


def fetch_comments():
    try:
        return fetch_comments_api()
    except Exception as e:
        log(f"API failed ({e}), trying HTML scrape...")
        try:
            return fetch_comments_html()
        except Exception as e2:
            raise Exception(f"Both API and HTML scrape failed: {e}; {e2}")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_comment_id": None, "last_check": None, "comment_count": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def format_time(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def check_once():
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()

    try:
        comments = fetch_comments()
    except Exception as e:
        log(f"Error fetching comments: {e}")
        return False

    comments_sorted = sorted(comments, key=lambda c: c["id"])
    current_count = len(comments_sorted)

    log(f"Checking PR #437... Total comments: {current_count}")

    if state["last_comment_id"] is None:
        log("First check - recording current state.")
        log("Current comments:")
        for c in comments_sorted:
            log(f"  - [{c['user']['login']}] {format_time(c['created_at'])}")
            body_preview = c['body'][:120].replace('\n', ' ')
            log(f"    {body_preview}{'...' if len(c['body']) > 120 else ''}")
    else:
        new_comments = [c for c in comments_sorted if c["id"] > state["last_comment_id"]]
        if new_comments:
            log(f"*** NEW REPLIES DETECTED: {len(new_comments)} new comment(s) ***")
            log(f"PR URL: {PR_URL}")
            for c in new_comments:
                log(f"  From: {c['user']['login']}")
                log(f"  Time: {format_time(c['created_at'])}")
                log(f"  ----")
                for line in c['body'].split('\n'):
                    log(f"  {line}")
                log(f"  ----")
        else:
            log("No new replies since last check.")

    if comments_sorted:
        state["last_comment_id"] = comments_sorted[-1]["id"]
    state["last_check"] = now
    state["comment_count"] = current_count
    save_state(state)
    return True


def main():
    log(f"PR Comment Checker started. Checking every {CHECK_INTERVAL} seconds.")
    log(f"PR URL: {PR_URL}")

    while True:
        check_once()
        log(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    if "--once" in sys.argv:
        check_once()
    else:
        main()
