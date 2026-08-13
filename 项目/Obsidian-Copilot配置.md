---
name: obsidian-copilot
description: Obsidian Copilot v4.0.0 + Ollama 本地模型集成全记录，含排错和换机自动化脚本
metadata: 
  node_type: memory
  type: project
  status: 待定
  version: v1.5
  modified: 2026-08-13T12:12:32.684Z
  originSessionId: 97234303-2b96-4c4c-8a01-e4743f297fee
---

# Obsidian Copilot + Ollama 配置

> v1.5 | 2026-08-13

## 最终架构

```
Obsidian Copilot v4.0.0
  ├── 聊天模型: qwen2.5:7b (Ollama 本地) ← 已下载 ✅
  ├── Embedding: bge-m3 (Ollama 本地)
  ├── 诊断代理: 127.0.0.1:11435 → 127.0.0.1:11434
  │   └── 路径重写: /chat/completions → /v1/chat/completions
  │                   /embeddings → /v1/embeddings
  └── 模式: Vault QA（基于笔记库的 RAG 问答）
```

## 模型现状

| 模型 | 用途 | 大小 | 状态 |
|------|------|------|------|
| qwen2.5:7b | 聊天/RAG（目标） | 4.68GB | ✅ 已下载 2026-08-13 03:03 |
| qwen2.5:3b | 聊天/RAG（备用） | 1.93GB | ✅ 运行中 |
| bge-m3 | 向量嵌入 | 1.16GB | ✅ 运行中 |
| nomic-embed-text | 向量嵌入（旧） | 0.27GB | 🗑️ 已弃用，可删除 |

## 📥 下载记录

| 模型 | 完成时间 | 大小 | 速度 | 结果 |
|------|----------|------|------|------|
| qwen2.5:7b | 2026-08-13 03:03:31 | 4.68GB | 35-81 MB/s | ✅ 成功 |
| bge-m3 | 2026-08-12 | 1.16GB | — | ✅ 成功 |
| qwen2.5:3b | 2026-08-12 | 1.93GB | — | ✅ 成功 |

**关键结论**：qwen2.5:7b 白天反复卡死在 80-92%（网速仅 16KB/s），凌晨 3 点下载网速飙到 80MB/s，几十秒完成。**大模型下载必须走凌晨时段**。

## 优化配置（v1.2 新增）

| 配置 | 值 | 说明 |
|------|-----|------|
| temperature | 0.3 | 从 0.1 提高，让回答更自然 |
| userSystemPrompt | 中文 RAG 提示词 | 要求引用来源、列出文件名、遇到无信息时明确说 |

系统提示词内容：
```
你是知识库助手。基于提供的笔记内容回答问题。规则：
1. 必须引用来源中的具体内容，不能笼统概括
2. 如果来源中没有明确信息，直接说「笔记中没有相关记录」
3. 列出每条信息的出处（文件名）
4. 用中文回答，简洁直接
```

## 五个大坑

| # | 问题 | 根因 | 解决 |
|---|------|------|------|
| 1 | 模型列表 "No models" | v4 需要 providers + configuredModels + backends 三层全配 | 配齐三层 |
| 2 | 聊天窗口空白 | provider 缺 `origin` 字段，JS 崩溃 | 加 `origin: {kind: "byok"}` |
| 3 | "Failed to fetch" → 404 | Copilot 用 OpenAI 格式 `/chat/completions`，Ollama 在 `/v1/chat/completions` | 代理路径重写 |
| 4 | enableSemanticSearchV3 = false | 索引需要此开关为 true 才启动 | 改为 true |
| 5 | qwen2.5:3b 回答太泛 | 3B 参数推理弱 + nomic-embed-text 中文差 | 升级 bge-m3 + 中文提示词 + 7b |

## 关键配置项（data.json）

| 配置 | 值 | 说明 |
|------|-----|------|
| defaultChainType | `"vault_qa"` | RAG 问答模式 |
| defaultModelKey | `"qwen2.5:3b\|ollama"` | ⚠️ 待切换为 7b |
| embeddingModelKey | `"bge-m3\|ollama"` | 向量嵌入模型 |
| enableSemanticSearchV3 | `true` | **必须为 true，否则索引不启动** |
| temperature | `0.3` | 适中的创造性 |
| userSystemPrompt | 中文 RAG 提示词 | 强制引用来源 |
| enableSelfHostMode | `false` | 用户模型不走自托管流程 |
| providers.ollama.baseUrl | `"http://127.0.0.1:11435"` | 指向诊断代理 |
| providers.ollama.providerType | `"openai-compatible"` | Copilot 实际走 OpenAI 兼容路径 |
| providers.ollama.origin | `{kind: "byok", catalogProviderId: "ollama"}` | 防止 JS 崩溃 |

