from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEF_FILE = ROOT / "src" / "new_emoji.def"
EXPORTS_H = ROOT / "src" / "exports.h"
COMPONENT_MANIFEST = ROOT / "docs" / "components" / "manifest.json"
AI_MANIFEST = ROOT / "docs" / "ai" / "api_manifest.full.json"
E_LANG_DOC = ROOT / "DLL命令" / "易语言DLL命令.md"

MODULE_DIR = ROOT / "examples" / "火山" / "new_emoji_module"
MODULE_SRC = MODULE_DIR / "src"
MODULE_RUNTIME = MODULE_DIR / "runtime"
MODULE_INTERFACE = MODULE_SRC / "new_emoji_接口.wsv"
MODULE_HELPER = MODULE_SRC / "new_emoji_助手.wsv"
MODULE_VGRP = MODULE_DIR / "new_emoji.vgrp"
MODULE_README = MODULE_DIR / "README.md"

DEMO_VSLN = ROOT / "examples" / "火山" / "NewEmojiModuleDemo_x64.vsln"
DEMO_VPRJ = ROOT / "examples" / "火山" / "NewEmojiModuleDemo_x64.vprj"
DEMO_SOURCE = ROOT / "examples" / "火山" / "src" / "module_demo.wsv"
DEMO_RUNTIME = ROOT / "examples" / "火山" / "runtime_x64"

PROGRESS_FILE = ROOT / "火山组件模块封装进度.md"

UTF16 = "utf-16"
UTF8 = "utf-8"


CALLBACK_TYPES = {
    "DateDisabledCallback",
    "DropdownCommandCallback",
    "ElementBeforeCloseCallback",
    "ElementClickCallback",
    "ElementKeyCallback",
    "ElementReorderCallback",
    "ElementTextCallback",
    "ElementValueCallback",
    "MenuSelectCallback",
    "MessageBoxExCallback",
    "MessageBoxResultCallback",
    "TableCellCallback",
    "TableVirtualRowCallback",
    "TreeNodeAllowDragCallback",
    "TreeNodeAllowDropCallback",
    "TreeNodeEventCallback",
    "WindowCloseCallback",
    "WindowResizeCallback",
}

VOLCANO_TYPE_MAP = {
    "void": "",
    "int": "整数",
    "HWND": "变整数",
    "Color": "整数",
    "unsigned int": "整数",
    "long long": "长整数",
    "float": "小数",
    "const unsigned char*": "变整数",
    "unsigned char*": "变整数",
    "int*": "变整数",
    "const int*": "变整数",
    "Color*": "变整数",
    "const Color*": "变整数",
    "float*": "变整数",
    "long long*": "变整数",
}

OLD_INTERFACE_ALIASES = {
    "EU_CreateWindow": ["创建窗口_字节集"],
    "EU_CreateText": ["创建文本_字节集"],
    "EU_CreateButton": ["创建按钮_字节集"],
    "EU_SetWindowTitle": ["设置窗口标题_字节集"],
    "EU_SetWindowIcon": ["设置窗口图标_字节集"],
    "EU_SetWindowIconFromBytes": ["设置窗口图标文件字节集_字节集"],
    "EU_SetElementText": ["设置元素文本_字节集"],
    "EU_SetEditBoxText": ["设置编辑框文本_字节集"],
    "EU_SetElementFont": ["设置元素字体_字节集"],
    "EU_SetButtonVariant": ["设置按钮样式"],
}

COMMON_HELPERS = {
    "EU_CreateWindow",
    "EU_CreateWindowDark",
    "EU_DestroyWindow",
    "EU_ShowWindow",
    "EU_RunMessageLoop",
    "EU_SetWindowTitle",
    "EU_SetWindowIcon",
    "EU_SetWindowIconFromBytes",
    "EU_SetWindowBounds",
    "EU_SetElementText",
    "EU_SetEditBoxText",
    "EU_SetElementColor",
    "EU_SetElementFont",
    "EU_SetTextOptions",
    "EU_SetButtonVariant",
    "EU_SetElementClickCallback",
    "EU_SetDarkMode",
    "EU_SetThemeMode",
    "EU_SetThemeColor",
    "EU_SetWindowRoundedCorners",
}


