# ColorPicker 颜色选择器

## 简介

`ColorPicker` 是 new_emoji 的表单/选择组件。当前状态：**已完成**。

已补齐 Element Plus 示例覆盖的样式：有默认值、无默认值、透明度开关、预设色、默认/中等/小型/超小四种尺寸，并支持主框直接编辑任意 `#RRGGBB` / `#AARRGGBB` 色号、弹层连续色域/色相选择、状态读回、变化回调、Python 封装和中文 emoji gallery 演示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateColorPicker` |
| 组件分类 | 表单/选择 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_colorpicker` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateColorPicker` | 创建颜色选择器，保持旧签名兼容 |
| `EU_SetColorPickerColor` / `EU_GetColorPickerColor` | 设置/读取 ARGB 颜色；空值态读回 0 |
| `EU_SetColorPickerAlpha` / `EU_GetColorPickerAlpha` | 设置/读取透明度，范围 0-255 |
| `EU_SetColorPickerHex` / `EU_GetColorPickerHex` | 设置/读取 `#RRGGBB` 或 `#AARRGGBB` 文本；空值态读回空字符串 |
| `EU_SetColorPickerOpen` / `EU_GetColorPickerOpen` | 设置/读取弹层打开状态 |
| `EU_SetColorPickerPalette` / `EU_GetColorPickerPaletteCount` | 设置/读取预设色数量，最多 32 个 ARGB 颜色 |
| `EU_SetColorPickerOptions` / `EU_GetColorPickerOptions` | 设置/读取透明度开关、尺寸和可清空状态 |
| `EU_ClearColorPicker` / `EU_GetColorPickerHasValue` | 清空颜色选择器，读取是否有值 |
| `EU_SetColorPickerChangeCallback` | 设置变化回调；空值态回调颜色与透明度均为 0 |

## 样式选项

`EU_SetColorPickerOptions(hwnd, id, show_alpha, size_mode, clearable)`：

| 参数 | 说明 |
|---|---|
| `show_alpha` | `0` 隐藏透明度条，`1` 显示透明度条 |
| `size_mode` | `0` 默认，`1` 中等，`2` 小型，`3` 超小 |
| `clearable` | `0` 不显示清空按钮，`1` 有值态显示清空按钮 |

空值态通过 `EU_ClearColorPicker` 或 Python helper 中 `color=None` 创建。空值态主框显示“未选择”，颜色读回为 `0`，十六进制文本读回为空。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🎨 颜色选择器示例", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)

ui.create_colorpicker(hwnd, root, "有默认值", 0xFF409EFF, 32, 40, 280, 42)
ui.create_colorpicker(hwnd, root, "无默认值", None, 32, 98, 280, 42)
ui.create_colorpicker(
    hwnd, root, "透明度", 0xADFF4500, 32, 156, 320, 42,
    show_alpha=True,
    palette=[0xFFFF4500, 0xFFFF8C00, 0xFFFFD700, 0xFF90EE90],
)

for i, name in enumerate(("默认", "中等", "小型", "超小")):
    ui.create_colorpicker(hwnd, root, name, 0xFF409EFF, 420, 40 + i * 48, 260, 42, size=i)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- 鼠标点击主框打开/关闭面板，主框获得焦点后可以直接键入任意 `#RRGGBB` 或 `#AARRGGBB` 色号；合法色号会立即写入当前颜色。
- 弹层顶部提供二维色域和色相条，可点击/拖动选择连续颜色；下方预设色仍作为常用快捷入口。
- `show_alpha=1` 时面板底部显示透明度条，拖动/点击后写入 alpha，并且十六进制读回使用 `#AARRGGBB`。
- `clearable=1` 且有值时主框右侧显示清空按钮；键盘 Delete/Backspace 也可清空。
- Enter/Space 切换面板，Esc 关闭面板。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。`component_gallery.py` 的 ColorPicker 专页已按桌面端属性面板、表单行和工具栏场景布置。

## 测试

优先运行：

```bash
python tests/python/test_colorpicker_complete_components.py
python tests/python/test_new_emoji.py
```

## 文档维护

如果 `ColorPicker` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
