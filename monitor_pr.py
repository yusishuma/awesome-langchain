#!/usr/bin/env python3
import time
import subprocess
import sys
from datetime import datetime

INTERVAL_SECONDS = 300
SCRIPT_PATH = "/workspace/check_pr_comments.py"
PID_FILE = "/workspace/.pr_monitor.pid"


def run_check():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行检查...")
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode == 0


def main():
    import os
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    print(f"PR 评论监控已启动，PID: {os.getpid()}")
    print(f"检查间隔: {INTERVAL_SECONDS} 秒 ({INTERVAL_SECONDS // 60} 分钟)")
    print(f"日志文件: /workspace/pr_comments.log")
    print("按 Ctrl+C 停止监控")
    print("=" * 60)

    try:
        while True:
            run_check()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 等待 {INTERVAL_SECONDS // 60} 分钟后再次检查...")
            print()
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n监控已停止")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


if __name__ == "__main__":
    main()
