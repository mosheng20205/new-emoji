# new_emoji.dll Python DLL 命令

本文件记录 `new_emoji.dll` 的 Python `ctypes` 声明，按 `src/new_emoji.def` 和 `src/exports.h` 生成。
当前导出命令数量：1153。

通用约定：
- 32 位 Python 加载 `bin/Win32/Release/new_emoji.dll`，64 位 Python 加载 `bin/x64/Release/new_emoji.dll`。
- 使用 `ctypes.WinDLL` 加载 DLL，匹配 `__stdcall` 调用约定。
- 文本参数按 UTF-8 bytes + 长度传入；可用 `text.encode("utf-8")` 生成字节。
- 输出文本由调用方创建 `ctypes.create_string_buffer(size)` 或 `ctypes.c_ubyte` 数组后传入。
- 回调使用 `ctypes.WINFUNCTYPE`，并且必须保存 Python 回调对象引用，避免被垃圾回收。
- 公共 helper 位于 `examples/python/new_emoji_ui.py`，普通示例建议优先复用 helper。

## 基础导入

```python
import ctypes
from ctypes import wintypes

dll = ctypes.WinDLL("new_emoji.dll")
```

## 回调类型

```python
ElementClickCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int)
ElementKeyCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
ElementTextCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
ElementValueCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
ElementBeforeCloseCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
TableCellCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
TableVirtualRowCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
DropdownCommandCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
MenuSelectCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
WindowResizeCallback = ctypes.WINFUNCTYPE(None, wintypes.HWND, ctypes.c_int, ctypes.c_int)
WindowCloseCallback = ctypes.WINFUNCTYPE(None, wintypes.HWND)
MessageBoxResultCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int)
MessageBoxExCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TreeNodeEventCallback = ctypes.WINFUNCTYPE(None, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TreeNodeAllowDragCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
TreeNodeAllowDropCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int)
DateDisabledCallback = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)
```

## 导出声明

## EU_CreateWindow

```python
dll.EU_CreateWindow.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32]
dll.EU_CreateWindow.restype = wintypes.HWND
```
## EU_CreateWindowDark

```python
dll.EU_CreateWindowDark.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32]
dll.EU_CreateWindowDark.restype = wintypes.HWND
```
## EU_DestroyWindow

```python
dll.EU_DestroyWindow.argtypes = [wintypes.HWND]
dll.EU_DestroyWindow.restype = None
```
## EU_ShowWindow

```python
dll.EU_ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ShowWindow.restype = None
```
## EU_RunMessageLoop

```python
dll.EU_RunMessageLoop.argtypes = []
dll.EU_RunMessageLoop.restype = ctypes.c_int
```
## EU_SetWindowTitle

```python
dll.EU_SetWindowTitle.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetWindowTitle.restype = None
```
## EU_SetWindowBounds

```python
dll.EU_SetWindowBounds.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetWindowBounds.restype = None
```
## EU_GetWindowBounds

```python
dll.EU_GetWindowBounds.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetWindowBounds.restype = ctypes.c_int
```
## EU_CreatePanel

```python
dll.EU_CreatePanel.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePanel.restype = ctypes.c_int
```
## EU_CreateButton

```python
dll.EU_CreateButton.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateButton.restype = ctypes.c_int
```
## EU_CreateEditBox

```python
dll.EU_CreateEditBox.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateEditBox.restype = ctypes.c_int
```
## EU_CreateInfoBox

```python
dll.EU_CreateInfoBox.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInfoBox.restype = ctypes.c_int
```
## EU_CreateText

```python
dll.EU_CreateText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateText.restype = ctypes.c_int
```
## EU_CreateLink

```python
dll.EU_CreateLink.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLink.restype = ctypes.c_int
```
## EU_CreateIcon

```python
dll.EU_CreateIcon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateIcon.restype = ctypes.c_int
```
## EU_CreateSpace

```python
dll.EU_CreateSpace.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSpace.restype = ctypes.c_int
```
## EU_CreateContainer

```python
dll.EU_CreateContainer.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateContainer.restype = ctypes.c_int
```
## EU_CreateHeader

```python
dll.EU_CreateHeader.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateHeader.restype = ctypes.c_int
```
## EU_CreateAside

```python
dll.EU_CreateAside.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAside.restype = ctypes.c_int
```
## EU_CreateMain

```python
dll.EU_CreateMain.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateMain.restype = ctypes.c_int
```
## EU_CreateFooter

```python
dll.EU_CreateFooter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateFooter.restype = ctypes.c_int
```
## EU_CreateLayout

```python
dll.EU_CreateLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLayout.restype = ctypes.c_int
```
## EU_CreateBorder

```python
dll.EU_CreateBorder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBorder.restype = ctypes.c_int
```
## EU_CreateCheckbox

```python
dll.EU_CreateCheckbox.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCheckbox.restype = ctypes.c_int
```
## EU_CreateCheckboxGroup

```python
dll.EU_CreateCheckboxGroup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCheckboxGroup.restype = ctypes.c_int
```
## EU_CreateRadio

```python
dll.EU_CreateRadio.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRadio.restype = ctypes.c_int
```
## EU_CreateRadioGroup

```python
dll.EU_CreateRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRadioGroup.restype = ctypes.c_int
```
## EU_CreateSwitch

```python
dll.EU_CreateSwitch.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSwitch.restype = ctypes.c_int
```
## EU_CreateSlider

```python
dll.EU_CreateSlider.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSlider.restype = ctypes.c_int
```
## EU_CreateInputNumber

```python
dll.EU_CreateInputNumber.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInputNumber.restype = ctypes.c_int
```
## EU_CreateInput

```python
dll.EU_CreateInput.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInput.restype = ctypes.c_int
```
## EU_CreateInputGroup

```python
dll.EU_CreateInputGroup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInputGroup.restype = ctypes.c_int
```
## EU_CreateInputTag

```python
dll.EU_CreateInputTag.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInputTag.restype = ctypes.c_int
```
## EU_CreateSelect

```python
dll.EU_CreateSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSelect.restype = ctypes.c_int
```
## EU_CreateSelectV2

```python
dll.EU_CreateSelectV2.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSelectV2.restype = ctypes.c_int
```
## EU_CreateRate

```python
dll.EU_CreateRate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRate.restype = ctypes.c_int
```
## EU_CreateColorPicker

```python
dll.EU_CreateColorPicker.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateColorPicker.restype = ctypes.c_int
```
## EU_CreateTag

```python
dll.EU_CreateTag.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTag.restype = ctypes.c_int
```
## EU_CreateBadge

```python
dll.EU_CreateBadge.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBadge.restype = ctypes.c_int
```
## EU_CreateProgress

```python
dll.EU_CreateProgress.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateProgress.restype = ctypes.c_int
```
## EU_CreateAvatar

```python
dll.EU_CreateAvatar.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAvatar.restype = ctypes.c_int
```
## EU_CreateEmpty

```python
dll.EU_CreateEmpty.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateEmpty.restype = ctypes.c_int
```
## EU_CreateSkeleton

```python
dll.EU_CreateSkeleton.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSkeleton.restype = ctypes.c_int
```
## EU_CreateDescriptions

```python
dll.EU_CreateDescriptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDescriptions.restype = ctypes.c_int
```
## EU_CreateTable

```python
dll.EU_CreateTable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTable.restype = ctypes.c_int
```
## EU_CreateCard

```python
dll.EU_CreateCard.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCard.restype = ctypes.c_int
```
## EU_CreateCollapse

```python
dll.EU_CreateCollapse.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCollapse.restype = ctypes.c_int
```
## EU_CreateTimeline

```python
dll.EU_CreateTimeline.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTimeline.restype = ctypes.c_int
```
## EU_CreateStatistic

```python
dll.EU_CreateStatistic.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateStatistic.restype = ctypes.c_int
```
## EU_CreateKpiCard

```python
dll.EU_CreateKpiCard.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateKpiCard.restype = ctypes.c_int
```
## EU_CreateTrend

```python
dll.EU_CreateTrend.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTrend.restype = ctypes.c_int
```
## EU_CreateStatusDot

```python
dll.EU_CreateStatusDot.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateStatusDot.restype = ctypes.c_int
```
## EU_CreateGauge

```python
dll.EU_CreateGauge.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateGauge.restype = ctypes.c_int
```
## EU_CreateRingProgress

```python
dll.EU_CreateRingProgress.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateRingProgress.restype = ctypes.c_int
```
## EU_CreateBulletProgress

```python
dll.EU_CreateBulletProgress.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBulletProgress.restype = ctypes.c_int
```
## EU_CreateLineChart

```python
dll.EU_CreateLineChart.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLineChart.restype = ctypes.c_int
```
## EU_CreateBarChart

```python
dll.EU_CreateBarChart.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBarChart.restype = ctypes.c_int
```
## EU_CreateDonutChart

```python
dll.EU_CreateDonutChart.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDonutChart.restype = ctypes.c_int
```
## EU_CreateDivider

```python
dll.EU_CreateDivider.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDivider.restype = ctypes.c_int
```
## EU_CreateCalendar

```python
dll.EU_CreateCalendar.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCalendar.restype = ctypes.c_int
```
## EU_CreateTree

```python
dll.EU_CreateTree.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTree.restype = ctypes.c_int
```
## EU_CreateTreeSelect

```python
dll.EU_CreateTreeSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTreeSelect.restype = ctypes.c_int
```
## EU_CreateTransfer

```python
dll.EU_CreateTransfer.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTransfer.restype = ctypes.c_int
```
## EU_CreateAutocomplete

```python
dll.EU_CreateAutocomplete.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAutocomplete.restype = ctypes.c_int
```
## EU_CreateMentions

```python
dll.EU_CreateMentions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateMentions.restype = ctypes.c_int
```
## EU_CreateCascader

```python
dll.EU_CreateCascader.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCascader.restype = ctypes.c_int
```
## EU_CreateDatePicker

```python
dll.EU_CreateDatePicker.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDatePicker.restype = ctypes.c_int
```
## EU_CreateTimePicker

```python
dll.EU_CreateTimePicker.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTimePicker.restype = ctypes.c_int
```
## EU_CreateDateTimePicker

```python
dll.EU_CreateDateTimePicker.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDateTimePicker.restype = ctypes.c_int
```
## EU_CreateTimeSelect

```python
dll.EU_CreateTimeSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTimeSelect.restype = ctypes.c_int
```
## EU_CreateDropdown

```python
dll.EU_CreateDropdown.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDropdown.restype = ctypes.c_int
```
## EU_CreateMenu

```python
dll.EU_CreateMenu.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateMenu.restype = ctypes.c_int
```
## EU_CreateAnchor

```python
dll.EU_CreateAnchor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAnchor.restype = ctypes.c_int
```
## EU_CreateBacktop

```python
dll.EU_CreateBacktop.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBacktop.restype = ctypes.c_int
```
## EU_CreateSegmented

```python
dll.EU_CreateSegmented.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSegmented.restype = ctypes.c_int
```
## EU_CreatePageHeader

```python
dll.EU_CreatePageHeader.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePageHeader.restype = ctypes.c_int
```
## EU_CreateAffix

```python
dll.EU_CreateAffix.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAffix.restype = ctypes.c_int
```
## EU_CreateWatermark

```python
dll.EU_CreateWatermark.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateWatermark.restype = ctypes.c_int
```
## EU_CreateTour

```python
dll.EU_CreateTour.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTour.restype = ctypes.c_int
```
## EU_CreateImage

```python
dll.EU_CreateImage.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateImage.restype = ctypes.c_int
```
## EU_CreateCarousel

```python
dll.EU_CreateCarousel.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateCarousel.restype = ctypes.c_int
```
## EU_CreateUpload

```python
dll.EU_CreateUpload.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateUpload.restype = ctypes.c_int
```
## EU_CreateInfiniteScroll

```python
dll.EU_CreateInfiniteScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateInfiniteScroll.restype = ctypes.c_int
```
## EU_CreateBreadcrumb

```python
dll.EU_CreateBreadcrumb.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateBreadcrumb.restype = ctypes.c_int
```
## EU_CreateTabs

```python
dll.EU_CreateTabs.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTabs.restype = ctypes.c_int
```
## EU_CreatePagination

```python
dll.EU_CreatePagination.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePagination.restype = ctypes.c_int
```
## EU_CreateSteps

```python
dll.EU_CreateSteps.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateSteps.restype = ctypes.c_int
```
## EU_CreateAlert

```python
dll.EU_CreateAlert.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAlert.restype = ctypes.c_int
```
## EU_CreateAlertEx

```python
dll.EU_CreateAlertEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateAlertEx.restype = ctypes.c_int
```
## EU_CreateResult

```python
dll.EU_CreateResult.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateResult.restype = ctypes.c_int
```
## EU_CreateNotification

```python
dll.EU_CreateNotification.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateNotification.restype = ctypes.c_int
```
## EU_CreateLoading

```python
dll.EU_CreateLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateLoading.restype = ctypes.c_int
```
## EU_CreateDialog

```python
dll.EU_CreateDialog.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDialog.restype = ctypes.c_int
```
## EU_SetDialogAdvancedOptions

```python
dll.EU_SetDialogAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDialogAdvancedOptions.restype = None
```
## EU_GetDialogAdvancedOptions

```python
dll.EU_GetDialogAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDialogAdvancedOptions.restype = ctypes.c_int
```
## EU_GetDialogContentParent

```python
dll.EU_GetDialogContentParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDialogContentParent.restype = ctypes.c_int
```
## EU_GetDialogFooterParent

```python
dll.EU_GetDialogFooterParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDialogFooterParent.restype = ctypes.c_int
```
## EU_SetDialogBeforeCloseCallback

```python
dll.EU_SetDialogBeforeCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementBeforeCloseCallback]
dll.EU_SetDialogBeforeCloseCallback.restype = None
```
## EU_ConfirmDialogClose

```python
dll.EU_ConfirmDialogClose.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ConfirmDialogClose.restype = None
```
## EU_CreateDrawer

```python
dll.EU_CreateDrawer.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDrawer.restype = ctypes.c_int
```
## EU_CreateTooltip

```python
dll.EU_CreateTooltip.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateTooltip.restype = ctypes.c_int
```
## EU_SetTooltipAdvancedOptions

```python
dll.EU_SetTooltipAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTooltipAdvancedOptions.restype = None
```
## EU_GetTooltipAdvancedOptions

```python
dll.EU_GetTooltipAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTooltipAdvancedOptions.restype = ctypes.c_int
```
## EU_CreatePopover

```python
dll.EU_CreatePopover.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePopover.restype = ctypes.c_int
```
## EU_SetPopoverAdvancedOptions

```python
dll.EU_SetPopoverAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverAdvancedOptions.restype = None
```
## EU_SetPopoverBehavior

```python
dll.EU_SetPopoverBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverBehavior.restype = None
```
## EU_GetPopoverBehavior

```python
dll.EU_GetPopoverBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopoverBehavior.restype = ctypes.c_int
```
## EU_GetPopoverContentParent

```python
dll.EU_GetPopoverContentParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopoverContentParent.restype = ctypes.c_int
```
## EU_CreatePopconfirm

```python
dll.EU_CreatePopconfirm.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreatePopconfirm.restype = ctypes.c_int
```
## EU_SetPopconfirmAdvancedOptions

```python
dll.EU_SetPopconfirmAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopconfirmAdvancedOptions.restype = None
```
## EU_SetPopconfirmIcon

```python
dll.EU_SetPopconfirmIcon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32, ctypes.c_int]
dll.EU_SetPopconfirmIcon.restype = None
```
## EU_GetPopconfirmIcon

```python
dll.EU_GetPopconfirmIcon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopconfirmIcon.restype = ctypes.c_int
```
## EU_ShowMessage

```python
dll.EU_ShowMessage.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_ShowMessage.restype = ctypes.c_int
```
## EU_ShowNotification

```python
dll.EU_ShowNotification.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_ShowNotification.restype = ctypes.c_int
```
## EU_ShowMessageBox

```python
dll.EU_ShowMessageBox.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, MessageBoxResultCallback]
dll.EU_ShowMessageBox.restype = ctypes.c_int
```
## EU_ShowConfirmBox

```python
dll.EU_ShowConfirmBox.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, MessageBoxResultCallback]
dll.EU_ShowConfirmBox.restype = ctypes.c_int
```
## EU_ShowMessageBoxEx

```python
dll.EU_ShowMessageBoxEx.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, MessageBoxExCallback]
dll.EU_ShowMessageBoxEx.restype = ctypes.c_int
```
## EU_ShowPromptBox

```python
dll.EU_ShowPromptBox.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, MessageBoxExCallback]
dll.EU_ShowPromptBox.restype = ctypes.c_int
```
## EU_SetElementText

```python
dll.EU_SetElementText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetElementText.restype = None
```
## EU_GetElementText

```python
dll.EU_GetElementText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetElementText.restype = ctypes.c_int
```
## EU_SetElementBounds

```python
dll.EU_SetElementBounds.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetElementBounds.restype = None
```
## EU_GetElementBounds

```python
dll.EU_GetElementBounds.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetElementBounds.restype = ctypes.c_int
```
## EU_SetElementVisible

```python
dll.EU_SetElementVisible.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetElementVisible.restype = None
```
## EU_GetElementVisible

```python
dll.EU_GetElementVisible.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetElementVisible.restype = ctypes.c_int
```
## EU_SetElementEnabled

```python
dll.EU_SetElementEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetElementEnabled.restype = None
```
## EU_GetElementEnabled

```python
dll.EU_GetElementEnabled.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetElementEnabled.restype = ctypes.c_int
```
## EU_SetElementColor

```python
dll.EU_SetElementColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetElementColor.restype = None
```
## EU_SetElementFont

```python
dll.EU_SetElementFont.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_float]
dll.EU_SetElementFont.restype = None
```
## EU_SetTextOptions

```python
dll.EU_SetTextOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTextOptions.restype = None
```
## EU_GetTextOptions

```python
dll.EU_GetTextOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTextOptions.restype = ctypes.c_int
```
## EU_SetLinkOptions

```python
dll.EU_SetLinkOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLinkOptions.restype = None
```
## EU_GetLinkOptions

```python
dll.EU_GetLinkOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLinkOptions.restype = ctypes.c_int
```
## EU_SetLinkContent

```python
dll.EU_SetLinkContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetLinkContent.restype = None
```
## EU_GetLinkContent

```python
dll.EU_GetLinkContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetLinkContent.restype = ctypes.c_int
```
## EU_SetLinkVisited

```python
dll.EU_SetLinkVisited.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetLinkVisited.restype = None
```
## EU_GetLinkVisited

```python
dll.EU_GetLinkVisited.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLinkVisited.restype = ctypes.c_int
```
## EU_SetIconOptions

```python
dll.EU_SetIconOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_float, ctypes.c_float]
dll.EU_SetIconOptions.restype = None
```
## EU_GetIconOptions

```python
dll.EU_GetIconOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
dll.EU_GetIconOptions.restype = ctypes.c_int
```
## EU_SetPanelStyle

```python
dll.EU_SetPanelStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_int]
dll.EU_SetPanelStyle.restype = None
```
## EU_GetPanelStyle

```python
dll.EU_GetPanelStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPanelStyle.restype = ctypes.c_int
```
## EU_SetPanelLayout

