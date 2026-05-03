# Dialog 对话框

## 简介

`Dialog` 是 new_emoji 的 反馈/浮层 组件。当前状态：**已完成**。

已补拖拽、遮罩关闭、打开状态、模态/关闭/尺寸选项、按钮区、焦点循环、键盘/程序按钮触发、按钮回调、文本/完整状态读回和独立中文 emoji 验证

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateDialog` |
| 组件分类 | 反馈/浮层 |
| Python helper | `test_new_emoji.py` 中的 `create_dialog` 或同类 helper |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateDialog` | 当前组件相关导出 |
| `EU_GetDialogButtonText` | 当前组件相关导出 |
| `EU_GetDialogFullState` | 当前组件相关导出 |
| `EU_GetDialogOpen` | 当前组件相关导出 |
| `EU_GetDialogOptions` | 当前组件相关导出 |
| `EU_GetDialogText` | 当前组件相关导出 |
| `EU_SetDialogBody` | 当前组件相关导出 |
| `EU_SetDialogButtonCallback` | 当前组件相关导出 |
| `EU_SetDialogButtons` | 当前组件相关导出 |
| `EU_SetDialogOpen` | 当前组件相关导出 |
| `EU_SetDialogOptions` | 当前组件相关导出 |
| `EU_SetDialogTitle` | 当前组件相关导出 |
| `EU_TriggerDialogButton` | 当前组件相关导出 |

## Python 使用

```python
import test_new_emoji as ui

hwnd = ui.create_window("✨ 对话框 示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
# 请根据 `test_new_emoji.py` 中的 helper 创建 `Dialog`。
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

优先运行对应完整测试文件，例如 `test_dialog_complete_components.py`。如果该组件被组合测试覆盖，请查看根目录 `test_*_complete_components.py`。

## 文档维护

如果 `Dialog` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`test_new_emoji.py` 和 `DLL命令/易语言DLL命令.md`。
