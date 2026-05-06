# Transfer 穿梭框

## 简介

`Transfer` 是左右列表穿梭选择组件。当前状态：**已完成**。

已覆盖基础穿梭、筛选、禁用项、多选勾选、默认勾选、自定义标题、自定义按钮文案、统计格式、底部操作区、字段映射、字段模板渲染、目标值读回、Python 封装、易语言命令文档和 `component_gallery.py` 桌面端完整样式演示。

## 数据格式

旧接口 `EU_CreateTransfer` / `EU_SetTransferItems` 继续支持 `|` 或换行分隔的简单文本列表。

扩展接口 `EU_SetTransferDataEx` 使用逐行 UTF-8 数据：

```text
key<Tab>label<Tab>value<Tab>desc<Tab>pinyin<Tab>disabled
```

目标值列表使用 `|` 或换行分隔。匹配目标侧时优先使用 `key`，并兼容 `value`、`label`。字段模板支持：

```text
{key} {label} {value} {desc} {pinyin}
```

## 样式与选项

| 能力 | API |
|---|---|
| 筛选框、多选、底部区、全选、统计、渲染模式 | `EU_SetTransferOptions` / `EU_GetTransferOptions` |
| 左右标题 | `EU_SetTransferTitles` |
| 左右移动按钮文案 | `EU_SetTransferButtonTexts` |
| 统计格式 | `EU_SetTransferFormat` |
| 数据项模板 | `EU_SetTransferItemTemplate` |
| 底部操作区文案 | `EU_SetTransferFooterTexts` |
| 筛选占位文案 | `EU_SetTransferFilterPlaceholder` |
| 默认勾选/程序勾选 | `EU_SetTransferCheckedKeys` |

统计格式支持 `${checked}`、`${total}`、`${matched}`。

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateTransfer` | 创建穿梭框，兼容简单文本列表 |
| `EU_SetTransferItems` | 设置简单左右列表 |
| `EU_SetTransferDataEx` | 设置结构化项目和目标值 |
| `EU_TransferMoveRight` / `EU_TransferMoveLeft` | 移动选中或已勾选项目 |
| `EU_TransferMoveAllRight` / `EU_TransferMoveAllLeft` | 移动当前匹配范围内全部可用项目 |
| `EU_SetTransferFilters` | 设置左右筛选文本 |
| `EU_SetTransferFilterPlaceholder` | 设置筛选输入框占位文案，如“请输入城市拼音 🔎” |
| `EU_SetTransferItemDisabled` | 设置项目禁用状态 |
| `EU_GetTransferValueKeys` | 读回右侧目标值，`|` 分隔 |
| `EU_GetTransferCheckedCount` | 读回指定侧勾选数量 |
| `EU_GetTransferText` | 读回标题、按钮、格式、模板、底部文案和筛选占位文案 |

## Python 使用

```python
items = [
    {"key": "beijing", "label": "🏛️ 北京", "pinyin": "beijing"},
    {"key": "shanghai", "label": "🏙️ 上海", "pinyin": "shanghai"},
    {"key": "shenzhen", "label": "🚄 深圳", "pinyin": "shenzhen"},
]

transfer = ui.create_transfer_ex(
    hwnd, root, items, target_keys=["shanghai"],
    filterable=True,
    titles=("📥 来源列表", "📤 目标列表"),
    button_texts=("到左边", "到右边"),
    item_template="{key} - {label}",
    show_footer=True,
    footer_texts=("⚙️ 左侧操作", "✅ 右侧操作"),
    filter_placeholder="请输入城市拼音 🔎",
    x=28, y=80, w=860, h=260,
)
ui.set_transfer_checked_keys(hwnd, transfer, ["beijing"], ["shanghai"])
```

字段映射示例：

```python
ui.create_transfer_ex(
    hwnd, root,
    [{"value": 1, "desc": "备选项 1"}, {"value": 2, "desc": "备选项 2"}],
    target_keys=[1],
    props={"key": "value", "label": "desc"},
)
```

## 测试

优先运行：

```powershell
python tests/python/test_transfer_complete_components.py
```

同时回归：

```powershell
python tests/python/test_selection_state_components.py
python tests/python/test_theme_focus_transfer_components.py
```

## 文档维护

如果 `Transfer` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/components/manifest.json`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