```python
dll.EU_SetPanelLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPanelLayout.restype = None
```
## EU_GetPanelLayout

```python
dll.EU_GetPanelLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPanelLayout.restype = ctypes.c_int
```
## EU_SetContainerLayout

```python
dll.EU_SetContainerLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetContainerLayout.restype = None
```
## EU_GetContainerLayout

```python
dll.EU_GetContainerLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetContainerLayout.restype = ctypes.c_int
```
## EU_SetContainerRegionTextOptions

```python
dll.EU_SetContainerRegionTextOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetContainerRegionTextOptions.restype = None
```
## EU_GetContainerRegionTextOptions

```python
dll.EU_GetContainerRegionTextOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetContainerRegionTextOptions.restype = ctypes.c_int
```
## EU_SetLayoutOptions

```python
dll.EU_SetLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLayoutOptions.restype = None
```
## EU_GetLayoutOptions

```python
dll.EU_GetLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLayoutOptions.restype = ctypes.c_int
```
## EU_SetLayoutChildWeight

```python
dll.EU_SetLayoutChildWeight.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLayoutChildWeight.restype = None
```
## EU_GetLayoutChildWeight

```python
dll.EU_GetLayoutChildWeight.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetLayoutChildWeight.restype = ctypes.c_int
```
## EU_SetBorderOptions

```python
dll.EU_SetBorderOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_float, ctypes.c_float, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBorderOptions.restype = None
```
## EU_GetBorderOptions

```python
dll.EU_GetBorderOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
dll.EU_GetBorderOptions.restype = ctypes.c_int
```
## EU_SetBorderDashed

```python
dll.EU_SetBorderDashed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBorderDashed.restype = None
```
## EU_GetBorderDashed

```python
dll.EU_GetBorderDashed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBorderDashed.restype = ctypes.c_int
```
## EU_SetInfoBoxText

```python
dll.EU_SetInfoBoxText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInfoBoxText.restype = None
```
## EU_SetInfoBoxOptions

```python
dll.EU_SetInfoBoxOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInfoBoxOptions.restype = None
```
## EU_SetInfoBoxClosed

```python
dll.EU_SetInfoBoxClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInfoBoxClosed.restype = None
```
## EU_GetInfoBoxClosed

```python
dll.EU_GetInfoBoxClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInfoBoxClosed.restype = ctypes.c_int
```
## EU_GetInfoBoxPreferredHeight

```python
dll.EU_GetInfoBoxPreferredHeight.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInfoBoxPreferredHeight.restype = ctypes.c_int
```
## EU_SetSpaceSize

```python
dll.EU_SetSpaceSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSpaceSize.restype = None
```
## EU_GetSpaceSize

```python
dll.EU_GetSpaceSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSpaceSize.restype = ctypes.c_int
```
## EU_SetDividerOptions

```python
dll.EU_SetDividerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_float, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDividerOptions.restype = None
```
## EU_GetDividerOptions

```python
dll.EU_GetDividerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDividerOptions.restype = ctypes.c_int
```
## EU_SetDividerSpacing

```python
dll.EU_SetDividerSpacing.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDividerSpacing.restype = None
```
## EU_GetDividerSpacing

```python
dll.EU_GetDividerSpacing.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDividerSpacing.restype = ctypes.c_int
```
## EU_SetDividerLineStyle

```python
dll.EU_SetDividerLineStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDividerLineStyle.restype = None
```
## EU_GetDividerLineStyle

```python
dll.EU_GetDividerLineStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDividerLineStyle.restype = ctypes.c_int
```
## EU_SetDividerContent

```python
dll.EU_SetDividerContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDividerContent.restype = None
```
## EU_GetDividerContent

```python
dll.EU_GetDividerContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDividerContent.restype = ctypes.c_int
```
## EU_SetButtonEmoji

```python
dll.EU_SetButtonEmoji.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetButtonEmoji.restype = None
```
## EU_SetButtonVariant

```python
dll.EU_SetButtonVariant.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetButtonVariant.restype = None
```
## EU_GetButtonState

```python
dll.EU_GetButtonState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetButtonState.restype = ctypes.c_int
```
## EU_SetButtonOptions

```python
dll.EU_SetButtonOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetButtonOptions.restype = None
```
## EU_GetButtonOptions

```python
dll.EU_GetButtonOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetButtonOptions.restype = ctypes.c_int
```
## EU_SetEditBoxText

```python
dll.EU_SetEditBoxText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEditBoxText.restype = None
```
## EU_SetEditBoxOptions

```python
dll.EU_SetEditBoxOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEditBoxOptions.restype = None
```
## EU_GetEditBoxOptions

```python
dll.EU_GetEditBoxOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetEditBoxOptions.restype = ctypes.c_int
```
## EU_GetEditBoxState

```python
dll.EU_GetEditBoxState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetEditBoxState.restype = ctypes.c_int
```
## EU_GetEditBoxText

```python
dll.EU_GetEditBoxText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetEditBoxText.restype = ctypes.c_int
```
## EU_SetEditBoxScroll

```python
dll.EU_SetEditBoxScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetEditBoxScroll.restype = None
```
## EU_GetEditBoxScroll

```python
dll.EU_GetEditBoxScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetEditBoxScroll.restype = ctypes.c_int
```
## EU_SetEditBoxTextCallback

```python
dll.EU_SetEditBoxTextCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementTextCallback]
dll.EU_SetEditBoxTextCallback.restype = None
```
## EU_SetElementFocus

```python
dll.EU_SetElementFocus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetElementFocus.restype = None
```
## EU_SetCheckboxChecked

```python
dll.EU_SetCheckboxChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCheckboxChecked.restype = None
```
## EU_GetCheckboxChecked

```python
dll.EU_GetCheckboxChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCheckboxChecked.restype = ctypes.c_int
```
## EU_SetCheckboxIndeterminate

```python
dll.EU_SetCheckboxIndeterminate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCheckboxIndeterminate.restype = None
```
## EU_GetCheckboxIndeterminate

```python
dll.EU_GetCheckboxIndeterminate.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCheckboxIndeterminate.restype = ctypes.c_int
```
## EU_SetCheckboxOptions

```python
dll.EU_SetCheckboxOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCheckboxOptions.restype = None
```
## EU_GetCheckboxOptions

```python
dll.EU_GetCheckboxOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCheckboxOptions.restype = ctypes.c_int
```
## EU_SetCheckboxGroupItems

```python
dll.EU_SetCheckboxGroupItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCheckboxGroupItems.restype = None
```
## EU_SetCheckboxGroupValue

```python
dll.EU_SetCheckboxGroupValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCheckboxGroupValue.restype = None
```
## EU_GetCheckboxGroupValue

```python
dll.EU_GetCheckboxGroupValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCheckboxGroupValue.restype = ctypes.c_int
```
## EU_SetCheckboxGroupOptions

```python
dll.EU_SetCheckboxGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCheckboxGroupOptions.restype = None
```
## EU_GetCheckboxGroupOptions

```python
dll.EU_GetCheckboxGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCheckboxGroupOptions.restype = ctypes.c_int
```
## EU_GetCheckboxGroupState

```python
dll.EU_GetCheckboxGroupState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCheckboxGroupState.restype = ctypes.c_int
```
## EU_SetCheckboxGroupChangeCallback

```python
dll.EU_SetCheckboxGroupChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetCheckboxGroupChangeCallback.restype = None
```
## EU_SetRadioChecked

```python
dll.EU_SetRadioChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetRadioChecked.restype = None
```
## EU_GetRadioChecked

```python
dll.EU_GetRadioChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRadioChecked.restype = ctypes.c_int
```
## EU_SetRadioGroup

```python
dll.EU_SetRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRadioGroup.restype = None
```
## EU_GetRadioGroup

```python
dll.EU_GetRadioGroup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroup.restype = ctypes.c_int
```
## EU_SetRadioValue

```python
dll.EU_SetRadioValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRadioValue.restype = None
```
## EU_GetRadioValue

```python
dll.EU_GetRadioValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioValue.restype = ctypes.c_int
```
## EU_SetRadioOptions

```python
dll.EU_SetRadioOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetRadioOptions.restype = None
```
## EU_GetRadioOptions

```python
dll.EU_GetRadioOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRadioOptions.restype = ctypes.c_int
```
## EU_SetRadioGroupItems

```python
dll.EU_SetRadioGroupItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRadioGroupItems.restype = None
```
## EU_SetRadioGroupValue

```python
dll.EU_SetRadioGroupValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRadioGroupValue.restype = None
```
## EU_GetRadioGroupValue

```python
dll.EU_GetRadioGroupValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRadioGroupValue.restype = ctypes.c_int
```
## EU_GetRadioGroupSelectedIndex

```python
dll.EU_GetRadioGroupSelectedIndex.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRadioGroupSelectedIndex.restype = ctypes.c_int
```
## EU_SetRadioGroupOptions

```python
dll.EU_SetRadioGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetRadioGroupOptions.restype = None
```
## EU_GetRadioGroupOptions

```python
dll.EU_GetRadioGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRadioGroupOptions.restype = ctypes.c_int
```
## EU_GetRadioGroupState

```python
dll.EU_GetRadioGroupState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRadioGroupState.restype = ctypes.c_int
```
## EU_SetRadioGroupChangeCallback

```python
dll.EU_SetRadioGroupChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetRadioGroupChangeCallback.restype = None
```
## EU_SetSwitchChecked

```python
dll.EU_SetSwitchChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSwitchChecked.restype = None
```
## EU_GetSwitchChecked

```python
dll.EU_GetSwitchChecked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchChecked.restype = ctypes.c_int
```
## EU_SetSwitchLoading

```python
dll.EU_SetSwitchLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSwitchLoading.restype = None
```
## EU_GetSwitchLoading

```python
dll.EU_GetSwitchLoading.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchLoading.restype = ctypes.c_int
```
## EU_SetSwitchTexts

```python
dll.EU_SetSwitchTexts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSwitchTexts.restype = None
```
## EU_GetSwitchOptions

```python
dll.EU_GetSwitchOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSwitchOptions.restype = ctypes.c_int
```
## EU_SetSwitchActiveColor

```python
dll.EU_SetSwitchActiveColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_SetSwitchActiveColor.restype = None
```
## EU_GetSwitchActiveColor

```python
dll.EU_GetSwitchActiveColor.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchActiveColor.restype = ctypes.c_uint32
```
## EU_SetSwitchInactiveColor

```python
dll.EU_SetSwitchInactiveColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_SetSwitchInactiveColor.restype = None
```
## EU_GetSwitchInactiveColor

```python
dll.EU_GetSwitchInactiveColor.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchInactiveColor.restype = ctypes.c_uint32
```
## EU_SetSwitchValue

```python
dll.EU_SetSwitchValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSwitchValue.restype = None
```
## EU_GetSwitchValue

```python
dll.EU_GetSwitchValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchValue.restype = ctypes.c_int
```
## EU_SetSwitchSize

```python
dll.EU_SetSwitchSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSwitchSize.restype = None
```
## EU_GetSwitchSize

```python
dll.EU_GetSwitchSize.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSwitchSize.restype = ctypes.c_int
```
## EU_SetSliderRange

```python
dll.EU_SetSliderRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSliderRange.restype = None
```
## EU_SetSliderValue

```python
dll.EU_SetSliderValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSliderValue.restype = None
```
## EU_GetSliderValue

```python
dll.EU_GetSliderValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSliderValue.restype = ctypes.c_int
```
## EU_SetSliderOptions

```python
dll.EU_SetSliderOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSliderOptions.restype = None
```
## EU_GetSliderStep

```python
dll.EU_GetSliderStep.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSliderStep.restype = ctypes.c_int
```
## EU_GetSliderOptions

```python
dll.EU_GetSliderOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSliderOptions.restype = ctypes.c_int
```
## EU_SetSliderRangeValue

```python
dll.EU_SetSliderRangeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSliderRangeValue.restype = None
```
## EU_GetSliderRangeValue

```python
dll.EU_GetSliderRangeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSliderRangeValue.restype = ctypes.c_int
```
## EU_SetSliderRangeMode

```python
dll.EU_SetSliderRangeMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSliderRangeMode.restype = None
```
## EU_GetSliderRangeMode

```python
dll.EU_GetSliderRangeMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSliderRangeMode.restype = ctypes.c_int
```
## EU_SetSliderValueCallback

```python
dll.EU_SetSliderValueCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetSliderValueCallback.restype = None
```
## EU_SetInputNumberRange

```python
dll.EU_SetInputNumberRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputNumberRange.restype = None
```
## EU_SetInputNumberStep

```python
dll.EU_SetInputNumberStep.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputNumberStep.restype = None
```
## EU_SetInputNumberValue

```python
dll.EU_SetInputNumberValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputNumberValue.restype = None
```
## EU_GetInputNumberValue

```python
dll.EU_GetInputNumberValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputNumberValue.restype = ctypes.c_int
```
## EU_GetInputNumberCanStep

```python
dll.EU_GetInputNumberCanStep.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputNumberCanStep.restype = ctypes.c_int
```
## EU_GetInputNumberOptions

```python
dll.EU_GetInputNumberOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputNumberOptions.restype = ctypes.c_int
```
## EU_SetInputNumberPrecision

```python
dll.EU_SetInputNumberPrecision.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputNumberPrecision.restype = None
```
## EU_GetInputNumberPrecision

```python
dll.EU_GetInputNumberPrecision.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputNumberPrecision.restype = ctypes.c_int
```
## EU_SetInputNumberText

```python
dll.EU_SetInputNumberText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputNumberText.restype = ctypes.c_int
```
## EU_GetInputNumberText

```python
dll.EU_GetInputNumberText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputNumberText.restype = ctypes.c_int
```
## EU_GetInputNumberState

```python
dll.EU_GetInputNumberState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputNumberState.restype = ctypes.c_int
```
## EU_SetInputNumberValueCallback

```python
dll.EU_SetInputNumberValueCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetInputNumberValueCallback.restype = None
```
## EU_SetInputNumberStepStrictly

```python
dll.EU_SetInputNumberStepStrictly.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputNumberStepStrictly.restype = None
```
## EU_GetInputNumberStepStrictly

```python
dll.EU_GetInputNumberStepStrictly.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputNumberStepStrictly.restype = ctypes.c_int
```
## EU_SetInputValue

```python
dll.EU_SetInputValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputValue.restype = None
```
## EU_GetInputValue

```python
dll.EU_GetInputValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputValue.restype = ctypes.c_int
```
## EU_SetInputPlaceholder

```python
dll.EU_SetInputPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputPlaceholder.restype = None
```
## EU_SetInputAffixes

```python
dll.EU_SetInputAffixes.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputAffixes.restype = None
```
## EU_SetInputIcons

```python
dll.EU_SetInputIcons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputIcons.restype = None
```
## EU_GetInputIcons

```python
dll.EU_GetInputIcons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputIcons.restype = ctypes.c_int
```
## EU_SetInputClearable

```python
dll.EU_SetInputClearable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputClearable.restype = None
```
## EU_SetInputOptions

```python
dll.EU_SetInputOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputOptions.restype = None
```
## EU_SetInputVisualOptions

```python
dll.EU_SetInputVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputVisualOptions.restype = None
```
## EU_GetInputVisualOptions

```python
dll.EU_GetInputVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputVisualOptions.restype = ctypes.c_int
```
## EU_SetInputSelection

```python
dll.EU_SetInputSelection.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputSelection.restype = None
```
## EU_GetInputSelection

```python
dll.EU_GetInputSelection.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputSelection.restype = ctypes.c_int
```
## EU_SetInputContextMenuEnabled

```python
dll.EU_SetInputContextMenuEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputContextMenuEnabled.restype = None
```
## EU_GetInputContextMenuEnabled

```python
dll.EU_GetInputContextMenuEnabled.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputContextMenuEnabled.restype = ctypes.c_int
```
## EU_GetInputState

```python
dll.EU_GetInputState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputState.restype = ctypes.c_int
```
## EU_SetInputScroll

```python
dll.EU_SetInputScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputScroll.restype = None
```
## EU_GetInputScroll

```python
dll.EU_GetInputScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputScroll.restype = ctypes.c_int
```
## EU_SetInputMaxLength

```python
dll.EU_SetInputMaxLength.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputMaxLength.restype = None
```
## EU_GetInputMaxLength

```python
dll.EU_GetInputMaxLength.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputMaxLength.restype = ctypes.c_int
```
## EU_SetInputTextCallback

```python
dll.EU_SetInputTextCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementTextCallback]
dll.EU_SetInputTextCallback.restype = None
```
## EU_SetInputGroupValue

```python
dll.EU_SetInputGroupValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputGroupValue.restype = None
```
## EU_GetInputGroupValue

```python
dll.EU_GetInputGroupValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputGroupValue.restype = ctypes.c_int
```
## EU_SetInputGroupOptions

```python
dll.EU_SetInputGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputGroupOptions.restype = None
```
## EU_GetInputGroupOptions

```python
dll.EU_GetInputGroupOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputGroupOptions.restype = ctypes.c_int
```
## EU_SetInputGroupTextAddon

```python
dll.EU_SetInputGroupTextAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputGroupTextAddon.restype = None
```
## EU_SetInputGroupButtonAddon

```python
dll.EU_SetInputGroupButtonAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetInputGroupButtonAddon.restype = None
```
## EU_SetInputGroupSelectAddon

```python
dll.EU_SetInputGroupSelectAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputGroupSelectAddon.restype = None
```
## EU_ClearInputGroupAddon

```python
dll.EU_ClearInputGroupAddon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ClearInputGroupAddon.restype = None
```
## EU_GetInputGroupInputElementId

```python
dll.EU_GetInputGroupInputElementId.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputGroupInputElementId.restype = ctypes.c_int
```
## EU_GetInputGroupAddonElementId

```python
dll.EU_GetInputGroupAddonElementId.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetInputGroupAddonElementId.restype = ctypes.c_int
```
## EU_SetInputTagTags

```python
dll.EU_SetInputTagTags.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputTagTags.restype = None
```
## EU_SetInputTagPlaceholder

```python
dll.EU_SetInputTagPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputTagPlaceholder.restype = None
```
## EU_SetInputTagOptions

```python
dll.EU_SetInputTagOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInputTagOptions.restype = None
```
## EU_GetInputTagCount

```python
dll.EU_GetInputTagCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetInputTagCount.restype = ctypes.c_int
```
## EU_GetInputTagOptions

```python
dll.EU_GetInputTagOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInputTagOptions.restype = ctypes.c_int
```
## EU_AddInputTagItem

```python
dll.EU_AddInputTagItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AddInputTagItem.restype = ctypes.c_int
```
## EU_RemoveInputTagItem

```python
dll.EU_RemoveInputTagItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_RemoveInputTagItem.restype = ctypes.c_int
```
## EU_SetInputTagInputValue

```python
dll.EU_SetInputTagInputValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInputTagInputValue.restype = None
```
## EU_GetInputTagInputValue

```python
dll.EU_GetInputTagInputValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputTagInputValue.restype = ctypes.c_int
```
## EU_GetInputTagItem

```python
dll.EU_GetInputTagItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetInputTagItem.restype = ctypes.c_int
```
## EU_SetInputTagChangeCallback

