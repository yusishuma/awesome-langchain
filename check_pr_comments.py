#!/usr/bin/env python3
import json
import urllib.request
import os
import time
from datetime import datetime

REPO_OWNER = "kyrolabs"
REPO_NAME = "awesome-langchain"
PR_NUMBER = 437
YOUR_USERNAME = "yusishuma"
STATE_FILE = "/workspace/.pr_last_check.json"
API_BASE = "https://api.github.com"


def fetch_issue_comments():
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_review_comments():
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}/reviews"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_comment_id": 0, "last_review_id": 0}


def save_state(issue_comments, review_comments):
    max_comment_id = max((c["id"] for c in issue_comments), default=0)
    max_review_id = max((r["id"] for r in review_comments), default=0)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_comment_id": max_comment_id, "last_review_id": max_review_id}, f)


def format_comment(comment, is_review=False):
    user = comment["user"]["login"]
    body = comment["body"]
    url = comment.get("html_url", comment.get("_links", {}).get("html", {}).get("href", ""))
    created = comment["created_at"]
    return f"[{created}] {user}:\n{body}\n{url}\n" + "=" * 60


def check_new_comments():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking PR #{PR_NUMBER} for new comments...")
    print(f"PR URL: https://github.com/{REPO_OWNER}/{REPO_NAME}/pull/{PR_NUMBER}")

    try:
        issue_comments = fetch_issue_comments()
        review_comments = fetch_review_comments()
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return False

    last_state = load_last_state()
    last_comment_id = last_state["last_comment_id"]
    last_review_id = last_state["last_review_id"]

    new_issue_comments = [c for c in issue_comments if c["id"] > last_comment_id and c["user"]["login"] != YOUR_USERNAME]
    new_review_comments = [r for r in review_comments if r["id"] > last_review_id and r["user"]["login"] != YOUR_USERNAME]

    new_total = len(new_issue_comments) + len(new_review_comments)

    if new_total > 0:
        print(f"\n{'=' * 60}")
        print(f"  NEW REPLIES FOUND: {new_total}")
        print(f"{'=' * 60}\n")

        for c in new_issue_comments:
            print(format_comment(c))

        for r in new_review_comments:
            print(format_comment(r, is_review=True))

        save_state(issue_comments, review_comments)
        return True
    else:
        total_comments = len(issue_comments) + len(review_comments)
        your_comments = sum(1 for c in issue_comments if c["user"]["login"] == YOUR_USERNAME) + \
                        sum(1 for r in review_comments if r["user"]["login"] == YOUR_USERNAME)
        others_comments = total_comments - your_comments
        print(f"No new replies. Total comments: {total_comments} (yours: {your_comments}, others: {others_comments})")
        save_state(issue_comments, review_comments)
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 600
        print(f"Watching PR #{PR_NUMBER} every {interval} seconds. Press Ctrl+C to stop.")
        while True:
            check_new_comments()
            time.sleep(interval)
    else:
        check_new_comments()
