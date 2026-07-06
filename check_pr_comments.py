#!/usr/bin/env python3
import time
import json
import urllib.request
import urllib.error
import os
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
STATE_FILE = "/workspace/.pr_comment_state.json"
LOG_FILE = "/workspace/pr_check_log.txt"


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_comment_id": None, "comment_count": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_comments():
    req = urllib.request.Request(API_URL)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "pr-comment-checker")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        log(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except Exception as e:
        log(f"Error fetching comments: {e}")
        return None


def check_for_new_comments():
    state = load_state()
    comments = fetch_comments()
    
    if comments is None:
        return False
    
    current_count = len(comments)
    last_id = state.get("last_comment_id")
    
    if last_id is None:
        log(f"Initial check: found {current_count} comments. Monitoring for new replies...")
        if comments:
            state["last_comment_id"] = comments[-1]["id"]
        state["comment_count"] = current_count
        save_state(state)
        return False
    
    if current_count > state["comment_count"]:
        new_comments = []
        for c in reversed(comments):
            if c["id"] == last_id:
                break
            new_comments.append(c)
        new_comments.reverse()
        
        log("=" * 60)
        log(f"NEW REPLY DETECTED! {len(new_comments)} new comment(s):")
        log("=" * 60)
        for c in new_comments:
            author = c["user"]["login"]
            created_at = c["created_at"]
            body = c["body"][:500]
            log(f"\n--- @{author} ({created_at}) ---")
            log(body)
            if len(c["body"]) > 500:
                log("... [truncated]")
        log("\n" + "=" * 60)
        log(f"Check PR here: {PR_URL}")
        log("=" * 60)
        
        state["last_comment_id"] = comments[-1]["id"]
        state["comment_count"] = current_count
        save_state(state)
        return True
    else:
        log(f"No new replies. Total comments: {current_count}")
        return False


def main():
    log("Starting PR comment monitor...")
    log(f"PR: {PR_URL}")
    log(f"Check interval: {CHECK_INTERVAL}s ({CHECK_INTERVAL//60} min)")
    log("-" * 40)
    
    check_for_new_comments()
    
    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            check_for_new_comments()
        except Exception as e:
            log(f"Error in check loop: {e}")


if __name__ == "__main__":
    main()