```python
dll.EU_SetInputTagChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementTextCallback]
dll.EU_SetInputTagChangeCallback.restype = None
```
## EU_SetSelectOptions

```python
dll.EU_SetSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectOptions.restype = None
```
## EU_SetSelectIndex

```python
dll.EU_SetSelectIndex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectIndex.restype = None
```
## EU_GetSelectIndex

```python
dll.EU_GetSelectIndex.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectIndex.restype = ctypes.c_int
```
## EU_SetSelectOpen

```python
dll.EU_SetSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectOpen.restype = None
```
## EU_GetSelectOpen

```python
dll.EU_GetSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectOpen.restype = ctypes.c_int
```
## EU_SetSelectSearch

```python
dll.EU_SetSelectSearch.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectSearch.restype = None
```
## EU_SetSelectOptionDisabled

```python
dll.EU_SetSelectOptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectOptionDisabled.restype = None
```
## EU_SetSelectOptionAlignment

```python
dll.EU_SetSelectOptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectOptionAlignment.restype = None
```
## EU_GetSelectOptionAlignment

```python
dll.EU_GetSelectOptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectOptionAlignment.restype = ctypes.c_int
```
## EU_SetSelectValueAlignment

```python
dll.EU_SetSelectValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectValueAlignment.restype = None
```
## EU_GetSelectValueAlignment

```python
dll.EU_GetSelectValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectValueAlignment.restype = ctypes.c_int
```
## EU_GetSelectOptionCount

```python
dll.EU_GetSelectOptionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectOptionCount.restype = ctypes.c_int
```
## EU_GetSelectMatchedCount

```python
dll.EU_GetSelectMatchedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectMatchedCount.restype = ctypes.c_int
```
## EU_GetSelectOptionDisabled

```python
dll.EU_GetSelectOptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectOptionDisabled.restype = ctypes.c_int
```
## EU_SetSelectMultiple

```python
dll.EU_SetSelectMultiple.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectMultiple.restype = None
```
## EU_GetSelectMultiple

```python
dll.EU_GetSelectMultiple.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectMultiple.restype = ctypes.c_int
```
## EU_SetSelectSelectedIndices

```python
dll.EU_SetSelectSelectedIndices.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectSelectedIndices.restype = None
```
## EU_GetSelectSelectedCount

```python
dll.EU_GetSelectSelectedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectSelectedCount.restype = ctypes.c_int
```
## EU_GetSelectSelectedAt

```python
dll.EU_GetSelectSelectedAt.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectSelectedAt.restype = ctypes.c_int
```
## EU_SetSelectChangeCallback

```python
dll.EU_SetSelectChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetSelectChangeCallback.restype = None
```
## EU_SetSelectV2Options

```python
dll.EU_SetSelectV2Options.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectV2Options.restype = None
```
## EU_SetSelectV2Index

```python
dll.EU_SetSelectV2Index.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2Index.restype = None
```
## EU_SetSelectV2VisibleCount

```python
dll.EU_SetSelectV2VisibleCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2VisibleCount.restype = None
```
## EU_GetSelectV2Index

```python
dll.EU_GetSelectV2Index.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2Index.restype = ctypes.c_int
```
## EU_GetSelectV2VisibleCount

```python
dll.EU_GetSelectV2VisibleCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2VisibleCount.restype = ctypes.c_int
```
## EU_SetSelectV2Open

```python
dll.EU_SetSelectV2Open.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2Open.restype = None
```
## EU_GetSelectV2Open

```python
dll.EU_GetSelectV2Open.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2Open.restype = ctypes.c_int
```
## EU_SetSelectV2Search

```python
dll.EU_SetSelectV2Search.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSelectV2Search.restype = None
```
## EU_SetSelectV2OptionDisabled

```python
dll.EU_SetSelectV2OptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2OptionDisabled.restype = None
```
## EU_SetSelectV2OptionAlignment

```python
dll.EU_SetSelectV2OptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2OptionAlignment.restype = None
```
## EU_GetSelectV2OptionAlignment

```python
dll.EU_GetSelectV2OptionAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2OptionAlignment.restype = ctypes.c_int
```
## EU_SetSelectV2ValueAlignment

```python
dll.EU_SetSelectV2ValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2ValueAlignment.restype = None
```
## EU_GetSelectV2ValueAlignment

```python
dll.EU_GetSelectV2ValueAlignment.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2ValueAlignment.restype = ctypes.c_int
```
## EU_GetSelectV2OptionCount

```python
dll.EU_GetSelectV2OptionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2OptionCount.restype = ctypes.c_int
```
## EU_GetSelectV2MatchedCount

```python
dll.EU_GetSelectV2MatchedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2MatchedCount.restype = ctypes.c_int
```
## EU_GetSelectV2OptionDisabled

```python
dll.EU_GetSelectV2OptionDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetSelectV2OptionDisabled.restype = ctypes.c_int
```
## EU_SetSelectV2ScrollIndex

```python
dll.EU_SetSelectV2ScrollIndex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSelectV2ScrollIndex.restype = None
```
## EU_GetSelectV2ScrollIndex

```python
dll.EU_GetSelectV2ScrollIndex.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSelectV2ScrollIndex.restype = ctypes.c_int
```
## EU_SetSelectV2ChangeCallback

```python
dll.EU_SetSelectV2ChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetSelectV2ChangeCallback.restype = None
```
## EU_SetRateValue

```python
dll.EU_SetRateValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetRateValue.restype = None
```
## EU_GetRateValue

```python
dll.EU_GetRateValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRateValue.restype = ctypes.c_int
```
## EU_SetRateMax

```python
dll.EU_SetRateMax.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetRateMax.restype = None
```
## EU_GetRateMax

```python
dll.EU_GetRateMax.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRateMax.restype = ctypes.c_int
```
## EU_SetRateValueX2

```python
dll.EU_SetRateValueX2.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetRateValueX2.restype = None
```
## EU_GetRateValueX2

```python
dll.EU_GetRateValueX2.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRateValueX2.restype = ctypes.c_int
```
## EU_SetRateOptions

```python
dll.EU_SetRateOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetRateOptions.restype = None
```
## EU_GetRateOptions

```python
dll.EU_GetRateOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRateOptions.restype = ctypes.c_int
```
## EU_SetRateTexts

```python
dll.EU_SetRateTexts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetRateTexts.restype = None
```
## EU_SetRateColors

```python
dll.EU_SetRateColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetRateColors.restype = None
```
## EU_GetRateColors

```python
dll.EU_GetRateColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetRateColors.restype = ctypes.c_int
```
## EU_SetRateIcons

```python
dll.EU_SetRateIcons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRateIcons.restype = None
```
## EU_GetRateIcons

```python
dll.EU_GetRateIcons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRateIcons.restype = ctypes.c_int
```
## EU_SetRateTextItems

```python
dll.EU_SetRateTextItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRateTextItems.restype = None
```
## EU_SetRateDisplayOptions

```python
dll.EU_SetRateDisplayOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetRateDisplayOptions.restype = None
```
## EU_GetRateDisplayOptions

```python
dll.EU_GetRateDisplayOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetRateDisplayOptions.restype = ctypes.c_int
```
## EU_SetRateChangeCallback

```python
dll.EU_SetRateChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetRateChangeCallback.restype = None
```
## EU_SetColorPickerColor

```python
dll.EU_SetColorPickerColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_SetColorPickerColor.restype = None
```
## EU_GetColorPickerColor

```python
dll.EU_GetColorPickerColor.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerColor.restype = ctypes.c_int
```
## EU_SetColorPickerAlpha

```python
dll.EU_SetColorPickerAlpha.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetColorPickerAlpha.restype = None
```
## EU_GetColorPickerAlpha

```python
dll.EU_GetColorPickerAlpha.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerAlpha.restype = ctypes.c_int
```
## EU_SetColorPickerHex

```python
dll.EU_SetColorPickerHex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetColorPickerHex.restype = ctypes.c_int
```
## EU_GetColorPickerHex

```python
dll.EU_GetColorPickerHex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetColorPickerHex.restype = ctypes.c_int
```
## EU_SetColorPickerOpen

```python
dll.EU_SetColorPickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetColorPickerOpen.restype = None
```
## EU_GetColorPickerOpen

```python
dll.EU_GetColorPickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerOpen.restype = ctypes.c_int
```
## EU_SetColorPickerPalette

```python
dll.EU_SetColorPickerPalette.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.c_int]
dll.EU_SetColorPickerPalette.restype = None
```
## EU_GetColorPickerPaletteCount

```python
dll.EU_GetColorPickerPaletteCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerPaletteCount.restype = ctypes.c_int
```
## EU_SetColorPickerOptions

```python
dll.EU_SetColorPickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetColorPickerOptions.restype = None
```
## EU_GetColorPickerOptions

```python
dll.EU_GetColorPickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetColorPickerOptions.restype = ctypes.c_int
```
## EU_ClearColorPicker

```python
dll.EU_ClearColorPicker.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearColorPicker.restype = None
```
## EU_GetColorPickerHasValue

```python
dll.EU_GetColorPickerHasValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetColorPickerHasValue.restype = ctypes.c_int
```
## EU_SetColorPickerChangeCallback

```python
dll.EU_SetColorPickerChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetColorPickerChangeCallback.restype = None
```
## EU_SetTagType

```python
dll.EU_SetTagType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagType.restype = None
```
## EU_SetTagEffect

```python
dll.EU_SetTagEffect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagEffect.restype = None
```
## EU_SetTagClosable

```python
dll.EU_SetTagClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagClosable.restype = None
```
## EU_SetTagClosed

```python
dll.EU_SetTagClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagClosed.restype = None
```
## EU_GetTagClosed

```python
dll.EU_GetTagClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTagClosed.restype = ctypes.c_int
```
## EU_GetTagOptions

```python
dll.EU_GetTagOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTagOptions.restype = ctypes.c_int
```
## EU_SetTagSize

```python
dll.EU_SetTagSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTagSize.restype = None
```
## EU_SetTagThemeColor

```python
dll.EU_SetTagThemeColor.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32]
dll.EU_SetTagThemeColor.restype = None
```
## EU_GetTagVisualOptions

```python
dll.EU_GetTagVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetTagVisualOptions.restype = ctypes.c_int
```
## EU_SetTagCloseCallback

```python
dll.EU_SetTagCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementClickCallback]
dll.EU_SetTagCloseCallback.restype = None
```
## EU_SetBadgeValue

```python
dll.EU_SetBadgeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBadgeValue.restype = None
```
## EU_SetBadgeMax

```python
dll.EU_SetBadgeMax.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeMax.restype = None
```
## EU_SetBadgeType

```python
dll.EU_SetBadgeType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeType.restype = None
```
## EU_SetBadgeDot

```python
dll.EU_SetBadgeDot.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeDot.restype = None
```
## EU_SetBadgeOptions

```python
dll.EU_SetBadgeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeOptions.restype = None
```
## EU_GetBadgeHidden

```python
dll.EU_GetBadgeHidden.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBadgeHidden.restype = ctypes.c_int
```
## EU_GetBadgeOptions

```python
dll.EU_GetBadgeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBadgeOptions.restype = ctypes.c_int
```
## EU_GetBadgeType

```python
dll.EU_GetBadgeType.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBadgeType.restype = ctypes.c_int
```
## EU_SetBadgeLayoutOptions

```python
dll.EU_SetBadgeLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBadgeLayoutOptions.restype = None
```
## EU_GetBadgeLayoutOptions

```python
dll.EU_GetBadgeLayoutOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBadgeLayoutOptions.restype = ctypes.c_int
```
## EU_SetProgressPercentage

```python
dll.EU_SetProgressPercentage.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetProgressPercentage.restype = None
```
## EU_GetProgressPercentage

```python
dll.EU_GetProgressPercentage.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressPercentage.restype = ctypes.c_int
```
## EU_SetProgressStatus

```python
dll.EU_SetProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetProgressStatus.restype = None
```
## EU_GetProgressStatus

```python
dll.EU_GetProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressStatus.restype = ctypes.c_int
```
## EU_SetProgressShowText

```python
dll.EU_SetProgressShowText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetProgressShowText.restype = None
```
## EU_SetProgressOptions

```python
dll.EU_SetProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetProgressOptions.restype = None
```
## EU_GetProgressOptions

```python
dll.EU_GetProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetProgressOptions.restype = ctypes.c_int
```
## EU_SetProgressFormatOptions

```python
dll.EU_SetProgressFormatOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetProgressFormatOptions.restype = None
```
## EU_GetProgressFormatOptions

```python
dll.EU_GetProgressFormatOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetProgressFormatOptions.restype = ctypes.c_int
```
## EU_SetProgressTextInside

```python
dll.EU_SetProgressTextInside.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetProgressTextInside.restype = None
```
## EU_GetProgressTextInside

```python
dll.EU_GetProgressTextInside.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressTextInside.restype = ctypes.c_int
```
## EU_SetProgressColors

```python
dll.EU_SetProgressColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetProgressColors.restype = None
```
## EU_GetProgressColors

```python
dll.EU_GetProgressColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetProgressColors.restype = ctypes.c_int
```
## EU_SetProgressColorStops

```python
dll.EU_SetProgressColorStops.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetProgressColorStops.restype = None
```
## EU_GetProgressColorStopCount

```python
dll.EU_GetProgressColorStopCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetProgressColorStopCount.restype = ctypes.c_int
```
## EU_GetProgressColorStop

```python
dll.EU_GetProgressColorStop.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetProgressColorStop.restype = ctypes.c_int
```
## EU_SetProgressCompleteText

```python
dll.EU_SetProgressCompleteText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetProgressCompleteText.restype = None
```
## EU_GetProgressCompleteText

```python
dll.EU_GetProgressCompleteText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetProgressCompleteText.restype = ctypes.c_int
```
## EU_SetProgressTextTemplate

```python
dll.EU_SetProgressTextTemplate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetProgressTextTemplate.restype = None
```
## EU_GetProgressTextTemplate

```python
dll.EU_GetProgressTextTemplate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetProgressTextTemplate.restype = ctypes.c_int
```
## EU_SetAvatarShape

```python
dll.EU_SetAvatarShape.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAvatarShape.restype = None
```
## EU_SetAvatarSource

```python
dll.EU_SetAvatarSource.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarSource.restype = None
```
## EU_SetAvatarFallbackSource

```python
dll.EU_SetAvatarFallbackSource.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarFallbackSource.restype = None
```
## EU_SetAvatarIcon

```python
dll.EU_SetAvatarIcon.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarIcon.restype = None
```
## EU_SetAvatarErrorText

```python
dll.EU_SetAvatarErrorText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAvatarErrorText.restype = None
```
## EU_SetAvatarFit

```python
dll.EU_SetAvatarFit.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAvatarFit.restype = None
```
## EU_GetAvatarImageStatus

```python
dll.EU_GetAvatarImageStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAvatarImageStatus.restype = ctypes.c_int
```
## EU_GetAvatarOptions

```python
dll.EU_GetAvatarOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAvatarOptions.restype = ctypes.c_int
```
## EU_SetEmptyDescription

```python
dll.EU_SetEmptyDescription.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEmptyDescription.restype = None
```
## EU_SetEmptyOptions

```python
dll.EU_SetEmptyOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEmptyOptions.restype = None
```
## EU_SetEmptyActionClicked

```python
dll.EU_SetEmptyActionClicked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetEmptyActionClicked.restype = None
```
## EU_GetEmptyActionClicked

```python
dll.EU_GetEmptyActionClicked.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetEmptyActionClicked.restype = ctypes.c_int
```
## EU_SetEmptyActionCallback

```python
dll.EU_SetEmptyActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementClickCallback]
dll.EU_SetEmptyActionCallback.restype = None
```
## EU_SetEmptyImage

```python
dll.EU_SetEmptyImage.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetEmptyImage.restype = None
```
## EU_SetEmptyImageSize

```python
dll.EU_SetEmptyImageSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetEmptyImageSize.restype = None
```
## EU_GetEmptyImageStatus

```python
dll.EU_GetEmptyImageStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetEmptyImageStatus.restype = ctypes.c_int
```
## EU_GetEmptyImageSize

```python
dll.EU_GetEmptyImageSize.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetEmptyImageSize.restype = ctypes.c_int
```
## EU_SetSkeletonRows

```python
dll.EU_SetSkeletonRows.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSkeletonRows.restype = None
```
## EU_SetSkeletonAnimated

```python
dll.EU_SetSkeletonAnimated.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSkeletonAnimated.restype = None
```
## EU_SetSkeletonLoading

```python
dll.EU_SetSkeletonLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSkeletonLoading.restype = None
```
## EU_SetSkeletonOptions

```python
dll.EU_SetSkeletonOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetSkeletonOptions.restype = None
```
## EU_GetSkeletonLoading

```python
dll.EU_GetSkeletonLoading.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSkeletonLoading.restype = ctypes.c_int
```
## EU_GetSkeletonOptions

```python
dll.EU_GetSkeletonOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSkeletonOptions.restype = ctypes.c_int
```
## EU_SetDescriptionsItems

```python
dll.EU_SetDescriptionsItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDescriptionsItems.restype = None
```
## EU_SetDescriptionsColumns

```python
dll.EU_SetDescriptionsColumns.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsColumns.restype = None
```
## EU_SetDescriptionsBordered

```python
dll.EU_SetDescriptionsBordered.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsBordered.restype = None
```
## EU_SetDescriptionsLayout

```python
dll.EU_SetDescriptionsLayout.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsLayout.restype = None
```
## EU_SetDescriptionsItemsEx

```python
dll.EU_SetDescriptionsItemsEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDescriptionsItemsEx.restype = None
```
## EU_SetDescriptionsOptions

```python
dll.EU_SetDescriptionsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsOptions.restype = None
```
## EU_GetDescriptionsItemCount

```python
dll.EU_GetDescriptionsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDescriptionsItemCount.restype = ctypes.c_int
```
## EU_SetDescriptionsAdvancedOptions

```python
dll.EU_SetDescriptionsAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsAdvancedOptions.restype = None
```
## EU_SetDescriptionsColors

```python
dll.EU_SetDescriptionsColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetDescriptionsColors.restype = None
```
## EU_SetDescriptionsExtra

```python
dll.EU_SetDescriptionsExtra.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDescriptionsExtra.restype = None
```
## EU_GetDescriptionsOptions

```python
dll.EU_GetDescriptionsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDescriptionsOptions.restype = ctypes.c_int
```
## EU_GetDescriptionsFullState

```python
dll.EU_GetDescriptionsFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDescriptionsFullState.restype = ctypes.c_int
```
## EU_SetTableData

```python
dll.EU_SetTableData.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableData.restype = None
```
## EU_SetTableStriped

```python
dll.EU_SetTableStriped.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableStriped.restype = None
```
## EU_SetTableBordered

```python
dll.EU_SetTableBordered.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableBordered.restype = None
```
## EU_SetTableEmptyText

```python
dll.EU_SetTableEmptyText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableEmptyText.restype = None
```
## EU_SetTableSelectedRow

```python
dll.EU_SetTableSelectedRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSelectedRow.restype = None
```
## EU_GetTableSelectedRow

```python
dll.EU_GetTableSelectedRow.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTableSelectedRow.restype = ctypes.c_int
```
## EU_GetTableRowCount

