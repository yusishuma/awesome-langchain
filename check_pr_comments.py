#!/usr/bin/env python3
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
STATE_FILE = "/workspace/.pr_check_state.json"
LOG_FILE = "/workspace/pr_check_log.txt"
CHECK_INTERVAL = 300


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_comment_count": 1, "last_check": None, "last_comment_id": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_comments():
    req = urllib.request.Request(API_URL)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "PR-Monitor-Bot")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        log(f"Error fetching comments: {e}")
        return None


def check_for_new_comments():
    state = load_state()
    comments = get_comments()
    
    if comments is None:
        return False
    
    current_count = len(comments)
    state["last_check"] = datetime.now().isoformat()
    
    if current_count > state["last_comment_count"]:
        new_comments = comments[state["last_comment_count"]:]
        log(f"🎉 发现 {len(new_comments)} 条新回复！")
        
        for comment in new_comments:
            author = comment["user"]["login"]
            body = comment["body"][:200] + ("..." if len(comment["body"]) > 200 else "")
            created_at = comment["created_at"]
            log(f"---")
            log(f"来自: @{author} ({created_at})")
            log(f"内容: {body}")
            log(f"链接: {comment['html_url']}")
        
        log(f"---")
        log(f"PR 地址: {PR_URL}")
        
        state["last_comment_count"] = current_count
        state["last_comment_id"] = comments[-1]["id"] if comments else None
        save_state(state)
        return True
    else:
        log(f"暂无新回复 (当前评论数: {current_count})")
        save_state(state)
        return False


def main():
    log("=" * 50)
    log("PR 回复监控启动")
    log(f"监控 PR: {PR_URL}")
    log(f"检查间隔: {CHECK_INTERVAL}秒 ({CHECK_INTERVAL//60}分钟)")
    log("=" * 50)
    
    state = load_state()
    log(f"初始状态: 已记录评论数 = {state['last_comment_count']}")
    
    while True:
        try:
            check_for_new_comments()
        except Exception as e:
            log(f"检查时发生错误: {e}")
        
        log(f"等待 {CHECK_INTERVAL//60} 分钟后再次检查...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
