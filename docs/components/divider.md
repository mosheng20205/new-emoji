# Divider 分割线

## 简介

`Divider` 是 new_emoji 的基础/布局组件。当前状态：**已完成**。

本轮已补齐 Element 风格常用分割线样式：默认横线、横向文字左/中/右、图标/emoji 内容、竖向分割线、实线/虚线/点线/双线、颜色、线宽、外边距、文本间隙、读回、Python 封装、易语言命令和 `component_gallery.py` 桌面端全样式演示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateDivider` |
| 组件分类 | 基础/布局 |
| Python helper | `create_divider` |
| 易语言命令 | `创建分割线` |

## 样式能力

| 能力 | 说明 |
|---|---|
| 方向 | `0` 横向，`1` 纵向 |
| 内容位置 | `0` 左/上，`1` 居中，`2` 右/下 |
| 线型 | `0` 实线，`1` 虚线，`2` 点线，`3` 双线 |
| 内容 | 可单独显示 emoji 图标，也可显示“图标 + 文本” |
| 间距 | `margin` 控制线条两端外边距，`gap` 控制文本与线条间隙 |
| 兼容性 | 旧 `dashed=True` 自动映射为线型 `1`，旧调用无需迁移 |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateDivider` | 创建分割线，传入 UTF-8 文本、方向、文本位置和逻辑尺寸 |
| `EU_SetDividerOptions` | 设置方向、文本位置、颜色、线宽、兼容虚线和文本 |
| `EU_GetDividerOptions` | 读回方向、文本位置、颜色、线宽和兼容虚线状态 |
| `EU_SetDividerSpacing` | 设置线条外边距和文本间隙 |
| `EU_GetDividerSpacing` | 读回线条外边距和文本间隙 |
| `EU_SetDividerLineStyle` | 设置线型：实线/虚线/点线/双线 |
| `EU_GetDividerLineStyle` | 读回线型 |
| `EU_SetDividerContent` | 设置图标/emoji 与文本内容 |
| `EU_GetDividerContent` | 读回图标/emoji 与文本内容 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("➗ 分割线示例", 240, 120, 920, 650)
root = ui.create_container(hwnd, 0, 0, 0, 880, 590)

divider = ui.create_divider(hwnd, root, "少年包青天", 0, 0, 40, 96, 760, 36)
ui.set_divider_options(hwnd, divider, 0, 0, 0xFF409EFF, 1.5, False, "少年包青天")
ui.set_divider_content(hwnd, divider, "⚖️", "少年包青天")
ui.set_divider_spacing(hwnd, divider, margin=18, gap=12)

phone = ui.create_divider(hwnd, root, "", 0, 1, 40, 150, 760, 36)
ui.set_divider_options(hwnd, phone, 0, 1, 0xFF67C23A, 2.0, False, "")
ui.set_divider_content(hwnd, phone, "📱", "")

dotted = ui.create_divider(hwnd, root, "点线", 0, 1, 40, 204, 760, 36)
ui.set_divider_line_style(hwnd, dotted, 2)
ui.set_divider_content(hwnd, dotted, "✨", "点线")

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，例如 `创建分割线`、`设置分割线线型`、`设置分割线内容`；DLL 入口名保留真实 `EU_` 导出名，确保绑定到 `new_emoji.def`。

## 测试与演示

- 独立验证：`tests/python/test_divider_complete_components.py`
- 组件画廊：运行 `examples/python/component_gallery.py`，并设置 `NEW_EMOJI_GALLERY_COMPONENT=Divider` 可直接打开分割线全样式页。
- 修改 Divider API 时必须同步检查：C++ 导出、`.def`、Python ctypes/helper、`test_new_emoji.py`、易语言 DLL 命令、组件文档、API 索引、组件 README、组件 manifest 和画廊演示。

## DPI 与首次窗口尺寸

示例窗口和容器均使用逻辑尺寸。新增或调整演示时，窗口宽高与容器尺寸必须覆盖首屏所有分割线样式，并保留至少 20px 逻辑余量。
