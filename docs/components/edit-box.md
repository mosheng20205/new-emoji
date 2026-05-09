# EditBox 兼容编辑内核

## 简介

`EditBox` 是 new_emoji 早期 MVP 保留下来的兼容编辑内核。当前状态：**已完成**。

它继续提供 IME 组合/提交、选区、复制粘贴、占位、密码/多行、只读、文本变化回调、状态读回和独立中文 emoji 验证。新建表单界面时推荐使用更完整的 `Input` 组件，`EditBox` 主要用于兼容旧示例、底层编辑行为验证和少量轻量输入场景。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateEditBox` |
| 组件分类 | 兼容内核 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_edit_box` 或同类 helper |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateEditBox` | 当前组件相关导出 |
| `EU_GetEditBoxOptions` | 当前组件相关导出 |
| `EU_GetEditBoxState` | 当前组件相关导出 |
| `EU_GetEditBoxText` | 当前组件相关导出 |
| `EU_SetEditBoxScroll` | 多行模式下设置垂直滚动位置，单行模式保持原有横向滚动行为 |
| `EU_GetEditBoxScroll` | 读取 `scroll_y`、`max_scroll_y`、内容高度和视口高度 |
| `EU_SetEditBoxOptions` | 当前组件相关导出 |
| `EU_SetEditBoxText` | 当前组件相关导出 |
| `EU_SetEditBoxTextCallback` | 当前组件相关导出 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("✍️ 兼容编辑内核示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
# 请根据 `examples/python/new_emoji_ui.py` 中的 helper 创建 `EditBox`。
# 示例界面文案应使用中文，并在标题、按钮或核心内容中加入 emoji。
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。

## 状态与交互

- 组件已按封装计划补齐创建、绘制、主题、DPI、交互、Set/Get、Python 封装和独立中文 emoji 验证。
- 多行内容超过可视区域时会自动显示右侧垂直滚动条，支持鼠标滚轮、拖动滑块、点击轨道翻页，以及通过滚动 API 回顶或跳转。
- 修改组件行为时，需要同步检查 hover、pressed、focus、keyboard、disabled、selected、popup、scroll 等相关状态。
- 涉及回调、状态读回或数据模型变化时，应更新对应独立测试文件。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行对应完整测试文件，例如 `tests/python/test_editbox_complete_components.py`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `EditBox` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py` 和 `DLL命令/易语言DLL命令.md`。如果只是新增业务表单输入能力，应优先补到 `Input`。
