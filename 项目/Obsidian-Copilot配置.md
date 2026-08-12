---
name: obsidian-copilot-config
description: Obsidian Copilot v4.0.0 集成 Ollama 本地模型完整排错记录
metadata: 
  node_type: memory
  tags: 
    - Obsidian
    - Copilot
    - Ollama
    - 排错
  type: project
  status: 配置中
  version: v1.0
  modified: 2026-08-12T06:40:30.883Z
  originSessionId: 97234303-2b96-4c4c-8a01-e4743f297fee
---

# Obsidian Copilot + Ollama 集成排错全记录

> 目标：在 Obsidian Copilot v4.0.0 中用 Ollama 本地模型（qwen2.5:3b）实现 Vault QA（RAG 问答）。

## 涉及文件

- `C:\Users\Administrator\.claude\projects\C--\memory\.obsidian\plugins\copilot\data.json` — Copilot 全部配置
- `C:\Users\Administrator\.claude\projects\C--\memory\.obsidian\plugins\copilot\main.js` — Copilot 核心代码（压缩后 5.6k 行）
- Ollama 环境变量：`OLLAMA_ORIGINS`（Windows 用户级）

---

## 问题一：模型选择器显示 "No models"

### 现象
Copilot 聊天窗口打开后，模型选择器显示 "No models-"（或全部灰色不可选）。

### 说"修好了"但实际没修好的过程
1. 第一次：叫用户在 UI 里添加自定义模型 → 用户看不懂操作步骤
2. 第二次：改 data.json 加 activeModels 中的 ollama 模型 → 不生效
3. 第三次：反复改 activeModels、改字段名、改格式 → 模型仍然不显示

### 真正根因
**Copilot v4.0.0 内部使用三个独立的存储 atom（状态管理单元），必须全部配齐模型才会显示：**

| 存储 key | 变量 | 作用 |
|----------|------|------|
| `vk` | `providers` | 定义"服务商"（Ollama 是什么、用什么协议） |
| `k_` | `configuredModels` | 定义"已配置的模型"（ID 格式：`模型名|服务商`） |
| `UU` | `backends` | 定义"各后端启用了哪些模型"（chat/opencode） |

**这三个缺一不可**。`BN` 选择器（模型列表的派生计算）会交叉比对这三个 atom，任何一个为空都会导致"无模型"。

我们只加了 `activeModels` 但没加上面三个 → 模型不显示。

### 正确做法
```json
{
  "providers": {
    "ollama": {
      "providerId": "ollama",
      "providerType": "openai-compatible",
      "displayName": "Ollama",
      "origin": {"kind": "byok"},
      "requiresApiKey": false,
      "baseUrl": "http://127.0.0.1:11434/v1",
      "addedAt": 0
    }
  },
  "configuredModels": [{
    "configuredModelId": "qwen2.5:3b|ollama",
    "providerId": "ollama",
    "info": {"id": "qwen2.5:3b", "name": "qwen2.5:3b", "displayName": "qwen2.5:3b"},
    "configuredAt": 0
  }],
  "backends": {
    "chat": {"enabledModels": ["qwen2.5:3b|ollama"]},
    "opencode": {"enabledModels": ["qwen2.5:3b|ollama"]}
  }
}
```

### 教训
- **不要凭 UI 直觉去猜配置结构**。老版本 Copilot（v2.x）只有 `activeModels` 一个列表，v4 重构后变成了 provider → model → backend 三层架构。
- **先读插件代码再动手**。`main.js` 虽然压缩了，但关键变量名（`vk`, `k_`, `UU`, `BN`, `Lh`）没有混淆，找到这些就能反推出数据结构。

---

## 问题二：聊天窗口变空白

### 现象
修改 data.json 后重开 Copilot，整个聊天窗口一片空白，没有任何 UI 元素。

### 说"修好了"但实际没修好的过程
1. 加 provider 时不知道需要 `origin` 字段 → 窗口空白
2. 尝试删掉新加的配置恢复原状 → 仍然空白（因为删除不完整）

### 真正根因
**Copilot 的 `v_()` 函数崩溃了。** 这个函数在 `enableSelfHostMode=true` 时会访问 `t.origin.kind`，但我们的 provider 没有 `origin` 字段，`t.origin` 是 `undefined`，访问 `.kind` 导致 JavaScript 异常，整个组件渲染崩溃。

代码逻辑（反编译自 main.js）：
```javascript
function v_(t, e) {
  if (!e.enableSelfHostMode) return false;  // 关了就跳过
  switch (t.origin.kind) {  // ← 如果 t.origin 是 undefined，这里崩溃
    case "selfhosted": return something;
    // ...
  }
}
```

### 正确做法
1. provider 必须加 `"origin": {"kind": "byok"}`
2. 同时把 `enableSelfHostMode` 设为 `false`（双重保险）

### 教训
- **改配置文件时，所有嵌套对象字段都要补全**。minifier 不会删字段但会重命名，不能假设缺少的字段会自动给默认值。
- **JavaScript 中访问 `undefined.kind` 足以让整个 UI 崩溃**。React/Svelte 组件渲染出错 → 空白页。

