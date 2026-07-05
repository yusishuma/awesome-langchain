import requests
import time
import os
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE = "/workspace/.last_pr_check"

def get_last_check_time():
    if os.path.exists(LAST_CHECK_FILE):
        with open(LAST_CHECK_FILE, 'r') as f:
            return float(f.read())
    return 0

def save_last_check_time(timestamp):
    with open(LAST_CHECK_FILE, 'w') as f:
        f.write(str(timestamp))

def check_new_comments():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在检查 PR #437 的新评论...")
    
    try:
        headers = {
            'User-Agent': 'PR-Comment-Checker/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        comments = response.json()
        
        if not comments:
            print("  暂无评论")
            return
        
        last_check = get_last_check_time()
        new_comments = []
        
        for comment in comments:
            comment_time = datetime.strptime(comment['created_at'], '%Y-%m-%dT%H:%M:%SZ').timestamp()
            if comment_time > last_check:
                new_comments.append({
                    'user': comment['user']['login'],
                    'time': comment['created_at'],
                    'body': comment['body'][:200] + '...' if len(comment['body']) > 200 else comment['body']
                })
        
        if new_comments:
            print(f"  发现 {len(new_comments)} 条新评论:")
            for idx, comment in enumerate(new_comments, 1):
                print(f"\n  --- 新评论 #{idx} ---")
                print(f"  用户: {comment['user']}")
                print(f"  时间: {comment['time']}")
                print(f"  内容: {comment['body']}")
                print(f"  ---")
            
            save_last_check_time(time.time())
            print(f"\n  🔔 通知：你收到了新的回复！")
            print(f"  PR 链接: {PR_URL}")
        else:
            print("  暂无新评论")
            
    except requests.exceptions.RequestException as e:
        print(f"  请求失败: {e}")
    except Exception as e:
        print(f"  发生错误: {e}")

def main():
    print(f"=== PR 评论监控器 ===")
    print(f"监控目标: {PR_URL}")
    print(f"检查间隔: 5 分钟")
    print(f"按 Ctrl+C 停止监控\n")
    
    check_new_comments()
    
    while True:
        time.sleep(300)
        check_new_comments()

if __name__ == "__main__":
    main()