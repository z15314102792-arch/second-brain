---
name: project-second-brain
description: 第二大脑 — 记忆系统，Obsidian 可视化，Git 备份
metadata: 
  node_type: memory
  type: project
  path: C:\Users\Administrator\.claude\projects\C--\memory
  github: z15314102792-arch/second-brain
  modified: 2026-08-06T06:28:44.893Z
  originSessionId: 6dd31fbb-2c41-49f3-808f-f0380c8b1198
---

# 第二大脑（记忆系统）

**状态**: 已搭建，正常运行

## 架构

```
Claude Code 聊天 → /保存进度 → memory/*.md 文件 → Obsidian 可视化
                    ↓                              ↓
              SessionEnd hook 提醒            Git → GitHub 备份
```

## 核心文件

| 文件 | 用途 |
|------|------|
| `MEMORY.md` | 全局索引，会话启动时自动加载 |
| `session-{日期}-progress.md` | 每天会话进度流水账 |
| `project-*.md` | 各项目专属状态文件 |
| `find-lost-project.md` | 找回丢失项目的搜索路径 |
| `session-resume-workflow.md` | 会话恢复标准流程 |
| `research-before-implement.md` | 调研先行原则 |
| `chinese-chess-stable-baseline.md` | 象棋 v2.1 基线（部分过时） |
| `installed-tools.md` | 本机已安装工具清单 |

## 自动化

- 每完成一个任务 → 自动更新进度文件 + git commit + push
- SessionEnd hook → 退出时检查是否已存档
- Obsidian 可打开 `memory/` 目录可视化浏览

## Git

- 仓库：github.com/z15314102792-arch/second-brain（私有）
- 路径：`C:\Users\Administrator\.claude\projects\C--\memory`
