import subprocess
import time
import sys
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL = 3600
YOUR_USERNAME = "yusishuma"

def fetch_pr_page():
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", PR_URL],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"❌ 获取失败: {result.stderr}")
            return None
        return result.stdout
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return None

def parse_comments(html):
    if not html:
        return []
    
    import re
    
    comment_pattern = re.compile(
        r'<div class="comment-body markdown-body[^"]*">.*?</div>',
        re.DOTALL
    )
    author_pattern = re.compile(r'<a class="author[^"]*"[^>]*>([^<]+)</a>')
    time_pattern = re.compile(r'<relative-time datetime="([^"]+)"')
    
    comments = []
    comment_bodies = comment_pattern.findall(html)
    
    if not comment_bodies:
        return []
    
    authors = author_pattern.findall(html)
    times = time_pattern.findall(html)
    
    for i, body in enumerate(comment_bodies):
        author = authors[i] if i < len(authors) else "unknown"
        created_at = times[i] if i < len(times) else "unknown"
        
        clean_body = re.sub(r'<[^>]+>', '', body).strip()
        clean_body = re.sub(r'\s+', ' ', clean_body)
        
        comments.append({
            "author": author.strip(),
            "created_at": created_at,
            "body": clean_body
        })
    
    return comments

def check_new_replies(comments):
    your_comments = [c for c in comments if YOUR_USERNAME.lower() in c['author'].lower()]
    if not your_comments:
        return None
    
    your_last_time = max(c['created_at'] for c in your_comments)
    replies = [c for c in comments if c['created_at'] > your_last_time]
    
    if replies:
        print("\n🎉 发现新回复！")
        for r in replies:
            print(f"\n--- 新评论 ---")
            print(f"👤 作者: {r['author']}")
            print(f"📅 时间: {r['created_at']}")
            print(f"💬 内容:\n{r['body']}")
        print("\n" + "="*60)
        return True
    return False

def print_full_comments(comments):
    if not comments:
        print("ℹ️ 暂无评论")
        return
    
    print(f"\n📝 共 {len(comments)} 条评论:\n")
    for i, c in enumerate(comments, 1):
        is_you = YOUR_USERNAME.lower() in c['author'].lower()
        print(f"--- 评论 #{i} ---")
        print(f"👤 作者: {c['author']} {'(你)' if is_you else ''}")
        print(f"📅 时间: {c['created_at']}")
        print(f"💬 内容:\n{c['body']}\n")

def main():
    print(f"🔍 PR #437 监控启动 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"⏰ 检查间隔: {CHECK_INTERVAL // 60} 分钟")
    print(f"👤 监控用户: {YOUR_USERNAME}")
    print("="*60)
    
    try:
        while True:
            print(f"\n🔍 正在检查... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            html = fetch_pr_page()
            
            if html:
                comments = parse_comments(html)
                
                if comments:
                    has_new = check_new_replies(comments)
                    
                    if has_new:
                        print("✅ 已收到回复！脚本将继续运行，但建议你直接查看 PR。")
                    
                    if not has_new:
                        print("⏳ 暂无新回复")
                else:
                    print("ℹ️ 无法解析评论")
            else:
                print("❌ 无法获取页面")
            
            print(f"\n⏳ 下次检查将在 {CHECK_INTERVAL // 60} 分钟后进行...")
            print("按 Ctrl+C 停止监控")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print(f"🔍 单次检查 PR #437... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        html = fetch_pr_page()
        
        if html:
            comments = parse_comments(html)
            
            if comments:
                check_new_replies(comments)
                print("\n" + "="*60)
                print("查看完整评论:")
                print_full_comments(comments)
            else:
                print("ℹ️ 无法解析评论")
        else:
            print("❌ 无法获取页面")
    else:
        main()