from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEF_FILE = ROOT / "src" / "new_emoji.def"
MANIFEST = ROOT / "docs" / "components" / "manifest.json"


CATEGORIES = {
    "基础/布局": [
        "Panel", "Button", "InfoBox", "Text", "Link", "Icon", "Space",
        "Container", "Header", "Aside", "Main", "Footer", "Layout", "Border", "Divider",
    ],
    "兼容内核": [
        "EditBox",
    ],
    "表单/选择": [
        "Checkbox", "Radio", "Switch", "Slider", "InputNumber", "Input",
        "InputGroup", "InputTag", "Select", "SelectV2", "Rate", "ColorPicker",
    ],
    "数据展示": [
        "Tag", "Badge", "Progress", "Avatar", "Empty", "Skeleton",
        "Descriptions", "Table", "InfiniteScroll", "Card", "Collapse", "Timeline", "Statistic",
    ],
    "指标/图表": [
        "KpiCard", "Trend", "StatusDot", "Gauge", "RingProgress",
        "BulletProgress", "LineChart", "BarChart", "DonutChart",
    ],
    "日期时间": [
        "Calendar", "DatePicker", "TimePicker", "DateTimePicker", "TimeSelect",
    ],
    "复杂选择": [
        "Tree", "TreeSelect", "Transfer", "Autocomplete", "Mentions", "Cascader",
    ],
    "导航": [
        "Dropdown", "Menu", "Anchor", "Backtop", "Segmented", "PageHeader",
        "Affix", "Breadcrumb", "Tabs", "Pagination", "Steps",
    ],
    "媒体/工具": [
        "Watermark", "Tour", "Image", "Carousel", "Upload",
    ],
    "反馈/浮层": [
        "Alert", "Result", "Message", "MessageBox", "Notification", "Loading", "Dialog",
        "Drawer", "Tooltip", "Popover", "Popconfirm",
    ],
}


ZH_NAMES = {
    "Panel": "面板", "Button": "按钮", "EditBox": "兼容编辑内核", "InfoBox": "信息框",
    "Text": "文本", "Link": "链接", "Icon": "图标", "Space": "间距",
    "Container": "容器套件", "Header": "顶栏", "Aside": "侧边栏",
    "Main": "主要区域", "Footer": "底栏", "Layout": "布局", "Border": "边框", "Divider": "分割线",
    "Checkbox": "复选框", "Radio": "单选框", "Switch": "开关", "Slider": "滑块",
    "InputNumber": "数字输入框", "Input": "输入框", "InputGroup": "组合输入", "InputTag": "标签输入",
    "Select": "选择器", "SelectV2": "虚拟选择器", "Rate": "评分",
    "ColorPicker": "颜色选择器", "Tag": "标签", "Badge": "徽标",
    "Progress": "进度条", "Avatar": "头像", "Empty": "空状态",
    "Skeleton": "骨架屏", "Descriptions": "描述列表", "Table": "表格",
    "Card": "卡片", "Collapse": "折叠面板", "Timeline": "时间线",
    "Statistic": "统计数值", "KpiCard": "指标卡", "Trend": "趋势",
    "StatusDot": "状态点", "Gauge": "仪表盘", "RingProgress": "环形进度",
    "BulletProgress": "子弹进度", "LineChart": "折线图",
    "BarChart": "柱状图", "DonutChart": "环形图", "Calendar": "日历",
    "Tree": "树", "TreeSelect": "树选择", "Transfer": "穿梭框",
    "Autocomplete": "自动补全", "Mentions": "提及", "Cascader": "级联选择",
    "DatePicker": "日期选择器", "TimePicker": "时间选择器",
    "DateTimePicker": "日期时间选择器", "TimeSelect": "时间选择",
    "Dropdown": "下拉菜单", "Menu": "菜单", "Anchor": "锚点",
    "Backtop": "回到顶部", "Segmented": "分段控制器",
    "PageHeader": "页头", "Affix": "固钉", "Watermark": "水印",
    "Tour": "漫游引导", "Image": "图片", "Carousel": "轮播",
    "Upload": "上传", "InfiniteScroll": "无限滚动", "Breadcrumb": "面包屑",
    "Tabs": "标签页", "Pagination": "分页", "Steps": "步骤条",
    "Alert": "警告提示", "Result": "结果页", "Message": "消息提示",
    "MessageBox": "消息框", "Notification": "通知",
    "Loading": "加载", "Dialog": "对话框", "Drawer": "抽屉",
    "Tooltip": "文字提示", "Popover": "弹出框", "Popconfirm": "气泡确认框",
}


