---
name: windows-forced-restart-diagnosis
description: Windows 弹出一分钟后重启时，优先按 lsass.exe 崩溃与底层驱动冲突方向排查
tags: [Windows, 故障排查, 系统]
metadata:
  type: reference
  modified: 2026-09-01 02:50
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

## 2026-08-31 复发补充

2026-08-31 16:10:39 左右再次非正常关闭，16:29:45 启动后系统日志记录 `6008`：上一次关闭是意外的。

关键证据：

- 16:27:53 应用程序错误：`lsass.exe` 崩溃，故障模块仍是 `C:\WINDOWS\SYSTEM32\RPCRT4.dll`，异常代码 `0xc0000005`，本次偏移变为 `00000000000d6362`。
- 16:28:10 Wininit `1015`：关键系统进程 `C:\WINDOWS\system32\lsass.exe` 失败，状态代码 `c0000005`，系统必须重启。
- 最新转储：`C:\Windows\System32\config\systemprofile\AppData\Local\CrashDumps\lsass.exe.1488.protected.dmp`。
- WER 报告路径：`C:\ProgramData\Microsoft\Windows\WER\ReportArchive\AppCrash_lsass.exe_5c93b6128aaae85d5535a4f68d3b4fbd8354f42a_9b3655d9_6c95c739-0125-4d05-a19f-fcf546716628`。
- 崩溃前 1 秒仍连续出现 `C:\Windows\System32\fcon.dll` 代码完整性 `3002`：缺少逐页映像哈希；但 `fcon.dll` 与 `RPCRT4.dll` 的 Authenticode 签名均为 Microsoft 且状态 `Valid`。
- `DISM /Online /Cleanup-Image /ScanHealth` 显示未检测到组件存储损坏；`sfc /verifyonly` 的 CBS 记录只显示 `[SR] Verify complete`，未发现明确不可修复项。
- 当前 Defender 已开启：实时保护、行为监控、IOAV 均为 `True`。
- 未找到 `inpoutx64.sys`；因此不要按 KB5121003 已知的单一 `inpoutx64` 路线处理。
- 当前仍存在 `360huabao.exe` 文件：`C:\Users\Administrator\AppData\Roaming\360huabao\360huabao.exe`，但当前 Run 注册表未再显示 360 画报自启动项。
- 当前仍有 Nahimic 内核驱动运行：`Nahimic_Mirroring.sys`、`NahimicBTLink.sys`；`NahimicService` 已禁用并停止。
- 代码完整性日志频繁阻止搜狗输入法组件加载：`SogouCloud.exe`、`PinyinUp.exe`、`SogouComMgr.exe`、`isgpet.exe` 未满足 Microsoft signing level requirements。

当前判断：

1. 直接原因仍是 `lsass.exe` 崩溃触发系统保护性重启，不是普通电源断电，也不是用户主动重启。
2. 最高疑方向仍是 Windows 11 Build 26200.9168 / 8 月更新与代码完整性、内存完整性、第三方输入法/旧安全软件残留/音效驱动之间的兼容冲突。
3. `fcon.dll` 与 `RPCRT4.dll` 本身签名有效，系统文件被明显篡改的可能性下降；更像更新版本与运行时策略/驱动交互问题。

黑框一闪新线索：

- Security 4688 已能记录进程创建；今天 16:23-16:27 大量黑框类进程来自 `cmd.exe` / `conhost.exe`。
- 一部分是当前 Codex/Gemini 工具链触发的命令窗口：父进程为 `pythonw.exe` 或 `codex.exe`，命令行为 `gemini-pro.cmd -p /usage`、`/model`、`/credits` 等。
- WPS 在 16:23:18、16:23:30、16:27:38 多次启动 `wpsupdate.exe`、`updateself.exe`、`ksolaunch.exe`、`wpscloudsvr.exe`，还调用 `regsvr32.exe` 注册 WPS 插件，是普通使用时黑框闪现的高疑来源之一。
- Windows 热补丁监控任务 `\Microsoft\Windows\Hotpatch\Monitoring` 会直接调用 `%systemroot%\system32\cmd.exe`，在 10:39:55 和 12:20:42 有记录，也是正常系统任务可能造成黑框闪现的来源。
- `WorkBuddy.exe` 在 16:27:19 调用了 `cmd.exe /d /s /c "ipconfig"`，也可能造成一次短暂黑框。

