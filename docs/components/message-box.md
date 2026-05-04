# MessageBox 消息框

## 简介

`MessageBox` 是 new_emoji 的服务式消息框组件，覆盖 Element UI 的 `$alert`、`$confirm`、`$prompt` 和 `$msgbox` 常用流程。当前状态：**已完成**。

已补基础 alert、confirm warning、prompt 输入校验、通用 msgbox、类型图标、居中、轻量 HTML/VNode 等价富文本、区分取消与关闭、确认按钮 loading/延迟关闭、输入值读回和扩展回调。

## 创建

| 项目 | 值 |
|---|---|
| 兼容导出 | `EU_ShowMessageBox`、`EU_ShowConfirmBox` |
| 扩展导出 | `EU_ShowMessageBoxEx`、`EU_ShowPromptBox` |
| 组件分类 | 反馈/浮层 |
| Python helper | `show_alert_box`、`show_confirm_box`、`show_prompt_box`、`show_msgbox` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_ShowMessageBoxEx` | 显示 alert/confirm/msgbox 扩展消息框 |
| `EU_ShowPromptBox` | 显示带输入框和校验规则的 prompt |
| `EU_SetMessageBoxBeforeClose` | 设置确认按钮 loading 文案和延迟关闭时间 |
| `EU_SetMessageBoxInput` | 设置 prompt 输入值、占位、校验规则和错误文案 |
| `EU_GetMessageBoxInput` | 读取 prompt 输入值 |
| `EU_GetMessageBoxFullState` | 读取类型、取消按钮、居中、富文本、prompt、loading、错误和最近动作 |

## 回调

`MessageBoxExCallback(messagebox_id, action, value_utf8, value_len)` 中 `action` 统一为：

| 值 | 含义 |
|---|---|
| `1` | confirm |
| `0` | cancel |
| `-1` | close |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🪟 消息框示例", 240, 120, 860, 560)
ui.show_alert_box(hwnd, "📌 HTML 片段", "<strong>这是 <i>HTML</i> 片段</strong>", rich=True, center=True)
ui.show_confirm_box(hwnd, "⚠️ 确认信息", "检测到未保存内容，是否保存修改？", box_type=2, distinguish_cancel_and_close=True)
ui.show_prompt_box(hwnd, "📧 输入邮箱", "请输入邮箱地址", placeholder="name@example.com", error="邮箱格式不正确")
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 富文本规则

轻量 HTML 子集支持 `<strong>/<b>`、`<i>/<em>`、`<span style="color: teal/#RRGGBB">` 和 `<br>`。其余标签按安全文本处理，不执行脚本、不加载图片。

## 测试

优先运行 `tests/python/test_messagebox_complete_components.py`。
