---
name: windows-hover-scroll
description: Windows 11 鼠标滚轮在剪贴板历史、文件管理器等非活动窗口失效时，优先检查悬停滚动注册表 MouseWheelRouting
tags: [知识, Windows, 鼠标, 排障]
metadata:
  type: feedback
  modified: 2026-08-29
---

# Windows 悬停滚动

## 核心结论

Windows 11 中，如果鼠标滚轮在浏览器、桌面等活动窗口正常，但在剪贴板历史（Win+V）、文件管理器等非活动窗口或浮层窗口里失效，优先检查“悬停滚动”设置。

对应注册表位置：

- `HKCU\Control Panel\Desktop`
- 键名：`MouseWheelRouting`

常见取值：

- `0`：禁用悬停滚动，滚轮只滚动当前活动窗口。
- `2`：启用 Windows 11 默认悬停滚动，鼠标指针悬停在哪个窗口就滚动哪个窗口。

## 现象判断

典型表现：

- 剪贴板历史（Win+V）列表不能直接用滚轮滚动，只能拖右侧滚动条。
- 文件管理器在未点击聚焦时，鼠标悬停滚动无效。
- 浏览器、桌面或当前活动窗口滚轮正常。
- 换场景正常，说明鼠标硬件和基础滚轮功能大概率不是主因。

## 修复方式

优先把注册表值改回：

```text
HKCU\Control Panel\Desktop\MouseWheelRouting = 2
```

等效图形界面：

```text
设置 → 蓝牙和其他设备 → 鼠标 → 滚动 → 打开“将鼠标悬停在非活动窗口上时滚动它们”
```

修改后通常可即时生效；若仍未生效，注销或重启系统后再验证。

## 后续排查

如果 `MouseWheelRouting = 2` 后问题仍存在，再排查第三方鼠标增强软件、手势工具、虚拟 HID 设备或厂商驱动。本次案例中发现过腾讯虚拟 HID 鼠标设备（`MyAppsHidBus.sys`），但不是最终根因。
