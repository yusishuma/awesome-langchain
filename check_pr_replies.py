import time
import requests
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
LAST_COMMENT_IDS = set()

def get_comments():
    try:
        response = requests.get(PR_URL)
        if response.status_code == 403:
            print(f"[{datetime.now()}] API rate limited. Waiting longer...")
            return None, True
        elif response.status_code != 200:
            print(f"[{datetime.now()}] API request failed: {response.status_code}")
            return None, False
        return response.json(), False
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching comments: {e}")
        return None, False

def check_for_replies():
    global LAST_COMMENT_IDS
    
    comments, rate_limited = get_comments()
    
    if rate_limited:
        return True
    
    if comments is None or not isinstance(comments, list):
        return False
    
    if not LAST_COMMENT_IDS:
        LAST_COMMENT_IDS = {c['id'] for c in comments}
        print(f"[{datetime.now()}] Initial check: Found {len(comments)} comments")
        for idx, c in enumerate(comments, 1):
            author = c.get('user', {}).get('login', 'unknown')
            created_at = c.get('created_at', '')
            body = c.get('body', '')
            if len(body) > 150:
                body = body[:150] + '...'
            print(f"  Comment {idx}: @{author} at {created_at}")
            print(f"    {body}")
        print()
        return False
    
    current_ids = {c['id'] for c in comments}
    new_ids = current_ids - LAST_COMMENT_IDS
    
    if new_ids:
        print(f"\n{'='*60}")
        print(f"[{datetime.now()}] NEW REPLY DETECTED!")
        print(f"{'='*60}")
        for c in comments:
            if c['id'] in new_ids:
                author = c.get('user', {}).get('login', 'unknown')
                created_at = c.get('created_at', '')
                body = c.get('body', '')
                print(f"\nFrom: @{author}")
                print(f"Time: {created_at}")
                print(f"Content:\n{body}")
        print(f"\n{'='*60}")
        LAST_COMMENT_IDS = current_ids
        return True
    else:
        print(f"[{datetime.now()}] No new replies yet (total: {len(comments)})")
        return False

if __name__ == "__main__":
    print(f"Starting PR reply monitor for https://github.com/kyrolabs/awesome-langchain/pull/437")
    print(f"Checking every {CHECK_INTERVAL/60} minutes...")
    print()
    
    check_for_replies()
    
    while True:
        time.sleep(CHECK_INTERVAL)
        if check_for_replies():
            print("\nYou have a new reply! Consider checking the PR page.")