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

# 项目健康状态：把 HTTP 码翻译成给人看的话
chess_http = os.environ.get('CHESS_HTTP', '?')
gomoku_http = os.environ.get('GOMOKU_HTTP', '?')
draw_http = os.environ.get('DRAW_HTTP', '?')
temple_http = os.environ.get('TEMPLE_HTTP', '?')

def desc(code, name, note=''):
    """把 HTTP 状态码翻译成中文说明"""
    if code == '200':
        return f'{name} ✅ 正常运行，网页可以正常打开访问'
    elif code == '404':
        return f'{name} ⚠️ 网页返回404（页面不存在）。{note}'
    elif code == '000':
        return f'{name} 🔴 无法连接，服务器可能挂了或网络不通'
    else:
        return f'{name} ❓ HTTP {code}（状态未知）'

# 构建提示词
prompt = (
    "你是我的私人AI管家。我是一个喜欢做小游戏的个人开发者，有几个业余项目部署在GitHub Pages上。"
    "请根据以下数据生成每日综合速报。\n\n"
    "## 格式要求\n\n"
    "### 🗞️ AI动态\n"
    "从原始新闻中选出3-5条，按重要程度排序。每条格式：\n\n"
    "**重要性：★★★（必读）/ ★★（值得关注）/ ★（知道就行）**\n\n"
    "**标题（中文翻译+链接）**\n\n"
    "- **发生了什么**：用2-3句话讲清楚这件事的核心内容，不要只扔个标题。比如：谁发布了什么、有什么用、怎么做到的。\n"
    "- **为什么重要**：对行业或开发者意味着什么。\n"
    "- **跟我有啥关系**：对我这个做小游戏的个人开发者，有什么实际影响或启发。无关的就说"暂时跟你关系不大"。\n\n"
    "判断重要性的标准：\n"
    "- ★★★：直接影响你的开发工具链、部署方式、或能帮你省钱省时间的\n"
    "- ★★：行业大趋势，最近可以关注的\n"
    "- ★：知道就行，当前不需要行动\n"
    "不要每一条都写得很长。★的简短，★★★的才展开写。\n\n"
    "### 🩺 项目状态\n\n"
    "四个项目的线上运行情况。记住：星月神殿已经退役了（不再维护），404是正常的，不要报错。\n\n"
    f"- {desc(chess_http, '中国象棋', '中国象棋双人对战游戏')}\n"
    f"- {desc(gomoku_http, '五子棋', '五子棋联机对战')}\n"
    f"- {desc(draw_http, '你画我猜', '你画我猜多人联机')}\n"
    f"- {desc(temple_http, '星月神殿', '已退役，404属正常状态')}\n\n"
    "如果有异常（不是200且不是退役项目），在下方单独列出需要处理的项目，用通俗语言说明可能的原因和修复方向。\n\n"
    "### 📌 今日小结\n"
    "2-3句话总结今天最重要的信息和需要做的事。\n\n"
    "原始新闻数据：\n" + news_raw
)

# 调用 DeepSeek
body = json.dumps({
    'model': 'deepseek-chat',
    'messages': [{'role': 'user', 'content': prompt}],
    'temperature': 0.7,
    'max_tokens': 4000
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

# 微信推送 — 取前2000字符作为预览
preview = digest[:2000]
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
