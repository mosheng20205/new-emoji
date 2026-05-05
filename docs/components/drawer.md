# Drawer 抽屉

## 简介

`Drawer` 是窗口级浮层抽屉组件，保持单 HWND + 纯 D2D 渲染。当前状态：**已完成**。

已补齐 Element UI 示例对应的抽屉样式：四方向、无标题栏、50% 百分比尺寸、before-close 关闭确认、真实内容 slot、真实页脚 slot、嵌套表格、嵌套表单、外层/内层抽屉和桌面属性面板风格。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateDrawer` |
| 组件分类 | 反馈/浮层 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_drawer` |
| 易语言命令 | `创建抽屉`，见 `DLL命令/易语言DLL命令.md` |

`EU_CreateDrawer` 创建后会自动附带两个内部 `Panel` slot：

| slot | 读取 API | 用途 |
|---|---|---|
| 内容区 | `EU_GetDrawerContentParent` | 挂载 `Table`、`Input`、`Select`、`Button`、`Text` 等真实子组件 |
| 页脚区 | `EU_GetDrawerFooterParent` | 挂载“取消 / 确定”等底部操作按钮 |

没有内容 slot 子组件时，Drawer 会继续绘制 `body` 文本，兼容旧用法。

## 位置与尺寸

| 值 | 位置 | 对应示例 |
|---|---|---|
| `0` | 左侧打开 | 从左往右开 |
| `1` | 右侧打开 | 从右往左开 |
| `2` | 顶部打开 | 从上往下开 |
| `3` | 底部打开 | 从下往上开 |

`EU_SetDrawerOptions` 的 `size` 保持旧语义：左右抽屉表示逻辑宽度，上下抽屉表示逻辑高度。

`EU_SetDrawerAdvancedOptions` 的 `size_mode` 增强尺寸表达：

| `size_mode` | `size_value` 含义 |
|---|---|
| `0` | 逻辑像素尺寸 |
| `1` | 百分比尺寸，`50` 表示 `size="50%"` |

百分比尺寸会按当前窗口客户区宽高计算；左右抽屉按宽度百分比，上下抽屉按高度百分比。

## 高级选项

```c
EU_SetDrawerAdvancedOptions(
    hwnd, id,
    show_header,
    show_close,
    close_on_escape,
    content_padding,
    footer_height,
    size_mode,
    size_value
);
```

| 参数 | 说明 |
|---|---|
| `show_header` | `0` 表示无标题栏，对应 `with-header=false` |
| `show_close` | `0` 仅隐藏右上角关闭按钮，不改变程序关闭能力 |
| `close_on_escape` | `0` 禁用 ESC 关闭 |
| `content_padding` | 内容区逻辑 padding |
| `footer_height` | 页脚 slot 逻辑高度 |
| `size_mode` | `0` 像素，`1` 百分比 |
| `size_value` | 像素值或百分比值 |

`EU_GetDrawerAdvancedOptions` 可读回：

`show_header`、`show_close`、`close_on_escape`、`content_padding`、`footer_height`、`size_mode`、`size_value`、`content_parent_id`、`footer_parent_id`、`close_pending`。

## 关闭语义

关闭来源统一进入 `close_drawer(action)`：

| action | 来源 |
|---|---|
| `2` | 鼠标点击关闭按钮 |
| `3` | ESC 键 |
| `4` | 程序调用 `EU_TriggerDrawerClose` |
| `5` | 点击遮罩 |

如果设置了 `EU_SetDrawerBeforeCloseCallback`：

- 回调返回非 0：立即关闭。
- 回调返回 `0`：保持打开，`close_pending=1`。
- `EU_ConfirmDrawerClose(hwnd, id, 1)`：确认继续关闭。
- `EU_ConfirmDrawerClose(hwnd, id, 0)`：取消关闭并清除 pending。
- `EU_SetDrawerCloseCallback` 只在实际关闭后触发。

`show_close=0` 只隐藏关闭按钮；`EU_TriggerDrawerClose` 和 `EU_ConfirmDrawerClose` 仍可关闭抽屉。

