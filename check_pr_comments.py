import requests
import time
import json
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE = "/workspace/last_pr_check.json"
CHECK_INTERVAL = 300 

def load_last_check():
    try:
        with open(LAST_CHECK_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_check_time": 0, "last_comment_id": 0}

def save_last_check(last_comment_id):
    data = {
        "last_check_time": int(time.time()),
        "last_comment_id": last_comment_id
    }
    with open(LAST_CHECK_FILE, 'w') as f:
        json.dump(data, f)

def get_comments():
    try:
        response = requests.get(PR_URL)
        if response.status_code == 403:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Rate limit exceeded, waiting...")
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 获取评论失败: {e}")
        return []

def format_comment(comment):
    author = comment.get('user', {}).get('login', 'Unknown')
    created_at = comment.get('created_at', '')
    body = comment.get('body', '')[:200]
    return f"\n作者: {author}\n时间: {created_at}\n内容: {body}..."

def check_for_new_comments():
    last_data = load_last_check()
    comments = get_comments()
    
    if comments is None:
        return
    if not comments:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 暂无评论或获取失败")
        return
    
    latest_comment_id = comments[-1]['id'] if comments else 0
    
    if latest_comment_id > last_data['last_comment_id']:
        new_comments = [c for c in comments if c['id'] > last_data['last_comment_id']]
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 发现新回复!")
        print(f"{'='*60}")
        for comment in new_comments:
            print(format_comment(comment))
            print("-" * 60)
        save_last_check(latest_comment_id)
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 暂无新回复")

def main():
    print(f"开始监控 PR #437 回复...")
    print(f"检查间隔: {CHECK_INTERVAL}秒")
    print(f"按 Ctrl+C 停止")
    print()
    
    while True:
        check_for_new_comments()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()