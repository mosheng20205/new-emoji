from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEF_FILE = ROOT / "src" / "new_emoji.def"
EXPORTS_H = ROOT / "src" / "exports.h"
COMMAND_DIR = ROOT / "DLL命令"
CSHARP_DOC = COMMAND_DIR / "CSharp DLL命令.md"
PYTHON_DOC = COMMAND_DIR / "Python DLL命令.md"


CALLBACKS = {
    "ElementClickCallback": {
        "cs": "ElementClickCallback",
        "py": "ElementClickCallback",
        "cs_decl": "public delegate void ElementClickCallback(int element_id);",
        "py_decl": "ElementClickCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int)",
    },
    "ElementKeyCallback": {
        "cs": "ElementKeyCallback",
        "py": "ElementKeyCallback",
        "cs_decl": "public delegate void ElementKeyCallback(int element_id, int vk_code, int key_down, int shift, int ctrl, int alt);",
        "py_decl": "ElementKeyCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)",
    },
    "ElementTextCallback": {
        "cs": "ElementTextCallback",
        "py": "ElementTextCallback",
        "cs_decl": "public delegate void ElementTextCallback(int element_id, IntPtr utf8, int len);",
        "py_decl": "ElementTextCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "ElementValueCallback": {
        "cs": "ElementValueCallback",
        "py": "ElementValueCallback",
        "cs_decl": "public delegate void ElementValueCallback(int element_id, int value, int range_start, int range_end);",
        "py_decl": "ElementValueCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)",
    },
    "ElementBeforeCloseCallback": {
        "cs": "ElementBeforeCloseCallback",
        "py": "ElementBeforeCloseCallback",
        "cs_decl": "public delegate int ElementBeforeCloseCallback(int element_id, int action);",
        "py_decl": "ElementBeforeCloseCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)",
    },
    "TableCellCallback": {
        "cs": "TableCellCallback",
        "py": "TableCellCallback",
        "cs_decl": "public delegate void TableCellCallback(int table_id, int row, int col, int action, int value);",
        "py_decl": "TableCellCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)",
    },
    "TableCellEditCallback": {
        "cs": "TableCellEditCallback",
        "py": "TableCellEditCallback",
        "cs_decl": "public delegate void TableCellEditCallback(int table_id, int row, int col, int action, IntPtr utf8, int len);",
        "py_decl": "TableCellEditCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "TableVirtualRowCallback": {
        "cs": "TableVirtualRowCallback",
        "py": "TableVirtualRowCallback",
        "cs_decl": "public delegate int TableVirtualRowCallback(int table_id, int row, IntPtr buffer, int buffer_size);",
        "py_decl": "TableVirtualRowCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "DropdownCommandCallback": {
        "cs": "DropdownCommandCallback",
        "py": "DropdownCommandCallback",
        "cs_decl": "public delegate void DropdownCommandCallback(int element_id, int item_index, IntPtr command_utf8, int command_len);",
        "py_decl": "DropdownCommandCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "MenuSelectCallback": {
        "cs": "MenuSelectCallback",
        "py": "MenuSelectCallback",
        "cs_decl": "public delegate void MenuSelectCallback(int element_id, int item_index, IntPtr path_utf8, int path_len, IntPtr command_utf8, int command_len);",
        "py_decl": "MenuSelectCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "WindowResizeCallback": {
        "cs": "WindowResizeCallback",
        "py": "WindowResizeCallback",
        "cs_decl": "public delegate void WindowResizeCallback(IntPtr hwnd, int width, int height);",
        "py_decl": "WindowResizeCallback = ctypes.WINFUNCTYPE(None, wintypes.HWND, ctypes.c_int, ctypes.c_int)",
    },
    "WindowCloseCallback": {
        "cs": "WindowCloseCallback",
        "py": "WindowCloseCallback",
        "cs_decl": "public delegate void WindowCloseCallback(IntPtr hwnd);",
        "py_decl": "WindowCloseCallback = ctypes.WINFUNCTYPE(None, wintypes.HWND)",
    },
    "MessageBoxResultCallback": {
        "cs": "MessageBoxResultCallback",
        "py": "MessageBoxResultCallback",
        "cs_decl": "public delegate void MessageBoxResultCallback(int messagebox_id, int result);",
        "py_decl": "MessageBoxResultCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int)",
    },
    "MessageBoxExCallback": {
        "cs": "MessageBoxExCallback",
        "py": "MessageBoxExCallback",
        "cs_decl": "public delegate void MessageBoxExCallback(int messagebox_id, int action, IntPtr value_utf8, int value_len);",
        "py_decl": "MessageBoxExCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "TreeNodeEventCallback": {
        "cs": "TreeNodeEventCallback",
        "py": "TreeNodeEventCallback",
        "cs_decl": "public delegate void TreeNodeEventCallback(int element_id, int event_code, int item_index, IntPtr payload_utf8, int payload_len);",
        "py_decl": "TreeNodeEventCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "TreeNodeAllowDragCallback": {
        "cs": "TreeNodeAllowDragCallback",
        "py": "TreeNodeAllowDragCallback",
        "cs_decl": "public delegate int TreeNodeAllowDragCallback(int element_id, IntPtr key_utf8, int key_len);",
        "py_decl": "TreeNodeAllowDragCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)",
    },
    "TreeNodeAllowDropCallback": {
        "cs": "TreeNodeAllowDropCallback",
        "py": "TreeNodeAllowDropCallback",
        "cs_decl": "public delegate int TreeNodeAllowDropCallback(int element_id, IntPtr drag_key_utf8, int drag_key_len, IntPtr drop_key_utf8, int drop_key_len, int drop_type);",
        "py_decl": "TreeNodeAllowDropCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int)",
    },
    "DateDisabledCallback": {
        "cs": "DateDisabledCallback",
        "py": "DateDisabledCallback",
        "cs_decl": "public delegate int DateDisabledCallback(int id, int yyyymmdd);",
        "py_decl": "DateDisabledCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)",
    },
}


