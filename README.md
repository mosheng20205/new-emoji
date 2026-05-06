# new_emoji

`new_emoji` 是一个 Windows 原生 UI DLL，已提供易语言、Python ctypes 和 C# P/Invoke 接入说明；同时通过统一的 `EU_` C API、`__stdcall` 调用约定和 UTF-8 字节数组文本参数，也可被 C/C++、Delphi、VB6/VBA、Go、Rust、Node.js FFI、Java JNA/JNI 等能够调用 Windows DLL 的语言接入。它采用单一 HWND + 纯 Direct2D / DirectWrite 渲染，把所有 UI 控件封装成 Element 组件，重点解决传统 GDI 子窗口在缩放和重绘时的闪烁问题，同时原生支持中文与彩色 emoji。

## 特性

- 纯 Direct2D / DirectWrite 渲染，单窗口元素树，减少闪烁。
- 统一 `EU_` C API 导出，适合 DLL 方式集成。
- 文本参数统一使用 UTF-8 字节数组 + 长度，方便易语言传递 emoji 和 Unicode 文本。
- 支持 Win32 与 x64 Release 构建，其中 Win32 是易语言交付优先目标。
- 组件完成度：88 / 88，计划内组件均已完成独立中文 emoji 验证。
- 内置主题、DPI、键鼠交互、Set/Get 状态读回和 Python ctypes helper。

## 快速入口

