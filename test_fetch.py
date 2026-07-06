import urllib.request

print('Testing urllib...')
try:
    req = urllib.request.Request('https://api.github.com/repos/kyrolabs/awesome-langchain/issues/437/comments', headers={'User-Agent': 'test'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        print('Success! Response length:', len(data))
except Exception as e:
    print('Error:', e)