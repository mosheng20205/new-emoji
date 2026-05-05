# Main 主要区域

`Main` 是 Container 套件中的主要内容区域组件，当前状态：**已完成**。

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateMain` |
| 默认样式 | 背景 `#E9EEF3`，文字 `#333333`，文本居中 |
| 默认尺寸 | 填充容器剩余空间 |
| Python helper | `create_main` |

相关 API：`EU_SetContainerRegionTextOptions`、`EU_GetContainerRegionTextOptions`、`EU_SetElementText`、`EU_SetPanelStyle`。

`Main` 可承载 Table、Card、表单或任意子组件。放入启用流式布局的 Container 后，会优先填充剩余主轴空间。
