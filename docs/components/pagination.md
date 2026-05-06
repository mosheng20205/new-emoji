# Pagination 分页

## 简介

`Pagination` 是 new_emoji 的导航组件。当前状态：**已完成**。

已补齐 Element Plus 常见分页样式：基础页码、页数较少、大于 7 页折叠、`pager-count`、背景分页、小尺寸、显示总数、每页数量、跳转页、完整功能和单页隐藏。组件支持鼠标、方向键/Home/End/Page 键、数字键/回车跳转、变化回调、完整状态读回、Python 封装、易语言命令文档和独立中文 emoji 验证。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreatePagination` |
| 组件分类 | 导航 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_pagination` |
| 易语言命令 | `创建分页`，见 `DLL命令/易语言DLL命令.md` |

## 样式与能力对照

| Element Plus 能力 | new_emoji 对应方式 |
|---|---|
| `layout="prev, pager, next"` | `EU_CreatePagination` + `EU_SetPaginationOptions(..., 0, 0, 7)` |
| `total` | `EU_SetPagination` / `EU_CreatePagination` 的 `total` |
| `page-size` | `EU_SetPaginationPageSize` |
| `pager-count` | `EU_SetPaginationOptions` 的 `visible_page_count`，范围 5-11，自动归一为奇数 |
| `background` | `EU_SetPaginationAdvancedOptions(..., 1, 0, 0)` |
| `small` | `EU_SetPaginationAdvancedOptions(..., 0, 1, 0)` |
| 显示总数 | 组件右侧自动显示 `共 N 条 / M 页` |
| `sizes` / `page-sizes` | `EU_SetPaginationOptions(..., show_size_changer=1, ...)` + `EU_SetPaginationPageSizeOptions`；当前桌面交互为点击循环切换 |
| `jumper` | `EU_SetPaginationOptions(..., show_jumper=1, ...)` |
| `hide-on-single-page` | `EU_SetPaginationAdvancedOptions(..., hide_on_single_page=1)` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreatePagination` | 创建分页组件 |
| `EU_SetPagination` | 设置总数、每页数量和当前页 |
| `EU_SetPaginationCurrent` | 设置当前页 |
| `EU_SetPaginationPageSize` | 设置每页数量 |
| `EU_SetPaginationOptions` | 设置跳转、每页数量切换和可见页码数 |
| `EU_SetPaginationAdvancedOptions` | 设置背景、小尺寸、单页隐藏 |
| `EU_SetPaginationPageSizeOptions` | 设置每页数量选项 |
| `EU_SetPaginationJumpPage` | 设置待跳转页码 |
| `EU_TriggerPaginationJump` | 触发跳转 |
| `EU_NextPaginationPageSize` | 切换到下一个每页数量选项 |
| `EU_GetPaginationCurrent` | 读取当前页 |
| `EU_GetPaginationPageCount` | 读取总页数 |
| `EU_GetPaginationState` | 读取基础状态 |
| `EU_GetPaginationFullState` | 读取完整交互状态 |
| `EU_GetPaginationAdvancedOptions` | 读取高级样式状态 |
| `EU_SetPaginationChangeCallback` | 设置页码/每页数量变化回调 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📚 分页示例", 240, 120, 980, 560)
root = ui.create_container(hwnd, 0, 0, 0, 940, 500)

pager = ui.create_pagination(hwnd, root, total=1000, page_size=100, current=5, x=32, y=64, w=860, h=46)
ui.set_pagination_options(hwnd, pager, show_jumper=True, show_size_changer=True, visible_page_count=11)
ui.set_pagination_page_size_options(hwnd, pager, [100, 200, 300, 400])
ui.set_pagination_advanced_options(hwnd, pager, background=True, small=False, hide_on_single_page=False)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。

## 状态与交互

- `hide_on_single_page=1` 且总页数不大于 1 时，组件不绘制且不响应鼠标/键盘分页动作。
- 修改组件行为时，需要同步检查 hover、pressed、focus、keyboard、disabled、selected 等相关状态。
- 涉及回调、状态读回或数据模型变化时，应更新 `tests/python/test_pagination_complete_components.py`。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行 `tests/python/test_pagination_complete_components.py`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `Pagination` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py` 和 `DLL命令/易语言DLL命令.md`。
