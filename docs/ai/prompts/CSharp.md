# C# AI Prompt

```text
你正在使用 new_emoji.dll 为 C# 生成 Windows 原生 UI。

请优先阅读：
1. docs/examples/csharp.md
2. examples/Csharp/MinimalExample.cs
3. bindings/csharp/NewEmoji/NewEmoji.csproj
4. examples/templates/csharp/BlankWindow.cs
5. DLL命令/CSharp DLL命令.md
6. docs/ai/api_manifest.full.json

规则：
- 优先使用 `NewEmoji` C# 封装库：`EmojiWindow`、`EmojiElement`、`AddButton`、`AddInput`、`EmojiApplication.Run()`。
- 常用复杂组件优先使用强类型封装：`EmojiTable`、`EmojiTabs`、`EmojiDialog`、`EmojiCard`、`EmojiDrawer`、`EmojiNotification`；只有封装库暂未覆盖高级能力时，才直接使用 `NewEmoji.Native.NativeMethods` 调用 `EU_` 导出。
- 需要 WinForms `.NET Framework 4.8` 时，参考 `examples/CsharpNet48/MinimalWinFormsExample.csproj`，使用 WinForms `Application.Run()` 消息循环，并把 x64 `new_emoji.dll` 复制到输出目录根部。
- 需要可视化设计器时，使用 `bindings/csharp/NewEmoji.Designer.WinForms48`；布局 JSON 和代码生成能力位于 `bindings/csharp/NewEmoji.Design`。
- 设计器支持组件树、拖拽、多选、移动/缩放、复制/粘贴/复制一份/删除、撤销/重做、方向键微调、对齐、打开/保存 JSON、导出 C# `.NET Framework 4.8` 项目。
- 直接 P/Invoke 时，CallingConvention 必须是 CallingConvention.StdCall。
- 直接 P/Invoke 时，中文和 emoji 文本必须使用 Encoding.UTF8.GetBytes(text) 转为 byte[]，并传入 Length；对象式封装会自动处理 UTF-8。
- 不要混用 WinForms 控件承载 new_emoji UI。
- 界面文案必须中文化，窗口标题、主按钮、核心展示项必须有 emoji。
- 窗口和根容器首次打开时不能裁切控件，要保留至少 20px 逻辑余量。
```

Table 普通表格行级增删优先使用 `EmojiTable.AddRow`、`EmojiTable.InsertRow`、`EmojiTable.DeleteRow`、`EmojiTable.ClearRows`；虚表和特别高级能力可继续调用 `NativeMethods`。

Table 普通文本单元格双击编辑优先使用 `EmojiTable.DoubleClickEdit`、`SetColumnDoubleClickEdit`、`SetCellDoubleClickEdit` 和 `CellEdit` 事件；直接 P/Invoke 时使用 `EU_SetTableCellEditCallback` 读取 UTF-8 文本。

窗口图标：调用 `EU_SetWindowIcon` 传入 UTF-8 `.ico` 路径字节，或调用 `EU_SetWindowIconFromBytes` 传入 `.ico` 文件完整字节。

窗口圆角：调用 `EU_SetWindowRoundedCorners(hwnd, enabled, radius)` 设置 Windows 窗口外形圆角；支持 DWM 的系统会优先使用平滑圆角，Win10 会回退为 per-pixel alpha 分层窗口并通过 `UpdateLayeredWindow(ULW_ALPHA)` 提交。

C# 封装库示例：

```csharp
using NewEmoji;

var win = EmojiWindow.Create("✅ C# 示例窗口", 860, 560);
var root = win.CreateContainer(0, 0, 820, 500);
root.AddText("欢迎使用 new_emoji 🚀", 32, 32, 420, 40);
root.AddButton("✅", "确认操作", 32, 96, 160, 42)
    .Clicked += (_, _) => win.ShowMessage("操作成功 🎉", EmojiMessageType.Success);
win.Show();
EmojiApplication.Run();
```

WinForms `.NET Framework 4.8` 示例用法：

```csharp
Application.EnableVisualStyles();
var win = EmojiWindow.Create("✅ .NET 4.8 示例", 900, 600);
win.Closing += (_, _) => Application.ExitThread();
win.Show();
Application.Run();
```
