# Python 示例说明

Python 示例和测试使用 `ctypes` 加载 `new_emoji.dll`。推荐复用根目录的 `test_new_emoji.py`，其中已经声明了导出函数签名和常用 helper。

## 位数检查

```powershell
python -c "import struct; print(struct.calcsize('P') * 8, 'bit')"
```

32 位 Python 对应 Win32 DLL，64 位 Python 对应 x64 DLL。

## 示例要求

- 界面文案使用中文。
- 窗口标题、主标题、主要按钮和关键展示项应包含 emoji。
- 窗口首次打开时必须完整覆盖控件区域，并保留至少 20px 逻辑余量。
- UI 测试不要闪退，应保持可见足够时间。
