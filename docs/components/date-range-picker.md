# DateRangePicker 日期范围选择器

## 简介

`DateRangePicker` 是 new_emoji 的 日期时间 组件。当前状态：**已完成**。

双面板日历布局：左面板选择开始日期、右面板选择结束日期，一次操作完成范围选择。支持快捷选项、自定义占位符、分隔符、禁用日期回调。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateDateRangePicker` |
| 组件分类 | 日期时间 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_date_range_picker` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateDateRangePicker` | 创建双面板日期范围选择器 |
| `EU_SetDateRangePickerValue` | 设置起止日期 |
| `EU_GetDateRangePickerValue` | 获取起止日期 |
| `EU_SetDateRangePickerRange` | 设置可选日期范围（min/max） |
| `EU_SetDateRangePickerPlaceholders` | 设置开始/结束占位符 |
| `EU_SetDateRangePickerSeparator` | 设置区间分隔符文本 |
| `EU_SetDateRangePickerFormat` | 设置日期格式（0=默认 1=中文） |
| `EU_SetDateRangePickerAlign` | 设置文本对齐（0/1/2） |
| `EU_SetDateRangePickerShortcuts` | 设置弹层快捷选项 |
| `EU_SetDateRangePickerDisabledDateCallback` | 设置禁用日期回调 |
| `EU_SetDateRangePickerOpen` | 设置弹层开关 |
| `EU_GetDateRangePickerOpen` | 获取弹层状态 |
| `EU_DateRangePickerClear` | 清空选择 |

## Python 使用

```python
import sys
sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📅 日期范围选择器 示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
ui.create_date_range_picker(hwnd, root, 20260501, 20260510, 30, 40, 360, 42)
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。

## 文档维护

如果 `DateRangePicker` 新增、删除、重命名或修改 API，必须同步更新本文件、`DLL命令/易语言DLL命令.md`、`examples/python/new_emoji_ui.py`。
