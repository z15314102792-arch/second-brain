# -*- coding: utf-8 -*-
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
    if code == '200':
        return f'{name} [正常] 网页可以打开，运行正常。{note}'
    elif code == '404':
        return f'{name} [404页面不存在] {note}'
    elif code == '000':
        return f'{name} [无法连接] 服务器可能挂了或网络不通'
    else:
        return f'{name} [HTTP {code}] 状态未知'

# 构建提示词 — 使用多行字符串避免引号嵌套问题
prompt_lines = []
prompt_lines.append("你是我的私人AI管家。我是一个喜欢做小游戏的个人开发者，有几个业余项目部署在GitHub Pages上。")
prompt_lines.append("请根据以下数据生成每日综合速报。")
prompt_lines.append("")
prompt_lines.append("== 格式要求 ==")
prompt_lines.append("")
prompt_lines.append("### 1. AI动态")
prompt_lines.append("从原始新闻中选出3-5条，按重要程度排序。每条必须包含：")
prompt_lines.append("")
prompt_lines.append("重要性: ★★★（必读）/ ★★（值得关注）/ ★（知道就行）")
prompt_lines.append("")
prompt_lines.append("标题（中文翻译，附链接）")
prompt_lines.append("")
prompt_lines.append("- 发生了什么: 用2-3句话讲清楚核心内容。不要只扔标题，要说清楚：谁发布了什么、有什么用、怎么做到的。")
prompt_lines.append("- 为什么重要: 对行业或开发者意味着什么。")
prompt_lines.append("- 跟我有啥关系: 对我这个做小游戏的个人开发者有什么实际影响。无关的就说'暂时关系不大'。")
prompt_lines.append("")
prompt_lines.append("重要性标准:")
prompt_lines.append("- ★★★ 直接影响你的开发工具链、部署方式、或能帮你省钱省时间")
prompt_lines.append("- ★★ 行业大趋势，可以关注")
prompt_lines.append("- ★ 知道就行，不需要行动")
prompt_lines.append("注意: ★的简短写，★★★的才展开写。不要每条一样长。")
prompt_lines.append("")
prompt_lines.append("### 2. 项目状态")
prompt_lines.append("四个项目的线上运行情况：")
prompt_lines.append("")
prompt_lines.append(desc(chess_http, '中国象棋', '双人在线对战游戏'))
prompt_lines.append(desc(gomoku_http, '五子棋', '联机五子棋对战'))
prompt_lines.append(desc(draw_http, '你画我猜', '多人你画我猜'))
prompt_lines.append(desc(temple_http, '星月神殿', '已退役不再维护，404是正常状态，不需要处理'))
prompt_lines.append("")
prompt_lines.append("重要提示: 星月神殿已经退役了！404是正常的，不要在报告中建议修复它。")
prompt_lines.append("")
prompt_lines.append("如果有非退役项目的异常（不是200），单独列出来说明可能的原因和修复方向。")
prompt_lines.append("")
prompt_lines.append("### 3. 今日小结")
prompt_lines.append("2-3句话总结今天最重要的信息和需要做的事。")
prompt_lines.append("")
prompt_lines.append("=== 原始新闻数据 ===")
prompt_lines.append(news_raw)

prompt = "\n".join(prompt_lines)

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

# 微信推送
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
