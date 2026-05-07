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
## Chrome 气泡增强

`Popover` 增加锚定按钮、小箭头、阴影层级、自动定位和关闭策略，用于下载气泡、站点信息气泡等 Chrome 外壳场景。

```text
EU_SetPopoverAnchorElement
EU_SetPopoverArrow
EU_SetPopoverElevation
EU_SetPopoverAutoPlacement
EU_SetPopoverDismissBehavior
```

关闭策略支持外部点击关闭和 Esc 关闭两个独立开关。

## 通用 Popup API

`Popover` 现在也可通过通用 Popup API 控制，适合把下载气泡、扩展气泡锚定到任意按钮下方：

```text
EU_SetPopupAnchorElement
EU_SetPopupPlacement
EU_SetPopupOpen / EU_GetPopupOpen
EU_SetPopupDismissBehavior
```

`placement` 使用 12 方位：`0 top-start`、`1 top`、`2 top-end`、`3 bottom-start`、`4 bottom`、`5 bottom-end`、`6 left-start`、`7 left`、`8 left-end`、`9 right-start`、`10 right`、`11 right-end`。设置锚点后窗口 resize 会按锚点重新计算弹层位置。

## Element Popup 绑定

`Popover` 可作为“组件弹层绑定”的目标，由任意 Element 通过左键、右键、悬停或聚焦打开：

```text
EU_SetElementPopup(hwnd, element_id, popover_id, trigger)
EU_ClearElementPopup(hwnd, element_id, trigger)
EU_GetElementPopup(hwnd, element_id, trigger)
```

`trigger`：`0=左键点击`、`1=右键点击`、`2=悬停`、`3=聚焦`、`4=手动`。触发时会自动把 Popover 锚定到当前组件，并关闭同窗口内其他已打开的绑定弹层。