```python
dll.EU_GetTableRowCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTableRowCount.restype = ctypes.c_int
```
## EU_GetTableColumnCount

```python
dll.EU_GetTableColumnCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTableColumnCount.restype = ctypes.c_int
```
## EU_SetTableOptions

```python
dll.EU_SetTableOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableOptions.restype = None
```
## EU_SetTableSort

```python
dll.EU_SetTableSort.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSort.restype = None
```
## EU_SetTableScrollRow

```python
dll.EU_SetTableScrollRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableScrollRow.restype = None
```
## EU_SetTableColumnWidth

```python
dll.EU_SetTableColumnWidth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableColumnWidth.restype = None
```
## EU_GetTableOptions

```python
dll.EU_GetTableOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTableOptions.restype = ctypes.c_int
```
## EU_SetTableColumnsEx

```python
dll.EU_SetTableColumnsEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableColumnsEx.restype = None
```
## EU_SetTableRowsEx

```python
dll.EU_SetTableRowsEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableRowsEx.restype = None
```
## EU_AddTableRow

```python
dll.EU_AddTableRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AddTableRow.restype = ctypes.c_int
```
## EU_InsertTableRow

```python
dll.EU_InsertTableRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_InsertTableRow.restype = ctypes.c_int
```
## EU_DeleteTableRow

```python
dll.EU_DeleteTableRow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_DeleteTableRow.restype = ctypes.c_int
```
## EU_ClearTableRows

```python
dll.EU_ClearTableRows.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearTableRows.restype = ctypes.c_int
```
## EU_SetTableCellEx

```python
dll.EU_SetTableCellEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableCellEx.restype = None
```
## EU_SetTableRowStyle

```python
dll.EU_SetTableRowStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableRowStyle.restype = None
```
## EU_SetTableCellStyle

```python
dll.EU_SetTableCellStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableCellStyle.restype = None
```
## EU_SetTableSelectionMode

```python
dll.EU_SetTableSelectionMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSelectionMode.restype = None
```
## EU_SetTableSelectedRows

```python
dll.EU_SetTableSelectedRows.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableSelectedRows.restype = None
```
## EU_SetTableFilter

```python
dll.EU_SetTableFilter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableFilter.restype = None
```
## EU_ClearTableFilter

```python
dll.EU_ClearTableFilter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ClearTableFilter.restype = None
```
## EU_SetTableSearch

```python
dll.EU_SetTableSearch.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableSearch.restype = None
```
## EU_SetTableSpan

```python
dll.EU_SetTableSpan.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableSpan.restype = None
```
## EU_ClearTableSpans

```python
dll.EU_ClearTableSpans.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearTableSpans.restype = None
```
## EU_SetTableSummary

```python
dll.EU_SetTableSummary.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTableSummary.restype = None
```
## EU_SetTableRowExpanded

```python
dll.EU_SetTableRowExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableRowExpanded.restype = None
```
## EU_SetTableTreeOptions

```python
dll.EU_SetTableTreeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableTreeOptions.restype = None
```
## EU_SetTableViewportOptions

```python
dll.EU_SetTableViewportOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableViewportOptions.restype = None
```
## EU_SetTableScroll

```python
dll.EU_SetTableScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableScroll.restype = None
```
## EU_SetTableHeaderDragOptions

```python
dll.EU_SetTableHeaderDragOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableHeaderDragOptions.restype = None
```
## EU_ExportTableExcel

```python
dll.EU_ExportTableExcel.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_ExportTableExcel.restype = ctypes.c_int
```
## EU_ImportTableExcel

```python
dll.EU_ImportTableExcel.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_ImportTableExcel.restype = ctypes.c_int
```
## EU_SetTableCellClickCallback

```python
dll.EU_SetTableCellClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, TableCellCallback]
dll.EU_SetTableCellClickCallback.restype = None
```
## EU_SetTableCellActionCallback

```python
dll.EU_SetTableCellActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, TableCellCallback]
dll.EU_SetTableCellActionCallback.restype = None
```
## EU_SetTableVirtualOptions

```python
dll.EU_SetTableVirtualOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTableVirtualOptions.restype = None
```
## EU_SetTableVirtualRowProvider

```python
dll.EU_SetTableVirtualRowProvider.argtypes = [wintypes.HWND, ctypes.c_int, TableVirtualRowCallback]
dll.EU_SetTableVirtualRowProvider.restype = None
```
## EU_ClearTableVirtualCache

```python
dll.EU_ClearTableVirtualCache.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearTableVirtualCache.restype = None
```
## EU_GetTableCellValue

```python
dll.EU_GetTableCellValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTableCellValue.restype = ctypes.c_int
```
## EU_GetTableFullState

```python
dll.EU_GetTableFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTableFullState.restype = ctypes.c_int
```
## EU_SetCardTitle

```python
dll.EU_SetCardTitle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardTitle.restype = None
```
## EU_SetCardBody

```python
dll.EU_SetCardBody.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardBody.restype = None
```
## EU_SetCardFooter

```python
dll.EU_SetCardFooter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardFooter.restype = None
```
## EU_SetCardItems

```python
dll.EU_SetCardItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardItems.restype = None
```
## EU_SetCardActions

```python
dll.EU_SetCardActions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCardActions.restype = None
```
## EU_GetCardItemCount

```python
dll.EU_GetCardItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCardItemCount.restype = ctypes.c_int
```
## EU_GetCardAction

```python
dll.EU_GetCardAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCardAction.restype = ctypes.c_int
```
## EU_ResetCardAction

```python
dll.EU_ResetCardAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ResetCardAction.restype = None
```
## EU_SetCardShadow

```python
dll.EU_SetCardShadow.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCardShadow.restype = None
```
## EU_SetCardOptions

```python
dll.EU_SetCardOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCardOptions.restype = None
```
## EU_SetCardStyle

```python
dll.EU_SetCardStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_int]
dll.EU_SetCardStyle.restype = None
```
## EU_GetCardStyle

```python
dll.EU_GetCardStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCardStyle.restype = ctypes.c_int
```
## EU_SetCardBodyStyle

```python
dll.EU_SetCardBodyStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCardBodyStyle.restype = None
```
## EU_GetCardBodyStyle

```python
dll.EU_GetCardBodyStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCardBodyStyle.restype = ctypes.c_int
```
## EU_GetCardOptions

```python
dll.EU_GetCardOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCardOptions.restype = ctypes.c_int
```
## EU_SetCollapseItems

```python
dll.EU_SetCollapseItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseItems.restype = None
```
## EU_SetCollapseItemsEx

```python
dll.EU_SetCollapseItemsEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseItemsEx.restype = None
```
## EU_SetCollapseActive

```python
dll.EU_SetCollapseActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCollapseActive.restype = None
```
## EU_GetCollapseActive

```python
dll.EU_GetCollapseActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCollapseActive.restype = ctypes.c_int
```
## EU_SetCollapseActiveItems

```python
dll.EU_SetCollapseActiveItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseActiveItems.restype = None
```
## EU_GetCollapseActiveItems

```python
dll.EU_GetCollapseActiveItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCollapseActiveItems.restype = ctypes.c_int
```
## EU_GetCollapseItemCount

```python
dll.EU_GetCollapseItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCollapseItemCount.restype = ctypes.c_int
```
## EU_SetCollapseOptions

```python
dll.EU_SetCollapseOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseOptions.restype = None
```
## EU_SetCollapseAdvancedOptions

```python
dll.EU_SetCollapseAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCollapseAdvancedOptions.restype = None
```
## EU_GetCollapseOptions

```python
dll.EU_GetCollapseOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCollapseOptions.restype = ctypes.c_int
```
## EU_GetCollapseStateJson

```python
dll.EU_GetCollapseStateJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCollapseStateJson.restype = ctypes.c_int
```
## EU_SetTimelineItems

```python
dll.EU_SetTimelineItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimelineItems.restype = None
```
## EU_SetTimelineOptions

```python
dll.EU_SetTimelineOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimelineOptions.restype = None
```
## EU_GetTimelineItemCount

```python
dll.EU_GetTimelineItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimelineItemCount.restype = ctypes.c_int
```
## EU_GetTimelineOptions

```python
dll.EU_GetTimelineOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimelineOptions.restype = ctypes.c_int
```
## EU_SetTimelineAdvancedOptions

```python
dll.EU_SetTimelineAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimelineAdvancedOptions.restype = None
```
## EU_GetTimelineAdvancedOptions

```python
dll.EU_GetTimelineAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimelineAdvancedOptions.restype = ctypes.c_int
```
## EU_SetStatisticValue

```python
dll.EU_SetStatisticValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticValue.restype = None
```
## EU_SetStatisticFormat

```python
dll.EU_SetStatisticFormat.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticFormat.restype = None
```
## EU_SetStatisticOptions

```python
dll.EU_SetStatisticOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetStatisticOptions.restype = None
```
## EU_GetStatisticOptions

```python
dll.EU_GetStatisticOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStatisticOptions.restype = ctypes.c_int
```
## EU_SetStatisticNumberOptions

```python
dll.EU_SetStatisticNumberOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticNumberOptions.restype = None
```
## EU_SetStatisticAffixOptions

```python
dll.EU_SetStatisticAffixOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int]
dll.EU_SetStatisticAffixOptions.restype = None
```
## EU_SetStatisticDisplayText

```python
dll.EU_SetStatisticDisplayText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticDisplayText.restype = None
```
## EU_SetStatisticCountdown

```python
dll.EU_SetStatisticCountdown.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStatisticCountdown.restype = None
```
## EU_SetStatisticCountdownState

```python
dll.EU_SetStatisticCountdownState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetStatisticCountdownState.restype = None
```
## EU_AddStatisticCountdownTime

```python
dll.EU_AddStatisticCountdownTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong]
dll.EU_AddStatisticCountdownTime.restype = None
```
## EU_SetStatisticFinishCallback

```python
dll.EU_SetStatisticFinishCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementClickCallback]
dll.EU_SetStatisticFinishCallback.restype = None
```
## EU_SetStatisticSuffixClickCallback

```python
dll.EU_SetStatisticSuffixClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementClickCallback]
dll.EU_SetStatisticSuffixClickCallback.restype = None
```
## EU_GetStatisticFullState

```python
dll.EU_GetStatisticFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_longlong)]
dll.EU_GetStatisticFullState.restype = ctypes.c_int
```
## EU_SetKpiCardData

```python
dll.EU_SetKpiCardData.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetKpiCardData.restype = None
```
## EU_SetKpiCardOptions

```python
dll.EU_SetKpiCardOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetKpiCardOptions.restype = None
```
## EU_GetKpiCardOptions

```python
dll.EU_GetKpiCardOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetKpiCardOptions.restype = ctypes.c_int
```
## EU_SetTrendData

```python
dll.EU_SetTrendData.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetTrendData.restype = None
```
## EU_SetTrendOptions

```python
dll.EU_SetTrendOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTrendOptions.restype = None
```
## EU_GetTrendDirection

```python
dll.EU_GetTrendDirection.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTrendDirection.restype = ctypes.c_int
```
## EU_GetTrendOptions

```python
dll.EU_GetTrendOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTrendOptions.restype = ctypes.c_int
```
## EU_SetStatusDot

```python
dll.EU_SetStatusDot.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetStatusDot.restype = None
```
## EU_SetStatusDotOptions

```python
dll.EU_SetStatusDotOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetStatusDotOptions.restype = None
```
## EU_GetStatusDotStatus

```python
dll.EU_GetStatusDotStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetStatusDotStatus.restype = ctypes.c_int
```
## EU_GetStatusDotOptions

```python
dll.EU_GetStatusDotOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStatusDotOptions.restype = ctypes.c_int
```
## EU_SetGaugeValue

```python
dll.EU_SetGaugeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetGaugeValue.restype = None
```
## EU_SetGaugeOptions

```python
dll.EU_SetGaugeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetGaugeOptions.restype = None
```
## EU_GetGaugeValue

```python
dll.EU_GetGaugeValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetGaugeValue.restype = ctypes.c_int
```
## EU_GetGaugeStatus

```python
dll.EU_GetGaugeStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetGaugeStatus.restype = ctypes.c_int
```
## EU_GetGaugeOptions

```python
dll.EU_GetGaugeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetGaugeOptions.restype = ctypes.c_int
```
## EU_SetRingProgressValue

```python
dll.EU_SetRingProgressValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetRingProgressValue.restype = None
```
## EU_SetRingProgressOptions

```python
dll.EU_SetRingProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetRingProgressOptions.restype = None
```
## EU_GetRingProgressValue

```python
dll.EU_GetRingProgressValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRingProgressValue.restype = ctypes.c_int
```
## EU_GetRingProgressStatus

```python
dll.EU_GetRingProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetRingProgressStatus.restype = ctypes.c_int
```
## EU_GetRingProgressOptions

```python
dll.EU_GetRingProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetRingProgressOptions.restype = ctypes.c_int
```
## EU_SetBulletProgressValue

```python
dll.EU_SetBulletProgressValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetBulletProgressValue.restype = None
```
## EU_SetBulletProgressOptions

```python
dll.EU_SetBulletProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBulletProgressOptions.restype = None
```
## EU_GetBulletProgressValue

```python
dll.EU_GetBulletProgressValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBulletProgressValue.restype = ctypes.c_int
```
## EU_GetBulletProgressTarget

```python
dll.EU_GetBulletProgressTarget.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBulletProgressTarget.restype = ctypes.c_int
```
## EU_GetBulletProgressStatus

```python
dll.EU_GetBulletProgressStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBulletProgressStatus.restype = ctypes.c_int
```
## EU_GetBulletProgressOptions

```python
dll.EU_GetBulletProgressOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBulletProgressOptions.restype = ctypes.c_int
```
## EU_SetLineChartData

```python
dll.EU_SetLineChartData.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetLineChartData.restype = None
```
## EU_SetLineChartSeries

```python
dll.EU_SetLineChartSeries.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetLineChartSeries.restype = None
```
## EU_SetLineChartOptions

```python
dll.EU_SetLineChartOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLineChartOptions.restype = None
```
## EU_SetLineChartSelected

```python
dll.EU_SetLineChartSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetLineChartSelected.restype = None
```
## EU_GetLineChartPointCount

```python
dll.EU_GetLineChartPointCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLineChartPointCount.restype = ctypes.c_int
```
## EU_GetLineChartSeriesCount

```python
dll.EU_GetLineChartSeriesCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLineChartSeriesCount.restype = ctypes.c_int
```
## EU_GetLineChartSelected

```python
dll.EU_GetLineChartSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLineChartSelected.restype = ctypes.c_int
```
## EU_GetLineChartOptions

```python
dll.EU_GetLineChartOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLineChartOptions.restype = ctypes.c_int
```
## EU_SetBarChartData

```python
dll.EU_SetBarChartData.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBarChartData.restype = None
```
## EU_SetBarChartSeries

```python
dll.EU_SetBarChartSeries.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBarChartSeries.restype = None
```
## EU_SetBarChartOptions

```python
dll.EU_SetBarChartOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBarChartOptions.restype = None
```
## EU_SetBarChartSelected

```python
dll.EU_SetBarChartSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBarChartSelected.restype = None
```
## EU_GetBarChartBarCount

```python
dll.EU_GetBarChartBarCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBarChartBarCount.restype = ctypes.c_int
```
## EU_GetBarChartSeriesCount

```python
dll.EU_GetBarChartSeriesCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBarChartSeriesCount.restype = ctypes.c_int
```
## EU_GetBarChartSelected

```python
dll.EU_GetBarChartSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBarChartSelected.restype = ctypes.c_int
```
## EU_GetBarChartOptions

```python
dll.EU_GetBarChartOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBarChartOptions.restype = ctypes.c_int
```
## EU_SetDonutChartData

```python
dll.EU_SetDonutChartData.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetDonutChartData.restype = None
```
## EU_SetDonutChartOptions

```python
dll.EU_SetDonutChartOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDonutChartOptions.restype = None
```
## EU_SetDonutChartAdvancedOptions

```python
dll.EU_SetDonutChartAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDonutChartAdvancedOptions.restype = None
```
## EU_SetDonutChartActive

```python
dll.EU_SetDonutChartActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDonutChartActive.restype = None
```
## EU_GetDonutChartSliceCount

```python
dll.EU_GetDonutChartSliceCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDonutChartSliceCount.restype = ctypes.c_int
```
## EU_GetDonutChartActive

```python
dll.EU_GetDonutChartActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDonutChartActive.restype = ctypes.c_int
```
## EU_GetDonutChartOptions

```python
dll.EU_GetDonutChartOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDonutChartOptions.restype = ctypes.c_int
```
## EU_GetDonutChartAdvancedOptions

```python
dll.EU_GetDonutChartAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDonutChartAdvancedOptions.restype = ctypes.c_int
```
## EU_SetCalendarDate

```python
dll.EU_SetCalendarDate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCalendarDate.restype = None
```
## EU_SetCalendarRange

```python
dll.EU_SetCalendarRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCalendarRange.restype = None
```
## EU_SetCalendarOptions

```python
dll.EU_SetCalendarOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCalendarOptions.restype = None
```
## EU_CalendarMoveMonth

```python
dll.EU_CalendarMoveMonth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_CalendarMoveMonth.restype = None
```
## EU_GetCalendarValue

```python
dll.EU_GetCalendarValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCalendarValue.restype = ctypes.c_int
```
## EU_GetCalendarRange

```python
dll.EU_GetCalendarRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarRange.restype = ctypes.c_int
```
## EU_GetCalendarOptions

```python
dll.EU_GetCalendarOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarOptions.restype = ctypes.c_int
```
## EU_SetCalendarSelectionRange

```python
dll.EU_SetCalendarSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCalendarSelectionRange.restype = None
```
## EU_GetCalendarSelectionRange

```python
dll.EU_GetCalendarSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarSelectionRange.restype = ctypes.c_int
```
## EU_SetCalendarDisplayRange

```python
dll.EU_SetCalendarDisplayRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCalendarDisplayRange.restype = None
```
## EU_GetCalendarDisplayRange

```python
dll.EU_GetCalendarDisplayRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCalendarDisplayRange.restype = ctypes.c_int
```
## EU_SetCalendarCellItems

```python
dll.EU_SetCalendarCellItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCalendarCellItems.restype = None
```
## EU_GetCalendarCellItems

```python
dll.EU_GetCalendarCellItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetCalendarCellItems.restype = ctypes.c_int
```
## EU_ClearCalendarCellItems

```python
dll.EU_ClearCalendarCellItems.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearCalendarCellItems.restype = None
```
## EU_SetCalendarVisualOptions

```python
dll.EU_SetCalendarVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_float]
dll.EU_SetCalendarVisualOptions.restype = None
```
## EU_GetCalendarVisualOptions

```python
dll.EU_GetCalendarVisualOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_float)]
dll.EU_GetCalendarVisualOptions.restype = ctypes.c_int
```
## EU_SetCalendarStateColors

```python
dll.EU_SetCalendarStateColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetCalendarStateColors.restype = None
```
## EU_GetCalendarStateColors

```python
dll.EU_GetCalendarStateColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetCalendarStateColors.restype = ctypes.c_int
```
## EU_SetCalendarSelectedMarker

```python
dll.EU_SetCalendarSelectedMarker.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCalendarSelectedMarker.restype = None
```
## EU_SetCalendarChangeCallback

