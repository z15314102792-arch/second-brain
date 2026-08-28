---
name: claude-code-env-maintenance
description: Claude Code/Codex 环境维护——hook 修复 + API 成本优化 + 读链接/识图能力扩展（mcp-vision 识图 + 读链接 Skill）+ 火山 Agent Plan 接入 + Codex 接入调研与导入检查
metadata: 
  node_type: memory
  type: project
  status: 稳定
  version: v2.4
  modified: 2026-08-28
---

# Claude Code 环境维护

> 版本 v2.4 · 2026-08-28

## v2.4 — 保存流程取消 G 盘 / hdd（2026-08-28）

用户明确取消保存时的 G 盘备份要求，原因是当前不需要，且每次检查/推送失败会浪费 token。

### 已改

- 删除 `E:\第二大脑` 仓库的 `hdd` remote，当前只保留 `origin`。
- `C:\Users\Administrator\.codex\commands\保存进度.md`：删除 G 盘备份步骤，保存只推 `origin master`。
- `C:\Users\Administrator\.claude\commands\保存进度.md`：明确不再检查/推送 `hdd`。
- `C:\Users\Administrator\.codex\AGENTS.md`：更新到 v2.4，明确不检查 G 盘 / `hdd`。
- `C:\Users\Administrator\.claude\AGENTS.md`、`C:\Users\Administrator\.claude\CLAUDE.md`：更新到 v2.3，明确不检查 G 盘 / `hdd`。
- `E:\第二大脑\CLAUDE.md`：更新到 v5.0，保存流程只保留 `git push origin master`。
- `E:\第二大脑\资料\WorkBuddy.md`：取消旧的 `push hdd master` 授权说明。

### 新规则

保存进度只执行：`git pull origin master` → 精确 `git add` → `git commit` → `git push origin master`。不再检查 G 盘路径，不再执行 `git push hdd master`。

## v2.3 — Codex AGENTS 新任务验证 + SessionEnd 路径修复（2026-08-28）

### 已验证

