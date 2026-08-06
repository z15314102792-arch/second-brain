---
name: project-memory-system
description: 项目记忆系统 — 从单文件流水账重建为结构化多项目记忆体系
metadata: 
  node_type: memory
  type: project
  path: C:\Users\Administrator\.claude\projects\C--\memory
  modified: 2026-08-06T06:29:15.694Z
  originSessionId: 6dd31fbb-2c41-49f3-808f-f0380c8b1198
---

# 项目记忆系统重建

**日期**: 2026-08-06
**状态**: ✅ 完成

## 背景

早上发现多个终端 `claude continue` 后全部读到相同内容，无法区分各自进度。根因是 memory 只有一份全局文件，没有"项目身份"概念。

## 做了什么

从 121 个会话文件中提取全部项目信息，把原来的单文件流水账重建为结构化多项目记忆体系。

### 新建文件（10 个 project-*.md）

| 文件 | 项目 | 版本 | 状态 |
|------|------|------|------|
| `project-chinese-chess.md` | 中国象棋 | v3.11 | 稳定 |
| `project-gomoku.md` | 五子棋 | v1.2 | 正常 |
| `project-draw-and-guess.md` | 你画我猜 | v8.13/6.0 | 完备 |
| `project-star-moon-temple.md` | 星月神殿 | v2.3 | 关卡待修 |
| `project-second-brain.md` | 第二大脑 | - | 活跃 |
| `project-cc-web.md` | cc-web | - | 已废弃 |
| `project-cce.md` | CCE 配置 | - | 8模型 |
| `project-huppy.md` | Huppy | v1.1.3 | 放弃 |
| `project-agnes-proxy.md` | Agnes 代理 | - | 需手动启动 |
| `project-free-claude-code.md` | NVIDIA 代理 | - | 国内不可用 |

### 新建流程文件

- `find-lost-project.md` — 丢失项目时从 .jsonl 会话记录中找回的 5 步搜索路径

### 重构文件

- `MEMORY.md` — 三区结构（流程与参考 / 项目 / 存档）
- `session-resume-workflow.md` — 添加 find-lost-project 引用

### CLAUDE.md 变更

- 删除：`find-lost-project` 自动触发规则（使用频率太低，不应占全局上下文）
- 新增：自动存档判断项目逻辑（文件路径 → 对话关键词 → 纯分析讨论主题 → 询问用户）
- 修复三条：自测豁免 / 版本标示灵活化 / 存档判断盲区

## 关键决策

1. **不按目录隔离**：用户记不住项目路径，与使用习惯冲突
2. **不分级 CLAUDE.md**：没必要，项目身份只需 3 行
3. **不是说"继续象棋"然后我去搜**：用户不需要记路径，他只需要项目名的自然语言
4. **应急流程放 memory，行为准则放 CLAUDE.md**：全局指令筛选原则
5. **改 CLAUDE.md 前自查三问**：能落地吗 / 有更省的吗 / 有副作用吗

## 使用方式

用户打开终端直接打字，不需要记路径：

```
继续象棋    → 搜 project-chinese-chess.md → 恢复
画画        → 搜 project-draw-and-guess.md → 恢复
五子棋      → 搜 project-gomoku.md → 恢复
那个闯关游戏 → 搜 project-star-moon-temple.md → 恢复
```

自动存档时，我根据文件路径+对话关键词判断项目，更新对应的 project-*.md。
