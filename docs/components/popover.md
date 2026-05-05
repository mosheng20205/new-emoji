# Popover 弹出框

`Popover` 已补齐 hover、click、focus、manual 四种触发方式，支持 12 方位、外部点击关闭、箭头、键盘 Escape/Tab/Enter 和内容 slot。无 slot 子元素时继续绘制原纯文本内容。

## 内容 slot

| API | 说明 |
|---|---|
| `EU_GetPopoverContentParent` | 返回 Popover 内容容器 ID，可挂载 `Table`、`Text`、`Button` 等组件 |

## API

| API | 说明 |
|---|---|
| `EU_CreatePopover` | 创建 Popover |
| `EU_SetPopoverOpen` / `EU_GetPopoverOpen` | 设置/读取打开状态 |
| `EU_SetPopoverTitle` / `EU_SetPopoverContent` | 设置标题和纯文本内容 |
| `EU_SetPopoverOptions` / `EU_GetPopoverOptions` | 旧四方位、打开状态、尺寸、关闭按钮 |
| `EU_SetPopoverAdvancedOptions` | 设置 12 方位、打开状态、尺寸、关闭按钮 |
| `EU_SetPopoverBehavior` / `EU_GetPopoverBehavior` | 设置/读取触发方式、外部关闭、箭头、offset |
| `EU_GetPopoverContentParent` | 获取内容 slot 容器 |
| `EU_TriggerPopover` | 程序打开/关闭 |
| `EU_SetPopoverActionCallback` | 打开/关闭动作回调 |
| `EU_GetPopoverText` / `EU_GetPopoverFullState` | 文本和完整状态读回 |

触发方式：`0 click`、`1 hover`、`2 focus`、`3 manual`。

## Python 示例

```python
pop = ui.create_popover(hwnd, root, "收货地址 📦", "📦 收货地址", "", 3, 60, 90, 160, 38)
ui.set_popover_advanced_options(hwnd, pop, placement="right",
                                open=False, popup_width=430,
                                popup_height=230, closable=True)
ui.set_popover_behavior(hwnd, pop, trigger_mode="click",
                        close_on_outside=True, show_arrow=True, offset=10)
content = ui.get_popover_content_parent(hwnd, pop)
ui.create_table(hwnd, content,
                ["日期", "姓名", "地址"],
                [["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"]],
                True, True, 0, 0, 380, 128)
```

## 测试

优先运行 `tests/python/test_popover_complete_components.py`。gallery 的 `Popover` 详情页覆盖四触发、嵌套表格和删除确认式组合内容。
