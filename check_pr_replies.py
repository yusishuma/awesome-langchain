import urllib.request
import urllib.error
import json
import time
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
USER_LOGIN = "yusishuma"

def get_comments():
    try:
        req = urllib.request.Request(PR_URL, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"[ERROR] Failed to fetch comments: {e}")
        return []

def check_new_replies(known_comment_ids):
    comments = get_comments()
    new_replies = []
    
    for comment in comments:
        comment_id = comment["id"]
        author = comment["user"]["login"]
        body = comment["body"]
        created_at = comment["created_at"]
        
        if comment_id not in known_comment_ids:
            known_comment_ids.add(comment_id)
            
            if author != USER_LOGIN:
                new_replies.append({
                    "author": author,
                    "body": body,
                    "created_at": created_at
                })
    
    return new_replies, known_comment_ids

def main():
    print(f"[START] Monitoring PR #437 for replies (checking every {CHECK_INTERVAL/60} minutes)")
    print(f"[INFO] Current time: {datetime.now()}")
    
    comments = get_comments()
    known_comment_ids = {c["id"] for c in comments}
    
    print(f"[INFO] Found {len(known_comment_ids)} existing comments")
    
    for comment in comments:
        author = comment["user"]["login"]
        created_at = comment["created_at"]
        print(f"  - {author} ({created_at})")
    
    print("\n[INFO] Waiting for new replies...\n")
    
    while True:
        new_replies, known_comment_ids = check_new_replies(known_comment_ids)
        
        if new_replies:
            print(f"[ALERT] NEW REPLY DETECTED at {datetime.now()}")
            print("=" * 60)
            for reply in new_replies:
                print(f"Author: {reply['author']}")
                print(f"Time: {reply['created_at']}")
                print(f"Content:\n{reply['body']}")
                print("-" * 60)
            print("\n[INFO] You have received a reply! Please check the PR:")
            print("https://github.com/kyrolabs/awesome-langchain/pull/437")
            break
        else:
            print(f"[CHECK] No new replies at {datetime.now()}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()