EMOJI = {
    "基础/布局": "🧱",
    "兼容内核": "🧩",
    "表单/选择": "📝",
    "数据展示": "📊",
    "指标/图表": "📈",
    "日期时间": "📅",
    "复杂选择": "🌲",
    "导航": "🧭",
    "媒体/工具": "🖼️",
    "反馈/浮层": "💬",
}


def slug(name: str) -> str:
    chars = []
    for index, ch in enumerate(name):
        if index and ch.isupper() and (not name[index - 1].isupper()):
            chars.append("-")
        chars.append(ch.lower())
    return "".join(chars).replace("-v2", "v2")


def parse_components() -> list[dict[str, str]]:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Missing component manifest: {MANIFEST}")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def parse_exports() -> list[str]:
    exports = []
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


def component_exports(component: str, exports: list[str], components: list[str]) -> list[str]:
    result = []
    longer = sorted([c for c in components if c != component and c.startswith(component)], key=len, reverse=True)
    for export in exports:
        matched = False
        for prefix in ("EU_Create", "EU_Show", "EU_Set", "EU_Get", "EU_Trigger", "EU_Reset"):
            head = prefix + component
            if not export.startswith(head):
                continue
            if any(export.startswith(prefix + other) for other in longer):
                continue
            matched = True
        if matched:
            result.append(export)
    return sorted(set(result))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def root_readme(components: list[dict[str, str]]) -> str:
    complete = sum(1 for c in components if c["status"] == "已完成")
    return f"""
# new_emoji

`new_emoji` 是一个面向 易语言 / Python / C# 调用的 Windows 原生 UI DLL。它采用单一 HWND + 纯 Direct2D 渲染架构，把所有控件封装成 Element 组件，重点解决传统 GDI 子窗口在缩放和重绘时的闪烁问题，同时原生支持中文与彩色 emoji。

## 特性

- 纯 Direct2D / DirectWrite 渲染，单窗口树，减少闪烁。
- 统一 `EU_` C API 导出，适合 DLL 方式集成。
- 文本参数统一使用 UTF-8 字节数组 + 长度，方便易语言传递 emoji 和 Unicode 文本。
- 支持 Win32 与 x64 Release 构建，其中 Win32 是易语言交付优先目标。
- 组件完成度：{complete} / {len(components)}，所有计划内组件均已完成独立中文 emoji 验证。
- 内置主题、DPI、键鼠交互、Set/Get 状态读回和 Python ctypes helper。

## 快速入口

- [文档总览](docs/README.md)
- [快速开始](docs/quick-start.md)
- [构建说明](docs/build.md)
- [API 约定](docs/api-conventions.md)
- [组件文档导航](docs/components/README.md)
- [易语言 DLL 命令](DLL命令/易语言DLL命令.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)
- [许可证](LICENSE)

## 最短 Python 示例

```python
import ctypes
from ctypes import wintypes
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("✨ new_emoji 示例", 240, 120, 820, 560)
root = ui.create_container(hwnd, 0, 0, 0, 780, 500)
ui.create_text(hwnd, root, "你好，new_emoji 🚀", 32, 32, 360, 40)
ui.create_button(hwnd, root, "✅", "确认操作", 32, 96, 160, 42)
ui.dll.EU_ShowWindow(hwnd, 1)

user32 = ctypes.windll.user32
msg = wintypes.MSG()
while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
```

> Python 位数必须和 DLL 位数一致：32 位 Python 加载 Win32 DLL，64 位 Python 加载 x64 DLL。

## 构建

```powershell
& "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe" .\\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
& "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe" .\\new_emoji.sln /p:Configuration=Release /p:Platform=x64
```

详细要求见 [构建说明](docs/build.md)。

## 文档维护

当某个组件新增、删除、重命名或修改导出 API 时，必须同步更新该组件文档、组件导航、Python ctypes/helper 和易语言 DLL 命令文档，避免开源用户看到过期接口。

## 许可证

本项目使用 [MIT License](LICENSE) 开源。
"""


