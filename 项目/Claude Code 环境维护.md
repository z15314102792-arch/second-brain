---
name: claude-code-env-maintenance
description: Claude Code 环境维护——hook 修复 + API 成本优化 + 读链接/识图能力扩展（mcp-vision 识图 + 读链接 Skill）
metadata: 
  node_type: memory
  type: project
  status: 稳定
  version: v1.4
  modified: 2026-08-16T13:00:00.000Z
---

# Claude Code 环境维护

> 版本 v1.4 · 2026-08-16

## v1.1 — 修复中文乱码

### 问题根因（三重叠加）

1. **hook 命令语法错误**：6 处 hook 命令写成 `PYTHONUTF8=1 python xxx.py`（Linux bash 写法），Windows 上 Claude Code 用 PowerShell 执行，PowerShell 把 `PYTHONUTF8=1` 当命令名，报"无法识别"，报错信息是 GBK 编码 → 被按 UTF-8 解读 → 界面显示乱码。
2. **python 不在 PATH**：系统 `python` 命令是 0 字节商店占位别名（`C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python.exe`），实际不可用。真 Python 3.13.14 由 workbuddy 管理，在 `C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe`。
3. **Python 默认 GBK 编解码**：Windows 中文系统下 Python 的 stdin/stdout/stderr 默认用 GBK，与 Claude Code 的 UTF-8 不匹配，中文输出/输入都会乱码或解析失败。

### 修复内容

1. **5 个 hook 脚本** 在 import 后加 UTF-8 强制（stdin/stdout/stderr 全部 `reconfigure(encoding="utf-8")`）：
   - `C:\Users\Administrator\.claude\hooks\claude-focus\hooks\token-guard.py`
   - `C:\Users\Administrator\.claude\hooks\claude-focus\hooks\verification-gate.py`
   - `C:\Users\Administrator\.claude\hooks\research-gate-pretool.py`
   - `C:\Users\Administrator\.claude\hooks\research-gate.py`
   - `C:\Users\Administrator\.claude\hooks\research-tracker.py`
2. **配置** `C:\Users\Administrator\.claude\settings.json`：6 处 hook 命令的 `PYTHONUTF8=1 python` 前缀去掉，改用 workbuddy Python 绝对路径。

### 验证结果

- settings.json 解析合法，无 PYTHONUTF8 残留，6 处命令全部绝对路径
- 5 个脚本 `py_compile` 通过
- 用 subprocess 模拟 Claude Code（UTF-8 管道 + 中文输入）调用 research-gate：正确拦截（exit 2），中文输出完整无乱码（乱码替换符 0 个）

### 注意事项

- **别用 `python` 命令**：PATH 里没有可用 Python，只能走 workbuddy 绝对路径。
- workbuddy 若升级/切换 Python 版本，`settings.json` 里的路径要同步更新。
- PowerShell 写 JSON 文件给 Python 读时，避免 `Set-Content -Encoding UTF8`（会加 BOM，Python 的 json.load 会报错）；用 Python 自己读写最稳。

---

## v1.2 — API 成本优化调研（纯咨询，无改动）

用户咨询「API 用不起，中转可不可行」。结论：**中转不解决根本问题**——便宜中转=逆向/掺假（CISPA 实测 45.83% 端点掉包），官方直通（OpenRouter）=官方同价不省钱。

### 现状与算账

- 用户用 Claude Code 内接 `deepseek-v4-pro`（官方直连 `api.deepseek.com/anthropic`），20 天 250 元 ≈ 375 元/月。
- 真 Claude 比 deepseek 贵 10-20 倍；Claude Max $100/月（725 元）嫌贵。
- deepseek 8/17 涨价：V4-Pro 高峰输出 6→27 元（4.5 倍），闲时 13.5 元。

### 配置现状（已查 settings.json，未改）

- Pro 做重活（主对话/opus/sonnet 档）、Flash 做轻活（haiku/子agent/小模型）——降档已配好。
- 缓存官方自动生效，但 Claude Code 动态前缀导致命中率低。

### 待办（下次继续）

- [ ] 用户试一周 `/compact` + 开新对话，看账单是否下降
- [ ] 若仍贵，帮准备「主对话降 Flash」配置（`ANTHROPIC_MODEL`/`ANTHROPIC_DEFAULT_SONNET_MODEL` → flash）
- [ ] 可选：错峰时间表（闲时输出便宜一半）

### 软文避雷名单

非线智能API、星链4SAPI、灵眸AI（LMU-AI=lmuai 同名 + 返利链接）均为自推软文，已剔除。

---

## v1.3 — 修复 check_edit_spiral 误拦（调阈值到 8）

