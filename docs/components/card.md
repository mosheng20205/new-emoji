# Card 卡片

## 简介

`Card` 是 new_emoji 的原生卡片组件，当前状态：**全样式已完成**。

本组件按“原生卡片 + 子元素插槽”封装：Card 自身绘制背景、边框、圆角、阴影、标题、正文、列表、页脚和操作区；图片卡片、头部右侧按钮、复杂业务内容通过把 `Image`、`Text`、`Button` 等元素创建为 Card 子元素完成。

## 样式能力

- 基础卡片：标题、正文、圆角、边框和阴影。
- 无头卡片：标题为空时只显示正文或列表。
- 页脚操作：`EU_SetCardFooter` + `EU_SetCardActions`，点击后用 `EU_GetCardAction` 读取操作索引。
- 正文列表：`EU_SetCardItems` 设置列表，`EU_SetCardBodyStyle` 控制 `item_gap`、`item_padding_y` 和分割线。
- 图片卡片：设置 `body-style` padding 为 0，然后在 Card 内创建 `Image`、`Text`、`Button` 子元素。
- 插槽组合：Card 会绘制并命中子元素，适合头部右侧按钮、图片区域、桌面端审批卡、工单卡、资料卡等场景。
- 阴影模式：0 无阴影，1 始终显示，2 悬停显示。

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateCard` | 创建卡片，标题/正文使用 UTF-8 字节数组 |
| `EU_SetCardTitle` | 设置标题 |
| `EU_SetCardBody` | 设置正文 |
| `EU_SetCardFooter` | 设置页脚文字 |
| `EU_SetCardItems` | 设置列表项，使用 `|`、换行或制表符分隔 |
| `EU_GetCardItemCount` | 读取列表项数量 |
| `EU_SetCardActions` | 设置页脚操作项 |
| `EU_GetCardAction` | 读取最近点击的操作索引 |
| `EU_ResetCardAction` | 重置操作索引 |
| `EU_SetCardShadow` | 设置阴影模式 |
| `EU_SetCardOptions` / `EU_GetCardOptions` | 设置/读取阴影、悬停和操作项数量 |
| `EU_SetCardStyle` / `EU_GetCardStyle` | 设置/读取背景、边框、线宽、圆角和外层 padding |
| `EU_SetCardBodyStyle` / `EU_GetCardBodyStyle` | 设置/读取正文 padding、字号、列表间距、列表内边距和分割线 |

## Python 示例

```python
card = ui.create_card(hwnd, root, "🪪 卡片名称", "", 1, 30, 40, 420, 180)
ui.set_card_items(hwnd, card, ["📄 列表内容 1", "📄 列表内容 2", "📄 列表内容 3"])
ui.set_card_body_style(hwnd, card, 18, 12, 18, 12, 14.0, 18, 0, False)
ui.create_button(hwnd, card, "", "操作按钮", 318, 9, 82, 28, variant=5)

image_card = ui.create_image_card(
    hwnd, root, "demo.bmp", "🍔 好吃的汉堡", "2026-05-06 09:30", "操作按钮",
    1, 30, 250, 300, 220
)
```

`examples/python/component_gallery.py` 的 Card 详情页已经覆盖基础卡片、头部操作、列表 margin、列表 padding、图片卡片、阴影矩阵和桌面端业务卡片。

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，例如 `.DLL命令 设置卡片正文样式, ..., "EU_SetCardBodyStyle"`；DLL 入口名保持真实 `EU_` 导出名。

## 测试

优先运行：

```powershell
python tests/python/test_card_complete_components.py
python tests/python/test_data_display_core_complete_components.py
```

新增或修改 Card API 时，必须同步更新 `src/new_emoji.def`、Python ctypes/helper、`tests/python/test_new_emoji.py`、本组件文档、API 索引、易语言 DLL 命令和 `component_gallery.py`。
