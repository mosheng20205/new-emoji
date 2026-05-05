# Rate 评分 ⭐

## 简介

`Rate` 是纯 D2D 的评分组件，支持默认星级、半星、可清空、只读/禁用、三段颜色、Unicode/emoji 图标、显示文字、显示分数、自定义分数模板和评分变化回调。

当前状态：**已完成，已补齐 Element Plus Rate 常见样式能力**。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateRate` |
| 组件分类 | 表单输入 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_rate` |
| 易语言命令 | `创建评分` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateRate` | 创建评分组件 |
| `EU_SetRateValue` / `EU_GetRateValue` | 设置/读取整数评分 |
| `EU_SetRateValueX2` / `EU_GetRateValueX2` | 设置/读取半星值，实际评分乘以 2 |
| `EU_SetRateMax` / `EU_GetRateMax` | 设置/读取最大评分，范围 1-10 |
| `EU_SetRateOptions` / `EU_GetRateOptions` | 设置/读取可清空、半星、只读和显示状态 |
| `EU_SetRateTexts` | 兼容旧接口，设置低分/高分文案并控制旧式评分文字 |
| `EU_SetRateColors` / `EU_GetRateColors` | 设置/读取低/中/高三段颜色 |
| `EU_SetRateIcons` / `EU_GetRateIcons` | 设置/读取满分、空值、低/中/高分 Unicode 图标 |
| `EU_SetRateTextItems` | 设置每分对应文案，UTF-8 文本用换行分隔 |
| `EU_SetRateDisplayOptions` / `EU_GetRateDisplayOptions` | 设置/读取 `show-text`、`show-score`、文字颜色和分数模板 |
| `EU_SetRateChangeCallback` | 设置评分变化回调 |

## 样式能力

- 默认不区分颜色：不调用 `EU_SetRateColors` 时使用主题强调色。
- 区分颜色：调用 `EU_SetRateColors(low, mid, high)`，按 `<=40%`、`<=80%`、`>80%` 分段。
- 显示文字：调用 `EU_SetRateTextItems` 后，再用 `EU_SetRateDisplayOptions(show_text=1, show_score=0, ...)`。
- 表情图标：调用 `EU_SetRateIcons` 传入 Unicode/emoji，例如 `😊`、`😶`、`😟`、`🙂`、`🤩`。
- 禁用显示分数：调用 `EU_SetRateDisplayOptions(show_text=0, show_score=1, text_color, "{value}")`，再禁用元素。
- 半星：`EU_SetRateOptions(..., allow_half=1, ...)`，半星值使用 `EU_SetRateValueX2`。
- 自定义模板：模板支持 `{value}` 和 `{max}`，例如 `{value}/{max} 分`。

## Python 示例

```python
rate = ui.create_rate(hwnd, parent, "体验评分 ⭐", 4, 5, 30, 60, 520, 40)
ui.set_rate_colors(hwnd, rate, 0xFF99A9BF, 0xFFF7BA2A, 0xFFFF9900)
ui.set_rate_icons(hwnd, rate, full_icon="😊", void_icon="😶", low_icon="😟", mid_icon="🙂", high_icon="🤩")
ui.set_rate_text_items(hwnd, rate, ["很差 😟", "较差 🙁", "一般 🙂", "满意 😄", "惊喜 🤩"])
ui.set_rate_display_options(hwnd, rate, show_text=True, show_score=True, text_color=0xFFFF9900, score_template="{value}/{max} 分")
```

## 维护要求

修改 Rate API 时必须同步更新：

- `src/exports.h`
- `src/exports.cpp`
- `src/new_emoji.def`
- `examples/python/new_emoji_ui.py`
- `tests/python/test_new_emoji.py`
- `DLL命令/易语言DLL命令.md`
- `docs/api-index.md`
- `examples/python/component_gallery.py`
- `组件封装进度.md`