@dataclass(frozen=True)
class Param:
    c_type: str
    name: str
    doc_name: str | None = None


@dataclass(frozen=True)
class Prototype:
    name: str
    return_type: str
    params: tuple[Param, ...]
    command_name: str


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
    fnptr = re.match(r"int\s+\(\*\s*(\w+)\s*\)\s*\(.*?\)$", param)
    if fnptr:
        return "DateDisabledCallback", fnptr.group(1)
    match = re.match(r"(.+?)\s*([A-Za-z_]\w*)$", param)
    if not match:
        raise ValueError(f"Cannot parse parameter: {param}")
    return normalize_space(match.group(1)), match.group(2)


def load_exports() -> list[str]:
    exports: list[str] = []
    in_exports = False
    for raw in DEF_FILE.read_text(encoding=UTF8).splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        if line.upper() == "EXPORTS":
            in_exports = True
            continue
        if in_exports:
            exports.append(line.split()[0])
    return exports


def load_e_language_docs() -> dict[str, dict[str, object]]:
    text = E_LANG_DOC.read_text(encoding=UTF8)
    result: dict[str, dict[str, object]] = {}
    current_export: str | None = None
    for raw in text.splitlines():
        command_match = re.match(r"\.DLL命令\s+([^,]+),.*?\"(EU_\w+)\"", raw)
        if command_match:
            command, export = command_match.groups()
            current_export = export
            result[export] = {"command": command.strip(), "params": []}
            continue
        param_match = re.match(r"\s*\.参数\s+([^,]+)", raw)
        if param_match and current_export:
            result[current_export]["params"].append(param_match.group(1).strip())
    return result


def sanitize_volcano_name(value: str, fallback: str) -> str:
    value = value.strip() or fallback
    value = value.replace("（", "_").replace("）", "_").replace("(", "_").replace(")", "_")
    chars: list[str] = []
    for ch in value:
        if ch == "_" or ch.isalnum() or "\u4e00" <= ch <= "\u9fff":
            chars.append(ch)
        else:
            chars.append("_")
    name = re.sub(r"_+", "_", "".join(chars)).strip("_")
    if not name:
        name = fallback
    if name[0].isdigit():
        name = "参数" + name
    return name


def unique_name(base: str, used: set[str], suffix: str) -> str:
    if base not in used:
        used.add(base)
        return base
    candidate = sanitize_volcano_name(f"{base}_{suffix}", f"{base}_{suffix}")
    index = 2
    while candidate in used:
        candidate = sanitize_volcano_name(f"{base}_{suffix}_{index}", f"{base}_{suffix}_{index}")
        index += 1
    used.add(candidate)
    return candidate


def parse_prototypes() -> dict[str, Prototype]:
    e_docs = load_e_language_docs()
    text = EXPORTS_H.read_text(encoding=UTF8)
    pattern = re.compile(r"([\w\s\*]+?)\s+__stdcall\s+(EU_\w+)\s*\((.*?)\);", re.S)
    parsed: dict[str, Prototype] = {}
    used_commands: set[str] = set()
    for return_type, name, params in pattern.findall(text):
        doc = e_docs.get(name, {})
        doc_params = list(doc.get("params", []))
        parsed_params: list[Param] = []
        raw_params = [parse_param(param) for param in split_params(params)]
        for index, (c_type, param_name) in enumerate(raw_params):
            doc_name = doc_params[index] if index < len(doc_params) else None
            parsed_params.append(Param(c_type=c_type, name=param_name, doc_name=doc_name))
        fallback_command = name.removeprefix("EU_")
        command = sanitize_volcano_name(str(doc.get("command", fallback_command)), fallback_command)
        command = unique_name(command, used_commands, name.removeprefix("EU_"))
        parsed[name] = Prototype(
            name=name,
            return_type=normalize_space(return_type),
            params=tuple(parsed_params),
            command_name=command,
        )
    return parsed


