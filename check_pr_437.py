import requests
import json
import os
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LOG_FILE = "/workspace/pr_437_check.log"
STATE_FILE = "/workspace/pr_437_state.json"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            return {"last_comment_count": 0, "last_comment_ids": []}
    return {"last_comment_count": 0, "last_comment_ids": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_pr():
    log("开始检查 PR #437")
    
    try:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PR-Checker/1.0"
        }
        
        response = requests.get(API_URL, headers=headers, timeout=30)
        
        if response.status_code == 200:
            comments = response.json()
            current_count = len(comments)
            current_ids = [comment["id"] for comment in comments]
            
            log(f"当前评论数: {current_count}")
            
            state = load_state()
            
            if current_count > state["last_comment_count"]:
                new_comments = [c for c in comments if c["id"] not in state["last_comment_ids"]]
                
                log("发现新回复！")
                for comment in new_comments:
                    author = comment.get("user", {}).get("login", "unknown")
                    body_preview = comment.get("body", "")[:100]
                    created_at = comment.get("created_at", "")
                    log(f"  - {author} ({created_at}): {body_preview}...")
                
                log(f"请访问: {PR_URL}")
                state["last_comment_count"] = current_count
                state["last_comment_ids"] = current_ids
                save_state(state)
                return True
            elif current_count == state["last_comment_count"]:
                log("暂无新回复")
                return False
            else:
                log("评论数减少（可能是页面变化）")
                state["last_comment_count"] = current_count
                state["last_comment_ids"] = current_ids
                save_state(state)
                return False
        else:
            log(f"API请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"检查失败: {str(e)}")
        return False

if __name__ == "__main__":
    check_pr()