```python
dll.EU_SetCalendarChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetCalendarChangeCallback.restype = None
```
## EU_SetTreeItems

```python
dll.EU_SetTreeItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeItems.restype = None
```
## EU_SetTreeSelected

```python
dll.EU_SetTreeSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeSelected.restype = None
```
## EU_GetTreeSelected

```python
dll.EU_GetTreeSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelected.restype = ctypes.c_int
```
## EU_SetTreeOptions

```python
dll.EU_SetTreeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeOptions.restype = None
```
## EU_GetTreeOptions

```python
dll.EU_GetTreeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTreeOptions.restype = ctypes.c_int
```
## EU_SetTreeItemExpanded

```python
dll.EU_SetTreeItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeItemExpanded.restype = None
```
## EU_ToggleTreeItemExpanded

```python
dll.EU_ToggleTreeItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ToggleTreeItemExpanded.restype = None
```
## EU_GetTreeItemExpanded

```python
dll.EU_GetTreeItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemExpanded.restype = ctypes.c_int
```
## EU_SetTreeItemChecked

```python
dll.EU_SetTreeItemChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeItemChecked.restype = None
```
## EU_GetTreeItemChecked

```python
dll.EU_GetTreeItemChecked.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemChecked.restype = ctypes.c_int
```
## EU_SetTreeItemLazy

```python
dll.EU_SetTreeItemLazy.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeItemLazy.restype = None
```
## EU_GetTreeItemLazy

```python
dll.EU_GetTreeItemLazy.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeItemLazy.restype = ctypes.c_int
```
## EU_GetTreeVisibleCount

```python
dll.EU_GetTreeVisibleCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeVisibleCount.restype = ctypes.c_int
```
## EU_SetTreeSelectItems

```python
dll.EU_SetTreeSelectItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectItems.restype = None
```
## EU_SetTreeSelectSelected

```python
dll.EU_SetTreeSelectSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeSelectSelected.restype = None
```
## EU_GetTreeSelectSelected

```python
dll.EU_GetTreeSelectSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelectSelected.restype = ctypes.c_int
```
## EU_SetTreeSelectOpen

```python
dll.EU_SetTreeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeSelectOpen.restype = None
```
## EU_GetTreeSelectOpen

```python
dll.EU_GetTreeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelectOpen.restype = ctypes.c_int
```
## EU_SetTreeSelectOptions

```python
dll.EU_SetTreeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeSelectOptions.restype = None
```
## EU_GetTreeSelectOptions

```python
dll.EU_GetTreeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTreeSelectOptions.restype = ctypes.c_int
```
## EU_SetTreeSelectSearch

```python
dll.EU_SetTreeSelectSearch.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectSearch.restype = None
```
## EU_GetTreeSelectSearch

```python
dll.EU_GetTreeSelectSearch.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectSearch.restype = ctypes.c_int
```
## EU_ClearTreeSelect

```python
dll.EU_ClearTreeSelect.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearTreeSelect.restype = None
```
## EU_SetTreeSelectSelectedItems

```python
dll.EU_SetTreeSelectSelectedItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectSelectedItems.restype = None
```
## EU_GetTreeSelectSelectedCount

```python
dll.EU_GetTreeSelectSelectedCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTreeSelectSelectedCount.restype = ctypes.c_int
```
## EU_GetTreeSelectSelectedItem

```python
dll.EU_GetTreeSelectSelectedItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectSelectedItem.restype = ctypes.c_int
```
## EU_SetTreeSelectItemExpanded

```python
dll.EU_SetTreeSelectItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTreeSelectItemExpanded.restype = None
```
## EU_ToggleTreeSelectItemExpanded

```python
dll.EU_ToggleTreeSelectItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ToggleTreeSelectItemExpanded.restype = None
```
## EU_GetTreeSelectItemExpanded

```python
dll.EU_GetTreeSelectItemExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTreeSelectItemExpanded.restype = ctypes.c_int
```
## EU_SetTreeDataJson

```python
dll.EU_SetTreeDataJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeDataJson.restype = None
```
## EU_GetTreeDataJson

```python
dll.EU_GetTreeDataJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeDataJson.restype = ctypes.c_int
```
## EU_SetTreeOptionsJson

```python
dll.EU_SetTreeOptionsJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeOptionsJson.restype = None
```
## EU_GetTreeStateJson

```python
dll.EU_GetTreeStateJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeStateJson.restype = ctypes.c_int
```
## EU_SetTreeCheckedKeysJson

```python
dll.EU_SetTreeCheckedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeCheckedKeysJson.restype = None
```
## EU_GetTreeCheckedKeysJson

```python
dll.EU_GetTreeCheckedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeCheckedKeysJson.restype = ctypes.c_int
```
## EU_SetTreeExpandedKeysJson

```python
dll.EU_SetTreeExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeExpandedKeysJson.restype = None
```
## EU_GetTreeExpandedKeysJson

```python
dll.EU_GetTreeExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeExpandedKeysJson.restype = ctypes.c_int
```
## EU_AppendTreeNodeJson

```python
dll.EU_AppendTreeNodeJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AppendTreeNodeJson.restype = None
```
## EU_UpdateTreeNodeJson

```python
dll.EU_UpdateTreeNodeJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_UpdateTreeNodeJson.restype = None
```
## EU_RemoveTreeNodeByKey

```python
dll.EU_RemoveTreeNodeByKey.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_RemoveTreeNodeByKey.restype = None
```
## EU_SetTreeNodeEventCallback

```python
dll.EU_SetTreeNodeEventCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeNodeEventCallback.restype = None
```
## EU_SetTreeLazyLoadCallback

```python
dll.EU_SetTreeLazyLoadCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeLazyLoadCallback.restype = None
```
## EU_SetTreeDragCallback

```python
dll.EU_SetTreeDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeDragCallback.restype = None
```
## EU_SetTreeAllowDragCallback

```python
dll.EU_SetTreeAllowDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDragCallback]
dll.EU_SetTreeAllowDragCallback.restype = None
```
## EU_SetTreeAllowDropCallback

```python
dll.EU_SetTreeAllowDropCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDropCallback]
dll.EU_SetTreeAllowDropCallback.restype = None
```
## EU_SetTreeSelectDataJson

```python
dll.EU_SetTreeSelectDataJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectDataJson.restype = None
```
## EU_GetTreeSelectDataJson

```python
dll.EU_GetTreeSelectDataJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectDataJson.restype = ctypes.c_int
```
## EU_SetTreeSelectOptionsJson

```python
dll.EU_SetTreeSelectOptionsJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectOptionsJson.restype = None
```
## EU_GetTreeSelectStateJson

```python
dll.EU_GetTreeSelectStateJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectStateJson.restype = ctypes.c_int
```
## EU_SetTreeSelectSelectedKeysJson

```python
dll.EU_SetTreeSelectSelectedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectSelectedKeysJson.restype = None
```
## EU_GetTreeSelectSelectedKeysJson

```python
dll.EU_GetTreeSelectSelectedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectSelectedKeysJson.restype = ctypes.c_int
```
## EU_SetTreeSelectExpandedKeysJson

```python
dll.EU_SetTreeSelectExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTreeSelectExpandedKeysJson.restype = None
```
## EU_GetTreeSelectExpandedKeysJson

```python
dll.EU_GetTreeSelectExpandedKeysJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTreeSelectExpandedKeysJson.restype = ctypes.c_int
```
## EU_AppendTreeSelectNodeJson

```python
dll.EU_AppendTreeSelectNodeJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AppendTreeSelectNodeJson.restype = None
```
## EU_UpdateTreeSelectNodeJson

```python
dll.EU_UpdateTreeSelectNodeJson.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_UpdateTreeSelectNodeJson.restype = None
```
## EU_RemoveTreeSelectNodeByKey

```python
dll.EU_RemoveTreeSelectNodeByKey.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_RemoveTreeSelectNodeByKey.restype = None
```
## EU_SetTreeSelectNodeEventCallback

```python
dll.EU_SetTreeSelectNodeEventCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeSelectNodeEventCallback.restype = None
```
## EU_SetTreeSelectLazyLoadCallback

```python
dll.EU_SetTreeSelectLazyLoadCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeSelectLazyLoadCallback.restype = None
```
## EU_SetTreeSelectDragCallback

```python
dll.EU_SetTreeSelectDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeEventCallback]
dll.EU_SetTreeSelectDragCallback.restype = None
```
## EU_SetTreeSelectAllowDragCallback

```python
dll.EU_SetTreeSelectAllowDragCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDragCallback]
dll.EU_SetTreeSelectAllowDragCallback.restype = None
```
## EU_SetTreeSelectAllowDropCallback

```python
dll.EU_SetTreeSelectAllowDropCallback.argtypes = [wintypes.HWND, ctypes.c_int, TreeNodeAllowDropCallback]
dll.EU_SetTreeSelectAllowDropCallback.restype = None
```
## EU_SetTransferItems

```python
dll.EU_SetTransferItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferItems.restype = None
```
## EU_TransferMoveRight

```python
dll.EU_TransferMoveRight.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TransferMoveRight.restype = None
```
## EU_TransferMoveLeft

```python
dll.EU_TransferMoveLeft.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TransferMoveLeft.restype = None
```
## EU_TransferMoveAllRight

```python
dll.EU_TransferMoveAllRight.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TransferMoveAllRight.restype = None
```
## EU_TransferMoveAllLeft

```python
dll.EU_TransferMoveAllLeft.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TransferMoveAllLeft.restype = None
```
## EU_SetTransferSelected

```python
dll.EU_SetTransferSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTransferSelected.restype = None
```
## EU_GetTransferSelected

```python
dll.EU_GetTransferSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferSelected.restype = ctypes.c_int
```
## EU_GetTransferCount

```python
dll.EU_GetTransferCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferCount.restype = ctypes.c_int
```
## EU_SetTransferFilters

```python
dll.EU_SetTransferFilters.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferFilters.restype = None
```
## EU_GetTransferMatchedCount

```python
dll.EU_GetTransferMatchedCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferMatchedCount.restype = ctypes.c_int
```
## EU_SetTransferItemDisabled

```python
dll.EU_SetTransferItemDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTransferItemDisabled.restype = None
```
## EU_GetTransferItemDisabled

```python
dll.EU_GetTransferItemDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferItemDisabled.restype = ctypes.c_int
```
## EU_GetTransferDisabledCount

```python
dll.EU_GetTransferDisabledCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferDisabledCount.restype = ctypes.c_int
```
## EU_SetTransferDataEx

```python
dll.EU_SetTransferDataEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferDataEx.restype = None
```
## EU_SetTransferOptions

```python
dll.EU_SetTransferOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTransferOptions.restype = None
```
## EU_GetTransferOptions

```python
dll.EU_GetTransferOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTransferOptions.restype = ctypes.c_int
```
## EU_SetTransferTitles

```python
dll.EU_SetTransferTitles.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferTitles.restype = None
```
## EU_SetTransferButtonTexts

```python
dll.EU_SetTransferButtonTexts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferButtonTexts.restype = None
```
## EU_SetTransferFormat

```python
dll.EU_SetTransferFormat.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferFormat.restype = None
```
## EU_SetTransferItemTemplate

```python
dll.EU_SetTransferItemTemplate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferItemTemplate.restype = None
```
## EU_SetTransferFooterTexts

```python
dll.EU_SetTransferFooterTexts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferFooterTexts.restype = None
```
## EU_SetTransferFilterPlaceholder

```python
dll.EU_SetTransferFilterPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferFilterPlaceholder.restype = None
```
## EU_SetTransferCheckedKeys

```python
dll.EU_SetTransferCheckedKeys.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTransferCheckedKeys.restype = None
```
## EU_GetTransferCheckedCount

```python
dll.EU_GetTransferCheckedCount.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetTransferCheckedCount.restype = ctypes.c_int
```
## EU_GetTransferValueKeys

```python
dll.EU_GetTransferValueKeys.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTransferValueKeys.restype = ctypes.c_int
```
## EU_GetTransferText

```python
dll.EU_GetTransferText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTransferText.restype = ctypes.c_int
```
## EU_SetAutocompleteSuggestions

```python
dll.EU_SetAutocompleteSuggestions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompleteSuggestions.restype = None
```
## EU_SetAutocompleteValue

```python
dll.EU_SetAutocompleteValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompleteValue.restype = None
```
## EU_SetAutocompletePlaceholder

```python
dll.EU_SetAutocompletePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompletePlaceholder.restype = None
```
## EU_GetAutocompletePlaceholder

```python
dll.EU_GetAutocompletePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompletePlaceholder.restype = ctypes.c_int
```
## EU_SetAutocompleteIcons

```python
dll.EU_SetAutocompleteIcons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompleteIcons.restype = None
```
## EU_GetAutocompleteIcons

```python
dll.EU_GetAutocompleteIcons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteIcons.restype = ctypes.c_int
```
## EU_SetAutocompleteBehaviorOptions

```python
dll.EU_SetAutocompleteBehaviorOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAutocompleteBehaviorOptions.restype = None
```
## EU_GetAutocompleteBehaviorOptions

```python
dll.EU_GetAutocompleteBehaviorOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAutocompleteBehaviorOptions.restype = ctypes.c_int
```
## EU_SetAutocompleteOpen

```python
dll.EU_SetAutocompleteOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAutocompleteOpen.restype = None
```
## EU_SetAutocompleteSelected

```python
dll.EU_SetAutocompleteSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAutocompleteSelected.restype = None
```
## EU_SetAutocompleteAsyncState

```python
dll.EU_SetAutocompleteAsyncState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetAutocompleteAsyncState.restype = None
```
## EU_SetAutocompleteEmptyText

```python
dll.EU_SetAutocompleteEmptyText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAutocompleteEmptyText.restype = None
```
## EU_GetAutocompleteValue

```python
dll.EU_GetAutocompleteValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAutocompleteValue.restype = ctypes.c_int
```
## EU_GetAutocompleteOpen

```python
dll.EU_GetAutocompleteOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAutocompleteOpen.restype = ctypes.c_int
```
## EU_GetAutocompleteSelected

```python
dll.EU_GetAutocompleteSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAutocompleteSelected.restype = ctypes.c_int
```
## EU_GetAutocompleteSuggestionCount

```python
dll.EU_GetAutocompleteSuggestionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAutocompleteSuggestionCount.restype = ctypes.c_int
```
## EU_GetAutocompleteOptions

```python
dll.EU_GetAutocompleteOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAutocompleteOptions.restype = ctypes.c_int
```
## EU_SetMentionsValue

```python
dll.EU_SetMentionsValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMentionsValue.restype = None
```
## EU_SetMentionsSuggestions

```python
dll.EU_SetMentionsSuggestions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMentionsSuggestions.restype = None
```
## EU_SetMentionsOpen

```python
dll.EU_SetMentionsOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMentionsOpen.restype = None
```
## EU_SetMentionsSelected

```python
dll.EU_SetMentionsSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMentionsSelected.restype = None
```
## EU_SetMentionsOptions

```python
dll.EU_SetMentionsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetMentionsOptions.restype = None
```
## EU_SetMentionsFilter

```python
dll.EU_SetMentionsFilter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMentionsFilter.restype = None
```
## EU_InsertMentionsSelected

```python
dll.EU_InsertMentionsSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_InsertMentionsSelected.restype = None
```
## EU_GetMentionsValue

```python
dll.EU_GetMentionsValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMentionsValue.restype = ctypes.c_int
```
## EU_GetMentionsOpen

```python
dll.EU_GetMentionsOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMentionsOpen.restype = ctypes.c_int
```
## EU_GetMentionsSelected

```python
dll.EU_GetMentionsSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMentionsSelected.restype = ctypes.c_int
```
## EU_GetMentionsSuggestionCount

```python
dll.EU_GetMentionsSuggestionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMentionsSuggestionCount.restype = ctypes.c_int
```
## EU_GetMentionsOptions

```python
dll.EU_GetMentionsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMentionsOptions.restype = ctypes.c_int
```
## EU_SetCascaderOptions

```python
dll.EU_SetCascaderOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCascaderOptions.restype = None
```
## EU_SetCascaderValue

```python
dll.EU_SetCascaderValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCascaderValue.restype = None
```
## EU_SetCascaderOpen

```python
dll.EU_SetCascaderOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCascaderOpen.restype = None
```
## EU_SetCascaderAdvancedOptions

```python
dll.EU_SetCascaderAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCascaderAdvancedOptions.restype = None
```
## EU_SetCascaderSearch

```python
dll.EU_SetCascaderSearch.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCascaderSearch.restype = None
```
## EU_GetCascaderOpen

```python
dll.EU_GetCascaderOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderOpen.restype = ctypes.c_int
```
## EU_GetCascaderOptionCount

```python
dll.EU_GetCascaderOptionCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderOptionCount.restype = ctypes.c_int
```
## EU_GetCascaderSelectedDepth

```python
dll.EU_GetCascaderSelectedDepth.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderSelectedDepth.restype = ctypes.c_int
```
## EU_GetCascaderLevelCount

```python
dll.EU_GetCascaderLevelCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCascaderLevelCount.restype = ctypes.c_int
```
## EU_GetCascaderAdvancedOptions

```python
dll.EU_GetCascaderAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCascaderAdvancedOptions.restype = ctypes.c_int
```
## EU_SetDatePickerDate

```python
dll.EU_SetDatePickerDate.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerDate.restype = None
```
## EU_SetDatePickerRange

```python
dll.EU_SetDatePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerRange.restype = None
```
## EU_SetDatePickerOptions

```python
dll.EU_SetDatePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerOptions.restype = None
```
## EU_SetDatePickerOpen

```python
dll.EU_SetDatePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerOpen.restype = None
```
## EU_ClearDatePicker

```python
dll.EU_ClearDatePicker.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearDatePicker.restype = None
```
## EU_DatePickerSelectToday

```python
dll.EU_DatePickerSelectToday.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_DatePickerSelectToday.restype = None
```
## EU_GetDatePickerOpen

```python
dll.EU_GetDatePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDatePickerOpen.restype = ctypes.c_int
```
## EU_GetDatePickerValue

```python
dll.EU_GetDatePickerValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDatePickerValue.restype = ctypes.c_int
```
## EU_DatePickerMoveMonth

```python
dll.EU_DatePickerMoveMonth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_DatePickerMoveMonth.restype = None
```
## EU_GetDatePickerRange

```python
dll.EU_GetDatePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDatePickerRange.restype = ctypes.c_int
```
## EU_GetDatePickerOptions

```python
dll.EU_GetDatePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDatePickerOptions.restype = ctypes.c_int
```
## EU_SetDatePickerSelectionRange

```python
dll.EU_SetDatePickerSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerSelectionRange.restype = None
```
## EU_GetDatePickerSelectionRange

```python
dll.EU_GetDatePickerSelectionRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDatePickerSelectionRange.restype = ctypes.c_int
```
## EU_SetDatePickerPlaceholder

```python
dll.EU_SetDatePickerPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerPlaceholder.restype = None
```
## EU_SetDatePickerRangeSeparator

```python
dll.EU_SetDatePickerRangeSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerRangeSeparator.restype = None
```
## EU_SetDatePickerStartPlaceholder

