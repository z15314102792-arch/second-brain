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

核对结果：本机桌面应用版本为 26.915.3509.0。`C:\Users\Administrator\.codex\config.toml` 当前默认值是 `model = "gpt-6-astra"`、`model_reasoning_effort = "high"`。2026-09-24 10:55:58（北京时间）的桌面日志显示用户尝试切到 `gpt-6-sol`、`high`，`config/batchWrite` 返回 `-32603`：`failed to persist config.toml: failed to persist config at C:\Users\Administrator\.codex\config.toml`。2026-09-23 也有相同报错；应用同步插件配置时亦遇到相同的持久化错误。

因此，已证实的直接故障是桌面应用无法保存全局配置。`config.toml` 可以解析、不是只读，CLI doctor 报告配置可加载。日志没有给出更底层的文件系统错误，尚不能确定是权限、文件占用、安全软件还是此版本写入逻辑问题。任务中切换可能只更新当前任务设置；这与新建页需要保存默认值的路径不同，属于基于日志的推断。

临时绕过：在已有任务中切换；若要改变以后新任务的初始默认值，可在备份后手动编辑 `config.toml` 顶层的 `model` 和 `model_reasoning_effort`，但这不能证明新建页按钮已经恢复。不要移动、重命名或重建整个 `.codex` 目录。

官方依据：[ChatGPT Work 入门](https://developers.openai.com/codex/get-started-with-work)说明可以在开始任务前从模型选择器选择模型；[Codex 基本配置](https://developers.openai.com/codex/config-file/config-basic)说明个人默认设置保存在 `~/.codex/config.toml`。

下一步若要修复按钮：在用户再次触发报错时抓取同一时间的桌面日志和 Windows 文件访问拒绝记录，确认持久化失败的底层原因，再决定是否修复 ACL、排除文件占用或向应用报告缺陷。尚未完成修复验收。
