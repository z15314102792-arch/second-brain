---
name: cc-web
description: cc-web — 废弃方案，Web 远程 Claude 原型
tags: [废弃方案]
metadata: 
  node_type: memory
  type: project
  path: C:\cc-web
  status: 废弃方案
  replaced_by: claude-code-remote + ZeroTier
  modified: 2026-08-07T03:38:58.430Z
  originSessionId: 6dd31fbb-2c41-49f3-808f-f0380c8b1198
---

# cc-web（废弃方案）

**状态**: ❌ 已废弃（server.log 显示不断重启，claude 命令找不到）
**替代方案**: claude-code-remote + ZeroTier 直连

## 做了什么

- 搭建了原型：`C:\cc-web\`（server.js + public/index.html）
- 架构：浏览器 ←WebSocket→ Node.js ←spawn→ claude
- 前端：移动端优先的聊天 UI，支持 Markdown 渲染、流式显示

## 放弃原因

- `--output-format stream-json` 只能在 `--print`（单次）模式下使用
- 每次请求都是新进程，无法保持会话上下文
- Huppy 和 claude-code-remote 更成熟

## 参考

- Huppy 调研也放弃了（依赖作者云服务器，有被墙/收费风险）
- 最终方案：claude-code-remote + ZeroTier
