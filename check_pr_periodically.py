import requests
import time
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
KNOWN_AUTHORS = ["yusishuma", "botbocks"]

def check_pr():
    print(f"[{datetime.now()}] 正在检查 PR #437...")
    
    try:
        response = requests.get(PR_URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        if response.status_code == 200:
            comments = response.json()
            
            if comments:
                print(f"[{datetime.now()}] 获取到 {len(comments)} 条评论:")
                for comment in comments:
                    author = comment['user']['login']
                    created_at = comment['created_at']
                    print(f"  - {author}: {created_at}")
                
                new_replies = [c for c in comments if c['user']['login'] not in KNOWN_AUTHORS]
                
                if new_replies:
                    print("\n✅✅✅ 检测到新回复！ ✅✅✅")
                    for comment in new_replies:
                        print(f"  {comment['user']['login']} 在 {comment['created_at']} 回复了")
                    print("\n🎉 快去查看吧！")
                    return True, comments
                else:
                    print(f"[{datetime.now()}] 暂无新回复")
                    return False, comments
            else:
                print(f"[{datetime.now()}] 没有找到评论")
                return False, []
        else:
            print(f"[{datetime.now()}] 请求失败，状态码: {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"[{datetime.now()}] 请求异常: {e}")
        return False, []

def main():
    print(f"开始监控 PR #437...")
    print(f"检查间隔: {CHECK_INTERVAL/60} 分钟")
    print(f"已知用户: {', '.join(KNOWN_AUTHORS)}")
    print(f"监控开始时间: {datetime.now()}\n")
    
    while True:
        found, comments = check_pr()
        if found:
            print("\n🎉 发现新回复！脚本结束。")
            break
        print(f"下次检查将在 {CHECK_INTERVAL/60} 分钟后进行\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()