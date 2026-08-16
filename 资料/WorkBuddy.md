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
  modified: 2026-08-12T10:18:06.714Z
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

- 2026-08-12 凌晨: winget 安装桌面端 v5.3.11 + npm 安装 CLI v2.134.0
- 2026-08-12 深夜: 白屏重装（原因是 HTTP 401 认证过期）。winget 卸载受权限限制失败 → 用自带卸载器 → 发现 3 个后台进程未退出 → taskkill 杀掉 → winget 覆盖安装成功。`.workbuddy` 用户数据目录完整保留。

### 重装避坑要点
- winget 管理员权限无法卸载用户域安装的包 → 用安装目录下的 `Uninstall WorkBuddy.exe`
- 卸载后 WorkBuddy 进程不会自动退出 → 需手动 `taskkill`
- `app.asar` 可能被系统锁 → 直接 winget 覆盖安装即可
