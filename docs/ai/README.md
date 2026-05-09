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
5. 从 `examples/templates/` 复制同语言模板开始改。
6. 运行 `python tools/validate_ai_sdk.py` 检查 AI SDK 文档一致性。

## Table 行级增删

- 生成普通表格增删改查界面时，可使用 `EU_AddTableRow`、`EU_InsertTableRow`、`EU_DeleteTableRow`、`EU_ClearTableRows` 或 Python helper `add_table_row`、`insert_table_row`、`delete_table_row`、`clear_table_rows`。
- 这些命令只适用于普通表格；虚表数据由 `EU_SetTableVirtualRowProvider` 的外部数据源维护。