下次复发优先动作：

1. 先按复发时间前后 5 分钟查 Security 4688，找 `cmd.exe`、`conhost.exe` 的父进程和完整命令行。
2. 如果继续是 WPS 更新链路，优先禁用 `WpsUpdateTask_Administrator`、`WpsUpdateLogonTask_Administrator`、`WpsWakeWnsLogonTask` 验证。
3. 如果继续是 `lsass.exe + RPCRT4.dll + c0000005`，下一步应安装/调用 WinDbg 分析最新 `lsass.exe.1488.protected.dmp`，或优先做 Windows 更新回滚/就地修复安装二选一。

## 2026-09-01 修复动作

2026-08-31 18:30:43 再次复发，System 日志 `1074` 仍记录 `wininit.exe` 因 `lsass.exe` 意外终止触发重启；Application 日志显示仍为 `lsass.exe + RPCRT4.dll + 0xc0000005`，偏移回到 `000000000001ebf2`。说明仅隔离 WPS 更新任务、360 用户目录、搜狗外围组件和 Nahimic 服务/驱动不足以阻止复发。

已执行修复：

- 恢复因隔离导致弹窗缺失的搜狗文件：`D:\搜狗输入法\SogouInput\Components\IChat\1.0.2.3232\SOGOUSmartAssistant.exe`。
- 为避免继续弹“找不到文件”，恢复此前隔离的搜狗外围程序：`SogouCloud.exe`、`PinyinUp.exe`、`SogouComMgr.exe`、`isgpet.exe`、`SOGOUSmartAssistant.exe`。结论：搜狗问题不应靠直接改名 exe 处理，应改为完整卸载/重装。
- 使用 DISM 卸载高疑 Windows 更新包：`Package_for_RollupFix~31bf3856ad364e35~amd64~~26100.9168.1.19`。输出显示 `The operation completed successfully`。
- 卸载后 `Get-HotFix` 中 `KB5121003` 已消失，出现 `KB5079473`；DISM 显示 `Package_for_RollupFix~31bf3856ad364e35~amd64~~26100.8037.1.19` 处于安装挂起状态。
- 当前系统存在 `Component Based Servicing\RebootPending` 和 `PendingFileRenameOperations`，说明必须正常重启一次，更新回滚才会真正完成。
- 为避免 Windows 立即重新安装问题更新，已临时设置自动更新策略：`HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU\NoAutoUpdate = 1`。
- 修复备份目录：`C:\Users\Administrator\Documents\Codex\2026-08-31\new-chat-2\work\windows-fix-20260831-165650`。

当前判断：

1. 弹窗属于人为隔离搜狗 exe 后残留调用导致，已恢复文件修复。
2. 自动重启仍是同一 `lsass.exe` 崩溃链路，已经升级到回滚 `26100.9168` 累积更新。
3. 重启后若系统版本仍为 `26200.9168` 或 `KB5121003` 回来，说明回滚未完成或被自动更新重新安装，需要进入恢复环境卸载质量更新，或做 Windows 就地修复安装。

重启后检查：

1. 查 `winver` / 系统版本是否不再是问题构建。
2. 查 `Get-HotFix` 是否仍无 `KB5121003`。
3. 查 Application 日志是否继续出现 `lsass.exe + RPCRT4.dll + c0000005`。
4. 若继续复发，优先走“就地修复安装 Windows，保留个人文件和应用”，不再继续小范围禁用软件。
