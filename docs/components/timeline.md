# Timeline 时间线

## 简介

`Timeline` 是 new_emoji 的时间线组件，当前状态：**已完成**。

已覆盖基础时间线、正序/倒序、节点图标、节点类型、自定义颜色、大尺寸节点、顶部/底部时间戳、卡片式时间线、左侧/右侧/交替位置、Python 封装、易语言 DLL 命令和独立中文 emoji 验证。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateTimeline` |
| 组件分类 | 数据展示 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_timeline` |
| 易语言命令 | `创建时间线` |

## 项目数据格式

`EU_SetTimelineItems` / `EU_CreateTimeline` 使用 UTF-8 字节集，项目之间用 `|` 或换行分隔。

旧格式继续支持：

```text
时间<TAB>内容<TAB>类型<TAB>图标
```

新版完整格式：

```text
时间<TAB>内容<TAB>类型<TAB>图标<TAB>颜色<TAB>尺寸<TAB>时间位置<TAB>卡片标题<TAB>卡片正文
```

字段说明：

| 字段 | 说明 |
|---|---|
| 类型 | `0` 默认、`1` 成功、`2` 警告、`3` 错误 |
| 图标 | emoji 或普通文本；`el-icon-more` 会映射为 `⋯` |
| 颜色 | 支持 `#RRGGBB` 和 `0xAARRGGBB`，优先级高于类型色 |
| 尺寸 | `0` / `normal` 普通，`1` / `large` 大节点 |
| 时间位置 | `top` 顶部，`bottom` 底部；为空时继承组件默认值 |
| 卡片标题/正文 | 任一字段不为空时绘制为卡片式时间线项目 |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateTimeline` | 创建时间线 |
| `EU_SetTimelineItems` | 设置时间线项目 |
| `EU_SetTimelineOptions` | 设置基础选项：位置、是否显示时间 |
| `EU_GetTimelineItemCount` | 读取项目数量 |
| `EU_GetTimelineOptions` | 读取基础选项 |
| `EU_SetTimelineAdvancedOptions` | 设置高级选项：位置、显示时间、倒序、默认时间位置 |
| `EU_GetTimelineAdvancedOptions` | 读取高级选项 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🕒 时间线示例", 240, 120, 900, 620)
root = ui.create_container(hwnd, 0, 0, 0, 860, 560)

timeline_id = ui.create_timeline(hwnd, root, [
    {"timestamp": "2018-04-15", "content": "🎉 活动按期开始", "type": 1, "icon": "✅"},
    {"timestamp": "2018-04-13", "content": "🧾 通过审核", "type": 0, "icon": "📌"},
    {"timestamp": "2018-04-11", "content": "🚀 创建成功", "type": 0, "icon": "🚀"},
], 30, 70, 420, 220)

ui.set_timeline_advanced_options(
    hwnd, timeline_id,
    position=0,
    show_time=True,
    reverse=True,
    default_placement="top",
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。

## 测试

优先运行 `tests/python/test_timeline_complete_components.py`，该测试覆盖基础数量读回、倒序高级选项、自定义节点、卡片式项目和交替位置。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。
