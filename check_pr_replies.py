import requests
import time
import json

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
LAST_CHECK_FILE = "/workspace/last_pr_check.json"

def load_last_check():
    try:
        with open(LAST_CHECK_FILE, "r") as f:
            return json.load(f)
    except:
        return {"last_comment_count": 0, "last_check_time": ""}

def save_last_check(comment_count):
    data = {
        "last_comment_count": comment_count,
        "last_check_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
    with open(LAST_CHECK_FILE, "w") as f:
        json.dump(data, f)

def check_comments():
    try:
        print("正在请求GitHub API...", flush=True)
        response = requests.get(PR_URL, timeout=10)
        print(f"API响应状态: {response.status_code}", flush=True)
        response.raise_for_status()
        comments = response.json()
        print(f"获取到 {len(comments)} 条评论", flush=True)
        return len(comments), comments
    except Exception as e:
        print(f"Error checking comments: {e}", flush=True)
        return -1, []

def main():
    print(f"=== PR #437 定时检查启动 ===", flush=True)
    
    current_count, _ = check_comments()
    if current_count == -1:
        print("无法连接到GitHub API，退出", flush=True)
        return
    
    last_data = load_last_check()
    
    if last_data["last_comment_count"] == 0:
        last_data["last_comment_count"] = current_count
        save_last_check(current_count)
    
    print(f"当前评论数: {current_count}", flush=True)
    print(f"检查间隔: {CHECK_INTERVAL}秒", flush=True)
    print("=" * 40, flush=True)
    
    while True:
        print("\n等待下一次检查...", flush=True)
        time.sleep(CHECK_INTERVAL)
        
        current_count, comments = check_comments()
        if current_count == -1:
            continue
        
        current_time = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        
        if current_count > last_data["last_comment_count"]:
            print(f"\n[{current_time}] 发现新回复！", flush=True)
            print(f"评论数从 {last_data['last_comment_count']} 增加到 {current_count}", flush=True)
            
            new_comments = comments[last_data["last_comment_count"]:]
            for comment in new_comments:
                author = comment.get("user", {}).get("login", "Unknown")
                body = comment.get("body", "").strip()[:200]
                created_at = comment.get("created_at", "")
                print(f"\n作者: @{author}", flush=True)
                print(f"时间: {created_at}", flush=True)
                print(f"内容: {body}...", flush=True)
            
            print("\n" + "=" * 40, flush=True)
            save_last_check(current_count)
            last_data["last_comment_count"] = current_count
        else:
            print(f"[{current_time}] 暂无新回复，当前评论数: {current_count}", flush=True)

if __name__ == "__main__":
    main()