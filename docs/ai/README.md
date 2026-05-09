# AI SDK 文档

这里是给 AI 客户端和多语言开发者使用的入口。它不替代组件文档，而是告诉 AI 如何稳定调用 `new_emoji.dll` 生成界面。

## 入口

- [多语言接入矩阵](language-matrix.md)
- [完整 API manifest](api_manifest.full.json)
- [易语言编码规则](e-language-encoding.md)
- [易语言 prompt](prompts/易语言.md)
- [火山 prompt](prompts/火山.md)
- [C# prompt](prompts/CSharp.md)
- [Python prompt](prompts/Python.md)

## 推荐流程

1. 先确定目标语言。
2. 阅读对应 prompt。
3. 查 `api_manifest.full.json` 选择组件和 DLL 导出。
4. 查 `docs/components/` 中的组件文档补充参数和交互细节。
5. 生成交互回调前核对对应 DLL 命令或 typedef 的真实参数，尤其易语言按钮点击回调不要套用错误的多参数模板。
6. 从 `examples/templates/` 复制同语言模板开始改。
7. 运行 `python tools/validate_ai_sdk.py` 检查 AI SDK 文档一致性。

## Table 行级增删

- 生成普通表格增删改查界面时，可使用 `EU_AddTableRow`、`EU_InsertTableRow`、`EU_DeleteTableRow`、`EU_ClearTableRows` 或 Python helper `add_table_row`、`insert_table_row`、`delete_table_row`、`clear_table_rows`。
- 这些命令只适用于普通表格；虚表数据由 `EU_SetTableVirtualRowProvider` 的外部数据源维护。

## 窗口图标

- 需要设置任务栏/标题栏图标时，优先使用 `EU_SetWindowIcon(hwnd, path_bytes, path_len)` 传入 UTF-8 `.ico` 文件路径。
- 如果图标来自资源或网络数据，使用 `EU_SetWindowIconFromBytes(hwnd, icon_bytes, icon_len)` 传入 `.ico` 文件完整字节集。
- Python 可参考 `examples/python/window_icon_demo.py`，该示例保持窗口打开直到用户手动关闭。

## 窗口圆角

- 需要 Windows 窗口外形圆角时，使用 `EU_SetWindowRoundedCorners(hwnd, enabled, radius)` 或 Python helper `set_window_rounded_corners(hwnd, True, radius)`。
- 支持 DWM 圆角的系统会优先使用系统抗锯齿圆角；Win10 等旧系统主路径回退到 per-pixel alpha 分层窗口，并按当前 DPI / 屏幕缩放换算逻辑半径；如果 layered 连续提交失败，会退到真实窗口区域圆角。`enabled=0` 或 `radius<=0` 恢复矩形窗口。
- Python 可参考 `examples/python/window_rounded_corners_demo.py`，该示例保持窗口打开直到用户手动关闭。
