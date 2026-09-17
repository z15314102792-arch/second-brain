---
name: claude-code-hook-restart-required
description: 历史 hook 热加载异常案例；当前先核实版本、信任与触发，不普遍要求重启
metadata:
  version: v1.0
  node_type: memory
  type: reference
  modified: 2026-09-17
  originSessionId: d4628283-c00a-44d4-84b8-e47c02346778
---

# Claude Code 历史 hook 热加载异常记录

## 2026-09-17 校正（当前适用）

本文保留历史现场；旧版本症状和当时推断不能直接当作当前全平台规则。当前维护入口为 [[项目/全局指令优化]]，执行与保存路径以当前 CLAUDE.md 为准。

- 文字规则和技能是软约束；程序只能约束实际覆盖、经过测试的条件。文件存在、配置可解析、已获信任、事件真实触发、原问题被检出是不同证据。
- “5—10轮必失效”“Hooks是唯一有效手段”“零延迟”“改钩子必重启”不能作为普适结论。版本、事件字段、信任状态、依赖、触发范围都要现场核查。
- 代码不调用模型不等于无耗时或完全无上下文成本；输出注入上下文仍可能消耗令牌。
- 调研与独立评审辅助判断，不能保证审美或因果正确；重复无新证据的微调应改为复现和对照验证。



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
