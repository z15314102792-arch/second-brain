---
name: deepseek-harness
description: DeepSeek Harness（dsh）安装记录，网页包装成桌面
metadata: 
  node_type: memory
  type: project
  status: 运行中
  version: v1.5
  modified: 2026-08-15T17:00:00.000Z
---

# DeepSeek Harness 项目

## 版本：v1.5（用户真人实测通过，转圈根治彻底收尾）

## 背景
用户想下载「deepseek Hermes」，经调研确认是 DeepSeek 官方刚出的首款 Agent 产品 **DeepSeek Harness**（命令 `dsh`），不是 Nous Research 的 Hermes Agent（第三方软件）。

## 环境
- Windows 11（10.0.26200），**无 WSL、无 git**
- Node.js v24.19.0（位于 `D:\node.exe`）+ npm 11.17.0
- Edge 浏览器（曾长期卡在 92 版本，2026-08-15 已升级到 151）
- 有 sharp（随 dsh 依赖安装）

## 已完成
1. 澄清「DeepSeek Hermes」真相（官方 Harness vs 第三方 Hermes Agent）
2. 全局安装 `@deepseek-ai/dsh@0.1.0-rc.6`（含原生依赖 allow-scripts 补跑）
3. 确认官方**无桌面版** → 采用「网页包装成桌面」方案
4. 启动脚本：`C:\Users\Administrator\DeepSeek-Harness\start-dsh.bat`
5. 桌面快捷方式：`C:\Users\Administrator\Desktop\DeepSeek Harness.lnk`
6. 更换快捷方式图标为黑色鲸鱼（开放平台 `fe-static.deepseek.com/platform/favicon.svg` → sharp 转 ICO：`deepseek-black.ico`）
7. **根治「转圈」问题**（见下方「转圈根因」）
8. **装 3 个插件**（dshmarket + dsh-persona-memory + @anweat/dsh-browser），见下方「插件安装」

## 转圈根因（真正原因，纠正 v1.1 的误判）

**现象**：web UI 卡在 loading spinner，进不了主界面。

**根因链**（用 CDP 无头浏览器抓取 console 定位）：
1. 用户的 **Edge 版本是 92.0.902.67**（2021 年 9 月），过时约 5 年。
2. dsh 前端用了 ES2022 的 `Object.hasOwn`（Edge 93+ 才支持），Edge 92 直接 `TypeError: Object.hasOwn is not a function` → boot 崩溃 → 永久转圈。
3. Edge 92 还有 WebSocket bug（"WebSocket is closed before the connection is established"，不发送握手请求），导致实时下行连接失败。

**修复**（两条都做了）：
1. **注入 polyfill**：编辑 `C:\Users\Administrator\AppData\Roaming\npm\node_modules\@deepseek-ai\dsh\node_modules\@deepseek-ai\dsh-web-frontend\dist\index.html`，在 `<title>` 后加一行 `Object.hasOwn` polyfill（`if(!Object.hasOwn){...}`，新浏览器里条件为 false 自动跳过，向后兼容无害）。
2. **升级 Edge 92 → 151**：自动更新三条路（`Start-Service edgeupdate` / `MicrosoftEdgeUpdate.exe /silent` / `winget upgrade`）全部失败（更新器日志 `Main failed 0x80040c01`）。改为**下载微软官方离线安装包** `go.microsoft.com/fwlink/?LinkID=2093437`（`MicrosoftEdgeEnterpriseX64.msi`，203MB，数字签名 Valid），`msiexec /i ... /qn /norestart` 静默覆盖安装，**92.0.902.67 → 151.0.4129.86**。

## 端到端验证（原始数据）
新版 Edge (151) headless + CDP 实测：
- boot 清单存在：true
- 仍显示转圈：false
- 主界面文字：`探索未至之境 / 预览版 / 选择工作区 / 标准模式`
- WebSocket 握手：`101 Switching Protocols` × 2
- 异常/错误：无

✅ 结论：进主界面 + WebSocket 正常 + 无异常。

- **用户真人实测（2026-08-15）**：双击桌面图标，进主界面 + 完成一次真实对话，✅ 通过。转圈问题彻底闭环。

## 关键结论
- dsh 后端 / API Key / 模型 / 网络 **全部正常**（`dsh --profile headless` 调用模型验证通过）
- 前端 Web UI 是 **v0.1 开发者预览版**，对**过时浏览器**不兼容（需要 Edge 93+ / 新版 Chrome）。
- ⚠️ **v1.1 曾误判根因是 `127.0.0.1` 和 Edge `--app` 模式**，实为 Edge 92 过旧导致 `Object.hasOwn` 崩溃 + WebSocket bug。已纠正。

## 插件安装（v1.3）

装了 3 个社区插件（都装到 web profile：`~/.dsh/profiles/web/`）：

| 插件 | 版本 | 作用 |
|------|------|------|
| dshmarket | 1.3.1 | 插件市场入口，Web UI 出现「设置→插件市场」 |
| dsh-persona-memory | 0.1.12 | 跨会话记忆（存 MEMORY.md / USER.md） |
| @anweat/dsh-browser | 0.1.3 | 浏览器自动化（AI 操作网页） |

### 前置与坑
- **必须先装 pnpm**（`npm i -g pnpm` → v11.21.0），`dsh plugin` 底层调 pnpm。
- **sharp 国内下载坑**：browser 依赖 sharp@0.32.0 从 GitHub 下 libvips 首次超时，重试后成功。若再遇到，设 `npm_config_sharp_libvips_binary_host=https://cdn.npmmirror.com/binaries/sharp-libvips`（pnpm 11 的 `config set` 不支持自定义 key，需直接写 .npmrc）。
- 装完需**重启 dsh web** 才生效。

### 验证
重启后 CDP 实测：仍转圈 false、主界面正常、无异常。

### 插件市场加载失败排查（v1.4）
- **现象**：装完插件后，Web UI 插件市场显示「插件目录加载失败，请稍后重试」。
- **排查**：快照文件 `data/registry-snapshot.json` JSON 合法（457 插件）；数据源 `awesome-dsh-plugin.com` 国内可达。**真正原因是 dsh web 服务进程崩溃（3080 无监听）**，前端请求不到 `/dsh-market/registry`。
- **修复**：重启 dsh web 后恢复，接口返回 `source: live`、573 插件、HTTP 200。
- **隐患**：崩溃确切原因未定位（当时日志被清理）；若再次崩溃需保留日志排查。

## 使用方式
- 双击桌面「DeepSeek Harness」图标（普通浏览器打开 localhost）
- 界面地址：http://localhost:3080
- API Key 已配置在 `C:\Users\Administrator\.dsh\.credentials.yaml`
- 命令行模式可用：`dsh --profile headless "任务"`

## 决策记录
- 不装第三方桌面 EXE（非官方、未签名、有风险）
- 用「普通浏览器打开 + 桌面快捷方式」实现桌面端体验（官方原版、零风险）
- Edge 自动更新组件损坏，改用官方 MSI 静默覆盖升级（国内直连微软、免费、零依赖）

## 待办
- （已确认 ✅）插件市场入口出现、目录加载正常（573 插件）。
- （待观察）记忆插件（dsh-persona-memory）是否跨会话生效。
- （可选）等 dsh 正式版后，再考虑「独立窗口」体验。
- （注意）dsh 升级后 index.html 的 polyfill 可能被覆盖；若未来又转圈且浏览器旧，需重新注入。
- （注意）dsh 升级后 profile 目录的插件可能需重装；装插件前先确认 pnpm 可用 + sharp 镜像配置。
