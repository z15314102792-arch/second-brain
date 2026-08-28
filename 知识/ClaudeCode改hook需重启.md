---
name: claude-code-hook-restart-required
description: Claude Code file watcher bug——用 Edit 原子保存 settings.json 会破坏 watcher，改 hook 后必须重启才生效
metadata:
  node_type: memory
  type: reference
  modified: 2026-08-13T04:18:14.142Z
  originSessionId: d4628283-c00a-44d4-84b8-e47c02346778
---

# 改 hook 后必须重启 Claude Code 才生效

> 踩坑时间：2026-08-12 | 来源：修复 hooks（metacog/research-gate/token-guard 等）时发现

## 现象

用 Edit 工具修改 `settings.json` 里的 hook 配置后，新改动的 hook **静默不生效**——不报错、不提示，就是没反应。只有重启 Claude Code 后才真正生效。

## 根因

这是 Claude Code 的已知 bug（GitHub issue #57852）：**用 Edit 工具原子保存 settings.json 会破坏文件 watcher**。

Claude Code 靠文件 watcher 监听 settings.json 的变化来热加载 hook 配置。但 Edit 工具的保存方式是"原子写"（先写临时文件再 rename 覆盖），这一步会中断 watcher 的监听，导致后续改动不再被感知，直到进程重启。

## 规避方案

- **改完 hook 必须提醒用户重启 Claude Code**，否则改动不生效。
- 这个 bug 无法从代码侧修复，只能靠"重启提醒"规避。

## 影响复盘

2026-08-12 的 hook 修复工作（verification-gate 补 contract、token-guard 加只读逃生通道）改完后，**实际可能都还没生效**，需要重启后重测一次。

> ⚠️ 更正（2026-08-13）：其中「metacog 按 session_id 隔离」后来确认是无效工作——metacog 有更根本的 `isError` 字段错误（真实字段是 `is_error`），已被软删废弃，见 [[知识/hook静默失效审计]]。

## 相关

- [[知识/CLAUDE-md规则强制执行]] — hooks 是唯一有效强制手段的调研，本坑是 hooks 系统自身的一个 bug
- [[知识/hook静默失效审计]] — 6个hook审计5个失效，metacog 因 isError 字段错误被软删