CS_KEYWORDS = {
    "base", "bool", "break", "byte", "case", "catch", "char", "checked",
    "class", "const", "continue", "decimal", "default", "delegate", "do",
    "double", "else", "enum", "event", "explicit", "extern", "false",
    "finally", "fixed", "float", "for", "foreach", "goto", "if", "implicit",
    "in", "int", "interface", "internal", "is", "lock", "long", "namespace",
    "new", "null", "object", "operator", "out", "override", "params",
    "private", "protected", "public", "readonly", "ref", "return", "sbyte",
    "sealed", "short", "sizeof", "stackalloc", "static", "string", "struct",
    "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong",
    "unchecked", "unsafe", "ushort", "using", "virtual", "void", "volatile",
    "while",
}


def parse_exports() -> list[str]:
    exports: list[str] = []
    in_exports = False
    for raw in DEF_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        if line.upper() == "EXPORTS":
            in_exports = True
            continue
        if in_exports:
            exports.append(line.split()[0])
    return exports


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\n", " ")).strip()


def split_params(params: str) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in params:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            result.append(normalize_space("".join(current)))
            current = []
            continue
        current.append(ch)
    tail = normalize_space("".join(current))
    if tail and tail != "void":
        result.append(tail)
    return result


def parse_param(param: str) -> tuple[str, str]:
    fnptr = re.match(r"int\s+\(\*\s*(\w+)\s*\)\s*\(\s*int\s+\w+\s*,\s*int\s+\w+\s*\)$", param)
    if fnptr:
        return "DateDisabledCallback", fnptr.group(1)
    match = re.match(r"(.+?)\s*([A-Za-z_]\w*)$", param)
    if not match:
        raise ValueError(f"Cannot parse parameter: {param}")
    return normalize_space(match.group(1)), match.group(2)


