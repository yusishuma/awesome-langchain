#!/usr/bin/env python3

import json
import os
import subprocess
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE = "/workspace/.last_pr_comment_check"
MY_LOGIN = "yusishuma"


def get_comments():
    result = subprocess.run(["curl", "-s", PR_URL], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"获取评论失败: {result.stderr}")
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("解析评论失败")
        return []


def get_last_comment_id():
    if os.path.exists(LAST_CHECK_FILE):
        with open(LAST_CHECK_FILE, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                return int(content)
    return 0


def save_last_comment_id(comment_id):
    with open(LAST_CHECK_FILE, "w") as f:
        f.write(str(comment_id))


def main():
    comments = get_comments()
    last_id = get_last_comment_id()
    
    new_replies = []
    max_id = last_id
    
    for comment in comments:
        comment_id = comment.get("id", 0)
        user_login = comment.get("user", {}).get("login", "")
        created_at = comment.get("created_at", "")
        body = comment.get("body", "")
        
        if comment_id > max_id:
            max_id = comment_id
            
            if user_login != MY_LOGIN:
                new_replies.append({
                    "user": user_login,
                    "created_at": created_at,
                    "body": body
                })
    
    if max_id > last_id:
        save_last_comment_id(max_id)
    
    if new_replies:
        print("=" * 50)
        print(f"PR #437 收到新回复！")
        print(f"时间: {datetime.now()}")
        print("=" * 50)
        for reply in new_replies:
            print(f"\n来自 @{reply['user']} ({reply['created_at']}):")
            print("-" * 30)
            print(reply['body'])
            print("-" * 30)
        print("\n")
    else:
        print(f"{datetime.now()}: 暂无新回复")


if __name__ == "__main__":
    main()