import time
import subprocess
import re
import sys
from datetime import datetime

PR_URL = "https://github.com/kyrolabs/awesome-langchain/pull/437"
CHECK_INTERVAL = 300
LAST_COMMENT_COUNT = 1

def log(msg):
    print(msg)
    sys.stdout.flush()

def fetch_pr_info():
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", PR_URL, "-H", "User-Agent: Mozilla/5.0"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log(f"Failed to fetch PR info: {result.stderr}")
            return None
    except Exception as e:
        log(f"Error fetching PR info: {e}")
        return None

def parse_comment_count(html_content):
    pattern = r'Conversation\s*(\d+)'
    match = re.search(pattern, html_content)
    if match:
        return int(match.group(1))
    return 0

def parse_participants(html_content):
    pattern = r'(\d+)\s*participants'
    match = re.search(pattern, html_content)
    if match:
        return int(match.group(1))
    return 0

def parse_comment_authors(html_content):
    authors = set()
    patterns = [
        r'<a[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)</a>',
        r'<span[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)</span>',
        r'data-hovercard-url="[^"]*users/([^/"]+)"'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content)
        for match in matches:
            authors.add(match.strip())
    
    return authors

def main():
    log(f"Starting PR comment monitor for {PR_URL}")
    log(f"Checking every {CHECK_INTERVAL} seconds...\n")
    
    global LAST_COMMENT_COUNT
    known_authors = {"yusishuma", "botbocks"}
    
    while True:
        log(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for updates...")
        
        html_content = fetch_pr_info()
        
        if html_content:
            comment_count = parse_comment_count(html_content)
            participant_count = parse_participants(html_content)
            current_authors = parse_comment_authors(html_content)
            
            new_authors = current_authors - known_authors
            
            log(f"Current state:")
            log(f"  - Comments: {comment_count}")
            log(f"  - Participants: {participant_count}")
            log(f"  - Authors: {current_authors}")
            
            if new_authors:
                log(f"\n  🎉 NEW COMMENT ALERT! New author(s) detected: {new_authors}")
                log(f"  Please check the PR: {PR_URL}\n")
                known_authors.update(new_authors)
            
            if comment_count > LAST_COMMENT_COUNT:
                log(f"\n  🎉 NEW COMMENT DETECTED! Comment count increased from {LAST_COMMENT_COUNT} to {comment_count}")
                log(f"  Please check the PR: {PR_URL}\n")
                LAST_COMMENT_COUNT = comment_count
            else:
                log("  No new comments detected\n")
        else:
            log("Failed to fetch PR information\n")
        
        log(f"Next check in {CHECK_INTERVAL} seconds...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()