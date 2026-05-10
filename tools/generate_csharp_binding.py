from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTS_H = ROOT / "src" / "exports.h"
COMPONENT_MANIFEST = ROOT / "docs" / "components" / "manifest.json"
CSHARP_ROOT = ROOT / "bindings" / "csharp" / "NewEmoji"
NATIVE_DIR = CSHARP_ROOT / "Native"
UI_DIR = CSHARP_ROOT / "UI"


CALLBACKS = {
    "ElementClickCallback": "public delegate void ElementClickCallback(int elementId);",
    "ElementKeyCallback": "public delegate void ElementKeyCallback(int elementId, int vkCode, int keyDown, int shift, int ctrl, int alt);",
    "ElementTextCallback": "public delegate void ElementTextCallback(int elementId, IntPtr utf8, int len);",
    "ElementValueCallback": "public delegate void ElementValueCallback(int elementId, int value, int rangeStart, int rangeEnd);",
    "ElementReorderCallback": "public delegate void ElementReorderCallback(int elementId, int fromIndex, int toIndex, int count);",
    "ElementBeforeCloseCallback": "public delegate int ElementBeforeCloseCallback(int elementId, int action);",
    "DateDisabledCallback": "public delegate int DateDisabledCallback(int elementId, int yyyymmdd);",
    "TableCellCallback": "public delegate void TableCellCallback(int tableId, int row, int col, int action, int value);",
    "TableCellEditCallback": "public delegate void TableCellEditCallback(int tableId, int row, int col, int action, IntPtr utf8, int len);",
    "TableVirtualRowCallback": "public delegate int TableVirtualRowCallback(int tableId, int row, IntPtr buffer, int bufferSize);",
    "DropdownCommandCallback": "public delegate void DropdownCommandCallback(int elementId, int itemIndex, IntPtr commandUtf8, int commandLen);",
    "MenuSelectCallback": "public delegate void MenuSelectCallback(int elementId, int itemIndex, IntPtr pathUtf8, int pathLen, IntPtr commandUtf8, int commandLen);",
    "WindowResizeCallback": "public delegate void WindowResizeCallback(IntPtr hwnd, int width, int height);",
    "WindowCloseCallback": "public delegate void WindowCloseCallback(IntPtr hwnd);",
    "WindowDestroyCallback": "public delegate void WindowDestroyCallback(IntPtr hwnd);",
    "MessageBoxResultCallback": "public delegate void MessageBoxResultCallback(int messageBoxId, int result);",
    "MessageBoxExCallback": "public delegate void MessageBoxExCallback(int messageBoxId, int action, IntPtr valueUtf8, int valueLen);",
    "TreeNodeEventCallback": "public delegate void TreeNodeEventCallback(int elementId, int eventCode, int itemIndex, IntPtr payloadUtf8, int payloadLen);",
    "TreeNodeAllowDragCallback": "public delegate int TreeNodeAllowDragCallback(int elementId, IntPtr keyUtf8, int keyLen);",
    "TreeNodeAllowDropCallback": "public delegate int TreeNodeAllowDropCallback(int elementId, IntPtr dragKeyUtf8, int dragKeyLen, IntPtr dropKeyUtf8, int dropKeyLen, int dropType);",
}


CS_KEYWORDS = {
    "base",
    "bool",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "checked",
    "class",
    "const",
    "continue",
    "decimal",
    "default",
    "delegate",
    "do",
    "double",
    "else",
    "enum",
    "event",
    "explicit",
    "extern",
    "false",
    "finally",
    "fixed",
    "float",
    "for",
    "foreach",
    "goto",
    "if",
    "implicit",
    "in",
    "int",
    "interface",
    "internal",
    "is",
    "lock",
    "long",
    "namespace",
    "new",
    "null",
    "object",
    "operator",
    "out",
    "override",
    "params",
    "private",
    "protected",
    "public",
    "readonly",
    "ref",
    "return",
    "sbyte",
    "sealed",
    "short",
    "sizeof",
    "stackalloc",
    "static",
    "string",
    "struct",
    "switch",
    "this",
    "throw",
    "true",
    "try",
    "typeof",
    "uint",
    "ulong",
    "unchecked",
    "unsafe",
    "ushort",
    "using",
    "virtual",
    "void",
    "volatile",
    "while",
}


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
            tail = normalize_space("".join(current))
            if tail and tail != "void":
                result.append(tail)
            current = []
            continue
        current.append(ch)

    tail = normalize_space("".join(current))
    if tail and tail != "void":
        result.append(tail)
    return result


