# Tooltip 文字提示

`Tooltip` 已补齐用户示例中的 12 方位、dark/light、换行内容、disabled 状态和旧 placement 兼容能力。

## 扩展位置枚举

旧 API `EU_SetTooltipOptions` 的 `0左 / 1右 / 2上 / 3下` 保持兼容。新高级 API 使用 12 方位：

| 值 | 位置 |
|---|---|
| 0 | `top-start` 上左 |
| 1 | `top` 上 |
| 2 | `top-end` 上右 |
| 3 | `bottom-start` 下左 |
| 4 | `bottom` 下 |
| 5 | `bottom-end` 下右 |
| 6 | `left-start` 左上 |
| 7 | `left` 左 |
| 8 | `left-end` 左下 |
| 9 | `right-start` 右上 |
| 10 | `right` 右 |
| 11 | `right-end` 右下 |

## API

| API | 说明 |
|---|---|
| `EU_CreateTooltip` | 创建文字提示触发器 |
| `EU_SetTooltipContent` | 设置提示内容，支持换行 |
| `EU_SetTooltipOpen` / `EU_GetTooltipOpen` | 设置/读取打开状态 |
| `EU_SetTooltipOptions` / `EU_GetTooltipOptions` | 旧四方位兼容 API |
| `EU_SetTooltipBehavior` | 设置显示/隐藏延迟、触发方式和箭头 |
| `EU_SetTooltipAdvancedOptions` / `EU_GetTooltipAdvancedOptions` | 设置 12 方位、dark/light、disabled、箭头、offset、最大宽度 |
| `EU_TriggerTooltip` | 程序打开/关闭 |
| `EU_GetTooltipText` / `EU_GetTooltipFullState` | 文本和完整状态读回 |

## Python 示例

```python
tip = ui.create_tooltip(hwnd, root, "上左 📍", "📍 Top Left 提示文字", 2, 40, 80, 130, 36)
ui.set_tooltip_advanced_options(hwnd, tip,
                                placement="top-start",
                                effect="dark",
                                disabled=False,
                                show_arrow=True,
                                offset=8,
                                max_width=220)
```

禁用：

```python
ui.set_tooltip_advanced_options(hwnd, tip, placement="bottom", effect="light",
                                disabled=True, show_arrow=True,
                                offset=8, max_width=220)
```

## 测试

优先运行 `tests/python/test_tooltip_complete_components.py`。gallery 的 `Tooltip` 详情页展示 12 方位矩阵、深浅主题、多行提示和 disabled 切换。
