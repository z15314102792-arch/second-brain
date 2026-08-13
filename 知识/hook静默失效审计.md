---
name: hook
description: 6个hook审计发现5个静默失效，失效原因分类+修复方案+治理原则
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-13T03:52:22.762Z
  originSessionId: f2741554-ffca-47e9-9a4d-84a925bc159a
---

# Hook 静默失效审计（2026-08-13）

## 核心发现

动态验证（喂官方文档确认的标准 payload）发现：**6 个 hook 里 5 个静默失效**，只有 token-guard 和 research-gate-pretool 有效。

关键认知：**hook 成功（exit 0）是静默的，transcript 里什么都不显示**，所以"我没看到报错"根本不能证明 hook 在工作。

## 失效原因分类（社区已归纳，本次全部命中）

1. **字段漂移**：读错 payload 字段名 —— `message`/`history` 实际不存在、`isError` 实际是 `is_error`（下划线）
2. **依赖缺失**：依赖的文件从未创建 —— echo-of-prompt 的 `task-context.md`
3. **路径不匹配**：文件名/路径对不上 —— session-end 找 `session-xxx-progress.md`，实际是 `存档/xxx-进度.md`

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

相关：[[知识/CLAUDE-md规则强制执行]]
