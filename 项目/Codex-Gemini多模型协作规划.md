---
name: codex-gemini-multi-model-plan
description: Codex 作为总管、Gemini 作为下级执行模型、本地脚本处理机械任务的额度优化规划
tags: [Codex, Gemini, 多模型, 额度优化, 工作流, workbuddy]
metadata:
  node_type: memory
  type: project
  status: 首版已落地，路由规则已修正
  version: v0.6
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

- `research` / `draft` 默认使用 `gemini-3.5-flash-low`，最多自动升级到 Medium，再升级到 `gemini-3.1-pro-low`。
- `edit` / `verify` 默认使用 `gemini-3.5-flash-medium`，需要时升级到 `gemini-3.6-flash-medium`，再升级到 `gemini-3.1-pro-low`。
- 每个任务最多自动升级两次；达到上限仍需重大决策时，直接返回 Codex，不继续在 Gemini 内部循环。
- 不把高档模型作为默认执行器；升级模型会收到前一档的升级包，不重复从头分析。
- 当前账号实时可见模型包括 Gemini 3.7/3.6/3.5 Flash、Gemini 3.1 Pro，以及 Claude/GPT-OSS 模型；本方案仍只使用 Gemini。
- 2026-08-28 实时查询结果：Gemini 五小时配额剩余 98%，周配额剩余 99%，AI Credits 为 0。具体 Google AI 套餐名称尚未从 CLI 输出确认，不能仅凭这些数字断言是 Pro、Plus 还是免费层。
- 试运行结果：`research` 简单任务使用 `gemini-3.5-flash-low`，自动升级次数为 0，桥接器 v0.4.0 连通正常。

## 待办

- [x] 检查 Gemini/Antigravity CLI 安装状态和版本
- [x] 检查登录状态
- [x] 执行一次只读任务验证 CLI
- [x] 设计并实现 Codex -> Gemini 的本地 MCP 桥接器
- [x] 验证 research / edit 权限模式和越界拒绝
- [x] 验证 draft / verify 模式可调用并遵守只读/草稿边界
- [x] 修正 AGENTS.md 中「能并行的独立任务派子 Agent」这句自相矛盾的指令（它会引导 Codex 开原生子智能体烧额度）
- [ ] 把「优先交给 Gemini」的软指令改为显式命令触发（用户主动说"交给 Gemini"或建快捷话术）
- [x] 修正分级规则：大范围重活才下放，小任务 Codex 直接干
- [ ] 用 PulseMeter 记录修正前后各一周额度数据

## Codex 复核修正（2026-08-28）

### 已确认正确

- `C:\Users\Administrator\.codex\AGENTS.md` 中原有「能并行的独立任务派子 Agent」与省额度目标冲突，已替换为禁止为了省额度调用 Codex 原生子 Agent。
- `C:\Users\Administrator\.codex\config.toml` 中 `model_verbosity = "high"` 会增加日常输出长度，已调整为 `medium`。
- 分级规则已改为“大范围调研下放，小查询和本地机械任务由当前 Codex 直接做”。
- 保存进度仍固定由当前 Codex 执行，不交给 Gemini/低成本模型。

### 需要降级表述

- “AGENTS.md 是建议，hooks 才是强制”应理解为：AGENTS.md 可以引导模型行为，但高风险边界不能只靠软指令；需要显式命令、工具层限制或 hooks 辅助。
- “社区已证伪”应理解为：仅靠 AGENTS.md 软指令做自动分派不可靠；成熟方案通常用宿主程序、路由层、hooks 或显式命令减少模型自由裁量。

### 当前固定规则

- 大范围 GitHub 初筛、README 摘要、长网页/大量资料整理：优先用 `delegate_to_gemini`。
- 单点查询、本地下载/解压/校验/启动、明确配置修正：当前 Codex 直接做。
- 保存进度：当前 Codex 直接写完整日志并复核 git 暂存。
- 禁止为了省额度调用 Codex 原生子 Agent。

## 社区调研结论：分级协作可行吗（2026-08-28）

### 总判定

**方向成立，机制有错。**"强模型决策 + 弱模型执行"在社区有硬数据支撑的成熟先例，但所有成熟案例的共同点是：**路由由程序机械执行，不靠主模型自觉**。目前方案里"写进 AGENTS.md 指望 Codex 主动分派"是已被社区证伪的做法。

### 成熟案例（按成熟度排序）

1. **Aider architect/editor 模式（最成熟，硬数据）**：架构师模型（强）只出方案，编辑器模型（便宜）只改代码，拆分由 Aider 程序代码强制完成。官方基准：DeepSeek R1 架构师 + Sonnet 编辑器成本 $13.29，对比 o1 单干 $186.50（14 倍），分数反而更高（64.0% vs 61.7%）。结论：分级本身省钱且提质，但拆分动作发生在宿主程序里，不是模型自己的选择。
2. **claude-code-router（musistudio，36.9k star）**：本地代理层路由，按请求类型把不同档位调用机械转发给不同模型（Gemini/DeepSeek/本地模型），完全不依赖模型服从。注意：只适用于 Claude Code 协议；**Codex 订阅鉴权走 OpenAI 官方，无法这样代理换后端**。用户 Claude Code 已用环境变量全套指向 DeepSeek，等效于这个方案。
3. **Gemini 当编排者、Codex 当执行者（Isopolito/mcp）**：层级反转结构——便宜/免费的 Gemini CLI 当日常主力界面，Codex/Claude 只在被委派时消耗额度。与本方案相反，但更符合"贵模型按需出场"的经济学。
4. **Codex→Gemini 委派（psychofanPLAYS/gemini4codex-mcp）**：与本项目几乎同构（Codex 指挥 Antigravity Gemini 做下级，git worktree 隔离，delegate_to_agent 工具），但**只有 1 star、2026-08-10 才创建，属于个人实验，不算成熟案例**。它同样依赖 BOOTSTRAP.md 软指令哄 Codex 分派。自研桥接器（v0.4.0）水平不低于它。
5. **codex-mcp-bridge（npm 包）**：作者自己承认——有 shell 的终端 Agent 直接调 CLI"更快、更便宜、零开销"，MCP 桥只在无 shell 客户端或需要结构化输出时才划算。印证：委派有固有开销，不是免费午餐。

