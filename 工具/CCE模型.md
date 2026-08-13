---
name: CCE模型
description: CCE 模型 — 多模型配置（DeepSeek 等）
metadata: 
  node_type: memory
  type: project
  path: C:\Users\Administrator\.cce
  modified: 2026-08-13T03:15:29.000Z
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

## 待办

- 补充详细信息
