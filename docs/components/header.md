# Header 顶栏

`Header` 是 Container 套件中的顶栏区域组件，当前状态：**已完成**。

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateHeader` |
| 默认样式 | 背景 `#B3C0D1`，文字 `#333333`，文本居中 |
| 默认尺寸 | 高度 60 |
| Python helper | `create_header` |

相关 API：`EU_SetContainerRegionTextOptions`、`EU_GetContainerRegionTextOptions`、`EU_SetElementText`、`EU_SetPanelStyle`。

`Header` 可直接承载 Button、Text、Dropdown、Menu 等子元素。放入启用流式布局的 Container 后，会参与自动纵向布局。
