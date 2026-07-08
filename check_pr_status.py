#!/usr/bin/env python3
"""
监控 GitHub PR #437 的更新状态
"""

import urllib.request
import urllib.error
import json
from datetime import datetime
import sys

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
PR_API = "https://api.github.com/repos/kyrolabs/awesome-langchain/pulls/437"
COMMENTS_API = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"

def fetch_json(url):
    """获取JSON数据"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))

def check_pr_updates():
    print("=" * 60)
    print(f"PR #437 更新监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

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

        print(f"评论总数: {len(comments_data)}")
        print()

        if comments_data:
            print("最近评论:")
            print("-" * 60)

            # 显示最后3条评论
            for comment in comments_data[-3:]:
                author = comment.get('user', {}).get('login', 'Unknown')
                created = comment.get('created_at', 'N/A')
                body = comment.get('body', '')[:200]

                print(f"作者: {author}")
                print(f"时间: {created}")
                print(f"内容: {body}...")
                print("-" * 60)

            # 检查是否有维护者的回复
            maintainers = ['botbocks']
            has_maintainer_reply = False
            for comment in comments_data:
                author = comment.get('user', {}).get('login', '')
                if author in maintainers:
                    has_maintainer_reply = True
                    print()
                    print("✅ 维护者已回复!")
                    break

            if not has_maintainer_reply:
                print()
                print("⏳ 暂无维护者回复")
        else:
            print("暂无评论")

    except Exception as e:
        print(f"❌ 获取评论失败: {e}")
        return

    print()
    print(f"PR链接: {PR_URL}")
    print("=" * 60)

if __name__ == "__main__":
    check_pr_updates()