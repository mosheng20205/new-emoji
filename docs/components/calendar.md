# Calendar 日历

## 简介

`Calendar` 是 new_emoji 的日期时间组件。当前状态：**已完成**。

本轮已补齐 Element UI Calendar 三类核心能力：基础日期绑定、自定义 `dateCell` 单元格内容/样式、`:range` 显示范围。组件仍然保持单 HWND + 纯 D2D/DirectWrite 绘制，emoji 通过 color font 原生渲染。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateCalendar` |
| 组件分类 | 日期时间 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_calendar` |
| 易语言命令 | `创建日历`，见 `DLL命令/易语言DLL命令.md` |

```python
cal = ui.create_calendar(hwnd, root, 2026, 5, 12, 36, 100, 360, 330)
```

## 日期绑定

| API | 说明 |
|---|---|
| `EU_SetCalendarDate` | 设置当前年月和选中日 |
| `EU_GetCalendarValue` | 读取当前选中日期，格式 `YYYYMMDD` |
| `EU_SetCalendarOptions` / `EU_GetCalendarOptions` | 设置/读取今天高亮日期和是否显示今天 |
| `EU_CalendarMoveMonth` | 上月/下月切换 |

Python helper：

```python
ui.set_calendar_date(hwnd, cal, 2026, 5, 12)
value = ui.get_calendar_value(hwnd, cal)
ui.calendar_move_month(hwnd, cal, 1)
```

## 可选范围与显示范围

`EU_SetCalendarRange` 和 `EU_SetCalendarDisplayRange` 语义不同：

| API | 用途 |
|---|---|
| `EU_SetCalendarRange(hwnd, id, min, max)` | 限制哪些日期可被点击选择；不改变日历展示结构 |
| `EU_SetCalendarDisplayRange(hwnd, id, start, end)` | 改变日历展示结构，对应 Element UI 的 `:range` |
| `EU_GetCalendarRange` | 读取可选范围 |
| `EU_GetCalendarDisplayRange` | 读取显示范围 |

`EU_SetCalendarDisplayRange(..., 0, 0)` 会恢复普通按月显示。显示范围启用时标题显示“起始 至 结束”，月份切换按钮隐藏；当前实现最多绘制连续 42 天，超过 42 天时显示前 42 天。

```python
ui.set_calendar_range(hwnd, cal, 20260505, 20260528)
ui.set_calendar_display_range(hwnd, cal, 20260504, 20260524)
print(ui.get_calendar_display_range(hwnd, cal))
```

## dateCell 自定义单元格

`EU_SetCalendarCellItems` 是 `dateCell slot` 的 C++ 等价能力。它不嵌入任意子 Element，而是用结构化元数据控制每个日期格的文本、emoji、badge、颜色和禁用态。

数据格式为 UTF-8 文本：每行一个日期，字段用 Tab 分隔。

```text
date=20260512	label=05-12	extra=会议	emoji=✔️	badge=会	bg=0xFFEAF2FF	fg=0xFF1989FA	border=0xFF1989FA	badge_bg=0xFF1989FA	badge_fg=0xFFFFFFFF	font_flags=1	disabled=0
```

支持字段：

| 字段 | 说明 |
|---|---|
| `date` | 必填，`YYYYMMDD` |
| `label` | 主标签，`label_mode=3` 时优先使用 |
| `extra` | 副文本 |
| `emoji` | 单元格内 emoji 或选中提示 |
| `badge` | 右下角小标签 |
| `bg` / `fg` / `border` | 该日期的背景、文字、边框色 |
| `badge_bg` / `badge_fg` | badge 背景和文字色 |
| `font_flags` | `1` 表示主标签加粗 |
| `disabled` | `1` 表示该日期不可点击 |

Python helper 可直接传 `dict` 列表：

