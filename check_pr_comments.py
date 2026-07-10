import requests
import json
import time
import sys
import os
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 3600
YOUR_USERNAME = "yusishuma"

def get_headers():
    token = os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def fetch_comments():
    try:
        response = requests.get(PR_URL, headers=get_headers())
        if response.status_code == 403:
            print("❌ API 速率限制，请设置 GH_TOKEN 环境变量")
            print("   生成 token: https://github.com/settings/tokens (只需 public_repo 权限)")
            return []
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取失败: {e}")
        return []

def format_comment(comment):
    author = comment['user']['login']
    created_at = comment['created_at']
    body = comment['body']
    is_you = author == YOUR_USERNAME
    return {
        "author": author,
        "created_at": created_at,
        "body": body,
        "is_you": is_you
    }

def check_new_replies(comments):
    your_comments = [c for c in comments if c['user']['login'] == YOUR_USERNAME]
    if not your_comments:
        return None
    
    your_last_time = max(c['created_at'] for c in your_comments)
    replies = [format_comment(c) for c in comments if c['created_at'] > your_last_time]
    
    if replies:
        print("\n🎉 发现新回复！")
        for r in replies:
            print(f"\n--- 新评论 ---")
            print(f"👤 作者: {r['author']} {'(你)' if r['is_you'] else ''}")
            print(f"📅 时间: {r['created_at']}")
            print(f"💬 内容:\n{r['body']}")
        print("\n" + "="*60)
        return True
    return False

def print_full_comments(comments):
    if not comments:
        print("ℹ️ 暂无评论")
        return
    
    formatted = [format_comment(c) for c in comments]
    formatted.sort(key=lambda x: x['created_at'])
    
    print(f"\n📝 共 {len(formatted)} 条评论:\n")
    for i, c in enumerate(formatted, 1):
        print(f"--- 评论 #{i} ---")
        print(f"👤 作者: {c['author']} {'(你)' if c['is_you'] else ''}")
        print(f"📅 时间: {c['created_at']}")
        print(f"💬 内容:\n{c['body']}\n")

def main():
    token_set = "✅" if os.environ.get("GH_TOKEN") else "❌"
    print(f"🔍 PR #437 监控启动 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"⏰ 检查间隔: {CHECK_INTERVAL // 60} 分钟")
    print(f"👤 监控用户: {YOUR_USERNAME}")
    print(f"🔑 Token 已设置: {token_set}")
    print("="*60)
    
    try:
        while True:
            print(f"\n🔍 正在检查... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            comments = fetch_comments()
            
            if comments:
                has_new = check_new_replies(comments)
                
                if has_new:
                    print("✅ 已收到回复！脚本将继续运行，但建议你直接查看 PR。")
                
                if not has_new:
                    print("⏳ 暂无新回复")
            else:
                print("❌ 无法获取评论信息")
            
            print(f"\n⏳ 下次检查将在 {CHECK_INTERVAL // 60} 分钟后进行...")
            print("按 Ctrl+C 停止监控")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print(f"🔍 单次检查 PR #437... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        comments = fetch_comments()
        
        if comments:
            check_new_replies(comments)
            print("\n" + "="*60)
            print("查看完整评论:")
            print_full_comments(comments)
        else:
            print("❌ 无法获取评论信息")
    else:
        main()