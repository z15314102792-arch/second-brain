---
name: research-before-implement
description: 做任何功能前必须先调研市面上同类产品怎么做、有哪些坑
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b8d6970d-3e4b-42fc-b0ca-454a36ac521f
  modified: 2026-07-30T05:46:12.319Z
---

# 调研先行原则

**Why:** 用户在多次合作中发现，直接上手写代码会导致基础问题一犯再犯（如 CSS z-index 层级覆盖 Canvas、横屏检测用 `innerWidth > innerHeight` 而非 `matchMedia` 等）。这些问题在同类产品中早已有成熟的解决方案，不需要重新踩坑。

**How to apply:**
1. 接到需求后，先花时间搜索同类产品的实现方案、开源项目、技术文章
2. 了解常见的坑和最佳实践（如移动端横屏用 `screen.orientation` + `matchMedia` 而非 `innerWidth`）
3. 调研完再出方案，方案里写明参考了哪些资料
4. 方案确认后再写代码
5. 禁止跳过调研直接编码
