# Popconfirm 气泡确认框

`Popconfirm` 复用 Popover 的扩展定位与触发能力，并补齐自定义确认/取消按钮、自定义图标文本/emoji、图标颜色、隐藏图标、确认/取消结果读回、结果重置、程序触发和结果回调。

## API

| API | 说明 |
|---|---|
| `EU_CreatePopconfirm` | 创建气泡确认框 |
| `EU_SetPopconfirmOpen` / `EU_GetPopconfirmOpen` | 设置/读取打开状态 |
| `EU_SetPopconfirmOptions` / `EU_GetPopconfirmOptions` | 旧四方位、打开状态、尺寸、结果读回 |
| `EU_SetPopconfirmAdvancedOptions` | 设置 12 方位、打开状态、尺寸、触发方式、外部关闭、箭头、offset |
| `EU_SetPopconfirmContent` | 设置标题和内容 |
| `EU_SetPopconfirmButtons` | 设置确认/取消按钮文本 |
| `EU_SetPopconfirmIcon` / `EU_GetPopconfirmIcon` | 设置/读取图标文本或 emoji、ARGB 颜色和显示状态 |
| `EU_TriggerPopconfirmResult` | 程序触发确认或取消 |
| `EU_GetPopconfirmResult` / `EU_ResetPopconfirmResult` | 读取和重置结果；`-1` 未选择、`0` 取消、`1` 确认 |
| `EU_SetPopconfirmResultCallback` | 结果回调 |
| `EU_GetPopconfirmText` / `EU_GetPopconfirmFullState` | 文本和完整状态读回 |

## Python 示例

```python
confirm = ui.create_popconfirm(hwnd, root,
                               "删除 ❓",
                               "确认操作",
                               "这是一段内容，确定删除吗？",
                               "确定 ✅",
                               "取消 ❌",
                               3, 60, 90, 132, 38)
ui.set_popconfirm_advanced_options(hwnd, confirm,
                                   placement="top",
                                   open=False,
                                   popup_width=286,
                                   popup_height=146,
                                   trigger_mode="click",
                                   close_on_outside=True,
                                   show_arrow=True,
                                   offset=8)
ui.set_popconfirm_icon(hwnd, confirm, icon="!", color=0xFFF56C6C, visible=True)
```

程序触发：

```python
ui.set_popconfirm_open(hwnd, confirm, True)
ui.trigger_popconfirm_result(hwnd, confirm, True)
result = ui.get_popconfirm_full_state(hwnd, confirm)["result"]
```

## 测试

优先运行 `tests/python/test_popconfirm_complete_components.py`。gallery 的 `Popconfirm` 详情页覆盖默认删除确认、自定义按钮、自定义图标颜色、隐藏图标、键盘操作和程序触发结果。
