# Button 按钮

## 简介

`Button` 是 new_emoji 的基础交互组件。当前状态：**已完成**。

已补齐默认、主要、成功、信息、警告、危险、文字、朴素、圆角、圆形、加载中、尺寸、禁用、鼠标点击、Space/Enter 键盘触发、状态读回和中文 emoji 验证。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateButton` |
| 组件分类 | 基础/布局 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_button`、`set_button_options`、`get_button_options` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateButton` | 创建按钮，支持 UTF-8 文本和 emoji |
| `EU_SetButtonEmoji` | 修改按钮左侧 emoji |
| `EU_SetButtonVariant` | 兼容旧接口，只设置样式变体 |
| `EU_GetButtonState` | 兼容旧接口，读回 pressed、focused、variant |
| `EU_SetButtonOptions` | 设置变体、朴素、圆角、圆形、加载和尺寸 |
| `EU_GetButtonOptions` | 读回变体、朴素、圆角、圆形、加载和尺寸 |

## 选项值

`variant` 保持旧编号兼容：

| 值 | 样式 |
|---|---|
| `0` | 默认 |
| `1` | 主要 |
| `2` | 成功 |
| `3` | 警告 |
| `4` | 危险 |
| `5` | 文字 |
| `6` | 信息 |

`size` 取值：

| 值 | 尺寸 |
|---|---|
| `0` | 默认 |
| `1` | 中等 |
| `2` | 小型 |
| `3` | 超小 |

`plain`、`round`、`circle`、`loading` 使用 `0/1`。`loading=1` 时按钮显示加载态，并抑制鼠标点击和 Space/Enter 键盘触发。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🚀 按钮示例", 240, 120, 960, 620)
root = ui.create_container(hwnd, 0, 0, 0, 920, 560)

ui.create_button(hwnd, root, "🚀", "主要按钮", 40, 60, 128, 38, variant=1)
ui.create_button(hwnd, root, "✅", "朴素成功", 188, 60, 128, 38, variant=2, plain=True)
ui.create_button(hwnd, root, "🔎", "", 340, 58, 42, 42, variant=1, circle=True)
ui.create_button(hwnd, root, "⏳", "加载中", 406, 60, 128, 38, variant=1, loading=True)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- 支持 hover、pressed、focus、disabled、loading、plain、round、circle 和 size 状态。
- `loading` 态不会触发点击回调，也不会响应 Space/Enter。
- 按钮组不新增 native 组件，可通过多个 `Button` 组合展示。
- 修改 API 或行为时，需要同步 `examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`DLL命令/易语言DLL命令.md` 和组件测试。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行：

```powershell
python .\tests\python\test_button_complete_components.py
```

## 文档维护

如果 `Button` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py` 和 `DLL命令/易语言DLL命令.md`。
