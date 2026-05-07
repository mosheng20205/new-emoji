# Window Frame 窗口框架

Window Frame API 用于创建无标题栏、自绘标题栏、自定义拖拽区、缩放边框和自绘窗口按钮。它是通用窗口外壳能力，不绑定 Chrome；浏览器式外壳、编辑器、播放器、启动器都可以复用。

## 创建

```text
EU_CreateWindowEx(title_bytes, title_len, x, y, w, h, titlebar_color, frame_flags)
EU_GetWindowFrameFlags(hwnd)
EU_SetWindowFrameFlags(hwnd, frame_flags)
```

`frame_flags`：

```text
EU_WINDOW_FRAME_DEFAULT        = 0x0000
EU_WINDOW_FRAME_BORDERLESS     = 0x0001
EU_WINDOW_FRAME_CUSTOM_CAPTION = 0x0002
EU_WINDOW_FRAME_CUSTOM_BUTTONS = 0x0004
EU_WINDOW_FRAME_RESIZABLE      = 0x0008
EU_WINDOW_FRAME_ROUNDED        = 0x0010
EU_WINDOW_FRAME_HIDE_TITLEBAR  = 0x0020
```

浏览器式外壳推荐组合：

```text
EU_WINDOW_FRAME_BROWSER_SHELL =
    BORDERLESS | CUSTOM_CAPTION | CUSTOM_BUTTONS |
    RESIZABLE | ROUNDED | HIDE_TITLEBAR
```

## 命中测试

```text
EU_SetWindowResizeBorder(hwnd, left, top, right, bottom)
EU_GetWindowResizeBorder(hwnd, left*, top*, right*, bottom*)
EU_SetWindowDragRegion(hwnd, x, y, w, h, enabled)
EU_ClearWindowDragRegions(hwnd)
EU_SetWindowNoDragRegion(hwnd, x, y, w, h, enabled)
EU_ClearWindowNoDragRegions(hwnd)
```

拖拽区用于空白标题栏/标签栏区域，非拖拽区用于地址栏、按钮、标签项等交互控件。

## 窗口命令

```text
EU_SetElementWindowCommand(hwnd, element_id, command)
EU_GetElementWindowCommand(hwnd, element_id)
```

`command`：`0=无`，`1=最小化`，`2=最大化/还原`，`3=关闭`。
