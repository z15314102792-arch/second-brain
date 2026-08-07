"""每日综合速报 - AI分析 + 微信推送"""
import urllib.request
import urllib.parse
import json
import os
import sys

DATE = os.environ.get('DATE', 'unknown')
DEEPSEEK_KEY = os.environ['DEEPSEEK_KEY']
SCT_KEY = os.environ['SCT_KEY']

# 读取新闻数据
news_raw = ''
try:
    with open('/tmp/news_raw.txt', 'r') as f:
        news_raw = f.read()
except FileNotFoundError:
    pass

# 构建提示词
prompt = (
    "你是我的私人AI管家。根据以下数据生成每日综合速报。\n\n"
    "格式:\n"
    "### 🗞️ AI动态\n"
    "选出3-5条新闻,每条: **[中文标题](链接)** + 一句话解释 + 💡跟你有啥关系\n\n"
    "### 🩺 项目状态\n"
    f"四个项目: 象棋HTTP={os.environ.get('CHESS_HTTP','?')} "
    f"五子棋HTTP={os.environ.get('GOMOKU_HTTP','?')} "
    f"画猜HTTP={os.environ.get('DRAW_HTTP','?')} "
    f"神殿HTTP={os.environ.get('TEMPLE_HTTP','?')}\n\n"
    "### 📌 一句话\n总结\n\n"
    "数据:\n" + news_raw
)

# 调用 DeepSeek
body = json.dumps({
    'model': 'deepseek-chat',
    'messages': [{'role': 'user', 'content': prompt}],
    'temperature': 0.7,
    'max_tokens': 3000
}, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request(
    'https://api.deepseek.com/v1/chat/completions',
    data=body,
    headers={
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {DEEPSEEK_KEY}'
    }
)
resp = json.loads(urllib.request.urlopen(req, timeout=90).read())
digest = resp['choices'][0]['message']['content']
tokens = resp['usage']['total_tokens']
print(f"DeepSeek: {tokens} tokens")

# 保存结果
with open('/tmp/digest.md', 'w', encoding='utf-8') as f:
    f.write(digest)

# 微信推送
preview = digest[:1500]
data = urllib.parse.urlencode({
    'title': f'每日速报 | {DATE}',
    'desp': preview
}).encode('utf-8')

r = urllib.request.urlopen(urllib.request.Request(
    f'https://sctapi.ftqq.com/{SCT_KEY}.send',
    data=data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
))
print(f"WeChat: {r.read().decode()[:100]}")
