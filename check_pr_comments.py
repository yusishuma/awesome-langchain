import urllib.request
import json
import time
import os

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_COMMENT_FILE = "/workspace/.last_pr_comment_id"


def get_comments():
    try:
        req = urllib.request.Request(PR_URL, headers={'User-Agent': 'PR-Monitor/1.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'message' in data:
                print(f"API Error: {data['message']}")
                return []
            return []
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []


def get_last_comment_id():
    if os.path.exists(LAST_COMMENT_FILE):
        with open(LAST_COMMENT_FILE, 'r') as f:
            content = f.read().strip()
            return int(content) if content else 0
    return 0


def set_last_comment_id(comment_id):
    with open(LAST_COMMENT_FILE, 'w') as f:
        f.write(str(comment_id))


def check_for_new_replies():
    comments = get_comments()
    if not comments:
        print("No comments found or failed to fetch.")
        return False
    
    last_id = get_last_comment_id()
    new_comments = [c for c in comments if c['id'] > last_id]
    
    if new_comments:
        print("\n=== NEW REPLIES FOUND ===")
        for comment in new_comments:
            author = comment['user']['login']
            created_at = comment['created_at']
            body = comment['body'][:500] + "..." if len(comment['body']) > 500 else comment['body']
            
            print(f"\nAuthor: @{author}")
            print(f"Time: {created_at}")
            print(f"Content:\n{body}\n")
            print(f"URL: {comment['html_url']}")
        
        set_last_comment_id(max(c['id'] for c in comments))
        return True
    else:
        print("No new replies yet.")
        return False


def main():
    print("=== PR Comment Monitor ===")
    print("Monitoring: https://github.com/kyrolabs/awesome-langchain/pull/437")
    print("Checking every 30 minutes...\n")
    
    comments = get_comments()
    if comments:
        latest_id = max(c['id'] for c in comments)
        if not get_last_comment_id():
            set_last_comment_id(latest_id)
            print(f"Initializing with {len(comments)} existing comments.")
    else:
        print("Failed to initialize - no comments found.")
    
    while True:
        print(f"\nChecking at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
        check_for_new_replies()
        time.sleep(1800)


if __name__ == "__main__":
    main()