# TimePicker 时间选择器

## 简介

`TimePicker` 是 new_emoji 的时间选择组件。当前状态：**已完成**。

已补齐弹层切换、步进、最小/最大时间范围、中文格式、长列表滚动、键盘列选择、箭头控制、时间区间选择、开始/结束占位符、区间分隔符、左右面板独立滚动、Python 封装和独立中文 emoji 验证。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateTimePicker` |
| 组件分类 | 日期时间 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_timepicker` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateTimePicker` | 创建时间选择器 |
| `EU_SetTimePickerTime` | 设置当前时间 |
| `EU_SetTimePickerRange` | 设置可选时间范围 |
| `EU_SetTimePickerOptions` | 设置分钟步进和显示格式 |
| `EU_SetTimePickerOpen` | 打开或关闭弹层 |
| `EU_SetTimePickerScroll` | 设置小时/分钟滚动位置 |
| `EU_GetTimePickerOpen` | 读取弹层打开状态 |
| `EU_GetTimePickerValue` | 读取当前时间 |
| `EU_GetTimePickerRange` | 读取可选时间范围 |
| `EU_GetTimePickerOptions` | 读取分钟步进和显示格式 |
| `EU_GetTimePickerScroll` | 读取小时/分钟滚动位置 |
| `EU_SetTimePickerArrowControl` | 设置箭头控制模式 |
| `EU_GetTimePickerArrowControl` | 读取箭头控制模式 |
| `EU_SetTimePickerRangeSelect` | 启用并设置时间区间选择 |
| `EU_SetTimePickerStartPlaceholder` | 设置区间开始占位符 |
| `EU_SetTimePickerEndPlaceholder` | 设置区间结束占位符 |
| `EU_SetTimePickerRangeSeparator` | 设置区间开始/结束时间之间的分隔符 |
| `EU_GetTimePickerRangeValue` | 读取时间区间值 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("⏰ 时间选择器示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)

picker = ui.create_timepicker(hwnd, root, 9, 0, 32, 56, 320, 42)
ui.set_timepicker_range_select(hwnd, picker, True, 900, 1800)
ui.set_timepicker_range_placeholders(hwnd, picker, "开始时间", "结束时间")
ui.set_timepicker_range_separator(hwnd, picker, " 至 ")

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- 组件已按封装计划补齐创建、绘制、主题、DPI、交互、Set/Get、Python 封装和独立中文 emoji 验证。
- 区间模式对齐 Element 官方 `is-range` 行为：开始/结束时间各自命中和滚动，结束侧滚轮不会回退触发开始侧滚动。
- 开始值不能晚于结束值，结束值不能早于开始值；非法候选项禁用而不是交换值。
- `00:00` 可作为有效区间值，不再被当作空占位。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行 `tests/python/test_timepicker_complete_components.py`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `TimePicker` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py` 和 `DLL命令/易语言DLL命令.md`。
