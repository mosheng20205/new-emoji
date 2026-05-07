# BrowserViewport 浏览内容占位区

`BrowserViewport` 不实现浏览器内核，只提供 Chrome 外壳内容区占位和未来接入 WebView2 的接口位置。

## 创建

```text
EU_CreateBrowserViewport(hwnd, parent_id, x, y, w, h)
```

## API

```text
EU_SetBrowserViewportState
EU_SetBrowserViewportPlaceholder
EU_SetBrowserViewportLoading
EU_SetBrowserViewportScreenshot
EU_GetBrowserViewportState
```

状态：`0=空白页`，`1=加载中`，`2=显示截图`，`3=错误页`，`4=新标签页`。