def volcano_type(c_type: str) -> str:
    if c_type in CALLBACK_TYPES:
        return "变整数"
    if c_type in VOLCANO_TYPE_MAP:
        return VOLCANO_TYPE_MAP[c_type]
    if c_type.endswith("*"):
        return "变整数"
    raise ValueError(f"Unsupported C type for Volcano mapping: {c_type}")


def method_type_attr(return_type: str) -> str:
    v_type = volcano_type(return_type)
    return f" 类型 = {v_type}" if v_type else ""


def param_name(param: Param, fallback: str) -> str:
    return sanitize_volcano_name(param.doc_name or param.name, fallback)


def format_import_method(proto: Prototype, method_name: str | None = None) -> str:
    name = method_name or proto.command_name
    lines = [
        f'    方法 {name} <公开 静态{method_type_attr(proto.return_type)} @视窗.输入 = "new_emoji.dll" @输出名 = "{proto.name}">'
    ]
    used: set[str] = set()
    for index, param in enumerate(proto.params, start=1):
        p_name = unique_name(param_name(param, f"参数{index}"), used, str(index))
        lines.append(f"    参数 {p_name} <类型 = {volcano_type(param.c_type)}>")
    return "\n".join(lines)


def format_alias_wrapper(proto: Prototype, alias: str) -> str:
    lines = [f"    方法 {alias} <公开 静态{method_type_attr(proto.return_type)}>"]
    used: set[str] = set()
    call_args: list[str] = []
    for index, param in enumerate(proto.params, start=1):
        p_name = unique_name(param_name(param, f"参数{index}"), used, str(index))
        call_args.append(p_name)
        lines.append(f"    参数 {p_name} <类型 = {volcano_type(param.c_type)}>")
    call = f"NewEmoji接口类.{proto.command_name} (" + ", ".join(call_args) + ")"
    lines.append("    {")
    if volcano_type(proto.return_type):
        lines.append(f"        返回 ({call})")
    else:
        lines.append(f"        {call}")
    lines.append("    }")
    return "\n".join(lines)


def render_interface(prototypes: dict[str, Prototype], exports: list[str]) -> str:
    lines = [
        '<火山程序 类型 = "通常" 版本 = 1 />',
        "",
        "包 火山.NewEmoji",
        "",
        '类 NewEmoji接口类 <公开 @视窗.附属文件.win32 = "..\\\\runtime\\\\win32\\\\new_emoji.dll" @视窗.附属文件.x64 = "..\\\\runtime\\\\x64\\\\new_emoji.dll">',
        "{",
    ]
    used_aliases = {prototypes[name].command_name for name in exports}
    for name in exports:
        proto = prototypes[name]
        lines.append(format_import_method(proto))
        for alias in OLD_INTERFACE_ALIASES.get(name, []):
            if alias not in used_aliases:
                used_aliases.add(alias)
                lines.append("")
                lines.append(format_alias_wrapper(proto, alias))
        lines.append("")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def component_command_name(item: dict[str, str]) -> str:
    create_export = str(item["create"]).split("/")[0].strip()
    prefix = "显示" if create_export.startswith("EU_Show") else "创建"
    return sanitize_volcano_name(prefix + item["zh"], prefix + item["name"])


def is_text_pair(params: tuple[Param, ...], index: int) -> bool:
    if index + 1 >= len(params):
        return False
    current = params[index]
    nxt = params[index + 1]
    if current.c_type != "const unsigned char*" or nxt.c_type != "int":
        return False
    n = nxt.name.lower()
    doc = (nxt.doc_name or "").lower()
    return "len" in n or "length" in n or "长度" in doc


def text_param_label(param: Param, fallback: str) -> str:
    name = param.doc_name or fallback
    for suffix in ("字节集指针", "字节指针", "文件字节指针", "指针", "bytes", "Bytes"):
        name = name.replace(suffix, "")
    name = name.replace("UTF_8", "").replace("UTF8", "")
    return sanitize_volcano_name(name, fallback)


