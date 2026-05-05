# Badge 徽标

## 概述

`Badge` 是 new_emoji 的徽标组件，用于消息数、状态点、文本提示和菜单计数。当前状态：**已完成**。

已支持的能力：

- 数值徽标
- `max` 超限截断
- 文本徽标
- `dot` 圆点模式
- 四角定位
- 独立徽标
- 语义类型配色
- 自定义 `bg/fg` 覆盖
- Python 封装
- 独立测试文件

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateBadge` |
| 组件分类 | 数据展示 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_badge` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateBadge` | 创建徽标 |
| `EU_SetBadgeValue` | 设置徽标值 |
| `EU_SetBadgeMax` | 设置最大值 |
| `EU_SetBadgeType` | 设置语义类型 |
| `EU_SetBadgeDot` | 设置圆点模式 |
| `EU_SetBadgeOptions` | 设置圆点、显示零值和偏移 |
| `EU_GetBadgeHidden` | 获取隐藏状态 |
| `EU_GetBadgeOptions` | 获取基础选项 |
| `EU_GetBadgeType` | 获取语义类型 |
| `EU_SetBadgeLayoutOptions` | 设置角标位置和独立模式 |
| `EU_GetBadgeLayoutOptions` | 获取角标位置和独立模式 |

## Python 用法

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("徽标示例 🔂", 240, 120, 920, 560)
root = ui.create_container(hwnd, 0, 0, 0, 900, 500)

badge = ui.create_badge(
    hwnd, root,
    "消息中心", "200", 99, False,
    40, 40, 220, 40,
    badge_type=3, placement=0, standalone=False
)
ui.set_badge_type(hwnd, badge, 1)
ui.set_badge_max(hwnd, badge, 99)
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧请使用中文命令名，右侧绑定真实的 `EU_` 导出名。`BadgeType` 建议从 `0` 开始按语义色选择：

- `0` 默认
- `1` 主色
- `2` 成功
- `3` 警告
- `4` 信息

## 状态与交互

- `Badge` 以单一 HWND / 纯 D2D 绘制。
- `set_element_color` 仍然可以覆盖任意背景色和前景色。
- `placement` 控制角标落点，`standalone` 控制是否按独立徽标布局。
- 文本徽标和 `dot` 圆点都应该在 `component_gallery.py` 中作为首屏可见样式演示。

## 测试

建议优先运行：

`tests/python/test_badge_complete_components.py`

如果 Badge 的 API、默认值或视觉布局变化，还要同步检查：

- `tests/python/test_new_emoji.py`
- `examples/python/new_emoji_ui.py`
- `examples/python/component_gallery.py`
- `DLL命令/易语言DLL命令.md`

## 文档维护

如果 Badge 新增或修改 API，请同步更新：

- `docs/components/README.md`
- `docs/api-index.md`
- `docs/components/manifest.json`
- `examples/python/new_emoji_ui.py`
- `tests/python/test_new_emoji.py`
- `DLL命令/易语言DLL命令.md`
