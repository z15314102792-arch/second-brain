# -*- coding: utf-8 -*-
"""AI日报 v3.0 — DeepSeek分析 + 微信推送 + 昨日总结日志 + 新闻按发布时间过滤"""
import urllib.request
import urllib.parse
import json
import os

DATE = os.environ.get('DATE', 'unknown')
DEEPSEEK_KEY = os.environ['DEEPSEEK_KEY']
SCT_KEY = os.environ['SCT_KEY']
YESTERDAY_LOGS = os.environ.get('YESTERDAY_LOGS', '')
GIT_LOG = os.environ.get('GIT_LOG', '')

# 读取新闻数据（采集步骤已按发布时间过滤：只留 YESTERDAY 当天及之后发布）
news_raw = ''
try:
    with open('/tmp/news_raw.txt', 'r', encoding='utf-8') as f:
        news_raw = f.read()
except FileNotFoundError:
    pass

# 项目运行状态（HTTP 并入日志板块作补充素材，不再单独开板块）
chess_http = os.environ.get('CHESS_HTTP', '?')
gomoku_http = os.environ.get('GOMOKU_HTTP', '?')
draw_http = os.environ.get('DRAW_HTTP', '?')
animal_http = os.environ.get('ANIMAL_HTTP', '?')
screw_http = os.environ.get('SCREW_HTTP', '?')
temple_http = os.environ.get('TEMPLE_HTTP', '?')

def health_line(name, code):
    if code == '200':
        return f'{name}正常'
    elif code == '404':
        return f'{name}404页面缺失'
    elif code == '000':
        return f'{name}无法连接'
    else:
        return f'{name}HTTP{code}'

health_status = [health_line('中国象棋', chess_http), health_line('五子棋', gomoku_http),
                 health_line('你画我猜', draw_http), health_line('动物大战', animal_http),
                 health_line('螺丝消除', screw_http), health_line('星月神殿', temple_http)]
http_all_unknown = all(code == '?' for code in [chess_http, gomoku_http, draw_http, animal_http, screw_http, temple_http])

# ══════════════════════════════════════════
# 构建提示词
# ══════════════════════════════════════════
prompt_parts = []

prompt_parts.append("你是我的私人AI管家。我是一个喜欢做小游戏的个人开发者，业余项目部署在GitHub Pages上。")
prompt_parts.append("请根据下方的今日新闻、昨日总结日志和git提交记录，生成今天的AI日报。")
prompt_parts.append("")

# ═══ 格式要求 ═══
prompt_parts.append("=" * 40)
prompt_parts.append("输出格式（必须严格遵循，不要遗漏任何板块）")
prompt_parts.append("=" * 40)
prompt_parts.append("")

# 板块1：AI动态
prompt_parts.append("## 1. AI动态")
prompt_parts.append("")
prompt_parts.append("下面的新闻列表已经按发布时间过滤过，只保留昨天和今天发布的，没有更早的旧闻。从中选出3-5条最重要的。")
prompt_parts.append("每条必须用 [中文标题](原文URL) 可点击链接格式。")
prompt_parts.append("不要加HN讨论链接（HN在国内打不开，加了没用）。")
prompt_parts.append("")
prompt_parts.append("格式：")
prompt_parts.append("### ★★★ [中文标题](原文URL)")
prompt_parts.append("- **发生了什么**：2-3句话讲清核心")
prompt_parts.append("- **为什么重要**：行业意义")
prompt_parts.append("- **跟我有啥关系**：对个人开发者的影响")
prompt_parts.append("")
prompt_parts.append("重要性：★★★展开写 ★★中等 ★★简短")
prompt_parts.append("如果过滤后一条新闻都没有，就写「昨日无AI相关新闻」。")
prompt_parts.append("")

# 板块2：日志
prompt_parts.append("## 2. 日志")
prompt_parts.append("")
prompt_parts.append("这是日报的核心板块。基于下面的「昨日总结日志」详细回顾昨天发生的事，这是唯一事实来源，只能写里面有的，绝不能编造。")
prompt_parts.append("")
prompt_parts.append("按这个思路组织，但不要被格式限制死，可以有自己的发挥：")
prompt_parts.append("- **昨天做了什么**：按条列出主要事项，每条一个「- 」，泾渭分明、不要堆在一起")
prompt_parts.append("- **遇到的问题和卡点**：昨天卡在什么地方、遇到了什么障碍")
prompt_parts.append("- **怎么突破的**：卡点是怎么解决的，用了什么方法或思路")
prompt_parts.append("- **遗留待办**：昨天列出的还没做完的事，原样保留")
prompt_parts.append("- **可以改进的地方**：你基于日志给出的建议——哪些流程可以优化、哪些坑值得记住")
prompt_parts.append("")
if not http_all_unknown:
    prompt_parts.append("项目运行状态（HTTP）放在「昨天做了什么」里顺带提一句即可，不用单独开板块：")
    prompt_parts.append('、'.join(health_status))
    prompt_parts.append("")
prompt_parts.append("如果昨日没有任何日志，就写「昨日没有留下日志记录」。")
prompt_parts.append("")

# ═══ 原始数据 ═══
prompt_parts.append("=" * 40)
prompt_parts.append("原始数据")
prompt_parts.append("=" * 40)
prompt_parts.append("")

prompt_parts.append("--- 今日新闻（已按发布时间过滤） ---")
prompt_parts.append(news_raw if news_raw.strip() else "（今日暂无AI相关新闻）")
prompt_parts.append("")

prompt_parts.append("--- 昨日总结日志（日记进度+会话快照+待办，逐条读，这是日志板块的事实来源） ---")
prompt_parts.append(YESTERDAY_LOGS[:8000] if YESTERDAY_LOGS.strip() else "（昨日无日志记录）")
prompt_parts.append("")

prompt_parts.append("--- git log（昨天代码改动，日志的补充素材） ---")
prompt_parts.append(GIT_LOG if GIT_LOG.strip() else "（无 git 记录）")

prompt = "\n".join(prompt_parts)

# ══════════════════════════════════════════
# 调用 DeepSeek
# ══════════════════════════════════════════
body = json.dumps({
    'model': 'deepseek-chat',
    'messages': [{'role': 'user', 'content': prompt}],
    'temperature': 0.7,
    'max_tokens': 8000
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
preview = digest[:8000]  # 日志板块内容较长，放宽到8000字符（Server酱上限32KB）
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