- 新建 Codex 验证任务：`01a046d7-312e-7962-904f-282f5afd44dd`。
- 只读检查 `C:\Users\Administrator\.codex\AGENTS.md`，结果通过：
  - 版本号为 v2.3 · 2026-08-28（Codex 导入后校正版）
  - 包含 `E:\第二大脑\MEMORY.md`
  - 包含 `E:\第二大脑\CLAUDE.md`
  - 包含 `C:\Users\Administrator\.codex\projects\C--\memory\`
  - 未发现 `E:\第二大脑\AGENTS.md`、`C:\Users\Administrator\.claude\projects\C--\memory\`、`.claude/verify.js` 残留

### 已修复

- `C:\Users\Administrator\.codex\hooks\session-end.js` 的第二大脑目录从 `E:\第二大脑\日记` 改为实际存在的 `E:\第二大脑\日志`。
- hook 注释版本从 v1.2 更新到 v1.3。
- 本地执行 `node C:\Users\Administrator\.codex\hooks\session-end.js`，退出码 0，无错误输出。

### 保留判断

- 不恢复 Claude 的 `PreToolUse`、`UserPromptSubmit`、`PostToolUse`、`Stop` 强拦截 hooks。原因：历史记录里 v1.8 已明确「Codex hooks 精简，只留 session-end.js」，且直接恢复可能导致 Codex 工具调用被旧 Claude 规则误拦。

## v2.2 — Codex 桌面版 Import 第二阶段检查（2026-08-28）

用户按「一库三用」迁移方案执行第二阶段，已到 Codex 桌面版 Settings → Import → Claude Code → 全选导入后的检查步骤。

### 已确认

- Codex 主配置存在：`C:\Users\Administrator\.codex\config.toml`，更新时间 2026-08-28 13:18:56。
- Codex 全局指令存在并已修正：`C:\Users\Administrator\.codex\AGENTS.md`，从旧 v2.1 更新为 v2.3。
- 技能已迁移：`C:\Users\Administrator\.claude\skills` 215 个文件；`C:\Users\Administrator\.codex\skills` 238 个文件（多出来的是 Codex 自带 `.system` 技能）。
- slash command 已迁移：`保存进度.md` 在 Claude/Codex 两边各 1 个。
- hooks 文件已迁移：Claude/Codex 两边均为 53 个文件。
- 插件缓存已迁移/安装：Claude 1456 个插件相关文件；Codex 1986 个插件相关文件。
- Claude 聊天导入记录存在：`C:\Users\Administrator\.codex\external_agent_session_imports.json` 共 132 条记录。

### 已修复

- `C:\Users\Administrator\.codex\AGENTS.md` 原来是 v2.1，落后于 `C:\Users\Administrator\.claude\AGENTS.md` / `CLAUDE.md` 的 v2.2。
- 新版 `AGENTS.md` 修正为 Codex 路径：
  - 第二大脑入口：`E:\第二大脑\MEMORY.md` + `E:\第二大脑\CLAUDE.md`
  - Codex 快捷记忆路径：`C:\Users\Administrator\.codex\projects\C--\memory\`
  - 验收脚本路径：`.codex/verify.js`

### 保留风险

- `C:\Users\Administrator\.codex\hooks.json` 当前只启用 `SessionEnd`，没有直接启用 Claude `settings.json` 里的 `PreToolUse`、`UserPromptSubmit`、`PostToolUse`、`Stop`。
- hooks 文件虽然都复制过来了，但 Claude hook 事件名和 Codex hook 兼容性不能假设完全一致。后续如要恢复强制调研/验收拦截，需要单独做 Codex hook 方案。

### 下一步

- [ ] 新开 Codex 任务验证全局 `AGENTS.md` v2.3 是否生效。
- [ ] 如用户要强制 hooks，再单独设计 Codex hook 兼容版本。

## v2.1 — Codex 接入调研：DeepSeek-V4-Flash 适配度（2026-08-20）

用户问"火山普通 API 接 Codex 能发挥多少效果、是不是满血"。重新调研，用数据说话，纠正之前"将近满血"的无据说法。

### 结论（数据化）

- **脑力接近满血**：DeepSeek-V4-Flash 正式版原生支持 Responses API，Terminal-Bench 2.1 得分 **82.7**，反超 V4-Pro 预览版（72.1），接近 GLM-5.2（81.0）和 Opus 4.8（85.0）。
- **但手脚四折**：
  1. 无视觉（纯文本，读不了图/截图，Codex 识图/Computer Use 用不了）
  2. 多 Agent 子代理任务被丢弃（已知未修复 bug，子代理只回 "Ready to help"，需本地代理改写 `agent_message`）
  3. 工具调用可能静默降级（协议不完整时退回"读整个文件→重写"低效模式，Token 翻倍、易覆盖他人代码）——这是"接上后感觉变笨"的根源，不是模型笨
  4. 复杂多步推理偏弱（官方自述，硬骨头不如 Pro）

### 端点纠正（重要，之前答错）

- 之前说"火山普通按量 `/api/v3` 直连 Codex 能用"是**错的**。
- **正解**：火山接 Codex = Coding Plan 端点 `/api/coding/v3`（原生支持 Responses），明确警告"不要误用按量端点"。
- 或走 DeepSeek 官方直连：`base_url = "https://api.deepseek.com/"`，`wire_api = "responses"`，官方明确"目前只有 Flash 支持接 Codex，Pro 暂不能直连"。

### 关键事实

- Codex 只认 OpenAI Responses API（`wire_api = "responses"`，chat 已废弃，2026-02 移除）；Claude Code 只认 Anthropic。协议分水岭是理解这一切的钥匙。
- 定价：Flash 输入 ¥1/M token、输出 ¥2/M token，约 Pro 的 1/10。

### 参考来源

- CC Switch v3.19.1 发布说明（火山 Coding Plan /api/coding/v3 原生 Responses）
- 阿里云开发者《给 Codex 和 Claude Code 接入 DeepSeek-V4-Flash》
- 腾讯云《Codex 接入 DeepSeek V4 后为什么感觉变笨了？原来是 Tools 能力失效了》

---

## v2.0 — 火山引擎 Agent Plan 接入（deepseek-v4-flash 正式版）（2026-08-20）

### 目标

把 Claude Code 后端从 DeepSeek 官方切换到火山方舟 Agent Plan 的 deepseek-v4-flash 正式版（GA），实测速率和效果。用户是小白，全程要能一键回滚。

### 最终配置（已实测通过，写在 switch-api.js v2.0）

- **Base URL（Anthropic 兼容）**：`https://ark.cn-beijing.volces.com/api/plan`
- **鉴权**：`ANTHROPIC_AUTH_TOKEN`（Agent Plan 专属 key，非普通 API key）
- **模型**：全部档位统一 `ark-code-latest`（内部路由到 `deepseek-v4-flash-ga-260731` 正式版）
- **切换脚本**：`C:\Users\Administrator\.claude\switch-api.js`（v2.0，命令：`node switch-api.js volcengine` / `restore` / `backup` / `status` / `list`）
- **一键回滚**：桌面「后悔药.lnk」→ `node switch-api.js restore`
- **备份目录**：`C:\Users\Administrator\.claude\api-backups\`

### 踩坑记录（按时间顺序）

1. **普通 API Key ≠ Agent Plan 专属 Key**：在方舟通用「API Key 管理」里创建的 key（`ark-100dde7d...`、`ark-d40cc10f...`）调 `/api/plan` 全部返回 401 `AuthenticationError`。Agent Plan 专属 key 必须去 Agent Plan 订阅管理页的「配置专属 API Key」步骤拿（`https://console.volcengine.com/ark/region:cn-beijing/subscription/agent-plan`）。
2. **Coding Plan ≠ Agent Plan，端点是 `/api/plan` 不是 `/api/coding`**：Coding Plan 走 `/api/coding`，Agent Plan 走 `/api/plan`。混用不消耗套餐额度。且两者都不能用通用 `/api/v3`（会额外按量计费）。
3. **模型 ID 不能直接填 `deepseek-v4-flash` 或 `deepseek-v4-flash-ga-260731`**：直接填会返回 500 `InternalServiceError`。必须填路由名 `ark-code-latest`，它自动路由到正式版 `deepseek-v4-flash-ga-260731`。
4. **`ANTHROPIC_API_KEY` 与 `ANTHROPIC_AUTH_TOKEN` 互斥**：切到火山（用 AUTH_TOKEN）时若不清掉旧 API_KEY，旧 key 会冲突导致"一换就坏"。已在 switch-api.js 加互斥清理逻辑（切谁就删谁）。
5. **火山官方明确警告**：使用 `/api/v3` 接入会产生额外费用且不消耗套餐额度，可能被判定违规。
6. **模型列表里同时有 `DeepSeek-V4-Flash正式版` 和 `DeepSeek-V4-flash`**：两个长得像、不是一回事，要勾「正式版」那个。

