import time
from datetime import datetime

CHECK_INTERVAL_MINUTES = 60


def main():
    print(f"[{datetime.now()}] Starting PR #437 watcher...")
    print(f"  Check interval: {CHECK_INTERVAL_MINUTES} minutes")
    print(f"  Press Ctrl+C to stop\n")
    
    try:
        while True:
            os.system("python3 /workspace/check_pr_comments.py")
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Watcher stopped.")


if __name__ == "__main__":
    import os
    main()