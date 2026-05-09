# Python 示例说明

Python 示例和测试使用 `ctypes` 加载 `new_emoji.dll`。普通示例推荐复用 `examples/python/new_emoji_ui.py`，其中已经声明了导出函数签名和常用 helper。

## 组件总览

运行 81 个组件的完整总览 Demo：

```powershell
python examples/python/component_gallery.py
```

该 Demo 使用中文界面和 emoji 文案，按 6 个分类分页展示所有组件：

- 基础布局
- 表单输入
- 选择媒体
- 数据展示
- 图表导航
- 反馈流程

默认窗口保持 180 秒。短时间冒烟验证可以设置：

```powershell
$env:NEW_EMOJI_GALLERY_SECONDS="12"
python examples/python/component_gallery.py
```

## 位数检查

```powershell
python -c "import struct; print(struct.calcsize('P') * 8, 'bit')"
```

32 位 Python 对应 Win32 DLL，64 位 Python 对应 x64 DLL。

## 窗口图标示例

运行窗口图标示例，窗口会保持打开直到手动关闭：

```powershell
python examples/python/window_icon_demo.py
```

示例同时演示 `EU_SetWindowIcon` 的 `.ico` 文件路径方式，以及 `EU_SetWindowIconFromBytes` 的 `.ico` 文件字节集方式。

## 窗口圆角示例

运行窗口圆角示例，窗口会保持打开直到手动关闭：

```powershell
python examples/python/window_rounded_corners_demo.py
```

示例演示 `EU_SetWindowRoundedCorners` 的 Windows 窗口外形圆角，并提供小圆角、中圆角、大圆角和关闭圆角按钮；支持 DWM 的系统会使用平滑圆角，Win10 会优先使用 per-pixel alpha 分层窗口圆角。

## 最小示例

```python
import ctypes
from ctypes import wintypes
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("✨ new_emoji 示例", 240, 120, 820, 560)
root = ui.create_container(hwnd, 0, 0, 0, 780, 500)
ui.create_text(hwnd, root, "你好，new_emoji 🚀", 32, 32, 360, 40)
ui.create_button(hwnd, root, "✅", "确认操作", 32, 96, 160, 42)
ui.dll.EU_ShowWindow(hwnd, 1)

user32 = ctypes.windll.user32
msg = wintypes.MSG()
while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
```

## 示例要求

- 界面文案使用中文。
- 窗口标题、主标题、主要按钮和关键展示项应包含 emoji。
- 窗口首次打开时必须完整覆盖控件区域，并保留至少 20px 逻辑余量。
- UI 测试不要闪退，应保持可见足够时间。