def render_helper_method(proto: Prototype, helper_name: str) -> str:
    params = proto.params
    method_params: list[tuple[str, str, str | None]] = []
    call_args: list[str] = []
    local_lines: list[str] = []
    index = 0
    text_counter = 1
    used: set[str] = set()
    while index < len(params):
        if is_text_pair(params, index):
            label = unique_name(text_param_label(params[index], f"文本{text_counter}"), used, str(text_counter))
            var_name = unique_name(f"{label}字节", used, f"字节{text_counter}")
            method_params.append((label, "文本型", None))
            local_lines.append(f"        变量 {var_name} <类型 = 字节集类>")
            local_lines.append(f"        {var_name} = 到UTF8 ({label})")
            call_args.append(f"字节集类.取字节集指针 ({var_name})")
            call_args.append(f"字节集类.取字节集长度 ({var_name})")
            text_counter += 1
            index += 2
            continue
        param = params[index]
        label = unique_name(param_name(param, f"参数{index + 1}"), used, str(index + 1))
        method_params.append((label, volcano_type(param.c_type), None))
        call_args.append(label)
        index += 1

    lines = [f"    方法 {helper_name} <公开 静态{method_type_attr(proto.return_type)}>"]
    for name, v_type, _ in method_params:
        lines.append(f"    参数 {name} <类型 = {v_type}>")
    lines.append("    {")
    lines.extend(local_lines)
    call = f"NewEmoji接口类.{proto.command_name} (" + ", ".join(call_args) + ")"
    if volcano_type(proto.return_type):
        lines.append(f"        返回 ({call})")
    else:
        lines.append(f"        {call}")
    lines.append("    }")
    return "\n".join(lines)


def render_helper(prototypes: dict[str, Prototype], components: list[dict[str, str]]) -> str:
    helper_exports: list[tuple[str, str]] = []
    for export in sorted(COMMON_HELPERS):
        if export in prototypes:
            helper_exports.append((export, prototypes[export].command_name))
    for item in components:
        export = str(item["create"]).split("/")[0].strip()
        helper_exports.append((export, component_command_name(item)))

    lines = [
        '<火山程序 类型 = "通常" 版本 = 1 />',
        "",
        "包 火山.NewEmoji",
        "",
        "类 NewEmoji助手类 <公开>",
        "{",
        "    方法 到ARGB <公开 静态 类型 = 整数>",
        "    参数 A <类型 = 整数>",
        "    参数 R <类型 = 整数>",
        "    参数 G <类型 = 整数>",
        "    参数 B <类型 = 整数>",
        "    {",
        "        返回 (A * 16777216 + R * 65536 + G * 256 + B)",
        "    }",
        "",
        "    方法 到UTF8 <公开 静态 类型 = 字节集类>",
        "    参数 内容 <类型 = 文本型>",
        "    {",
        "        返回 (文本类.文本到UTF8 (内容, 假))",
        "    }",
        "",
    ]
    used_methods = {"到ARGB", "到UTF8"}
    for export, desired_name in helper_exports:
        proto = prototypes[export]
        method_name = unique_name(sanitize_volcano_name(desired_name, proto.command_name), used_methods, export.removeprefix("EU_"))
        lines.append(render_helper_method(proto, method_name))
        lines.append("")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_vgrp() -> str:
    return """doc_format_version = 1
project_identifier = "wutao.vproject.pc.win.1"

author = "Codex"
name = "new_emoji"
version = 1
unique_mark = new_emoji_ui
explain = "new_emoji 单一 HWND 纯 D2D 中文 emoji 界面库火山封装"
dependence = "*\\sys\\base\\base.vgrp"
dependence = "*\\sys\\iconv\\w_iconv.vgrp"

file
{
    name = "src\\\\new_emoji_接口.wsv"
    name = "src\\\\new_emoji_助手.wsv"
}
"""


def render_module_readme(export_count: int, component_count: int) -> str:
    return f"""# new_emoji 火山模块

本目录是 `new_emoji.vcip` 的模块源目录。模块定义文件为 `new_emoji.vgrp`，最终安装包需要在火山 IDE 中通过“工具 -> 制作模块安装包”生成。

- 底层 DLL 导入：`src/new_emoji_接口.wsv`
- 中文助手封装：`src/new_emoji_助手.wsv`
- DLL 附属文件：`runtime/win32/new_emoji.dll`、`runtime/x64/new_emoji.dll`
- 当前导入导出数量：{export_count}
- 当前组件助手数量：{component_count}

使用规则：

1. 火山项目加入本模块后，优先调用 `NewEmoji助手类`。
2. 中文和 emoji 文本统一由助手类转换为 UTF-8 字节指针 + 长度。
3. DLL 位数必须和火山项目位数一致。
4. 可见界面文案必须中文化，并在窗口标题、主要按钮和核心展示项中使用 emoji。
"""


