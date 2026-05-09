# new_emoji — 项目理念与初衷

## 为什么重写？

旧版 `emoji_window.dll` 最早是基于 GDI 子窗口 + D2D 混合渲染的架构。在窗口拖拽缩放大小时，GDI 子窗口会产生 erase→paint 闪烁（白底闪烁），多次尝试修补仍然无法从根本上消除。

根本原因是 **GDI 和 D2D 两种渲染模型无法在同一个窗口树中完美协作**：
- GDI 用 `WM_ERASEBKGND` 擦背景，子窗口独立绘制
- D2D 是一次性 Draw → EndDraw 原子呈现
- 两者混合必然产生时序差，导致闪烁

旧 DLL 的修复手段（resize 期间隐藏所有子窗口、D2DERR_RECREATE_TARGET 回退等）都是治标不治本。

## 核心理念

**单一 HWND + 纯 D2D 渲染。**

整个窗口只有一个 HWND，所有 UI 组件（按钮、编辑框、面板等）都是“虚拟元素”，在同一个 D2D 渲染周期中一次性绘出。GDI 完全不参与。

这样做的好处：
1. **零闪烁**：WM_ERASEBKGND 返回 1，没有 GDI 擦背景。只有一个 BeginDraw→Clear→Paint→EndDraw 循环，原子呈现。
2. **Unicode / Emoji 原生支持**：DirectWrite 配合 `D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT` 渲染彩色 emoji。
3. **干净的 Element 架构**：类似 DOM 的元素树，每个元素有 layout/paint/hit_test/input 事件，便于扩展新组件。
4. **DPI 自适应**：标题栏高度、字体大小、padding 随系统 DPI 缩放。

## 架构对比

| | 旧 DLL (emoji_window) | 新 DLL (new_emoji) |
|---|---|---|
| HWND 数量 | 每个控件一个 | 整个窗口一个 |
| 渲染方式 | GDI + D2D 混合 | 纯 D2D |
| 缩放闪烁 | 有（多次修复仍残留） | 无（架构保证） |
| 组件模型 | 散落的 HWND 子类化 | Element 虚基类 + 树结构 |
| 代码组织 | 单文件上万行 | 多文件，每个文件 <500 行 |
| 文件数量 | ~6 个 .cpp | ~15 个 .cpp |

## Element 组件模型

```
Element (虚基类)
├── Panel     → 矩形容器，背景+圆角+子元素
├── Button    → 按钮，文本+emoji+hover/press 状态
├── EditBox   → 编辑框，光标+选区+IME+剪贴板
└── TitleBar  → 标题栏，窗口拖拽+最小化/最大化/关闭按钮
```

每个 Element 的生命周期：
- `layout(available)` → 计算布局
- `paint(ctx)` → D2D 绘制（应用坐标变换，在 (0,0) 本地坐标系中画）
- `hit_test(x,y)` → 命中检测，递归遍历子元素
- `on_mouse_*` / `on_key_*` / `on_char` → 输入事件

## 导出 API 设计

前缀统一用 `EU_`（Element UI），避免与旧 DLL 冲突。所有文本参数走 UTF-8 字节数组 + 长度。

```
EU_CreateWindow(title, x, y, w, h, titlebar_color)
EU_CreatePanel(hwnd, parent_id, x, y, w, h)
EU_CreateButton(hwnd, parent_id, emoji, text, x, y, w, h)
EU_CreateEditBox(hwnd, parent_id, x, y, w, h)
EU_SetElementText / EU_SetElementColor / EU_SetElementFont / ...
```

面向易语言的 DLL 命令文档必须使用中文方法名，例如 `.DLL命令 创建窗口, ..., "EU_CreateWindow"`。左侧命令名给易语言用户调用，必须中文化；右侧 DLL 入口名保留真实 C++ 导出名，确保绑定到 `new_emoji.def` 中的 `EU_` 导出。

## DPI 与首次窗口尺寸规则

