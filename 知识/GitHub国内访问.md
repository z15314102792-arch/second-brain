---
name: github-china-access
description: GitHub 在国内网络不稳定——HTTPS经常被干扰，SSH走443端口是最稳方案
metadata: 
  node_type: memory
  tags: 
    - 踩坑
  type: reference
  modified: 2026-08-07T06:38:22.709Z
  originSessionId: 53099e30-6fac-4ddc-b8d1-0dd8bee1197a
---

# GitHub 国内访问

## 踩到的坑

在国内用 HTTPS 方式 push/pull GitHub 经常失败：
- `Could not resolve host: github.com`（DNS 污染）
- `Failed to connect to github.com:443`（TCP 被干扰）
- 时好时坏，和白名单/防火墙无关，是 GFW 层面的干扰

## 最佳方案：SSH over 443

GitHub 提供 `ssh.github.com`，SSH 走 443 端口（和网页浏览一样），GFW 眼里就是普通 HTTPS 流量。

### 1. SSH config

`~/.ssh/config`：
```
Host ssh.github.com
    HostName ssh.github.com
    Port 443
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

### 2. Git remote

所有仓库 remote 改为 SSH 格式：
```
git@ssh.github.com:用户名/仓库名.git
```

### 3. insteadOf 兜底

防止 Obsidian Git 插件或其他工具把 remote 改回 HTTPS：
```bash
git config --global url."git@ssh.github.com:z15314102792-arch/".insteadOf "https://github.com/z15314102792-arch/"
```

这样即使 remote 显示 HTTPS，Git 底层也会自动转成 SSH。

## 已应用此方案的仓库

| 仓库 | 路径 |
|------|------|
| second-brain | `C:\Users\Administrator\.claude\projects\C--\memory` |
| chinese-chess | `C:\chinese-chess` |
| gomoku | `C:\gomoku` |
| draw-and-guess | `C:\draw-and-guess` |
| animal-battle | `C:\animal-battle` |

## 为什么不用的方案

| 方案 | 问题 |
|------|------|
| Windows 防火墙白名单 | 不相关，干扰不在本地 |
| 改 hosts 文件 | GitHub IP 经常变，不可靠 |
| 代理/VPN | 额外开销，不值得为 git 专门开 |
| 国内镜像（Gitee） | 延迟同步，多一套管理 |
