---
name: project-free-claude-code
description: free-claude-code — Claude Code 免费方案
metadata: 
  node_type: memory
  type: project
  path: C:\free-claude-code
  modified: 2026-08-06T06:11:58.394Z
  originSessionId: 6dd31fbb-2c41-49f3-808f-f0380c8b1198
---

# Free Claude Code

**状态**: 待确认

## 已知

- 路径：`C:\free-claude-code\`
- 文件：`proxy.py`（Python 标准库，零依赖）
- 功能：Anthropic API → NVIDIA NIM 转发，支持流式 SSE
- 监听：`127.0.0.1:8082`
- 5 个模型映射：kimi-k2 / minimax-m2.5 / nemotron-3 / qwen3.5 / glm-4.7
- 需要设置 `NVIDIA_NIM_API_KEY` 环境变量
- 未集成到 .cce configs.json

## 待办

- 补充详细信息
