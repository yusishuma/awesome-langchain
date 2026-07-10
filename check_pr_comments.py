#!/usr/bin/env python3
import json
import time
import urllib.request
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
PR_HTML_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL = 300  # 5 minutes
INITIAL_COMMENT_COUNT = 1
MY_USERNAME = "yusishuma"


def get_comments():
    req = urllib.request.Request(PR_URL)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "PR Comment Checker")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode())


def check_new_replies():
    try:
        comments = get_comments()
        new_comments = [
            c for c in comments
            if c["user"]["login"] != MY_USERNAME
        ]

        if new_comments:
            print("\n" + "=" * 60)
            print(f"[!] 发现 {len(new_comments)} 条新回复！")
            print("=" * 60)
            for c in new_comments:
                print(f"\n👤 用户: {c['user']['login']}")
                print(f"🕐 时间: {c['created_at']}")
                print(f"💬 内容:\n{c['body']}")
                print("-" * 60)
            print(f"\n🔗 查看 PR: {PR_HTML_URL}")
            return True, comments
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] 暂无新回复 (总评论数: {len(comments)})")
            return False, comments
    except Exception as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] 检查失败: {e}")
        return False, None


def main():
    print(f"开始监控 PR 评论: {PR_HTML_URL}")
    print(f"检查间隔: {CHECK_INTERVAL // 60} 分钟")
    print(f"当前初始评论数: {INITIAL_COMMENT_COUNT}")
    print("-" * 60)

    check_new_replies()

    while True:
        time.sleep(CHECK_INTERVAL)
        has_new, _ = check_new_replies()
        if has_new:
            print("\n📢 检测到回复！请及时查看。")


if __name__ == "__main__":
    main()
