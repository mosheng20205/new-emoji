# InputGroup 组合输入

## 简介

`InputGroup` 是本轮新增的原生组件，用来承接 Element 风格的 `prepend / append` 输入组合。

当前支持两侧附加项：

- 文本 `text`
- 按钮 `button`
- 选择器 `select`

内部会创建真实子元素，因此外部可以继续复用现有：

- `Input` 的 Set/Get 与文本回调
- `Button` 的点击回调
- `Select` 的选择状态与回调

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateInputGroup` |
| Python helper | `create_input_group(...)` |
| 组件分类 | 表单输入 |
| 当前状态 | 已完成 |

## 相关导出

### 创建与基础值

- `EU_CreateInputGroup`
- `EU_SetInputGroupValue`
- `EU_GetInputGroupValue`
- `EU_SetInputGroupOptions`
- `EU_GetInputGroupOptions`

### 两侧附加项

- `EU_SetInputGroupTextAddon`
- `EU_SetInputGroupButtonAddon`
- `EU_SetInputGroupSelectAddon`
- `EU_ClearInputGroupAddon`

### 内部元素 ID

- `EU_GetInputGroupInputElementId`
- `EU_GetInputGroupAddonElementId`

## 选项说明

`EU_SetInputGroupOptions(hwnd, id, size, clearable, password, show_word_limit, autosize, min_rows, max_rows)`

- `size`
  - `0` 默认
  - `1` medium
  - `2` small
  - `3` mini
- 其余输入选项与 `Input` 保持一致

## 附加项 side 约定

- `0`：`prepend`
- `1`：`append`

## Select 附加项数据格式

`EU_SetInputGroupSelectAddon` 的项目数据为 UTF-8 逐行文本：

```text
显示文本<Tab>值
显示文本<Tab>值
```

当前 `InputGroup` 主要使用其显示文本和选中索引来构造内部 `Select`。

## Python 示例

```python
import new_emoji_ui as ui

group_id = ui.create_input_group(
    hwnd,
    root,
    value="",
    placeholder="请输入内容 🔎",
    prepend={
        "type": "select",
        "items": [("餐厅名", "1"), ("订单号", "2"), ("用户电话", "3")],
        "selected": 0,
        "placeholder": "请选择",
    },
    append={
        "type": "button",
        "emoji": "🔎",
        "text": "",
        "variant": 1,
    },
    x=40, y=60, w=520, h=40,
)

input_id = ui.get_input_group_input_element_id(hwnd, group_id)
append_id = ui.get_input_group_addon_element_id(hwnd, group_id, 1)
```

## 对应示例与测试

- 图库：`examples/python/component_gallery.py` 的 `InputGroup` 专页
- 测试：
  - `tests/python/test_input_group_complete_components.py`
