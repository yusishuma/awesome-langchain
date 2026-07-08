import subprocess
import time
import sys

def main():
    print("Starting PR #437 monitoring...")
    print("Checking every hour for new comments...")
    print("Press Ctrl+C to stop.\n")
    
    while True:
        try:
            result = subprocess.run(["python3", "/workspace/check_pr_comments.py"], 
                                  capture_output=True, text=True, timeout=30)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"STDERR: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Check timed out")
        except Exception as e:
            print(f"Error during check: {e}")
        
        time.sleep(3600)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping monitoring.")
        sys.exit(0)