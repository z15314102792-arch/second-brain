---
name: codex-desktop-model-switch-failure
description: Codex 桌面版新建工作任务时无法切换模型和推理强度的已核实故障记录。
tags: [Codex, 桌面版, 排障]
metadata:
  type: reference
  modified: 2026-09-24
---

# Codex 桌面版模型切换故障

## 2026-09-24 本机案例

用户观察：新建“工作”任务页默认显示 GPT-6 Astra、高推理强度；选择其他模型或强度后提示“无法更新模型设置”。任务开始后可以再切换。

核对结果：本机桌面应用版本为 26.915.3509.0。故障发生时 `C:\Users\Administrator\.codex\config.toml` 默认值为 `model = "gpt-6-astra"`、`model_reasoning_effort = "high"`。2026-09-24 10:55:58（北京时间）的桌面日志显示用户尝试切到 `gpt-6-sol`、`high`，`config/batchWrite` 返回 `-32603`：`failed to persist config.toml: failed to persist config at C:\Users\Administrator\.codex\config.toml`。2026-09-23 也有相同报错；应用同步插件配置时亦遇到相同的持久化错误。

根因：一个 2026-09-17 19:01 启动的 `@wonderwhy-er/desktop-commander` Node.js 子进程（当时 PID 10572，父进程由 2026-09-16 启动的独立 `npx ... desktop-commander remote` 服务派生）持续占用 `config.toml`。Windows Restart Manager 报告该进程正在使用文件；将相同内容的临时副本替换原文件时，Windows 返回 `PermissionError: [WinError 5] 拒绝访问`。应用自身配置接口在“值不变”时返回成功，实际改模型时失败，符合文件被占用导致无法替换的机制。未找到证据将占用归因于某个具体 Codex 会话。

修复与验收：在备份 `config.toml` 后，只结束这个旧 Node.js 子进程，没有结束 Codex 或移动 `.codex` 目录。Restart Manager 随后不再报告占用；应用自身接口实际切换到 Sol、再切回 Astra 均成功，配置恢复到备份的逐字节内容。用户随后在新建“工作”任务页成功切换模型及推理强度；桌面日志中两次 `config/batchWrite` 均无错误，最终配置为 `gpt-6-sol`、`xhigh`，与用户选择一致。用户已确认界面恢复。新启动的 Desktop Commander 子进程暂未再次占用该文件；若复发，应再次核对文件占用者。

官方依据：[ChatGPT Work 入门](https://developers.openai.com/codex/get-started-with-work)说明可以在开始任务前从模型选择器选择模型；[Codex 基本配置](https://developers.openai.com/codex/config-file/config-basic)说明个人默认设置保存在 `~/.codex/config.toml`。

本案例已修复并完成界面与日志验收。保留的配置备份位于 `C:\Users\Administrator\.codex\config.toml.bak-modelswitch-20260924`。
