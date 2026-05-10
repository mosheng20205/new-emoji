# new_emoji 火山模块

本目录是 `new_emoji.vcip` 的模块源目录。模块定义文件为 `new_emoji.vgrp`，最终安装包需要在火山 IDE 中通过“工具 -> 制作模块安装包”生成。

- 底层 DLL 导入：`src/new_emoji_接口.wsv`
- 中文助手封装：`src/new_emoji_助手.wsv`
- DLL 附属文件：`runtime/win32/new_emoji.dll`、`runtime/x64/new_emoji.dll`
- 当前导入导出数量：1253
- 当前组件助手数量：91

使用规则：

1. 火山项目加入本模块后，优先调用 `NewEmoji助手类`。
2. 中文和 emoji 文本统一由助手类转换为 UTF-8 字节指针 + 长度。
3. DLL 位数必须和火山项目位数一致。
4. 可见界面文案必须中文化，并在窗口标题、主要按钮和核心展示项中使用 emoji。
