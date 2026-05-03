# Result 结果页

## 简介

`Result` 是 new_emoji 的 反馈/浮层 组件。当前状态：**已完成**。

已补完整操作区交互、自定义内容/类型状态、鼠标/键盘/程序触发、操作回调、文本/操作项/完整状态读回、Python 封装、易语言 DLL 命令文档和独立中文 emoji 验证

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateResult` |
| 组件分类 | 反馈/浮层 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_result` 或同类 helper |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateResult` | 当前组件相关导出 |
| `EU_GetResultAction` | 当前组件相关导出 |
| `EU_GetResultActionText` | 当前组件相关导出 |
| `EU_GetResultFullState` | 当前组件相关导出 |
| `EU_GetResultOptions` | 当前组件相关导出 |
| `EU_GetResultText` | 当前组件相关导出 |
| `EU_SetResultActionCallback` | 当前组件相关导出 |
| `EU_SetResultActions` | 当前组件相关导出 |
| `EU_SetResultExtraContent` | 当前组件相关导出 |
| `EU_SetResultSubtitle` | 当前组件相关导出 |
| `EU_SetResultType` | 当前组件相关导出 |
| `EU_TriggerResultAction` | 当前组件相关导出 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("✨ 结果页 示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
# 请根据 `examples/python/new_emoji_ui.py` 中的 helper 创建 `Result`。
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

优先运行对应完整测试文件，例如 `tests/python/test_result_complete_components.py`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `Result` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py` 和 `DLL命令/易语言DLL命令.md`。
