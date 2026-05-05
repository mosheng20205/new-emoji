# Loading 加载

## 简介

`Loading` 是反馈/浮层组件，当前状态：**已完成**。

本轮已补齐 Element UI 常见加载样式：局部遮罩、自定义文本、自定义遮罩背景、点状旋转、圆弧旋转、脉冲圆点、全屏锁定、服务式显示/关闭、进度显示、目标绑定和完整状态读回。

## 创建与服务式调用

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateLoading` |
| 服务式导出 | `EU_ShowLoading` / `EU_CloseLoading` |
| 组件分类 | 反馈/浮层 |
| Python helper | `create_loading` / `show_loading` / `close_loading` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateLoading` | 创建普通 Loading 元素 |
| `EU_SetLoadingActive` / `EU_GetLoadingActive` | 设置/读取激活状态 |
| `EU_SetLoadingText` / `EU_GetLoadingText` | 设置/读取 UTF-8 加载文本 |
| `EU_SetLoadingOptions` / `EU_GetLoadingOptions` | 设置/读取激活、全屏和进度 |
| `EU_SetLoadingStyle` / `EU_GetLoadingStyle` | 设置/读取遮罩色、图标色、文字色、spinner 类型和输入锁定 |
| `EU_SetLoadingTarget` | 绑定目标元素并按目标区域覆盖遮罩 |
| `EU_ShowLoading` / `EU_CloseLoading` | 服务式显示/关闭 Loading |
| `EU_GetLoadingFullState` | 读取激活、全屏、进度、目标、动画帧、定时器和最近动作 |

## Spinner 类型

| 值 | 样式 | 用途 |
|---|---|---|
| `0` | 点状旋转 | 默认样式，兼容旧版本 |
| `1` | 圆弧旋转 | 对应 Element UI `el-icon-loading` |
| `2` | 脉冲圆点 | 适合桌面端状态卡片和轻量等待 |

## Python 示例

```python
import new_emoji_ui as ui

hwnd = ui.create_window("⏳ 加载示例", 240, 120, 960, 620)
root = ui.create_container(hwnd, 0, 0, 0, 920, 560)

table = ui.create_table(
    hwnd, root,
    ["日期", "姓名", "地址"],
    [["2016-05-03", "王小虎", "上海市普陀区金沙江路 1518 弄"]],
    True, True, 40, 80, 760, 180,
)

loading = ui.create_loading(hwnd, root, "拼命加载中", True, 40, 80, 760, 180)
ui.set_loading_target(hwnd, loading, table, 0)
ui.set_loading_style(
    hwnd, loading,
    background=0xCC000000,
    spinner_color=0xFFFFFFFF,
    text_color=0xFFFFFFFF,
    spinner="el-icon-loading",
    lock_input=True,
)

service_id = ui.show_loading(
    hwnd, 0, "🔒 正在全屏处理",
    fullscreen=True,
    lock_input=True,
    background=0xCC111827,
    spinner_color=0xFF409EFF,
    text_color=0xFFFFFFFF,
    spinner="arc",
)
ui.close_loading(hwnd, service_id)
```

## 行为说明

- `fullscreen=1` 时覆盖标题栏以下的主工作区，并默认锁定底层控件输入。
- `lock_input=0` 时 Loading 只做视觉遮罩，鼠标可以穿透到底层控件。
- `lock_input=1` 时 Loading 会拦截鼠标命中和键盘焦点，适合提交、导入、保存等不可重复触发场景。
- `progress=-1` 隐藏进度条，`0-100` 显示进度条。
- 所有文本参数使用 UTF-8 字节数组 + 长度，支持中文和 emoji。

## 测试

优先运行：

```powershell
python tests/python/test_loading_complete_components.py
```

该测试覆盖默认动画、目标绑定、自定义文案、黑色遮罩、圆弧 spinner、脉冲 spinner、全屏锁定、服务式打开/关闭和关闭后底层点击恢复。

## 文档维护

如果 `Loading` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`tests/python/test_loading_complete_components.py`、`component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
