import urllib.request
import urllib.error
import json
import time
import random

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CHECK_INTERVAL = 3600
LAST_COMMENT_TIME = None
LAST_COMMENT_AUTHOR = None

def get_comments():
    try:
        req = urllib.request.Request(PR_URL, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=30)
        data = response.read().decode('utf-8')
        return json.loads(data)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"API Rate Limit hit. Retrying later...")
        else:
            print(f"HTTP Error: {e.code}")
        return None
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return None

def format_comment(comment):
    author = comment.get('user', {}).get('login', 'Unknown')
    created_at = comment.get('created_at', '')
    body = comment.get('body', '')[:150] + '...' if len(comment.get('body', '')) > 150 else comment.get('body', '')
    return f"👤 {author}\n📅 {created_at}\n💬 {body}\n---"

def check_for_updates():
    global LAST_COMMENT_TIME, LAST_COMMENT_AUTHOR
    comments = get_comments()
    if comments is None:
        return False
    if not comments:
        print("No comments found")
        return False
    
    latest_comment = comments[-1]
    latest_time = latest_comment.get('created_at')
    author = latest_comment.get('user', {}).get('login', '')
    
    if LAST_COMMENT_TIME is None:
        LAST_COMMENT_TIME = latest_time
        LAST_COMMENT_AUTHOR = author
        print(f"=== Initial Check ===")
        print(f"Total comments: {len(comments)}")
        print(f"Latest comment by: {author}")
        print(f"Time: {latest_time}")
        print(format_comment(latest_comment))
        
        if author == 'yusishuma':
            print("\n⚠️  No new replies yet. Waiting for maintainer response...")
        return False
    
    if latest_time > LAST_COMMENT_TIME:
        LAST_COMMENT_TIME = latest_time
        LAST_COMMENT_AUTHOR = author
        print(f"\n=== NEW REPLY DETECTED ===")
        print(format_comment(latest_comment))
        print("\n🎉 There's a new reply to your PR!")
        return True
    else:
        print(f"⏰ Checked at {time.strftime('%Y-%m-%d %H:%M:%S')} - No new replies (latest: {author} at {latest_time})")
        return False

print(f"Starting PR comment monitor for https://github.com/kyrolabs/awesome-langchain/pull/437")
print(f"Checking every {CHECK_INTERVAL/60} minutes...\n")

check_for_updates()

while True:
    sleep_time = CHECK_INTERVAL + random.randint(0, 600)
    print(f"\nSleeping for {sleep_time//60} minutes {sleep_time%60} seconds...")
    time.sleep(sleep_time)
    if check_for_updates():
        print("\n✅ New reply found! Exiting monitor.")
        break