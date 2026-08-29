---
name: ai-quota-monitor
description: OpenAI Codex Plus 与 Google Antigravity 双模型纯中文实时额度桌面监控看板研发全记录
tags: [项目, AI额度, 监控, Codex, Gemini, Antigravity, Python]
metadata:
  type: project
  status: 活跃
  version: v1.4
  modified: 2026-08-29
---

# AI 额度与状态实时监控桌面看板

> 项目路径：`E:\项目\ai-quota-monitor` / `C:\Tools\AIUsageMonitor`
> 当前稳定版本：`v1.4` · 2026-08-29

---

## 1. 项目背景与立项原因

### 1.1 痛点分析
1. **旧工具（PulseMeter / 社区脚本）体验不佳**：
   - 界面全英文，专有名词繁杂。
   - 无法同时直观展示“已用百分比”和“剩余百分比”。
   - 缺乏对 Google Antigravity (Gemini 3.7 Flash) 的联动监控。
   - 界面固定不可缩放，高分辨率或大字号下内容容易被截断。
2. **用户核心诉求**：
   - **双模型一体化**：同时监控 OpenAI Codex Plus（5小时主限额 + 周度限额）与 Google Antigravity 状态。
   - **纯中文极简展示**：直观展示已用、剩余百分比与精确重置倒计时。
   - **自由定制与无遮挡**：支持深浅双模式、自由调色盘、无级字号调节、窗口上下左右任意拉伸。
   - **开箱即用与免维护**：零外部依赖、不需手动配置 API Key、启动轻量无控制台黑框。

---

## 2. 系统架构与技术选型

```mermaid
graph TD
    A[桌面悬浮看板 GUI] -->|Python Tkinter| B[自适应弹性卡片容器]
    B --> C[OpenAI Codex 监控卡片]
    B --> D[Google Antigravity 监控卡片]
    B --> E[右键菜单 & 外观设置面板]

    C -->|JSON-RPC 通信| F[Codex 本地 app-server]
    C -->|JWT 解码| G[auth.json 账号解析]
    D -->|状态探测| H[Antigravity 进程与配额池]
    E -->|JSON 持久化| I[widget_config.json]
```

- **GUI 引擎**：Python 原生 `tkinter`，零第三方库依赖，内存开销 < 25MB。
- **无边框边缘拉伸（Resize Grip）**：通过鼠标位置与边缘距离（margin <= 12px）动态切换光标（`size_we`、`size_ns`、`size_nw_se`）并计算窗口新宽高。
- **数据抓取引擎**：
  - **Codex**：本地启动后台 `codex.exe app-server` 子进程，按协议发送 `initialize` ➔ `initialized` ➔ `account/rateLimits/read` 获取 5 小时与周度实时限额及 `resetsAt` 时间戳。
  - **账号信息**：解析 `~/.codex/auth.json` 中的 `id_token` JWT 荷载，自动提取绑定邮箱与订阅计划（Plus）。
  - **Antigravity**：监控 Gemini 3.7 Flash 模型响应与配额健康度。

---

## 3. 研发过程关键卡点与突破记录（详细复盘）

### 突破 1：Codex 本地限额数据的逆向提取与倒计时解析
* **卡点**：OpenAI 官方未开放公开的 Rate Limits 查询 HTTP 接口，直接调 Web 页面需登录认证。
* **突破**：
  1. 定位本机 `AppData\Local\OpenAI\Codex\bin\*\codex.exe`。
  2. 利用 Python `subprocess.Popen` 建立 `app-server` 的标准输入输出管道。
  3. 模拟标准 JSON-RPC 握手流程，抓取 `account/rateLimits/read` 返回的 `primary`（5小时限额）与 `secondary`（周度限额）数据。
  4. 编写 `format_countdown()` 函数将 `resetsAt` 秒级时间戳转换为 `X天X小时X分后重置`。

---

### 突破 2：PowerShell 命令行超长限制与 UTF-8 BOM（\ufeff）陷阱
* **卡点**：
  - 代码量膨胀到 15KB 以上时，PowerShell `run_command` 触发 Windows 单行 8191 字符上限（报 `The filename or extension is too long`）。
  - 使用 PowerShell `Set-Content -Encoding UTF8` 写入时，系统自动附加了 UTF-8 BOM 头（`0xEF 0xBB 0xBF`），导致 Python 与 CLI JSON 解析器报错 `invalid character '\ufeff' looking for beginning of value`。
* **突破**：
  1. 将大文件采用多片段安全追加（Append）或 Python 独立脚本分块写入。
  2. 全面采用 `System.Text.UTF8Encoding($false)` 或 Python `encoding='utf-8'` 强制无 BOM 保存，彻底杜绝 `\ufeff` 报错。

---

### 突破 3：Antigravity CLI 模式限制与全局零审批放行
* **卡点**：
  - 用户之前运行 `agy --mode=accept-edits`，该模式只自动批准文件编辑，每当执行终端命令（`Bash` / `run_command`）时系统依然强制弹窗。
* **突破**：
  1. 在 `~/.gemini/antigravity-cli/settings.json` 的 `permissions.allow` 白名单中直接写入 `"command(*)"`。
  2. 将 CLI 启动参数升级为 `--dangerously-skip-permissions`（YOLO 免审批模式），彻底实现文件与命令 100% 自动执行。

---

### 突破 4：PowerShell 原生别名冲突与极速指令开发
* **卡点**：
  - 用户在 PowerShell 输入 `gc` 触发 `Get-Content`，输入 `gl` 触发 `Get-Location`。
