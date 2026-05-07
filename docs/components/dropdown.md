# Dropdown 下拉菜单

## 概述

`Dropdown` 已补齐 Element 风格的常见桌面端样式：文字链接、按钮、split-button、hover/click/manual、`hide_on_click`、图标、禁用、分割线、层级、`command` 回调和四种尺寸。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateDropdown` |
| 分类 | 导航 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_dropdown` / `set_dropdown_options` / `set_dropdown_item_meta` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateDropdown` | 创建下拉菜单 |
| `EU_SetDropdownItems` | 设置项目文本 |
| `EU_SetDropdownSelected` / `EU_GetDropdownSelected` | 读写当前选中项 |
| `EU_SetDropdownOpen` / `EU_GetDropdownOpen` | 读写打开状态 |
| `EU_SetDropdownDisabled` | 设置运行时禁用索引 |
| `EU_GetDropdownItemCount` | 读取项目数量 |
| `EU_GetDropdownState` | 读取选中项、数量、禁用数、层级和 hover 索引 |
| `EU_SetDropdownOptions` / `EU_GetDropdownOptions` | 读写触发模式、hide-on-click、split-button、按钮变体、尺寸和触发器样式 |
| `EU_SetDropdownItemMeta` / `EU_GetDropdownItemMeta` | 读写图标、command、分割线、禁用和层级元数据 |
| `EU_SetDropdownCommandCallback` | 点击启用项后回调 command；未设置 command 时回传显示文本 |
| `EU_SetDropdownMainClickCallback` | split-button 左侧主按钮回调 |

## 枚举

### 触发模式

| 值 | 含义 |
|---|---|
| `0` | 点击 |
| `1` | 悬停 |
| `2` | 手动 |

### 触发器样式

| 值 | 含义 |
|---|---|
| `0` | 按钮 |
| `1` | 文字链接 |

### 按钮变体

| 值 | 含义 |
|---|---|
| `0` | 默认 |
| `1` | 主色 |
| `2` | 成功 |
| `3` | 警告 |
| `4` | 危险 |
| `5` | 文本 |
| `6` | 信息 |

### 尺寸

| 值 | 含义 |
|---|---|
| `0` | 默认 |
| `1` | medium |
| `2` | small |
| `3` | mini |

## 项目文本语法

`EU_CreateDropdown` 和 `EU_SetDropdownItems` 仍兼容旧语法：

```text
📄 复制
> ✏️ 编辑
> !🗑️ 删除
```

规则：

- `>` 表示层级，每多一个 `>` 就再缩进一层。
- `!` 表示禁用项。
- `EU_SetDropdownItemMeta` 可继续叠加图标、command 和分割线。

## 元数据

`EU_SetDropdownItemMeta` 的三个输入都是按项目顺序对齐：

- `icons_utf8`：`|` 分隔的 UTF-8 图标文本
- `commands_utf8`：`|` 分隔的 UTF-8 command 文本
- `divided_indices`：需要显示分割线的项目索引数组

`EU_GetDropdownItemMeta` 会读回：

- `icon`
- `command`
- `divided`
- `disabled`
- `level`

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📂 Dropdown 演示", 240, 120, 1100, 760)
root = ui.create_container(hwnd, 0, 0, 0, 1040, 700)

items = [
    "📄 复制",
    "✏️ 编辑",
    "> !🗑️ 删除",
    "📤 导出",
]
dd = ui.create_dropdown(hwnd, root, "📂 更多菜单", items, 0, 34, 74, 220, 36)
ui.set_dropdown_options(hwnd, dd, trigger_mode=0, hide_on_click=False, split_button=False,
                        button_variant=1, size=0, trigger_style=0)
ui.set_dropdown_item_meta(
    hwnd, dd,
    ["📄", "✏️", "🗑️", "📤"],
    ["copy", "", "delete", "export"],
    [3],
)
ui.set_dropdown_open(hwnd, dd, True)
```

## 易语言调用

易语言侧使用中文命令名，右侧保持真实 `EU_` 导出名。例如：

```text
.DLL命令 创建下拉菜单, 整数型, "new_emoji.dll", "EU_CreateDropdown"
.DLL命令 设置下拉菜单选项, , "new_emoji.dll", "EU_SetDropdownOptions"
.DLL命令 设置下拉菜单项目元数据, , "new_emoji.dll", "EU_SetDropdownItemMeta"
```

`EU_SetDropdownCommandCallback` 的回调签名为 `子程序(元素ID, 选中索引, command字节集指针, command长度)`。

## 测试

- 优先运行 `tests/python/test_dropdown_complete_components.py`
- 图库页使用 `NEW_EMOJI_GALLERY_COMPONENT=Dropdown python examples/python/component_gallery.py`
- Dropdown 专属页要能完整展示文字链接、按钮、split-button、hover/click/manual、hide-on-click=false、图标、禁用、分割线、层级、长列表滚动和四种尺寸

## 文档维护

如果 `Dropdown` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`examples/python/component_gallery.py`、`tests/python/test_dropdown_complete_components.py` 和 `DLL命令/易语言DLL命令.md`。

## 通用 Popup 与组件绑定

`Dropdown` 除了自身 `click / hover / manual` 触发方式，也可以作为通用 Popup 被任意 Element 打开：

```text
EU_SetPopupAnchorElement
EU_SetPopupPlacement
EU_SetPopupOpen / EU_GetPopupOpen
EU_SetPopupDismissBehavior
EU_SetElementPopup
EU_ClearElementPopup
EU_GetElementPopup
```

典型右键菜单用法：创建一个 `Dropdown`，把自身 trigger 设为 manual，再通过 `EU_SetElementPopup(hwnd, panel_id, dropdown_id, 1)` 绑定到普通面板或按钮。触发时 Dropdown 会按锚点重新计算菜单位置，并参与外部点击和 Esc 关闭策略。