---

## 问题三：模型已显示但报 "Failed to fetch"（★ 最难根因）

### 现象
模型列表里 qwen2.5:3b 正常显示，选择后发消息显示：
```
⚠️ Error occurred
Connection error.
more message: Failed to fetch
```

### 反复"修好"但实际没修好的过程（共 5 轮尝试）

| 轮次 | 尝试的修复 | 为什么无效 |
|------|-----------|-----------|
| 1 | 改 baseUrl 格式（加/去 `/v1`、改端口） | 根本和 URL 格式无关，Ollama 始终可达 |
| 2 | `set OLLAMA_ORIGINS=*` 重启动 Ollama | Windows 上 `set` 只影响当前 CMD 会话，重启后 env var 丢失；且 `*` 回显的值 Electron 不认 |
| 3 | curl 验证 CORS 通过 → 宣布修好 | curl 测试时返回 `*` 确实"通过"了，但 Electron 的 Chromium 对非 HTTP 来源（`app://`）拒绝 `*` 通配符 |
| 4 | 改 `localhost` 为 `127.0.0.1` | DNS 解析不是问题，`localhost` 和 `127.0.0.1` 都能正常解析 |
| 5 | 给 apiKey 设空字符串 `""` | `requiresApiKey: false` 时 apiKey 根本不检查 |

### 真正根因（两个层面）

**表层根因：`OLLAMA_ORIGINS` 环境变量从未真正设置成功。**
- 用户级注册表：空
- 系统级注册表：空
- 当前 Ollama 进程环境：空（因为 `ollama app.exe` 启动时还没设这个变量）

**深层根因：Electron 的 CORS 策略比浏览器更严格。**
- 标准 HTTP 来源 → `Access-Control-Allow-Origin: *` 有效
- `app://obsidian.md` 来源 → 必须回显具体 Origin，不接受 `*`
- 设 `OLLAMA_ORIGINS=*` → Ollama 返回 `ACAO: *` → curl 测试通过 → 但 Obsidian 仍然报 "Failed to fetch"
- 设 `OLLAMA_ORIGINS=app://obsidian.md*` → Ollama 返回 `ACAO: app://obsidian.md` → 正常工作

### 正确做法
```powershell
# 1. 持久化到 Windows 用户注册表
[Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', 'app://obsidian.md*', 'User')

# 2. 杀掉旧进程
Get-Process -Name 'ollama*' | Stop-Process -Force

# 3. 用新环境变量重新启动（显式传入确保当前进程拿到）
$env:OLLAMA_ORIGINS = 'app://obsidian.md*'
Start-Process 'ollama app.exe'
```

### 验证方法（正确）
```bash
# 必须用 app://obsidian.md 做 Origin 测试
curl -s -o /dev/null -D - http://127.0.0.1:11434/api/tags \
  -H "Origin: app://obsidian.md"

# 正确输出应包含（不是 *！）：
# Access-Control-Allow-Origin: app://obsidian.md
```

### 教训
- **Windows 上设置环境变量，命令行 `set` 只在当前会话生效**。持久化要用 `setx` 或 `[Environment]::SetEnvironmentVariable`。
- **Ollama 作为后台服务/Win32 应用运行，不从普通终端继承 `set` 的环境变量**。必须持久化后重启动。
- **curl 测 CORS 通过 ≠ 目标应用（Electron）能通**。Electron 的安全策略比浏览器更严，特别是对非标准协议（`app://`、`chrome-extension://` 等）。
- **永远在排查时先确认"配置是否真正生效了"**，而不是假设已生效后继续改别的东西。用 `GetEnvironmentVariable` 读注册表、用 `Get-Process` 看进程参数，不要信"我已经设过了"。

---

## 其他技术发现

### Copilot v4.0.0 架构要点
- **模型 ID 格式**：通过 UI 添加的是 UUID，手动配置用 `"模型名|服务商ID"` 格式
- **`origin.kind` 取值**：`byok`（自带密钥）、`selfhosted`（自托管）、`copilot-plus`（官方）
- **`embeddingModelKey` 同理**：`"nomic-embed-text|ollama"`
- **GitHub issue #1256**：早期版本即使 `requiresApiKey: false`，也需要塞一个非空 apiKey（如 `"ollama"`）才能被识别

### Electron + CORS 铁律
- `Access-Control-Allow-Origin: *` 对非标准协议（`app://`、`custom://`）无效
- 必须让服务器回显调用方的具体 Origin
- 需要同时处理 OPTIONS 预检请求（Headers + Methods）

---

## 当前状态（2026-08-12）

- ✅ 模型识别 — qwen2.5:3b 显示在模型列表
- ✅ 不崩溃 — Copilot 窗口正常显示
- ✅ CORS — `OLLAMA_ORIGINS=app://obsidian.md*` 持久化
- ✅ API 连通 — curl + `Origin: app://obsidian.md` 测试通过
- ⏳ 待确认 — 用户在 Obsidian 中实际测试发送消息
- ⏳ 后续 — 切换至 Vault QA 模式、启动向量索引