def docs_readme() -> str:
    return """
# new_emoji 文档

这里是开源文档入口。根目录 `README.md` 用于快速了解项目；本目录保存更详细的使用、构建、API 约定和组件文档。

## 导航

- [快速开始](quick-start.md)
- [构建说明](build.md)
- [API 约定](api-conventions.md)
- [API 索引](api-index.md)
- [组件文档](components/README.md)
- [Python 示例说明](examples/python.md)
- [易语言接入说明](examples/e-lang.md)
- [C# 接入说明](examples/csharp.md)

## 读者路径

- 想快速跑起来：先读 [快速开始](quick-start.md)。
- 想接入易语言：先读 [易语言接入说明](examples/e-lang.md)，再查 [易语言 DLL 命令](../DLL命令/易语言DLL命令.md)。
- 想查控件能力：从 [组件文档](components/README.md) 进入对应组件页面。
- 想贡献代码：先读根目录 [贡献指南](../CONTRIBUTING.md) 中的组件 API 与文档同步规则。
"""


def quick_start() -> str:
    return """
# 快速开始

## 1. 选择 DLL 位数

- 易语言交付优先使用 Win32 DLL。
- 64 位 Python / C# 进程使用 x64 DLL。
- 进程位数必须和 DLL 位数一致，否则会加载失败。

## 2. 构建 DLL

```powershell
& "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe" .\\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
```

输出位置：

- `bin/Win32/Release/new_emoji.dll`
- `bin/x64/Release/new_emoji.dll`

## 3. Python 运行一个窗口

```python
import ctypes
from ctypes import wintypes
import time
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)

hwnd = ui.create_window("✨ 快速开始", 240, 120, 860, 560)
ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
ui.create_text(hwnd, root, "欢迎使用 new_emoji 🚀", 32, 32, 500, 42)
ui.create_button(hwnd, root, "✅", "开始体验", 32, 100, 160, 42)
ui.dll.EU_ShowWindow(hwnd, 1)

user32 = ctypes.windll.user32
msg = wintypes.MSG()
while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
```

## 4. 查组件文档

所有组件入口见 [组件文档导航](components/README.md)。每个组件页面包含创建 API、相关导出、Python helper、易语言文档入口和测试文件建议。
"""


def build_doc() -> str:
    return """
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
& "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe" .\\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
```

x64：

```powershell
& "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe" .\\new_emoji.sln /p:Configuration=Release /p:Platform=x64
```

## 输出目录

- `bin/Win32/Release/new_emoji.dll`
- `bin/x64/Release/new_emoji.dll`

## 验证建议

组件级验证优先运行对应的 `tests/python/test_*_complete_components.py`。UI 测试应保持窗口可见足够时间，确认中文、emoji、DPI、首次窗口尺寸和交互行为正常。
"""


def api_conventions() -> str:
    return """
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
"""


def example_python() -> str:
    return """
# Python 示例说明

Python 示例和测试使用 `ctypes` 加载 `new_emoji.dll`。推荐复用 `examples/python/new_emoji_ui.py`，其中已经声明了导出函数签名和常用 helper。

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
"""


def example_elang() -> str:
    return """
# 易语言接入说明

易语言接入时建议优先使用 Win32 版本 DLL。

## 文本传参

emoji 和特殊 Unicode 文本应按 UTF-8 字节数组传给 DLL，并传入字节长度。返回文本同样按 UTF-8 字节数组处理。

## DLL 命令

完整命令声明见：

- [易语言 DLL 命令](../../DLL命令/易语言DLL命令.md)

左侧命令名面向易语言用户，使用中文；右侧 DLL 入口名保留真实 `EU_` 导出名。

## 文档同步

如果新增或修改 DLL 导出，必须同步更新易语言命令文档，避免用户按旧签名调用。
"""


