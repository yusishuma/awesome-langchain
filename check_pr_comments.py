import requests
import time
import re
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL = 600
USER_LOGIN = "yusishuma"
LOG_FILE = "/tmp/pr_monitor.log"

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_page_content():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(PR_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        log(f"Error fetching page: {e}")
        return None

def extract_non_user_comments(html):
    if not html:
        return []
    
    authors = re.findall(r'<a[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)</a>', html)
    
    comments = []
    for i, author in enumerate(authors):
        if author.strip() != USER_LOGIN:
            comments.append({
                "index": i,
                "author": author.strip()
            })
    
    return comments

def main():
    log("Starting PR #437 comment monitor...")
    log(f"Checking every {CHECK_INTERVAL/60} minutes for responses from maintainers")
    
    html = get_page_content()
    initial_comments = extract_non_user_comments(html)
    known_comment_count = len(initial_comments)
    
    log(f"Found {known_comment_count} non-user comments (excluding your own)")
    if initial_comments:
        for c in initial_comments:
            log(f"  - Author: @{c['author']}")
    
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            html = get_page_content()
            current_comments = extract_non_user_comments(html)
            
            if len(current_comments) > known_comment_count:
                new_comments = current_comments[known_comment_count:]
                
                log("\n" + "="*60)
                log("NEW RESPONSE DETECTED!")
                log("="*60)
                for resp in new_comments:
                    log(f"\nAuthor: @{resp['author']}")
                    log(f"URL: {PR_URL}")
                log("\n" + "="*60)
                
                known_comment_count = len(current_comments)
            else:
                log("No new responses yet...")
                
        except KeyboardInterrupt:
            log("Monitor stopped.")
            break
        except Exception as e:
            log(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()