- [下载组件总览独立运行版 EXE](https://github.com/mosheng20205/new-emoji/releases)
- [文档总览](docs/README.md)
- [快速开始](docs/quick-start.md)
- [构建说明](docs/build.md)
- [API 约定](docs/api-conventions.md)
- [组件文档导航](docs/components/README.md)
- [Python 示例说明](docs/examples/python.md)
- [易语言 DLL 命令](DLL命令/易语言DLL命令.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)
- [图片预览](#图片预览)
- [许可证](LICENSE)

## 组件总览 Demo

如果只想快速体验组件效果，可以前往 [Releases 页面](https://github.com/mosheng20205/new-emoji/releases) 下载 `new_emoji_component_gallery.exe`，双击即可运行，不需要安装 Python 环境。

运行完整组件总览：

```powershell
python examples/python/component_gallery.py
```

该 Demo 展示当前 87 个推荐组件；`EditBox` 作为兼容编辑内核保留 API 和文档，不再放入基础布局总览。Demo 包含中文界面、emoji 渲染、主题切换、分类分页、常见交互和复杂组件预览。默认窗口保持 180 秒，便于检查首屏尺寸、DPI 和交互效果。

如果只想短时间冒烟验证：

```powershell
$env:NEW_EMOJI_GALLERY_SECONDS="12"
python examples/python/component_gallery.py
```

公共 Python ctypes 封装位于 `examples/python/new_emoji_ui.py`，普通示例建议优先复用它，而不是从测试目录导入 helper。

## 最短 Python 示例

```python
import ctypes
from ctypes import wintypes
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("✨ new_emoji 示例", 240, 120, 820, 560)
root = ui.create_container(hwnd, 0, 0, 0, 780, 500)
ui.create_text(hwnd, root, "你好，new_emoji 🚀", 32, 32, 360, 40)
ui.create_button(hwnd, root, "✅", "确认操作", 32, 96, 160, 42)
ui.dll.EU_ShowWindow(hwnd, 1)

user32 = ctypes.windll.user32
msg = wintypes.MSG()
while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
    user32.TranslateMessage(ctypes.byref(msg))
    user32.DispatchMessageW(ctypes.byref(msg))
```

> Python 位数必须和 DLL 位数一致：32 位 Python 加载 Win32 DLL，64 位 Python 加载 x64 DLL。

## 构建

```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=Win32
& "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" .\new_emoji.sln /p:Configuration=Release /p:Platform=x64
```

详细要求见 [构建说明](docs/build.md)。

## 文档维护

当某个组件新增、删除、重命名或修改导出 API 时，必须同步更新该组件文档、组件导航、`docs/api-index.md`、Python ctypes/helper 和易语言 DLL 命令文档，避免开源用户看到过期接口。

## 图片预览

截图较多，默认折叠；点击下方标题可展开查看组件总览截图。

<details>
<summary>展开 90 张组件截图</summary>

<p>
<img src="imgs/Affix.png" alt="Affix" width="480">
<img src="imgs/Alert.png" alt="Alert" width="480">
<img src="imgs/Anchor.png" alt="Anchor" width="480">
<img src="imgs/Aside.png" alt="Aside" width="480">
<img src="imgs/Autocomplete.png" alt="Autocomplete" width="480">
<img src="imgs/Avatar.png" alt="Avatar" width="480">
<img src="imgs/Backtop.png" alt="Backtop" width="480">
<img src="imgs/Badge.png" alt="Badge" width="480">
<img src="imgs/BarChart.png" alt="BarChart" width="480">
<img src="imgs/Border.png" alt="Border" width="480">
<img src="imgs/Breadcrumb.png" alt="Breadcrumb" width="480">
<img src="imgs/BulletProgress.png" alt="BulletProgress" width="480">
<img src="imgs/Button.png" alt="Button" width="480">
<img src="imgs/Calendar.png" alt="Calendar" width="480">
<img src="imgs/Card.png" alt="Card" width="480">
<img src="imgs/Carousel.png" alt="Carousel" width="480">
<img src="imgs/Cascader.png" alt="Cascader" width="480">
<img src="imgs/Checkbox.png" alt="Checkbox" width="480">
<img src="imgs/Collapse.png" alt="Collapse" width="480">
<img src="imgs/ColorPicker.png" alt="ColorPicker" width="480">
<img src="imgs/Container.png" alt="Container" width="480">
<img src="imgs/DatePicker.png" alt="DatePicker" width="480">
<img src="imgs/DateRangePicker.png" alt="DateRangePicker" width="480">
<img src="imgs/DateTimePicker.png" alt="DateTimePicker" width="480">
<img src="imgs/DateTimeRange.png" alt="DateTimeRange" width="480">
<img src="imgs/Descriptions.png" alt="Descriptions" width="480">
<img src="imgs/Dialog.png" alt="Dialog" width="480">
<img src="imgs/Divider.png" alt="Divider" width="480">
<img src="imgs/DonutChart.png" alt="DonutChart" width="480">
<img src="imgs/Drawer.png" alt="Drawer" width="480">
<img src="imgs/Dropdown.png" alt="Dropdown" width="480">
<img src="imgs/Empty.png" alt="Empty" width="480">
<img src="imgs/Footer.png" alt="Footer" width="480">
<img src="imgs/Gauge.png" alt="Gauge" width="480">
<img src="imgs/Header.png" alt="Header" width="480">
<img src="imgs/Icon.png" alt="Icon" width="480">
<img src="imgs/Image.png" alt="Image" width="480">
<img src="imgs/InfiniteScroll.png" alt="InfiniteScroll" width="480">
<img src="imgs/InfoBox.png" alt="InfoBox" width="480">
<img src="imgs/Input.png" alt="Input" width="480">
<img src="imgs/InputGroup.png" alt="InputGroup" width="480">
<img src="imgs/InputNumber.png" alt="InputNumber" width="480">
<img src="imgs/InputTag.png" alt="InputTag" width="480">
<img src="imgs/KPI%20Card.png" alt="KPI Card" width="480">
<img src="imgs/Layout.png" alt="Layout" width="480">
<img src="imgs/LineChart.png" alt="LineChart" width="480">
<img src="imgs/Link.png" alt="Link" width="480">
<img src="imgs/Loading.png" alt="Loading" width="480">
<img src="imgs/Main.png" alt="Main" width="480">
<img src="imgs/Mentions.png" alt="Mentions" width="480">
<img src="imgs/Menu.png" alt="Menu" width="480">
<img src="imgs/Message.png" alt="Message" width="480">
<img src="imgs/MessageBox.png" alt="MessageBox" width="480">
<img src="imgs/Notification.png" alt="Notification" width="480">
<img src="imgs/PageHeader.png" alt="PageHeader" width="480">
<img src="imgs/Pagination.png" alt="Pagination" width="480">
<img src="imgs/Panel.png" alt="Panel" width="480">
<img src="imgs/Popconfirm.png" alt="Popconfirm" width="480">
<img src="imgs/Popover.png" alt="Popover" width="480">
<img src="imgs/Progress.png" alt="Progress" width="480">
<img src="imgs/Radio.png" alt="Radio" width="480">
<img src="imgs/Rate.png" alt="Rate" width="480">
<img src="imgs/Result.png" alt="Result" width="480">
<img src="imgs/RingProgress.png" alt="RingProgress" width="480">
<img src="imgs/Segmented.png" alt="Segmented" width="480">
<img src="imgs/Select.png" alt="Select" width="480">
<img src="imgs/SelectV2.png" alt="SelectV2" width="480">
<img src="imgs/Skeleton.png" alt="Skeleton" width="480">
<img src="imgs/Slider.png" alt="Slider" width="480">
<img src="imgs/Space.png" alt="Space" width="480">
<img src="imgs/Statistic.png" alt="Statistic" width="480">
<img src="imgs/StatusDot.png" alt="StatusDot" width="480">
<img src="imgs/Steps.png" alt="Steps" width="480">
<img src="imgs/Switch.png" alt="Switch" width="480">
<img src="imgs/Table.png" alt="Table" width="480">
<img src="imgs/Tabs.png" alt="Tabs" width="480">
<img src="imgs/Tag.png" alt="Tag" width="480">
<img src="imgs/Text.png" alt="Text" width="480">
<img src="imgs/Timeline.png" alt="Timeline" width="480">
<img src="imgs/TimePicker.png" alt="TimePicker" width="480">
<img src="imgs/TimeRange.png" alt="TimeRange" width="480">
<img src="imgs/TimeSelect.png" alt="TimeSelect" width="480">
<img src="imgs/Tooltip.png" alt="Tooltip" width="480">
<img src="imgs/Tour.png" alt="Tour" width="480">
<img src="imgs/Transfer.png" alt="Transfer" width="480">
<img src="imgs/Tree.png" alt="Tree" width="480">
<img src="imgs/TreeSelect.png" alt="TreeSelect" width="480">
<img src="imgs/Trend.png" alt="Trend" width="480">
<img src="imgs/Upload.png" alt="Upload" width="480">
<img src="imgs/Watermark.png" alt="Watermark" width="480">
</p>

</details>

## 许可证

本项目使用 [MIT License](LICENSE) 开源。