def parse_prototypes() -> dict[str, dict[str, object]]:
    text = EXPORTS_H.read_text(encoding="utf-8")
    pattern = re.compile(r"([\w\s\*]+?)\s+__stdcall\s+(EU_\w+)\s*\((.*?)\);", re.S)
    prototypes: dict[str, dict[str, object]] = {}
    for return_type, name, params in pattern.findall(text):
        parsed_params = [parse_param(param) for param in split_params(params)]
        prototypes[name] = {
            "return_type": normalize_space(return_type),
            "params": parsed_params,
        }
    return prototypes


def cs_name(name: str) -> str:
    return f"@{name}" if name in CS_KEYWORDS else name


def cs_type(c_type: str) -> str:
    mapping = {
        "void": "void",
        "int": "int",
        "HWND": "IntPtr",
        "Color": "uint",
        "unsigned int": "uint",
        "long long": "long",
        "float": "float",
        "const unsigned char*": "byte[]",
        "unsigned char*": "byte[]",
        "int*": "IntPtr",
        "const int*": "IntPtr",
        "Color*": "IntPtr",
        "const Color*": "IntPtr",
        "float*": "IntPtr",
        "long long*": "IntPtr",
    }
    if c_type in CALLBACKS:
        return CALLBACKS[c_type]["cs"]
    return mapping.get(c_type, "IntPtr")


def py_type(c_type: str) -> str:
    mapping = {
        "int": "ctypes.c_int",
        "HWND": "wintypes.HWND",
        "Color": "ctypes.c_uint32",
        "unsigned int": "ctypes.c_uint32",
        "long long": "ctypes.c_longlong",
        "float": "ctypes.c_float",
        "const unsigned char*": "ctypes.POINTER(ctypes.c_ubyte)",
        "unsigned char*": "ctypes.POINTER(ctypes.c_ubyte)",
        "int*": "ctypes.POINTER(ctypes.c_int)",
        "const int*": "ctypes.POINTER(ctypes.c_int)",
        "Color*": "ctypes.POINTER(ctypes.c_uint32)",
        "const Color*": "ctypes.POINTER(ctypes.c_uint32)",
        "float*": "ctypes.POINTER(ctypes.c_float)",
        "long long*": "ctypes.POINTER(ctypes.c_longlong)",
    }
    if c_type in CALLBACKS:
        return CALLBACKS[c_type]["py"]
    return mapping.get(c_type, "ctypes.c_void_p")


def cs_return(c_type: str) -> str:
    return {
        "void": "void",
        "int": "int",
        "HWND": "IntPtr",
        "Color": "uint",
        "unsigned int": "uint",
        "long long": "long",
        "float": "float",
    }.get(c_type, "IntPtr")


def py_return(c_type: str) -> str:
    return {
        "void": "None",
        "int": "ctypes.c_int",
        "HWND": "wintypes.HWND",
        "Color": "ctypes.c_uint32",
        "unsigned int": "ctypes.c_uint32",
        "long long": "ctypes.c_longlong",
        "float": "ctypes.c_float",
    }.get(c_type, "ctypes.c_void_p")


def cs_signature(name: str, proto: dict[str, object]) -> str:
    params = proto["params"]
    assert isinstance(params, list)
    pieces = [f"{cs_type(c_type)} {cs_name(param_name)}" for c_type, param_name in params]
    joined = ", ".join(pieces)
    return (
        '[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]\n'
        f"public static extern {cs_return(str(proto['return_type']))} {name}({joined});"
    )


def py_signature(name: str, proto: dict[str, object]) -> str:
    params = proto["params"]
    assert isinstance(params, list)
    argtypes = ", ".join(py_type(c_type) for c_type, _ in params)
    if argtypes:
        first = f"dll.{name}.argtypes = [{argtypes}]"
    else:
        first = f"dll.{name}.argtypes = []"
    return f"{first}\ndll.{name}.restype = {py_return(str(proto['return_type']))}"


