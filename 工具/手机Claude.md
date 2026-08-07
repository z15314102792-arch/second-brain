---
name: 手机Claude
description: 红米K70至尊版独立运行Claude Code，Termux+proot+Ubuntu，DeepSeek API
metadata: 
  node_type: memory
  type: project
  device: 红米K70至尊版（天玑9300+ / 16GB / Android 14 + HyperOS）
  created: 2026-08-06
  status: 运行中
  originSessionId: be80e689-330f-4a06-b20e-796308e39605
  modified: 2026-08-07T12:22:49.846Z
---

## 架构

```
Android 手机
  └── Termux (终端模拟器)
        └── proot-distro Ubuntu (完整Linux环境+glibc)
              └── Node.js v22 (via nvm)
                    └── Claude Code v2.1.112 (npm)
                          └── DeepSeek V4-Pro[1m] API
```

不依赖 PC，手机独立运行。

## 关键版本

| 组件 | 版本 | 为什么选这个 |
|------|------|------------|
| Claude Code | **v2.1.112** | 纯JS，ARM64不崩，支持ANTHROPIC_BASE_URL |
| Node.js | v22 | nvm管理 |
| proot-distro | latest | 提供glibc环境 |
| Termux | v0.118.3 | F-Droid版，非Play版 |

**不能升级 Claude Code**：v2.1.112 不会自动更新，这正是我们要的。v1.0.51+ 在ARM64上必崩。

## API 配置

- **Endpoint**：`https://api.deepseek.com/anthropic`（DeepSeek官方Anthropic兼容端点）
- **Key**：`sk-...`（独立Key，和PC分开计费，完整Key存于GitHub Secrets DEEPSEEK_KEY）
- **主模型**：`deepseek-v4-pro[1m]`
- **快速模型**：`deepseek-v4-flash`

## 启动方式

打开 Termux：
```bash
proot-distro login ubuntu  # 进入Ubuntu
claude                      # 启动Claude Code
```

卡顿时可切快速模型：`/model deepseek-v4-flash`

## 已配置权限

`/permissions` → 允许所有（`*`），自动执行不询问。

## 安装记录

完整12步安装流程见 [[存档/2026-08-06-进度#14. 手机独立运行 Claude Code ✅]]

## 和PC端的差异

| | PC | 手机 |
|------|-----|------|
| 版本 | 最新版 | v2.1.112 |
| 记忆文件 | ✅ 全套 | 🟡 进行中（已打包，等安装） |
| 全局指令 | ✅ 完整 | 🟡 进行中（精简模板已就绪） |

## 记忆同步（2026-08-07）

**方案**：PC 端 HTTP 服务（端口3456）→ 手机端 curl 一键安装
- 安装包：`C:\tmp\phone-http\phone-memory-sync.tar.gz`（22个.md文件，27KB）
- 安装脚本：`C:\tmp\phone-http\phone-setup.sh`
- CLAUDE.md 精简模板：`知识/手机端CLAUDE模板.md`
- 启动服务：双击 `C:\tmp\phone-http\start-server.bat`（端口3456，已验证防火墙放行）

**精简规则**：保留语言/自测/沟通，移除 Agent分派/调研先行/版本标示/会话存档/编码自查

## 待做

- [ ] 完成记忆同步安装（用户启动 bat → 手机 curl）
- [ ] 验证：文件数=22、CLAUDE.md 存在、claude 启动列出项目
- [ ] 每次 PC 端记忆更新后同步到手机（需建立自动流程）

## 相关

- [[工具/废弃/免费Claude]] — PC 端也曾尝试过的免费方案
- [[工具/CCE模型]] — 多模型配置参考
