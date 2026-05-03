# Pagination 分页

## 简介

`Pagination` 是 new_emoji 的 导航 组件。当前状态：**已完成**。

已补省略页码、上一页/下一页、每页数量切换、每页数量选项、跳转页、方向键/Home/End/Page 键/数字键/回车键盘操作、变化回调、完整状态读回、Python 封装、易语言命令文档和独立中文 emoji 验证

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreatePagination` |
| 组件分类 | 导航 |
| Python helper | `tests/python/test_new_emoji.py` 中的 `create_pagination` 或同类 helper |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreatePagination` | 当前组件相关导出 |
| `EU_GetPaginationCurrent` | 当前组件相关导出 |
| `EU_GetPaginationFullState` | 当前组件相关导出 |
| `EU_GetPaginationPageCount` | 当前组件相关导出 |
| `EU_GetPaginationState` | 当前组件相关导出 |
| `EU_SetPagination` | 当前组件相关导出 |
| `EU_SetPaginationChangeCallback` | 当前组件相关导出 |
| `EU_SetPaginationCurrent` | 当前组件相关导出 |
| `EU_SetPaginationJumpPage` | 当前组件相关导出 |
| `EU_SetPaginationOptions` | 当前组件相关导出 |
| `EU_SetPaginationPageSize` | 当前组件相关导出 |
| `EU_SetPaginationPageSizeOptions` | 当前组件相关导出 |
| `EU_TriggerPaginationJump` | 当前组件相关导出 |

## Python 使用

```python
import sys

sys.path.insert(0, "tests/python")
import test_new_emoji as ui

hwnd = ui.create_window("✨ 分页 示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
# 请根据 `tests/python/test_new_emoji.py` 中的 helper 创建 `Pagination`。
# 示例界面文案应使用中文，并在标题、按钮或核心内容中加入 emoji。
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。

## 状态与交互

- 组件已按封装计划补齐创建、绘制、主题、DPI、交互、Set/Get、Python 封装和独立中文 emoji 验证。
- 修改组件行为时，需要同步检查 hover、pressed、focus、keyboard、disabled、selected、popup、scroll 等相关状态。
- 涉及回调、状态读回或数据模型变化时，应更新对应独立测试文件。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行对应完整测试文件，例如 `tests/python/test_pagination_complete_components.py`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `Pagination` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`tests/python/test_new_emoji.py` 和 `DLL命令/易语言DLL命令.md`。