```python
dll.EU_SetDatePickerStartPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerStartPlaceholder.restype = None
```
## EU_SetDatePickerEndPlaceholder

```python
dll.EU_SetDatePickerEndPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerEndPlaceholder.restype = None
```
## EU_SetDatePickerFormat

```python
dll.EU_SetDatePickerFormat.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerFormat.restype = None
```
## EU_SetDatePickerAlign

```python
dll.EU_SetDatePickerAlign.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerAlign.restype = None
```
## EU_SetDatePickerMode

```python
dll.EU_SetDatePickerMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerMode.restype = None
```
## EU_GetDatePickerMode

```python
dll.EU_GetDatePickerMode.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDatePickerMode.restype = ctypes.c_int
```
## EU_SetDatePickerMultiSelect

```python
dll.EU_SetDatePickerMultiSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDatePickerMultiSelect.restype = None
```
## EU_GetDatePickerSelectedDates

```python
dll.EU_GetDatePickerSelectedDates.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDatePickerSelectedDates.restype = ctypes.c_int
```
## EU_SetDatePickerShortcuts

```python
dll.EU_SetDatePickerShortcuts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDatePickerShortcuts.restype = None
```
## EU_SetDatePickerDisabledDateCallback

```python
dll.EU_SetDatePickerDisabledDateCallback.argtypes = [wintypes.HWND, ctypes.c_int, DateDisabledCallback]
dll.EU_SetDatePickerDisabledDateCallback.restype = None
```
## EU_CreateDateRangePicker

```python
dll.EU_CreateDateRangePicker.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_CreateDateRangePicker.restype = ctypes.c_int
```
## EU_SetDateRangePickerValue

```python
dll.EU_SetDateRangePickerValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerValue.restype = None
```
## EU_GetDateRangePickerValue

```python
dll.EU_GetDateRangePickerValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateRangePickerValue.restype = ctypes.c_int
```
## EU_SetDateRangePickerRange

```python
dll.EU_SetDateRangePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerRange.restype = None
```
## EU_SetDateRangePickerPlaceholders

```python
dll.EU_SetDateRangePickerPlaceholders.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateRangePickerPlaceholders.restype = None
```
## EU_SetDateRangePickerSeparator

```python
dll.EU_SetDateRangePickerSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateRangePickerSeparator.restype = None
```
## EU_SetDateRangePickerFormat

```python
dll.EU_SetDateRangePickerFormat.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerFormat.restype = None
```
## EU_SetDateRangePickerAlign

```python
dll.EU_SetDateRangePickerAlign.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerAlign.restype = None
```
## EU_SetDateRangePickerShortcuts

```python
dll.EU_SetDateRangePickerShortcuts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateRangePickerShortcuts.restype = None
```
## EU_SetDateRangePickerDisabledDateCallback

```python
dll.EU_SetDateRangePickerDisabledDateCallback.argtypes = [wintypes.HWND, ctypes.c_int, DateDisabledCallback]
dll.EU_SetDateRangePickerDisabledDateCallback.restype = None
```
## EU_SetDateRangePickerOpen

```python
dll.EU_SetDateRangePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateRangePickerOpen.restype = None
```
## EU_GetDateRangePickerOpen

```python
dll.EU_GetDateRangePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateRangePickerOpen.restype = ctypes.c_int
```
## EU_DateRangePickerClear

```python
dll.EU_DateRangePickerClear.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_DateRangePickerClear.restype = None
```
## EU_SetTimePickerTime

```python
dll.EU_SetTimePickerTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerTime.restype = None
```
## EU_SetTimePickerRange

```python
dll.EU_SetTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerRange.restype = None
```
## EU_SetTimePickerOptions

```python
dll.EU_SetTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerOptions.restype = None
```
## EU_SetTimePickerOpen

```python
dll.EU_SetTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerOpen.restype = None
```
## EU_SetTimePickerScroll

```python
dll.EU_SetTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerScroll.restype = None
```
## EU_GetTimePickerOpen

```python
dll.EU_GetTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimePickerOpen.restype = ctypes.c_int
```
## EU_GetTimePickerValue

```python
dll.EU_GetTimePickerValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimePickerValue.restype = ctypes.c_int
```
## EU_GetTimePickerRange

```python
dll.EU_GetTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerRange.restype = ctypes.c_int
```
## EU_GetTimePickerOptions

```python
dll.EU_GetTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerOptions.restype = ctypes.c_int
```
## EU_GetTimePickerScroll

```python
dll.EU_GetTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerScroll.restype = ctypes.c_int
```
## EU_SetTimePickerArrowControl

```python
dll.EU_SetTimePickerArrowControl.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerArrowControl.restype = None
```
## EU_GetTimePickerArrowControl

```python
dll.EU_GetTimePickerArrowControl.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimePickerArrowControl.restype = ctypes.c_int
```
## EU_SetTimePickerRangeSelect

```python
dll.EU_SetTimePickerRangeSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimePickerRangeSelect.restype = None
```
## EU_SetTimePickerStartPlaceholder

```python
dll.EU_SetTimePickerStartPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimePickerStartPlaceholder.restype = None
```
## EU_SetTimePickerEndPlaceholder

```python
dll.EU_SetTimePickerEndPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimePickerEndPlaceholder.restype = None
```
## EU_SetTimePickerRangeSeparator

```python
dll.EU_SetTimePickerRangeSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimePickerRangeSeparator.restype = None
```
## EU_GetTimePickerRangeValue

```python
dll.EU_GetTimePickerRangeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimePickerRangeValue.restype = ctypes.c_int
```
## EU_SetTimeSelectPlaceholder

```python
dll.EU_SetTimeSelectPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTimeSelectPlaceholder.restype = None
```
## EU_SetDateTimePickerDateTime

```python
dll.EU_SetDateTimePickerDateTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerDateTime.restype = None
```
## EU_SetDateTimePickerRange

```python
dll.EU_SetDateTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerRange.restype = None
```
## EU_SetDateTimePickerOptions

```python
dll.EU_SetDateTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerOptions.restype = None
```
## EU_SetDateTimePickerOpen

```python
dll.EU_SetDateTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerOpen.restype = None
```
## EU_ClearDateTimePicker

```python
dll.EU_ClearDateTimePicker.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearDateTimePicker.restype = None
```
## EU_DateTimePickerSelectToday

```python
dll.EU_DateTimePickerSelectToday.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_DateTimePickerSelectToday.restype = None
```
## EU_DateTimePickerSelectNow

```python
dll.EU_DateTimePickerSelectNow.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_DateTimePickerSelectNow.restype = None
```
## EU_SetDateTimePickerScroll

```python
dll.EU_SetDateTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerScroll.restype = None
```
## EU_GetDateTimePickerOpen

```python
dll.EU_GetDateTimePickerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateTimePickerOpen.restype = ctypes.c_int
```
## EU_GetDateTimePickerDateValue

```python
dll.EU_GetDateTimePickerDateValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateTimePickerDateValue.restype = ctypes.c_int
```
## EU_GetDateTimePickerTimeValue

```python
dll.EU_GetDateTimePickerTimeValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDateTimePickerTimeValue.restype = ctypes.c_int
```
## EU_DateTimePickerMoveMonth

```python
dll.EU_DateTimePickerMoveMonth.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_DateTimePickerMoveMonth.restype = None
```
## EU_GetDateTimePickerRange

```python
dll.EU_GetDateTimePickerRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerRange.restype = ctypes.c_int
```
## EU_GetDateTimePickerOptions

```python
dll.EU_GetDateTimePickerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerOptions.restype = ctypes.c_int
```
## EU_GetDateTimePickerScroll

```python
dll.EU_GetDateTimePickerScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerScroll.restype = ctypes.c_int
```
## EU_SetDateTimePickerShortcuts

```python
dll.EU_SetDateTimePickerShortcuts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerShortcuts.restype = None
```
## EU_SetDateTimePickerStartPlaceholder

```python
dll.EU_SetDateTimePickerStartPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerStartPlaceholder.restype = None
```
## EU_SetDateTimePickerEndPlaceholder

```python
dll.EU_SetDateTimePickerEndPlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerEndPlaceholder.restype = None
```
## EU_SetDateTimePickerDefaultTime

```python
dll.EU_SetDateTimePickerDefaultTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerDefaultTime.restype = None
```
## EU_SetDateTimePickerRangeDefaultTime

```python
dll.EU_SetDateTimePickerRangeDefaultTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerRangeDefaultTime.restype = None
```
## EU_SetDateTimePickerRangeSeparator

```python
dll.EU_SetDateTimePickerRangeSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDateTimePickerRangeSeparator.restype = None
```
## EU_SetDateTimePickerRangeSelect

```python
dll.EU_SetDateTimePickerRangeSelect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDateTimePickerRangeSelect.restype = None
```
## EU_GetDateTimePickerRangeValue

```python
dll.EU_GetDateTimePickerRangeValue.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDateTimePickerRangeValue.restype = ctypes.c_int
```
## EU_SetTimeSelectTime

```python
dll.EU_SetTimeSelectTime.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectTime.restype = None
```
## EU_SetTimeSelectRange

```python
dll.EU_SetTimeSelectRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectRange.restype = None
```
## EU_SetTimeSelectOptions

```python
dll.EU_SetTimeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectOptions.restype = None
```
## EU_SetTimeSelectOpen

```python
dll.EU_SetTimeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectOpen.restype = None
```
## EU_SetTimeSelectScroll

```python
dll.EU_SetTimeSelectScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTimeSelectScroll.restype = None
```
## EU_GetTimeSelectOpen

```python
dll.EU_GetTimeSelectOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimeSelectOpen.restype = ctypes.c_int
```
## EU_GetTimeSelectValue

```python
dll.EU_GetTimeSelectValue.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTimeSelectValue.restype = ctypes.c_int
```
## EU_GetTimeSelectRange

```python
dll.EU_GetTimeSelectRange.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimeSelectRange.restype = ctypes.c_int
```
## EU_GetTimeSelectOptions

```python
dll.EU_GetTimeSelectOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimeSelectOptions.restype = ctypes.c_int
```
## EU_GetTimeSelectState

```python
dll.EU_GetTimeSelectState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTimeSelectState.restype = ctypes.c_int
```
## EU_SetDropdownItems

```python
dll.EU_SetDropdownItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDropdownItems.restype = None
```
## EU_SetDropdownSelected

```python
dll.EU_SetDropdownSelected.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDropdownSelected.restype = None
```
## EU_GetDropdownSelected

```python
dll.EU_GetDropdownSelected.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDropdownSelected.restype = ctypes.c_int
```
## EU_SetDropdownOpen

```python
dll.EU_SetDropdownOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDropdownOpen.restype = None
```
## EU_GetDropdownOpen

```python
dll.EU_GetDropdownOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDropdownOpen.restype = ctypes.c_int
```
## EU_GetDropdownItemCount

```python
dll.EU_GetDropdownItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDropdownItemCount.restype = ctypes.c_int
```
## EU_SetDropdownDisabled

```python
dll.EU_SetDropdownDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetDropdownDisabled.restype = None
```
## EU_GetDropdownState

```python
dll.EU_GetDropdownState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDropdownState.restype = ctypes.c_int
```
## EU_SetDropdownOptions

```python
dll.EU_SetDropdownOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDropdownOptions.restype = None
```
## EU_GetDropdownOptions

```python
dll.EU_GetDropdownOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDropdownOptions.restype = ctypes.c_int
```
## EU_SetDropdownItemMeta

```python
dll.EU_SetDropdownItemMeta.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetDropdownItemMeta.restype = None
```
## EU_GetDropdownItemMeta

```python
dll.EU_GetDropdownItemMeta.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDropdownItemMeta.restype = ctypes.c_int
```
## EU_SetDropdownCommandCallback

```python
dll.EU_SetDropdownCommandCallback.argtypes = [wintypes.HWND, ctypes.c_int, DropdownCommandCallback]
dll.EU_SetDropdownCommandCallback.restype = None
```
## EU_SetDropdownMainClickCallback

```python
dll.EU_SetDropdownMainClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementClickCallback]
dll.EU_SetDropdownMainClickCallback.restype = None
```
## EU_SetMenuItems

```python
dll.EU_SetMenuItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMenuItems.restype = None
```
## EU_SetMenuActive

```python
dll.EU_SetMenuActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMenuActive.restype = None
```
## EU_GetMenuActive

```python
dll.EU_GetMenuActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuActive.restype = ctypes.c_int
```
## EU_SetMenuOrientation

```python
dll.EU_SetMenuOrientation.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMenuOrientation.restype = None
```
## EU_GetMenuOrientation

```python
dll.EU_GetMenuOrientation.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuOrientation.restype = ctypes.c_int
```
## EU_GetMenuItemCount

```python
dll.EU_GetMenuItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuItemCount.restype = ctypes.c_int
```
## EU_SetMenuExpanded

```python
dll.EU_SetMenuExpanded.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetMenuExpanded.restype = None
```
## EU_GetMenuState

```python
dll.EU_GetMenuState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMenuState.restype = ctypes.c_int
```
## EU_GetMenuActivePath

```python
dll.EU_GetMenuActivePath.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMenuActivePath.restype = ctypes.c_int
```
## EU_SetMenuColors

```python
dll.EU_SetMenuColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetMenuColors.restype = None
```
## EU_GetMenuColors

```python
dll.EU_GetMenuColors.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
dll.EU_GetMenuColors.restype = ctypes.c_int
```
## EU_SetMenuCollapsed

```python
dll.EU_SetMenuCollapsed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMenuCollapsed.restype = None
```
## EU_GetMenuCollapsed

```python
dll.EU_GetMenuCollapsed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetMenuCollapsed.restype = ctypes.c_int
```
## EU_SetMenuItemMeta

```python
dll.EU_SetMenuItemMeta.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMenuItemMeta.restype = None
```
## EU_GetMenuItemMeta

```python
dll.EU_GetMenuItemMeta.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMenuItemMeta.restype = ctypes.c_int
```
## EU_SetMenuSelectCallback

```python
dll.EU_SetMenuSelectCallback.argtypes = [wintypes.HWND, ctypes.c_int, MenuSelectCallback]
dll.EU_SetMenuSelectCallback.restype = None
```
## EU_SetAnchorItems

```python
dll.EU_SetAnchorItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAnchorItems.restype = None
```
## EU_SetAnchorActive

```python
dll.EU_SetAnchorActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAnchorActive.restype = None
```
## EU_GetAnchorActive

```python
dll.EU_GetAnchorActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAnchorActive.restype = ctypes.c_int
```
## EU_GetAnchorItemCount

```python
dll.EU_GetAnchorItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAnchorItemCount.restype = ctypes.c_int
```
## EU_SetAnchorTargets

```python
dll.EU_SetAnchorTargets.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetAnchorTargets.restype = None
```
## EU_SetAnchorOptions

```python
dll.EU_SetAnchorOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetAnchorOptions.restype = None
```
## EU_SetAnchorScroll

```python
dll.EU_SetAnchorScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAnchorScroll.restype = None
```
## EU_GetAnchorState

```python
dll.EU_GetAnchorState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAnchorState.restype = ctypes.c_int
```
## EU_SetBacktopState

```python
dll.EU_SetBacktopState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBacktopState.restype = None
```
## EU_GetBacktopVisible

```python
dll.EU_GetBacktopVisible.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBacktopVisible.restype = ctypes.c_int
```
## EU_GetBacktopState

```python
dll.EU_GetBacktopState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBacktopState.restype = ctypes.c_int
```
## EU_SetBacktopOptions

```python
dll.EU_SetBacktopOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetBacktopOptions.restype = None
```
## EU_SetBacktopScroll

```python
dll.EU_SetBacktopScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBacktopScroll.restype = None
```
## EU_TriggerBacktop

```python
dll.EU_TriggerBacktop.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TriggerBacktop.restype = None
```
## EU_GetBacktopFullState

```python
dll.EU_GetBacktopFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBacktopFullState.restype = ctypes.c_int
```
## EU_SetSegmentedItems

```python
dll.EU_SetSegmentedItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetSegmentedItems.restype = None
```
## EU_SetSegmentedActive

```python
dll.EU_SetSegmentedActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetSegmentedActive.restype = None
```
## EU_GetSegmentedActive

```python
dll.EU_GetSegmentedActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSegmentedActive.restype = ctypes.c_int
```
## EU_GetSegmentedItemCount

```python
dll.EU_GetSegmentedItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetSegmentedItemCount.restype = ctypes.c_int
```
## EU_SetSegmentedDisabled

```python
dll.EU_SetSegmentedDisabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetSegmentedDisabled.restype = None
```
## EU_GetSegmentedState

```python
dll.EU_GetSegmentedState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetSegmentedState.restype = ctypes.c_int
```
## EU_SetPageHeaderText

```python
dll.EU_SetPageHeaderText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPageHeaderText.restype = None
```
## EU_SetPageHeaderBreadcrumbs

```python
dll.EU_SetPageHeaderBreadcrumbs.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPageHeaderBreadcrumbs.restype = None
```
## EU_SetPageHeaderActions

```python
dll.EU_SetPageHeaderActions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPageHeaderActions.restype = None
```
## EU_GetPageHeaderAction

```python
dll.EU_GetPageHeaderAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPageHeaderAction.restype = ctypes.c_int
```
## EU_SetPageHeaderBackText

```python
dll.EU_SetPageHeaderBackText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPageHeaderBackText.restype = None
```
## EU_SetPageHeaderActiveAction

```python
dll.EU_SetPageHeaderActiveAction.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPageHeaderActiveAction.restype = None
```
## EU_SetPageHeaderBreadcrumbActive

```python
dll.EU_SetPageHeaderBreadcrumbActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPageHeaderBreadcrumbActive.restype = None
```
## EU_TriggerPageHeaderBack

```python
dll.EU_TriggerPageHeaderBack.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TriggerPageHeaderBack.restype = None
```
## EU_ResetPageHeaderResult

```python
dll.EU_ResetPageHeaderResult.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ResetPageHeaderResult.restype = None
```
## EU_GetPageHeaderState

```python
dll.EU_GetPageHeaderState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPageHeaderState.restype = ctypes.c_int
```
## EU_SetAffixText

```python
dll.EU_SetAffixText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAffixText.restype = None
```
## EU_SetAffixState

```python
dll.EU_SetAffixState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetAffixState.restype = None
```
## EU_GetAffixFixed

```python
dll.EU_GetAffixFixed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAffixFixed.restype = ctypes.c_int
```
## EU_GetAffixState

```python
dll.EU_GetAffixState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAffixState.restype = ctypes.c_int
```
## EU_SetAffixOptions

```python
dll.EU_SetAffixOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetAffixOptions.restype = None
```
## EU_GetAffixOptions

```python
dll.EU_GetAffixOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAffixOptions.restype = ctypes.c_int
```
## EU_SetWatermarkContent

```python
dll.EU_SetWatermarkContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetWatermarkContent.restype = None
```
## EU_SetWatermarkOptions

```python
dll.EU_SetWatermarkOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetWatermarkOptions.restype = None
```
## EU_GetWatermarkOptions

```python
dll.EU_GetWatermarkOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetWatermarkOptions.restype = ctypes.c_int
```
## EU_SetWatermarkLayer

```python
dll.EU_SetWatermarkLayer.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetWatermarkLayer.restype = None
```
## EU_GetWatermarkFullOptions

