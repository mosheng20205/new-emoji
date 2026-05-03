# API 约定

## 导出命名

所有新 DLL 导出统一使用 `EU_` 前缀，例如：

- `EU_CreateWindow`
- `EU_CreateButton`
- `EU_SetElementText`
- `EU_GetElementText`

## 文本编码

文本参数使用 UTF-8 字节数组 + 长度，不直接依赖调用方源码是否能保存 Unicode 或 emoji。

```cpp
int __stdcall EU_CreateButton(
    HWND hwnd,
    int parent_id,
    const unsigned char* emoji_bytes,
    int emoji_len,
    const unsigned char* text_bytes,
    int text_len,
    int x,
    int y,
    int w,
    int h
);
```

返回文本时通常由调用方提供缓冲区，DLL 返回写入的 UTF-8 字节数。

## 调用约定

导出 API 使用 `__stdcall`，便于易语言、C# P/Invoke 和 Python ctypes 调用。

## 尺寸与 DPI

Python helper 和 DLL API 中的窗口、控件坐标通常按逻辑尺寸传入。`EU_CreateWindow` 会在创建前读取目标显示器 DPI，并把逻辑尺寸换算到物理窗口尺寸。

新增示例时应保证首次打开窗口即可完整显示首屏内容，窗口和容器尺寸覆盖所有控件，并至少保留 20px 逻辑余量。

## 主题

组件应同时适配亮色和深色主题。涉及弹层、滚动条、hover、pressed、selected、disabled、focus 等子状态时，需要一起检查主题颜色。

## 文档同步

如果组件 API 发生变化，必须同步更新：

- 对应 `docs/components/*.md`
- `docs/components/README.md`
- `docs/api-index.md`
- `examples/python/new_emoji_ui.py`
- `DLL命令/易语言DLL命令.md`
- 必要时更新独立测试文件
