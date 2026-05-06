# Container 容器套件

## 简介

`Container` 是 new_emoji 的基础布局容器套件，当前状态：**已完成**。

本轮补齐 Element Plus 风格的 `Container / Header / Aside / Main / Footer` 五件套：保留旧容器绝对定位语义，同时新增可选流式布局、自动横纵方向、默认区域样式、文本对齐和嵌套后台布局能力。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateContainer` |
| 区域导出 | `EU_CreateHeader` / `EU_CreateAside` / `EU_CreateMain` / `EU_CreateFooter` |
| 组件分类 | 基础/布局 |
| Python helper | `create_container` / `create_header` / `create_aside` / `create_main` / `create_footer` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateContainer` | 创建外层或嵌套容器 |
| `EU_CreateHeader` | 创建顶栏区域，默认高 60，背景 `#B3C0D1` |
| `EU_CreateAside` | 创建侧边栏区域，默认宽 200，背景 `#D3DCE6` |
| `EU_CreateMain` | 创建主要区域，默认填充剩余空间，背景 `#E9EEF3` |
| `EU_CreateFooter` | 创建底栏区域，默认高 60，背景 `#B3C0D1` |
| `EU_SetContainerLayout` / `EU_GetContainerLayout` | 设置或读取容器流式布局：0 自动、1 横向、2 纵向 |
| `EU_SetContainerRegionTextOptions` / `EU_GetContainerRegionTextOptions` | 设置或读取区域文本对齐：0 起始、1 居中、2 末尾 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📦 容器套件示例", 240, 120, 980, 680)
root = ui.create_container(hwnd, 0, 0, 0, 940, 620)
ui.set_container_layout(hwnd, root, True, 0, 0)

ui.create_header(hwnd, root, "📌 顶栏", h=60)
body = ui.create_container(hwnd, root, 0, 0, 0, 0)
ui.set_container_layout(hwnd, body, True, 1, 0)
ui.create_aside(hwnd, body, "🧭 侧边栏", w=200)
ui.create_main(hwnd, body, "📄 主要区域")
ui.create_footer(hwnd, root, "✅ 底栏", h=60)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 布局规则

- `EU_CreateContainer` 默认仍按旧行为工作，不启用流式布局，避免破坏既有绝对定位示例。
- 调用 `EU_SetContainerLayout(..., enabled=1, direction=0, gap=0)` 后启用流式布局。
- 自动方向规则：直接子元素包含 Header 或 Footer 时纵向排列，否则横向排列。
- Header/Footer 使用高度作为主轴固定尺寸，Aside 使用宽度作为主轴固定尺寸，Main 和嵌套 Container 填充剩余空间。
- 区域本身继承 Panel 能力，可挂载 Menu、Table、Button、Text 等子元素。

## 测试

优先运行：

```powershell
python tests/python/test_container_complete_components.py
python tests/python/test_foundation_layout_complete_components.py
```

`component_gallery.py` 的 Container 页已覆盖七种官方布局、样式覆盖和桌面后台壳演示。
