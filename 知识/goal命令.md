---
name: goal
description: /goal — Claude Code 自主执行命令，设目标后持续推进直到完成
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-11T07:52:02.368Z
  originSessionId: 3148f26d-3249-4f5e-9638-549b9116aa7c
---

# /goal — 自主执行命令

**用途**：设定一个目标，Claude Code 跨多轮对话自动推进，不停下来等确认，直到产出成品。

## 用法

```
/goal 完成螺丝消除的全部优化
/goal 把五子棋的AI难度提升到中级
/goal clear          ← 清除已有目标
```

## 相关

- [[/loop]] — 固定间隔循环执行
- [[/workflow]] — 多 Agent 并行编排
- [[/background]] — 后台持续运行
