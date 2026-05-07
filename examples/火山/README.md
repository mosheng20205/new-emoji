# new_emoji 火山简单窗口 Demo

这是一个火山视窗 x64 示例工程，演示火山源码直接调用 `new_emoji.dll` 的 `EU_` 导出接口创建单一 HWND、纯 D2D 的中文 emoji 窗口。

## 文件

- `NewEmojiSimpleDemo_x64.vsln`：火山解决方案文件。
- `NewEmojiSimpleDemo_x64.vprj`：火山 x64 项目文件。
- `src/new_emoji_接口.wsv`：`new_emoji.dll` 的最小 DLL 导入封装。
- `src/main.wsv`：简单窗口 demo 主程序。
- `runtime_x64/new_emoji.dll`：运行时 DLL，编译/调试时应放在 exe 同目录。

## 运行

1. 用火山视窗打开 `NewEmojiSimpleDemo_x64.vsln`。
2. 确认项目平台为 x64。
3. 编译并运行。

首屏窗口尺寸按逻辑尺寸 `860 x 560` 创建，内容右侧和底部都保留了余量，适合高 DPI 首次打开时检查布局。
