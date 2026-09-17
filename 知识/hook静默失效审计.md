---
name: hook
description: 历史 hook 失效案例；原计数自相矛盾，保留原因分类并以实际复测为准
metadata:
  version: v1.0
  node_type: memory
  type: reference
  modified: 2026-09-17
  originSessionId: f2741554-ffca-47e9-9a4d-84a925bc159a
---

# Hook 静默失效审计（2026-08-13）

## 2026-09-17 校正（当前适用）

本文保留历史现场；旧版本症状和当时推断不能直接当作当前全平台规则。当前维护入口为 [[项目/全局指令优化]]，执行与保存路径以当前 CLAUDE.md 为准。

- 文字规则和技能是软约束；程序只能约束实际覆盖、经过测试的条件。文件存在、配置可解析、已获信任、事件真实触发、原问题被检出是不同证据。
- “5—10轮必失效”“Hooks是唯一有效手段”“零延迟”“改钩子必重启”不能作为普适结论。版本、事件字段、信任状态、依赖、触发范围都要现场核查。
- 代码不调用模型不等于无耗时或完全无上下文成本；输出注入上下文仍可能消耗令牌。
- 调研与独立评审辅助判断，不能保证审美或因果正确；重复无新证据的微调应改为复现和对照验证。



## 核心发现

历史记录称“6个中5个失效”，同时又列出两个有效项，计数矛盾，不能作为已核实统计。以下失效分类保留作排查线索，当前以逐项真实测试为准。

关键认知：**hook 成功（exit 0）是静默的，transcript 里什么都不显示**，所以"我没看到报错"根本不能证明 hook 在工作。

## 失效原因分类（社区已归纳，本次全部命中）

1. **字段漂移**：读错 payload 字段名 —— `message`/`history` 实际不存在、`isError` 实际是 `is_error`（下划线）
2. **依赖缺失**：依赖的文件从未创建 —— echo-of-prompt 的 `task-context.md`
3. **路径不匹配**：文件名/路径对不上 —— session-end 找 `session-xxx-progress.md`，实际是 `日志/xxx-进度.md`

## 治理原则（调研社区得出，可复用）

- **抓真实 payload，别猜字段名**：文档和真实 schema 会漂移（`Task`→`Agent`、`tool_result`→`tool_response`）
- **硬规则 → hook + exit 2**；提醒类 → skill/CLAUDE.md（LLM 会静默无视注入指令）
- **证据审计**：数真实触发次数，0 次触发的删（可读 `~/.claude/projects/**/*.jsonl`）
- 现成工具：`cc-hook-test`、`tool-mock`（npm，mock payload 测试）、`hookprobe`（付费，扫 transcript 找 NEVER_FIRED）

## 处理结果

| Hook | 问题 | 处理 |
|------|------|------|
| research-gate.py | 读 `message`/`history` | 重写 v2（`last_assistant_message` + 状态文件） |
| metacog-lite.py | `isError` 驼峰 | 软删（.disabled） |
| echo-of-prompt.py | 依赖缺失 | 软删（.disabled） |
| session-end.js | 路径不匹配 | 修复路径 |
| verification-gate.py | 全局无 contracts | 保留（项目级有效） |

## 误报案例（v2 上线当天）

research-gate v2 重写后第一轮就误拦：汇报测试结果时写了「说"推荐"→ exit 2」，「推荐」二字被关键词匹配误判成"在给推荐方案"。用户决策：**保留硬拦截（选 B）**，不再修关键词。

> 关键词匹配判断语义，方向本身脆弱，会漏检也会误报。已修两轮关键词，用户拍板保留后停止投入。

相关：[[知识/CLAUDE-md规则强制执行]]
