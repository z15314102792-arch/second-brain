---
name: installed-tools
description: 本机已安装的工具/软件清单，含安装命令，恢复时可一键重装
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-05T11:46:36.067Z
  originSessionId: c000a00f-a6cc-4681-89f9-a1c39a80f8df
---

# 已安装工具清单

## 远程访问

| 软件 | 版本 | 安装方式 | 安装命令 | 用途 |
|------|------|----------|----------|------|
| ZeroTier | 1.16.2 | MSI 安装包 | 下载 https://download.zerotier.com/dist/ZeroTier%20One.msi 双击安装 | PC-手机虚拟组网 |
| ZeroTier One (Android) | 1.16.0 | APK 直装 | APKPure 下载 `com.zerotier.one`，约 13MB | 手机端组网 |
| claude-code-remote | 0.1.9 | npm 全局 | `npm install -g claude-code-remote` | 手机远程终端 |
| cloudflared | - | 手动下载 | 浏览器下载 exe 放到 `C:\Users\Administrator\AppData\Roaming\npm\` | Cloudflare 隧道（国内被墙，暂不用） |

## Node.js 生态

| 软件 | 版本 | 安装方式 | 安装命令 | 用途 |
|------|------|----------|----------|------|
| Node.js | - | 安装包 | - | JavaScript 运行时 |
| npm | - | 随 Node.js | - | 包管理器 |
| Claude Code CLI | - | npm 全局 | `npm install -g @anthropic-ai/claude-code` | AI 编程助手 |

## 开发工具

| 软件 | 版本 | 安装方式 | 安装命令 | 用途 |
|------|------|----------|----------|------|
| Git | - | 安装包 | - | 版本控制 |
| Obsidian | - | 安装包 | - | 记忆库可视化 |

## 恢复说明

如果换电脑或重装系统，按以下顺序恢复：

```bash
# 1. 安装 Node.js（npm 自带）
# 浏览器打开 https://nodejs.org 下载 LTS 版本安装

# 2. 安装 Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 3. 安装 claude-code-remote
npm install -g claude-code-remote

# 4. 安装 ZeroTier
# 浏览器打开 https://www.zerotier.com/download 下载 Windows 版安装
# 加入网络: 154a350c866d74d3

# 5. 安装 Git
# 浏览器打开 https://git-scm.com/download/win 下载安装

# 6. 克隆记忆库
git clone https://github.com/z15314102792-arch/second-brain.git C:\Users\Administrator\.claude\projects\C--\memory
```