def parse_param(param: str) -> tuple[str, str]:
    match = re.match(r"(.+?)\s*([A-Za-z_]\w*)$", param)
    if not match:
        raise ValueError(f"Cannot parse parameter: {param}")
    return normalize_space(match.group(1)), match.group(2)


def parse_prototypes() -> dict[str, dict[str, object]]:
    text = EXPORTS_H.read_text(encoding="utf-8")
    pattern = re.compile(r"([\w\s\*]+?)\s+__stdcall\s+(EU_\w+)\s*\((.*?)\);", re.S)
    prototypes: dict[str, dict[str, object]] = {}
    for return_type, name, params in pattern.findall(text):
        prototypes[name] = {
            "return_type": normalize_space(return_type),
            "params": [parse_param(param) for param in split_params(params)],
        }
    return prototypes


def cs_name(name: str) -> str:
    return f"@{name}" if name in CS_KEYWORDS else name


def pascal_name(name: str) -> str:
    parts = [part for part in re.split(r"[_\-\s]+", name) if part]
    return "".join(part[:1].upper() + part[1:] for part in parts)


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
        return c_type
    return mapping.get(c_type, "IntPtr")


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


def generated_header() -> str:
    return (
        "// <auto-generated />\n"
        "// Generated by tools/generate_csharp_binding.py. Do not edit by hand.\n"
        "\n"
    )


def write_native_callbacks() -> None:
    lines = [
        generated_header(),
        "using System;\n",
        "using System.Runtime.InteropServices;\n\n",
        "namespace NewEmoji.Native;\n\n",
    ]
    for _, declaration in CALLBACKS.items():
        lines.append("[UnmanagedFunctionPointer(CallingConvention.StdCall)]\n")
        lines.append(f"{declaration}\n\n")
    write_file(NATIVE_DIR / "NativeCallbacks.Generated.cs", "".join(lines).rstrip() + "\n")


def write_native_methods(prototypes: dict[str, dict[str, object]]) -> None:
    lines = [
        generated_header(),
        "using System;\n",
        "using System.Runtime.InteropServices;\n\n",
        "namespace NewEmoji.Native;\n\n",
        "public static partial class NativeMethods\n",
        "{\n",
        '    internal const string DllName = "new_emoji.dll";\n\n',
    ]

    for name, proto in prototypes.items():
        return_type = cs_return(str(proto["return_type"]))
        params = proto["params"]
        rendered_params = ", ".join(
            f"{cs_type(c_type)} {cs_name(param_name)}" for c_type, param_name in params  # type: ignore[assignment]
        )
        lines.append("    [DllImport(DllName, CallingConvention = CallingConvention.StdCall)]\n")
        lines.append(f"    public static extern {return_type} {name}({rendered_params});\n\n")

    lines.append("}\n")
    write_file(NATIVE_DIR / "NativeMethods.Generated.cs", "".join(lines))


def get_components() -> list[dict]:
    return json.loads(COMPONENT_MANIFEST.read_text(encoding="utf-8-sig"))


def param_public_name(native_name: str) -> str:
    name = native_name
    if name.endswith("_bytes"):
        name = name[: -len("_bytes")]
    if name == "w":
        return "width"
    if name == "h":
        return "height"
    return cs_name(name)


