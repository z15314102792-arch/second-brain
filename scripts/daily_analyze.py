# -*- coding: utf-8 -*-
"""AI日报 — DeepSeek分析 + 微信推送"""
import urllib.request
import urllib.parse
import json
import os

DATE = os.environ.get('DATE', 'unknown')
DEEPSEEK_KEY = os.environ['DEEPSEEK_KEY']
SCT_KEY = os.environ['SCT_KEY']
YESTERDAY_REPORT = os.environ.get('YESTERDAY_REPORT', '')
GIT_LOG = os.environ.get('GIT_LOG', '')

# 读取新闻数据
news_raw = ''
try:
    with open('/tmp/news_raw.txt', 'r', encoding='utf-8') as f:
        news_raw = f.read()
except FileNotFoundError:
    pass

# 项目健康状态
chess_http = os.environ.get('CHESS_HTTP', '?')
gomoku_http = os.environ.get('GOMOKU_HTTP', '?')
draw_http = os.environ.get('DRAW_HTTP', '?')
animal_http = os.environ.get('ANIMAL_HTTP', '?')
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

# ══════════════════════════════════════════
# 构建提示词
# ══════════════════════════════════════════
prompt_parts = []

# 角色设定
prompt_parts.append("你是我的私人AI管家。我是一个喜欢做小游戏的个人开发者，业余项目部署在GitHub Pages上。")
prompt_parts.append("请生成今天的AI日报。必须严格遵循以下格式，不要遗漏任何板块。")
prompt_parts.append("")

# ═══ 格式要求 ═══
prompt_parts.append("=" * 40)
prompt_parts.append("输出格式（严格遵循）")
prompt_parts.append("=" * 40)
prompt_parts.append("")

# 板块1：AI动态
prompt_parts.append("## 1. AI动态")
prompt_parts.append("")
prompt_parts.append("选出3-5条最重要的AI相关新闻。格式要求：")
prompt_parts.append("")
prompt_parts.append("**每条新闻必须包含可点击的Markdown链接！** 标题和HN讨论都要用 [文字](URL) 格式。")
prompt_parts.append("示例格式：")
prompt_parts.append("### ★★★ [中文标题](原文URL)")
prompt_parts.append("[HN讨论](HN的URL)")
prompt_parts.append("")
prompt_parts.append("- **发生了什么**：2-3句话讲清楚核心内容")
prompt_parts.append("- **为什么重要**：对行业或开发者意味着什么")
prompt_parts.append("- **跟我有啥关系**：对我这个做小游戏的个人开发者有什么实际影响。无关就说'暂时关系不大'")
prompt_parts.append("")
prompt_parts.append("重要性标准：")
prompt_parts.append("- ★★★ 直接影响开发工具链、部署方式、或能省钱省时间 → 展开写")
prompt_parts.append("- ★★ 行业大趋势 → 中等篇幅")
prompt_parts.append("- ★ 知道就行 → 简短写")
prompt_parts.append("")

# 板块2：项目健康
prompt_parts.append("## 2. 项目健康")
prompt_parts.append("")
prompt_parts.append("用表格展示五个项目的运行状态，并补充昨日动态：")
prompt_parts.append("")
prompt_parts.append("| 项目 | HTTP | 昨日动态 |")
prompt_parts.append("|------|------|----------|")
prompt_parts.append(desc(chess_http, '中国象棋', '双人在线对战'))
prompt_parts.append(desc(gomoku_http, '五子棋', '联机对战'))
prompt_parts.append(desc(draw_http, '你画我猜', '多人你画我猜'))
prompt_parts.append(desc(animal_http, '动物大战', '动物自动对战'))
prompt_parts.append(desc(temple_http, '星月神殿', '已退役，404正常'))
prompt_parts.append("")
prompt_parts.append("「昨日动态」列请根据下方提供的昨日AI日报内容，总结每个项目昨天做了什么改动或保持稳定。"
                     "如果昨日日报没提到某个项目，写'无变动'。")
prompt_parts.append("星月神殿已退役，永远标注'已退役'，不要建议修复。")
prompt_parts.append("")

# 板块3：昨日日志
prompt_parts.append("## 3. 昨日日志")
prompt_parts.append("")
prompt_parts.append("根据下方提供的昨日AI日报，总结昨天的操作内容。格式：")
prompt_parts.append("")
prompt_parts.append("- **做了什么**：列出昨天进行的主要操作（项目改动、系统调整、Bug修复等）")
prompt_parts.append("- **为什么这么做**：解释每项操作的动机和背景")
prompt_parts.append("- **效果如何**：操作的结果（已部署？已修复？待验证？）")
prompt_parts.append("")
prompt_parts.append("如果没有昨日日报，写'昨日无记录'即可。")
prompt_parts.append("")

# 板块4：今日小结
prompt_parts.append("## 4. 今日小结")
prompt_parts.append("")
prompt_parts.append("分两部分：")
prompt_parts.append("")
prompt_parts.append("**新闻方面**：对今天推送的AI新闻提出你的看法和建议。哪条值得我花时间看？哪条可以直接忽略？有没有什么趋势值得警惕或把握？")
prompt_parts.append("")
prompt_parts.append("**项目方面**：对昨天的操作做简短评价。做得好的提一句，有隐患的指出来，可以改进的建议说一下。")
prompt_parts.append("")

# ═══ 原始数据 ═══
prompt_parts.append("=" * 40)
prompt_parts.append("原始数据")
prompt_parts.append("=" * 40)
prompt_parts.append("")

prompt_parts.append("--- 今日新闻 ---")
prompt_parts.append(news_raw if news_raw.strip() else "（今日暂无AI相关新闻）")
prompt_parts.append("")

if YESTERDAY_REPORT.strip():
    prompt_parts.append("--- 昨日AI日报（供参考） ---")
    # 只取前3000字符，避免token浪费
    prompt_parts.append(YESTERDAY_REPORT[:3000])
else:
    prompt_parts.append("--- 昨日AI日报 ---")
    prompt_parts.append("（无昨日记录）")

prompt = "\n".join(prompt_parts)

# ══════════════════════════════════════════
# 调用 DeepSeek
# ══════════════════════════════════════════
body = json.dumps({
    'model': 'deepseek-chat',
    'messages': [{'role': 'user', 'content': prompt}],
    'temperature': 0.7,
    'max_tokens': 6000
}, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request(
    'https://api.deepseek.com/v1/chat/completions',
    data=body,
    headers={
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {DEEPSEEK_KEY}'
    }
)
resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
digest = resp['choices'][0]['message']['content']
tokens = resp['usage']['total_tokens']
print(f"DeepSeek: {tokens} tokens")

# 保存
with open('/tmp/digest.md', 'w', encoding='utf-8') as f:
    f.write(digest)

# ══════════════════════════════════════════
# 微信推送
# ══════════════════════════════════════════
# Server酱支持 [文字](URL) Markdown链接
preview = digest[:2500]  # 多取一些，保证日志和总结都能推送到
data = urllib.parse.urlencode({
    'title': f'AI日报 | {DATE}',
    'desp': preview
}).encode('utf-8')

r = urllib.request.urlopen(urllib.request.Request(
    f'https://sctapi.ftqq.com/{SCT_KEY}.send',
    data=data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
))
result = r.read().decode()
print(f"WeChat: {result[:100]}")
