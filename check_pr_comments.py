import time
import urllib.request
import urllib.error
import json
import os
import re
import sys

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
API_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
LAST_CHECK_FILE = "/tmp/pr_437_last_check.json"
CHECK_INTERVAL = 300

def log(msg):
    print(msg, flush=True)

def get_comments():
    try:
        req = urllib.request.Request(API_URL, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                data = response.read().decode('utf-8')
                return json.loads(data)
            elif response.getcode() == 403:
                log("  Rate limited, trying web page fallback...")
                return get_comments_web()
            else:
                log(f"  API request failed: {response.getcode()}")
                return None
    except urllib.error.HTTPError as e:
        if e.code == 403:
            log("  Rate limited, trying web page fallback...")
            return get_comments_web()
        log(f"  HTTP error: {e.code}")
        return None
    except Exception as e:
        log(f"  Error fetching comments: {e}")
        return None

def get_comments_web():
    try:
        req = urllib.request.Request(PR_URL)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                content = response.read().decode('utf-8')
                comments = []
                pattern = r'"login":"([^"]+)"[^}]*"created_at":"([^"]+)"'
                for match in re.finditer(pattern, content):
                    comments.append({
                        "user": match.group(1),
                        "created_at": match.group(2)
                    })
                return comments
            else:
                log(f"  Web request failed: {response.getcode()}")
                return None
    except Exception as e:
        log(f"  Error fetching web page: {e}")
        return None

def load_last_check():
    if os.path.exists(LAST_CHECK_FILE):
        try:
            with open(LAST_CHECK_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"count": 0, "comments": []}
    return {"count": 0, "comments": []}

def save_last_check(data):
    with open(LAST_CHECK_FILE, 'w') as f:
        json.dump(data, f)

def main():
    log("=== Starting PR comment checker ===")
    log(f"PR: {PR_URL}")
    log(f"Checking every {CHECK_INTERVAL} seconds...")
    log("")
    
    last_check = load_last_check()
    
    if last_check["count"] == 0:
        log("Initializing...")
        comments = get_comments()
        if comments:
            count = len(comments)
            last_check = {"count": count, "comments": comments}
            save_last_check(last_check)
            log(f"  Initial comment count: {count}")
            for c in comments:
                user = c.get("user", c.get("author", {}).get("login", "unknown"))
                date = c.get("created_at", "unknown")
                log(f"    - {user} at {date}")
        else:
            log("  Failed to initialize")
        log("")
    
    while True:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        log(f"[{now}] Checking for new comments...")
        
        comments = get_comments()
        
        if not comments:
            log("  Failed to fetch data, retrying...")
            time.sleep(CHECK_INTERVAL)
            continue
        
        current_count = len(comments)
        log(f"  Current comment count: {current_count}")
        log(f"  Last check count: {last_check['count']}")
        
        if current_count > last_check["count"]:
            log("")
            log("=== NEW COMMENT DETECTED ===")
            log(f"  Current: {current_count} comments")
            log(f"  Previous: {last_check['count']} comments")
            log(f"  PR URL: {PR_URL}")
            log("  New comments:")
            for c in comments[-current_count + last_check["count"]:]:
                user = c.get("user", c.get("author", {}).get("login", "unknown"))
                date = c.get("created_at", "unknown")
                log(f"    - {user} at {date}")
            log("=== NEW COMMENT DETECTED ===")
            log("")
            last_check = {"count": current_count, "comments": comments}
            save_last_check(last_check)
        else:
            log("  No new comments.")
        
        log("")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()