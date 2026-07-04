#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from datetime import datetime

REPO = "kyrolabs/awesome-langchain"
PR_NUMBER = "437"
STATE_FILE = "/workspace/.pr_last_check.json"
LOG_FILE = "/workspace/pr_comments.log"

API_URL = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def fetch_comments():
    req = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PR-Checker",
        },
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None


def save_state(count, last_id):
    state = {
        "LAST_COUNT": count,
        "LAST_ID": last_id,
        "LAST_CHECK": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def main():
    log(f"开始检查 PR #{PR_NUMBER} 的评论...")

    try:
        comments = fetch_comments()
    except Exception as e:
        log(f"获取评论失败: {e}")
        sys.exit(1)

    if isinstance(comments, dict) and "message" in comments:
        log(f"API 错误: {comments['message']}")
        sys.exit(1)

    current_count = len(comments)
    last_id = comments[-1]["id"] if comments else 0

    log(f"当前评论总数: {current_count}")

    state = load_state()

    if state:
        last_count = state.get("LAST_COUNT", 0)
        last_known_id = state.get("LAST_ID", 0)

        if current_count > last_count:
            new_count = current_count - last_count
            log("=" * 40)
            log(f"  发现新评论！新增 {new_count} 条")
            log("=" * 40)

            new_comments = [c for c in comments if c["id"] > last_known_id]
            for c in new_comments:
                log("---")
                log(f"用户: {c['user']['login']}")
                log(f"时间: {c['created_at']}")
                log(f"内容: {c['body']}")
                log("")

        elif current_count == last_count:
            log(f"没有新评论，评论数保持不变: {current_count}")
        else:
            log(f"评论数减少了: {last_count} -> {current_count} (可能有评论被删除)")
    else:
        log("首次检查，记录当前状态")
        if comments:
            log("最近的评论:")
            for c in comments[-3:]:
                log("---")
                log(f"用户: {c['user']['login']}")
                log(f"时间: {c['created_at']}")
                log(f"内容: {c['body'][:200]}...")
            log("")

    save_state(current_count, last_id)
    log("检查完成")
    log("")


if __name__ == "__main__":
    main()
