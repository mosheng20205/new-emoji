# Autocomplete 自动补全

## 简介

`Autocomplete` 在现有基础上已补齐常用 Element 风格能力：

- `placeholder`
- `trigger_on_focus`
- `prefix_icon` / `suffix_icon`
- 单行建议项
- 双行建议项：`标题 + 副标题 + 写回值`
- 异步加载状态
- 空状态文案
- 键盘上下、回车、ESC

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateAutocomplete` |
| Python helper | `create_autocomplete(...)` |
| 组件分类 | 复杂选择 |
| 当前状态 | 已完成 |

## 相关导出

### 创建与基础状态

- `EU_CreateAutocomplete`
- `EU_SetAutocompleteSuggestions`
- `EU_SetAutocompleteValue`
- `EU_SetAutocompleteOpen`
- `EU_SetAutocompleteSelected`
- `EU_SetAutocompleteAsyncState`
- `EU_SetAutocompleteEmptyText`
- `EU_GetAutocompleteValue`
- `EU_GetAutocompleteOpen`
- `EU_GetAutocompleteSelected`
- `EU_GetAutocompleteSuggestionCount`
- `EU_GetAutocompleteOptions`

### 新增视觉与行为接口

- `EU_SetAutocompletePlaceholder`
- `EU_GetAutocompletePlaceholder`
- `EU_SetAutocompleteIcons`
- `EU_GetAutocompleteIcons`
- `EU_SetAutocompleteBehaviorOptions`
- `EU_GetAutocompleteBehaviorOptions`

## 建议项格式

### 旧格式

单行纯文本，兼容原有调用：

```text
北京
上海
深圳
```

### 新格式

逐行 UTF-8：

```text
标题<Tab>副标题<Tab>写回值
标题<Tab>副标题<Tab>写回值
```

规则：

- 没有第三列时，写回值默认使用标题
- 没有副标题时，按单行建议项绘制

## 行为选项

`EU_SetAutocompleteBehaviorOptions(hwnd, id, trigger_on_focus)`

- `trigger_on_focus = 1`
  - 聚焦即展开建议
- `trigger_on_focus = 0`
  - 输入后再匹配展开

## Python 示例

```python
import new_emoji_ui as ui

ui.create_autocomplete(
    hwnd,
    root,
    value="",
    placeholder="请输入餐厅名 🍜",
    prefix_icon="🔎",
    trigger_on_focus=False,
    suggestions=[
        ("三全鲜食（北新泾店）", "长宁区新渔路144号", "三全鲜食（北新泾店）"),
        ("新旺角茶餐厅", "普陀区真北路988号", "新旺角茶餐厅"),
        ("Monica 摩托主题咖啡店", "嘉定区曹安公路2409号", "Monica 摩托主题咖啡店"),
    ],
    x=40, y=60, w=460, h=40,
)
```

## 说明

- `suffix_icon` 只补尾部图标点击语义，不扩展成任意 slot 模板
- 双行建议项是本轮固定样式，不做通用富模板系统
- 异步状态和空状态仍可与旧 API 兼容混用

## 对应示例与测试

- 图库：`examples/python/component_gallery.py` 的 `Autocomplete` 专页
- 测试：
  - `tests/python/test_autocomplete_complete_components.py`
