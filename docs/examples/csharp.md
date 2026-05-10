# C# 接入说明

推荐优先使用 `bindings/csharp/NewEmoji` 中的 C# 友好封装库。它会自动处理 `new_emoji.dll` 加载、UTF-8 文本转换、`HWND` / `element_id` 管理和常用事件回调。

当前 C# 封装库支持：
- `.NET Framework 4.8`
- `net10.0-windows`
- WinForms `.NET Framework 4.8` 示例和独立可视化设计器

## 快速开始

```csharp
using NewEmoji;

var win = EmojiWindow.Create("✅ C# 示例窗口", 860, 560);
var root = win.CreateContainer(0, 0, 820, 500);

root.AddText("欢迎使用 new_emoji C# 界面库 🚀", 32, 32, 420, 40);
root.AddInput("", "请输入一段中文或 emoji 😊", 32, 88, 320, 42)
    .TextChanged += (_, e) => win.SetTitle($"✅ 输入中：{e.Text}");

root.AddButton("✅", "确认操作", 32, 152, 160, 42)
    .Clicked += (_, _) => win.ShowMessage("操作成功 🎉", EmojiMessageType.Success);

win.Show();
EmojiApplication.Run();
```

## 项目引用

```xml
<ItemGroup>
  <ProjectReference Include="..\..\bindings\csharp\NewEmoji\NewEmoji.csproj" />
</ItemGroup>
```

`NewEmoji` 类库会把 x64 / Win32 原生 DLL 复制到 `runtimes/win-x64/native/` 和 `runtimes/win-x86/native/`，运行时按当前进程位数加载。

`.NET Framework 4.8` WinForms 项目建议把对应位数的 `new_emoji.dll` 复制到输出目录根部；仓库里的 `examples/CsharpNet48/MinimalWinFormsExample.csproj` 已经配置 x64 DLL。

## API 分层

- `NewEmoji`：推荐用户入口，包含 `EmojiWindow`、`EmojiElement`、`EmojiContainer`、`EmojiButton`、`EmojiInput`、`EmojiTable`、`EmojiTabs`、`EmojiDialog`、`EmojiCard`、`EmojiDrawer`、`EmojiNotification` 等对象式 API。
- `NewEmoji.Native`：完整 P/Invoke 层，`NativeMethods.Generated.cs` 覆盖全部 `EU_` 导出。
- `NewEmoji.Runtime`：原生 DLL 加载与位数检查。
- `NewEmoji.Design`：布局 JSON 模型、校验和 C# .NET 4.8 代码生成。

如果需要调用尚未封装成对象属性的高级能力，可以直接使用 `NewEmoji.Native.NativeMethods`。

## 强类型组件

第一批表单类组件已经提供常用属性和事件：`EmojiInput`、`EmojiEditBox`、`EmojiSelect`、`EmojiCheckbox`、`EmojiRadio`、`EmojiSwitch`、`EmojiSlider`。

复杂组件已经从“可创建 + NativeMethods 兜底”推进到常用强类型封装：
- `EmojiTable`：数据、列、行、选中行、行列数量、基础选项、排序、筛选、搜索、单元格读写、单元格点击/动作事件、普通文本单元格双击原地编辑和编辑回调。
- `EmojiTabs`：标签项、激活项、激活名称、数量、类型、位置、可编辑、内容区显示、切换/关闭/新增事件。
- `EmojiDialog`：打开状态、标题、正文、按钮、按钮点击事件、基础选项、内容/页脚容器 ID。
- `EmojiCard`：标题、正文、页脚、项目、动作、阴影、悬停、样式和动作读回。
- `EmojiDrawer`：打开状态、标题、正文、位置、尺寸、动画、关闭事件、关闭前确认、内容/页脚容器 ID。
- `EmojiNotification`：标题、正文、类型、关闭状态、位置、富文本模式、堆叠、关闭事件和完整状态读回。

## .NET Framework 4.8 示例

```powershell
dotnet run --project examples\CsharpNet48\MinimalWinFormsExample.csproj
```

该示例使用 WinForms 消息循环承载 new_emoji 窗口，界面包含中文、emoji、输入框、按钮和事件回调。

## WinForms 可视化设计器

```powershell
dotnet run --project bindings\csharp\NewEmoji.Designer.WinForms48\NewEmoji.Designer.WinForms48.csproj
```

设计器支持：
- 左侧拖入 Panel、Text、Button、Input、EditBox、Table、Card、Tabs、Dialog、Drawer、Notification
- 左侧组件树选择元素
- `Ctrl` / `Shift` 点击多选组件
- 中间画布移动和调整大小
- 方向键 1px 微调，Shift + 方向键 10px 微调
- 复制、粘贴、复制一份、删除组件
- 撤销 / 重做
- 左对齐、右对齐、顶端对齐、底端对齐、水平居中、垂直居中、等宽、等高
- 右侧属性面板编辑文本、emoji、坐标、尺寸、事件名和常用组件属性
- 保存 / 打开布局 JSON
- 导出 C# `.NET Framework 4.8` 项目并构建运行

示例布局见 `examples/CsharpNet48/designer/sample_layout.json`。

## 注意事项

- 当前设计器是独立 WinForms `.NET Framework 4.8` 桌面程序，不是 Visual Studio 原生拖拽插件。
- 不要混用 WinForms 控件承载 new_emoji UI；new_emoji 仍然是单一 HWND + 纯 D2D 虚拟元素架构。
- 界面文案必须中文化，并在窗口标题、主按钮和核心展示项中使用 emoji。
- 首屏窗口尺寸要覆盖最右侧和最下方控件，并保留至少 20px 逻辑余量。

底层 P/Invoke 声明仍可参考 `DLL命令/CSharp DLL命令.md`。
