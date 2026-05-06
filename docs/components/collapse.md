# Collapse 折叠面板

## 简介

`Collapse` 是 new_emoji 的数据展示组件。当前状态：**全样式已完成**。

已补齐 Element Plus 常见折叠面板样式：普通多展开、手风琴、自定义标题图标、右侧说明/图标、禁用项、展开动画、键盘操作、选项读回、状态 JSON、Python 封装和桌面端中文 emoji 演示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateCollapse` |
| 组件分类 | 数据展示 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_collapse` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateCollapse` | 创建折叠面板；旧项目格式 `标题:正文` 继续可用 |
| `EU_SetCollapseItems` | 设置项目，兼容旧格式和扩展格式 |
| `EU_SetCollapseItemsEx` | 设置扩展项目：每项 `标题<TAB>正文<TAB>标题图标<TAB>右侧说明<TAB>禁用(0/1)`，项目间建议用 `|` 分隔 |
| `EU_SetCollapseActive` / `EU_GetCollapseActive` | 兼容旧单激活项读写 |
| `EU_SetCollapseActiveItems` / `EU_GetCollapseActiveItems` | 多激活项读写，非手风琴模式可同时展开多个项目 |
| `EU_SetCollapseOptions` | 设置手风琴、是否允许再次点击折叠和禁用索引 |
| `EU_SetCollapseAdvancedOptions` | 在基础选项上增加动画开关 |
| `EU_GetCollapseOptions` | 读取手风琴、再次点击折叠、动画和禁用项数量 |
| `EU_GetCollapseItemCount` | 读取项目数量 |
| `EU_GetCollapseStateJson` | 读取完整状态 JSON，包含 `activeIndices`、`disabledIndices`、`items` 等 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📂 折叠面板 示例", 240, 120, 900, 620)
root = ui.create_container(hwnd, 0, 0, 0, 860, 560)

collapse_id = ui.create_collapse(
    hwnd, root,
    [
        ("一致性 Consistency", "与现实生活一致。\n界面结构一致。", "🎯", "已展开", 0),
        ("反馈 Feedback", "控制反馈。\n页面反馈。", "💬", "已展开", 0),
        ("效率 Efficiency", "简化流程。\n清晰明确。", "⚡", "可展开", 0),
    ],
    active=[0, 1],
    accordion=False,
    x=30, y=40, w=520, h=260,
)
ui.set_collapse_options(hwnd, collapse_id, accordion=False, allow_collapse=True)
print(ui.get_collapse_state_json(hwnd, collapse_id))

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- `accordion=False` 时，内部使用 `activeIndices` 集合，可同时展开多个项目。
- `accordion=True` 时，只保留一个激活项；旧 `EU_SetCollapseActive` 仍按单展开行为工作。
- 标题支持左侧 emoji/图标和右侧说明，正文支持显式换行并按内容计算展开高度。
- 禁用项会弱化显示，并跳过鼠标点击和键盘切换。
- 键盘支持方向键、Home/End 移动焦点，Enter/Space 切换展开状态。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行 `tests/python/test_collapse_complete_components.py`，并回归数据展示相关测试。

## 文档维护

如果 `Collapse` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py` 和 `DLL命令/易语言DLL命令.md`。
