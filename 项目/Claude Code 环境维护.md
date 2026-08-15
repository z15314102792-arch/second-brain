---
name: claude-code-env-maintenance
description: Claude Code 环境维护——hook 中文乱码三重根因修复 + API 成本优化调研（中转选型/降本方案）
metadata: 
  node_type: memory
  type: project
  status: 稳定
  version: v1.2
  modified: 2026-08-15T18:20:00.000Z
---

# Claude Code 环境维护

> 版本 v1.2 · 2026-08-15

## v1.1 — 修复中文乱码

### 问题根因（三重叠加）

1. **hook 命令语法错误**：6 处 hook 命令写成 `PYTHONUTF8=1 python xxx.py`（Linux bash 写法），Windows 上 Claude Code 用 PowerShell 执行，PowerShell 把 `PYTHONUTF8=1` 当命令名，报"无法识别"，报错信息是 GBK 编码 → 被按 UTF-8 解读 → 界面显示乱码。
2. **python 不在 PATH**：系统 `python` 命令是 0 字节商店占位别名（`C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python.exe`），实际不可用。真 Python 3.13.14 由 workbuddy 管理，在 `C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe`。
3. **Python 默认 GBK 编解码**：Windows 中文系统下 Python 的 stdin/stdout/stderr 默认用 GBK，与 Claude Code 的 UTF-8 不匹配，中文输出/输入都会乱码或解析失败。

### 修复内容

1. **5 个 hook 脚本** 在 import 后加 UTF-8 强制（stdin/stdout/stderr 全部 `reconfigure(encoding="utf-8")`）：
   - `C:\Users\Administrator\.claude\hooks\claude-focus\hooks\token-guard.py`
   - `C:\Users\Administrator\.claude\hooks\claude-focus\hooks\verification-gate.py`
   - `C:\Users\Administrator\.claude\hooks\research-gate-pretool.py`
   - `C:\Users\Administrator\.claude\hooks\research-gate.py`
   - `C:\Users\Administrator\.claude\hooks\research-tracker.py`
2. **配置** `C:\Users\Administrator\.claude\settings.json`：6 处 hook 命令的 `PYTHONUTF8=1 python` 前缀去掉，改用 workbuddy Python 绝对路径。

### 验证结果

- settings.json 解析合法，无 PYTHONUTF8 残留，6 处命令全部绝对路径
- 5 个脚本 `py_compile` 通过
- 用 subprocess 模拟 Claude Code（UTF-8 管道 + 中文输入）调用 research-gate：正确拦截（exit 2），中文输出完整无乱码（乱码替换符 0 个）

### 注意事项

- **别用 `python` 命令**：PATH 里没有可用 Python，只能走 workbuddy 绝对路径。
- workbuddy 若升级/切换 Python 版本，`settings.json` 里的路径要同步更新。
- PowerShell 写 JSON 文件给 Python 读时，避免 `Set-Content -Encoding UTF8`（会加 BOM，Python 的 json.load 会报错）；用 Python 自己读写最稳。

---

## v1.2 — API 成本优化调研（纯咨询，无改动）

用户咨询「API 用不起，中转可不可行」。结论：**中转不解决根本问题**——便宜中转=逆向/掺假（CISPA 实测 45.83% 端点掉包），官方直通（OpenRouter）=官方同价不省钱。

### 现状与算账

- 用户用 Claude Code 内接 `deepseek-v4-pro`（官方直连 `api.deepseek.com/anthropic`），20 天 250 元 ≈ 375 元/月。
- 真 Claude 比 deepseek 贵 10-20 倍；Claude Max $100/月（725 元）嫌贵。
- deepseek 8/17 涨价：V4-Pro 高峰输出 6→27 元（4.5 倍），闲时 13.5 元。

### 配置现状（已查 settings.json，未改）

- Pro 做重活（主对话/opus/sonnet 档）、Flash 做轻活（haiku/子agent/小模型）——降档已配好。
- 缓存官方自动生效，但 Claude Code 动态前缀导致命中率低。

### 待办（下次继续）

- [ ] 用户试一周 `/compact` + 开新对话，看账单是否下降
- [ ] 若仍贵，帮准备「主对话降 Flash」配置（`ANTHROPIC_MODEL`/`ANTHROPIC_DEFAULT_SONNET_MODEL` → flash）
- [ ] 可选：错峰时间表（闲时输出便宜一半）

### 软文避雷名单

非线智能API、星链4SAPI、灵眸AI（LMU-AI=lmuai 同名 + 返利链接）均为自推软文，已剔除。
