---
name: project-star-moon-temple
description: 星月神殿（双人闯关） — v2.3，GitHub Pages 部署，关卡待修
metadata: 
  node_type: memory
  type: project
  path: C:\star-moon-temple
  github: z15314102792-arch/star-moon-temple
  url: https://z15314102792-arch.github.io/star-moon-temple/
  version: v2.3
  modified: 2026-08-06T06:14:38.551Z
  originSessionId: 6dd31fbb-2c41-49f3-808f-f0380c8b1198
---

# 星月神殿（双人闯关）

**版本**: v2.3
**状态**: 关卡待修（7月30日后无改动）

## 项目概况

- 灵感来源：森林冰火人（Fireboy & Watergirl），原创主题
- 技术：原生 JS + Canvas + PeerJS (WebRTC) + PWA，零框架依赖
- 部署：GitHub Pages

## 已实现功能

- WebRTC P2P 双人联机，权威主机模式 20Hz 同步
- 单人模式（可切换角色 晴阳/月影）
- CSS rotate 横屏 + 触摸坐标映射
- 6 个瓦片关卡（AABB 碰撞），固定视野缩放
- 教程提示系统（每关前 5 秒）
- 狼跳时间 (8 帧) + 跳跃缓冲 (10 帧)
- 17/18 单元测试通过

## 待办

| 优先级 | 事项 | 说明 |
|--------|------|------|
| 🔴 高 | 关卡可玩性验证 | 6 关均需在手机上实际通关测试 |
| 🔴 高 | 横屏实际效果 | CSS rotate 在 iOS Safari/微信浏览器表现待验证 |
| 🟡 中 | 教程系统验证 | 确认提示文字显示正确 |
| 🟡 中 | 关卡设计优化 | 参考原版调整难度曲线 |

## 注意

- 之前进度文件标记为"Railway 部署"，实际部署在 GitHub Pages
- 下次继续时首要任务：手机真机通关测试
