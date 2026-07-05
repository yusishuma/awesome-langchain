import requests
import time
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
INTERVAL = 3600

def get_comments():
    try:
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print(f"Rate limited, retrying later", flush=True)
            return None
        else:
            print(f"Failed to fetch comments: {response.status_code}", flush=True)
            return None
    except Exception as e:
        print(f"Error fetching comments: {e}", flush=True)
        return None

def check_new_comments(last_comment_id=None):
    comments = get_comments()
    if not comments:
        return False, []
    
    new_comments = []
    for comment in comments:
        if last_comment_id is None or comment["id"] > last_comment_id:
            new_comments.append({
                "id": comment["id"],
                "user": comment["user"]["login"],
                "body": comment["body"][:100] + "..." if len(comment["body"]) > 100 else comment["body"],
                "created_at": comment["created_at"]
            })
    
    if new_comments:
        return True, new_comments
    return False, []

def main():
    print(f"Starting PR monitor for {PR_URL}", flush=True)
    print(f"Checking every {INTERVAL/60} minutes...\n", flush=True)
    
    comments = get_comments()
    last_comment_id = comments[-1]["id"] if comments else None
    
    print(f"Initial check - Last comment ID: {last_comment_id}", flush=True)
    if comments:
        print(f"Current comment count: {len(comments)}", flush=True)
        print("=" * 60, flush=True)
    
    counter = 0
    while True:
        try:
            counter += 1
            has_new, new_comments = check_new_comments(last_comment_id)
            if has_new:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NEW REPLY DETECTED!", flush=True)
                print("=" * 60, flush=True)
                for comment in new_comments:
                    print(f"User: @{comment['user']}", flush=True)
                    print(f"Time: {comment['created_at']}", flush=True)
                    print(f"Content: {comment['body']}", flush=True)
                    print("-" * 60, flush=True)
                last_comment_id = new_comments[-1]["id"]
                print("\n*** NEW REPLY FOUND! ***", flush=True)
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Check #{counter} - No new replies yet", flush=True)
            
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\nStopping monitor...", flush=True)
            break
        except Exception as e:
            print(f"Error: {e}", flush=True)
            time.sleep(INTERVAL)

if __name__ == "__main__":
    main()