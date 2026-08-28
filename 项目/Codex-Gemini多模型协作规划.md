---
name: codex-gemini-multi-model-plan
description: Codex 作为总管、Gemini 作为下级执行模型、本地脚本处理机械任务的额度优化规划
tags: [Codex, Gemini, 多模型, 额度优化, 工作流]
metadata:
  node_type: memory
  type: project
  status: 首版已落地
  version: v0.3
  modified: 2026-08-28
---

# Codex + Gemini 多模型协作规划

## 目标

在不购买 OpenAI 官方 API、不依赖野生中转站的前提下，减少 Codex Plus 额度消耗。

最终效果：用户只提出目标，由 Codex 判断任务等级；简单任务自动交给 Gemini 或本地工具；复杂任务由 Codex 处理；用户不需要在 Codex 和 Gemini 之间手动复制粘贴。

## 第一版范围

- 下级模型只使用 Gemini，不接入 DeepSeek。
- Gemini 既负责调研，也负责低风险的文件操作和测试执行。
- Codex 负责任务分类、方案决策、复杂任务、最终复核。
- 本地脚本负责不需要智能判断的机械工作。
- OpenAI 官方 API 暂不接入，避免额外消费。
- 中转站暂不接入，避免模型降级、隐私泄露和结果不可靠。

## 分级规则

### 0 级：本地工具

不调用模型：搜索文件、运行测试、格式化、统计、批量重命名、图片压缩、音视频转换、固定规则替换和读取日志。

### 1 级：Gemini 调研和文本任务

交给 Gemini：搜索 GitHub 成熟方案、读长文、总结资料、整理竞品、生成初稿、解释普通报错、整理需求、扫描项目结构和寻找重复代码。

### 2 级：Gemini 低风险执行

交给 Gemini：批量改文案、补注释、生成测试数据、按明确规则修改多个文件、执行已有测试、修复简单格式问题和编写小型脚本。

限制：不能接触密钥和敏感目录，不能删除项目，不能执行不可逆操作，不能推送 Git；核心逻辑改动必须回到 Codex 复核。

### 3 级：Codex Luna

处理必须结合本地上下文、但复杂度不高的任务，例如少量文件的小功能、明确的小 bug、项目配置和简单接口接入。

### 4 级：Codex Terra

处理跨文件、跨模块、数据流、接口兼容性、前后端联动和需要工程判断的任务。

### 5 级：Codex Sol

处理安全、权限、密钥、支付、数据迁移、复杂架构、疑难 bug、不可逆操作和最终上线前审查。

## Gemini 的调用方式

用户不手动复制粘贴 Gemini 结果。计划采用本地 MCP 桥接方式：

```text
Codex 判断任务等级
  -> 调用本地 Gemini MCP 工具
  -> MCP 桥接器启动 Gemini CLI 或 Gemini ACP
  -> Gemini 读取文件、调研或执行受限操作
  -> 返回文字结果、修改文件和测试结果
  -> Codex 审核并决定是否接受
```

### 实现顺序

1. 确认本机已安装 Gemini CLI，并验证能登录、读取文件和执行一个只读任务。
2. 先用 Gemini CLI 的非交互命令验证自动调用，例如 `gemini -p "任务"`。
3. 编写一个很小的本地 MCP 桥接器，向 Codex 暴露 `delegate_to_gemini` 工具。
4. 后续优先使用 Gemini CLI 的 ACP 模式，让外部客户端通过结构化协议控制 Gemini，而不是自行重写完整 Agent。
5. 桥接器提供四种权限模式：`research`、`draft`、`edit`、`verify`。
6. 默认只读；`edit` 才允许改文件；禁止删除、改密钥、改系统配置和 Git push。
7. 用真实任务验证 Gemini 的修改、命令输出和测试结果能否自动返回 Codex。

## 任务包格式

Codex 转交 Gemini 时必须包含：目标、工作目录、允许访问的路径、允许修改的文件、禁止操作、允许执行的命令、完成标准和必须返回的结果。

示例：

```text
目标：扫描项目中的重复错误处理逻辑
模式：research
允许：读取源码、搜索文本、生成报告
禁止：修改文件、删除文件、安装依赖、推送 Git
返回：文件路径、行号、重复逻辑、建议方案、潜在副作用和不确定项
```

## 自动路由原则

- 机械且确定：本地工具。
- 查资料、读长文、初稿和简单批处理：Gemini。
- 明确规则的低风险文件修改：Gemini。
- 必须理解本地项目的小改动：Codex Luna。
- 跨模块或需要工程判断：Codex Terra。
- 高风险和最终把关：Codex Sol。

