# AI 客户端使用指南

把本项目交给 AI 客户端写界面时，可以先复制这段提示词：

```text
你正在使用 new_emoji.dll 编写 Windows 原生 UI。请先阅读 SKILL.md、docs/ai/api_manifest.full.json、docs/ai/language-matrix.md，并根据目标语言阅读对应 prompt 和模板。所有界面文案必须中文化，并在窗口标题、主按钮、核心展示项中使用 emoji。不要修改 EU_ DLL 导出名。
```

## 通用规则

- `new_emoji.dll` 使用单 HWND + 纯 Direct2D / DirectWrite 渲染。
- DLL 导出统一为 `EU_` 前缀，调用约定为 `__stdcall`。
- 所有文本参数使用 UTF-8 字节数组 + 长度。
- 进程位数必须和 DLL 位数一致；易语言交付优先使用 Win32 DLL。
- 首次创建窗口时，窗口和根容器必须覆盖首屏内容边界，并保留至少 20px 逻辑余量。
- 可见界面文案必须使用中文；窗口标题、主按钮、核心展示项必须带合适 emoji。

## 易语言

优先阅读：

- `docs/ai/prompts/易语言.md`
- `docs/ai/e-language-encoding.md`
- `DLL命令/易语言DLL命令.md`
- `examples/templates/易语言/空白窗口.md`

易语言 IDE 源码中不要直接写 emoji 或特殊 Unicode 字符，否则可能保存或显示为 `?`。AI 生成易语言示例时，必须使用 UTF-8 字节集 + 长度，例如标题、按钮 emoji、按钮文字分别生成字节集变量，再传给 DLL 命令。

易语言 DLL 命令里的回调函数指针参数通常声明为 `整数型`。传入子程序指针时不要直接写 `&回调子程序`，否则会报“不能将子程序指针数据转换到整数型”。必须写成 `到整数 (&回调子程序)`。例如：

```text
错误：设置标签页重排回调 (窗口句柄, Chrome标签页, &标签页重排回调)
正确：设置标签页重排回调 (窗口句柄, Chrome标签页, 到整数 (&标签页重排回调))
```

## 火山

优先阅读：

- `docs/ai/prompts/火山.md`
- `examples/火山/src/new_emoji_接口.wsv`
- `examples/火山/README.md`
- `examples/templates/火山/空白窗口.md`

火山接口已提供 `_字节集` 风格方法，示例应优先传 UTF-8 字节指针和长度。

## C#

优先阅读：

- `docs/ai/prompts/CSharp.md`
- `bindings/csharp/NewEmoji/NewEmoji.csproj`
- `bindings/csharp/NewEmoji.Design/NewEmoji.Design.csproj`
- `bindings/csharp/NewEmoji.Designer.WinForms48/NewEmoji.Designer.WinForms48.csproj`
- `examples/Csharp/MinimalExample.cs`
- `examples/CsharpNet48/MinimalWinFormsExample.csproj`
- `examples/templates/csharp/BlankWindow.cs`
- `DLL命令/CSharp DLL命令.md`

C# 优先使用 `NewEmoji` 对象式封装库，普通界面用 `EmojiWindow.Create`、`CreateContainer`、`AddButton`、`AddInput` 和 `EmojiApplication.Run()`。WinForms `.NET Framework 4.8` 示例使用 `Application.Run()` 消息循环，参考 `examples/CsharpNet48/`；可视化设计器 MVP 位于 `bindings/csharp/NewEmoji.Designer.WinForms48/`。只有封装库暂未覆盖高级能力时才直接 P/Invoke；直接调用 `EU_` 导出时，`CallingConvention` 必须为 `CallingConvention.StdCall`，中文和 emoji 文本必须使用 `Encoding.UTF8.GetBytes(text)` 转成 `byte[]`，并传入数组长度。

## Python

优先阅读：

- `docs/ai/prompts/Python.md`
- `examples/python/new_emoji_ui.py`
- `examples/templates/python/blank_window.py`

普通示例优先调用 `new_emoji_ui.py` 中的 helper，不要从测试目录导入 helper，也不要重复手写大量 ctypes 签名。
