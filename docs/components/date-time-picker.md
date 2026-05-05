# DateTimePicker 日期时间选择器

## 简介

`DateTimePicker` 是 new_emoji 的日期时间选择组件。当前状态：**已完成**。

已补齐快捷选项、默认时间、日期时间区间模式、固定高度弹层、小时 0-23 全量列表、分钟长列表滚动、清空、快捷今天、快捷当前时间、日期时间范围夹取、区间分隔符、左右面板独立滚动、键盘选择、滚动位置读写、Python 封装和独立中文 emoji 验证。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateDateTimePicker` |
| 组件分类 | 日期时间 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_datetimepicker` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateDateTimePicker` | 创建日期时间选择器 |
| `EU_SetDateTimePickerDateTime` | 设置当前日期时间 |
| `EU_SetDateTimePickerRange` | 设置可选日期和时间范围 |
| `EU_SetDateTimePickerOptions` | 设置今天值、今天按钮、分钟步进和日期格式 |
| `EU_SetDateTimePickerOpen` | 打开或关闭弹层 |
| `EU_ClearDateTimePicker` | 清空当前日期时间 |
| `EU_DateTimePickerSelectToday` | 快捷选择今天 |
| `EU_DateTimePickerSelectNow` | 快捷选择当前时间 |
| `EU_SetDateTimePickerScroll` | 设置小时/分钟滚动位置 |
| `EU_GetDateTimePickerOpen` | 读取弹层打开状态 |
| `EU_GetDateTimePickerDateValue` | 读取当前日期 |
| `EU_GetDateTimePickerTimeValue` | 读取当前时间 |
| `EU_DateTimePickerMoveMonth` | 切换月份 |
| `EU_GetDateTimePickerRange` | 读取可选日期和时间范围 |
| `EU_GetDateTimePickerOptions` | 读取选项 |
| `EU_GetDateTimePickerScroll` | 读取小时/分钟滚动位置 |
| `EU_SetDateTimePickerShortcuts` | 设置弹层快捷选项 |
| `EU_SetDateTimePickerStartPlaceholder` | 设置区间开始占位符 |
| `EU_SetDateTimePickerEndPlaceholder` | 设置区间结束占位符 |
| `EU_SetDateTimePickerDefaultTime` | 设置单个默认时间，并同步到区间开始/结束默认时间 |
| `EU_SetDateTimePickerRangeDefaultTime` | 设置区间开始/结束各自的默认时间 |
| `EU_SetDateTimePickerRangeSeparator` | 设置区间开始/结束日期时间之间的分隔符 |
| `EU_SetDateTimePickerRangeSelect` | 启用并设置日期时间区间选择 |
| `EU_GetDateTimePickerRangeValue` | 读取日期时间区间值 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🗓️ 日期时间选择器示例", 240, 120, 960, 620)
root = ui.create_container(hwnd, 0, 0, 0, 920, 560)

picker = ui.create_datetimepicker(hwnd, root, 2026, 5, 1, 9, 0, 32, 56, 480, 42)
ui.set_datetimepicker_range_select(hwnd, picker, True, 20260501, 900, 20260510, 1800)
ui.set_datetimepicker_range_placeholders(hwnd, picker, "开始日期时间", "结束日期时间")
ui.set_datetimepicker_range_separator(hwnd, picker, " 至 ")
ui.set_datetimepicker_range_default_time(hwnd, picker, 9, 0, 18, 0)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- 组件已按封装计划补齐创建、绘制、主题、DPI、交互、Set/Get、Python 封装和独立中文 emoji 验证。
- 区间模式对齐 Element 官方 `datetimerange` 行为：左右日期/时间面板独立命中和滚动，结束侧滚轮不会回退触发开始侧滚动。
- 右侧结束日期面板的 overlay hit-test、右侧月份前进按钮和时间列滚动命中已补齐。
- 区间日期高亮按完整 `YYYYMMDD` 判断，不再把月份误当日期。
- 默认时间允许 `00:00`，并支持开始/结束各自默认时间。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行 `tests/python/test_datetimepicker_complete_components.py`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `DateTimePicker` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py` 和 `DLL命令/易语言DLL命令.md`。
