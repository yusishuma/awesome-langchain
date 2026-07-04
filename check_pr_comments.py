import requests
import time
import json
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 3600  

last_comment_count = 1
last_check_time = None


def check_comments():
    global last_comment_count, last_check_time
    
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        
        comments = response.json()
        current_count = len(comments)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{current_time}] 检查PR #437 评论状态...")
        print(f"  当前评论数: {current_count}")
        
        if current_count > last_comment_count:
            print("\n" + "="*60)
            print("  🎉 检测到新回复！")
            print("="*60)
            
            new_comments = comments[last_comment_count:]
            for comment in new_comments:
                author = comment.get('user', {}).get('login', 'Unknown')
                body = comment.get('body', '')[:200] + '...' if len(comment.get('body', '')) > 200 else comment.get('body', '')
                created_at = comment.get('created_at', '')
                
                print(f"\n  作者: @{author}")
                print(f"  时间: {created_at}")
                print(f"  内容: {body}")
            
            print("\n" + "="*60)
            print(f"  请查看PR: {PR_URL}")
            print("="*60 + "\n")
            
            last_comment_count = current_count
            return True
        else:
            print("  暂无新回复，继续等待...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  请求失败: {e}")
        return False


def main():
    print("="*60)
    print("  PR #437 回复监控脚本")
    print(f"  PR地址: {PR_URL}")
    print(f"  检查间隔: {CHECK_INTERVAL // 60}分钟")
    print(f"  当前评论数: {last_comment_count}")
    print("="*60 + "\n")
    
    while True:
        check_comments()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()