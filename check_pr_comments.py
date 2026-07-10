import json
import os
import time
from datetime import datetime

PR_NUMBER = 437
REPO = "kyrolabs/awesome-langchain"
API_URL = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
STATE_FILE = "/workspace/.pr_comment_state"


def get_comments():
    import urllib.request
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching comments: {e}")
        return None


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_comment_count": 0, "last_check_time": None}


def save_state(count):
    state = {"last_comment_count": count, "last_check_time": datetime.now().isoformat()}
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def check_for_new_comments():
    comments = get_comments()
    if comments is None:
        return
    
    current_count = len(comments)
    state = load_state()
    last_count = state["last_comment_count"]
    
    print(f"[{datetime.now()}] Checking PR #{PR_NUMBER}...")
    print(f"  Current comment count: {current_count}")
    print(f"  Previous comment count: {last_count}")
    
    if current_count > last_count:
        print("\n  ==================== NEW REPLY DETECTED! ====================")
        new_comments = comments[last_count:]
        for comment in new_comments:
            author = comment["user"]["login"]
            created_at = comment["created_at"]
            body = comment["body"].strip()[:300] + "..." if len(comment["body"]) > 300 else comment["body"]
            print(f"\n  Author: @{author}")
            print(f"  Time: {created_at}")
            print(f"  Content: {body}")
            print(f"  Link: {comment['html_url']}")
        print("  ==============================================================\n")
        
        save_state(current_count)
        return True
    else:
        print("  No new comments.\n")
        save_state(current_count)
        return False


if __name__ == "__main__":
    check_for_new_comments()