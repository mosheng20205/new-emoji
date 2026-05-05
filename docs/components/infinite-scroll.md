# InfiniteScroll 无限滚动

## 简介

`InfiniteScroll` 是 `new_emoji` 的原生数据展示组件，用于桌面端长列表、任务流、记录流和卡片流。它替换旧公开 `Scrollbar` 组件；`EU_*Scrollbar*` 导出已移除。`Table` 内部仍保留私有滚动条绘制与交互，不受本组件替换影响。

组件内置列表数据、滚动偏移、触底阈值、`loading` / `no_more` / `disabled` 状态、状态行文案和竖向滚动指示条。触底时组件会先自动进入 `loading=True`，避免重复触发，再调用加载回调；宿主程序追加数据并设置状态后结束加载。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateInfiniteScroll` |
| 组件分类 | 数据展示 |
| Python helper | `create_infinite_scroll` |
| 易语言命令 | `创建无限滚动` |
| 专项测试 | `tests/python/test_infinite_scroll_complete_components.py` |
| 图库入口 | `component_gallery.py` 的 InfiniteScroll 专属页 |

## 数据格式

所有文本参数使用 UTF-8 字节数组 + 长度。

- 行以 `\n` 或 `|` 分隔。
- 每行支持 `标题\t副标题\t标签`。
- 纯文本行按标题处理。

示例：

```text
📌 发布任务 01	研发组 · 今日 09:30	进行中
🧾 审批记录 02	财务组 · 等待复核	待处理
📦 出库提醒 03	华东仓 · 即将超时	提醒
```

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateInfiniteScroll` | 创建无限滚动列表 |
| `EU_SetInfiniteScrollItems` | 重设全部项目并回到顶部 |
| `EU_AppendInfiniteScrollItems` | 追加项目，用于加载回调结束后补入新数据 |
| `EU_ClearInfiniteScrollItems` | 清空项目，显示空状态文案 |
| `EU_SetInfiniteScrollState` | 设置 `loading`、`no_more`、`disabled` |
| `EU_SetInfiniteScrollOptions` | 设置行高、间距、触底阈值、样式模式、是否显示指示条、是否显示索引 |
| `EU_SetInfiniteScrollTexts` | 设置加载中、没有更多、空状态文案 |
| `EU_SetInfiniteScrollScroll` | 设置垂直滚动位置 |
| `EU_GetInfiniteScrollFullState` | 读取项目数、滚动位置、内容高度、状态、触发次数、样式选项等完整状态 |
| `EU_SetInfiniteScrollLoadCallback` | 设置触底加载回调，签名沿用 `ValueCallback(id, item_count, scroll_y, max_scroll)` |

## 交互

- 鼠标滚轮滚动列表。
- 拖动竖向滚动指示条。
- 点击指示条轨道快速定位。
- 键盘支持 `Home`、`End`、`PageUp`、`PageDown`、上/下方向键。
- 当 `disabled=True` 或 `no_more=True` 时不会触发加载回调。
- 当已经 `loading=True` 时不会重复触发加载回调。

## Python 示例

```python
items = [
    ("📌 发布任务 01", "研发组 · 今日 09:30", "进行中"),
    ("🧾 审批记录 02", "财务组 · 等待复核", "待处理"),
]

lst = ui.create_infinite_scroll(hwnd, root, items, 40, 80, 520, 360)
ui.set_infinite_scroll_options(
    hwnd, lst,
    item_height=62,
    gap=8,
    threshold=96,
    style_mode=3,
    show_scrollbar=True,
    show_index=True,
)
ui.set_infinite_scroll_texts(
    hwnd, lst,
    "⏳ 正在加载下一批记录...",
    "✅ 没有更多记录了",
    "📭 暂无记录",
)

@ui.ValueCallback
def on_load(element_id, item_count, scroll_y, max_scroll):
    ui.append_infinite_scroll_items(
        hwnd, element_id,
        [("📌 新任务", "触底回调追加的数据", "新加载")],
    )
    ui.set_infinite_scroll_state(hwnd, element_id, loading=False, no_more=False, disabled=False)

ui.set_infinite_scroll_load_callback(hwnd, lst, on_load)
```

## 测试

优先运行：

```powershell
python tests/python/test_infinite_scroll_complete_components.py
```

测试覆盖创建、设置项目、追加项目、清空、滚轮滚动、键盘滚动、触底回调、`loading` 防重复、`disabled` 不触发、`no_more` 不触发、状态文本、样式模式和完整状态读回。

## 同步要求

如果 `InfiniteScroll` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/components/manifest.json`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`examples/python/component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
