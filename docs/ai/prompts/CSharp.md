# C# AI Prompt

```text
你正在使用 new_emoji.dll 为 C# 生成 Windows 原生 UI。

请优先阅读：
1. DLL命令/CSharp DLL命令.md
2. examples/Csharp/MinimalExample.cs
3. docs/ai/api_manifest.full.json
4. examples/templates/csharp/BlankWindow.cs

规则：
- 使用 P/Invoke 调用 EU_ 导出。
- CallingConvention 必须是 CallingConvention.StdCall。
- 中文和 emoji 文本必须使用 Encoding.UTF8.GetBytes(text) 转为 byte[]，并传入 Length。
- 不要混用 WinForms 控件承载 new_emoji UI。
- 界面文案必须中文化，窗口标题、主按钮、核心展示项必须有 emoji。
- 窗口和根容器首次打开时不能裁切控件，要保留至少 20px 逻辑余量。
```

Table 普通表格行级增删使用 `EU_AddTableRow`、`EU_InsertTableRow`、`EU_DeleteTableRow`、`EU_ClearTableRows`；虚表数据由回调数据源维护。
