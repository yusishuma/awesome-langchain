import urllib.request
import urllib.error
import json
import os
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"

def get_comments():
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def load_last_check():
    if os.path.exists("/workspace/.pr_last_check.json"):
        try:
            with open("/workspace/.pr_last_check.json", "r") as f:
                return json.load(f)
        except:
            return {"last_comment_id": 0, "last_check_time": ""}
    return {"last_comment_id": 0, "last_check_time": ""}

def save_last_check(last_comment_id):
    data = {
        "last_comment_id": last_comment_id,
        "last_check_time": datetime.now().isoformat()
    }
    with open("/workspace/.pr_last_check.json", "w") as f:
        json.dump(data, f)

def format_comment(comment):
    user = comment.get("user", {}).get("login", "Unknown")
    created_at = comment.get("created_at", "")
    body = comment.get("body", "")
    return f"\n---\nAuthor: @{user}\nDate: {created_at}\n\n{body}\n"

def main():
    print(f"\n=== Checking PR #437 at {datetime.now()} ===")
    
    last_check = load_last_check()
    comments = get_comments()
    
    if not comments:
        print("No comments found or failed to fetch.")
        return
    
    max_comment_id = max(c["id"] for c in comments)
    
    new_comments = [c for c in comments if c["id"] > last_check["last_comment_id"]]
    
    if new_comments:
        print(f"🎉 Found {len(new_comments)} new comment(s)!")
        for comment in sorted(new_comments, key=lambda x: x["id"]):
            print(format_comment(comment))
        save_last_check(max_comment_id)
    else:
        print("No new comments since last check.")
        save_last_check(max_comment_id)
    
    print(f"\nTotal comments: {len(comments)}")
    print(f"PR URL: {PR_URL}")

if __name__ == "__main__":
    main()