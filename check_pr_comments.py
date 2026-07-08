import subprocess
import time
import sys
import re

PR_URL = 'https://github.com/kyrolabs/awesome-langchain/pull/437'
CHECK_INTERVAL = 300

def get_comments():
    try:
        result = subprocess.run(
            ['curl', '-s', '-A', 'Mozilla/5.0', PR_URL],
            capture_output=True,
            text=True,
            timeout=30
        )
        html = result.stdout
        
        comment_sections = re.findall(r'<details class="review-comment[^>]*>[\s\S]*?</details>', html)
        timeline_items = re.findall(r'<div class="TimelineItem-body">[\s\S]*?</div>', html)
        
        comments = []
        
        for item in timeline_items:
            author_match = re.search(r'<a href="/([^"]+)"[^>]*class="[^"]*author[^"]*"', item)
            date_match = re.search(r'<relative-time datetime="([^"]+)"', item)
            body_match = re.search(r'<div class="comment-body">([\s\S]*?)</div>', item)
            
            if author_match:
                author = author_match.group(1)
                if 'comment-body' in item:
                    if date_match:
                        date_str = date_match.group(1)[:19].replace('T', ' ')
                    else:
                        date_str = 'Unknown'
                        
                    if body_match:
                        body = re.sub(r'<[^>]+>', '', body_match.group(1)).strip()[:300].replace('\n', ' ')
                    else:
                        body = 'No content'
                        
                    comments.append({
                        'author': author,
                        'date': date_str,
                        'body': body
                    })
        
        for section in comment_sections:
            author_match = re.search(r'<a href="/([^"]+)"[^>]*class="[^"]*author[^"]*"', section)
            date_match = re.search(r'<relative-time datetime="([^"]+)"', section)
            body_match = re.search(r'<td class="comment-body">([\s\S]*?)</td>', section)
            
            if author_match and body_match:
                author = author_match.group(1)
                if date_match:
                    date_str = date_match.group(1)[:19].replace('T', ' ')
                else:
                    date_str = 'Unknown'
                    
                body = re.sub(r'<[^>]+>', '', body_match.group(1)).strip()[:300].replace('\n', ' ')
                
                exists = False
                for c in comments:
                    if c['author'] == author and c['date'] == date_str:
                        exists = True
                        break
                
                if not exists:
                    comments.append({
                        'author': author,
                        'date': date_str,
                        'body': body
                    })
        
        return comments if comments else None
        
    except Exception as e:
        print(f'请求失败: {e}', flush=True)
        return None

def print_comments(comments):
    if not comments:
        print('没有获取到评论', flush=True)
        return
    
    print(f'\n=== PR #437 评论列表 ({len(comments)} 条) ===', flush=True)
    for i, comment in enumerate(comments, 1):
        print(f'\n{i}. [{comment["date"]}] @{comment["author"]}', flush=True)
        print(f'   {comment["body"]}', flush=True)

def main():
    print('开始定时检查 PR #437 的新回复...', flush=True)
    print(f'检查间隔: {CHECK_INTERVAL // 60} 分钟', flush=True)
    print('按 Ctrl+C 停止检查\n', flush=True)
    
    last_comment_count = None
    
    while True:
        comments = get_comments()
        if comments is None:
            time.sleep(CHECK_INTERVAL)
            continue
        
        current_count = len(comments)
        
        if last_comment_count is None:
            print_comments(comments)
            last_comment_count = current_count
        elif current_count > last_comment_count:
            print(f'\n✓ 发现新回复！当前评论数: {current_count}', flush=True)
            print_comments(comments[-1:])
            last_comment_count = current_count
        else:
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] 暂无新回复，当前评论数: {current_count}', flush=True)
        
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n检查已停止', flush=True)
        sys.exit(0)