```python
dll.EU_GetWatermarkFullOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetWatermarkFullOptions.restype = ctypes.c_int
```
## EU_SetTourSteps

```python
dll.EU_SetTourSteps.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTourSteps.restype = None
```
## EU_SetTourActive

```python
dll.EU_SetTourActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourActive.restype = None
```
## EU_SetTourOpen

```python
dll.EU_SetTourOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourOpen.restype = None
```
## EU_SetTourOptions

```python
dll.EU_SetTourOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourOptions.restype = None
```
## EU_SetTourTargetElement

```python
dll.EU_SetTourTargetElement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourTargetElement.restype = None
```
## EU_SetTourMaskBehavior

```python
dll.EU_SetTourMaskBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTourMaskBehavior.restype = None
```
## EU_GetTourActive

```python
dll.EU_GetTourActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTourActive.restype = ctypes.c_int
```
## EU_GetTourOpen

```python
dll.EU_GetTourOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTourOpen.restype = ctypes.c_int
```
## EU_GetTourStepCount

```python
dll.EU_GetTourStepCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTourStepCount.restype = ctypes.c_int
```
## EU_GetTourOptions

```python
dll.EU_GetTourOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTourOptions.restype = ctypes.c_int
```
## EU_GetTourFullState

```python
dll.EU_GetTourFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTourFullState.restype = ctypes.c_int
```
## EU_SetImageSource

```python
dll.EU_SetImageSource.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetImageSource.restype = None
```
## EU_SetImageFit

```python
dll.EU_SetImageFit.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImageFit.restype = None
```
## EU_SetImagePreview

```python
dll.EU_SetImagePreview.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreview.restype = None
```
## EU_SetImagePreviewEnabled

```python
dll.EU_SetImagePreviewEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreviewEnabled.restype = None
```
## EU_SetImagePreviewTransform

```python
dll.EU_SetImagePreviewTransform.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreviewTransform.restype = None
```
## EU_SetImageCacheEnabled

```python
dll.EU_SetImageCacheEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImageCacheEnabled.restype = None
```
## EU_SetImageLazy

```python
dll.EU_SetImageLazy.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImageLazy.restype = None
```
## EU_SetImagePlaceholder

```python
dll.EU_SetImagePlaceholder.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetImagePlaceholder.restype = None
```
## EU_SetImageErrorContent

```python
dll.EU_SetImageErrorContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32]
dll.EU_SetImageErrorContent.restype = None
```
## EU_SetImagePreviewList

```python
dll.EU_SetImagePreviewList.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreviewList.restype = None
```
## EU_SetImagePreviewIndex

```python
dll.EU_SetImagePreviewIndex.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetImagePreviewIndex.restype = None
```
## EU_GetImageStatus

```python
dll.EU_GetImageStatus.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetImageStatus.restype = ctypes.c_int
```
## EU_GetImagePreviewOpen

```python
dll.EU_GetImagePreviewOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetImagePreviewOpen.restype = ctypes.c_int
```
## EU_GetImageOptions

```python
dll.EU_GetImageOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetImageOptions.restype = ctypes.c_int
```
## EU_GetImageFullOptions

```python
dll.EU_GetImageFullOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetImageFullOptions.restype = ctypes.c_int
```
## EU_GetImageAdvancedOptions

```python
dll.EU_GetImageAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetImageAdvancedOptions.restype = ctypes.c_int
```
## EU_SetCarouselItems

```python
dll.EU_SetCarouselItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetCarouselItems.restype = None
```
## EU_SetCarouselActive

```python
dll.EU_SetCarouselActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselActive.restype = None
```
## EU_SetCarouselOptions

```python
dll.EU_SetCarouselOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselOptions.restype = None
```
## EU_SetCarouselBehavior

```python
dll.EU_SetCarouselBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselBehavior.restype = None
```
## EU_GetCarouselBehavior

```python
dll.EU_GetCarouselBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCarouselBehavior.restype = ctypes.c_int
```
## EU_SetCarouselVisual

```python
dll.EU_SetCarouselVisual.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int]
dll.EU_SetCarouselVisual.restype = None
```
## EU_GetCarouselVisual

```python
dll.EU_GetCarouselVisual.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCarouselVisual.restype = ctypes.c_int
```
## EU_SetCarouselAutoplay

```python
dll.EU_SetCarouselAutoplay.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselAutoplay.restype = None
```
## EU_SetCarouselAnimation

```python
dll.EU_SetCarouselAnimation.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetCarouselAnimation.restype = None
```
## EU_CarouselAdvance

```python
dll.EU_CarouselAdvance.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_CarouselAdvance.restype = None
```
## EU_CarouselTick

```python
dll.EU_CarouselTick.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_CarouselTick.restype = None
```
## EU_GetCarouselActive

```python
dll.EU_GetCarouselActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCarouselActive.restype = ctypes.c_int
```
## EU_GetCarouselItemCount

```python
dll.EU_GetCarouselItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetCarouselItemCount.restype = ctypes.c_int
```
## EU_GetCarouselOptions

```python
dll.EU_GetCarouselOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCarouselOptions.restype = ctypes.c_int
```
## EU_GetCarouselFullState

```python
dll.EU_GetCarouselFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetCarouselFullState.restype = ctypes.c_int
```
## EU_SetUploadFiles

```python
dll.EU_SetUploadFiles.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadFiles.restype = None
```
## EU_SetUploadFileItems

```python
dll.EU_SetUploadFileItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadFileItems.restype = None
```
## EU_SetUploadOptions

```python
dll.EU_SetUploadOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetUploadOptions.restype = None
```
## EU_SetUploadStyle

```python
dll.EU_SetUploadStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetUploadStyle.restype = None
```
## EU_GetUploadStyle

```python
dll.EU_GetUploadStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetUploadStyle.restype = ctypes.c_int
```
## EU_SetUploadTexts

```python
dll.EU_SetUploadTexts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadTexts.restype = None
```
## EU_SetUploadConstraints

```python
dll.EU_SetUploadConstraints.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadConstraints.restype = None
```
## EU_GetUploadConstraints

```python
dll.EU_GetUploadConstraints.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetUploadConstraints.restype = ctypes.c_int
```
## EU_SetUploadPreviewOpen

```python
dll.EU_SetUploadPreviewOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetUploadPreviewOpen.restype = None
```
## EU_GetUploadPreviewState

```python
dll.EU_GetUploadPreviewState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetUploadPreviewState.restype = ctypes.c_int
```
## EU_SetUploadSelectedFiles

```python
dll.EU_SetUploadSelectedFiles.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetUploadSelectedFiles.restype = None
```
## EU_SetUploadFileStatus

```python
dll.EU_SetUploadFileStatus.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetUploadFileStatus.restype = None
```
## EU_RemoveUploadFile

```python
dll.EU_RemoveUploadFile.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_RemoveUploadFile.restype = None
```
## EU_RetryUploadFile

```python
dll.EU_RetryUploadFile.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_RetryUploadFile.restype = None
```
## EU_ClearUploadFiles

```python
dll.EU_ClearUploadFiles.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearUploadFiles.restype = None
```
## EU_OpenUploadFileDialog

```python
dll.EU_OpenUploadFileDialog.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_OpenUploadFileDialog.restype = ctypes.c_int
```
## EU_StartUpload

```python
dll.EU_StartUpload.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_StartUpload.restype = ctypes.c_int
```
## EU_GetUploadFileCount

```python
dll.EU_GetUploadFileCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetUploadFileCount.restype = ctypes.c_int
```
## EU_GetUploadFileStatus

```python
dll.EU_GetUploadFileStatus.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetUploadFileStatus.restype = ctypes.c_int
```
## EU_GetUploadSelectedFiles

```python
dll.EU_GetUploadSelectedFiles.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetUploadSelectedFiles.restype = ctypes.c_int
```
## EU_GetUploadFileName

```python
dll.EU_GetUploadFileName.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetUploadFileName.restype = ctypes.c_int
```
## EU_GetUploadFullState

```python
dll.EU_GetUploadFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetUploadFullState.restype = ctypes.c_int
```
## EU_SetUploadSelectCallback

```python
dll.EU_SetUploadSelectCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementTextCallback]
dll.EU_SetUploadSelectCallback.restype = None
```
## EU_SetUploadActionCallback

```python
dll.EU_SetUploadActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetUploadActionCallback.restype = None
```
## EU_SetInfiniteScrollItems

```python
dll.EU_SetInfiniteScrollItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInfiniteScrollItems.restype = None
```
## EU_AppendInfiniteScrollItems

```python
dll.EU_AppendInfiniteScrollItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AppendInfiniteScrollItems.restype = None
```
## EU_ClearInfiniteScrollItems

```python
dll.EU_ClearInfiniteScrollItems.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ClearInfiniteScrollItems.restype = None
```
## EU_SetInfiniteScrollState

```python
dll.EU_SetInfiniteScrollState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInfiniteScrollState.restype = None
```
## EU_SetInfiniteScrollOptions

```python
dll.EU_SetInfiniteScrollOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetInfiniteScrollOptions.restype = None
```
## EU_SetInfiniteScrollTexts

```python
dll.EU_SetInfiniteScrollTexts.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetInfiniteScrollTexts.restype = None
```
## EU_SetInfiniteScrollScroll

```python
dll.EU_SetInfiniteScrollScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetInfiniteScrollScroll.restype = None
```
## EU_GetInfiniteScrollFullState

```python
dll.EU_GetInfiniteScrollFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetInfiniteScrollFullState.restype = ctypes.c_int
```
## EU_SetInfiniteScrollLoadCallback

```python
dll.EU_SetInfiniteScrollLoadCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetInfiniteScrollLoadCallback.restype = None
```
## EU_SetBreadcrumbItems

```python
dll.EU_SetBreadcrumbItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBreadcrumbItems.restype = None
```
## EU_SetBreadcrumbSeparator

```python
dll.EU_SetBreadcrumbSeparator.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetBreadcrumbSeparator.restype = None
```
## EU_SetBreadcrumbCurrent

```python
dll.EU_SetBreadcrumbCurrent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetBreadcrumbCurrent.restype = None
```
## EU_TriggerBreadcrumbClick

```python
dll.EU_TriggerBreadcrumbClick.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerBreadcrumbClick.restype = None
```
## EU_GetBreadcrumbCurrent

```python
dll.EU_GetBreadcrumbCurrent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBreadcrumbCurrent.restype = ctypes.c_int
```
## EU_GetBreadcrumbItemCount

```python
dll.EU_GetBreadcrumbItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetBreadcrumbItemCount.restype = ctypes.c_int
```
## EU_GetBreadcrumbState

```python
dll.EU_GetBreadcrumbState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBreadcrumbState.restype = ctypes.c_int
```
## EU_GetBreadcrumbItem

```python
dll.EU_GetBreadcrumbItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetBreadcrumbItem.restype = ctypes.c_int
```
## EU_GetBreadcrumbFullState

```python
dll.EU_GetBreadcrumbFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetBreadcrumbFullState.restype = ctypes.c_int
```
## EU_SetBreadcrumbSelectCallback

```python
dll.EU_SetBreadcrumbSelectCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetBreadcrumbSelectCallback.restype = None
```
## EU_SetTabsItems

```python
dll.EU_SetTabsItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTabsItems.restype = None
```
## EU_SetTabsItemsEx

```python
dll.EU_SetTabsItemsEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTabsItemsEx.restype = None
```
## EU_SetTabsActive

```python
dll.EU_SetTabsActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsActive.restype = None
```
## EU_SetTabsActiveName

```python
dll.EU_SetTabsActiveName.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTabsActiveName.restype = None
```
## EU_SetTabsType

```python
dll.EU_SetTabsType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsType.restype = None
```
## EU_SetTabsPosition

```python
dll.EU_SetTabsPosition.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsPosition.restype = None
```
## EU_SetTabsHeaderAlign

```python
dll.EU_SetTabsHeaderAlign.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsHeaderAlign.restype = None
```
## EU_SetTabsOptions

```python
dll.EU_SetTabsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsOptions.restype = None
```
## EU_SetTabsEditable

```python
dll.EU_SetTabsEditable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsEditable.restype = None
```
## EU_SetTabsContentVisible

```python
dll.EU_SetTabsContentVisible.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsContentVisible.restype = None
```
## EU_AddTabsItem

```python
dll.EU_AddTabsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_AddTabsItem.restype = None
```
## EU_CloseTabsItem

```python
dll.EU_CloseTabsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_CloseTabsItem.restype = None
```
## EU_SetTabsScroll

```python
dll.EU_SetTabsScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTabsScroll.restype = None
```
## EU_TabsScroll

```python
dll.EU_TabsScroll.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TabsScroll.restype = None
```
## EU_GetTabsActive

```python
dll.EU_GetTabsActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsActive.restype = ctypes.c_int
```
## EU_GetTabsHeaderAlign

```python
dll.EU_GetTabsHeaderAlign.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsHeaderAlign.restype = ctypes.c_int
```
## EU_GetTabsItemCount

```python
dll.EU_GetTabsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTabsItemCount.restype = ctypes.c_int
```
## EU_GetTabsState

```python
dll.EU_GetTabsState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTabsState.restype = ctypes.c_int
```
## EU_GetTabsItem

```python
dll.EU_GetTabsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTabsItem.restype = ctypes.c_int
```
## EU_GetTabsActiveName

```python
dll.EU_GetTabsActiveName.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTabsActiveName.restype = ctypes.c_int
```
## EU_GetTabsItemContent

```python
dll.EU_GetTabsItemContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTabsItemContent.restype = ctypes.c_int
```
## EU_GetTabsFullState

```python
dll.EU_GetTabsFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTabsFullState.restype = ctypes.c_int
```
## EU_GetTabsFullStateEx

```python
dll.EU_GetTabsFullStateEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTabsFullStateEx.restype = ctypes.c_int
```
## EU_SetTabsChangeCallback

```python
dll.EU_SetTabsChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetTabsChangeCallback.restype = None
```
## EU_SetTabsCloseCallback

```python
dll.EU_SetTabsCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetTabsCloseCallback.restype = None
```
## EU_SetTabsAddCallback

```python
dll.EU_SetTabsAddCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetTabsAddCallback.restype = None
```
## EU_SetPagination

```python
dll.EU_SetPagination.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPagination.restype = None
```
## EU_SetPaginationCurrent

```python
dll.EU_SetPaginationCurrent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationCurrent.restype = None
```
## EU_SetPaginationPageSize

```python
dll.EU_SetPaginationPageSize.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationPageSize.restype = None
```
## EU_SetPaginationOptions

```python
dll.EU_SetPaginationOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationOptions.restype = None
```
## EU_SetPaginationAdvancedOptions

```python
dll.EU_SetPaginationAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationAdvancedOptions.restype = None
```
## EU_SetPaginationPageSizeOptions

```python
dll.EU_SetPaginationPageSizeOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetPaginationPageSizeOptions.restype = None
```
## EU_SetPaginationJumpPage

```python
dll.EU_SetPaginationJumpPage.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPaginationJumpPage.restype = None
```
## EU_TriggerPaginationJump

```python
dll.EU_TriggerPaginationJump.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TriggerPaginationJump.restype = None
```
## EU_NextPaginationPageSize

```python
dll.EU_NextPaginationPageSize.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_NextPaginationPageSize.restype = None
```
## EU_GetPaginationCurrent

```python
dll.EU_GetPaginationCurrent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPaginationCurrent.restype = ctypes.c_int
```
## EU_GetPaginationPageCount

```python
dll.EU_GetPaginationPageCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPaginationPageCount.restype = ctypes.c_int
```
## EU_GetPaginationState

```python
dll.EU_GetPaginationState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPaginationState.restype = ctypes.c_int
```
## EU_GetPaginationFullState

```python
dll.EU_GetPaginationFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPaginationFullState.restype = ctypes.c_int
```
## EU_GetPaginationAdvancedOptions

```python
dll.EU_GetPaginationAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPaginationAdvancedOptions.restype = ctypes.c_int
```
## EU_SetPaginationChangeCallback

```python
dll.EU_SetPaginationChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetPaginationChangeCallback.restype = None
```
## EU_SetStepsItems

```python
dll.EU_SetStepsItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsItems.restype = None
```
## EU_SetStepsDetailItems

```python
dll.EU_SetStepsDetailItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsDetailItems.restype = None
```
## EU_SetStepsIconItems

```python
dll.EU_SetStepsIconItems.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetStepsIconItems.restype = None
```
## EU_SetStepsActive

```python
dll.EU_SetStepsActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetStepsActive.restype = None
```
## EU_SetStepsDirection

```python
dll.EU_SetStepsDirection.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetStepsDirection.restype = None
```
## EU_SetStepsOptions

```python
dll.EU_SetStepsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetStepsOptions.restype = None
```
## EU_GetStepsOptions

```python
dll.EU_GetStepsOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStepsOptions.restype = ctypes.c_int
```
## EU_SetStepsStatuses

```python
dll.EU_SetStepsStatuses.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
dll.EU_SetStepsStatuses.restype = None
```
## EU_TriggerStepsClick

```python
dll.EU_TriggerStepsClick.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerStepsClick.restype = None
```
## EU_GetStepsActive

```python
dll.EU_GetStepsActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetStepsActive.restype = ctypes.c_int
```
## EU_GetStepsItemCount

```python
dll.EU_GetStepsItemCount.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetStepsItemCount.restype = ctypes.c_int
```
## EU_GetStepsState

```python
dll.EU_GetStepsState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStepsState.restype = ctypes.c_int
```
## EU_GetStepsItem

```python
dll.EU_GetStepsItem.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetStepsItem.restype = ctypes.c_int
```
## EU_GetStepsFullState

```python
dll.EU_GetStepsFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStepsFullState.restype = ctypes.c_int
```
## EU_GetStepsVisualState

```python
dll.EU_GetStepsVisualState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetStepsVisualState.restype = ctypes.c_int
```
## EU_SetStepsChangeCallback

```python
dll.EU_SetStepsChangeCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetStepsChangeCallback.restype = None
```
## EU_SetAlertDescription

```python
dll.EU_SetAlertDescription.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAlertDescription.restype = None
```
## EU_SetAlertType

```python
dll.EU_SetAlertType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertType.restype = None
```
## EU_SetAlertEffect

```python
dll.EU_SetAlertEffect.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertEffect.restype = None
```
## EU_SetAlertClosable

```python
dll.EU_SetAlertClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertClosable.restype = None
```
## EU_SetAlertAdvancedOptions

```python
dll.EU_SetAlertAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertAdvancedOptions.restype = None
```
## EU_GetAlertAdvancedOptions

```python
dll.EU_GetAlertAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAlertAdvancedOptions.restype = ctypes.c_int
```
## EU_SetAlertCloseText

```python
dll.EU_SetAlertCloseText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetAlertCloseText.restype = None
```
## EU_GetAlertText

```python
dll.EU_GetAlertText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetAlertText.restype = ctypes.c_int
```
## EU_SetAlertClosed

```python
dll.EU_SetAlertClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetAlertClosed.restype = None
```
## EU_TriggerAlertClose

```python
dll.EU_TriggerAlertClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TriggerAlertClose.restype = None
```
## EU_GetAlertClosed

