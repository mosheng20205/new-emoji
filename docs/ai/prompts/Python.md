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
- Table 普通表格行级增删优先使用 `add_table_row`、`insert_table_row`、`delete_table_row`、`clear_table_rows`；虚表数据由 provider 维护。
```
