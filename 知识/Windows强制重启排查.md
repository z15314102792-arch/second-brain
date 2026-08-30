---
name: windows-forced-restart-diagnosis
description: Windows 弹出一分钟后重启时，优先按 lsass.exe 崩溃与底层驱动冲突方向排查
tags: [Windows, 故障排查, 系统]
metadata:
  type: reference
  modified: 2026-08-30 15:10
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

同时发现机器安装过 360 安全卫士，存在多项 360 内核级驱动、文件系统筛选器和卸载残留，且早期排查时 Microsoft Defender 处于关闭状态。初期最可疑方向是 Windows 25H2 / Build 26200.9168 与 360 底层驱动兼容冲突。

用户已处理：

- 卸载 360 安全卫士。
- 卸载 360 看图。
- 开启 Windows 内存完整性。

2026-08-30 17:17 左右再次复发后，判断需要升级：

- 本次 360 内核驱动和文件系统筛选器已不再显示运行，但代码完整性日志仍显示 Chrome 尝试加载 360 残留 `safewrapper.dll`。
- 已将 `C:\Program Files (x86)\360` 改名隔离为 `C:\Program Files (x86)\360.disabled-20260830`。
- 新崩溃仍为 `lsass.exe` + `RPCRT4.dll` + `0xc0000005`，崩溃转储为 `C:\Windows\System32\config\systemprofile\AppData\Local\CrashDumps\lsass.exe.1360.protected.dmp`。
- 代码完整性日志在崩溃前 1 秒连续报告 `C:\Windows\System32\fcon.dll` 缺少逐页哈希；该文件本身为微软签名，版本来自 8 月 16 日安装的 9168 更新。
- DISM ScanHealth 显示组件存储未损坏，CBS 记录 `Total Detected Corruption: 0`。
- 本机系统为 Windows 11 Pro Build 26200.9168，2026-08-16 安装 KB5121003 / KB5123304 / KB5120708。微软官方 KB5121003 支持页提到该更新存在应用卡死、访问冲突和设备无预警重启的已知问题背景；本机未发现其点名的 `inpoutx64` 驱动，因此不能只按该单项处理。

当前优先级：

1. 直接原因：`lsass.exe` 崩溃导致 `wininit.exe` 强制重启。
2. 高疑方向：Build 26200.9168 / KB5121003 兼容问题，叠加代码完整性/内存完整性策略、360 残留和 `fcon.dll` 校验异常。
3. 待验证方向：显卡驱动偏旧导致黑屏/显示驱动重置，Nahimic 音效组件导致黑框一闪。

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

## 黑框一闪

类似终端的黑框一闪而过，常见原因是某个自启动项、计划任务、更新器或脚本短暂打开了 `cmd.exe`、`powershell.exe` 或 `conhost.exe`。排查时优先看：

- 当前用户和全局自启动：`HKCU:\Software\Microsoft\Windows\CurrentVersion\Run`、`HKLM:\Software\Microsoft\Windows\CurrentVersion\Run`。
- 计划任务：重点看最近运行时间、每小时触发、登录后触发、动作里含 `cmd.exe`、`powershell.exe`、`updater.exe`、`.cmd` 的任务。
- 预读取记录：`C:\Windows\Prefetch` 中最近的 `CMD.EXE`、`CONHOST.EXE`、`POWERSHELL.EXE`、`WINDOWSTERMINAL.EXE`、`UPDATER.EXE`。
- 进程创建日志：需要开启命令行记录后，下次复现才能看到更清楚的来源。

本机 2026-08-30 排查发现：

- 360 安全卫士卸载后仍残留 360 画报自启动：`C:\Users\Administrator\AppData\Roaming\360huabao\360huabao.exe`，已删除注册表自启动项。
- 360 看图目录已不存在，但 360 安全卫士目录和多个 360 内核驱动仍有残留。
- 多个 360 驱动仍在运行：`360AntiAttack`、`360AntiHijack`、`360AntiSteal`、`360Camera`、`360FsFlt`。
- 文件系统筛选器仍挂着：`360AntiSteal`、`360Box64`、`360FsFlt`。
- 这些驱动可能需要重启后才完全卸载；重启后若仍存在，说明 360 没卸干净。
- 已开启计划任务详细日志：`Microsoft-Windows-TaskScheduler/Operational`。
- 已开启进程创建命令行记录：`ProcessCreationIncludeCmdLine_Enabled = 1`。
- 17:17 复查时已成功开启进程创建审计；测试确认 Security 4688 能记录新进程、父进程和完整命令行。
- `NahimicTask32` / `NahimicTask64` 在 2026-08-30 16:49:58-16:50:01 三秒内启动 42 个计划任务进程，强烈吻合“终端黑框一闪很多次”。已停止并禁用 `NahimicService`。
- WER 中有多条 `LiveKernelEvent 141`，属于显卡/显示驱动卡死恢复类问题；但部分 WATCHDOG 转储是旧文件，需结合后续新时间戳确认。

可能造成黑框一闪的任务包括 WPS 更新、Google 更新、Edge 更新、Windows 热补丁监控、抖音守护、OneDrive 更新。不能只凭任务存在就定罪，要等下次复现后按新日志确认。

若再次复发：

1. 先查 `Security` 日志 4688，按复发前 5 分钟提取新进程、父进程和命令行。
2. 再查 `Application` 中 `lsass.exe` 崩溃报告，确认是否仍为 `RPCRT4.dll` 偏移 `000000000001ebf2`。
3. 查看 `CodeIntegrity/Operational` 是否仍在崩溃前出现 `fcon.dll`、360、搜狗或其他第三方模块阻止加载。
4. 若仍是同一模式，优先分析最新 `lsass.exe.*.protected.dmp`，其次评估卸载/回滚 KB5121003 或就地修复安装。
