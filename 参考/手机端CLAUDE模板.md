---
name: 手机端CLAUDE模板
description: 手机端 Claude Code 精简版全局指令模板（供参考）
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-07T03:10:37.818Z
  originSessionId: 53099e30-6fac-4ddc-b8d1-0dd8bee1197a
---

# 手机端全局指令（精简版）

## 语言

- 永远使用中文回复。
- 代码标识符可用英文。

## 执行

- 简单任务直接做，复杂任务先给方案再动手。
- 不确定的事实先查证再说。

## 自测

- 代码修改后主动验证，不靠用户发现问题。

## 记忆

- 项目记忆文件在 `~/.claude/projects/C--/memory/` 下。
- 手机端只读记忆，不在手机上自动存档（存档由 PC 端完成）。
- 需要了解项目背景时，先读对应的 `项目/xxx.md`。

## 沟通

- 小白友好：新概念首次出现时解释。
- 有更好的方案时简短提一句。