```python
dll.EU_GetAlertClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetAlertClosed.restype = ctypes.c_int
```
## EU_GetAlertOptions

```python
dll.EU_GetAlertOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAlertOptions.restype = ctypes.c_int
```
## EU_GetAlertFullState

```python
dll.EU_GetAlertFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetAlertFullState.restype = ctypes.c_int
```
## EU_SetAlertCloseCallback

```python
dll.EU_SetAlertCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetAlertCloseCallback.restype = None
```
## EU_SetResultSubtitle

```python
dll.EU_SetResultSubtitle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetResultSubtitle.restype = None
```
## EU_SetResultType

```python
dll.EU_SetResultType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetResultType.restype = None
```
## EU_SetResultActions

```python
dll.EU_SetResultActions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetResultActions.restype = None
```
## EU_GetResultAction

```python
dll.EU_GetResultAction.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetResultAction.restype = ctypes.c_int
```
## EU_GetResultOptions

```python
dll.EU_GetResultOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetResultOptions.restype = ctypes.c_int
```
## EU_SetResultExtraContent

```python
dll.EU_SetResultExtraContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetResultExtraContent.restype = None
```
## EU_TriggerResultAction

```python
dll.EU_TriggerResultAction.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerResultAction.restype = None
```
## EU_GetResultText

```python
dll.EU_GetResultText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetResultText.restype = ctypes.c_int
```
## EU_GetResultActionText

```python
dll.EU_GetResultActionText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetResultActionText.restype = ctypes.c_int
```
## EU_GetResultFullState

```python
dll.EU_GetResultFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetResultFullState.restype = ctypes.c_int
```
## EU_SetResultActionCallback

```python
dll.EU_SetResultActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetResultActionCallback.restype = None
```
## EU_SetMessageBoxBeforeClose

```python
dll.EU_SetMessageBoxBeforeClose.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMessageBoxBeforeClose.restype = None
```
## EU_SetMessageBoxInput

```python
dll.EU_SetMessageBoxInput.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMessageBoxInput.restype = None
```
## EU_GetMessageBoxInput

```python
dll.EU_GetMessageBoxInput.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetMessageBoxInput.restype = ctypes.c_int
```
## EU_GetMessageBoxFullState

```python
dll.EU_GetMessageBoxFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMessageBoxFullState.restype = ctypes.c_int
```
## EU_SetMessageText

```python
dll.EU_SetMessageText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetMessageText.restype = None
```
## EU_SetMessageOptions

```python
dll.EU_SetMessageOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetMessageOptions.restype = None
```
## EU_SetMessageClosed

```python
dll.EU_SetMessageClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetMessageClosed.restype = None
```
## EU_GetMessageOptions

```python
dll.EU_GetMessageOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMessageOptions.restype = ctypes.c_int
```
## EU_GetMessageFullState

```python
dll.EU_GetMessageFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetMessageFullState.restype = ctypes.c_int
```
## EU_TriggerMessageClose

```python
dll.EU_TriggerMessageClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TriggerMessageClose.restype = None
```
## EU_SetMessageCloseCallback

```python
dll.EU_SetMessageCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetMessageCloseCallback.restype = None
```
## EU_SetNotificationBody

```python
dll.EU_SetNotificationBody.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetNotificationBody.restype = None
```
## EU_SetNotificationType

```python
dll.EU_SetNotificationType.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationType.restype = None
```
## EU_SetNotificationClosable

```python
dll.EU_SetNotificationClosable.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationClosable.restype = None
```
## EU_SetNotificationPlacement

```python
dll.EU_SetNotificationPlacement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationPlacement.restype = None
```
## EU_SetNotificationRichMode

```python
dll.EU_SetNotificationRichMode.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationRichMode.restype = None
```
## EU_SetNotificationOptions

```python
dll.EU_SetNotificationOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationOptions.restype = None
```
## EU_SetNotificationClosed

```python
dll.EU_SetNotificationClosed.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationClosed.restype = None
```
## EU_GetNotificationClosed

```python
dll.EU_GetNotificationClosed.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetNotificationClosed.restype = ctypes.c_int
```
## EU_GetNotificationOptions

```python
dll.EU_GetNotificationOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetNotificationOptions.restype = ctypes.c_int
```
## EU_SetNotificationStack

```python
dll.EU_SetNotificationStack.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetNotificationStack.restype = None
```
## EU_TriggerNotificationClose

```python
dll.EU_TriggerNotificationClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TriggerNotificationClose.restype = None
```
## EU_GetNotificationText

```python
dll.EU_GetNotificationText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetNotificationText.restype = ctypes.c_int
```
## EU_GetNotificationFullState

```python
dll.EU_GetNotificationFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetNotificationFullState.restype = ctypes.c_int
```
## EU_GetNotificationFullStateEx

```python
dll.EU_GetNotificationFullStateEx.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetNotificationFullStateEx.restype = ctypes.c_int
```
## EU_SetNotificationCloseCallback

```python
dll.EU_SetNotificationCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetNotificationCloseCallback.restype = None
```
## EU_SetLoadingActive

```python
dll.EU_SetLoadingActive.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetLoadingActive.restype = None
```
## EU_SetLoadingText

```python
dll.EU_SetLoadingText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetLoadingText.restype = None
```
## EU_SetLoadingOptions

```python
dll.EU_SetLoadingOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLoadingOptions.restype = None
```
## EU_SetLoadingStyle

```python
dll.EU_SetLoadingStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int, ctypes.c_int]
dll.EU_SetLoadingStyle.restype = None
```
## EU_GetLoadingActive

```python
dll.EU_GetLoadingActive.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetLoadingActive.restype = ctypes.c_int
```
## EU_GetLoadingOptions

```python
dll.EU_GetLoadingOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLoadingOptions.restype = ctypes.c_int
```
## EU_SetLoadingTarget

```python
dll.EU_SetLoadingTarget.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetLoadingTarget.restype = None
```
## EU_GetLoadingText

```python
dll.EU_GetLoadingText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetLoadingText.restype = ctypes.c_int
```
## EU_GetLoadingStyle

```python
dll.EU_GetLoadingStyle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLoadingStyle.restype = ctypes.c_int
```
## EU_ShowLoading

```python
dll.EU_ShowLoading.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int]
dll.EU_ShowLoading.restype = ctypes.c_int
```
## EU_CloseLoading

```python
dll.EU_CloseLoading.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_CloseLoading.restype = ctypes.c_int
```
## EU_GetLoadingFullState

```python
dll.EU_GetLoadingFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetLoadingFullState.restype = ctypes.c_int
```
## EU_SetDialogOpen

```python
dll.EU_SetDialogOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDialogOpen.restype = None
```
## EU_SetDialogTitle

```python
dll.EU_SetDialogTitle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDialogTitle.restype = None
```
## EU_SetDialogBody

```python
dll.EU_SetDialogBody.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDialogBody.restype = None
```
## EU_SetDialogOptions

```python
dll.EU_SetDialogOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDialogOptions.restype = None
```
## EU_GetDialogOpen

```python
dll.EU_GetDialogOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDialogOpen.restype = ctypes.c_int
```
## EU_GetDialogOptions

```python
dll.EU_GetDialogOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDialogOptions.restype = ctypes.c_int
```
## EU_SetDialogButtons

```python
dll.EU_SetDialogButtons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDialogButtons.restype = None
```
## EU_TriggerDialogButton

```python
dll.EU_TriggerDialogButton.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerDialogButton.restype = None
```
## EU_GetDialogText

```python
dll.EU_GetDialogText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDialogText.restype = ctypes.c_int
```
## EU_GetDialogButtonText

```python
dll.EU_GetDialogButtonText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDialogButtonText.restype = ctypes.c_int
```
## EU_GetDialogFullState

```python
dll.EU_GetDialogFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDialogFullState.restype = ctypes.c_int
```
## EU_SetDialogButtonCallback

```python
dll.EU_SetDialogButtonCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetDialogButtonCallback.restype = None
```
## EU_SetDrawerOpen

```python
dll.EU_SetDrawerOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerOpen.restype = None
```
## EU_SetDrawerTitle

```python
dll.EU_SetDrawerTitle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDrawerTitle.restype = None
```
## EU_SetDrawerBody

```python
dll.EU_SetDrawerBody.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetDrawerBody.restype = None
```
## EU_SetDrawerPlacement

```python
dll.EU_SetDrawerPlacement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerPlacement.restype = None
```
## EU_SetDrawerOptions

```python
dll.EU_SetDrawerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerOptions.restype = None
```
## EU_SetDrawerAdvancedOptions

```python
dll.EU_SetDrawerAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerAdvancedOptions.restype = None
```
## EU_GetDrawerAdvancedOptions

```python
dll.EU_GetDrawerAdvancedOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDrawerAdvancedOptions.restype = ctypes.c_int
```
## EU_GetDrawerContentParent

```python
dll.EU_GetDrawerContentParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDrawerContentParent.restype = ctypes.c_int
```
## EU_GetDrawerFooterParent

```python
dll.EU_GetDrawerFooterParent.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDrawerFooterParent.restype = ctypes.c_int
```
## EU_SetDrawerBeforeCloseCallback

```python
dll.EU_SetDrawerBeforeCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementBeforeCloseCallback]
dll.EU_SetDrawerBeforeCloseCallback.restype = None
```
## EU_ConfirmDrawerClose

```python
dll.EU_ConfirmDrawerClose.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ConfirmDrawerClose.restype = None
```
## EU_GetDrawerOpen

```python
dll.EU_GetDrawerOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetDrawerOpen.restype = ctypes.c_int
```
## EU_GetDrawerOptions

```python
dll.EU_GetDrawerOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDrawerOptions.restype = ctypes.c_int
```
## EU_SetDrawerAnimation

```python
dll.EU_SetDrawerAnimation.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetDrawerAnimation.restype = None
```
## EU_TriggerDrawerClose

```python
dll.EU_TriggerDrawerClose.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_TriggerDrawerClose.restype = None
```
## EU_GetDrawerText

```python
dll.EU_GetDrawerText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetDrawerText.restype = ctypes.c_int
```
## EU_GetDrawerFullState

```python
dll.EU_GetDrawerFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetDrawerFullState.restype = ctypes.c_int
```
## EU_SetDrawerCloseCallback

```python
dll.EU_SetDrawerCloseCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetDrawerCloseCallback.restype = None
```
## EU_SetTooltipContent

```python
dll.EU_SetTooltipContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetTooltipContent.restype = None
```
## EU_SetTooltipOpen

```python
dll.EU_SetTooltipOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetTooltipOpen.restype = None
```
## EU_SetTooltipOptions

```python
dll.EU_SetTooltipOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTooltipOptions.restype = None
```
## EU_GetTooltipOpen

```python
dll.EU_GetTooltipOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetTooltipOpen.restype = ctypes.c_int
```
## EU_GetTooltipOptions

```python
dll.EU_GetTooltipOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTooltipOptions.restype = ctypes.c_int
```
## EU_SetTooltipBehavior

```python
dll.EU_SetTooltipBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetTooltipBehavior.restype = None
```
## EU_TriggerTooltip

```python
dll.EU_TriggerTooltip.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerTooltip.restype = None
```
## EU_GetTooltipText

```python
dll.EU_GetTooltipText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetTooltipText.restype = ctypes.c_int
```
## EU_GetTooltipFullState

```python
dll.EU_GetTooltipFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetTooltipFullState.restype = ctypes.c_int
```
## EU_SetPopoverOpen

```python
dll.EU_SetPopoverOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverOpen.restype = None
```
## EU_SetPopoverContent

```python
dll.EU_SetPopoverContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopoverContent.restype = None
```
## EU_SetPopoverTitle

```python
dll.EU_SetPopoverTitle.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopoverTitle.restype = None
```
## EU_SetPopoverOptions

```python
dll.EU_SetPopoverOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopoverOptions.restype = None
```
## EU_GetPopoverOpen

```python
dll.EU_GetPopoverOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopoverOpen.restype = ctypes.c_int
```
## EU_GetPopoverOptions

```python
dll.EU_GetPopoverOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopoverOptions.restype = ctypes.c_int
```
## EU_TriggerPopover

```python
dll.EU_TriggerPopover.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerPopover.restype = None
```
## EU_GetPopoverText

```python
dll.EU_GetPopoverText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetPopoverText.restype = ctypes.c_int
```
## EU_GetPopoverFullState

```python
dll.EU_GetPopoverFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopoverFullState.restype = ctypes.c_int
```
## EU_SetPopoverActionCallback

```python
dll.EU_SetPopoverActionCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetPopoverActionCallback.restype = None
```
## EU_SetPopconfirmOpen

```python
dll.EU_SetPopconfirmOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopconfirmOpen.restype = None
```
## EU_SetPopconfirmOptions

```python
dll.EU_SetPopconfirmOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopconfirmOptions.restype = None
```
## EU_SetPopconfirmContent

```python
dll.EU_SetPopconfirmContent.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopconfirmContent.restype = None
```
## EU_SetPopconfirmButtons

```python
dll.EU_SetPopconfirmButtons.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_SetPopconfirmButtons.restype = None
```
## EU_ResetPopconfirmResult

```python
dll.EU_ResetPopconfirmResult.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_ResetPopconfirmResult.restype = None
```
## EU_GetPopconfirmOpen

```python
dll.EU_GetPopconfirmOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopconfirmOpen.restype = ctypes.c_int
```
## EU_GetPopconfirmResult

```python
dll.EU_GetPopconfirmResult.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopconfirmResult.restype = ctypes.c_int
```
## EU_GetPopconfirmOptions

```python
dll.EU_GetPopconfirmOptions.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopconfirmOptions.restype = ctypes.c_int
```
## EU_TriggerPopconfirmResult

```python
dll.EU_TriggerPopconfirmResult.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_TriggerPopconfirmResult.restype = None
```
## EU_GetPopconfirmText

```python
dll.EU_GetPopconfirmText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
dll.EU_GetPopconfirmText.restype = ctypes.c_int
```
## EU_GetPopconfirmFullState

```python
dll.EU_GetPopconfirmFullState.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
dll.EU_GetPopconfirmFullState.restype = ctypes.c_int
```
## EU_SetPopconfirmResultCallback

```python
dll.EU_SetPopconfirmResultCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementValueCallback]
dll.EU_SetPopconfirmResultCallback.restype = None
```
## EU_SetElementClickCallback

```python
dll.EU_SetElementClickCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementClickCallback]
dll.EU_SetElementClickCallback.restype = None
```
## EU_SetElementKeyCallback

```python
dll.EU_SetElementKeyCallback.argtypes = [wintypes.HWND, ctypes.c_int, ElementKeyCallback]
dll.EU_SetElementKeyCallback.restype = None
```
## EU_SetWindowResizeCallback

```python
dll.EU_SetWindowResizeCallback.argtypes = [wintypes.HWND, WindowResizeCallback]
dll.EU_SetWindowResizeCallback.restype = None
```
## EU_SetWindowCloseCallback

```python
dll.EU_SetWindowCloseCallback.argtypes = [wintypes.HWND, WindowCloseCallback]
dll.EU_SetWindowCloseCallback.restype = None
```
## EU_SetDarkMode

```python
dll.EU_SetDarkMode.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetDarkMode.restype = None
```
## EU_SetThemeMode

```python
dll.EU_SetThemeMode.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_SetThemeMode.restype = None
```
## EU_GetThemeMode

```python
dll.EU_GetThemeMode.argtypes = [wintypes.HWND]
dll.EU_GetThemeMode.restype = ctypes.c_int
```
## EU_SetThemeColor

```python
dll.EU_SetThemeColor.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32]
dll.EU_SetThemeColor.restype = ctypes.c_int
```
## EU_ResetTheme

```python
dll.EU_ResetTheme.argtypes = [wintypes.HWND]
dll.EU_ResetTheme.restype = None
```
## EU_InvalidateElement

```python
dll.EU_InvalidateElement.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_InvalidateElement.restype = None
```

## Chrome 高仿外壳 API

### 新增组件

| 导出 | 说明 |
|---|---|
| `EU_CreateIconButton` | 创建透明默认态的工具栏图标按钮，支持 hover/press/checked、徽标、tooltip、dropdown。 |
| `EU_CreateOmnibox` | 创建 Chrome 风格地址栏，支持安全状态、前缀 chip、动作图标、建议列表和提交回调。 |
| `EU_CreateBrowserViewport` | 创建浏览内容占位区，提供空白页、加载中、截图占位、错误页和新标签页状态。 |

### 主要增强导出

## 通用 Popup API

```python
dll.EU_SetPopupAnchorElement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopupAnchorElement.restype = None
dll.EU_SetPopupPlacement.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopupPlacement.restype = None
dll.EU_SetPopupOpen.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopupOpen.restype = None
dll.EU_GetPopupOpen.argtypes = [wintypes.HWND, ctypes.c_int]
dll.EU_GetPopupOpen.restype = ctypes.c_int
dll.EU_SetPopupDismissBehavior.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetPopupDismissBehavior.restype = None
dll.EU_SetElementPopup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.EU_SetElementPopup.restype = None
dll.EU_ClearElementPopup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_ClearElementPopup.restype = None
dll.EU_GetElementPopup.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
dll.EU_GetElementPopup.restype = ctypes.c_int
```

`EU_SetPopup*` 支持 `Popover`、`Menu` 和 `Dropdown`。`EU_SetElementPopup` 的 `trigger`：`0=左键`、`1=右键`、`2=悬停`、`3=聚焦`、`4=手动`。

`EU_SetTabsChromeMode`、`EU_GetTabsChromeMode`、`EU_SetTabsItemChromeState`、`EU_GetTabsItemChromeState`、`EU_SetMenuItemIcon`、`EU_SetMenuItemShortcut`、`EU_SetMenuItemChecked`、`EU_SetPopoverAnchorElement`、`EU_SetPopoverDismissBehavior`、`EU_SetPopupAnchorElement`、`EU_SetPopupPlacement`、`EU_SetPopupOpen`、`EU_GetPopupOpen`、`EU_SetPopupDismissBehavior`、`EU_SetElementPopup`、`EU_ClearElementPopup`、`EU_GetElementPopup`、`EU_SetWindowDragRegion`、`EU_SetContainerFlexLayout`、`EU_SetChromeThemePreset`、`EU_SetThemeToken`、`EU_GetThemeToken`、`EU_SetHighContrastMode`、`EU_SetIncognitoMode`。

易语言命令左侧可使用中文名，例如 `创建工具栏图标按钮`、`创建地址栏`、`创建浏览内容占位区`；右侧 DLL 入口名保持上述 `EU_` 导出名。
## Window Frame 通用窗口框架 API

Python helper 已新增：

```text
create_window_ex(...)
create_borderless_window(...)
create_browser_shell_window(...)
get_window_frame_flags(...)
set_window_frame_flags(...)
set_window_resize_border(...)
get_window_resize_border(...)
set_window_no_drag_region(...)
clear_window_no_drag_regions(...)
set_element_window_command(...)
get_element_window_command(...)
```

底层 DLL 入口为 `EU_CreateWindowEx`、`EU_GetWindowFrameFlags`、`EU_SetWindowFrameFlags`、`EU_SetWindowResizeBorder`、`EU_GetWindowResizeBorder`、`EU_SetWindowNoDragRegion`、`EU_ClearWindowNoDragRegions`、`EU_SetElementWindowCommand`、`EU_GetElementWindowCommand`。
