# Window Frame 窗口框架

Window Frame API 用于创建无标题栏、自绘标题栏、自定义拖拽区、缩放边框和自绘窗口按钮。它是通用窗口外壳能力，不绑定 Chrome；浏览器式外壳、编辑器、播放器、启动器都可以复用。

## 创建

```text
EU_CreateWindowEx(title_bytes, title_len, x, y, w, h, titlebar_color, frame_flags)
EU_GetWindowFrameFlags(hwnd)
EU_SetWindowFrameFlags(hwnd, frame_flags)
EU_SetWindowRoundedCorners(hwnd, enabled, radius)
```

## 窗口图标

```text
EU_SetWindowIcon(hwnd, path_bytes, path_len)
EU_SetWindowIconFromBytes(hwnd, icon_bytes, icon_len)
```

`EU_SetWindowIcon` 使用 UTF-8 文件路径加载 `.ico` 文件；`EU_SetWindowIconFromBytes` 传入 `.ico` 文件完整字节集。两个接口都会同时设置 `ICON_BIG` 和 `ICON_SMALL`，用于任务栏、Alt-Tab 和系统标题栏图标，返回 `1` 表示成功、`0` 表示失败。

`EU_SetWindowRoundedCorners` 会设置 Windows 窗口外形圆角。支持 DWM 圆角的系统会优先使用系统抗锯齿圆角；Win10 等不支持 DWM 圆角的系统会回退为 per-pixel alpha 分层窗口，由 D2D 渲染到 32bpp PBGRA 位图后通过 `UpdateLayeredWindow(ULW_ALPHA)` 提交透明抗锯齿圆角，不再使用锯齿明显的 `SetWindowRgn` 作为最终圆角方案。`radius` 使用逻辑像素，内部按当前窗口 DPI / 屏幕缩放换算为物理半径；窗口缩放、跨屏 DPI 变化和 `EU_WINDOW_FRAME_ROUNDED` flag 都会重新应用圆角。传入 `enabled=0` 或 `radius<=0` 会恢复矩形窗口。

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
