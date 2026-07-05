import requests
import time
import os
import sys

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
LAST_COMMENT_FILE = "/workspace/.last_comment_id"

def get_comments():
    try:
        response = requests.get(PR_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[{time.ctime()}] Error fetching comments: {e}", flush=True)
        return []

def load_last_comment_id():
    if os.path.exists(LAST_COMMENT_FILE):
        with open(LAST_COMMENT_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_comment_id(comment_id):
    with open(LAST_COMMENT_FILE, "w") as f:
        f.write(str(comment_id))

def main():
    print(f"[{time.ctime()}] Starting PR comment monitor for https://github.com/kyrolabs/awesome-langchain/pull/437", flush=True)
    print(f"Checking every {CHECK_INTERVAL} seconds...", flush=True)
    print("-" * 60, flush=True)
    
    initial_comments = get_comments()
    if initial_comments:
        last_id = str(initial_comments[-1]["id"])
        save_last_comment_id(last_id)
        print(f"[{time.ctime()}] Initial comments loaded. Last comment ID: {last_id}", flush=True)
        print(f"[{time.ctime()}] Total comments: {len(initial_comments)}", flush=True)
        for comment in initial_comments:
            author = comment["user"]["login"]
            created_at = comment["created_at"]
            body_preview = comment["body"][:100].replace("\n", " ") + "..." if len(comment["body"]) > 100 else comment["body"].replace("\n", " ")
            print(f"  - {author} ({created_at}): {body_preview}", flush=True)
    else:
        print(f"[{time.ctime()}] No comments found yet.", flush=True)
    
    print("-" * 60, flush=True)
    
    while True:
        time.sleep(CHECK_INTERVAL)
        comments = get_comments()
        
        if not comments:
            continue
            
        current_last_id = str(comments[-1]["id"])
        saved_last_id = load_last_comment_id()
        
        if current_last_id != saved_last_id:
            new_comments = [c for c in comments if str(c["id"]) > saved_last_id]
            save_last_comment_id(current_last_id)
            
            print(f"\n{'='*60}", flush=True)
            print(f"[{time.ctime()}] NEW REPLY DETECTED!", flush=True)
            print(f"{'='*60}", flush=True)
            
            for comment in new_comments:
                author = comment["user"]["login"]
                created_at = comment["created_at"]
                body = comment["body"].strip()
                print(f"\nAuthor: {author}", flush=True)
                print(f"Time: {created_at}", flush=True)
                print(f"Content:\n{body}", flush=True)
                print(f"\nLink: {comment['html_url']}", flush=True)
            
            print(f"\n{'='*60}", flush=True)
        else:
            print(f"[{time.ctime()}] No new comments. Total: {len(comments)}", flush=True)

if __name__ == "__main__":
    main()