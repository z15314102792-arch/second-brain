---
name: Huppy
description: Huppy — 远程 AI 编程助手，已安装但放弃使用
tags: [已放弃]
metadata: 
  node_type: memory
  type: project
  path: /tmp/huppy-app (C:\Users\Administrator\AppData\Local\Temp\huppy-app)
  version: 1.1.3
  status: 已放弃
  modified: 2026-08-07T03:39:00.835Z
  originSessionId: 6dd31fbb-2c41-49f3-808f-f0380c8b1198
---

# Huppy

**版本**: v1.1.3
**状态**: ⚠️ 已安装但未认证，已决定不使用

## 是什么

开源的远程 AI 编程助手控制平台。从手机/浏览器远程操控电脑上的 Claude Code，端到端加密。GitHub: slopus/happy（22,700+ stars）。

## 当前状态

- `huppy doctor` 诊断通过
- `@slopus/huppy-wire` stub 已修复（CJS + ESM）
- 未认证（需 `huppy auth login`）
- 未启动 daemon

## 放弃原因

1. 依赖作者云服务器中转（非本地直连）
2. 服务器在海外，可能被墙
3. 商业产品，随时可能收费或停运
4. Windows 兼容是长期负债（主要为 macOS 设计）

## 替代方案

claude-code-remote + ZeroTier — 纯本地直连，零外部依赖

## 注意

- 每次 `npm install` 后需重建 `@slopus/huppy-wire` stub
- postinstall 脚本只含 macOS 工具包，需 `--ignore-scripts`
