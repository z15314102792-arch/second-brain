---
name: workbuddy
description: 腾讯AI办公Agent，已安装CLI+桌面端，用于非编程任务
metadata: 
  node_type: memory
  tags: 
    - AI
    - Agent
    - 办公
    - 腾讯
  type: tool
  status: 运行中
  version: v5.3.11
  modified: 2026-08-12T03:21:40.103Z
  originSessionId: 97234303-2b96-4c4c-8a01-e4743f297fee
---

# WorkBuddy

> 腾讯出品的 AI 办公 Agent——「你说需求，它来干活」

## 已安装

| 组件 | 版本 | 路径 |
|------|------|------|
| 桌面端 | v5.3.11 | `C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe` |
| CLI | v2.134.0 | `codebuddy` 命令 |

## 核心能力

- 自然语言操作本地文件（生成 Excel/PPT/文档等）
- 多模型切换（国际版有 Claude + GPT-5 + Gemini）
- 批量处理文档、数据分析、行业调研
- 首次登录需国际网络，后续可直连

## 和 Claude Code 的分工

| 场景 | 用哪个 |
|------|--------|
| 写代码、改bug | Claude Code（我） |
| 做表格、写报告、做PPT | WorkBuddy |
| 搜笔记、知识库问答 | Obsidian Copilot RAG |
| 批量文件处理 | WorkBuddy |

## 费用

- 国际版 $10/月（约 ¥70）
- 免费版有基础额度，先试用再决定是否付费

## 安装记录

- 2026-08-12: 通过 winget 安装桌面端 v5.3.11 + npm 安装 CLI v2.134.0