def example_csharp() -> str:
    return """
# C# 接入说明

C# 可通过 P/Invoke 调用 `new_emoji.dll`。注意应用进程位数必须和 DLL 位数一致。

## 建议

- x86 应用加载 Win32 DLL。
- x64 应用加载 x64 DLL。
- 文本参数按 UTF-8 byte array 传递。
- 回调保持 `StdCall` 调用约定。

更完整的 P/Invoke 声明可参考导出表 `src/new_emoji.def` 和 Python ctypes 封装 `examples/python/new_emoji_ui.py`。
"""


def api_index(exports: list[str]) -> str:
    rows = "\n".join(f"| `{name}` | |" for name in exports)
    return f"""
# API 索引

本索引从 `src/new_emoji.def` 生成，用于快速确认当前 DLL 导出名称。说明列可逐步补充，组件级说明请查看 [组件文档](components/README.md)。

| 导出 | 说明 |
|---|---|
{rows}
"""


def components_index(components: list[dict[str, str]]) -> str:
    blocks = [f"# 组件文档导航\n\n计划内 {len(components)} 个组件均已完成封装。每个组件都有单独文档，组件 API 变更时必须同步更新对应文档。\n"]
    for category, names in CATEGORIES.items():
        blocks.append(f"\n## {EMOJI.get(category, '📦')} {category}\n")
        blocks.append("| 组件 | 中文名 | 创建导出 | 状态 | 文档 |\n|---|---|---|---|---|\n")
        by_name = {c["name"]: c for c in components}
        for name in names:
            c = by_name[name]
            blocks.append(f"| `{c['name']}` | {c['zh']} | `{c['create']}` | {c['status']} | [{c['zh']}](./{c['slug']}.md) |\n")
    return "".join(blocks)


def component_doc(c: dict[str, str], apis: list[str]) -> str:
    api_rows = "\n".join(f"| `{api}` | 当前组件相关导出 |" for api in apis) or "| 暂无专用导出 | 使用通用 Element API |"
    test_guess = f"test_{c['slug'].replace('-', '')}_complete_components.py"
    return f"""
# {c['name']} {c['zh']}

## 简介

`{c['name']}` 是 new_emoji 的 {c['category']} 组件。当前状态：**{c['status']}**。

{c['summary']}

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `{c['create']}` |
| 组件分类 | {c['category']} |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_{c['slug'].replace('-', '_')}` 或同类 helper |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
{api_rows}

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("✨ {c['zh']} 示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)
# 请根据 `examples/python/new_emoji_ui.py` 中的 helper 创建 `{c['name']}`。
# 示例界面文案应使用中文，并在标题、按钮或核心内容中加入 emoji。
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。

## 状态与交互

- 组件已按封装计划补齐创建、绘制、主题、DPI、交互、Set/Get、Python 封装和独立中文 emoji 验证。
- 修改组件行为时，需要同步检查 hover、pressed、focus、keyboard、disabled、selected、popup、scroll 等相关状态。
- 涉及回调、状态读回或数据模型变化时，应更新对应独立测试文件。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。

## 测试

优先运行对应完整测试文件，例如 `tests/python/{test_guess}`。如果该组件被组合测试覆盖，请查看 `tests/python/test_*_complete_components.py`。

## 文档维护

如果 `{c['name']}` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py` 和 `DLL命令/易语言DLL命令.md`。
"""


def main() -> None:
    components = parse_components()
    exports = parse_exports()
    names = [c["name"] for c in components]

    write(ROOT / "README.md", root_readme(components))
    write(ROOT / "docs" / "README.md", docs_readme())
    write(ROOT / "docs" / "quick-start.md", quick_start())
    write(ROOT / "docs" / "build.md", build_doc())
    write(ROOT / "docs" / "api-conventions.md", api_conventions())
    write(ROOT / "docs" / "api-index.md", api_index(exports))
    write(ROOT / "docs" / "examples" / "python.md", example_python())
    write(ROOT / "docs" / "examples" / "e-lang.md", example_elang())
    write(ROOT / "docs" / "examples" / "csharp.md", example_csharp())
    write(ROOT / "docs" / "components" / "README.md", components_index(components))

    for component in components:
        apis = component_exports(component["name"], exports, names)
        write(ROOT / "docs" / "components" / f"{component['slug']}.md", component_doc(component, apis))


if __name__ == "__main__":
    main()
