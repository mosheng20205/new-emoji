# 快速开始

## 1. 选择 DLL 位数

- 易语言交付优先使用 Win32 DLL。
- 64 位 Python / C# 进程使用 x64 DLL。
- 进程位数必须和 DLL 位数一致，否则会加载失败。

## 2. 构建 DLL

```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
```

输出位置：

- `bin/Win32/Release/new_emoji.dll`
- `bin/x64/Release/new_emoji.dll`

## 3. Python 运行一个窗口

```python
import ctypes
from ctypes import wintypes
import time
import sys

sys.path.insert(0, "tests/python")
import test_new_emoji as ui

@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)

hwnd = ui.create_window("✨ 快速开始", 240, 120, 860, 560)
ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
ui.create_text(hwnd, root, "欢迎使用 new_emoji 🚀", 32, 32, 500, 42)
ui.create_button(hwnd, root, "✅", "开始体验", 32, 100, 160, 42)
ui.dll.EU_ShowWindow(hwnd, 1)

user32 = ctypes.windll.user32
msg = wintypes.MSG()
while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
```

## 4. 查组件文档

所有组件入口见 [组件文档导航](components/README.md)。每个组件页面包含创建 API、相关导出、Python helper、易语言文档入口和测试文件建议。