## 环境变量

`OLLAMA_ORIGINS=app://obsidian.md*`（持久化到 Windows 注册表用户级）

## 换机自动化

新设备上执行以下步骤：

### 1. 安装 Ollama

从 https://ollama.com 下载安装 Windows 版

### 2. 设置 CORS

```powershell
[Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', 'app://obsidian.md*', 'User')
# 重启 Ollama（任务栏托盘图标 → 右键 → Quit → 重新打开）
```

### 3. 下载模型

```bash
ollama pull qwen2.5:7b   # 建议凌晨下载，白天网速仅 16KB/s 会卡死
ollama pull bge-m3
```

### 4. 启动诊断代理

将 `ollama-proxy.py` 放到任意目录，运行：
```bash
python ollama-proxy.py
```

代理脚本位置：`C:\Users\Administrator\.claude\projects\C--\ollama-proxy.py`

### 5. 安装 Obsidian 插件

在 Obsidian 社区插件中搜索安装 **Copilot**（v4.0.0+）

### 6. 配置 Copilot

复制 `data.json` 到 `.obsidian/plugins/copilot/` 下，或手动按上表配置。

### 7. 启用 Vault QA + 索引

- `defaultChainType` → `vault_qa`
- `enableSemanticSearchV3` → `true`
- 加载后执行 `Ctrl+P` → "Copilot: Index vault"

## 相关文件

| 文件 | 位置 |
|------|------|
| Copilot 配置 | `memory\.obsidian\plugins\copilot\data.json` |
| 诊断代理 | `C:\Users\Administrator\.claude\projects\C--\ollama-proxy.py` |
| 代理日志 | `C:\Users\Administrator\.claude\projects\C--\proxy.log` |

## 检索跑偏根因 + 止损决策（2026-08-13）

### 根因（4 组实测排除法）

7b 模型 ✅、bge-m3 排序 ✅、索引 ✅ 都正常，问题在 **Copilot 插件检索拼装环节**：

1. bge-m3 输出 1024 维，Orama 向量库只建 256 维 → 相似度乱算（issue #1224）
2. MiniSearch 中文退化单字匹配，英文词反而准 → 「私有改 public」被顶前

### 调研「更新+重建」结论

- 更新无意义（装的 v4.0.0 已是最新，8/11 发布）
- 重建索引有 75% 把握（源码已修维度 bug + 中文 bigram），命令 =「Force Reindex Vault」

### 决策：止损

用户体验「太差，要非常严谨才能勉强答」。决定**放弃折腾 Copilot 检索**：查笔记/问版本/找信息 → 直接问 Claude Code；Copilot 留作聊天/写作。

## 待办

- [x] 凌晨 3 点 cron 自动下载 qwen2.5:7b → ✅ 已完成（2026-08-13 03:03）
- [x] 7b 下载成功后：改回 defaultModelKey + configuredModels + backends → ✅ 已完成（三层全 = qwen2.5:7b）
- [x] 7b 实测 → ✅ 已测，检索跑偏根因定位（见上）
- [ ] 写一键换机脚本 → 因放弃 Copilot 检索，降级为「可选」

## 用户反馈与决策（2026-08-13）

### 7b「不聪明」反馈

用户实测后反馈 qwen2.5:7b 不够聪明。查配置：GTX 1650 4GB + 32GB 内存 + i5-10400F，本地模型舒适区 7b~14b。

### 三方案讨论结论

| 方案 | 结论 |
|------|------|
| qwen3:8b | 小改善（60→70 分），非质变 |
| qwen3:14b | 更聪明但 CPU 硬扛，慢 |
| 混合方案（本地找笔记 + DeepSeek 云端回答） | 唯一能「明显变聪明」，¥10 用很久 |

**核心认知**：本地小模型换哪代都不可能「很聪明」，变聪明只有云端。当初选纯本地时未摊开讲这个代价。

### 决策

不升级、不上混合方案，保持现状。Copilot 检索已止损，查笔记改问 Claude Code；Ollama 留着本地聊天/写作。

### 环境备注

- Ollama 已升级 0.32.8，自带白色聊天界面 + launch 启动器（launch 是启动第三方 AI 工具，与本项目无关）
- nomic-embed-text 已弃用，可删（274MB）