## 嵌套抽屉

Drawer 默认是窗口级浮层。内层 Drawer 应作为独立根级 Drawer 创建，由外层内容 slot 中的按钮打开；后创建的内层抽屉位于更高绘制层，等价于 Element UI 的 `append-to-body=true` 场景。

## Python 示例

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📚 抽屉示例", 240, 120, 980, 640)
root = ui.create_container(hwnd, 0, 0, 0, 940, 580)

drawer = ui.create_drawer(hwnd, "🧾 活动表单", "", placement=1, modal=True, closable=True, size=420)
ui.set_drawer_options(hwnd, drawer, placement=1, open=True, modal=True, closable=True, close_on_mask=True, size=420)
ui.set_drawer_advanced_options(hwnd, drawer, content_padding=24, footer_height=66, size_mode=1, size_value=50)

content = ui.get_drawer_content_parent(hwnd, drawer)
footer = ui.get_drawer_footer_parent(hwnd, drawer)

ui.create_text(hwnd, content, "活动名称", 0, 8, 96, 28)
ui.create_input(hwnd, content, "", "请输入活动名称 🎉", x=110, y=2, w=260, h=38)
ui.create_text(hwnd, content, "活动区域", 0, 66, 96, 28)
ui.create_select(hwnd, content, "请选择活动区域", ["区域一：上海", "区域二：北京"], 0, 110, 60, 260, 38)

ui.create_button(hwnd, footer, "❌", "取消", 120, 14, 90, 36)
ui.create_button(hwnd, footer, "✅", "确定", 224, 14, 90, 36)
ui.dll.EU_ShowWindow(hwnd, 1)
```

## Gallery 覆盖

`examples/python/component_gallery.py` 中的 Drawer 专页为桌面端“抽屉工作台”，覆盖：

- “方向与尺寸”：左/右/上/下打开，含 50% 宽度/高度。
- “无标题栏”：`show_header=0`、`show_close=0`。
- “嵌套表格”：内容 slot 内挂真实 `Table`。
- “嵌套表单”：内容 slot 内挂真实 `Input`、`Select`，页脚 slot 挂按钮。
- “关闭确认”：before-close 触发中文确认 `Dialog`，确认后调用 `EU_ConfirmDrawerClose`。
- “外层/内层抽屉”：外层内容按钮打开根级内层 Drawer。
- “自定义风格”：通过颜色/字体接口和现有表单控件组合出桌面属性面板。

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateDrawer` | 创建抽屉 |
| `EU_SetDrawerOpen` / `EU_GetDrawerOpen` | 设置/读取打开状态 |
| `EU_SetDrawerTitle` / `EU_SetDrawerBody` | 设置标题和正文 |
| `EU_SetDrawerPlacement` | 设置打开方向 |
| `EU_SetDrawerOptions` / `EU_GetDrawerOptions` | 设置/读取基础选项 |
| `EU_SetDrawerAdvancedOptions` / `EU_GetDrawerAdvancedOptions` | 设置/读取标题栏、ESC、padding、footer、百分比尺寸和 slot 状态 |
| `EU_GetDrawerContentParent` | 获取内容 slot 容器 ID |
| `EU_GetDrawerFooterParent` | 获取页脚 slot 容器 ID |
| `EU_SetDrawerBeforeCloseCallback` | 设置关闭前拦截回调 |
| `EU_ConfirmDrawerClose` | before-close pending 后确认或取消关闭 |
| `EU_SetDrawerAnimation` | 设置打开动画时长 |
| `EU_TriggerDrawerClose` | 程序触发关闭 |
| `EU_GetDrawerText` | 读取标题或正文 |
| `EU_GetDrawerFullState` | 读取完整基础状态 |
| `EU_SetDrawerCloseCallback` | 设置实际关闭后的回调 |

## 测试

优先运行：

```powershell
python tests/python/test_drawer_complete_components.py
```

测试覆盖四方向、像素/百分比尺寸、header/close/ESC 开关、content/footer slot、真实表格/表单挂载、before-close pending/取消/确认、关闭回调和外层/内层抽屉。