### Codex 额度机制的关键事实

- **原生子智能体烧额度是官方仓库已确认的已知问题**：openai/codex#13179（开启 subagents 后 PRO 每小时烧掉约 20% 周配额）、#9748（6 个并发子 Agent 瞬间清空 5 小时配额——子 Agent 启动时按推理时间预留配额，不是按实际用量）、superpowers#1152（Plus 用户单次 subagent 驱动开发直接耗尽 5 小时预算）。**"提醒后开一堆智能体把额度烧光"不是个人操作问题，是这类功能的已知行为。**
- Codex/ChatGPT/相关工具共享同一额度池；消耗与模型档位、推理强度、Fast Mode（约 2.5 倍速烧）相关。
- **AGENTS.md 是建议，hooks 是强制**（社区共识）：模型的指令服从有可测的失败率（论文级结论：指令层级可被绕过，Codex 官方也承认需要 hooks/沙箱等模型外层兜底）。Codex hooks 需 `[features] codex_hooks = true` 显式开启，本机 hooks 机制已验证可运行（SessionEnd 在用）。

### 本方案设定里的具体错误（按严重度）

1. **AGENTS.md「能并行的独立任务派子 Agent」在教 Codex 烧额度**：Codex 原生子 Agent 全部用 GPT 模型、吃 Plus 额度，且与"优先交给 Gemini"自相矛盾——模型看到两条冲突指令，被提醒分派时选择了开子 Agent 这条路。这是"一提醒反而烧光"的直接原因。
2. **指望模型自觉委派，机制上就不成立**：从模型视角，委派比直接干更贵（写任务包传上下文 + 等待 + 读结果 + 复核，全是主模型 token）。小任务它"理性地"不分派。成熟方案全部用程序强制（Aider 宿主代码 / 代理路由 / hooks / 显式命令）。
3. **下放对象选反了**："简单任务给下级"是最不划算的委派。真正省额度的是**重活下放**：要读大量内容的初筛、大批量机械改动、长文摘要——这些活 Codex 自己干时上下文 token 全记 GPT 账上。规则应改为"大范围调研下放，小查询直接干"。
4. **配置层加速烧额度**：`model_verbosity = "high"` + `model_reasoning_effort = "medium"` 全局生效，日常任务也在高输出档。建议建 profiles 分档（日常 low/medium，攻坚才 high）。

### 修正方案（按性价比排序）

1. **改 AGENTS.md 那句话（5 分钟，零成本）**：删除「能并行的独立任务派子 Agent」，替换为「能并行的独立调研/批量任务用 delegate_to_gemini 交给 Gemini；禁止 spawn Codex 原生子 Agent 并行跑任务（会成倍烧 Plus 额度）」。
2. **显式命令替代自动分派（立刻见效）**：不指望它自觉，由用户在需要时说「交给 Gemini 做：xxx」；或仿 Claude Code 建快捷指令。控制权在人，不赌模型。
3. **改分级规则措辞**：CLAUDE.md 与 AGENTS.md 同步——「1级：大范围调研（需读大量文件/网页的初筛）交 Gemini；单点小查询 Codex 直接干」。
4. **建 model profiles**：config.toml 加 profiles，日常任务用低推理+中输出，攻坚手动切高档。
5. **进阶可选 A（hooks 强制）**：UserPromptSubmit hook 注入路由提醒，或 PreToolUse hook 拦截子 Agent 生成类工具调用并提示改走 delegate_to_gemini。机械强制，但需要开发和调试。
6. **进阶可选 B（层级反转，最大节省）**：日常界面换成 Antigravity/Gemini CLI（当前五小时配额只用 2%），Codex 只在明确需要时被点名出场。GPT 额度从"默认每轮消耗"变"按需消耗"，比哄 Codex 下放省得多——因为总管自己每轮对话就在烧 GPT。参考 Isopolito/mcp 结构。
7. **数据验证**：PulseMeter 记录修正前后各一周的额度曲线，用数据决定是否继续投入进阶方案。

### 调研来源

- openai/codex#13179、#9748、#13186（子 Agent 与计量异常）
- musistudio/claude-code-router（36.9k star 代理路由）
- Aider architect 模式基准数据（aider.chat / aiwiki）
- psychofanPLAYS/gemini4codex-mcp（同构项目，1 star）
- Isopolito/mcp（Gemini 编排 + Codex/Claude 执行）
- codex-mcp-bridge npm（桥接开销自述）
- Codex hooks 机制（社区实践：AGENTS.md 建议 vs hooks 强制）

> 🧠 **声明**：以上「社区调研结论」一节由 WorkBuddy（小墨）于 2026-08-28 写入，其余章节为 Codex 会话维护。本块内容为 WorkBuddy 调研结论，非用户原话或原意，供 Claude Code/Codex 等其他模型识别，避免误删误当用户意图。
