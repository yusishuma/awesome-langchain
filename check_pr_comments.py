#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_COMMENT_FILE = "/workspace/.last_pr_comment_id"


def get_comments():
    result = subprocess.run(["curl", "-s", PR_URL], capture_output=True, text=True)
    return json.loads(result.stdout)


def main():
    print("=== 检查 PR #437 评论状态 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    comments = get_comments()

    if not comments:
        print("暂无评论")
        return

    latest = comments[-1]
    latest_id = latest["id"]
    latest_time = latest["created_at"]
    latest_user = latest["user"]["login"]
    latest_body = latest.get("body", "")[:100] + "..." if len(latest.get("body", "")) > 100 else latest.get("body", "")

    print("最新评论信息：")
    print(f"  用户: {latest_user}")
    print(f"  时间: {latest_time}")
    print(f"  ID: {latest_id}")
    print(f"  内容: {latest_body}")
    print()

    has_new_reply = False

    if os.path.exists(LAST_COMMENT_FILE):
        with open(LAST_COMMENT_FILE, "r") as f:
            last_id = int(f.read().strip())

        if latest_id > last_id:
            print("✅ 有新回复！")
            print("查看地址: https://github.com/kyrolabs/awesome-langchain/pull/437")
            has_new_reply = True
        else:
            print("❌ 暂无新回复")
    else:
        print("首次检查，记录当前最新评论 ID")

    with open(LAST_COMMENT_FILE, "w") as f:
        f.write(str(latest_id))

    exit(0 if has_new_reply else 1)


if __name__ == "__main__":
    main()