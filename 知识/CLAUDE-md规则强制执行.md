---
name: claude-md-rule-enforcement
description: CLAUDE.md 规则强制执行问题的社区方案调研，含 rulehook、claude-core-values、misfire 等方案对比
metadata: 
  node_type: memory
  tags: 
    - 规则强制执行
    - hooks
    - CLAUDE.md
    - 调研
  type: reference
  modified: 2026-08-12T12:26:11.265Z
  originSessionId: d4628283-c00a-44d4-84b8-e47c02346778
---

# CLAUDE.md 规则强制执行

> 调研时间：2026-08-12 | 问题：CLAUDE.md 文本规则是"建议"不是"约束"，会话 5-10 轮后失效

## 问题本质

1. **注意力衰减（Issue #80873）**：规则在前 5-10 轮被遵守，之后逐渐被忽略——即使规则仍在 system-reminder 中
2. **免责声明弱化（Issue #19252）**：CLAUDE.md 注入时被标记为"may or may not be relevant"，降低了规则约束力
3. **上下文竞争**：代码内容挤占规则注意力，Claude 优先关注"当前代码"而非"行为准则"
4. **没有强制执行机制**：文本规则本质上是 self-moderation，缺乏外部强制闭环

## 社区方案（6 种）

| 方案 | 类型 | 强制层 | Token 开销 | 成熟度 |
|---|---|---|---|---|
| rulehook | 开源模式 | L1 Skill + L2 Stop + L3 SessionStart | 零（Regex） | 高 |
| claude-core-values | 插件 | SessionStart + UserPromptSubmit | ~15/轮 | 高 |
| Stop Hook + Haiku | 模式 | 每轮响应后 LLM 审查 | 1 Haiku 调用/轮 | 中 |
| Rippletide Code | 商业 beta | PreToolUse 执行前拦截 | 零（外部图） | Beta |
| claude-enforcer | 开源 Skill | 路由门控 + hooks | 不等 | 中 |
| misfire | CLI 工具 | 证据驱动的 hook 脚手架 | 零（确定性） | 中 |

## 核心洞察

**所有方案最终都收敛到同一个结论：Hooks 是社区唯一有效的强制手段。**

纯文本规则（CLAUDE.md / rules/）无法被依赖，必须用外部 hook 系统配合：
- **确定性检查**（Regex/静态分析）→ 零 token 开销、无延迟
- **LLM 审查**（Stop hook + Haiku）→ 灵活但增加延迟和成本
- **持久注入**（SessionStart/UserPromptSubmit）→ 绕过免责声明弱化

## 我们已有的基础设施

当前项目已部署的 hooks：
- PreToolUse: token-guard, echo-of-prompt, research-gate-pretool
- PostToolUse: research-tracker, metacog-lite, Write 提醒
- Stop: verification-gate, research-gate
- UserPromptSubmit: token-guard
- SessionEnd: session-end.js

**差距分析**：
- ✅ 调研门控（research-gate）已覆盖
- ✅ 错误检测（metacog Nociception）已覆盖
- ✅ 自检提醒（PostToolUse Write 提醒）已覆盖
- ❌ 规则持久注入：缺少 UserPromptSubmit 级别的核心规则提醒
- ❌ 规则违反检测：缺少对 CLAUDE.md 规则违规的 Stop 后审查
- ❌ 会话后审计：SessionEnd 只做清理，不做规则合规分析

## 建议的下一步

1. **短期（已实现）**：metacog + research-gate 的组合提供了基本的行为监控
2. **中期（推荐）**：在 UserPromptSubmit 注入简短的核心规则提醒（~50 tokens）
3. **长期**：参考 misfire 模式，基于实际违规数据决定哪些规则需要 hook 化
4. **不强求**：强制规则违反检测（Stop + Haiku 审查）受限于当前 API 环境（DeepSeek），暂不实施