def render_demo_source() -> str:
    return """<火山程序 类型 = "通常" 版本 = 1 />

包 火山.程序

类 启动类 <公开 基础类 = 窗口程序类>
{
    变量 主窗口 <公开 静态 类型 = 变整数>
    变量 主面板 <静态 类型 = 整数>
    变量 状态文本 <静态 类型 = 整数>
    变量 按钮确认 <静态 类型 = 整数>
    变量 标题文本 <静态 类型 = 整数>
    变量 说明文本 <静态 类型 = 整数>
    变量 输入框 <静态 类型 = 整数>
    变量 打包文本 <静态 类型 = 整数>

    方法 启动方法 <公开 类型 = 整数>
    {
        启动类.主窗口 = NewEmoji助手类.创建窗口 ("🌋 new_emoji 火山模块演示", -1, -1, 900, 600, NewEmoji助手类.到ARGB (255, 37, 99, 235))
        如果 (启动类.主窗口 == 0)
        {
            返回 (0)
        }

        启动类.构建界面 ()
        NewEmoji助手类.显示窗口 (启动类.主窗口, 1)
        NewEmoji助手类.运行消息循环 ()
        返回 (0)
    }

    方法 构建界面 <静态>
    {
        启动类.主面板 = NewEmoji助手类.创建面板 (启动类.主窗口, 0, 24, 58, 852, 486)
        NewEmoji助手类.设置元素颜色 (启动类.主窗口, 启动类.主面板, NewEmoji助手类.到ARGB (255, 15, 23, 42), NewEmoji助手类.到ARGB (255, 226, 232, 240))

        启动类.标题文本 = NewEmoji助手类.创建文本 (启动类.主窗口, 启动类.主面板, "✨ 已通过 new_emoji.vcip 模块源调用", 32, 28, 650, 42)
        NewEmoji助手类.设置元素颜色 (启动类.主窗口, 启动类.标题文本, NewEmoji助手类.到ARGB (0, 0, 0, 0), NewEmoji助手类.到ARGB (255, 248, 250, 252))
        启动类.说明文本 = NewEmoji助手类.创建文本 (启动类.主窗口, 启动类.主面板, "此示例引用 new_emoji 火山模块，窗口、面板、文本、按钮和输入框均由 DLL 的单一 HWND + 纯 D2D Element 架构创建。", 32, 84, 760, 70)
        NewEmoji助手类.设置元素颜色 (启动类.主窗口, 启动类.说明文本, NewEmoji助手类.到ARGB (0, 0, 0, 0), NewEmoji助手类.到ARGB (255, 203, 213, 225))

        启动类.输入框 = NewEmoji助手类.创建输入框 (启动类.主窗口, 启动类.主面板, "你好，火山模块 🚀", "请输入中文和 emoji", "", "", 1, 32, 180, 520, 44)
        NewEmoji助手类.设置元素颜色 (启动类.主窗口, 启动类.输入框, NewEmoji助手类.到ARGB (255, 30, 41, 59), NewEmoji助手类.到ARGB (255, 226, 232, 240))
        启动类.按钮确认 = NewEmoji助手类.创建按钮 (启动类.主窗口, 启动类.主面板, "✅", "确认模块可用", 580, 180, 180, 44)
        NewEmoji助手类.设置按钮样式变体 (启动类.主窗口, 启动类.按钮确认, 1)

        启动类.状态文本 = NewEmoji助手类.创建文本 (启动类.主窗口, 启动类.主面板, "💡 状态：模块源已加载，等待按钮回调。", 32, 270, 740, 34)
        NewEmoji助手类.设置元素颜色 (启动类.主窗口, 启动类.状态文本, NewEmoji助手类.到ARGB (0, 0, 0, 0), NewEmoji助手类.到ARGB (255, 167, 243, 208))
        启动类.打包文本 = NewEmoji助手类.创建文本 (启动类.主窗口, 启动类.主面板, "📦 打包步骤：在火山 IDE 中选择“工具 -> 制作模块安装包”，选择 new_emoji.vgrp，生成 new_emoji.vcip。", 32, 330, 760, 70)
        NewEmoji助手类.设置元素颜色 (启动类.主窗口, 启动类.打包文本, NewEmoji助手类.到ARGB (0, 0, 0, 0), NewEmoji助手类.到ARGB (255, 191, 219, 254))

        NewEmoji接口类.设置元素点击回调 (启动类.主窗口, 启动类.按钮确认, 指针操作类.取静态方法地址 (启动类.元素点击回调))
    }

    方法 元素点击回调 <公开 静态>
    参数 元素ID <类型 = 整数>
    {
        如果 (元素ID == 启动类.按钮确认)
        {
            NewEmoji助手类.设置元素文本 (启动类.主窗口, 启动类.状态文本, "✅ 状态：火山模块按钮回调已触发，中文和 emoji 正常。")
        }
    }
}
"""