### 问题

token-guard.py 的 check_edit_spiral 按「同一文件 Edit 次数」计数（不区分成功/失败、不区分参数是否相同），默认 ≥3 次就拦截，把正常的多处编辑误判成「编辑死循环」；改 token-guard.py 本身时甚至把自己锁死（改到第 3 次就被拦）。

### 调研结论（loop-breaker 官方 README）

**遇到误报 → 调高 consecutive_threshold 或加 ignore_tools，不要用 off（禁用）。** 即「调阈值优先，别删除检查」。

> 另发现：Edit 失败（old_string 不匹配）返回 <tool_use_error>，不触发 PostToolUse / PostToolUseFailure（Issue #24908），故「挪到 PostToolUse 按失败计数」方案不可行。

### 修复

- 只改 settings.json 的 env，加 CLAUDE_FOCUS_EDIT_FAIL_LIMIT=8（同文件 Edit 到第 8 次才拦）。
- 未改 token-guard.py 代码；「完全相同重试」的精确防护（check_exact_retry）仍在。

### 验证

- settings.json JSON 合法（json.load 通过），CLAUDE_FOCUS_EDIT_FAIL_LIMIT = 8 已写入。

### 待办

- [ ] 需重启 Claude Code 才生效（settings.json env 改动不热加载）
- [ ] 若一个文件一次改超过 8 处仍被拦，可再调高或改用 ignore_tools 方案

---

## v1.4 — 加「读链接」+「识图」能力（2026-08-16）

用户想让 Claude Code（后端 DeepSeek 纯文本模型）获得两个新本领：①读链接（抖音/B站/小红书/网页 → 说出内容）；②识图（看图/截图/视频帧）。

### 识图（✅ 已完成验证）

- 装 `mcp-vision`（`pip install mcp-vision`），配智谱 GLM-4V-Flash（复用 CCE 已有 zhipu key）。
- 原理：眼睛（视觉模型）+ 大脑（DeepSeek）分离——图片先交给 GLM-4V 转文字，再喂 DeepSeek。DeepSeek 的 Anthropic 接口本身不支持图片。
- 验证：GLM-4V-Flash 测试 status 200，能描述图片内容。

### 读链接（✅ 已完成，需用户登录浏览器测真实视频）

- 封装成 Skill：`C:\Users\Administrator\.claude\skills\读链接\`（SKILL.md v1.1 + scripts/read_link.py），一句话触发「帮我看看这个链接」。
- 技术链：yt-dlp 探测/下载音频 → ffmpeg 切片 → 智谱 GLM-ASR 转写；网页走 httpx 抓正文；图片交给识图 MCP。
- 验证：网页抓取 OK、ASR 单段+60秒切片转写 OK、本地 loopback 端到端 OK。

### 关键决策：ASR 用智谱 GLM-ASR 纯 HTTP，弃本地 FunASR

本地 FunASR 连踩 3 坑后放弃（Hypothesis Reset）：
1. funasr import 段错误（torch 没装，funasr 把 torch 当可选依赖跳过了）
2. 装 torch 2.13 后 import 报 `c10.dll` 加载失败（WinError 1114）
3. onnxruntime 1.28 同样 DLL 加载失败——判断是 workbuddy 便携 Python 3.13 对原生 C++ 扩展的 DLL 加载有问题（VC++ 运行库其实都在 System32）

改用智谱 `glm-asr-2512`（`POST open.bigmodel.cn/api/paas/v4/audio/transcriptions`），复用 zhipu key，国内直连、纯 HTTP、无本地 C 库。单次 ≤30 秒，用 ffmpeg 切 25 秒段解决长音频。

### 平台限制（需用户知晓）

- B站/抖音/小红书有反爬，需浏览器登录后脚本读 cookie（`--cookies-from-browser chrome`，可用环境变量 `LINK_COOKIE_BROWSER` 切换）。实测 B 站无登录返回 HTTP 412。
- 智谱 GLM-ASR 免费额度待确认（用户付不了费，需关注计费）。

### 文件清单

- `C:\Users\Administrator\.claude\skills\读链接\SKILL.md`（v1.1）
- `C:\Users\Administrator\.claude\skills\读链接\scripts\read_link.py`
- mcp-vision 配置写入 `.claude.json`（`claude mcp add`）
- API key 运行时从 `.cce/configs.json` 读取，未硬编码

### 待办

- [ ] 用户在浏览器登录 B站/抖音后，测真实视频链接
- [ ] 确认智谱 GLM-ASR 免费额度
- [ ] （可选）read_link.py 的下载时长上限、并发切片优化