def component_public_params(params: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    public: list[tuple[str, str, str]] = []
    i = 2  # skip HWND hwnd, int parent_id
    while i < len(params):
        c_type, name = params[i]
        if c_type == "const unsigned char*" and i + 1 < len(params) and params[i + 1][1].endswith("_len"):
            public.append(("string", param_public_name(name), name))
            i += 2
            continue
        public.append((cs_type(c_type), param_public_name(name), name))
        i += 1
    return public


def component_call_args(params: list[tuple[str, str]]) -> list[str]:
    args = ["window.Handle", "parentId"]
    i = 2
    while i < len(params):
        c_type, name = params[i]
        if c_type == "const unsigned char*" and i + 1 < len(params) and params[i + 1][1].endswith("_len"):
            public_name = param_public_name(name).lstrip("@")
            bytes_name = f"{public_name}Bytes"
            args.append(bytes_name)
            args.append(f"{bytes_name}.Length")
            i += 2
            continue
        args.append(param_public_name(name))
        i += 1
    return args


def write_generated_components(prototypes: dict[str, dict[str, object]]) -> None:
    create_names: list[str] = []
    for component in get_components():
        create_export = component["create"].split("/")[0].strip()
        if create_export.startswith("EU_Create") and create_export in prototypes:
            proto = prototypes[create_export]
            params = proto["params"]
            if len(params) >= 2 and params[0] == ("HWND", "hwnd") and params[1] == ("int", "parent_id"):
                create_names.append(create_export)

    lines = [
        generated_header(),
        "using System;\n",
        "using NewEmoji.Native;\n\n",
        "namespace NewEmoji;\n\n",
        "public static class EmojiGeneratedComponents\n",
        "{\n",
    ]

    for export_name in create_names:
        component_name = export_name.removeprefix("EU_Create")
        public_params = component_public_params(prototypes[export_name]["params"])  # type: ignore[arg-type]
        signature = ", ".join(["this EmojiWindow window", "int parentId"] + [f"{typ} {name}" for typ, name, _ in public_params])
        call_args = component_call_args(prototypes[export_name]["params"])  # type: ignore[arg-type]
        lines.append(f"    public static EmojiElement Create{component_name}(this EmojiWindow window, int parentId")
        for typ, name, _ in public_params:
            lines.append(f", {typ} {name}")
        lines.append(")\n")
        lines.append("    {\n")
        lines.append("        if (window is null) throw new ArgumentNullException(nameof(window));\n")
        for typ, name, native_name in public_params:
            if typ == "string":
                bytes_name = f"{name.lstrip('@')}Bytes"
                lines.append(f"        var {bytes_name} = NativeUtf8.GetBytes({name});\n")
        lines.append(f"        var id = NativeMethods.{export_name}({', '.join(call_args)});\n")
        lines.append(f'        return EmojiElement.Wrap(window, id, "{component_name}");\n')
        lines.append("    }\n\n")

        add_signature = ", ".join(["this EmojiElement parent"] + [f"{typ} {name}" for typ, name, _ in public_params])
        lines.append(f"    public static EmojiElement Add{component_name}({add_signature})\n")
        lines.append("    {\n")
        lines.append("        if (parent is null) throw new ArgumentNullException(nameof(parent));\n")
        rendered_args = ", ".join(["parent.Id"] + [name for _, name, _ in public_params])
        lines.append(f"        return parent.Window.Create{component_name}({rendered_args});\n")
        lines.append("    }\n\n")

    lines.append("}\n")
    write_file(UI_DIR / "GeneratedComponents.cs", "".join(lines))


def write_file(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fp:
        fp.write(text)


def main() -> None:
    NATIVE_DIR.mkdir(parents=True, exist_ok=True)
    UI_DIR.mkdir(parents=True, exist_ok=True)
    prototypes = parse_prototypes()
    write_native_callbacks()
    write_native_methods(prototypes)
    write_generated_components(prototypes)
    print(f"Wrote C# bindings to {CSHARP_ROOT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
