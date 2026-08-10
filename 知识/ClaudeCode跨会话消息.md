---
name: claude-code-cross-session-messaging
description: Claude Code 跨会话消息传递功能——是什么、怎么用、我的环境能不能用
metadata: 
  node_type: memory
  tags: 
    - claude-code
    - 跨会话
  type: reference
  modified: 2026-08-10T12:01:06.891Z
  originSessionId: cff3a954-f401-4560-a650-cd5e2cbf9583
---

# Claude Code 跨会话消息传递

## 是什么

Claude Code **v2.1.224** 起新增的功能，让**多个终端窗口里的 Claude Code 会话可以直接互相发消息**。

比如窗口 A 在修 bug 改了个共享函数名，可以自动通知窗口 B「我刚改了这个，你那边可能受影响」——不用手动复制粘贴上下文。

## 原理

- **本机通信**：通过 Unix 域套接字（Unix domain sockets），消息只在电脑内部传递，不经过外网
- **跨机器通信**：通过 Anthropic 的 Remote Control 服务中转

## 两个核心工具

| 工具 | 作用 |
|------|------|
| `ListAgents` | 发现当前可通信的会话（本地、子 Agent、远程） |
| `SendMessage` | 给指定会话发文本消息 |

用户可用 `/list-agents`（或 `/peers`）查看会话列表，用 `/rename` 给会话起名。

## 支持平台

- ✅ macOS
- ✅ Linux
- ✅ WSL 2（Windows 上的 Linux 子系统）
- ❌ Windows 原生（含 Git Bash/MSYS2）
- ❌ AWS Bedrock、Google Cloud Agent Platform 等非 Anthropic 平台

## 我的环境（2026-08-10）

- Claude Code **v2.1.226**（版本够新 ✅）
- Windows 10 原生 + Git Bash（**不支持** ❌，缺 Unix 域套接字）
- API 走 DeepSeek 代理（跨机器消息不可用 ⚠️）

**结论：当前环境用不了。** 要启用需要：①装 WSL 2 → ②在 WSL 2 里装 Claude Code → ③切回 Anthropic 官方 API（跨机器部分）。

## 安全性

- 消息**不能**批准权限、改配置、执行命令
- 收到 `/compact` 等命令也只是纯文本，不会被执行
- 任何需要权限的操作仍然会弹审批框
- 组织可通过 `crossSessionInbound: "refuse"` 全局禁用

## 相关链接

- [[知识/GitHub国内访问]] — 另一项基础设施踩坑记录
- [[工具/CCE模型]] — 当前 API 配置（DeepSeek 代理）

> 调研日期：2026-08-10，基于 WebSearch 搜索结果和本地环境实测。
