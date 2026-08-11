# -*- coding: utf-8 -*-
"""AI日报 v2.5 — DeepSeek分析 + 微信推送 + 跨仓库git log + 螺丝消除"""
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
screw_http = os.environ.get('SCREW_HTTP', '?')
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
prompt_parts.append("请根据下方的新闻、git提交记录和昨日日报，生成今天的AI日报。")
prompt_parts.append("")

# ═══ 格式要求 ═══
prompt_parts.append("=" * 40)
prompt_parts.append("输出格式（必须严格遵循，不要遗漏任何板块）")
prompt_parts.append("=" * 40)
prompt_parts.append("")

# 板块1：AI动态
prompt_parts.append("## 1. AI动态")
prompt_parts.append("")
prompt_parts.append("选出3-5条最重要的AI相关新闻。")
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
prompt_parts.append("")

# 板块2：项目健康
prompt_parts.append("## 2. 项目健康")
prompt_parts.append("")
prompt_parts.append("六个项目的HTTP状态 + 昨日实际变动。")
prompt_parts.append("")
prompt_parts.append("**「昨日动态」列必须逐条扫描下方 git log！禁止漏报！**")
prompt_parts.append("git log 格式: commit_hash 日期 消息。消息里包含项目名（动物大战/五子棋/象棋/你画我猜/螺丝消除/日报/记忆等）。")
prompt_parts.append("识别规则：看到「动物大战 v3.6」→ 动物大战写「v3.6 防御性错误处理」。看到「日报系统」→ 对应系统改动。")
prompt_parts.append("一个项目有多条 commit 就逐条列出，按时间正序排列（v3.4→v3.5→v4.0，禁止倒序！）。")
prompt_parts.append("每条改动独占一行，用 &lt;br&gt; 换行，不要堆在一起。")
prompt_parts.append("如果 git log 里确实没有某项目的提交，才写「无变动」。")
prompt_parts.append("不许写「代码提交记录中未出现」这种废话——直接列出版本号和改动内容。")
prompt_parts.append("")
prompt_parts.append("表格格式：")
prompt_parts.append("| 项目 | HTTP | 昨日动态 |")
prompt_parts.append("|------|------|----------|")
prompt_parts.append(desc(chess_http, '中国象棋', '双人象棋'))
prompt_parts.append(desc(gomoku_http, '五子棋', '联机五子棋'))
prompt_parts.append(desc(draw_http, '你画我猜', '你画我猜'))
prompt_parts.append(desc(animal_http, '动物大战', '动物自动对战'))
prompt_parts.append(desc(screw_http, '螺丝消除', '抖音解压小游戏'))
prompt_parts.append(desc(temple_http, '星月神殿', '已退役'))
prompt_parts.append("")
prompt_parts.append("星月神殿永远标注'已退役'。")
prompt_parts.append("")

# 板块3：昨日日志（事实记录）
prompt_parts.append("## 3. 昨日日志")
prompt_parts.append("")
prompt_parts.append("日志是**操作轨迹的事实记录**，不评价好坏。逐条扫描 git log，按时间顺序列出每个 commit：")
prompt_parts.append("")
prompt_parts.append("- **代码提交**：逐条列出（项目名 + 版本号 + 改动内容，从 commit message 提取）")
prompt_parts.append("- **操作原因**：根据 commit message 推断（修bug/新功能/重构/配置调整）")
prompt_parts.append("- **部署状态**：已推送")
prompt_parts.append("")
prompt_parts.append("如果有 commit 就如实列出，没 commit 写'昨日无代码提交'。")
prompt_parts.append("禁止写「代码提交记录中未出现与项目直接相关的功能性改动」——git log 里的每一条都是改动，如实列出。")
prompt_parts.append("")

# 板块4：今日小结（评价和建议）
prompt_parts.append("## 4. 今日小结")
prompt_parts.append("")
prompt_parts.append("小结是你的**评价和建议**，不是重复日志内容。这是日报最重要的板块，必须认真写，不能敷衍。")
prompt_parts.append("")
prompt_parts.append("**新闻评价**：今天哪条新闻最值得关注？有什么趋势或风险？")
prompt_parts.append("")
prompt_parts.append("**项目评价**：根据昨天的改动，做得好的地方提一下，有隐患的指出来，可以改进的建议说一下。")
prompt_parts.append("")

# ═══ 原始数据 ═══
prompt_parts.append("=" * 40)
prompt_parts.append("原始数据")
prompt_parts.append("=" * 40)
prompt_parts.append("")

prompt_parts.append("--- 今日新闻 ---")
prompt_parts.append(news_raw if news_raw.strip() else "（今日暂无AI相关新闻）")
prompt_parts.append("")

prompt_parts.append("--- git log（昨天所有代码改动，逐条读！每条都要反映到「昨日动态」和「昨日日志」里） ---")
prompt_parts.append(GIT_LOG if GIT_LOG.strip() else "（无 git 记录）")
prompt_parts.append("")

if YESTERDAY_REPORT.strip():
    prompt_parts.append("--- 昨日AI日报（辅助参考） ---")
    prompt_parts.append(YESTERDAY_REPORT[:2000])
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
preview = digest[:5000]  # 确保小结能完整推送
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
