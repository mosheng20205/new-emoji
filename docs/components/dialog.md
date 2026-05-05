# Dialog 对话框

`Dialog` 是反馈/浮层组件，已补齐本批 Element UI 示例所需的基础提示、居中、遮罩关闭、拖拽、嵌套表格、嵌套表单、外层/内层 Dialog、页脚 slot 和 before-close 关闭拦截能力。

## 位置与 slot

Dialog 创建后会自动生成两个内部容器：

| API | 说明 |
|---|---|
| `EU_GetDialogContentParent` | 返回内容 slot 容器 ID，可挂载 `Table`、`Text`、`Input`、`Select`、`Button` 等元素 |
| `EU_GetDialogFooterParent` | 返回页脚 slot 容器 ID；有子元素时替代默认按钮区绘制 |

## API

| API | 说明 |
|---|---|
| `EU_CreateDialog` | 创建 Dialog |
| `EU_SetDialogOpen` / `EU_GetDialogOpen` | 设置/读取打开状态 |
| `EU_SetDialogTitle` / `EU_SetDialogBody` | 设置标题和正文 |
| `EU_SetDialogOptions` / `EU_GetDialogOptions` | 设置打开、模态、关闭按钮、遮罩关闭、拖拽、宽高 |
| `EU_SetDialogAdvancedOptions` / `EU_GetDialogAdvancedOptions` | 设置逻辑像素宽度/百分比宽度、标题居中、页脚居中、内容 padding、页脚高度，并读回 slot ID 和关闭待确认状态 |
| `EU_SetDialogButtons` / `EU_GetDialogButtonText` | 设置和读取默认页脚按钮 |
| `EU_TriggerDialogButton` | 程序触发按钮 |
| `EU_SetDialogButtonCallback` | 按钮点击回调 |
| `EU_SetDialogBeforeCloseCallback` | 关闭前回调；返回 `1` 允许关闭，返回 `0` 拦截 |
| `EU_ConfirmDialogClose` | before-close 拦截后继续或取消关闭 |
| `EU_GetDialogText` / `EU_GetDialogFullState` | 文本和完整状态读回 |

## Python 示例

```python
dlg = ui.create_dialog(hwnd, "📦 收货地址", "", True, True, 680, 360)
ui.set_dialog_advanced_options(hwnd, dlg, width_mode=0, width_value=680,
                               center=False, footer_center=False,
                               content_padding=22, footer_height=62)
content = ui.get_dialog_content_parent(hwnd, dlg)
ui.create_table(hwnd, content,
                ["日期", "姓名", "地址"],
                [["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"]],
                True, True, 0, 0, 620, 120)
ui.set_dialog_buttons(hwnd, dlg, ["确定 ✅", "取消 ❌"])
```

before-close：

```python
@ui.BeforeCloseCallback
def on_before_close(element_id, action):
    print("🛡️ 先拦截关闭，等待用户确认")
    return 0

ui.set_dialog_before_close_callback(hwnd, dlg, on_before_close)
ui.confirm_dialog_close(hwnd, dlg, True)
```

## 测试

优先运行 `tests/python/test_dialog_complete_components.py`。gallery 的 `Dialog` 详情页覆盖基础、表格 slot、表单 slot、嵌套 Dialog、居中和 before-close 演示。
