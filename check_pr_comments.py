import time
import requests
import json
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300  
LAST_COMMENT_TIME_FILE = "/workspace/last_comment_time.txt"

def load_last_comment_time():
    try:
        with open(LAST_COMMENT_TIME_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_comment_time(comment_time):
    with open(LAST_COMMENT_TIME_FILE, "w") as f:
        f.write(comment_time)

def get_comments():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[{datetime.now()}] Failed to fetch comments: HTTP {response.status_code}", flush=True)
            return None
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching comments: {e}", flush=True)
        return None

def check_for_new_replies():
    comments = get_comments()
    if not comments:
        return
    
    last_comment_time = load_last_comment_time()
    
    if not last_comment_time:
        latest_comment = comments[-1] if comments else None
        if latest_comment:
            last_comment_time = latest_comment['created_at']
            save_last_comment_time(last_comment_time)
            print(f"[{datetime.now()}] Initialized. Last comment time: {last_comment_time}", flush=True)
        return
    
    new_comments = []
    for comment in comments:
        if comment['created_at'] > last_comment_time:
            new_comments.append(comment)
    
    if new_comments:
        print(f"\n{'='*60}", flush=True)
        print(f"[{datetime.now()}] NEW REPLY FOUND!", flush=True)
        print(f"{'='*60}", flush=True)
        for comment in new_comments:
            author = comment['user']['login']
            body = comment['body'][:200] + "..." if len(comment['body']) > 200 else comment['body']
            created_at = comment['created_at']
            print(f"\nAuthor: @{author}", flush=True)
            print(f"Time: {created_at}", flush=True)
            print(f"Content: {body}", flush=True)
            print(f"Link: {PR_URL}#issuecomment-{comment['id']}", flush=True)
        
        save_last_comment_time(new_comments[-1]['created_at'])
        print(f"\n{'='*60}", flush=True)
        print("Notification: You have a new reply on your PR!", flush=True)
        print(f"{'='*60}", flush=True)
        return True
    else:
        print(f"[{datetime.now()}] No new replies yet.", flush=True)
        return False

def main():
    print(f"[{datetime.now()}] Starting PR comment monitor for {PR_URL}", flush=True)
    print(f"Checking every {CHECK_INTERVAL} seconds...\n", flush=True)
    
    check_for_new_replies()
    
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            check_for_new_replies()
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Monitor stopped.", flush=True)
            break

if __name__ == "__main__":
    main()