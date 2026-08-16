---
name: CCE模型
description: CCE 模型 — 多模型配置（DeepSeek 等）
metadata: 
  node_type: memory
  type: project
  path: C:\Users\Administrator\.cce
  modified: 2026-08-13T10:20:04.391Z
  originSessionId: 6dd31fbb-2c41-49f3-808f-f0380c8b1198
---

# CCE 模型配置

**状态**: 多模型已配

## 已知

- 路径：`C:\Users\Administrator\.cce\`
- 文件：`configs.json`
- 8 个后端配置：deepseek、zhipu、qwen、qwen-free、gemini-free、nemotron、modelscope、agnes
- 默认使用 deepseek（`deepseek-v4-pro` + `deepseek-v4-flash`）
- Claude Code 通过 `.cce` 实现多引擎切换

## 当前配置

- API Base URL: `https://api.deepseek.com/anthropic`
- 主模型: `deepseek-v4-pro`
- 辅助模型: `deepseek-v4-flash`

## 调研模型分档（2026-08-13 决策）

- **大范围/深度调研** → 派子 Agent 时传 `model: "haiku"` → 落到 `deepseek-v4-flash`（便宜档、国内直连）
- **简单查事** → 自己直接 WebSearch，用主模型 `deepseek-v4-pro`（很短，省不了几个 token，不用切）
- 落地位置：全局 `CLAUDE.md`「## 调研」部分（版本 v1.1）
- 理由：调研本质是「搜索 + 归纳」，flash 够用；只有深度方案选型 / 复杂根因分析才需要 pro

## 模型分流 + 串行配置（2026-08-13）

用户 DeepSeek API 20 天花 200+，排查根因后，在 `~/.claude/settings.json` 的 env 块加了 5 个变量：

| 变量 | 值 | 作用 |
|------|-----|------|
| `CLAUDE_CODE_SUBAGENT_MODEL` | `deepseek-v4-flash` | 子 Agent 用便宜 Flash（之前缺失，子 Agent 跑 Pro） |
| `ANTHROPIC_SMALL_FAST_MODEL` | `deepseek-v4-flash` | 后台轻任务用 Flash |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | `1` | 强制串行，防并行 ×3 |
| `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` | `50` | 单会话子 Agent 总数上限 |
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` | `1` | 禁止子 Agent 嵌套 |

**烧钱根因（非显而易见，值得记）**：V4-Pro 贵 + 官方 8 月涨价 + 峰谷定价翻倍 + agent 输入膨胀（87% token 在「找代码」）+ 缺 SUBAGENT_MODEL 致子 Agent 跑 Pro。

⚠️ 需重启 Claude Code 才生效（file watcher bug，见 [[知识/ClaudeCode改hook需重启]]）。

## 待办

- [ ] 用户重启后验证子 Agent 实际跑 deepseek-v4-flash（看 subagent 日志 message.model，不能只看配置）
- [ ] 教用户触发 video-use skill
- 补充详细信息
