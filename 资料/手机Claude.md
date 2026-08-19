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
  modified: 2026-08-12T09:14:22.414Z
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

完整12步安装流程见 [[日志/2026-08-06-进度#14. 手机独立运行 Claude Code ✅]]

## 和PC端的差异

| | PC | 手机 |
|------|-----|------|
| 版本 | 最新版 | v2.1.112 |
| 记忆文件 | ✅ 全套 | 🟡 进行中（已打包，等安装） |
| 全局指令 | ✅ 完整 | 🟡 进行中（精简模板已就绪） |

## 记忆同步（2026-08-12 已落地）

**方案**：Git + GitHub SSH 443 端口（放弃旧 HTTP 服务方案）
- 仓库：`git@github.com:z15314102792-arch/second-brain.git`
- 手机 Termux 直接 `git clone` 到 `~/storage/shared/Documents/second-brain/`
- SSH 配置：`ssh -p 443 git@ssh.github.com`（防墙）
- 安装脚本：`sh scripts/phone-setup.sh`（一键建 `sy`/`ph` 命令）
- Obsidian App 打开 `Documents/second-brain` 作为库

### 日常使用

| 操作 | 怎么操作 |
|------|----------|
| 拉取最新笔记 | Termux → `sy` |
| 上传改动 | Termux → `ph` |
| 看/写笔记 | Obsidian App |
| 看关系图谱 | Obsidian 右下角图标 |

### 重要提醒

- Termux 本体操作，不要进 Ubuntu proot（proot 里创建的文件 App 看不到）
- `.obsidian/graph.json` 已从 git 追踪中移除（多设备冲突源）

## 相关

- [[仓库/免费Claude]] — PC 端也曾尝试过的免费方案
- [[资料/CCE模型]] — 多模型配置参考
