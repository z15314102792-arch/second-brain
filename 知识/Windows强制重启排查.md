---
name: windows-forced-restart-diagnosis
description: Windows 弹出一分钟后重启时，优先按 lsass.exe 崩溃与底层驱动冲突方向排查
tags: [Windows, 故障排查, 系统]
metadata:
  type: reference
  modified: 2026-08-30
---

# Windows 强制重启排查

## 结论

Windows 弹出“电脑出现了一些问题，将在一分钟后重启”时，不要先按普通 Windows 更新处理。优先查看系统日志里是否有 `lsass.exe`、`wininit.exe`、事件 ID `1074`、应用程序错误 ID `1000`。

如果日志显示 `lsass.exe` 意外终止，Windows 会为了保护登录和权限系统强制重启。这类问题常见方向是：

- Windows 核心组件异常。
- 安全软件、杀毒软件、登录保护、文件系统筛选器等底层驱动冲突。
- 系统更新后与旧驱动不兼容。
- 极少数情况下是恶意软件或系统文件损坏。

## 本机案例

2026-08-29 和 2026-08-30，本机两次强制重启的直接原因都是：

- 崩溃进程：`C:\WINDOWS\system32\lsass.exe`
- 故障模块：`C:\WINDOWS\SYSTEM32\RPCRT4.dll`
- 异常代码：`0xc0000005`
- 强制重启触发者：`wininit.exe`
- 重启说明：`lsass.exe` 意外终止，状态码 `-1073741819`

同时发现机器安装了 360 安全卫士，存在多项 360 内核级驱动和文件系统筛选器，且 Microsoft Defender 处于关闭状态。当前最可疑方向是 Windows 25H2 / Build 26200.9168 与 360 底层驱动兼容冲突。

用户已处理：

- 卸载 360 安全卫士。
- 卸载 360 看图。
- 开启 Windows 内存完整性。

## 排查顺序

1. 查系统日志：重点看 `System` 里的 `1074`、`6008`，以及 `Application` 里的 `1000`、`1001`。
2. 查可靠性记录：确认是否是同一个进程反复崩溃。
3. 查崩溃报告：`C:\ProgramData\Microsoft\Windows\WER\ReportArchive` 和 `ReportQueue`。
4. 查转储文件：`C:\Windows\System32\config\systemprofile\AppData\Local\CrashDumps`。
5. 查底层驱动：重点看杀毒、安全、VPN、网卡过滤、文件系统筛选器。
6. 查系统完整性：`DISM /Online /Cleanup-Image /CheckHealth` 和 `sfc /verifyonly`。
7. 若仍复发，用 WinDbg 打开 `.dmp` 文件看调用栈。

## 注意

`lsass.exe` 里没有第三方 DLL，不代表第三方软件无关。内核驱动和文件系统筛选器可能在更底层影响系统调用，通常不会直接出现在 `lsass.exe` 的已加载模块列表里。
