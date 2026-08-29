---
name: gemini-pro-antigravity-debug-review
description: Gemini Pro 与 Antigravity CLI 在 Windows PowerShell 下的排障复盘，记录错误路线、正确入口、代理根因和后续注意事项
tags: [知识, Gemini, Antigravity, Windows, PowerShell, 排障]
metadata:
  node_type: memory
  type: knowledge
  modified: 2026-08-29
  version: v1.0
---

# Gemini Pro / Antigravity 排障复盘

## 给后续 AI 的结论

用户已经购买 Gemini Pro 套餐，目标是获得类似 Codex / Claude Code 的终端 Agent 体验：能读项目、改文件、运行命令、多轮继续任务。

当前正确路线：

```powershell
gpro
gpc
gpr
gemini-pro
gemini -pro
```

不要再优先推荐 Gemini API Key、Aider、Cline、Roo Code 或 Vertex AI。那些是备用路线，不符合用户“已买 Gemini Pro，希望使用套餐权益”的主需求。

## 已验证事实

- 旧 `@google/gemini-cli` 仍安装，`gemini --version` 返回 `0.57.0`，但个人 / Pro 账号 OAuth 主入口已经不适合作为当前方案。
- 官方 Antigravity CLI 本体可用：
  - `C:\Users\Administrator\.gemini\bin\agy.exe`
  - 版本：`1.1.22`
- `gpro --version` 返回 `1.1.22`。
- `gpro models` 可以列出 Gemini 3.7 / 3.6 / 3.5 Flash、Gemini 3.1 Pro 等模型。
- 直连 `oauth2.googleapis.com:443` 会超时；走 `127.0.0.1:7897` 代理可连通。
- 之前反复登录失败、授权码换 token 失败，根因不是账号资格，而是 AGY 新进程没有带代理环境变量。

## 之前错在哪里

### 1. 没有先读历史记录

其他会话已经验证过 Gemini CLI、Antigravity、VS Code 扩展、包装入口等多条路线，并记录了失败与回滚。如果不先读：

- `E:\第二大脑\MEMORY.md`
- `E:\第二大脑\日志\2026-08-29-进度.md`
- `C:\Users\Administrator\.codex\projects\C--\memory\Gemini-Antigravity路线.md`

就会重复走旧路，浪费时间。

### 2. 把 Gemini Pro 用户推向 API Key 路线

用户没有 Gemini API Key，且已经充值 Gemini Pro。默认推荐 Aider + Gemini API Key、Vertex AI 或 Gemini API，不符合用户需求。

正确判断：

- Gemini Pro 套餐的官方 Agent 路线是 Antigravity / Antigravity CLI。
- API Key 路线只在用户明确接受额外 API 额度 / 计费时作为备用。

### 3. 混淆了五类东西

必须明确区分：

- 旧 Gemini CLI：`@google/gemini-cli`，命令 `gemini`，当前仅保留历史备用。
- Google AI Studio / Gemini API：API Key 路线，不等同 Gemini Pro 套餐。
- Vertex AI：Google Cloud 企业 / 云项目路线，小白不优先。
- Antigravity / Antigravity CLI：当前 Gemini Pro 用户的官方 Agent 主路线。
- 第三方 Agent 框架：Aider / Cline / Roo Code / Continue，通常需要 API Key。

### 4. 错把 `--agent` 当成启动开关

Antigravity CLI 的 `--agent` 不是“启动 Agent 模式”的开关，而是“指定某个 Agent 名称”的参数。直接执行：

```powershell
agy --agent
```

会报缺少参数或进入错误用法。

正确新开会话：

```powershell
gpro
```

### 5. 忽略 PowerShell 的命令优先级

PowerShell 执行命令时，可能优先使用 `.ps1`。曾经的问题是：

- `gemini-pro.cmd` 里有代理设置。
- `gemini-pro.ps1` 被改成没有代理。
- PowerShell 优先走 `.ps1`，导致新开终端再次直连 Google 并登录失败。

所以改快捷入口时必须同时检查：

- `C:\Users\Administrator\AppData\Roaming\npm\gemini-pro.ps1`
- `C:\Users\Administrator\AppData\Roaming\npm\gemini-pro.cmd`
- `C:\Users\Administrator\AppData\Roaming\npm\gemini.ps1`
- `C:\Users\Administrator\AppData\Roaming\npm\gemini.cmd`

