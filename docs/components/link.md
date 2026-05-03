# Link 链接

## 简介

`Link` 是文本型交互组件，适合文档入口、外部链接、表格行操作和轻量导航。当前已支持 Element 风格的链接类型、禁用态、悬停态、访问态、下划线开关、前后缀图标、`href/target` 状态和键鼠触发。

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateLink` | 创建链接元素，文本使用 UTF-8 字节数组 |
| `EU_SetLinkOptions` | 设置链接类型、下划线、自动打开和访问态 |
| `EU_GetLinkOptions` | 读取链接类型、下划线、自动打开和访问态 |
| `EU_SetLinkContent` | 设置前缀图标、后缀图标、href 和 target |
| `EU_GetLinkContent` | 读取前缀图标、后缀图标、href 和 target |
| `EU_SetLinkVisited` | 兼容旧接口，设置访问态 |
| `EU_GetLinkVisited` | 兼容旧接口，读取访问态 |

`type` 取值：`0` 默认、`1` 主要、`2` 成功、`3` 警告、`4` 危险、`5` 信息。默认链接使用中性色，主要链接使用主题 accent 色。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🔗 Link 链接示例", 240, 120, 960, 560)
root = ui.create_container(hwnd, 0, 0, 0, 920, 500)

ui.create_link(hwnd, root, "默认链接 🔗", 40, 40, 160, 30)
ui.create_link(hwnd, root, "主要链接 🚀", 220, 40, 160, 30, type=1)
ui.create_link(hwnd, root, "无下划线", 40, 90, 160, 30, underline=False)
ui.create_link(
    hwnd, root, "查看文档", 220, 90, 180, 30,
    type=1, prefix_icon="✏️", suffix_icon="👀",
    href="https://element.eleme.io", target="_blank",
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 状态与交互

- `enabled=0` 时链接不可点击，颜色使用主题 muted 色。
- 鼠标点击或键盘回车/空格触发时会设置 `visited=1`，并继续触发现有元素点击回调。
- `auto_open=1` 且 `href` 非空时，点击会调用系统默认方式打开链接；`target` 作为状态保存并可读回。
- 前缀/后缀图标按普通文本和 emoji 渲染，仍走 DirectWrite 彩色 emoji fallback。

## 测试

优先运行：

```powershell
python .\tests\python\test_link_complete_components.py
```

测试窗口必须保持可见，首屏要能完整展示中文和 emoji 示例，并覆盖浅色/深色主题下的基本视觉状态。

## 文档维护

如果 `Link` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py` 和 `DLL命令/易语言DLL命令.md`。