def render_demo_vprj() -> str:
    return """doc_format_version = 1
project_identifier = "wutao.vproject.pc.win.1"

root_filter
{
    child_filter
    {
        filter1
        {
            child_filter
            {
                filter1
                {
                    collapsed = true
                    files.num_files = 16
                    group_file_name = "*plugins\\\\vprj_win\\\\classlib\\\\sys\\\\base\\\\base.vgrp"
                    name = 视窗基本类
                }

                filter2
                {
                    collapsed = true
                    files.num_files = 1
                    group_file_name = "*plugins\\\\vprj_win\\\\classlib\\\\sys\\\\iconv\\\\w_iconv.vgrp"
                    name = 字符编码
                }

                filter3
                {
                    collapsed = true
                    files.num_files = 2
                    group_file_name = "new_emoji_module\\\\new_emoji.vgrp"
                    name = new_emoji模块
                }

                num_child_filters = 3
            }

            name = 模块
        }

        num_child_filters = 1
    }

    files
    {
        file1.file_name = "src\\\\module_demo.wsv"
        num_files = 1
    }

    name = new_emoji火山模块Demo_x64
    type = project
}

settings
{
    project
    {
        auto_support_high_dpi = true
        debug_working_dir = runtime_x64
        out_file_name = "runtime_x64\\\\NewEmojiVolcanoModuleDemo_$(p).exe"
        target_platform = 2
    }
}
"""


def render_demo_vsln() -> str:
    return """doc_format_version = 1
name = new_emoji火山模块Demo_x64
property.settings.active_project_name = new_emoji火山模块Demo_x64

root_filter
{
    child_filter
    {
        filter1
        {
            build_order = 0
            project_file_name = "NewEmojiModuleDemo_x64.vprj"
            projects_dependent
            type = project
        }

        num_child_filters = 1
    }

    name = root
}
"""


def render_progress(components: list[dict[str, str]], export_count: int) -> str:
    lines = [
        "# 火山组件模块封装进度",
        "",
        f"- 组件总数：{len(components)}",
        "- 已完成：0",
        f"- 底层 EU 导入：{export_count} 个已生成",
        "- 完成判定：底层导入、助手封装、中文/emoji 示例、x64/Win32 验证、`.vcip` 打包验证全部通过后，才允许标记为“已完成”。",
        "",
        "| 序号 | 组件 | 中文名 | 创建/服务导出 | 火山助手方法 | 状态 | 验证 |",
        "|---:|---|---|---|---|---|---|",
    ]
    for item in components:
        export = str(item["create"]).split("/")[0].strip()
        helper = component_command_name(item)
        lines.append(
            f"| {item['index']} | {item['name']} | {item['zh']} | `{export}` | `{helper}` | 基础封装已生成，未完成 | 待火山 IDE x64/Win32 与 .vcip 验证 |"
        )
    lines.append("")
    return "\n".join(lines)


def write_text(path: Path, text: str, encoding: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding, newline="\n") as handle:
        handle.write(text)


