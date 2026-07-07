import time
import requests
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL = 300
KNOWN_AUTHORS = ["yusishuma", "botbocks"]

def check_pr():
    try:
        response = requests.get(PR_URL, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if response.status_code == 200:
            content = response.text
            return parse_comments(content)
        else:
            print(f"[{datetime.now()}] 请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"[{datetime.now()}] 请求异常: {e}")
        return None

def parse_comments(html):
    import re
    
    comment_blocks = re.findall(r'<div class="comment-body[^"]*">.*?</div>', html, re.DOTALL)
    
    comments = []
    for block in comment_blocks:
        author_match = re.search(r'<a[^>]*class="author[^"]*"[^>]*>([^<]+)</a>', block)
        time_match = re.search(r'<relative-time[^>]*>([^<]+)</relative-time>', block)
        
        if author_match and time_match:
            author = author_match.group(1).strip()
            comment_time = time_match.group(1).strip()
            comments.append({
                "author": author,
                "time": comment_time
            })
    
    return comments

def has_new_reply(comments):
    if not comments:
        return False, []
    
    replies = [c for c in comments if c['author'] not in KNOWN_AUTHORS]
    return len(replies) > 0, replies

def main():
    print(f"开始监控 PR #{PR_URL.split('/')[-1]}...")
    print(f"检查间隔: {CHECK_INTERVAL/60} 分钟")
    print(f"已知用户: {', '.join(KNOWN_AUTHORS)}")
    print(f"监控时间: {datetime.now()}\n")
    
    while True:
        comments = check_pr()
        
        if comments:
            print(f"[{datetime.now()}] 获取到 {len(comments)} 条评论")
            for comment in comments:
                print(f"  - {comment['author']}: {comment['time']}")
            
            found, replies = has_new_reply(comments)
            if found:
                print("\n✅✅✅ 检测到新回复！ ✅✅✅")
                for reply in replies:
                    print(f"  {reply['author']} 在 {reply['time']} 回复了")
                print("\n🎉 快去查看吧！")
                break
            else:
                print(f"\n⏳ 暂无新回复，下次检查将在 {CHECK_INTERVAL/60} 分钟后进行")
        else:
            print(f"[{datetime.now()}] 无法获取评论")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()