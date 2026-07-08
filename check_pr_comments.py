#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import time
import os

PR_URL = "https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments"
CACHE_FILE = "/workspace/pr_comments_cache.json"
CHECK_INTERVAL = 300

def get_comments():
    try:
        req = urllib.request.Request(PR_URL, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"网络请求失败: {e}")
        return None
    except Exception as e:
        print(f"请求出错: {e}")
        return None

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_cache(comments):
    with open(CACHE_FILE, 'w') as f:
        json.dump(comments, f)

def has_new_comments(old_comments, new_comments):
    old_ids = {c['id'] for c in old_comments}
    new_ids = {c['id'] for c in new_comments}
    return new_ids - old_ids

def format_comment(comment):
    author = comment.get('user', {}).get('login', 'unknown')
    created_at = comment.get('created_at', '')
    body = comment.get('body', '')[:200] + '...' if len(comment.get('body', '')) > 200 else comment.get('body', '')
    return f"\n作者: {author}\n时间: {created_at}\n内容: {body}\n链接: {comment.get('html_url', '')}"

def main():
    print(f"开始监控 PR #437 的新回复...", flush=True)
    print(f"检查间隔: {CHECK_INTERVAL} 秒", flush=True)
    print(f"按 Ctrl+C 停止监控\n", flush=True)
    
    old_comments = load_cache()
    
    try:
        while True:
            new_comments = get_comments()
            
            if new_comments is None:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取评论失败，稍后重试...", flush=True)
                time.sleep(CHECK_INTERVAL)
                continue
            
            if not old_comments:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 首次获取，当前共有 {len(new_comments)} 条评论", flush=True)
                save_cache(new_comments)
                old_comments = new_comments
            else:
                new_ids = has_new_comments(old_comments, new_comments)
                if new_ids:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ 发现 {len(new_ids)} 条新回复!", flush=True)
                    for comment in new_comments:
                        if comment['id'] in new_ids:
                            print(format_comment(comment), flush=True)
                    save_cache(new_comments)
                    old_comments = new_comments
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 暂无新回复，当前评论数: {len(new_comments)}", flush=True)
            
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n监控已停止", flush=True)
        save_cache(old_comments)
        print("缓存已保存", flush=True)

if __name__ == "__main__":
    main()