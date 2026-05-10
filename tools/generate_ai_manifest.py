from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_MANIFEST = ROOT / "docs" / "components" / "manifest.json"
DEF_FILE = ROOT / "src" / "new_emoji.def"
PY_HELPERS = ROOT / "examples" / "python" / "new_emoji_ui.py"
OUTPUT = ROOT / "docs" / "ai" / "api_manifest.full.json"


SPECIAL_HELPERS = {
    "EditBox": "create_editbox",
    "InfoBox": "create_infobox",
    "SelectV2": "create_select_v2",
    "ColorPicker": "create_colorpicker",
    "DatePicker": "create_datepicker",
    "TimePicker": "create_timepicker",
    "DateTimePicker": "create_datetimepicker",
    "PageHeader": "create_pageheader",
    "MessageBox": "show_messagebox",
}

USAGE_NOTES = {
    "Button": "用于普通文本按钮和主要操作按钮；图标工具按钮优先使用 IconButton。",
    "IconButton": "用于工具栏、标题栏和浏览器外壳中的图标按钮。",
    "Input": "推荐用于新表单输入；兼容编辑内核请使用 EditBox。",
    "EditBox": "兼容早期 MVP 的底层编辑内核；新表单输入优先使用 Input。",
    "Table": "用于数据列表、筛选、树形、虚表、增删改查和普通文本单元格双击编辑；双击编辑使用 EU_SetTableDoubleClickEdit / EU_SetTableCellEditCallback。",
    "Dialog": "用于窗口内弹窗、表单编辑和确认流程。",
    "BrowserViewport": "用于浏览器式外壳的内容占位区域。",
}


def load_components() -> list[dict]:
    return json.loads(COMPONENT_MANIFEST.read_text(encoding="utf-8-sig"))


def load_exports() -> set[str]:
    exports: set[str] = set()
    in_exports = False
    for raw in DEF_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        if line.upper() == "EXPORTS":
            in_exports = True
            continue
        if in_exports:
            exports.add(line.split()[0])
    return exports


def load_python_helpers() -> set[str]:
    text = PY_HELPERS.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, flags=re.MULTILINE))


def snake_from_slug(slug: str) -> str:
    return slug.replace("-", "_")


def first_export(create_field: str) -> str:
    return create_field.split("/")[0].strip()


def helper_for(component: dict, helpers: set[str]) -> str | None:
    name = component["name"]
    if name in SPECIAL_HELPERS and SPECIAL_HELPERS[name] in helpers:
        return SPECIAL_HELPERS[name]

    slug = snake_from_slug(component["slug"])
    export = first_export(component["create"])
    candidates = []
    if export.startswith("EU_Show"):
        candidates.append(f"show_{slug}")
    candidates.append(f"create_{slug}")
    candidates.append(f"show_{slug}")

    for candidate in candidates:
        if candidate in helpers:
            return candidate
    return None


def command_name(component: dict) -> str:
    prefix = "显示" if first_export(component["create"]).startswith("EU_Show") else "创建"
    return prefix + component["zh"]


def csharp_wrapper_method(component: dict) -> str:
    name = component["name"]
    export = first_export(component["create"])
    if export == "EU_ShowMessage":
        return "EmojiWindow.ShowMessage"
    if export == "EU_ShowMessageBoxEx":
        return "EmojiWindow.ShowMessageBox"
    if name in {"Dialog", "Drawer"}:
        return f"EmojiWindow.Create{name}"
    return f"EmojiElement.Add{name}"


def build_manifest() -> list[dict]:
    helpers = load_python_helpers()
    exports = load_exports()
    result = []

    for item in load_components():
        create_export = first_export(item["create"])
        if create_export not in exports:
            raise ValueError(f"Missing export in {DEF_FILE}: {create_export}")

        component_doc = f"docs/components/{item['slug']}.md"
        result.append(
            {
                "component": item["name"],
                "zh": item["zh"],
                "category": item["category"],
                "status": item["status"],
                "create_export": create_export,
                "calling_convention": "__stdcall",
                "text_encoding": "utf8_bytes_with_length",
                "doc": component_doc,
                "bindings": {
                    "python": {
                        "helper": helper_for(item, helpers),
                        "file": "examples/python/new_emoji_ui.py",
                    },
                    "csharp": {
                        "wrapper": csharp_wrapper_method(item),
                        "wrapper_file": "bindings/csharp/NewEmoji",
                        "native_entry": create_export,
                        "native_file": "DLL命令/CSharp DLL命令.md",
                        "text_rule": "封装库自动处理 UTF-8；直接 P/Invoke 时使用 Encoding.UTF8.GetBytes(text)",
                    },
                    "e_language": {
                        "command_name": command_name(item),
                        "entry": create_export,
                        "file": "DLL命令/易语言DLL命令.md",
                        "text_rule": "不要在源码中直接写 emoji；使用 UTF-8 字节集 + 长度",
                        "source_unicode_safe": False,
                    },
                    "volcano": {
                        "entry": create_export,
                        "file": "examples/火山/new_emoji_module/src/new_emoji_接口.wsv",
                    },
                },
                "usage_notes": USAGE_NOTES.get(
                    item["name"],
                    f"用于创建和配置 {item['zh']} 组件；详细参数和行为见组件文档。",
                ),
            }
        )

    return result


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as fp:
        fp.write(json.dumps(build_manifest(), ensure_ascii=False, indent=2))
        fp.write("\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
