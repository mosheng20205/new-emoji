# 多语言接入矩阵

| 语言 | 推荐入口 | 文本传参 | DLL 位数 | 示例目录 | 适用人群 |
|---|---|---|---|---|---|
| 易语言 | `DLL命令/易语言DLL命令.md` | UTF-8 字节集 + 长度；源码不要直接写 emoji | Win32 优先 | `examples/E/`、`examples/templates/易语言/` | 易语言桌面软件开发者 |
| 火山 | `examples/火山/src/new_emoji_接口.wsv` | UTF-8 字节指针 + 长度 | 与进程位数一致 | `examples/火山/`、`examples/templates/火山/` | 火山视窗开发者 |
| C# | `DLL命令/CSharp DLL命令.md` | `Encoding.UTF8.GetBytes(text)` + `Length` | 与进程位数一致 | `examples/Csharp/`、`examples/templates/csharp/` | .NET / P/Invoke 用户 |
| Python | `examples/python/new_emoji_ui.py` | helper 自动处理 UTF-8 | 与 Python 位数一致 | `examples/python/`、`examples/templates/python/` | Python 原型和自动化用户 |

## 通用约束

- DLL 导出统一为 `EU_` 前缀。
- 调用约定为 `__stdcall`。
- 文本都按 UTF-8 字节数组 + 长度传入。
- 首屏窗口尺寸必须覆盖最右侧和最下方控件，并保留至少 20px 逻辑余量。
- 可见界面文案必须中文化，并在标题、主按钮和核心展示项中使用 emoji。