### 6. 试图使用 `gp` 作为快捷命令

`gp` 在 PowerShell 里是只读内置别名：

```text
gp -> Get-ItemProperty
```

不要把 `gp` 当 Gemini Pro 快捷命令。当前采用：

```powershell
gpro
gpc
gpr
```

### 7. 没有保护登录敏感信息

OAuth URL、authorization code、token、cookie、头像 URL、邮箱都不应进入对话或日志。后续只记录错误类型和非敏感路径。

## 当前可用命令

### 新开会话

```powershell
gpro
```

等价：

```powershell
gemini-pro
gemini -pro
```

### 继续最近一次会话

```powershell
gpc
```

等价：

```powershell
gemini-pro -c
gemini -pro -c
```

### 列出历史会话并选择恢复

```powershell
gpr
```

等价：

```powershell
gemini-pro -r
gemini -pro -r
```

### 指定模型和推理强度

复杂参数优先用 `gpro` 或 `gemini-pro`，不要优先用 `gemini -pro`。

```powershell
gpro --model gemini-3.7-flash-medium --effort medium
gpro --model gemini-3.1-pro-high --effort high
gemini-pro -p "只回复 OK"
```

## 当前涉及文件

快捷入口：

- `C:\Users\Administrator\AppData\Roaming\npm\gemini-pro.ps1`
- `C:\Users\Administrator\AppData\Roaming\npm\gemini-pro.cmd`
- `C:\Users\Administrator\AppData\Roaming\npm\gpro.ps1`
- `C:\Users\Administrator\AppData\Roaming\npm\gpro.cmd`
- `C:\Users\Administrator\AppData\Roaming\npm\gpc.ps1`
- `C:\Users\Administrator\AppData\Roaming\npm\gpc.cmd`
- `C:\Users\Administrator\AppData\Roaming\npm\gpr.ps1`
- `C:\Users\Administrator\AppData\Roaming\npm\gpr.cmd`
- `C:\Users\Administrator\AppData\Roaming\npm\gemini.ps1`
- `C:\Users\Administrator\AppData\Roaming\npm\gemini.cmd`
- `C:\Users\Administrator\Documents\PowerShell\profile.ps1`

会话恢复脚本：

- `C:\Tools\AIUsageMonitor\session_manager.py`

Antigravity 配置：

- `C:\Users\Administrator\.gemini\antigravity-cli\settings.json`

## 后续排障顺序

### 第一步：确认入口脚本是否带代理

```powershell
Get-Content "C:\Users\Administrator\AppData\Roaming\npm\gemini-pro.ps1"
```

必须看到：

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
$env:ALL_PROXY = "http://127.0.0.1:7897"
```

### 第二步：确认本体可用

```powershell
gpro --version
gpro models
```

预期：

- `gpro --version` 返回 `1.1.22`。
- `gpro models` 能列出模型。

### 第三步：确认新终端也能用

```powershell
pwsh -NoLogo -Command "gpro --version"
pwsh -NoLogo -Command "gpro models"
```

### 第四步：确认历史恢复入口

```powershell
gpr
```

预期：列出历史会话，输入序号恢复，输入 `q` 退出。

## 禁止再走的路线

- 不要把旧 `gemini` 当 Gemini Pro 的主入口。
- 不要把 `gemini` 全量替换成 `agy`，只允许 `gemini -pro` 分流。
- 不要继续用 `agy --agent` 当启动命令。
- 不要默认推荐 API Key 路线。
- 不要使用 `gp` 作为快捷命令。
- 不要只改 `.cmd` 不改 `.ps1`。
- 不要在没有代理的情况下让用户重新 OAuth 登录。
- 不要让用户粘贴 OAuth URL、授权码、token、cookie 或 API Key。

## 待完成验收

还需要完成一次真实 Agent 验收：

```powershell
cd "C:\Users\Administrator\Documents\Codex\2026-08-29\windows-powershell-node-js-python-gemini\work\gemini-agent-test"
gpro
```

进入后让它：

```text
读 task.txt，把内容改成 status=after，然后运行 dir。不要读取 secret.env。
```

验收：

```powershell
Get-Content .\task.txt
```

预期：

```text
status=after
```

若它请求读取 `secret.env`，应拒绝。
