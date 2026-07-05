import urllib.request
import urllib.error
import time
import json
import os

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
STATE_FILE = "/workspace/pr_comments_state.json"

def get_comments():
    try:
        req = urllib.request.Request(PR_URL, headers={'Accept': 'application/vnd.github.v3+json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return []
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"last_comment_id": 0, "last_check_time": ""}
    return {"last_comment_id": 0, "last_check_time": ""}

def save_state(comment_id):
    state = {
        "last_comment_id": comment_id,
        "last_check_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def print_comments(comments):
    if not comments:
        print("No new comments found.")
        return
    
    print("\n=== NEW COMMENTS ===")
    for comment in comments:
        author = comment.get('user', {}).get('login', 'Unknown')
        body = comment.get('body', '')
        created_at = comment.get('created_at', '')
        
        print(f"\nAuthor: {author}")
        print(f"Time: {created_at}")
        print(f"Content:\n{body}")
        print("-" * 50)

def main():
    print(f"Starting PR comment monitor for https://github.com/kyrolabs/awesome-langchain/pull/437")
    print(f"Checking every {CHECK_INTERVAL} seconds...\n")
    
    state = load_state()
    last_comment_id = state["last_comment_id"]
    
    if last_comment_id > 0:
        print(f"Last checked at: {state['last_check_time']}")
        print(f"Last comment ID: {last_comment_id}\n")
    
    while True:
        comments = get_comments()
        
        if comments:
            comments.sort(key=lambda x: x.get('id', 0))
            new_comments = [c for c in comments if c.get('id', 0) > last_comment_id]
            
            if new_comments:
                print_comments(new_comments)
                last_comment_id = new_comments[-1].get('id', 0)
                save_state(last_comment_id)
            else:
                print(f"No new comments at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"Failed to fetch comments at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()