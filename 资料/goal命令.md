---
name: goal
description: /goal — Claude Code 官方自主执行命令，条件驱动循环，无失败熔断器，必须写 bound 子句封顶
metadata:
  node_type: memory
  type: reference
  modified: 2026-08-13T03:14:27.222Z
  originSessionId: 3148f26d-3249-4f5e-9638-549b9116aa7c
---

# /goal — 自主执行命令

> 调研：2026-08-13 | 版本要求 v2.1.139+（本机 2.1.229 ✅）

**是什么**：官方内置命令，设一个「可衡量的完成条件」，Claude 跨多轮自主推进。每轮结束由一个独立小模型（Haiku）评估条件是否满足，不满足就继续下一轮，满足就自动清除。

## 正确用法（关键）

条件必须是**可衡量的终态**，且**必须写 bound 子句封顶**，否则会无限烧 token：

```
/goal 修复所有测试，直到 npm test 退出码为 0，或 20 轮后停止
/goal 完成迁移，直到所有调用点编译通过，或 1 小时后停止
```

- `/goal`（不带参数）→ 查看状态（轮数、耗时、token、评估器最近理由）
- `/goal clear`（别名 stop / off / reset / cancel）→ 提前清除

## ⚠️ 大坑：没有失败熔断器

- **没有「连续失败 N 次就停止」的参数**，官方唯一护栏就是 bound 子句。
- issue #58550：条件不可满足时，评估器会无限空转——实测 200+ 轮、5 小时、烧掉约 50% 周 token 预算。
- 通用保险丝 `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`（默认 8 次）**拦不住 /goal 评估器**（它不走普通 Stop hook 的计数路径）。

## 评估器的限制

评估器**只看对话记录，不跑命令、不读文件**——条件必须能用 Claude 自己的输出证明（比如测试结果出现在对话里），不能写「代码质量更好」这种主观条件。

## 与其他自主命令的区别

| 命令 | 触发方式 | 停止条件 |
|------|---------|---------|
| /goal | 条件驱动（上一轮结束就开始） | 条件满足 / 你 Esc 中断 |
| /loop | 定时（每隔 N 分钟） | 你手动停 / 7 天过期 |
| /background | 脱机后台 | 空闲 1 小时停 |
| /workflows | 多 Agent 并行编排 | 各自任务完成 |

## 本项目的死锁教训

2026-08-12 死锁根因：/goal 循环的 Stop 反馈不触发 UserPromptSubmit，token-guard 的 volume 计数永不重置 → 死锁。已通过 token-guard 只读逃生通道解决（见 [[知识/ClaudeCode改hook需重启]]）。

## 相关

- [[知识/ClaudeCode改hook需重启]] — hook 改动需重启才生效
- [[知识/CLAUDE-md规则强制执行]] — hooks 强制手段调研

## 参考来源

- 官方文档：[Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)（[中文](https://code.claude.com/docs/zh-CN/goal)）
- issue：[#58550 /goal evaluator has no circuit breaker](https://github.com/anthropics/claude-code/issues/58550)
- 社区熔断插件：[burnstop](https://github.com/phuryn/burnstop)、[claude-focus](https://github.com/assafkip/claude-focus)
