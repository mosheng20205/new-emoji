# Calendar 日历

## 简介

`Calendar` 是 new_emoji 的 日期时间 组件。当前状态：**已完成**。

已补月份切换、日期值读取、限制范围、区间选择、禁用日期、今天高亮、键盘导航、Python 封装和独立中文 emoji 验证

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateCalendar` |
| 组件分类 | 日期时间 |
| Python helper | `tests/python/test_new_emoji.py` 中的 `create_calendar` 或同类 helper |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateCalendar` | 当前组件相关导出 |
| `EU_GetCalendarOptions` | 当前组件相关导出 |
| `EU_GetCalendarRange` | 当前组件相关导出 |
| `EU_GetCalendarSelectionRange` | 当前组件相关导出 |
| `EU_GetCalendarValue` | 当前组件相关导出 |
| `EU_SetCalendarDate` | 当前组件相关导出 |
| `EU_SetCalendarOptions` | 当前组件相关导出 |
| `EU_SetCalendarRange` | 当前组件相关导出 |
| `EU_SetCalendarSelectionRange` | 当前组件相关导出 |

## Python 使用

```python
import sys

sys.path.insert(0, "tests/python")
import test_new_emoji as ui

hwnd = ui.create_window("✨ 日历 示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
# 请根据 `tests/python/test_new_emoji.py` 中的 helper 创建 `Calendar`。
# 示例界面文案应使用中文，并在标题、按钮或核心内容中加入 emoji。
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。

## 状态与交互

- 组件已按封装计划补齐创建、绘制、主题、DPI、交互、Set/Get、Python 封装和独立中文 emoji 验证。
- 修改组件行为时，需要同步检查 hover、pressed、focus、keyboard、disabled、selected、popup、scroll 等相关状态。
- 涉及回调、状态读回或数据模型变化时，应更新对应独立测试文件。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行对应完整测试文件，例如 `tests/python/test_calendar_complete_components.py`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `Calendar` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`tests/python/test_new_emoji.py` 和 `DLL命令/易语言DLL命令.md`。
