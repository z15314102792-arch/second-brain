---
name: obsidian-copilot
description: Obsidian Copilot v4.0.0 + Ollama 本地模型集成全记录，含排错和换机自动化脚本
metadata: 
  node_type: memory
  type: project
  status: 运行中
  version: v1.1
  modified: 2026-08-12T08:27:06.829Z
  originSessionId: 97234303-2b96-4c4c-8a01-e4743f297fee
---

# Obsidian Copilot + Ollama 配置

> v1.1 | 2026-08-12

## 最终架构

```
Obsidian Copilot v4.0.0
  ├── 聊天模型: qwen2.5:7b (Ollama 本地)
  ├── Embedding: bge-m3 (Ollama 本地)
  ├── 诊断代理: 127.0.0.1:11435 → 127.0.0.1:11434
  │   └── 路径重写: /chat/completions → /v1/chat/completions
  │                   /embeddings → /v1/embeddings
  └── 模式: Vault QA（基于笔记库的 RAG 问答）
```

## 三个大坑

| # | 问题 | 根因 | 解决 |
|---|------|------|------|
| 1 | 模型列表 "No models" | v4 需要 providers + configuredModels + backends 三层全配 | 配齐三层 |
| 2 | 聊天窗口空白 | provider 缺 `origin` 字段，JS 崩溃 | 加 `origin: {kind: "byok"}` |
| 3 | "Failed to fetch" → 404 | Copilot 用 OpenAI 格式 `/chat/completions`，Ollama 在 `/v1/chat/completions` | 代理路径重写 |
| 4 | enableSemanticSearchV3 = false | 索引需要此开关为 true 才启动 | 改为 true |
| 5 | qwen2.5:3b 回答太泛 | 3B 参数推理弱 + nomic-embed-text 中文差 | 升级 7B + bge-m3 |

## 关键配置项（data.json）

| 配置 | 值 | 说明 |
|------|-----|------|
| defaultChainType | `"vault_qa"` | RAG 问答模式 |
| defaultModelKey | `"qwen2.5:7b\|ollama"` | 聊天模型 |
| embeddingModelKey | `"bge-m3\|ollama"` | 向量嵌入模型 |
| enableSemanticSearchV3 | `true` | **必须为 true，否则索引不启动** |
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
ollama pull qwen2.5:7b
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

## 待办

- [ ] 写一键换机脚本（自动安装 Ollama + 下载模型 + 配置 Copilot + 启动代理）
