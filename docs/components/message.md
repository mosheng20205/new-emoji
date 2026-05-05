# Message 消息提示

## 简介

`Message` 是 new_emoji 的服务式轻提示组件，对齐 Element UI 的 `$message` 常用样式。当前状态：**已完成**。

已补普通消息、`success` / `warning` / `error` / `info` 四类型、可关闭、居中、轻量 HTML/VNode 等价富文本、默认 3000ms 自动关闭、`duration=0` 不自动关闭、顶部偏移、多条堆叠、关闭回调和完整状态读回。

## 创建

| 项目 | 值 |
|---|---|
| 服务式导出 | `EU_ShowMessage` |
| 组件分类 | 反馈/浮层 |
| Python helper | `show_message`、`message_success`、`message_warning`、`message_error`、`message_info` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_ShowMessage` | 显示服务式消息提示 |
| `EU_SetMessageText` | 更新消息文本 |
| `EU_SetMessageOptions` | 设置类型、关闭按钮、居中、富文本、持续时间和偏移 |
| `EU_SetMessageClosed` | 设置关闭/显示状态 |
| `EU_GetMessageOptions` | 读取基础选项 |
| `EU_GetMessageFullState` | 读取完整状态、堆叠、计时器和最近动作 |
| `EU_TriggerMessageClose` | 程序触发关闭 |
| `EU_SetMessageCloseCallback` | 设置关闭回调 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("💬 消息提示示例", 240, 120, 860, 560)
ui.message_info(hwnd, "ℹ️ 这是一条消息提示", closable=True, duration_ms=0)
ui.message_success(hwnd, "✅ 恭喜你，这是一条成功消息")
ui.message_warning(hwnd, "⚠️ 警告哦，这是一条警告消息", center=True)
ui.message_error(hwnd, "❌ 内容可以是 <span style=\"color: teal\">VNode</span>", rich=True, closable=True)
ui.dll.EU_ShowWindow(hwnd, 1)
```

## 富文本规则

轻量 HTML 子集支持 `<strong>/<b>`、`<i>/<em>`、`<span style="color: teal/#RRGGBB">` 和 `<br>`。其余标签按安全文本处理，不执行脚本、不加载图片。

## 测试

优先运行 `tests/python/test_message_complete_components.py`。