def copy_runtime() -> None:
    pairs = [
        (ROOT / "bin" / "Win32" / "Release" / "new_emoji.dll", MODULE_RUNTIME / "win32" / "new_emoji.dll"),
        (ROOT / "bin" / "x64" / "Release" / "new_emoji.dll", MODULE_RUNTIME / "x64" / "new_emoji.dll"),
        (ROOT / "bin" / "x64" / "Release" / "new_emoji.dll", DEMO_RUNTIME / "new_emoji.dll"),
    ]
    for src, dst in pairs:
        if not src.exists():
            raise FileNotFoundError(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def build_outputs() -> dict[Path, tuple[str, str]]:
    exports = load_exports()
    prototypes = parse_prototypes()
    components = json.loads(COMPONENT_MANIFEST.read_text(encoding="utf-8-sig"))
    ai_manifest = json.loads(AI_MANIFEST.read_text(encoding="utf-8-sig"))
    missing = [name for name in exports if name not in prototypes]
    if missing:
        raise ValueError(f"Exports missing prototypes: {', '.join(missing[:10])}")
    if len(exports) != len(prototypes):
        raise ValueError(f"Export/prototype count mismatch: {len(exports)} vs {len(prototypes)}")
    if len(components) != 91:
        raise ValueError(f"Component count is {len(components)}, expected 91")
    if len(ai_manifest) != 91:
        raise ValueError(f"AI manifest count is {len(ai_manifest)}, expected 91")
    helper_exports = {str(item["create"]).split("/")[0].strip() for item in components}
    missing_helpers = sorted(export for export in helper_exports if export not in prototypes)
    if missing_helpers:
        raise ValueError(f"Components missing create/service prototypes: {', '.join(missing_helpers)}")

    return {
        MODULE_INTERFACE: (render_interface(prototypes, exports), UTF16),
        MODULE_HELPER: (render_helper(prototypes, components), UTF16),
        MODULE_VGRP: (render_vgrp(), UTF16),
        MODULE_README: (render_module_readme(len(exports), len(components)), UTF8),
        DEMO_SOURCE: (render_demo_source(), UTF16),
        DEMO_VPRJ: (render_demo_vprj(), UTF16),
        DEMO_VSLN: (render_demo_vsln(), UTF16),
        PROGRESS_FILE: (render_progress(components, len(exports)), UTF8),
    }


def check_outputs(outputs: dict[Path, tuple[str, str]]) -> int:
    errors: list[str] = []
    interface_text = outputs[MODULE_INTERFACE][0]
    output_names = re.findall(r'@输出名 = "([^"]+)"', interface_text)
    duplicate_outputs = sorted({name for name in output_names if output_names.count(name) > 1})
    if duplicate_outputs:
        errors.append(f"duplicate Volcano @输出名 values: {', '.join(duplicate_outputs[:10])}")
    export_count = len(load_exports())
    if len(output_names) != export_count:
        errors.append(f"Volcano import count mismatch: {len(output_names)} vs {export_count}")
    for path, (expected, encoding) in outputs.items():
        if not path.exists():
            errors.append(f"missing: {path}")
            continue
        actual = path.read_text(encoding=encoding)
        if actual.replace("\r\n", "\n") != expected:
            errors.append(f"stale: {path}")
    runtime_files = [
        MODULE_RUNTIME / "win32" / "new_emoji.dll",
        MODULE_RUNTIME / "x64" / "new_emoji.dll",
        DEMO_RUNTIME / "new_emoji.dll",
    ]
    for path in runtime_files:
        if not path.exists():
            errors.append(f"missing runtime: {path}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Volcano module generation check passed.")
    return 0


def write_outputs(outputs: dict[Path, tuple[str, str]]) -> None:
    for path, (text, encoding) in outputs.items():
        write_text(path, text, encoding)
    copy_runtime()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Volcano module sources for new_emoji.")
    parser.add_argument("--check", action="store_true", help="Validate generated files without writing.")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.check:
        return check_outputs(outputs)
    write_outputs(outputs)
    print(f"Wrote Volcano module to {MODULE_DIR}")
    print(f"Wrote local progress file to {PROGRESS_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
