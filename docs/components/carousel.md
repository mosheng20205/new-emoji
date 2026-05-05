# Carousel 走马灯 🎠

## 简介

`Carousel` 是 new_emoji 的媒体/工具组件，用纯 D2D 绘制轮播内容、箭头、指示器和卡片模式。当前状态：**已完成**。

本轮已补齐 Element Plus Carousel 常用桌面样式：指示器 hover/click 触发、inside/outside 位置、箭头 hover/always/never、自动播放与 interval、普通/卡片模式、水平/垂直方向、循环与非循环边界，以及 Element Plus 示例色系对应的文字和背景视觉样式。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateCarousel` |
| 组件分类 | 媒体/工具 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_carousel` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateCarousel` | 创建走马灯组件 |
| `EU_SetCarouselItems` | 设置 UTF-8 项目列表，项目可用 `|` 或换行分隔 |
| `EU_SetCarouselActive` | 设置当前激活项 |
| `EU_SetCarouselOptions` | 设置循环、指示器位置、是否显示箭头、是否显示指示器；旧接口继续兼容 |
| `EU_SetCarouselBehavior` | 设置指示器触发、箭头模式、方向、普通/卡片类型和悬停暂停 |
| `EU_GetCarouselBehavior` | 读取走马灯行为选项 |
| `EU_SetCarouselVisual` | 设置文本颜色/透明度/字号、奇偶背景、面板背景、指示器颜色和卡片缩放 |
| `EU_GetCarouselVisual` | 读取走马灯视觉样式 |
| `EU_SetCarouselAutoplay` | 设置自动播放与间隔毫秒 |
| `EU_SetCarouselAnimation` | 设置切换动画时长 |
| `EU_CarouselAdvance` | 手动上一页/下一页 |
| `EU_CarouselTick` | 外部消息循环主动推进动画和自动播放 |
| `EU_GetCarouselActive` | 读取当前激活项 |
| `EU_GetCarouselItemCount` | 读取项目数量 |
| `EU_GetCarouselOptions` | 读取旧选项和自动播放基础状态 |
| `EU_GetCarouselFullState` | 读取激活项、动画、自动播放和变化次数等完整状态 |

## 行为枚举

| 参数 | 取值 |
|---|---|
| `trigger_mode` | `0=hover` 悬停切换，`1=click` 点击切换 |
| `arrow_mode` | `0=hover` 悬停显示，`1=always` 始终显示，`2=never` 隐藏 |
| `direction` | `0=horizontal` 横向，`1=vertical` 纵向 |
| `carousel_type` | `0=normal` 普通模式，`1=card` 卡片模式 |
| `pause_on_hover` | `0` 关闭，`1` 悬停暂停自动播放 |

`EU_SetCarouselOptions` 中的旧 `show_arrows` 会继续生效：`true` 映射为 `arrow_mode=always`，`false` 映射为 `arrow_mode=never`，方便旧工程无感升级。

## 视觉样式

`EU_SetCarouselVisual` 使用 ARGB 颜色值：

| 参数 | 说明 |
|---|---|
| `text_color` | 轮播项文本颜色，例如 Element Plus 示例的 `#FF475669` |
| `text_alpha` | 文本透明度，`0-255`，示例常用约 `191` |
| `text_font_size` | 文本字号，逻辑像素 |
| `odd_bg` / `even_bg` | 奇偶项交替背景，例如 `#FFD3DCE6` / `#FF99A9BF` |
| `panel_bg` | 组件底色 |
| `active_indicator` | 激活指示器颜色 |
| `inactive_indicator` | 未激活指示器颜色 |
| `card_scale_percent` | 卡片模式侧项缩放比例，建议 `60-100` |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🎠 走马灯全样式演示", 240, 120, 980, 620)
root = ui.create_container(hwnd, 0, 0, 0, 940, 560)

carousel = ui.create_carousel(
    hwnd,
    root,
    ["🎯 第一项", "✨ 第二项", "🚀 第三项", "📦 第四项"],
    active=0,
    indicator_position=0,
    x=24,
    y=40,
    w=420,
    h=180,
)
ui.set_carousel_options(hwnd, carousel, loop=True, indicator_position=0, show_arrows=True, show_indicators=True)
ui.set_carousel_behavior(
    hwnd,
    carousel,
    trigger_mode="hover",
    arrow_mode="hover",
    direction="horizontal",
    carousel_type="normal",
    pause_on_hover=True,
)
ui.set_carousel_visual(
    hwnd,
    carousel,
    text_color=0xFF475669,
    text_alpha=191,
    text_font_size=14,
    odd_bg=0xFFD3DCE6,
    even_bg=0xFF99A9BF,
)
ui.set_carousel_autoplay(hwnd, carousel, True, 5000)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 图库演示

`examples/python/component_gallery.py` 已注册 `Carousel` 专属全样式演示页，覆盖：

- 默认 hover 指示器触发 + click 指示器触发
- `indicator-position="outside"`
- 箭头 `always` / `hover` / `never`
- 自动播放 interval 与手动暂停/继续
- `type="card"` 卡片模式
- `direction="vertical"` 且 `autoplay=false`
- Element Plus 示例色：`#475669` 文本、`#99a9bf/#d3dce6` 交替背景、字号 14/18、透明度约 0.75

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，例如 `设置走马灯行为`、`设置走马灯视觉样式`；DLL 入口名保留真实 `EU_` 导出名。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整走马灯示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量，避免在 4K / 150% DPI 首次打开时裁切底部或右侧内容。

## 测试

优先运行：

```powershell
python tests/python/test_carousel_complete_components.py
```

该测试覆盖新增行为/视觉 getter、hover/click 触发、箭头模式、垂直方向、卡片模式、自动播放 interval、非循环边界和动画进度。

## 文档维护

如果 `Carousel` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`DLL命令/易语言DLL命令.md` 和对应专项测试。
