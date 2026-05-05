# Input 输入框

## 简介

`Input` 是 `new_emoji` 的原生输入组件，当前已补齐 Element 风格常用能力：

- 单行 / 多行输入
- `placeholder`
- `prefix` / `suffix` 文本
- `prefix_icon` / `suffix_icon`
- `clearable`
- `password` + 密码显隐按钮
- `show_word_limit`
- `maxlength`
- `Ctrl+A` 全选、鼠标拖动选中文字
- 右键菜单，可通过 `EU_SetInputContextMenuEnabled` 开关
- `size`：`0默认 / 1中等 / 2小型 / 3超小`
- `autosize`、`min_rows`、`max_rows`
- `readonly`、校验态、文本变化回调

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateInput` |
| Python helper | `create_input(...)` |
| 组件分类 | 表单输入 |
| 当前状态 | 已完成 |

## 相关导出

### 创建

- `EU_CreateInput`

### 基础值与状态

- `EU_SetInputValue`
- `EU_GetInputValue`
- `EU_SetInputPlaceholder`
- `EU_SetInputClearable`
- `EU_SetInputOptions`
- `EU_GetInputState`
- `EU_SetInputMaxLength`
- `EU_GetInputMaxLength`
- `EU_SetInputTextCallback`
- `EU_SetInputSelection`
- `EU_GetInputSelection`
- `EU_SetInputContextMenuEnabled`
- `EU_GetInputContextMenuEnabled`

### 前后缀与视觉扩展

- `EU_SetInputAffixes`
- `EU_SetInputIcons`
- `EU_GetInputIcons`
- `EU_SetInputVisualOptions`
- `EU_GetInputVisualOptions`

## 视觉选项

`EU_SetInputVisualOptions(hwnd, id, size, show_password_toggle, show_word_limit, autosize, min_rows, max_rows)`

- `size`
  - `0` 默认
  - `1` medium
  - `2` small
  - `3` mini
- `show_password_toggle`
  - 仅在 `password=1` 时显示眼睛按钮
- `show_word_limit`
  - 显示 `当前长度/最大长度`
- `autosize`
  - 仅对 `multiline=1` 生效
- `min_rows` / `max_rows`
  - 仅对 `multiline=1` + `autosize=1` 生效

## Python 示例

```python
import new_emoji_ui as ui

hwnd = ui.create_window("⌨️ Input 示例", 200, 120, 900, 620)
root = ui.create_container(hwnd, 0, 0, 0, 860, 560)

ui.create_input(
    hwnd,
    root,
    value="",
    placeholder="请输入内容 👋",
    prefix_icon="🔎",
    suffix_icon="📅",
    clearable=True,
    x=40, y=60, w=320, h=40,
)

ui.create_input(
    hwnd,
    root,
    value="secret-emoji",
    placeholder="请输入密码 🔐",
    show_password=True,
    x=40, y=120, w=320, h=40,
)

ui.create_input(
    hwnd,
    root,
    value="第一行\n第二行",
    placeholder="多行说明 📝",
    multiline=True,
    autosize=True,
    min_rows=2,
    max_rows=4,
    show_word_limit=True,
    max_length=30,
    x=40, y=190, w=420, h=120,
)
```

## 说明

- `disabled` 继续使用通用 `EU_SetElementEnabled`
- 多行模式仍沿用当前 `Input` 文本引擎，不单独切回 `EditBox`
- `suffix` 区从左到右布局为：
  `suffix文本/图标 -> 密码显隐 -> clear -> 字数统计`

## 对应示例与测试

- 图库：`examples/python/component_gallery.py` 的 `Input` 专页
- 测试：
  - `tests/python/test_input_complete_components.py`
  - `tests/python/test_form_input_enhanced_state_components.py`
  - `tests/python/test_foundation_input_complete_components.py`
