#!/usr/bin/env python3
import urllib.request
import json
import os
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE = "/workspace/.last_pr_check"

def get_comments():
    try:
        req = urllib.request.Request(PR_URL)
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def get_last_check():
    if os.path.exists(LAST_CHECK_FILE):
        with open(LAST_CHECK_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_check(comment_id):
    with open(LAST_CHECK_FILE, 'w') as f:
        f.write(str(comment_id))

def check_for_new_replies():
    comments = get_comments()
    if not comments:
        print("No comments found.")
        return
    
    last_comment_id = get_last_check()
    latest_comment = comments[-1]
    latest_id = str(latest_comment['id'])
    
    your_comment_ids = [str(c['id']) for c in comments if c['user']['login'] == 'yusishuma']
    
    has_new_reply = False
    if last_comment_id is None:
        print(f"Initial check. Latest comment ID: {latest_id}")
        save_last_check(latest_id)
    elif latest_id != last_comment_id:
        for comment in comments:
            if str(comment['id']) > last_comment_id:
                if comment['user']['login'] != 'yusishuma':
                    has_new_reply = True
                    print(f"\n=== NEW REPLY DETECTED ===")
                    print(f"Author: {comment['user']['login']}")
                    print(f"Time: {comment['created_at']}")
                    print(f"Content:\n{comment['body']}")
                    print("==========================")
        
        save_last_check(latest_id)
    
    if not has_new_reply and last_comment_id is not None:
        print(f"No new replies since last check.")
    
    print(f"\nPR Status Summary:")
    print(f"Total comments: {len(comments)}")
    print(f"Your comments: {len(your_comment_ids)}")
    print(f"Latest comment by: {latest_comment['user']['login']}")
    print(f"Latest comment time: {latest_comment['created_at']}")

if __name__ == "__main__":
    print(f"Checking PR #437 comments at {datetime.now().isoformat()}")
    check_for_new_replies()
    print("-" * 50)