### 关键决策

- **用户否决沙盒测试方案**，选择正式使用亲自确认速率——所以必须先建自动备份+恢复机制（switch-api.js backup/restore + 桌面后悔药）兜底。
- **超额后付费不开**：燃料值 20,000/月，超额单价未公开查到，为避免扣完自动扣余额，建议扣完等刷新或手动续订。
- **Harness 全部跳过**：专业数据集/豆包搜索/Agent记忆/AI Native底座等全部不开启，每一个都是燃料值黑洞，Claude Code 用不上。

### 待办

- [ ] 用户执行切换命令并完全重启，`/status` 确认 Base URL 指向 `/api/plan`
- [ ] 实测速率后决定保留或切回 DeepSeek
- [ ] 火山专属 key 更新到 `E:\第二大脑\系统\API密钥.md`（本地，gitignore）

---

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

- [x] 用户在浏览器登录 B站/抖音后，测真实视频链接（已免登录解决，无需此待办）
- [x] 确认智谱 GLM-ASR 免费额度（已弃用，改本地 FunASR，免费无限量）
- [x] （可选）read_link.py 的下载时长上限、并发切片优化（已用 60s 切片方案）

---

## v1.5 — 读链接全打通：本地 FunASR + 抖音免登录（2026-08-16）

### 推翻 v1.4 的两个判断

1. **FunASR 失败根因不是 Python 3.13**：真实根因是缺 VC++ 运行库 `vcruntime140_2.dll`（VC++ 2019+ 的 DLL，torch 的 c10.dll 依赖它）。用 winget 装 `Microsoft.VCRedist.2015+.x64`（v14.51.36247.0）后，torch 2.13.0+cpu 和 funasr 1.4.2 直接 import 成功。之前"workbuddy 便携 Python 3.13 对原生 C++ 扩展 DLL 加载有问题"的判断是错的。
2. **改用标准 Python 3.11**（`C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe`，winget 装）作为 Skill 运行环境，比 workbuddy 便携 3.13 更稳。

### 本地 FunASR 免费转写（弃智谱 GLM-ASR）

