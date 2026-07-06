import requests
import time
import json
from datetime import datetime

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300

def load_last_check():
    try:
        with open('/workspace/pr_last_check.json', 'r') as f:
            return json.load(f)
    except:
        return {"last_comment_count": 0, "last_check": ""}

def save_last_check(count):
    data = {"last_comment_count": count, "last_check": datetime.now().isoformat()}
    with open('/workspace/pr_last_check.json', 'w') as f:
        json.dump(data, f)

def check_comments():
    try:
        response = requests.get(PR_URL)
        response.raise_for_status()
        comments = response.json()
        return len(comments), comments
    except Exception as e:
        print(f"Error checking comments: {e}")
        return 0, []

def get_non_user_comments(comments, username="yusishuma"):
    non_user = []
    for comment in comments:
        if comment['user']['login'] != username:
            non_user.append({
                'user': comment['user']['login'],
                'body': comment['body'],
                'created_at': comment['created_at']
            })
    return non_user

def main():
    print(f"Starting PR reply monitor for https://github.com/kyrolabs/awesome-langchain/pull/437")
    print(f"Checking every {CHECK_INTERVAL/60} minutes...\n")
    
    last_data = load_last_check()
    last_count = last_data["last_comment_count"]
    print(f"Previous check: {last_data['last_check']}")
    print(f"Previous comment count: {last_count}\n")
    
    while True:
        count, comments = check_comments()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if count > last_count:
            new_comments = comments[last_count:]
            non_user = get_non_user_comments(new_comments)
            
            if non_user:
                print("=" * 60)
                print(f"NEW REPLY DETECTED at {now}!")
                print("=" * 60)
                for c in non_user:
                    print(f"\nUser: @{c['user']}")
                    print(f"Time: {c['created_at']}")
                    print(f"Content:\n{c['body']}")
                    print("-" * 60)
            else:
                print(f"[{now}] New comment(s) detected but only from your account")
            
            last_count = count
            save_last_check(count)
        else:
            print(f"[{now}] No new replies. Total comments: {count}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()