# new_emoji

`new_emoji` 是一个面向 易语言 / Python / C# 调用的 Windows 原生 UI DLL。它采用单一 HWND + 纯 Direct2D 渲染架构，把所有控件封装成 Element 组件，重点解决传统 GDI 子窗口在缩放和重绘时的闪烁问题，同时原生支持中文与彩色 emoji。

## 特性

- 纯 Direct2D / DirectWrite 渲染，单窗口树，减少闪烁。
- 统一 `EU_` C API 导出，适合 DLL 方式集成。
- 文本参数统一使用 UTF-8 字节数组 + 长度，方便易语言传递 emoji 和 Unicode 文本。
- 支持 Win32 与 x64 Release 构建，其中 Win32 是易语言交付优先目标。
- 组件完成度：81 / 81，所有计划内组件均已完成独立中文 emoji 验证。
- 内置主题、DPI、键鼠交互、Set/Get 状态读回和 Python ctypes helper。

## 快速入口

- [文档总览](docs/README.md)
- [快速开始](docs/quick-start.md)
- [构建说明](docs/build.md)
- [API 约定](docs/api-conventions.md)
- [组件文档导航](docs/components/README.md)
- [易语言 DLL 命令](DLL命令/易语言DLL命令.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)
- [许可证](LICENSE)

## 最短 Python 示例

```python
import ctypes
from ctypes import wintypes
import test_new_emoji as ui

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

> Python 位数必须和 DLL 位数一致：32 位 Python 加载 Win32 DLL，64 位 Python 加载 x64 DLL。

## 构建

```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=x64
```

详细要求见 [构建说明](docs/build.md)。

## 文档维护

当某个组件新增、删除、重命名或修改导出 API 时，必须同步更新该组件文档、组件导航、Python ctypes/helper 和易语言 DLL 命令文档，避免开源用户看到过期接口。

## 许可证

本项目使用 [MIT License](LICENSE) 开源。