- Python 3.11 上 `pip install torch torchaudio funasr`（清华源），模型用 SenseVoiceSmall（iic/SenseVoiceSmall，约 936MB，首次从 ModelScope 下载）。
- 验证：转写「今天天气很好，我们一起去公园玩」完全正确，rtf 0.14（比实时快 7 倍），清理掉 SenseVoice 的 `<|zh|>` 等标记 token。
- read_link.py 的 transcribe() 改用本地 FunASR，删掉智谱 GLM-ASR、load_zhipu_key、ffmpeg 切片逻辑。**免费无限量**，不再依赖智谱 ASR 计费。

### 抖音免登录下载突破（关键，借鉴开源踩坑）

之前卡在「Fresh cookies needed」签名墙。按用户要求"借鉴别人的路径"，SSH clone 开源项目看实现后打通：

- **方案来源**：`Evil0ctal/Douyin_TikTok_Download_API`（a_bogus 纯 Python 签名实现，用 gmssl 的 SM3 哈希）+ `jsnjzxy/abogus_cpp`（签名算法 JS 版参考）。GitHub HTTPS 被墙，走 `git@github.com:...`（SSH 443）。
- **免登录原理**：`aweme_id`（短链重定向正则提取）→ 游客 `ttwid`（POST `ttwid.bytedance.com/ttwid/union/register/` 自动获取）→ 构造 detail API 参数 + `msToken=''` 置空 + `a_bogus` 签名 → GET `aweme/v1/web/aweme/detail/` 拿视频直链（douyinvod CDN）。
- **验证**：用户实测链接 `v.douyin.com/xn8UvyQCqRE/` 端到端跑通——拿到标题「零基础搭AI知识库…」+ 作者「姜胡说」+ 直链，FunASR 转写全文。
- **关键文件**：`scripts/douyin_sign.py`（a_bogus 签名，复制自开源，保留 license 注释）+ read_link.py 加抖音免登录分支（`is_douyin`/`extract_aweme_id`/`get_ttwid`/`fetch_douyin`/`download_douyin_audio`）。

### 版本

- SKILL.md v1.3（抖音免登录 + 本地 FunASR）
- read_link.py 用 Python 3.11 运行（SKILL.md 调用命令已改路径）

### 待办

- [ ] B站/小红书仍可能需登录 cookie（B站无登录实测 HTTP 412）
- [ ] 抖音 a_bogus 签名算法可能随抖音更新失效，失效时需重新同步开源实现（Douyin_TikTok_Download_API 等）
- [ ] 抖音直链有效期约 1-2 小时，下载需及时

---

## v1.6 — 读链接扩展多平台：B站免登录攻克 + 长音频切片（2026-08-16）

### B站 412 风控绕过（关键突破）

- **问题**：B站视频页对免登录请求返回 412（「哔哩哔哩安全风控策略」），yt-dlp 和 httpx + buvid3/buvid4 都失败。
- **根因**：B站 2025-2026 风控升级，需要 WBI 签名 + 完整设备指纹（buvid3/4 + b_nut + bili_ticket）+ **TLS/JA3 指纹模拟**。yt-dlp 缺 TLS 指纹模拟，httpx 缺 WBI 签名和 TLS 指纹。
- **解法**：装 `bilibili-api-python`（Nemo2011 库，内置 WBI 签名缓存 + buvid 自动生成 + curl_cffi 的 impersonate 浏览器 TLS 指纹模拟），免登录拿标题 + 音频流。
- **验证**：B站视频「三星堆：是谁杀死了他们的神？」（438 秒）端到端跑通，转写全文。
- **追加坑（音频下载也要 curl_cffi）**：B站音频 CDN（mcdn.bilivideo.cn 等）同样检测 TLS 指纹，httpx 下载会报 SSL `UNEXPECTED_EOF_WHILE_READING`（不同视频走不同 CDN，严格程度不同）。`download_bilibili_audio` 已改用 curl_cffi 的 `impersonate("chrome110")` 下载，覆盖所有 CDN。

### 长音频切片（修复 OOM）

- **问题**：34 分钟长音频一次性转写报 `not enough memory: 19080449424 bytes`（≈19GB），SenseVoice 的 self-attention 对整个序列算爆内存。
- **根因**：FunASR 没有 VAD 模型时整个音频当一个 chunk 处理；`batch_size_s` 依赖 VAD 才分段，单独传不生效。
- **解法**：ffmpeg 把长音频（>60 秒）切成 60 秒小段，逐段转写再拼接。
- **验证**：438 秒视频切 8 段，转写成功无 OOM。

### 多平台覆盖现状