def csharp_doc(exports: list[str], prototypes: dict[str, dict[str, object]]) -> str:
    callback_decls = "\n".join(f"[UnmanagedFunctionPointer(CallingConvention.StdCall)]\n{item['cs_decl']}" for item in CALLBACKS.values())
    rows = []
    for name in exports:
        proto = prototypes[name]
        rows.append(f"## {name}\n\n```csharp\n{cs_signature(name, proto)}\n```\n")
    return f"""# new_emoji.dll C# DLL 命令

本文件记录 `new_emoji.dll` 的 C# P/Invoke 声明，按 `src/new_emoji.def` 和 `src/exports.h` 生成。
当前导出命令数量：{len(exports)}。

推荐普通 C# 程序优先使用 `bindings/csharp/NewEmoji` 对象式封装库；本文件作为高级能力和底层 P/Invoke 参考。

通用约定：
- x86 应用加载 `bin/Win32/Release/new_emoji.dll`，x64 应用加载 `bin/x64/Release/new_emoji.dll`。
- 所有导出 API 使用 `CallingConvention.StdCall`。
- `HWND` 使用 `IntPtr`，`Color` 使用 `uint`，颜色格式为 ARGB：`0xAARRGGBB`。
- 文本参数按 UTF-8 字节数组 + 长度传入；示例 helper 可用 `Encoding.UTF8.GetBytes(text)` 生成 `byte[]`。
- 输出指针和数组类参数在本文件中保守使用 `IntPtr` 或 `byte[]`，复杂场景可按实际缓冲区改成 pinned array。
- 回调 delegate 必须由调用方保存引用，避免被 GC 回收。

## 基础 using

```csharp
using System;
using System.Runtime.InteropServices;
using System.Text;
```

## 回调 delegate

```csharp
{callback_decls}
```

## 导出声明

{''.join(rows)}""".rstrip() + "\n"


def python_doc(exports: list[str], prototypes: dict[str, dict[str, object]]) -> str:
    callback_decls = "\n".join(item["py_decl"] for item in CALLBACKS.values())
    rows = []
    for name in exports:
        proto = prototypes[name]
        rows.append(f"## {name}\n\n```python\n{py_signature(name, proto)}\n```\n")
    return f"""# new_emoji.dll Python DLL 命令

本文件记录 `new_emoji.dll` 的 Python `ctypes` 声明，按 `src/new_emoji.def` 和 `src/exports.h` 生成。
当前导出命令数量：{len(exports)}。

通用约定：
- 32 位 Python 加载 `bin/Win32/Release/new_emoji.dll`，64 位 Python 加载 `bin/x64/Release/new_emoji.dll`。
- 使用 `ctypes.WinDLL` 加载 DLL，匹配 `__stdcall` 调用约定。
- 文本参数按 UTF-8 bytes + 长度传入；可用 `text.encode("utf-8")` 生成字节。
- 输出文本由调用方创建 `ctypes.create_string_buffer(size)` 或 `ctypes.c_ubyte` 数组后传入。
- 回调使用 `ctypes.WINFUNCTYPE`，并且必须保存 Python 回调对象引用，避免被垃圾回收。
- 公共 helper 位于 `examples/python/new_emoji_ui.py`，普通示例建议优先复用 helper。

## 基础导入

```python
import ctypes
from ctypes import wintypes

dll = ctypes.WinDLL("new_emoji.dll")
```

## 回调类型

```python
{callback_decls}
```

## 导出声明

{''.join(rows)}""".rstrip() + "\n"


def main() -> None:
    exports = parse_exports()
    prototypes = parse_prototypes()
    missing = [name for name in exports if name not in prototypes]
    if missing:
        raise SystemExit(f"Missing prototypes for exports: {', '.join(missing[:20])}")
    COMMAND_DIR.mkdir(exist_ok=True)
    with CSHARP_DOC.open("w", encoding="utf-8", newline="\n") as fp:
        fp.write(csharp_doc(exports, prototypes))
    with PYTHON_DOC.open("w", encoding="utf-8", newline="\n") as fp:
        fp.write(python_doc(exports, prototypes))
    print(f"Wrote {CSHARP_DOC.relative_to(ROOT)}")
    print(f"Wrote {PYTHON_DOC.relative_to(ROOT)}")
    print(f"Export count: {len(exports)}")


if __name__ == "__main__":
    main()
