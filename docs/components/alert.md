# Alert 警告提示

## 简介

`Alert` 是 new_emoji 的页面内警告提示组件。当前状态：**已完成**。

已覆盖 Element UI 常用 Alert 样式：成功、信息、警告、错误四类型，浅色/深色效果，不可关闭，自定义关闭文字，关闭回调，显示/隐藏图标，居中文案，辅助说明和长中文描述换行。所有文本支持中文与 emoji。

## 创建

| 项目 | 值 |
|---|---|
| 基础创建导出 | `EU_CreateAlert` |
| 高级创建导出 | `EU_CreateAlertEx` |
| 组件分类 | 反馈/浮层 |
| Python helper | `create_alert` / `create_alert_ex` |
| 易语言命令 | `创建警告` / `创建高级警告` |

`EU_CreateAlert` 保持旧签名兼容，默认显示图标、左对齐、描述不换行、关闭按钮为 X。需要完整样式时使用 `EU_CreateAlertEx`。

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateAlert` | 创建兼容版警告提示 |
| `EU_CreateAlertEx` | 创建高级警告提示，支持图标、居中、描述换行和关闭文字 |
| `EU_SetAlertDescription` | 设置辅助描述 |
| `EU_SetAlertType` | 设置类型：0信息 1成功 2警告 3错误 |
| `EU_SetAlertEffect` | 设置效果：0浅色 1深色 |
| `EU_SetAlertClosable` | 设置是否可关闭 |
| `EU_SetAlertAdvancedOptions` | 设置显示图标、居中和描述换行 |
| `EU_GetAlertAdvancedOptions` | 读回高级选项 |
| `EU_SetAlertCloseText` | 设置关闭文字，空文本显示 X |
| `EU_GetAlertText` | 读回标题、描述或关闭文字 |
| `EU_SetAlertClosed` | 设置关闭/重新显示 |
| `EU_TriggerAlertClose` | 程序触发关闭 |
| `EU_GetAlertClosed` | 读回关闭状态 |
| `EU_GetAlertOptions` | 读回基础选项 |
| `EU_GetAlertFullState` | 读回关闭 hover、按下、次数和最近动作 |
| `EU_SetAlertCloseCallback` | 设置关闭回调 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🚨 警告提示 示例", 240, 120, 980, 620)
root = ui.create_container(hwnd, 0, 0, 0, 940, 560)

ui.create_alert_ex(
    hwnd, root,
    title="✅ 成功提示的文案",
    description="这是一条支持中文、emoji、居中和长描述换行的提示。",
    alert_type=1,
    effect=0,
    closable=True,
    show_icon=True,
    center=True,
    wrap_description=True,
    close_text="知道了",
    x=28, y=40, w=720, h=82,
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## DPI 与图库

`component_gallery.py` 中 `Alert` 已使用专属完整演示页，按桌面端工作台风格展示基础类型、深色效果、关闭能力、图标与居中、辅助说明和交互读回。新增示例时窗口与容器需要覆盖首屏控件并保留至少 20px 逻辑余量。

## 测试

优先运行 `tests/python/test_alert_complete_components.py`。如果修改公共封装，还需要运行 `tests/python/test_feedback_components.py` 和 `tests/python/test_new_emoji.py`。

## 文档维护

如果 `Alert` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`DLL命令/易语言DLL命令.md` 和 `component_gallery.py`。
