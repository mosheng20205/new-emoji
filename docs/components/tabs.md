# Tabs 标签页

## 简介

`Tabs` 是纯 D2D 标签页组件，当前状态：**已完成**。

已覆盖默认线形、卡片、边框卡片、上/右/下/左四方向、表头左/中/右对齐、图标标签、禁用项、可关闭、可新增、editable、溢出滚动、键盘导航、标签内容区绘制、按索引/名称激活、状态读回、Python 封装、易语言命令文档和 `component_gallery.py` 桌面端完整样式演示。

## 样式与选项

| 选项 | 取值 |
|---|---|
| `tab_type` | `0` 线形，`1` 卡片，`2` 边框卡片 |
| `tab_position` | `0` 上，`1` 右，`2` 下，`3` 左 |
| `header_align` | `0` 左对齐，`1` 居中，`2` 右对齐 |
| `closable` | 是否显示标签关闭按钮 |
| `addable` | 是否显示新增按钮 |
| `editable` | 同时开启新增和关闭，适合多文档标签页 |
| `content_visible` | 是否由 Tabs 自身绘制当前标签内容区 |

扩展项目格式用于 `EU_SetTabsItemsEx`：

```text
标签\t名称\t内容\t图标\t禁用\t可关闭
```

多项用 `|` 或换行分隔。`禁用`、`可关闭` 使用 `0/1`、`true/false`、`是/否` 语义；未填写名称时会自动生成名称。

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateTabs` | 创建标签页，兼容旧的简单标签列表 |
| `EU_SetTabsItems` | 设置简单标签文本列表 |
| `EU_SetTabsItemsEx` | 设置扩展标签项：标签、名称、内容、图标、禁用、可关闭 |
| `EU_SetTabsActive` | 按索引激活标签 |
| `EU_SetTabsActiveName` | 按名称激活标签 |
| `EU_SetTabsType` | 设置线形/卡片/边框卡片 |
| `EU_SetTabsPosition` | 设置上/右/下/左位置 |
| `EU_SetTabsHeaderAlign` | 设置标签表头文本对齐：左/中/右 |
| `EU_SetTabsOptions` | 设置类型、可关闭、可新增 |
| `EU_SetTabsEditable` | 设置 editable 模式 |
| `EU_SetTabsContentVisible` | 设置是否绘制内容区 |
| `EU_AddTabsItem` | 新增标签 |
| `EU_CloseTabsItem` | 关闭标签 |
| `EU_SetTabsScroll` / `EU_TabsScroll` | 设置或增量滚动标签栏 |
| `EU_GetTabsActive` / `EU_GetTabsActiveName` | 读取当前激活索引或名称 |
| `EU_GetTabsHeaderAlign` | 读取标签表头文本对齐方式 |
| `EU_GetTabsItem` / `EU_GetTabsItemContent` | 读取标签文本或内容 |
| `EU_GetTabsFullState` / `EU_GetTabsFullStateEx` | 读取完整状态 |
| `EU_SetTabsChangeCallback` | 标签切换回调 |
| `EU_SetTabsCloseCallback` | 标签关闭回调 |
| `EU_SetTabsAddCallback` | 标签新增回调 |

## Python 使用

```python
tabs = ui.create_tabs_ex(
    hwnd, root,
    [
        {"label": "用户管理", "name": "users", "content": "👥 用户管理内容", "icon": "👥"},
        {"label": "配置管理", "name": "config", "content": "⚙️ 配置管理内容", "icon": "⚙️"},
        {"label": "角色管理", "name": "roles", "content": "🛡️ 角色管理内容", "icon": "🛡️"},
    ],
    active=1,
    tab_type=2,
    tab_position="left",
    closable=True,
    editable=True,
    content_visible=True,
    x=32, y=64, w=520, h=240,
)
ui.set_tabs_active_name(hwnd, tabs, "roles")
ui.set_tabs_header_align(hwnd, tabs, "center")
state = ui.get_tabs_full_state_ex(hwnd, tabs)
```

## 交互

- 鼠标点击标签切换，点击 `x` 关闭，点击 `+` 新增。
- 横向标签支持左右方向键，纵向标签支持上下方向键。
- `Home/End` 跳到首尾，`PageUp/PageDown` 滚动溢出标签。
- `Delete/Backspace` 关闭当前标签，`Insert/+` 新增标签。
- 禁用项不可激活；单项 `可关闭=0` 时不会响应关闭。

## 测试

优先运行：

```powershell
python tests/python/test_tabs_complete_components.py
```

该测试覆盖三种类型、四方向、表头对齐、扩展项目、按名称激活、内容读回、editable、增删回调、滚动和纵向键盘导航。
## Chrome 标签栏模式

`Tabs` 保留原通用标签页行为，并通过 `EU_SetTabsChromeMode(hwnd, element_id, 1)` 开启 Chrome 外壳绘制模式。

新增能力：

```text
EU_SetTabsChromeMode / EU_GetTabsChromeMode
EU_SetTabsItemIcon
EU_SetTabsItemLoading
EU_SetTabsItemPinned
EU_SetTabsItemMuted
EU_SetTabsItemClosable
EU_SetTabsItemChromeState / EU_GetTabsItemChromeState
EU_SetTabsChromeMetrics
EU_SetTabsNewButtonVisible
EU_SetTabsDragOptions
EU_SetTabsReorderCallback
```

Chrome 模式下支持圆角顶部标签、活动标签前置、固定标签、加载态、静音态、告警态和新建标签按钮。`detach_enabled` 当前只记录配置，不创建真实新窗口。