| 平台 | 方案 | 状态 |
|------|------|------|
| 抖音 | a_bogus 签名 + 游客 ttwid | ✅ 免登录已验证 |
| B站 | bilibili-api WBI 签名 + TLS 指纹 | ✅ 免登录已验证 |
| 网页 | httpx 抓正文 | ✅ 已验证 |
| 小红书/微博/YouTube | yt-dlp 通用路径 | 代码已覆盖，需真实链接实测 |

### 版本

- SKILL.md v1.4、read_link.py 加 B站分支（is_bilibili/fetch_bilibili/download_bilibili_audio）+ transcribe 切片
- 新增依赖：bilibili-api-python + curl_cffi（Python 3.11 环境）

---

## v1.7 — 沉淀「卡点止损判定」工作方法论（2026-08-16）

任务三（分析两种执行方式效率）的产出，已写入 Claude Code 记忆库（feedback 类型，自动加载）。

### 结论

- 用户让我分析「自己顺路径一路破解」vs「遇卡点就调研」哪个快、省 token。调研斯坦福/MIT、Lovable、Bito.ai、ISSTA 等硬数据：**试错循环占 token 约 60%，带调试循环比一次生成贵 5.6 倍，预先检索便宜 6 倍、快 3 倍**——「遇卡点就调研」全面占优。
- 但用户追出关键问题：「遇卡点就调研」若无**判定标准**（怎么知道该停手了）就是空话。深入调研 AI 领域（自适应 RAG、信息增益、重复熔断器）得出 4 条客观判定标准。

### 沉淀的 4 条止损判定（详见记忆库 stuck-stop-loss）

1. 信息增益递减 → 停
2. 本质重复熔断（连续 3 次只改表面参数）→ 强制停
3. 原因不收敛 → 停
4. 不迷信「我觉得」（AI 过度自信，只信客观信号）

核心：判定不靠主观感觉（AI 和试错的人都会过度自信），靠信息增益等客观信号。

### 版本

- 记忆库新增 `stuck-stop-loss.md`（feedback）+ MEMORY.md 索引 +1 行

---

## v1.9 — 记忆持续化方案：全局 CLAUDE.md 启动必读 + 跨项目记忆拷贝（2026-08-18）

### 问题
Session 中断续接时发现记忆丢失。用户认为「换 API 导致失忆」，追查后确认：
- **根因不是换 API**，是**启动目录变了**：`C:\Users\Administrator\` → `C:\`
- Claude Code 按启动目录定项目身份（`C--Users-Administrator` → `C--`），记忆是 per-project 的
- 旧项目 `memory/` 有 5 个文件，新项目 `memory/` 空的

### 方案
- **方案 A**：旧项目记忆复制到当前项目 `C:\Users\Administrator\.claude\projects\C--\memory\`（5 个文件）
- **方案 B**：全局 CLAUDE.md 加「启动必读」章节 → v2.1，每次会话先读第二大脑，不再依赖项目级记忆目录
- 用户否决了额外钩子方案（已有 CLAUDE.md 指令，加钩子会每次消息都强制读，浪费）

### 涉及文件
- `C:\Users\Administrator\.claude\CLAUDE.md` → v2.1（新增「启动必读」小节）
- `C:\Users\Administrator\.claude\projects\C--\memory\` — 5 个记忆文件已就位

### 待办
- [ ] 后续新会话验证：CLAUDE.md 指令是否自动触发第二大脑读取

---

## v1.8 — Codex 迁移收尾 + 中转站套壳鉴定（2026-08-16）

### codex 命令 PowerShell 失败修复

- 根因：`codex.cmd` 中文提示 UTF-8 编码，cmd.exe 按 GBK 读乱码，脚本崩
- 修复：重写 `C:\Users\Administrator\AppData\Roaming\npm\codex.cmd`（纯 ASCII）+ 新建 `codex.ps1`；验证 `codex --version` → 0.148.0-alpha.9

### 中转站（tkapi.cc.cd）套壳实锤

- API 返回 `_sub2api_display_scaled: true`（Sub-API 套壳字段）
- 模型自曝「动态路由」、报不出型号只说「基于 GPT-5」
- 禁网逼供三问全「不知道」，自认「不足以证明 GPT-5.6 是公开发布的产品」
- 结论：非真 GPT-5.6，套壳站跑的知识截止较早的便宜模型

### Codex hooks 精简

- `.codex/hooks.json` 删 6 个 Claude 迁来旧 hook，只留 session-end.js
