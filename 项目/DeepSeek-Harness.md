---
name: deepseek-harness
description: DeepSeek Harness（dsh）安装记录，网页包装成桌面
metadata: 
  node_type: memory
  type: project
  status: 运行中
  version: v1.1
  modified: 2026-08-15T10:00:00.000Z
---

# DeepSeek Harness 项目

## 版本：v1.1（修复前端转圈 + 更换黑色鲸鱼图标）

## 背景
用户想下载「deepseek Hermes」，经调研确认是 DeepSeek 官方刚出的首款 Agent 产品 **DeepSeek Harness**（命令 `dsh`），不是 Nous Research 的 Hermes Agent（第三方软件）。

## 环境
- Windows 11（10.0.26200），**无 WSL、无 git**
- Node.js v24.19.0（位于 `D:\node.exe`）+ npm 11.17.0
- Edge 浏览器可用；有 sharp（随 dsh 依赖安装）

## 已完成
1. 澄清「DeepSeek Hermes」真相（官方 Harness vs 第三方 Hermes Agent）
2. 全局安装 `@deepseek-ai/dsh@0.1.0-rc.6`（含原生依赖 allow-scripts 补跑）
3. 确认官方**无桌面版** → 采用「网页包装成桌面」方案
4. 启动脚本：`C:\Users\Administrator\DeepSeek-Harness\start-dsh.bat`
5. 桌面快捷方式：`C:\Users\Administrator\Desktop\DeepSeek Harness.lnk`
6. **修复前端转圈**（根因：`127.0.0.1` 与 Edge `--app` 独立窗口均不兼容，改用 `localhost` + 普通浏览器打开）
7. **更换快捷方式图标为黑色鲸鱼**（开放平台 `fe-static.deepseek.com/platform/favicon.svg` → sharp 转 ICO：`deepseek-black.ico`）

## 关键结论（重要）
- dsh 后端 / API Key / 模型 / 网络 **全部正常**（`dsh --profile headless` 调用模型验证通过）
- 前端 Web UI 是 **v0.1 开发者预览版**，有两个兼容坑：
  1. 访问地址必须用 `http://localhost:3080`（`127.0.0.1` 会转圈）
  2. 不能用 Edge 的 `--app` 独立窗口模式（会转圈），要用普通浏览器标签页

## 使用方式
- 双击桌面「DeepSeek Harness」图标（普通浏览器打开 localhost）
- 界面地址：http://localhost:3080
- API Key 已配置在 `C:\Users\Administrator\.dsh\.credentials.yaml`
- 命令行模式可用：`dsh --profile headless "任务"`

## 决策记录
- 不装第三方桌面 EXE（非官方、未签名、有风险）
- 用「普通浏览器打开 + 桌面快捷方式」实现桌面端体验（官方原版、零风险）

## 待办
- 用户确认双击桌面图标能正常进主界面、正常对话
- （可选）等 dsh 正式版后，再考虑「独立窗口」体验
