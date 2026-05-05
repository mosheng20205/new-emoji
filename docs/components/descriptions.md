# Descriptions 描述列表

## 简介

`Descriptions` 是 new_emoji 的数据展示组件。当前状态：**已完成**。

本组件已补齐桌面端常用描述列表样式：基础信息、带边框、无边框、横向、垂直、四种尺寸、逐项跨列、标签图标、内容标签、右上角操作按钮、逐项 label/content 背景色和内容右对齐。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateDescriptions` |
| 组件分类 | 数据展示 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_descriptions` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateDescriptions` | 创建描述列表，兼容旧 label/value 数据 |
| `EU_SetDescriptionsItems` | 设置旧协议项目 |
| `EU_SetDescriptionsItemsEx` | 设置高级项目，支持跨列、图标、标签、对齐和逐项颜色 |
| `EU_SetDescriptionsLayout` | 设置横向/垂直、尺寸、列数和边框 |
| `EU_SetDescriptionsOptions` | 设置列数、边框、标签宽度、最小行高、内容换行 |
| `EU_SetDescriptionsAdvancedOptions` | 设置响应式列和旧的末项跨列行为 |
| `EU_SetDescriptionsColors` | 设置全局边框、label/content 和标题颜色 |
| `EU_SetDescriptionsExtra` | 设置右上角操作按钮，点击触发元素点击回调 |
| `EU_GetDescriptionsItemCount` | 读取项目数量 |
| `EU_GetDescriptionsOptions` | 读取旧选项 |
| `EU_GetDescriptionsFullState` | 读取方向、尺寸、列数、项目数、操作点击次数等完整状态 |

## 高级项目协议

`EU_SetDescriptionsItemsEx` 使用 UTF-8 多行文本，每行一个项目，字段用 Tab 分隔：

```text
标签<TAB>内容<TAB>跨列<TAB>标签图标<TAB>内容类型<TAB>标签类型<TAB>内容对齐<TAB>标签背景<TAB>内容背景<TAB>标签文字色<TAB>内容文字色
```

- 内容类型：`0` 文本，`1` 内置标签。
- 标签类型：`0` 默认，`1` 成功，`2` 信息，`3` 警告，`4` 危险。
- 内容对齐：`0` 左，`1` 中，`2` 右。
- 颜色：`0` 表示主题默认，也支持 ARGB 整数或 `0xAARRGGBB`。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📋 描述列表 示例", 240, 120, 960, 620)
root = ui.create_container(hwnd, 0, 0, 0, 920, 560)
desc = ui.create_descriptions(
    hwnd, root, "📋 用户信息",
    [
        {"label": "用户名", "content": "kooriookami", "label_icon": "👤"},
        {"label": "备注", "content": "学校", "label_icon": "🏷️", "content_type": 1, "tag_type": 1},
        {"label": "联系地址", "content": "江苏省苏州市吴中区吴中大道 1188 号", "span": 2, "content_align": 2},
    ],
    columns=3, bordered=True, x=24, y=48, w=820, h=180,
    label_width=110, min_row_height=42, wrap_values=True, responsive=False,
)
ui.set_descriptions_extra(hwnd, desc, "⚙️", "操作", True, 1)
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 测试

优先运行：

```bash
python tests/python/test_descriptions_complete_components.py
```

同时检查 `component_gallery.py` 中“数据展示 / Descriptions”专属页面，确认中文与 emoji、首次窗口尺寸、垂直/边框/无边框/尺寸/跨列/样式变体均显示正常。

## 文档维护

如果 `Descriptions` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
