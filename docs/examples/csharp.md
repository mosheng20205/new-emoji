# C# 接入说明

C# 可通过 P/Invoke 调用 `new_emoji.dll`。注意应用进程位数必须和 DLL 位数一致。

## 建议

- x86 应用加载 Win32 DLL。
- x64 应用加载 x64 DLL。
- 文本参数按 UTF-8 byte array 传递。
- 回调保持 `StdCall` 调用约定。

更完整的 P/Invoke 声明可参考导出表 `new_emoji.def` 和 Python ctypes 封装 `test_new_emoji.py`。
