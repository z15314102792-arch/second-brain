# 第二大脑协同准则 (Multi-Agent Universal Guidelines)

> 本知识库是用户的唯一主知识库（Obsidian 库）。
> 适用于所有接入的 AI 助手：Claude Code、OpenAI Codex、Google Antigravity (Gemini)。

---

## 1. 核心索引与操作手册
- **总索引**：`[[MEMORY]]` (即 `E:\第二大脑\MEMORY.md`)
- **操作规则与规范**：`[[CLAUDE]]` (即 `E:\第二大脑\CLAUDE.md`)
- **核心分类维度**：
  - 🎯 `项目/`：正在做/做过的项目
  - 🧠 `知识/`：长期有效的结论、规则、教训
  - 🛠️ `技能/`：标准操作步骤与操作指南
  - 📚 `资料/`：工具配置、环境信息
  - 📅 `日志/`：每日进度记录（早报日报放 `日志/AI日报记录/`）
  - 💡 `灵感/`：未定点子
  - ✅ `待办/`：待办清单
  - 📦 `仓库/`：归档与历史备份
  - 🔐 `系统/`：敏感密钥（已被 .gitignore 拦截，绝不能外传）
  - 🗑️ `_垃圾站/`：废弃暂存

---

## 2. Frontmatter 与 Wikilink 规范
- 文件名一律采用 **中文命名**。
- 链接一律采用 **Obsidian Wikilink**：`[[路径/文件名]]`（不带 `.md` 后缀）。
- Frontmatter 顶层必须包含：
  ```yaml
  ---
  name: <英文slug>
  description: <一句话描述>
  tags: [标签1, 标签2]
  metadata:
    type: user | feedback | project | reference
    modified: <修改日期>
  ---
  ```

---

## 3. 多 Agent 协作与防冲突铁律
1. **先 pull 后写**：在准备写入任何笔记或提交前，先执行 `git pull origin master` 同步云端。
2. **日志一律追加**：编辑 `日志/当天日期-进度.md` 时采用追加（Append）模式，保留其他 Agent 已记录的成果。
3. **安全提交白名单**：禁止使用 `git add -A`，仅提交指定的知识库目录；`系统/` 目录严禁提交。