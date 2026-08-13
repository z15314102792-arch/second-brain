---
name: ai-short-drama-video
description: AI短剧+解说视频，文案→AI生成动态画面→自动成片，工具VideoClaw
metadata: 
  node_type: memory
  tags: 
    - 视频制作
    - AI
    - 解说视频
    - AI短剧
  type: project
  status: 活跃
  version: v1.0
  modified: 2026-08-13T12:13:12.641Z
  originSessionId: ea901041-16df-4c31-8a13-61c485404177
---

# AI短剧解说视频

> 核心需求：只给文案/声音，AI 自动生成符合内容的动态画面，自动剪辑成片。做 AI 短剧 + 解说类视频。

## 工具：VideoClaw

- 哈工大深圳张民团队 + 阿里开源的 AI 视频生成框架（网页版，不是桌面软件）
- 全流程：文案 → 分割分段 → 每段 AI 生成画面 → 图生视频"动起来" → 配音 → 字幕 → 拼成片
- 全程调云端 API，**不需要本地显卡**（4GB 显卡不是障碍）

## 部署位置

```
D:\VideoClaw\video-claw\video-claw\
├── backend\           ← 后端（Python/FastAPI）
│   └── config.yaml    ← 配置（key + 模型）
└── frontend\          ← 前端（Next.js 网页）
```

## 启动方式（明天开机后需要重新启动）

服务会随关机停止，重开需在**两个黑窗口**分别跑：

**后端**（先开）：
```
cd D:\VideoClaw\video-claw\video-claw\backend && uv run python api_server.py
```

**前端**（后开）：
```
cd D:\VideoClaw\video-claw\video-claw\frontend && npm run dev
```

然后浏览器打开 **`http://localhost:3000`** 就是软件界面。

> ⚠️ 明天直接让 Claude Code 帮忙启动即可，不必自己敲命令。

## 配置（已配好，只需 2 个 key）

| 用途 | 模型 | 供应商 |
|------|------|--------|
| 写文案/翻译画面指令 | `deepseek-v4-flash` | DeepSeek（用户已有） |
| 视觉评估 | `qwen3.6-flash` | 阿里云百炼 |
| 生成画面 | `wan2.7-image` | 阿里云百炼 |
| 图生视频 | `wan2.7-i2v` | 阿里云百炼 |
| 配音 | edge-tts | 微软（免费） |

两个 key 都存在 `backend\config.yaml`，已验证连通。

## 免费额度与成本

| 项 | 额度/单价 |
|----|-----------|
| 阿里云百炼新用户 | 免费 50 秒视频 + 50 张图（90 天有效） |
| 已消耗（今天试跑） | 约 10 秒视频 + 6 张图 |
| 剩余 | 约 40 秒视频 + 44 张图 |
| 超额度单价 | 视频 720P ¥0.6/秒、1080P ¥1/秒；图约 ¥0.2-0.3/张 |

## 两种出片模式（关键）

| 模式 | 参数 | 效果 | 成本 |
|------|------|------|------|
| 静态图轮播 | `video_mode: image_concat` | 静态图 + 配音 + 字幕 | 只耗图，不耗视频 |
| 动态视频 | `video_mode: dynamic_video` | 每张图"动起来"（镜头移动/元素运动） | 耗视频秒数 |

用户要的是**动态视频**（画面有基础运动变化）。

## 已完成的验证（2026-08-13）

1. ✅ 静态图轮播跑通（4 段文案 → 4 张图 → 配音字幕 → final.mp4，105 秒）
2. ✅ 动态视频跑通（2 段文案 → 2 张图 → 图生视频 → final.mp4，197 秒，约 10 秒成片）
3. 成片示例路径：`D:\VideoClaw\video-claw\video-claw\backend\code\result\task\20260813_200342_a756183e\final.mp4`

## 待办（明天继续）

- [ ] **换画面风格**：默认是「黑白火柴人简笔画」（`style_control` 默认值），用户不想要。需让用户选风格（写实电影感 / 3D卡通 / 国风水墨 等），通过 `style_control` 参数改
- [ ] **用用户自己的文案**试跑一条（今天用的是我造的"三个AI工具"示例文案）
- [ ] 教用户在网页 `localhost:3000` 上自己操作
- [ ] 用户评估动态效果是否满意，不满意再调（换更强视频模型/加长每段/调运动幅度，会相应加成本）

## 关键知识（踩坑记录）

- **风格由 `style_control` 参数控制**，默认 `Minimalist black-and-white matchstick figure style illustration`（黑白火柴人）。不改就是火柴人简笔画。
- 文案按**句号**分割成段，每段一张图。想让某段画面独立，就在文案里用句号隔开。
- 提交任务的 API：`POST /api/pipelines/standard/tasks`，参数见 `backend\api\schemas\pipelines.py` 的 `StandardPipelineRequest`。
- 文案（中文）通过 curl 提交会乱码，要用文件方式（`curl --data-binary @文件.json`）。
- 任务一旦启动**无法中途停止**（只能杀后端进程），提交前确认好文案和段数，别浪费额度。
- 图生视频慢：2 段约 3.3 分钟，段数越多越久。

## 参考

- 项目计划：`C:\Users\Administrator\.claude\plans\witty-wibbling-pebble.md`
- 相关项目：[[项目/进云老师剪辑]]（口播剪辑，真人出镜，不同路线）、[[项目/数字人口播]]（克隆脸+声音，因 4GB 显卡暂停）
