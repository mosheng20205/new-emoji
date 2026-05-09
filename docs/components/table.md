# Table 表格

## 简介

`Table` 是 `new_emoji` 的高级数据展示组件。当前状态：**高级样式完成**。

本轮在兼容旧 `EU_CreateTable` / `EU_SetTableData` 行为的基础上，补齐 Element UI 风格表格能力：基础/斑马/边框、固定表头、最大高度、纵向滚动条、横向滚动条、固定左右列、多级表头、单选多选、索引列、排序筛选搜索、展开行、树形行、懒加载标记、合计行、行列合并、行/列/单元格样式覆盖、单元格点击回调，以及表格单元格内置按钮、按钮组、组合款、开关、选择框、进度条、状态和标签展示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateTable` |
| 组件分类 | 数据展示 |
| Python helper | `create_table`、`create_table_ex` |
| 专项测试 | `tests/python/test_table_complete_components.py` |
| 图库入口 | `component_gallery.py` 的 Table 专属页 |

## 高级文本协议

高级 API 使用 UTF-8 字节数组 + 长度，不引入 JSON 依赖。

- 行以 `\n` 分隔。
- 字段以 `\t` 分隔。
- 键值以 `=` 分隔。
- 列表以 `|` 分隔。
- 支持反斜杠转义：`\\`、`\n`、`\t`、`\=`、`\|`。
- 虚表模式的 row provider 直接返回同一套高级行协议字符串，组件负责可视区缓存、滚动命中和原生绘制。

列配置示例：

```text
title=日期	key=date	width=120	sortable=1	filterable=1
title=姓名	key=name	width=120	sortable=1
title=地址	key=address	parent=配送信息	width=260	tooltip=1
title=操作	key=actions	type=buttons	width=150	fixed=right
```

行配置示例：

```text
key=r0	expanded=1	children=1	c0=2016-05-02	c1=王小虎 🎯	c2=上海市普陀区金沙江路 1518 弄	c3=查看 👀|编辑 ✏️	c3_type=buttons
parent=r0	level=1	c0=2016-05-02	c1=明细行	c2=子行说明	c3=归档 🗃️	c3_type=button
```

## 单元格类型

| 类型 | 说明 |
|---|---|
| `text` | 普通文本 |
| `index` | 索引列，可配合自定义索引逻辑 |
| `selection` | 多选勾选列 |
| `expand` | 展开/树形展开入口 |
| `button` | 单按钮 |
| `buttons` | 横向按钮组 |
| `combo` | 组合款单元格，例如“状态 + 操作” |
| `switch` | 开关 |
| `select` | 选择框，点击循环候选项 |
| `progress` | 进度条 |
| `status` | 状态点/状态文本 |
| `tag` | 标签 |
| `popover_tag` | 带提示语义的标签 |

虚表模式适合大数据滚动展示。调用方负责排序、筛选和搜索策略，组件侧专注于渲染、滚动、缓存与命中。

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateTable` | 创建基础表格，旧接口保持兼容 |
| `EU_SetTableData` | 设置旧协议列/行数据 |
| `EU_SetTableStriped` / `EU_SetTableBordered` | 设置斑马纹和边框 |
| `EU_SetTableOptions` / `EU_GetTableOptions` | 设置/读取行高、表头高、选择等基础选项 |
| `EU_SetTableSort` | 设置排序列与方向 |
| `EU_SetTableScrollRow` / `EU_SetTableColumnWidth` | 设置旧接口滚动行和统一列宽 |
| `EU_GetTableSelectedRow` / `EU_GetTableRowCount` / `EU_GetTableColumnCount` | 读取基础状态 |
| `EU_SetTableColumnsEx` | 设置高级列配置 |
| `EU_SetTableRowsEx` | 设置高级行数据 |
| `EU_AddTableRow` / `EU_InsertTableRow` | 普通表格追加或插入一行，行数据使用高级行单行协议 |
| `EU_DeleteTableRow` / `EU_ClearTableRows` | 普通表格删除单行或清空所有行；虚表模式返回失败 |
| `EU_SetTableVirtualOptions` | 设置虚表开关、总行数和缓存窗口 |
| `EU_SetTableVirtualRowProvider` | 设置虚表按行取数回调，返回 UTF-8 高级行协议字符串 |
| `EU_ClearTableVirtualCache` | 清空虚表行缓存 |
| `EU_SetTableCellEx` | 设置单元格类型、值和选项 |
| `EU_SetTableRowStyle` | 设置某一行背景色、前景色、对齐、字体标志、字号 |
| `EU_SetTableCellStyle` | 设置某一单元格背景色、前景色、对齐、字体标志、字号 |
| `EU_SetTableSelectionMode` / `EU_SetTableSelectedRows` | 设置无选择/单选/多选和当前选中行 |
| `EU_SetTableFilter` / `EU_ClearTableFilter` / `EU_SetTableSearch` | 设置列筛选、清除筛选和搜索文本 |
| `EU_SetTableSpan` / `EU_ClearTableSpans` | 设置或清除行列合并 |
| `EU_SetTableSummary` | 设置合计行文本 |
| `EU_SetTableRowExpanded` / `EU_SetTableTreeOptions` | 设置展开状态、树形与懒加载选项 |
| `EU_SetTableViewportOptions` / `EU_SetTableScroll` | 设置最大高度、固定表头、横向滚动、汇总显示和滚动位置；内容溢出时自动绘制可拖拽的纵向/横向滚动条 |
| `EU_SetTableCellClickCallback` | 设置任意单元格点击回调；回调签名同动作回调，点击时 `action=1`、`value=0` |
| `EU_SetTableCellActionCallback` | 设置按钮、开关、选择、展开等单元格交互回调 |
| `EU_GetTableCellValue` / `EU_GetTableFullState` | 读取单元格值和表格完整摘要状态 |

