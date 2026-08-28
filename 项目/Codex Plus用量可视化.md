---
name: codex-plus-usage-visualization
description: Codex Plus 用量可视化工具选择与本机安装记录
tags: [项目, Codex, Plus, 用量]
metadata:
  type: project
  status: 稳定
  version: v0.1
  modified: 2026-08-28
---

# Codex Plus 用量可视化

## 当前结论

最终保留 `lorytek/PulseMeter` 作为 Codex Plus 用量可视化工具；放弃 `D1NOOO/codex-usage-monitor`。

选择原因：

- PulseMeter 功能更完整：可看 Codex 用量、剩余额度、重置时间、项目用量估算和使用速度预测。
- 用户明确要求保留原方案，优先使用 PulseMeter。
- `D1NOOO/codex-usage-monitor` 虽然中文友好，但功能更轻量，已按用户要求删除。

## 本机路径

- PulseMeter 程序：`C:\Users\Administrator\Documents\Codex\tools\PulseMeter\app\PulseMeter.exe`
- PulseMeter 桌面快捷方式：`C:\Users\Administrator\Desktop\PulseMeter.lnk`
- PulseMeter 设置目录：`C:\Users\Administrator\AppData\Local\PulseMeter`
- 已删除工具目录：`C:\Users\Administrator\Documents\Codex\tools\CodexRateMonitor`

## 安装与校验

- PulseMeter 版本：v0.6.3
- Release ZIP SHA256：`5ff3066d05e94846092eeb5111d23da5f8d8a8a77a4abdb95e295dcccf4d1d10`
- 校验结果：匹配
- 当前状态：PulseMeter 已启动运行

## 风险边界

- PulseMeter 是非官方社区工具，不是 OpenAI 官方产品。
- Windows 可能提示未签名程序风险；只从 GitHub Release 下载并校验 SHA256。
- PulseMeter 可能读取本机 Codex 数据用于用量和项目估算，包括 `.codex` 下的认证/状态/会话元数据。
- 不使用需要手动粘贴 Cookie、Token、账号密码的方案。

## 后续

- 如果英文界面影响使用，再重新寻找支持中文且功能接近 PulseMeter 的工具。
- 如果 PulseMeter 后续因 ChatGPT/Codex 更新失效，优先查看其 GitHub Release 是否有新版。
