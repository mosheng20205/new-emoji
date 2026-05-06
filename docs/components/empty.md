# Empty 空状态

## 简介

`Empty` 是 new_emoji 的数据展示组件。当前状态：**已完成**。

已补齐 Element Plus 常见空状态样式：描述文字、自定义图片、本地/HTTP/HTTPS 图片源、图片尺寸、内置操作按钮、真实子元素按钮插槽、操作回调、图片状态读回、Python 封装和桌面端中文 emoji 全样式演示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateEmpty` |
| 组件分类 | 数据展示 |
| Python helper | `create_empty` / `set_empty_image` / `set_empty_image_size` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateEmpty` | 创建空状态，传入标题、描述和逻辑坐标尺寸 |
| `EU_SetEmptyDescription` | 设置描述文字 |
| `EU_SetEmptyOptions` | 设置 emoji 图标和内置操作按钮文字 |
| `EU_SetEmptyImage` | 设置空状态图片，支持本地路径、HTTP、HTTPS |
| `EU_SetEmptyImageSize` | 设置图片显示尺寸，0 为自适应 |
| `EU_GetEmptyImageStatus` | 读取图片状态：0 默认图标/无图片，1 已加载，2 加载失败，3 加载中 |
| `EU_GetEmptyImageSize` | 读取图片逻辑尺寸 |
| `EU_SetEmptyActionClicked` | 设置内置操作按钮点击状态 |
| `EU_GetEmptyActionClicked` | 读取内置操作按钮点击状态 |
| `EU_SetEmptyActionCallback` | 设置内置操作按钮回调 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📭 空状态 示例", 240, 120, 980, 680)
root = ui.create_container(hwnd, 0, 0, 0, 940, 620)

empty = ui.create_empty(
    hwnd, root,
    "暂无订单 🍔",
    "当前筛选条件下没有订单，可调整条件后重试。",
    40, 40, 360, 260,
    image="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png",
    image_size=200,
)

# 默认插槽按钮：把真实 Button 挂载到 Empty 子树。
ui.create_button(hwnd, empty, "➕", "创建内容", 106, 204, 148, 42)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- 无图片时绘制 emoji 图标；设置图片后优先绘制图片，加载中和失败时显示占位图标。
- `image_size=0` 使用自适应尺寸；正数按逻辑尺寸绘制并随 DPI 缩放。
- 内置 `action` 按钮保持兼容；需要更复杂按钮时，直接以 Empty 的元素 ID 作为父元素创建 Button。
- 子按钮使用普通元素命中测试和绘制流程，可使用 `EU_SetElementClickCallback` 绑定事件。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行 `tests/python/test_empty_complete_components.py`，并在 `component_gallery.py` 中打开 Empty 专属页做视觉检查。

## 文档维护

如果 `Empty` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`DLL命令/易语言DLL命令.md` 和 `component_gallery.py`。
