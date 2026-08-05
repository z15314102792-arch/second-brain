---
name: session-resume-workflow
description: 会话恢复的标准流程：关前存档、开后 claude continue
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-05T05:57:06.986Z
  originSessionId: c000a00f-a6cc-4681-89f9-a1c39a80f8df
---

## 核心认知

- **Claude Code 会话绑定终端进程**，VS Code 关闭 → 终端死 → 会话永久消失
- **`claude --resume <id>` 只能恢复还在运行的会话**，复活不了已死的
- **正确的恢复方式是 `claude continue`**（新会话读取 memory 文件接上进度）

## 标准流程

### 关闭前
对 Claude 说：**"保存进度"**
→ Claude 把当前任务/待办写入 memory 目录

### 打开后
在项目目录终端输入：**`claude continue`**
→ 新会话自动加载 memory 文件，接上进度

## 已配置的自动化

- `C:\Users\Administrator\claude-code-records\settings.json`：SessionEnd hook（正常退出时自动标记）
- `C:\Users\Administrator\.claude\settings.json`：autoMemoryEnabled=true

## 注意事项

- SessionEnd hook 在 VS Code 强制关闭时可能不触发，不能完全依赖
- 手动说"保存进度"是最可靠的方式
- memory 文件持久化在硬盘，不受会话生命周期影响
