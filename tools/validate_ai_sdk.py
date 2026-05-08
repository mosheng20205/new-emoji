from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_MANIFEST = ROOT / "docs" / "components" / "manifest.json"
AI_MANIFEST = ROOT / "docs" / "ai" / "api_manifest.full.json"
DEF_FILE = ROOT / "src" / "new_emoji.def"
PY_HELPERS = ROOT / "examples" / "python" / "new_emoji_ui.py"
README = ROOT / "README.md"


REQUIRED_FILES = [
    ROOT / "SKILL.md",
    ROOT / "AI_USAGE.md",
    ROOT / "docs" / "ai" / "README.md",
    ROOT / "docs" / "ai" / "language-matrix.md",
    ROOT / "docs" / "ai" / "e-language-encoding.md",
    ROOT / "docs" / "ai" / "prompts" / "易语言.md",
    ROOT / "docs" / "ai" / "prompts" / "火山.md",
    ROOT / "docs" / "ai" / "prompts" / "CSharp.md",
    ROOT / "docs" / "ai" / "prompts" / "Python.md",
    ROOT / "examples" / "templates" / "python" / "blank_window.py",
    ROOT / "examples" / "templates" / "csharp" / "BlankWindow.cs",
    ROOT / "examples" / "templates" / "易语言" / "空白窗口.md",
    ROOT / "examples" / "templates" / "火山" / "空白窗口.md",
    ROOT / "DLL命令" / "CSharp DLL命令.md",
    ROOT / "DLL命令" / "Python DLL命令.md",
    ROOT / "DLL命令" / "易语言DLL命令.md",
    ROOT / "examples" / "火山" / "src" / "new_emoji_接口.wsv",
]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def require_text(path: Path, needles: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for needle in needles:
        if needle not in text:
            fail(f"{path} missing text: {needle}", errors)


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"Missing required file: {path}", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    components = load_json(COMPONENT_MANIFEST)
    ai_manifest = load_json(AI_MANIFEST)
    exports = load_exports()
    helpers = load_python_helpers()

    if len(components) != 91:
        fail(f"Component manifest count is {len(components)}, expected 91", errors)
    if len(ai_manifest) != 91:
        fail(f"AI manifest count is {len(ai_manifest)}, expected 91", errors)

    by_component = {item["component"]: item for item in ai_manifest}
    for component in components:
        name = component["name"]
        item = by_component.get(name)
        if item is None:
            fail(f"AI manifest missing component: {name}", errors)
            continue

        export = item.get("create_export")
        if export not in exports:
            fail(f"AI manifest export missing from def: {name} -> {export}", errors)

        doc = ROOT / item.get("doc", "")
        if not doc.exists():
            fail(f"Component doc missing: {name} -> {doc}", errors)

        python_helper = item.get("bindings", {}).get("python", {}).get("helper")
        if python_helper and python_helper not in helpers:
            fail(f"Python helper not found: {name} -> {python_helper}", errors)

        e_binding = item.get("bindings", {}).get("e_language", {})
        if e_binding.get("source_unicode_safe") is not False:
            fail(f"易语言 source_unicode_safe must be false: {name}", errors)
        if "UTF-8 字节集 + 长度" not in e_binding.get("text_rule", ""):
            fail(f"易语言 text_rule missing UTF-8 rule: {name}", errors)

    require_text(
        README,
        [
            "AI_USAGE.md",
            "SKILL.md",
            "docs/ai/README.md",
            "docs/ai/language-matrix.md",
            "docs/ai/api_manifest.full.json",
            "examples/templates/",
            "易语言源码中不要直接写 emoji",
        ],
        errors,
    )
    require_text(ROOT / "AI_USAGE.md", ["UTF-8 字节集 + 长度", "不要直接写 emoji"], errors)
    require_text(ROOT / "docs" / "ai" / "prompts" / "易语言.md", ["UTF-8 字节集 + 长度", "不要直接写 emoji"], errors)
    require_text(ROOT / "examples" / "templates" / "易语言" / "空白窗口.md", ["UTF-8 字节集 + 长度", "不要直接写 emoji"], errors)
    require_text(ROOT / "examples" / "templates" / "csharp" / "BlankWindow.cs", ["Encoding.UTF8.GetBytes", "CallingConvention.StdCall"], errors)
    require_text(ROOT / "examples" / "templates" / "python" / "blank_window.py", ["new_emoji_ui", "欢迎使用 new_emoji 🚀"], errors)
    require_text(ROOT / "examples" / "templates" / "火山" / "空白窗口.md", ["UTF-8 字节指针 + 长度", "欢迎使用 new_emoji 🚀"], errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("AI SDK validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
