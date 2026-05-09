# 多语言接入矩阵

| 语言 | 推荐入口 | 文本传参 | DLL 位数 | 示例目录 | 适用人群 |
|---|---|---|---|---|---|
| 易语言 | `DLL命令/易语言DLL命令.md` | UTF-8 字节集 + 长度；源码不要直接写 emoji | Win32 优先 | `examples/E/`、`examples/templates/易语言/` | 易语言桌面软件开发者 |
| 火山 | `examples/火山/src/new_emoji_接口.wsv` | UTF-8 字节指针 + 长度 | 与进程位数一致 | `examples/火山/`、`examples/templates/火山/` | 火山视窗开发者 |
| C# | `DLL命令/CSharp DLL命令.md` | `Encoding.UTF8.GetBytes(text)` + `Length` | 与进程位数一致 | `examples/Csharp/`、`examples/templates/csharp/` | .NET / P/Invoke 用户 |
| Python | `examples/python/new_emoji_ui.py` | helper 自动处理 UTF-8 | 与 Python 位数一致 | `examples/python/`、`examples/templates/python/` | Python 原型和自动化用户 |

## Table 行级增删

- 普通表格行级增删使用 `EU_AddTableRow` / `EU_InsertTableRow` / `EU_DeleteTableRow` / `EU_ClearTableRows`；Python 优先使用 `add_table_row` / `insert_table_row` / `delete_table_row` / `clear_table_rows`。
- 虚表数据仍由 `EU_SetTableVirtualRowProvider` 的回调数据源维护，不使用这些行级增删命令。

## 窗口图标

- 路径方式：`EU_SetWindowIcon(hwnd, path_bytes, path_len)`，路径按 UTF-8 字节集 + 长度传入，建议使用 `.ico` 文件。
- 字节集方式：`EU_SetWindowIconFromBytes(hwnd, icon_bytes, icon_len)`，传入 `.ico` 文件完整字节。

## 窗口圆角

- 窗口外形圆角使用 `EU_SetWindowRoundedCorners(hwnd, enabled, radius)`；Python 对应 `set_window_rounded_corners(hwnd, True, radius)`。
- 支持 DWM 圆角的系统会优先使用系统抗锯齿圆角；Win10 等旧系统主路径回退到 per-pixel alpha 分层窗口，并按当前 DPI / 屏幕缩放换算逻辑半径；如果 layered 连续提交失败，会退到真实窗口区域圆角。关闭时传 `enabled=0` 或 `radius<=0`。
- Python 示例可参考 `examples/python/window_rounded_corners_demo.py`，窗口会保持打开直到用户手动关闭。

## 通用约束

- DLL 导出统一为 `EU_` 前缀。
- 调用约定为 `__stdcall`。
- 文本都按 UTF-8 字节数组 + 长度传入。
- 回调子程序参数必须严格匹配对应 DLL 导出的真实回调签名；例如易语言 `设置元素点击回调` 只传 1 个 `元素ID`，不要写成 4 参数回调，否则点击按钮可能闪退。
- 首屏窗口尺寸必须覆盖最右侧和最下方控件，并保留至少 20px 逻辑余量。
- 可见界面文案必须中文化，并在标题、主按钮和核心展示项中使用 emoji。
