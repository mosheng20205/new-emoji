# Checkbox 复选框

## 简介

`Checkbox` 用于多选、权限配置、批量操作和 checklist 场景。当前状态：**已完成**。

已覆盖 Element 常见用法：普通复选、禁用态、半选态、独立边框样式、尺寸、原生 `CheckboxGroup`、按钮式 `CheckboxButton`、边框组、整组禁用、单项禁用、min/max 勾选限制、状态读回、变更回调、Python 封装、component_gallery 专页和独立中文 emoji 验证。

## 能力覆盖

| 能力 | 状态 |
|---|---|
| 普通 checked / unchecked | 已完成 |
| disabled / 选中且禁用 | 已完成，独立项走通用 enabled，组内项走 item disabled |
| indeterminate 半选 | 已完成 |
| CheckboxGroup 多选值列表 | 已完成 |
| min / max 勾选数量限制 | 已完成 |
| CheckboxButton 按钮样式 | 已完成，作为 CheckboxGroup 的 `style=1` |
| border 边框样式 | 已完成，独立项和组均支持 |
| medium / small / mini | 已完成，`size=1/2/3` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateCheckbox` | 创建独立复选框 |
| `EU_SetCheckboxChecked` / `EU_GetCheckboxChecked` | 设置/读取选中状态 |
| `EU_SetCheckboxIndeterminate` / `EU_GetCheckboxIndeterminate` | 设置/读取半选状态 |
| `EU_SetCheckboxOptions` / `EU_GetCheckboxOptions` | 设置/读取独立复选框 `border` 与 `size` |
| `EU_CreateCheckboxGroup` | 创建原生复选框组 |
| `EU_SetCheckboxGroupItems` | 设置组内项目 |
| `EU_SetCheckboxGroupValue` / `EU_GetCheckboxGroupValue` | 设置/读取选中 value 列表 |
| `EU_SetCheckboxGroupOptions` / `EU_GetCheckboxGroupOptions` | 设置/读取整组禁用、样式、尺寸、min/max |
| `EU_GetCheckboxGroupState` | 读取完整状态：已选数、项目数、禁用数、hover、press、focus、last_action |
| `EU_SetCheckboxGroupChangeCallback` | 设置选中变化回调 |

`CheckboxGroup` 的 items 文本格式为 UTF-8，每行一项，列用 Tab 分隔：

```text
显示文本<Tab>值<Tab>禁用(0/1)
```

选中值列表为 UTF-8 换行分隔 value。`style=0` 普通，`style=1` 按钮式，`style=2` 边框式；`size=0` 默认，`1` 中等，`2` 小型，`3` 超小。`max_checked=0` 表示不限制最大数量，`min_checked=0` 表示不限制最小数量。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("☑️ 复选框示例", 240, 120, 960, 560)
root = ui.create_container(hwnd, 0, 0, 0, 920, 500)

ui.create_checkbox(hwnd, root, "接收通知 🔔", True, 32, 40, 180, 36)
ui.create_checkbox(hwnd, root, "边框选项 📦", False, 232, 38, 160, 40, border=True, size=1)

ui.create_checkbox_group(
    hwnd, root,
    [("上海 🏙️", "上海", False), ("北京 🔒", "北京", True), ("深圳 🚀", "深圳", False)],
    ["上海"],
    style=1, size=2, min_checked=1, max_checked=2,
    x=32, y=110, w=520, h=36,
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 测试

优先运行 `tests/python/test_checkbox_complete_components.py`。该测试覆盖创建、checked/indeterminate、border/size、CheckboxGroup、按钮样式、边框样式、单项禁用、整组禁用、min/max、鼠标点击、键盘切换、回调、中文与 emoji 首屏展示。

## 文档维护

如果 `Checkbox` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