## 成本控制

- 优先使用 Gemini 订阅和 Gemini CLI 的可用额度。
- Gemini Developer API 与 Gemini Pro 应用订阅不视为同一额度；没有确认前不把 API 当作免费无限通道。
- API 方案以后只作为可选后备，不作为第一版基础设施。
- 不让最高档模型处理总结、搜索、批量改文案等低风险任务。
- 每次调用记录任务等级、模型、是否成功和是否返工；用一周真实数据决定是否继续扩展。

## 调研依据

- Gemini CLI 工具文档：支持文件系统工具、Shell、MCP 和工具权限控制。
  https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/tools.md
- Gemini CLI 命令参考：支持 `gemini -p` 非交互调用和 `--approval-mode` 权限模式。
  https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/cli-reference.md
- Gemini CLI ACP 文档：ACP 通过 stdio 上的 JSON-RPC 让外部客户端程序化控制 Gemini CLI，适合作为桥接基础。
  https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/acp-mode.md
- Gemini API 官方价格说明：Developer API 的免费层和付费层独立于应用使用限制，需要分别核实。
  https://ai.google.dev/gemini-api/docs/pricing

## 当前状态

2026-08-28：首版已落地。旧版 Gemini CLI 已确认不再支持个人 Code Assist；改用官方 Antigravity CLI `agy` 作为 Gemini 执行端。Codex 已通过本地 MCP 桥接器直接调用，不需要用户手动复制粘贴。

已完成的本机组件：

- `C:\Users\Administrator\Documents\Codex\gemini-bridge\server.mjs`：MCP 桥接器，版本 v0.2.0。
- `C:\Users\Administrator\Documents\Codex\gemini-bridge\package.json`：桥接器依赖与版本信息。
- `C:\Users\Administrator\.codex\config.toml`：已注册 `gemini_bridge` MCP 服务。
- `C:\Users\Administrator\.gemini\antigravity-cli\settings.json`：最小权限白名单。

真实验收结果：

- Antigravity CLI `agy` v1.1.22 已安装并完成登录，支持 `agy -p` 非交互调用。
- MCP `initialize` 和 `tools/call` 均通过。
- `research`：成功读取桥接器 `package.json` 并返回 `name`、`version`。
- `edit`：只授权桥接目录后，成功把临时文件内容从 `before` 改为 `after`；测试文件已清理。
- 越界目录：`E:\第二大脑\系统` 被桥接器直接拒绝。
- 空 stdout：桥接器现在会把 Antigravity stderr 的软拒绝原因作为错误返回，不再误报成功。

安全边界：默认只读；Gemini 不允许访问密钥、凭据、系统目录，不允许删除文件、安装依赖或 `git push`。普通工作区写入只通过 `edit` 模式和明确目录白名单开启。

## 动态协作规则

任务等级不是一次性分类。Gemini 执行过程中可以继续处理低风险步骤；一旦遇到需求歧义、不可逆操作、跨模块影响、多个方案取舍、权限不足或低置信度判断，必须停止并返回 `ESCALATE` 升级包，由 Codex 作为指挥官决定后续动作。Codex 做出决定后，再把明确的下一步交回 Gemini。

## 当前模型策略

- `research` / `draft` 默认使用 `gemini-3.5-flash-low`。
- `edit` / `verify` 默认使用 `gemini-3.5-flash-medium`。
- 只有需要更复杂推理且低档模型明确升级时，才临时使用 `gemini-3.6-flash` 或 `gemini-3.1-pro`；不把高档模型作为默认执行器。
- 当前账号实时可见模型包括 Gemini 3.7/3.6/3.5 Flash、Gemini 3.1 Pro，以及 Claude/GPT-OSS 模型；本方案仍只使用 Gemini。
- 2026-08-28 实时查询结果：Gemini 五小时配额剩余 98%，周配额剩余 99%，AI Credits 为 0。具体 Google AI 套餐名称尚未从 CLI 输出确认，不能仅凭这些数字断言是 Pro、Plus 还是免费层。

## 待办

- [x] 检查 Gemini/Antigravity CLI 安装状态和版本
- [x] 检查登录状态
- [x] 执行一次只读任务验证 CLI
- [x] 设计并实现 Codex -> Gemini 的本地 MCP 桥接器
- [x] 验证 research / edit 权限模式和越界拒绝
- [x] 验证 draft / verify 模式可调用并遵守只读/草稿边界
- [ ] 用真实项目跑一周并记录额度节省和返工次数