* **突破**：
  1. 在 `$PROFILE` 中使用 `Remove-Item Alias:gc, Alias:gl -Force` 覆盖系统默认别名。
  2. 注册无冲突的专属极速指令：
     - **`gpc`** / **`gemini-pro -c`**：一秒继续上次会话 + 全自动免审批。
     - **`gpl`** / **`gemini-pro -l`**：调用自研的 `session_manager.py` 终端图形化历史会话管理器，输入序号即可秒切历史会话。

---

### 突破 5：无边框窗口自由拉伸与字号缩放防截断
* **卡点**：
  - 传统 `overrideredirect(True)` 移除了系统标题栏和边框，导致无法拖拽边框缩放。
  - 用户调大字号后，固定高度的卡片发生文字遮挡和进度条被挤压。
* **突破**：
  1. 实现边缘像素级碰撞检测：鼠标进入边缘 12px 范围自动变为缩放手势（`size_we`、`size_ns`、`size_nw_se`），按住拖动即可改变宽高。
  2. 所有组件采用 `expand=True` 与 `fill=tk.BOTH` 弹性填充，尺寸随字号和窗口动态伸缩，杜绝任何字符被遮蔽。
  3. 重构设置面板排版为卡片分栏：深浅模式置顶、5 套色系、微调胶囊、所见即所得实时文字预览。

---

### 突破 6：Antigravity (Gemini) 真实运行感知与会话逆向探测
* **卡点**：
  - 过去 Antigravity 监控卡片仅返回静态 Mock 数据，无法反映真实的 CLI 进程状态与上下文活跃度。
* **突破**：
  1. 通过静默 Windows API / `tasklist` 实时探测 `agy.exe` 运行状态，精准标识「`活跃运行中 🟢`」与「`待命就绪 🟢`」。
  2. 逆向遍历 `~\.gemini\antigravity-cli\brain` 目录结构与 `transcript.jsonl`，自动统计历史会话总数、最近活跃时间差（如「刚刚」、「3分钟前」）并提取最新会话标题摘要。
  3. 支持双击卡片直达终端会话选择器（`session_manager.py`）或极速指令 `gpc`。

---

### 突破 7：8 方向无死角自由边缘拉伸与屏幕绝对坐标记忆
* **卡点**：
  - 之前的拉伸仅支持右侧和底侧，无法从左侧、顶部及另外 3 个角落自由拖拽。
  - 重新启动看板后，窗口位置无法保持在用户上次摆放的精确屏幕位置。
* **突破**：
  1. 升级边缘碰撞检测算法至 8 个几何象限（`nw`, `n`, `ne`, `w`, `e`, `sw`, `s`, `se`），计算坐标平移量与反向尺寸伸缩，支持全方位无死角拉伸。
  2. 拖拽与缩放结束后实时将 `pos_x`, `pos_y`, `width`, `height` 持久化写入 `widget_config.json`，启动时精准恢复。

---

### 突破 8：秒级本地递减倒计时与低配额智能双重色觉预警
* **卡点**：
  - 30 秒轮询间隔导致重置倒计时长时间不更新。
  - 额度耗尽前缺乏醒目的视觉反馈。
* **突破**：
  1. 后台缓存 `resetsAt` 秒级时间戳，GUI 线程启动 1 秒本地轻量定时器，秒级平滑递减剩余时间。
  2. 当 5 小时额度剩余 <= 15% 或周度额度剩余 <= 10% 时，进度条与状态灯自动触发警示色（橙红高亮），提供直观用量警报。

---

## 4. 版本迭代记录 (Changelog)

| 版本号 | 发布日期 | 核心更新内容 |
| :--- | :--- | :--- |
| **v0.1** | 2026-08-28 | 调研并测试 PulseMeter，确立 Codex 额度监控需求。 |
| **v1.0** | 2026-08-29 | 首次完成纯中文桌面悬浮看板，集成 OpenAI Codex 与 Google Antigravity 双监控。 |
| **v1.1** | 2026-08-29 | 新增右键设置菜单、5 套预设主题、置顶切换与半透明毛玻璃调节。 |
| **v1.2** | 2026-08-29 | 新增 🌙 深色 / ☀️ 浅色双模式、自由调色盘、无级字号调节（8pt~20pt）。 |
| **v1.3** | 2026-08-29 | 支持鼠标边缘自由拉伸缩放，重构弹性自适应排版与胶囊设置面板。 |
| **v1.4** | 2026-08-29 | **当前版本**：深度集成 Antigravity 真实会话与进程探测、升级 **8 方向全方位自由拉伸**、新增**窗口坐标记忆持久化**、**秒级动态递减倒计时**、**智能低配额色觉预警**、**开机自启一键管理**。 |

---

## 5. 文件与配置清单

- **主程序**：`E:\项目\ai-quota-monitor\AI_Quota_Monitor_ZH.pyw`（无黑框后台运行）
- **配置文件**：`E:\项目\ai-quota-monitor\widget_config.json`（持久化记录颜色、字号、窗口宽高、透明度）
- **会话管理脚本**：`E:\项目\ai-quota-monitor\session_manager.py`（终端恢复历史对话）
- **系统快捷入口**：`gpc`（继续会话）、`gpl`（会话清单）、`gy`（全新免审批会话）

---

## 6. 相关记忆与链接

- [[项目/Codex Plus用量可视化]] — 项目初期调研对比记录
- [[项目/Codex-Gemini多模型协作规划]] — 多模型分工与调度规划
- [[知识/用户人物画像]] — 用户偏好与即时反馈需求
- [[CLAUDE]] — 知识库维护与协作总则