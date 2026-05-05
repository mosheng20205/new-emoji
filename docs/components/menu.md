# Menu 菜单 / NavMenu 导航菜单

## 简介

`Menu` 是 new_emoji 的导航菜单组件。当前状态：**已完成**。

本组件已补齐 Element UI NavMenu 常用桌面端样式：横向默认、横向暗色/自定义色、纵向默认、纵向暗色/自定义色、多级子菜单、禁用项、分组标题、图标、链接项、侧栏展开/收起、激活路径读回、完整状态读回、选择回调、Python 封装、易语言命令文档和独立中文 emoji 验证。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateMenu` |
| 组件分类 | 导航 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_menu` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateMenu` | 创建菜单 |
| `EU_SetMenuItems` | 设置菜单项目，兼容 `>` 层级和 `!` 禁用标记 |
| `EU_SetMenuActive` / `EU_GetMenuActive` | 设置/读取激活项 |
| `EU_SetMenuOrientation` / `EU_GetMenuOrientation` | 设置/读取方向，`0` 水平、`1` 垂直 |
| `EU_SetMenuExpanded` | 设置展开的父菜单索引 |
| `EU_GetMenuItemCount` | 读取项目数量 |
| `EU_GetMenuState` | 读取激活项、项目数、方向、层级、可见数、展开数、悬停项 |
| `EU_GetMenuActivePath` | 读取当前激活路径 |
| `EU_SetMenuColors` / `EU_GetMenuColors` | 设置/读取背景、文字、激活文字、悬停背景、禁用文字和边框色 |
| `EU_SetMenuCollapsed` / `EU_GetMenuCollapsed` | 设置/读取垂直侧栏收起状态 |
| `EU_SetMenuItemMeta` / `EU_GetMenuItemMeta` | 设置/读取图标、分组、链接、目标和命令元数据 |
| `EU_SetMenuSelectCallback` | 菜单项被选择时回传索引、路径和命令 |

## 项目数据规则

- 文本项目继续使用 UTF-8 字节数组，多个项目用 `|` 或换行分隔。
- `>` 前缀表示子级，例如 `> 选项1`、`> > 选项1`。
- `!` 前缀表示禁用项，例如 `!消息中心` 或 `> !已停用模块`。
- `EU_SetMenuItemMeta` 的图标、链接、目标和命令同样用 `|` 分隔，按索引对应菜单项目；空项目保留空字段。
- 分组标题通过 `group_indices` 标记，分组项不可选，会在纵向菜单中以弱化标题显示。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🧭 导航菜单示例", 240, 120, 980, 640)
root = ui.create_container(hwnd, 0, 0, 0, 940, 580)

items = ["处理中心", "我的工作台", "> 选项1", "> 选项2", "!消息中心", "订单管理"]
menu = ui.create_menu(hwnd, root, items, active=0, orientation=0, x=32, y=40, w=720, h=48)
ui.set_menu_colors(hwnd, menu, 0xFF545C64, 0xFFFFFFFF, 0xFFFFD04B, 0xFF646E78, 0xFF9CA3AF, 0xFF545C64)
ui.set_menu_item_meta(
    hwnd, menu,
    icons=["🏠", "🧭", "📌", "📌", "💬", "🧾"],
    hrefs=["", "", "", "", "", "https://www.ele.me"],
    targets=["", "", "", "", "", "_blank"],
    commands=["center", "workspace", "opt1", "opt2", "message", "orders"],
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- 水平菜单使用下划线强调激活项，适合顶部工具栏和模块导航。
- 垂直菜单使用左侧激活条、层级缩进、箭头展开和分组标题，适合桌面软件侧边栏。
- `EU_SetMenuCollapsed` 只影响垂直菜单展示：收起后保留图标列并隐藏文字。
- 链接项保存 `href/target` 元数据，点击时会按系统默认浏览器打开链接；业务侧也可通过 `EU_GetMenuItemMeta` 自行处理。
- 菜单项选择回调优先返回 `command`；未设置命令时可使用显示文本和激活路径。

## 测试

优先运行：

```powershell
python tests/python/test_menu_complete_components.py
```

该测试覆盖横向/纵向、默认/暗色、多级、分组、禁用、链接元数据、收起侧栏、颜色 Set/Get、状态读回和中文 emoji 首屏显示。

## 文档维护

如果 `Menu` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py` 和 `DLL命令/易语言DLL命令.md`。
