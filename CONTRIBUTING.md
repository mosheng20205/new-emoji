# 贡献指南

感谢你愿意改进 `new_emoji`。这个项目面向 Windows 原生 UI DLL、易语言交付、Python/C# 调用和中文 emoji 界面验证，贡献时请同时关注代码、导出、文档和测试的一致性。

## 开发环境

- Windows
- Visual Studio 2022
- MSVC v143
- Windows SDK 10.0
- C++17
- Python，用于 ctypes 示例和 UI 验证

## 构建

```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=x64
```

Win32 是易语言交付优先目标。提交前至少确认相关平台可以构建。

## 组件修改要求

如果修改某个组件，请同步检查：

- C++ Element 本体
- `exports.h`
- `exports.cpp`
- `src/new_emoji.def`
- `examples/python/new_emoji_ui.py`
- 对应 `tests/python/test_*_complete_components.py`
- `DLL命令/易语言DLL命令.md`
- `docs/components/<component>.md`
- `docs/components/README.md`
- `docs/api-index.md`

组件 API 发生变化时，组件文档必须同步更新，不能让文档和实际导出不一致。

## 文档生成

组件导航、组件文档和 API 索引可通过以下命令刷新：

```powershell
python .\tools\generate_docs.py
```

生成脚本读取 `docs/components/manifest.json` 和 `src/new_emoji.def`。如果组件名称、分类或中文名发生变化，请同步更新 manifest 或脚本中的映射。

## 示例与测试文案

- UI 示例使用中文文案。
- 窗口标题、主标题、主要按钮和核心展示项应包含合适 emoji。
- 首次窗口尺寸必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。
- UI 测试应保持窗口可见足够时间，避免闪退式验证。

## 提交建议

- 小步提交，避免把无关格式化和功能修改混在一起。
- 修改 DLL 导出时，在提交说明中列出新增、删除或签名变化的 API。
- 修复 bug 时尽量补充或更新独立测试文件。

## 许可证

提交到本项目的贡献默认按 MIT License 授权发布。