样式优先级：**单元格 > 行 > 列 > 表格默认**。

## 表头拖拽与 Excel

- 表头拖拽默认关闭，可通过 `EU_SetTableHeaderDragOptions` 打开或关闭。
- 列宽拖拽命中表头分隔线；表头高度拖拽命中表头底边，适合桌面端手工调宽习惯。
- `EU_ExportTableExcel` 默认导出整张表，并保留多行表头结构。
- `EU_ImportTableExcel` 按第一张工作表回填当前 Table；若遇到当前版本尚未支持的压缩格式，会返回 `0`。
- 行级增删 API 只作用于普通表格；虚表数据由回调数据源负责，`EU_AddTableRow` / `EU_InsertTableRow` 返回 `-1`，`EU_DeleteTableRow` / `EU_ClearTableRows` 返回 `0`。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📊 高级表格示例", 240, 120, 1120, 720)
root = ui.create_container(hwnd, 0, 0, 0, 1080, 640)

columns = [
    {"title": "序号", "key": "idx", "type": "index", "width": 64, "fixed": "left"},
    {"title": "日期", "key": "date", "width": 120, "sortable": True},
    {"title": "姓名", "key": "name", "width": 120, "searchable": True},
    {"title": "进度", "key": "progress", "type": "progress", "width": 140},
    {"title": "操作", "key": "actions", "type": "buttons", "width": 150, "fixed": "right"},
]
rows = [
    {"cells": [{"type": "index"}, "2016-05-02", "王小虎 🎯", {"type": "progress", "value": 88}, {"type": "buttons", "value": ["查看 👀", "编辑 ✏️"]}]},
]

table = ui.create_table_ex(hwnd, root, columns, rows, True, True, 20, 60, 980, 300, selection_mode=1)
ui.set_table_cell_style(hwnd, table, 0, 2, 0xFFEAF2FF, 0xFF1F3D64, 0, 1, 15)
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。左侧命令名使用中文，右侧 DLL 入口名保持真实 `EU_` 导出名。

## 验收

- `Release|x64` 与 `Release|Win32` 构建通过。
- `tests/python/test_table_complete_components.py` 覆盖高级 API、样式读回、选择、排序筛选、展开树形、汇总、合并和内置控件。
- `tests/python/test_data_display_table_complete_components.py` 保留旧基础表格回归。
- `component_gallery.py` 的 Table 专属页分组展示所有样式，首屏使用中文和 emoji，并保留首次窗口尺寸余量。
