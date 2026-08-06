---
name: CCE模型
description: CCE 模型 — 多模型配置（DeepSeek 等）
metadata: 
  node_type: memory
  type: project
  path: C:\Users\Administrator\.cce
  modified: 2026-08-06T06:12:00.498Z
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

## 待办

- 补充详细信息
