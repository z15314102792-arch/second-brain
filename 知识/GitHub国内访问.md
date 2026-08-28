---
name: github-china-access
description: GitHub 国内访问——HTTPS全被墙，remote统一用 git@github.com（SSH config自动走443），禁止直接用 git@ssh.github.com
tags: [踩坑]
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-13T02:55:22.897Z
  originSessionId: 53099e30-6fac-4ddc-b8d1-0dd8bee1197a
---

# GitHub 国内访问

## 踩到的坑

在国内用 Git 访问 GitHub 经常失败，原因都在 GFW（防火墙）层面：

| 错误信息 | 原因 |
|----------|------|
| `Could not resolve host: github.com` | DNS 污染 |
| `Failed to connect to github.com:443` | TCP 被干扰（HTTPS 端口） |
| `ssh: connect to host github.com port 22: Connection timed out` | SSH 22 端口被墙 |
| `fatal: unable to access 'https://github.com/...': The requested URL returned error: 403` | HTTPS 认证被干扰 |

**关键认知**：只有 `ssh.github.com:443` 是通的。GitHub 官方提供这个地址就是为了绕过防火墙——SSH 流量走 HTTPS 端口，GFW 看起来就是普通网页浏览。

## 最终方案：Host github.com → ssh.github.com:443

**核心思路**：让 `github.com` 这个 Host 名直接指向 `ssh.github.com:443`，这样所有 `git@github.com:...` 格式的 SSH 地址自动走 443 端口，不需要任何 git remote 改写。

### SSH config（最终版本）

`C:\Users\Administrator\.ssh\config`：
```
Host github.com
    HostName ssh.github.com
    Port 443
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

### 为什么这个配置比旧版好

旧版配置（已废弃）：
```
Host ssh.github.com        ← 单独定义一个 ssh.github.com Host
    HostName ssh.github.com
    Port 443
    ...
```
旧版的问题：需要把每个仓库的 remote 从 `git@github.com:...` 改成 `git@ssh.github.com:...`，或者用 `insteadOf` 做 URL 改写。多了两个容易出错的地方。

新版只需一条 SSH config，什么都不用改：
- remote 保持 `git@github.com:z15314102792-arch/second-brain.git` 不动
- SSH 看到目标 Host 是 `github.com`，自动走 `ssh.github.com:443`
- 新仓库 clone 时直接用 `git@github.com:...` 格式，自动走 443

### 不需要 insteadOf

旧版需要 `git config --global url."git@ssh.github.com:".insteadOf "https://github.com/"` 来做 URL 改写。新版不需要——只要 remote 是 SSH 格式（`git@github.com:...`），SSH config 自动处理。HTTPS 格式的 remote 依然会被墙，但可以直接 `git remote set-url origin git@github.com:...` 改成 SSH。

### 验证命令

```bash
# 测试 SSH 连通性
ssh -T git@github.com
# 应该输出: Hi z15314102792-arch! You've successfully authenticated...

# 测试 git 操作
git push --dry-run
# 应该输出: Everything up-to-date
```

## 加密墙原理（给不是搞技术的人）

| 端口 | 用途 | 被墙？ | 为什么 |
|------|------|--------|--------|
| github.com:443 | HTTPS | ✅ 经常被墙 | GFW 会主动干扰 GitHub 的 HTTPS |
| github.com:22 | SSH | ✅ 被墙 | GFW 封锁 SSH 默认端口 |
| **ssh.github.com:443** | SSH over HTTPS | ❌ 通 | GFW 以为是普通网页，不拦 |

简单理解：GFW 是个门卫，拦下了 GitHub 的 HTTPS 和 SSH 端口，但 `ssh.github.com:443` 伪装成了普通网页流量，门卫看不出来就放行了。

## SSH 密钥安全提醒

**私钥（`id_ed25519`，没有 `.pub` 后缀）绝对不能暴露。** 它等同于你的 GitHub 密码。

私钥文件位置：`C:\Users\Administrator\.ssh\id_ed25519`
公钥文件位置：`C:\Users\Administrator\.ssh\id_ed25519.pub`（可以公开）

> ⚠️ 2026-08-11 曾因 VS Code 误选中导致私钥泄露到对话上下文，已重新生成密钥对。详见 [[日志/2026-08-11-进度]]。

## 已应用此方案的仓库（2026-08-13 全盘检测后补全）

| 仓库 | 路径 | remote 格式 |
|------|------|-------------|
| second-brain | `E:\第二大脑` | `git@github.com:z15314102792-arch/second-brain.git` |
| chinese-chess | `E:\项目\chinese-chess` | `git@github.com:z15314102792-arch/chinese-chess.git` |
| gomoku | `E:\项目\gomoku` | `git@github.com:z15314102792-arch/gomoku.git` |
| draw-and-guess | `E:\项目\draw-and-guess` | `git@github.com:z15314102792-arch/draw-and-guess.git` |
| screw-jam | `E:\项目\screw-jam` | `git@github.com:z15314102792-arch/screw-jam.git` |
| animal-battle | `E:\项目\animal-battle` | `git@github.com:z15314102792-arch/animal-battle.git` |
| cc-web | `E:\项目\cc-web` | `git@github.com:z15314102792-arch/cc-web.git` |
| star-moon-temple | `E:\项目\star-moon-temple` | `git@github.com:z15314102792-arch/star-moon-temple.git` |
| free-claude-code | `E:\项目\free-claude-code` | `git@github.com:z15314102792-arch/free-claude-code.git` |
| dashboard | `E:\项目\dashboard` | `git@github.com:z15314102792-arch/dashboard.git` |

## 2026-08-13 全盘检测的补充结论

全盘扫描 9 个项目的 git 仓库，发现三类 remote 错误，已全部修复：

| 错误类型 | 现象 | 修复 |
|----------|------|------|
| remote 指向错误仓库 | chinese-chess 的 remote 指到了 animal-battle | `remote set-url` 改回 |
| remote 用 `git@ssh.github.com` | host key 验证失败 | 改回 `git@github.com`（SSH config 自动走 443） |
| remote 用 HTTPS | `Empty reply from server` / `Could not connect to github.com:443` | 改回 SSH |

**关键结论**：
1. **remote 一律用 `git@github.com:...` 格式**，SSH config 会自动走 443 端口
2. **不要直接写 `git@ssh.github.com:...`**——绕过了 SSH config 的 Host 匹配，会 host key 验证失败
3. **HTTPS 格式（`https://github.com/...`）全部被墙**，一个都不能用
4. 标准 `git@github.com` 在配置了 SSH config 后完全可用（本次 9 个项目全部验证通过）

## 为什么不用的方案

| 方案 | 问题 |
|------|------|
| Windows 防火墙白名单 | 不相关，干扰不在本地 |
| 改 hosts 文件 | GitHub IP 经常变，不可靠 |
| 代理/VPN | 额外开销，不值得为 git 专门开 |
| 国内镜像（Gitee） | 延迟同步，多一套管理 |
| HTTPS + Personal Access Token | 和 HTTPS 一样被墙，没有区别 |
| `insteadOf` URL 改写 | 旧方案需要，新 SSH config 后不需要了 |
