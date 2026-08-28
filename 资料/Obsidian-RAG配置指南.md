---
name: obsidian-rag-setup
description: Obsidian Copilot RAG 本地知识库 AI 问答配置步骤
tags: [Obsidian, RAG, AI, 知识库]
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-28
  originSessionId: 97234303-2b96-4c4c-8a01-e4743f297fee
---

# Obsidian RAG 配置指南

> 当前定位：旧版操作指南，保守留档。实际排错、最终配置和是否继续使用 Copilot 检索，以 [[资料/Obsidian-Copilot配置]] 为主。

> 目标：让你能用自然语言搜索自己的笔记，比如"我之前调研螺丝消除时得出什么结论？"

## 你已经有的

- ✅ Obsidian v1.13.6 已安装
- ✅ 知识库已关联：`E:\第二大脑`
- ✅ 社区插件已开启

## 你需要做的（3步，约15分钟）

### 第1步：安装 Copilot 插件（2分钟）

1. Obsidian 应该已经打开了你的知识库
2. 按 `Ctrl+,` 打开设置 → 点击左侧「第三方插件」
3. 如果提示"安全模式"，点击「关闭安全模式」
4. 点击「浏览」按钮 → 搜索 `Copilot`
5. 找到作者为 **Logan Yang** 的 Copilot 插件 → 点击「安装」→ 再点「启用」

### 第2步：注册 DeepSeek API（3分钟）

1. 打开 `https://platform.deepseek.com/`
2. 用手机号注册（国内直接访问，不需翻墙）
3. 进入「API Keys」页面 → 点击「创建 API Key」→ 复制保存
4. 充值 ¥10 就够用很久（¥1/百万 token，一条问答约 ¥0.001）

### 第3步：配置 Copilot（10分钟）

#### 3a. 配置聊天模型

在 Obsidian 设置 → Copilot → General Settings：
1. 点击「Add Custom Model」
2. 填写：
   - Model Name: `deepseek-chat`
   - Provider: `OpenAI Format`
   - Base URL: `https://api.deepseek.com/v1`
   - API Key: 粘贴第2步创建的 Key
3. 点击「Verify Connection」→ 看到绿色勾 → 点击「Add Model」
4. 在上方下拉列表选中 `deepseek-chat`

#### 3b. 配置 Embedding 模型（让 AI 能"读"你的笔记）

**推荐方案：LM Studio 本地免费**

1. 下载 LM Studio：`https://lmstudio.ai/`（选 Windows 版）
2. 安装后打开 → 搜索模型 `text-embedding-qwen3-embedding-0.6b`
3. 下载并加载该模型
4. 在 LM Studio 设置中 **开启 CORS（Enable CORS）**
5. 记下本地地址（如 `http://localhost:1234/v1`）

回到 Obsidian 设置 → Copilot → QA Settings：
1. 点击「Add Custom Model」
2. 填写：
   - Model Name: `text-embedding-qwen3-embedding-0.6b`
   - Provider: `LM Studio`
   - Base URL: LM Studio 显示的地址
   - API Key: 留空
   - CORS: ✅ 勾选
3. 点「Add Model」
4. 在上方列表选中该模型

#### 3c. 建立索引

1. 在 QA Settings 中设置：
   - Auto-Index Strategy: `ON MODE SWITCH`
   - qaExclusions: `.git/,.obsidian/`
2. 按 `Ctrl+P` → 输入 `Copilot: Force re-index vault for QA` → 回车
3. 右上角会出现索引进度条，等待完成（约1-2分钟）

## 使用方式

### 日常问答（Vault QA 模式）

1. 点击左侧 Copilot 图标打开对话窗口
2. 将模式从 `chat` 切换为 `vault QA (basic)`
3. 用自然语言提问，例如：
   - "总结中国象棋项目都改过什么"
   - "我之前调研螺丝消除游戏得出了什么结论"
   - "列出所有游戏项目的版本号"
   - "五子棋和象棋相比有哪些技术差异"
4. AI 会搜索你的笔记并给出带来源链接的回答

### 普通对话（Chat 模式）

就是普通的 AI 聊天，不搜索你的笔记。适合问通用问题。

## 常见问题

| 问题 | 解决 |
|------|------|
| 插件安装后找不到 | 确认在「第三方插件」中已启用，可能需要重启 Obsidian |
| Verify Connection 失败 | 检查 API Key 是否正确、网络是否正常 |
| 索引后搜不到内容 | 确认 qaExclusions 没把笔记目录排除掉 |
| 回复很慢 | 本地 embedding 模型首次加载慢，之后会快很多 |
| 不想装 LM Studio | 可以用 DeepSeek API 同时做聊天和嵌入，但效果会差一些 |

## 费用预估

| 项目 | 费用 |
|------|------|
| DeepSeek API（聊天） | ¥10 起充，日常使用约 ¥2-5/月 |
| LM Studio（Embedding） | 免费，本地运行 |
| **月均总计** | **约 ¥3-5**（几乎可以忽略） |

## 和 WorkBuddy 的区别

| | Obsidian RAG | WorkBuddy |
|------|-------------|-----------|
| 搜索范围 | 你的私人笔记 | 整个电脑文件 |
| 用途 | 知识库问答 | 办公自动化 |
| 隐私 | 笔记在本地 | 文件可能上传云端 |
| 费用 | ¥3-5/月 | $10/月 |

两者互补：Obsidian RAG 管知识检索，WorkBuddy 管文件操作。
