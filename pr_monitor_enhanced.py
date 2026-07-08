#!/usr/bin/env python3
"""
增强版 GitHub PR 监控脚本
- 自动检测是否有新的维护者回复
- 记录历史状态
- 发送通知(可选)
"""

import urllib.request
import urllib.error
import json
from datetime import datetime
import os
import sys

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
PR_API = "https://api.github.com/repos/kyrolabs/awesome-langchain/pulls/437"
COMMENTS_API = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
HISTORY_FILE = "/workspace/pr_history.json"
MAINTAINERS = ['botbocks']

def fetch_json(url):
    """获取JSON数据"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))

def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"last_comment_count": 0, "last_maintainer_reply": False, "checks": []}

def save_history(history):
    """保存历史记录"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def check_pr_updates():
    print("=" * 70)
    print(f"PR #437 增强监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    # 加载历史记录
    history = load_history()
    last_comment_count = history.get("last_comment_count", 0)
    last_maintainer_reply = history.get("last_maintainer_reply", False)

    # 获取PR基本信息
    try:
        pr_data = fetch_json(PR_API)

        title = pr_data.get('title', 'N/A')
        state = pr_data.get('state', 'N/A')
        created_at = pr_data.get('created_at', 'N/A')
        closed_at = pr_data.get('closed_at', 'N/A')
        user_login = pr_data.get('user', {}).get('login', 'N/A')

        print(f"PR标题: {title}")
        print(f"PR状态: {state}")
        print(f"创建者: {user_login}")
        print(f"创建时间: {created_at}")
        if closed_at:
            print(f"关闭时间: {closed_at}")
        print()

    except Exception as e:
        print(f"❌ 获取PR信息失败: {e}")
        return

    # 获取评论信息
    try:
        comments_data = fetch_json(COMMENTS_API)
        current_comment_count = len(comments_data)

        print(f"评论总数: {current_comment_count} (上次检查: {last_comment_count})")
        print()

        # 检查是否有维护者的回复
        has_maintainer_reply = False
        maintainer_comments = []

        for comment in comments_data:
            author = comment.get('user', {}).get('login', '')
            if author in MAINTAINERS:
                has_maintainer_reply = True
                maintainer_comments.append(comment)

        # 显示所有评论
        if comments_data:
            print("所有评论:")
            print("-" * 70)
            for i, comment in enumerate(comments_data, 1):
                author = comment.get('user', {}).get('login', 'Unknown')
                created = comment.get('created_at', 'N/A')
                body = comment.get('body', '')[:150]

                is_maintainer = " [维护者]" if author in MAINTAINERS else ""
                is_new = " 🆕" if i > last_comment_count else ""

                print(f"[{i}] 作者: {author}{is_maintainer}{is_new}")
                print(f"    时间: {created}")
                print(f"    内容: {body}...")
                print("-" * 70)
        else:
            print("暂无评论")

        # 检查变化
        print()
        if current_comment_count > last_comment_count:
            print("🔔 检测到新评论!")
            print(f"   新增评论数: {current_comment_count - last_comment_count}")

        if has_maintainer_reply and not last_maintainer_reply:
            print("🎉 检测到维护者回复!")
            print()
            print("维护者评论内容:")
            for comment in maintainer_comments:
                print(f"  - {comment.get('body', '')[:200]}")

        if not has_maintainer_reply:
            print("⏳ 暂无维护者回复")

        # 更新历史记录
        current_check = {
            "timestamp": datetime.now().isoformat(),
            "comment_count": current_comment_count,
            "has_maintainer_reply": has_maintainer_reply,
            "pr_state": state
        }
        history["last_comment_count"] = current_comment_count
        history["last_maintainer_reply"] = has_maintainer_reply
        history["checks"].append(current_check)

        # 只保留最近10次检查记录
        history["checks"] = history["checks"][-10:]

        save_history(history)

    except Exception as e:
        print(f"❌ 获取评论失败: {e}")
        return

    print()
    print(f"PR链接: {PR_URL}")
    print("=" * 70)

    # 返回状态码(用于其他脚本判断)
    if has_maintainer_reply and not last_maintainer_reply:
        return 1  # 有新的维护者回复
    elif current_comment_count > last_comment_count:
        return 2  # 有新评论但不是维护者
    return 0  # 无变化

if __name__ == "__main__":
    exit_code = check_pr_updates()
    sys.exit(exit_code)