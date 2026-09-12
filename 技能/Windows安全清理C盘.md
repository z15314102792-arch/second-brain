---
name: windows-safe-c-drive-cleanup
description: Windows C 盘的保守型清理方法，只处理明确白名单中的可再生文件，并默认先预览。
tags: [Windows, 磁盘清理, PowerShell, 安全]
metadata:
  type: reference
  modified: 2026-09-12
  version: v1.2
---

# Windows 安全清理 C 盘

## 适用目标

在不影响软件登录、聊天记录、剪映草稿、项目文件、系统更新和软件修复能力的前提下，清理 C 盘中能够自动重新生成的临时文件与缓存。

## 本机脚本

- 脚本：`E:\第二大脑\scripts\Safe-CDriveCleanup.ps1`
- 桌面双击入口：`C:\Users\Administrator\Desktop\双击清理C盘.cmd`
- 桌面后台脚本：`C:\Users\Administrator\Desktop\Safe-CDriveCleanup.ps1`
- 默认行为：只扫描预览，不删除。
- 固定保留期：默认只处理 7 天以前的文件。
- 实际执行：必须显式传入 `-Execute`，且默认还要输入 `CLEAN`。

## 固定安全范围

- 用户临时文件、Windows 临时文件。
- 崩溃转储和 Windows 错误报告。
- DirectX 着色器缓存。
- Chrome、Edge 的 HTTP、代码、图形缓存；浏览器运行时跳过。
- 剪映、飞书、豆包、VS Code 的可再生网页或图形缓存；软件运行时跳过。
- 资源管理器缩略图缓存；资源管理器运行时跳过。

## 一次性旧副本

已迁移到 D 盘的 Ollama、ModelScope、npm、pip、pnpm 旧副本不属于周期清理。脚本只有在新路径设置正确，并且 D 盘存在同相对路径、同字节数文件时，才把对应 C 盘文件列为候选。

Downloads 旧目录、Hugging Face 的符号链接结构和 Whisper 旧缓存不自动纳入，必须单独复核。

## 永久禁区

- 不删除 `C:\Windows\Installer`、`WinSxS`、驱动仓库、事件日志、预取目录、系统还原点。
- 不清空整个 `SoftwareDistribution`，不停止 Windows Update 服务。
- 不使用 `DISM /ResetBase`。
- 不删除或移动整个 `AppData`。
- 不碰聊天数据库、浏览器登录数据、剪映草稿、Codex 数据和用户项目。
- 不自动清空 Downloads 与回收站。

## 调研结论

微软的“存储感知”支持定期处理临时文件，并对下载目录、回收站设置独立保留期。社区脚本可借鉴默认预览、明确执行开关、进程检测和白名单；不能照搬删除 Installer 包、重置更新缓存、删除预取或事件日志等激进功能。

## 2026-09-12 本机执行结果

- 清理前 C 盘剩余 29.334 GB，清理后剩余 48.810 GB，实际增加 19.477 GB。
- 成功删除 90733 个白名单文件；21 个被占用文件合计约 0.060 GB，二次重试仍占用，因此保留。
- Chrome、VS Code、资源管理器运行中，对应缓存被正确跳过，没有强制关闭软件。
- D 盘 Downloads、Ollama、Hugging Face、ModelScope、Whisper、npm、pip、pnpm 数据复检存在。
- 一次性已验证旧副本清理完毕，复检候选为 0 GB。
- 回收站约 1.383 GB，默认不清。
- 休眠文件约 6.29 GB，保留以免影响休眠和快速启动。

## 桌面使用方式

用户不需要为 `.ps1` 选择打开应用，也不需要记命令。直接双击桌面上的 `双击清理C盘.cmd`，入口会调用经过校验的后台脚本，执行固定白名单清理；正在运行的软件缓存仍会自动跳过。
