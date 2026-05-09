# Python AI Prompt

```text
你正在使用 new_emoji.dll 为 Python 生成 Windows 原生 UI。

请优先阅读：
1. examples/python/new_emoji_ui.py
2. docs/ai/api_manifest.full.json
3. docs/components/README.md
4. examples/templates/python/blank_window.py

规则：
- 普通示例优先 import examples/python/new_emoji_ui.py，不要重复手写 ctypes 签名。
- 不要从 tests/python 导入 helper。
- Python 位数必须和 DLL 位数一致。
- 界面文案必须中文化，窗口标题、主按钮、核心展示项必须有 emoji。
- 窗口和根容器首次打开时不能裁切控件，要保留至少 20px 逻辑余量。
- 设置窗口任务栏/标题栏图标时，使用 `set_window_icon(hwnd, ico_path)` 或 `set_window_icon_from_bytes(hwnd, ico_bytes)`，底层分别绑定 `EU_SetWindowIcon` 和 `EU_SetWindowIconFromBytes`。
- 设置 Windows 窗口外形圆角时，使用 `set_window_rounded_corners(hwnd, True, radius)`；支持 DWM 的系统会优先使用平滑圆角，Win10 会回退为 per-pixel alpha 分层窗口并通过 `UpdateLayeredWindow(ULW_ALPHA)` 提交。
- 窗口图标示例可参考 `examples/python/window_icon_demo.py`；示例窗口应进入消息循环，不能自动关闭。
- 窗口圆角示例可参考 `examples/python/window_rounded_corners_demo.py`；示例窗口应进入消息循环，不能自动关闭。
- Table 普通表格行级增删优先使用 `add_table_row`、`insert_table_row`、`delete_table_row`、`clear_table_rows`；虚表数据由 provider 维护。
```