```python
ui.set_calendar_visual_options(hwnd, cal, True, True, 3, True, 8.0)
ui.set_calendar_cell_items(hwnd, cal, [
    {"date": 20260512, "label": "05-12", "extra": "会议", "emoji": "✔️", "badge": "会",
     "bg": "0xFFEAF2FF", "fg": "0xFF1989FA", "border": "0xFF1989FA", "font_flags": 1},
    {"date": 20260518, "label": "05-18", "extra": "不可选", "emoji": "⛔", "disabled": 1},
])
items = ui.get_calendar_cell_items(hwnd, cal)
ui.clear_calendar_cell_items(hwnd, cal)
```

## 视觉选项与状态颜色

| API | 说明 |
|---|---|
| `EU_SetCalendarVisualOptions` | 设置标题栏、星期栏、标签模式、相邻月份日期、单元格圆角 |
| `EU_GetCalendarVisualOptions` | 读取视觉选项 |
| `EU_SetCalendarStateColors` | 设置选中、区间、今天、悬停、禁用、相邻日期颜色 |
| `EU_GetCalendarStateColors` | 读取状态颜色 |
| `EU_SetCalendarSelectedMarker` | 设置选中标记，例如 `✔️` |

`label_mode`：

| 值 | 说明 |
|---|---|
| `0` | 日号 |
| `1` | 月-日 |
| `2` | 年-月-日 |
| `3` | 优先使用自定义 `label` |

颜色传 `0` 表示使用主题默认值。

```python
ui.set_calendar_selected_marker(hwnd, cal, "✔️")
ui.set_calendar_state_colors(
    hwnd, cal,
    selected_bg=0xFF1989FA,
    selected_fg=0xFFFFFFFF,
    range_bg=0x332F80ED,
    today_border=0xFFE6A23C,
)
```

## 区间选择与回调

| API | 说明 |
|---|---|
| `EU_SetCalendarSelectionRange` | 设置区间选择起止值和启用状态 |
| `EU_GetCalendarSelectionRange` | 读取区间选择状态 |
| `EU_SetCalendarChangeCallback` | 日期变化回调 |

变化回调使用统一 `ElementValueCallback`：`element_id, value, range_start, range_end`。其中 `value` 是当前选中 `YYYYMMDD`，`range_start/range_end` 是当前区间选择值。

```python
def on_change(element_id, value, range_start, range_end):
    print("选中日期", value, "区间", range_start, range_end)

ui.set_calendar_change_callback(hwnd, cal, on_change)
```

## 键盘导航

日历获得焦点后支持：

| 按键 | 行为 |
|---|---|
| `←/→` | 前一天/后一天 |
| `↑/↓` | 上一周/下一周 |
| `Home/End` | 当前行第一天/最后一天 |
| `PageUp/PageDown` | 上月/下月 |

如果目标日期被可选范围或 `disabled=1` 限制，将不会选中。

## 易语言示例

易语言左侧命令名使用中文，右侧 DLL 入口名保持真实 `EU_` 导出名：

```text
.DLL命令 设置日历显示范围, , "new_emoji.dll", "EU_SetCalendarDisplayRange"
.DLL命令 设置日历单元格数据, , "new_emoji.dll", "EU_SetCalendarCellItems"
.DLL命令 设置日历视觉选项, , "new_emoji.dll", "EU_SetCalendarVisualOptions"
.DLL命令 设置日历状态颜色, , "new_emoji.dll", "EU_SetCalendarStateColors"
.DLL命令 设置日历选中标记, , "new_emoji.dll", "EU_SetCalendarSelectedMarker"
```

## 验证

优先运行：

```powershell
python tests/python/test_calendar_complete_components.py
python tests/python/test_new_emoji.py
$env:NEW_EMOJI_GALLERY_COMPONENT="Calendar"; python examples/python/component_gallery.py
```

Gallery 的 Calendar 专属页按桌面端工作台设计，包含左侧操作区、中间三种日历、右侧状态读回和底部样式矩阵。
