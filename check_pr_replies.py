import requests
import time
import json
from datetime import datetime
import re

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 300
EXCLUDED_AUTHORS = {"yusishuma"}

def load_last_check_info():
    try:
        with open("last_check_info.json", "r") as f:
            data = json.load(f)
            return data.get("last_comment_count", 0), data.get("last_comment_author", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return 0, ""

def save_last_check_info(count, author):
    with open("last_check_info.json", "w") as f:
        json.dump({"last_comment_count": count, "last_comment_author": author}, f)

def get_comments():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 403:
            print("API rate limit exceeded, trying web page...")
            return get_comments_from_web()
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}, trying web page...")
        return get_comments_from_web()

def get_comments_from_web():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(PR_URL, headers=headers)
        response.raise_for_status()
        html = response.text
        
        comments = []
        author_pattern = r'<a[^>]+class="author"[^>]*>([^<]+)</a>'
        time_pattern = r'<relative-time[^>]+datetime="([^"]+)"[^>]*>'
        body_pattern = r'<td class="comment-body">[^<]*<p>([^<]+)</p>'
        
        authors = re.findall(author_pattern, html)
        times = re.findall(time_pattern, html)
        bodies = re.findall(body_pattern, html)
        
        n = min(len(authors), len(times), len(bodies))
        for i in range(n):
            comment_time = datetime.strptime(times[i], "%Y-%m-%dT%H:%M:%SZ")
            comments.append({
                "user": {"login": authors[i]},
                "created_at": times[i],
                "body": bodies[i],
                "html_url": f"{PR_URL}#comment-{i+1}"
            })
        
        return comments
    except requests.exceptions.RequestException as e:
        print(f"Web page error: {e}")
        return []

def check_for_new_replies():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking PR #437 for new replies...")
    
    comments = get_comments()
    
    if not comments:
        print("No comments found or fetch failed.")
        return
    
    last_count, last_author = load_last_check_info()
    
    filtered_comments = []
    for comment in comments:
        author = comment["user"]["login"]
        if author not in EXCLUDED_AUTHORS:
            filtered_comments.append({
                "author": author,
                "time": comment["created_at"],
                "body": comment["body"],
                "url": comment.get("html_url", "")
            })
    
    has_new = False
    if filtered_comments:
        current_count = len(filtered_comments)
        current_author = filtered_comments[-1]["author"]
        
        if current_count > last_count or (current_count == last_count and current_author != last_author):
            has_new = True
    
    if has_new:
        print("\n📢 NEW REPLIES FOUND!")
        for comment in filtered_comments:
            comment_dt = datetime.strptime(comment["time"], "%Y-%m-%dT%H:%M:%SZ")
            print(f"\nAuthor: @{comment['author']}")
            print(f"Time: {comment_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"URL: {comment['url']}")
            print(f"Content: {comment['body']}")
        
        save_last_check_info(len(filtered_comments), filtered_comments[-1]["author"])
        print(f"\n✅ Latest check info saved.")
        return True
    else:
        print("No new replies yet.")
        if filtered_comments:
            save_last_check_info(len(filtered_comments), filtered_comments[-1]["author"])
        return False

def main():
    print(f"Starting PR #437 monitoring...")
    print(f"Checking every {CHECK_INTERVAL // 60} minutes")
    print(f"PR URL: {PR_URL}\n")
    
    while True:
        found_new = check_for_new_replies()
        if found_new:
            print("\n🎉 Notification: New reply received! Stopping monitor.")
            break
        print(f"Waiting {CHECK_INTERVAL // 60} minutes for next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()