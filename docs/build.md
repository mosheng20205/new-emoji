# 构建说明

## 环境要求

- Windows
- Visual Studio 2022
- MSVC v143
- Windows SDK 10.0
- C++17
- 源码按 UTF-8 编译

## Release 构建

Win32，易语言交付优先目标：

```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
```

x64：

```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=x64
```

## 输出目录

- `bin/Win32/Release/new_emoji.dll`
- `bin/x64/Release/new_emoji.dll`

## 验证建议

组件级验证优先运行对应的 `test_*_complete_components.py`。UI 测试应保持窗口可见足够时间，确认中文、emoji、DPI、首次窗口尺寸和交互行为正常。