- `EU_CreateWindow` 创建窗口时，必须先把当前线程切到 `DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2`，再调用 `MonitorFromPoint` / `GetDpiForMonitor` 读取目标显示器 DPI，并用该 DPI 把传入的逻辑宽高换算为物理窗口宽高。
- 不能先按默认 DPI 创建窗口，再让元素按窗口 DPI 缩放；这样在 4K 150% 等高 DPI 屏幕首次运行时会出现窗口物理尺寸偏小、右侧或底部控件被裁切的问题。
- Python 示例里的 `create_window(..., w, h)` 传入的是逻辑尺寸。每个示例首次运行时必须完整显示首屏内容：窗口宽度要覆盖最右侧控件 `x + w`，高度要覆盖最下方控件 `y + h`，并保留至少 20px 逻辑余量。
- 新增或调整示例时，要同时检查 `create_container` 的宽高，容器尺寸应与窗口客户区匹配，不能小于当前示例内容边界。
- 适配要求以“首次打开窗口”为准，不能依赖用户拖动到另一块屏幕、手动缩放或最大化后才显示正常。

## 界面语言规则

- 所有程序界面文案必须使用中文，包括窗口标题、按钮、标签、提示框、卡片、弹窗、下拉项、示例数据、组件内部按钮和空状态文案。
- 所有程序和示例界面都必须加入合适的 emoji 表情，至少覆盖窗口标题、主标题、主要按钮和核心展示项；这是该界面库的核心亮点之一，新增或调整界面时要在首屏和交互展开内容中确认 emoji 能正常显示。
- 技术名词或 API 名称只有在必须用于说明接口时才保留英文；如果会直接显示给最终用户，应优先提供中文名称或中文说明。
- 新增或调整 Python 示例、C++ 组件默认文案时，要同步检查首屏可见内容和交互展开内容，避免控件弹层、引导卡片、菜单项中残留英文界面文案。

## 组件封装计划与进度规则

- 继续封装或完善组件时，必须按照 `组件封装计划.md` 执行；用户说“做下一批”时，默认表示继续新增或完善 C++ Element 组件本体，而不是只新增 Python 组合示例。
- 每次完成组件封装、补齐组件功能、增加导出 API、更新 Python ctypes 封装或新增独立测试文件后，必须同步更新 `组件封装进度.md`。
- 每次更新 `组件封装进度.md` 后，必须在回复中告诉用户当前总进度：已完成多少、还剩多少未完成；如果文档中有明确总数，按总数统计并给出数量和百分比。
- 只有创建、绘制、主题、DPI、交互、Set/Get、Python 封装、独立测试、中文/emoji 示例和首次窗口尺寸适配都完成时，才允许在 `组件封装进度.md` 中把组件标记为“已完成”。
- 如果只是完成 `EU_CreateXxx`、基础绘制或少量属性设置，只能标记为“基础封装”或“功能完善中”，不能标记为“已完成”。
- 如果某个组件新增、删除、重命名或修改 API，导致 `docs/components/` 中对应组件文档、`docs/components/README.md`、`docs/api-index.md`、`test_new_emoji.py` 或 `DLL命令/易语言DLL命令.md`、`DLL命令/CSharp DLL命令.md`、`DLL命令/Python DLL命令.md` 与实际导出不一致，必须在同一轮修改中同步更新这些文档和封装，不能让组件 API 与对应文档出现出入。
- 如果任何新增、删除、重命名或修改涉及 AI SDK 可见能力，包括组件、导出 API、绑定、示例、模板、语言规则、prompt 或编码规则，必须在同一轮修改中同步更新 `docs/ai/` 相关文档，尤其是 `docs/ai/api_manifest.full.json`、`docs/ai/README.md`、`docs/ai/language-matrix.md` 和 `docs/ai/prompts/` 下对应语言 prompt；更新后必须运行 `python tools/validate_ai_sdk.py`，确认 AI SDK 文档与实际导出、组件清单和模板保持一致。

## 当前状态

MVP 阶段已完成：Panel、Button、EditBox、TitleBar（带窗口控制按钮）。后续按需扩展更多组件。
