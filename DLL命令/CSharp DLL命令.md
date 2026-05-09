# new_emoji.dll C# DLL 命令

本文件记录 `new_emoji.dll` 的 C# P/Invoke 声明，按 `src/new_emoji.def` 和 `src/exports.h` 生成。
当前导出命令数量：1253。

通用约定：
- x86 应用加载 `bin/Win32/Release/new_emoji.dll`，x64 应用加载 `bin/x64/Release/new_emoji.dll`。
- 所有导出 API 使用 `CallingConvention.StdCall`。
- `HWND` 使用 `IntPtr`，`Color` 使用 `uint`，颜色格式为 ARGB：`0xAARRGGBB`。
- 文本参数按 UTF-8 字节数组 + 长度传入；示例 helper 可用 `Encoding.UTF8.GetBytes(text)` 生成 `byte[]`。
- 输出指针和数组类参数在本文件中保守使用 `IntPtr` 或 `byte[]`，复杂场景可按实际缓冲区改成 pinned array。
- 回调 delegate 必须由调用方保存引用，避免被 GC 回收。

## 基础 using

```csharp
using System;
using System.Runtime.InteropServices;
using System.Text;
```

## 回调 delegate

```csharp
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void ElementClickCallback(int element_id);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void ElementKeyCallback(int element_id, int vk_code, int key_down, int shift, int ctrl, int alt);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void ElementTextCallback(int element_id, IntPtr utf8, int len);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void ElementValueCallback(int element_id, int value, int range_start, int range_end);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate int ElementBeforeCloseCallback(int element_id, int action);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void TableCellCallback(int table_id, int row, int col, int action, int value);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate int TableVirtualRowCallback(int table_id, int row, IntPtr buffer, int buffer_size);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void DropdownCommandCallback(int element_id, int item_index, IntPtr command_utf8, int command_len);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void MenuSelectCallback(int element_id, int item_index, IntPtr path_utf8, int path_len, IntPtr command_utf8, int command_len);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void WindowResizeCallback(IntPtr hwnd, int width, int height);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void WindowCloseCallback(IntPtr hwnd);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void MessageBoxResultCallback(int messagebox_id, int result);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void MessageBoxExCallback(int messagebox_id, int action, IntPtr value_utf8, int value_len);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate void TreeNodeEventCallback(int element_id, int event_code, int item_index, IntPtr payload_utf8, int payload_len);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate int TreeNodeAllowDragCallback(int element_id, IntPtr key_utf8, int key_len);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate int TreeNodeAllowDropCallback(int element_id, IntPtr drag_key_utf8, int drag_key_len, IntPtr drop_key_utf8, int drop_key_len, int drop_type);
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate int DateDisabledCallback(int id, int yyyymmdd);
```

## 导出声明

## EU_CreateWindow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern IntPtr EU_CreateWindow(byte[] title_bytes, int title_len, int x, int y, int w, int h, uint titlebar_color);
```
## EU_CreateWindowDark

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern IntPtr EU_CreateWindowDark(byte[] title_bytes, int title_len, int x, int y, int w, int h, uint titlebar_color);
```
## EU_DestroyWindow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_DestroyWindow(IntPtr hwnd);
```
## EU_ShowWindow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ShowWindow(IntPtr hwnd, int visible);
```
## EU_RunMessageLoop

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_RunMessageLoop();
```
## EU_SetWindowTitle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWindowTitle(IntPtr hwnd, byte[] bytes, int len);
```
## EU_SetWindowIcon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_SetWindowIcon(IntPtr hwnd, byte[] path_bytes, int path_len);
```
## EU_SetWindowIconFromBytes

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_SetWindowIconFromBytes(IntPtr hwnd, byte[] icon_bytes, int icon_len);
```
## EU_SetWindowBounds

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWindowBounds(IntPtr hwnd, int x, int y, int w, int h);
```
## EU_GetWindowBounds

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetWindowBounds(IntPtr hwnd, IntPtr x, IntPtr y, IntPtr w, IntPtr h);
```
## EU_CreatePanel

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreatePanel(IntPtr hwnd, int parent_id, int x, int y, int w, int h);
```
## EU_CreateButton

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateButton(IntPtr hwnd, int parent_id, byte[] emoji_bytes, int emoji_len, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateEditBox

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateEditBox(IntPtr hwnd, int parent_id, int x, int y, int w, int h);
```
## EU_CreateInfoBox

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateInfoBox(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateText(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateLink

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateLink(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateIcon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateIcon(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateSpace

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSpace(IntPtr hwnd, int parent_id, int x, int y, int w, int h);
```
## EU_CreateContainer

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateContainer(IntPtr hwnd, int parent_id, int x, int y, int w, int h);
```
## EU_CreateHeader

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateHeader(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateAside

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateAside(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateMain

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateMain(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateFooter

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateFooter(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateLayout

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateLayout(IntPtr hwnd, int parent_id, int orientation, int gap, int x, int y, int w, int h);
```
## EU_CreateBorder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateBorder(IntPtr hwnd, int parent_id, int x, int y, int w, int h);
```
## EU_CreateCheckbox

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateCheckbox(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int @checked, int x, int y, int w, int h);
```
## EU_CreateCheckboxGroup

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateCheckboxGroup(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, byte[] checked_bytes, int checked_len, int style_mode, int size, int group_disabled, int min_checked, int max_checked, int x, int y, int w, int h);
```
## EU_CreateRadio

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateRadio(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int @checked, int x, int y, int w, int h);
```
## EU_CreateRadioGroup

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateRadioGroup(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, byte[] value_bytes, int value_len, int style_mode, int size, int group_disabled, int x, int y, int w, int h);
```
## EU_CreateSwitch

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSwitch(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int @checked, int x, int y, int w, int h);
```
## EU_CreateSlider

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSlider(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int min_value, int max_value, int value, int x, int y, int w, int h);
```
## EU_CreateInputNumber

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateInputNumber(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int value, int min_value, int max_value, int step, int x, int y, int w, int h);
```
## EU_CreateInput

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateInput(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, byte[] placeholder_bytes, int placeholder_len, byte[] prefix_bytes, int prefix_len, byte[] suffix_bytes, int suffix_len, int clearable, int x, int y, int w, int h);
```
## EU_CreateInputGroup

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateInputGroup(IntPtr hwnd, int parent_id, byte[] value_bytes, int value_len, byte[] placeholder_bytes, int placeholder_len, int size, int clearable, int password, int show_word_limit, int autosize, int min_rows, int max_rows, int x, int y, int w, int h);
```
## EU_CreateInputTag

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateInputTag(IntPtr hwnd, int parent_id, byte[] tags_bytes, int tags_len, byte[] placeholder_bytes, int placeholder_len, int x, int y, int w, int h);
```
## EU_CreateSelect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSelect(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, byte[] options_bytes, int options_len, int selected_index, int x, int y, int w, int h);
```
## EU_CreateSelectV2

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSelectV2(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, byte[] options_bytes, int options_len, int selected_index, int visible_count, int x, int y, int w, int h);
```
## EU_CreateRate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateRate(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int value, int max_value, int x, int y, int w, int h);
```
## EU_CreateColorPicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateColorPicker(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, uint value, int x, int y, int w, int h);
```
## EU_CreateTag

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTag(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int tag_type, int effect, int closable, int x, int y, int w, int h);
```
## EU_CreateBadge

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateBadge(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, byte[] value_bytes, int value_len, int max_value, int dot, int x, int y, int w, int h);
```
## EU_CreateProgress

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateProgress(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int percentage, int status, int x, int y, int w, int h);
```
## EU_CreateAvatar

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateAvatar(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int shape, int x, int y, int w, int h);
```
## EU_CreateEmpty

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateEmpty(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] desc_bytes, int desc_len, int x, int y, int w, int h);
```
## EU_CreateSkeleton

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSkeleton(IntPtr hwnd, int parent_id, int rows, int animated, int x, int y, int w, int h);
```
## EU_CreateDescriptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDescriptions(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] items_bytes, int items_len, int columns, int bordered, int x, int y, int w, int h);
```
## EU_CreateTable

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTable(IntPtr hwnd, int parent_id, byte[] columns_bytes, int columns_len, byte[] rows_bytes, int rows_len, int striped, int bordered, int x, int y, int w, int h);
```
## EU_CreateCard

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateCard(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len, int shadow, int x, int y, int w, int h);
```
## EU_CreateCollapse

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateCollapse(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int active_index, int accordion, int x, int y, int w, int h);
```
## EU_CreateTimeline

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTimeline(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int x, int y, int w, int h);
```
## EU_CreateStatistic

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateStatistic(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] value_bytes, int value_len, byte[] prefix_bytes, int prefix_len, byte[] suffix_bytes, int suffix_len, int x, int y, int w, int h);
```
## EU_CreateKpiCard

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateKpiCard(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] value_bytes, int value_len, byte[] subtitle_bytes, int subtitle_len, byte[] trend_bytes, int trend_len, int trend_type, int x, int y, int w, int h);
```
## EU_CreateTrend

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTrend(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] value_bytes, int value_len, byte[] percent_bytes, int percent_len, byte[] detail_bytes, int detail_len, int direction, int x, int y, int w, int h);
```
## EU_CreateStatusDot

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateStatusDot(IntPtr hwnd, int parent_id, byte[] label_bytes, int label_len, byte[] desc_bytes, int desc_len, int status, int x, int y, int w, int h);
```
## EU_CreateGauge

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateGauge(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, int value, byte[] caption_bytes, int caption_len, int status, int x, int y, int w, int h);
```
## EU_CreateRingProgress

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateRingProgress(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, int value, byte[] label_bytes, int label_len, int status, int x, int y, int w, int h);
```
## EU_CreateBulletProgress

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateBulletProgress(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] desc_bytes, int desc_len, int value, int target, int status, int x, int y, int w, int h);
```
## EU_CreateLineChart

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateLineChart(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] points_bytes, int points_len, int chart_style, int x, int y, int w, int h);
```
## EU_CreateBarChart

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateBarChart(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] bars_bytes, int bars_len, int orientation, int x, int y, int w, int h);
```
## EU_CreateDonutChart

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDonutChart(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] slices_bytes, int slices_len, int active_index, int x, int y, int w, int h);
```
## EU_CreateDivider

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDivider(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int direction, int content_position, int x, int y, int w, int h);
```
## EU_CreateCalendar

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateCalendar(IntPtr hwnd, int parent_id, int year, int month, int selected_day, int x, int y, int w, int h);
```
## EU_CreateTree

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTree(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int selected_index, int x, int y, int w, int h);
```
## EU_CreateTreeSelect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTreeSelect(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int selected_index, int x, int y, int w, int h);
```
## EU_CreateTransfer

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTransfer(IntPtr hwnd, int parent_id, byte[] left_bytes, int left_len, byte[] right_bytes, int right_len, int x, int y, int w, int h);
```
## EU_CreateAutocomplete

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateAutocomplete(IntPtr hwnd, int parent_id, byte[] value_bytes, int value_len, byte[] suggestions_bytes, int suggestions_len, int x, int y, int w, int h);
```
## EU_CreateMentions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateMentions(IntPtr hwnd, int parent_id, byte[] value_bytes, int value_len, byte[] suggestions_bytes, int suggestions_len, int x, int y, int w, int h);
```
## EU_CreateCascader

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateCascader(IntPtr hwnd, int parent_id, byte[] options_bytes, int options_len, byte[] selected_bytes, int selected_len, int x, int y, int w, int h);
```
## EU_CreateDatePicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDatePicker(IntPtr hwnd, int parent_id, int year, int month, int selected_day, int x, int y, int w, int h);
```
## EU_CreateTimePicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTimePicker(IntPtr hwnd, int parent_id, int hour, int minute, int x, int y, int w, int h);
```
## EU_CreateDateTimePicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDateTimePicker(IntPtr hwnd, int parent_id, int year, int month, int day, int hour, int minute, int x, int y, int w, int h);
```
## EU_CreateTimeSelect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTimeSelect(IntPtr hwnd, int parent_id, int hour, int minute, int x, int y, int w, int h);
```
## EU_CreateDropdown

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDropdown(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, byte[] items_bytes, int items_len, int selected_index, int x, int y, int w, int h);
```
## EU_CreateMenu

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateMenu(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int active_index, int orientation, int x, int y, int w, int h);
```
## EU_CreateAnchor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateAnchor(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int active_index, int x, int y, int w, int h);
```
## EU_CreateBacktop

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateBacktop(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int x, int y, int w, int h);
```
## EU_CreateSegmented

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSegmented(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int active_index, int x, int y, int w, int h);
```
## EU_CreatePageHeader

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreatePageHeader(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] subtitle_bytes, int subtitle_len, byte[] back_bytes, int back_len, int x, int y, int w, int h);
```
## EU_CreateAffix

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateAffix(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len, int offset, int x, int y, int w, int h);
```
## EU_CreateWatermark

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateWatermark(IntPtr hwnd, int parent_id, byte[] content_bytes, int content_len, int gap_x, int gap_y, int x, int y, int w, int h);
```
## EU_CreateTour

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTour(IntPtr hwnd, int parent_id, byte[] steps_bytes, int steps_len, int active_index, int open, int x, int y, int w, int h);
```
## EU_CreateImage

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateImage(IntPtr hwnd, int parent_id, byte[] src_bytes, int src_len, byte[] alt_bytes, int alt_len, int fit, int x, int y, int w, int h);
```
## EU_CreateCarousel

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateCarousel(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int active_index, int indicator_position, int x, int y, int w, int h);
```
## EU_CreateUpload

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateUpload(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] tip_bytes, int tip_len, byte[] files_bytes, int files_len, int x, int y, int w, int h);
```
## EU_CreateInfiniteScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateInfiniteScroll(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int x, int y, int w, int h);
```
## EU_CreateBreadcrumb

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateBreadcrumb(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, byte[] separator_bytes, int separator_len, int current_index, int x, int y, int w, int h);
```
## EU_CreateTabs

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTabs(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int active_index, int tab_type, int x, int y, int w, int h);
```
## EU_CreatePagination

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreatePagination(IntPtr hwnd, int parent_id, int total, int page_size, int current_page, int x, int y, int w, int h);
```
## EU_CreateSteps

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateSteps(IntPtr hwnd, int parent_id, byte[] items_bytes, int items_len, int active_index, int x, int y, int w, int h);
```
## EU_CreateAlert

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateAlert(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] desc_bytes, int desc_len, int alert_type, int effect, int closable, int x, int y, int w, int h);
```
## EU_CreateAlertEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateAlertEx(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] desc_bytes, int desc_len, int alert_type, int effect, int closable, int show_icon, int center, int wrap_description, byte[] close_text_bytes, int close_text_len, int x, int y, int w, int h);
```
## EU_CreateResult

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateResult(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] subtitle_bytes, int subtitle_len, int result_type, int x, int y, int w, int h);
```
## EU_CreateNotification

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateNotification(IntPtr hwnd, int parent_id, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len, int notify_type, int closable, int x, int y, int w, int h);
```
## EU_CreateLoading

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateLoading(IntPtr hwnd, int parent_id, byte[] text_bytes, int text_len, int active, int x, int y, int w, int h);
```
## EU_CreateDialog

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDialog(IntPtr hwnd, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len, int modal, int closable, int w, int h);
```
## EU_SetDialogAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogAdvancedOptions(IntPtr hwnd, int element_id, int width_mode, int width_value, int center, int footer_center, int content_padding, int footer_height);
```
## EU_GetDialogAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogAdvancedOptions(IntPtr hwnd, int element_id, IntPtr width_mode, IntPtr width_value, IntPtr center, IntPtr footer_center, IntPtr content_padding, IntPtr footer_height, IntPtr content_parent_id, IntPtr footer_parent_id, IntPtr close_pending);
```
## EU_GetDialogContentParent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogContentParent(IntPtr hwnd, int element_id);
```
## EU_GetDialogFooterParent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogFooterParent(IntPtr hwnd, int element_id);
```
## EU_SetDialogBeforeCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogBeforeCloseCallback(IntPtr hwnd, int element_id, ElementBeforeCloseCallback cb);
```
## EU_ConfirmDialogClose

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ConfirmDialogClose(IntPtr hwnd, int element_id, int allow);
```
## EU_CreateDrawer

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDrawer(IntPtr hwnd, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len, int placement, int modal, int closable, int size);
```
## EU_CreateTooltip

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateTooltip(IntPtr hwnd, int parent_id, byte[] label_bytes, int label_len, byte[] content_bytes, int content_len, int placement, int x, int y, int w, int h);
```
## EU_SetTooltipAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTooltipAdvancedOptions(IntPtr hwnd, int element_id, int placement, int effect, int disabled, int show_arrow, int offset, int max_width);
```
## EU_GetTooltipAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTooltipAdvancedOptions(IntPtr hwnd, int element_id, IntPtr placement, IntPtr effect, IntPtr disabled, IntPtr show_arrow, IntPtr offset, IntPtr max_width);
```
## EU_CreatePopover

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreatePopover(IntPtr hwnd, int parent_id, byte[] label_bytes, int label_len, byte[] title_bytes, int title_len, byte[] content_bytes, int content_len, int placement, int x, int y, int w, int h);
```
## EU_SetPopoverAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopoverAdvancedOptions(IntPtr hwnd, int element_id, int placement, int open, int popup_width, int popup_height, int closable);
```
## EU_SetPopoverBehavior

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopoverBehavior(IntPtr hwnd, int element_id, int trigger_mode, int close_on_outside, int show_arrow, int offset);
```
## EU_GetPopoverBehavior

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopoverBehavior(IntPtr hwnd, int element_id, IntPtr trigger_mode, IntPtr close_on_outside, IntPtr show_arrow, IntPtr offset);
```
## EU_GetPopoverContentParent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopoverContentParent(IntPtr hwnd, int element_id);
```
## EU_CreatePopconfirm

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreatePopconfirm(IntPtr hwnd, int parent_id, byte[] label_bytes, int label_len, byte[] title_bytes, int title_len, byte[] content_bytes, int content_len, byte[] confirm_bytes, int confirm_len, byte[] cancel_bytes, int cancel_len, int placement, int x, int y, int w, int h);
```
## EU_SetPopconfirmAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopconfirmAdvancedOptions(IntPtr hwnd, int element_id, int placement, int open, int popup_width, int popup_height, int trigger_mode, int close_on_outside, int show_arrow, int offset);
```
## EU_SetPopconfirmIcon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopconfirmIcon(IntPtr hwnd, int element_id, byte[] icon_bytes, int icon_len, uint icon_color, int visible);
```
## EU_GetPopconfirmIcon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopconfirmIcon(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size, IntPtr icon_color, IntPtr visible);
```
## EU_ShowMessage

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ShowMessage(IntPtr hwnd, byte[] text_bytes, int text_len, int message_type, int closable, int center, int rich, int duration_ms, int offset);
```
## EU_ShowNotification

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ShowNotification(IntPtr hwnd, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len, int notify_type, int closable, int duration_ms, int placement, int offset, int rich, int w, int h);
```
## EU_ShowMessageBox

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ShowMessageBox(IntPtr hwnd, byte[] title_bytes, int title_len, byte[] text_bytes, int text_len, byte[] confirm_bytes, int confirm_len, MessageBoxResultCallback cb);
```
## EU_ShowConfirmBox

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ShowConfirmBox(IntPtr hwnd, byte[] title_bytes, int title_len, byte[] text_bytes, int text_len, byte[] confirm_bytes, int confirm_len, byte[] cancel_bytes, int cancel_len, MessageBoxResultCallback cb);
```
## EU_ShowMessageBoxEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ShowMessageBoxEx(IntPtr hwnd, byte[] title_bytes, int title_len, byte[] text_bytes, int text_len, byte[] confirm_bytes, int confirm_len, byte[] cancel_bytes, int cancel_len, int box_type, int show_cancel, int center, int rich, int distinguish_cancel_and_close, MessageBoxExCallback cb);
```
## EU_ShowPromptBox

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ShowPromptBox(IntPtr hwnd, byte[] title_bytes, int title_len, byte[] text_bytes, int text_len, byte[] placeholder_bytes, int placeholder_len, byte[] value_bytes, int value_len, byte[] pattern_bytes, int pattern_len, byte[] error_bytes, int error_len, byte[] confirm_bytes, int confirm_len, byte[] cancel_bytes, int cancel_len, int box_type, int center, int rich, int distinguish_cancel_and_close, MessageBoxExCallback cb);
```
## EU_SetElementText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementText(IntPtr hwnd, int element_id, byte[] bytes, int len);
```
## EU_GetElementText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetElementText(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetElementBounds

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementBounds(IntPtr hwnd, int element_id, int x, int y, int w, int h);
```
## EU_GetElementBounds

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetElementBounds(IntPtr hwnd, int element_id, IntPtr x, IntPtr y, IntPtr w, IntPtr h);
```
## EU_SetElementVisible

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementVisible(IntPtr hwnd, int element_id, int visible);
```
## EU_GetElementVisible

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetElementVisible(IntPtr hwnd, int element_id);
```
## EU_SetElementEnabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementEnabled(IntPtr hwnd, int element_id, int enabled);
```
## EU_GetElementEnabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetElementEnabled(IntPtr hwnd, int element_id);
```
## EU_SetElementColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementColor(IntPtr hwnd, int element_id, uint bg, uint fg);
```
## EU_SetElementFont

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementFont(IntPtr hwnd, int element_id, byte[] font_bytes, int font_len, float size);
```
## EU_SetTextOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTextOptions(IntPtr hwnd, int element_id, int align, int valign, int wrap, int ellipsis);
```
## EU_GetTextOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTextOptions(IntPtr hwnd, int element_id, IntPtr align, IntPtr valign, IntPtr wrap, IntPtr ellipsis);
```
## EU_SetLinkOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLinkOptions(IntPtr hwnd, int element_id, int type, int underline, int auto_open, int visited);
```
## EU_GetLinkOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLinkOptions(IntPtr hwnd, int element_id, IntPtr type, IntPtr underline, IntPtr auto_open, IntPtr visited);
```
## EU_SetLinkContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLinkContent(IntPtr hwnd, int element_id, byte[] prefix_bytes, int prefix_len, byte[] suffix_bytes, int suffix_len, byte[] href_bytes, int href_len, byte[] target_bytes, int target_len);
```
## EU_GetLinkContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLinkContent(IntPtr hwnd, int element_id, byte[] prefix_buffer, int prefix_buffer_size, byte[] suffix_buffer, int suffix_buffer_size, byte[] href_buffer, int href_buffer_size, byte[] target_buffer, int target_buffer_size);
```
## EU_SetLinkVisited

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLinkVisited(IntPtr hwnd, int element_id, int visited);
```
## EU_GetLinkVisited

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLinkVisited(IntPtr hwnd, int element_id);
```
## EU_SetIconOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetIconOptions(IntPtr hwnd, int element_id, float scale, float rotation_degrees);
```
## EU_GetIconOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetIconOptions(IntPtr hwnd, int element_id, IntPtr scale, IntPtr rotation_degrees);
```
## EU_SetPanelStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPanelStyle(IntPtr hwnd, int element_id, uint bg, uint border, float border_width, float radius, int padding);
```
## EU_GetPanelStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPanelStyle(IntPtr hwnd, int element_id, IntPtr bg, IntPtr border, IntPtr border_width, IntPtr radius, IntPtr padding);
```
## EU_SetPanelLayout

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPanelLayout(IntPtr hwnd, int element_id, int fill_parent, int content_layout);
```
## EU_GetPanelLayout

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPanelLayout(IntPtr hwnd, int element_id, IntPtr fill_parent, IntPtr content_layout);
```
## EU_SetContainerLayout

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetContainerLayout(IntPtr hwnd, int element_id, int enabled, int direction, int gap);
```
## EU_GetContainerLayout

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetContainerLayout(IntPtr hwnd, int element_id, IntPtr enabled, IntPtr direction, IntPtr gap, IntPtr actual_direction);
```
## EU_SetContainerRegionTextOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetContainerRegionTextOptions(IntPtr hwnd, int element_id, int align, int valign);
```
## EU_GetContainerRegionTextOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetContainerRegionTextOptions(IntPtr hwnd, int element_id, IntPtr align, IntPtr valign, IntPtr role);
```
## EU_SetLayoutOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLayoutOptions(IntPtr hwnd, int element_id, int orientation, int gap, int stretch, int align, int wrap);
```
## EU_GetLayoutOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLayoutOptions(IntPtr hwnd, int element_id, IntPtr orientation, IntPtr gap, IntPtr stretch, IntPtr align, IntPtr wrap);
```
## EU_SetLayoutChildWeight

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLayoutChildWeight(IntPtr hwnd, int layout_id, int child_id, int weight);
```
## EU_GetLayoutChildWeight

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLayoutChildWeight(IntPtr hwnd, int layout_id, int child_id);
```
## EU_SetBorderOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBorderOptions(IntPtr hwnd, int element_id, int sides, uint color, float width, float radius, byte[] title_bytes, int title_len);
```
## EU_GetBorderOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBorderOptions(IntPtr hwnd, int element_id, IntPtr sides, IntPtr color, IntPtr width, IntPtr radius);
```
## EU_SetBorderDashed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBorderDashed(IntPtr hwnd, int element_id, int dashed);
```
## EU_GetBorderDashed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBorderDashed(IntPtr hwnd, int element_id);
```
## EU_SetInfoBoxText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfoBoxText(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len);
```
## EU_SetInfoBoxOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfoBoxOptions(IntPtr hwnd, int element_id, int type, int closable, uint accent, byte[] icon_bytes, int icon_len);
```
## EU_SetInfoBoxClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfoBoxClosed(IntPtr hwnd, int element_id, int closed);
```
## EU_GetInfoBoxClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInfoBoxClosed(IntPtr hwnd, int element_id);
```
## EU_GetInfoBoxPreferredHeight

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInfoBoxPreferredHeight(IntPtr hwnd, int element_id);
```
## EU_SetSpaceSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSpaceSize(IntPtr hwnd, int element_id, int w, int h);
```
## EU_GetSpaceSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSpaceSize(IntPtr hwnd, int element_id, IntPtr w, IntPtr h);
```
## EU_SetDividerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDividerOptions(IntPtr hwnd, int element_id, int direction, int content_position, uint color, float width, int dashed, byte[] text_bytes, int text_len);
```
## EU_GetDividerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDividerOptions(IntPtr hwnd, int element_id, IntPtr direction, IntPtr content_position, IntPtr color, IntPtr width, IntPtr dashed);
```
## EU_SetDividerSpacing

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDividerSpacing(IntPtr hwnd, int element_id, int margin, int gap);
```
## EU_GetDividerSpacing

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDividerSpacing(IntPtr hwnd, int element_id, IntPtr margin, IntPtr gap);
```
## EU_SetDividerLineStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDividerLineStyle(IntPtr hwnd, int element_id, int line_style);
```
## EU_GetDividerLineStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDividerLineStyle(IntPtr hwnd, int element_id, IntPtr line_style);
```
## EU_SetDividerContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDividerContent(IntPtr hwnd, int element_id, byte[] icon_bytes, int icon_len, byte[] text_bytes, int text_len);
```
## EU_GetDividerContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDividerContent(IntPtr hwnd, int element_id, byte[] icon_buffer, int icon_buffer_size, byte[] text_buffer, int text_buffer_size);
```
## EU_SetButtonEmoji

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetButtonEmoji(IntPtr hwnd, int element_id, byte[] bytes, int len);
```
## EU_SetButtonVariant

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetButtonVariant(IntPtr hwnd, int element_id, int variant);
```
## EU_GetButtonState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetButtonState(IntPtr hwnd, int element_id, IntPtr pressed, IntPtr focused, IntPtr variant);
```
## EU_SetButtonOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetButtonOptions(IntPtr hwnd, int element_id, int variant, int plain, int round, int circle, int loading, int size);
```
## EU_GetButtonOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetButtonOptions(IntPtr hwnd, int element_id, IntPtr variant, IntPtr plain, IntPtr round, IntPtr circle, IntPtr loading, IntPtr size);
```
## EU_SetEditBoxText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEditBoxText(IntPtr hwnd, int element_id, byte[] bytes, int len);
```
## EU_SetEditBoxOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEditBoxOptions(IntPtr hwnd, int element_id, int @readonly, int password, int multiline, uint focus_border, byte[] placeholder_bytes, int placeholder_len);
```
## EU_GetEditBoxOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetEditBoxOptions(IntPtr hwnd, int element_id, IntPtr @readonly, IntPtr password, IntPtr multiline, IntPtr focus_border);
```
## EU_GetEditBoxState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetEditBoxState(IntPtr hwnd, int element_id, IntPtr cursor, IntPtr sel_start, IntPtr sel_end, IntPtr text_length);
```
## EU_GetEditBoxText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetEditBoxText(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetEditBoxScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEditBoxScroll(IntPtr hwnd, int element_id, int scroll_y);
```
## EU_GetEditBoxScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetEditBoxScroll(IntPtr hwnd, int element_id, IntPtr scroll_y, IntPtr max_scroll_y, IntPtr content_height, IntPtr viewport_height);
```
## EU_SetEditBoxTextCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEditBoxTextCallback(IntPtr hwnd, int element_id, ElementTextCallback cb);
```
## EU_SetElementFocus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementFocus(IntPtr hwnd, int element_id);
```
## EU_SetCheckboxChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCheckboxChecked(IntPtr hwnd, int element_id, int @checked);
```
## EU_GetCheckboxChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCheckboxChecked(IntPtr hwnd, int element_id);
```
## EU_SetCheckboxIndeterminate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCheckboxIndeterminate(IntPtr hwnd, int element_id, int indeterminate);
```
## EU_GetCheckboxIndeterminate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCheckboxIndeterminate(IntPtr hwnd, int element_id);
```
## EU_SetCheckboxOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCheckboxOptions(IntPtr hwnd, int element_id, int border, int size);
```
## EU_GetCheckboxOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCheckboxOptions(IntPtr hwnd, int element_id, IntPtr border, IntPtr size);
```
## EU_SetCheckboxGroupItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCheckboxGroupItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetCheckboxGroupValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCheckboxGroupValue(IntPtr hwnd, int element_id, byte[] values_bytes, int values_len);
```
## EU_GetCheckboxGroupValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCheckboxGroupValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetCheckboxGroupOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCheckboxGroupOptions(IntPtr hwnd, int element_id, int group_disabled, int style_mode, int size, int min_checked, int max_checked);
```
## EU_GetCheckboxGroupOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCheckboxGroupOptions(IntPtr hwnd, int element_id, IntPtr group_disabled, IntPtr style_mode, IntPtr size, IntPtr min_checked, IntPtr max_checked);
```
## EU_GetCheckboxGroupState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCheckboxGroupState(IntPtr hwnd, int element_id, IntPtr checked_count, IntPtr item_count, IntPtr disabled_count, IntPtr group_disabled, IntPtr style_mode, IntPtr size, IntPtr min_checked, IntPtr max_checked, IntPtr hover_index, IntPtr press_index, IntPtr focus_index, IntPtr last_action);
```
## EU_SetCheckboxGroupChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCheckboxGroupChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetRadioChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioChecked(IntPtr hwnd, int element_id, int @checked);
```
## EU_GetRadioChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioChecked(IntPtr hwnd, int element_id);
```
## EU_SetRadioGroup

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioGroup(IntPtr hwnd, int element_id, byte[] group_bytes, int group_len);
```
## EU_GetRadioGroup

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioGroup(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetRadioValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_GetRadioValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetRadioOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioOptions(IntPtr hwnd, int element_id, int border, int size);
```
## EU_GetRadioOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioOptions(IntPtr hwnd, int element_id, IntPtr border, IntPtr size);
```
## EU_SetRadioGroupItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioGroupItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetRadioGroupValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioGroupValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_GetRadioGroupValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioGroupValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetRadioGroupSelectedIndex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioGroupSelectedIndex(IntPtr hwnd, int element_id);
```
## EU_SetRadioGroupOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioGroupOptions(IntPtr hwnd, int element_id, int group_disabled, int style_mode, int size);
```
## EU_GetRadioGroupOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioGroupOptions(IntPtr hwnd, int element_id, IntPtr group_disabled, IntPtr style_mode, IntPtr size);
```
## EU_GetRadioGroupState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRadioGroupState(IntPtr hwnd, int element_id, IntPtr selected_index, IntPtr item_count, IntPtr disabled_count, IntPtr group_disabled, IntPtr style_mode, IntPtr size, IntPtr hover_index, IntPtr press_index, IntPtr last_action);
```
## EU_SetRadioGroupChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRadioGroupChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetSwitchChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSwitchChecked(IntPtr hwnd, int element_id, int @checked);
```
## EU_GetSwitchChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSwitchChecked(IntPtr hwnd, int element_id);
```
## EU_SetSwitchLoading

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSwitchLoading(IntPtr hwnd, int element_id, int loading);
```
## EU_GetSwitchLoading

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSwitchLoading(IntPtr hwnd, int element_id);
```
## EU_SetSwitchTexts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSwitchTexts(IntPtr hwnd, int element_id, byte[] active_bytes, int active_len, byte[] inactive_bytes, int inactive_len);
```
## EU_GetSwitchOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSwitchOptions(IntPtr hwnd, int element_id, IntPtr @checked, IntPtr loading, IntPtr has_active_text, IntPtr has_inactive_text);
```
## EU_SetSwitchActiveColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSwitchActiveColor(IntPtr hwnd, int element_id, uint color);
```
## EU_GetSwitchActiveColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern uint EU_GetSwitchActiveColor(IntPtr hwnd, int element_id);
```
## EU_SetSwitchInactiveColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSwitchInactiveColor(IntPtr hwnd, int element_id, uint color);
```
## EU_GetSwitchInactiveColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern uint EU_GetSwitchInactiveColor(IntPtr hwnd, int element_id);
```
## EU_SetSwitchValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSwitchValue(IntPtr hwnd, int element_id, int value);
```
## EU_GetSwitchValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSwitchValue(IntPtr hwnd, int element_id);
```
## EU_SetSwitchSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSwitchSize(IntPtr hwnd, int element_id, int size);
```
## EU_GetSwitchSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSwitchSize(IntPtr hwnd, int element_id);
```
## EU_SetSliderRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSliderRange(IntPtr hwnd, int element_id, int min_value, int max_value);
```
## EU_SetSliderValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSliderValue(IntPtr hwnd, int element_id, int value);
```
## EU_GetSliderValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSliderValue(IntPtr hwnd, int element_id);
```
## EU_SetSliderOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSliderOptions(IntPtr hwnd, int element_id, int step, int show_tooltip);
```
## EU_GetSliderStep

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSliderStep(IntPtr hwnd, int element_id);
```
## EU_GetSliderOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSliderOptions(IntPtr hwnd, int element_id, IntPtr min_value, IntPtr max_value, IntPtr step, IntPtr show_tooltip);
```
## EU_SetSliderRangeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSliderRangeValue(IntPtr hwnd, int element_id, int start_value, int end_value);
```
## EU_GetSliderRangeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSliderRangeValue(IntPtr hwnd, int element_id, IntPtr start_value, IntPtr end_value);
```
## EU_SetSliderRangeMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSliderRangeMode(IntPtr hwnd, int element_id, int enabled, int start_value, int end_value);
```
## EU_GetSliderRangeMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSliderRangeMode(IntPtr hwnd, int element_id, IntPtr enabled, IntPtr start_value, IntPtr end_value);
```
## EU_SetSliderValueCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSliderValueCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetInputNumberRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputNumberRange(IntPtr hwnd, int element_id, int min_value, int max_value);
```
## EU_SetInputNumberStep

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputNumberStep(IntPtr hwnd, int element_id, int step);
```
## EU_SetInputNumberValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputNumberValue(IntPtr hwnd, int element_id, int value);
```
## EU_GetInputNumberValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputNumberValue(IntPtr hwnd, int element_id);
```
## EU_GetInputNumberCanStep

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputNumberCanStep(IntPtr hwnd, int element_id, int delta);
```
## EU_GetInputNumberOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputNumberOptions(IntPtr hwnd, int element_id, IntPtr min_value, IntPtr max_value, IntPtr step);
```
## EU_SetInputNumberPrecision

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputNumberPrecision(IntPtr hwnd, int element_id, int precision);
```
## EU_GetInputNumberPrecision

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputNumberPrecision(IntPtr hwnd, int element_id);
```
## EU_SetInputNumberText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_SetInputNumberText(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_GetInputNumberText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputNumberText(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetInputNumberState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputNumberState(IntPtr hwnd, int element_id, IntPtr precision, IntPtr editing, IntPtr valid, IntPtr can_decrease, IntPtr can_increase);
```
## EU_SetInputNumberValueCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputNumberValueCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetInputNumberStepStrictly

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputNumberStepStrictly(IntPtr hwnd, int element_id, int strict);
```
## EU_GetInputNumberStepStrictly

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputNumberStepStrictly(IntPtr hwnd, int element_id);
```
## EU_SetInputValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_GetInputValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetInputPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputPlaceholder(IntPtr hwnd, int element_id, byte[] placeholder_bytes, int placeholder_len);
```
## EU_SetInputAffixes

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputAffixes(IntPtr hwnd, int element_id, byte[] prefix_bytes, int prefix_len, byte[] suffix_bytes, int suffix_len);
```
## EU_SetInputIcons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputIcons(IntPtr hwnd, int element_id, byte[] prefix_icon_bytes, int prefix_icon_len, byte[] suffix_icon_bytes, int suffix_icon_len);
```
## EU_GetInputIcons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputIcons(IntPtr hwnd, int element_id, byte[] prefix_icon_buffer, int prefix_icon_buffer_size, byte[] suffix_icon_buffer, int suffix_icon_buffer_size);
```
## EU_SetInputClearable

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputClearable(IntPtr hwnd, int element_id, int clearable);
```
## EU_SetInputOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputOptions(IntPtr hwnd, int element_id, int @readonly, int password, int multiline, int validate_state);
```
## EU_SetInputVisualOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputVisualOptions(IntPtr hwnd, int element_id, int size, int show_password_toggle, int show_word_limit, int autosize, int min_rows, int max_rows);
```
## EU_GetInputVisualOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputVisualOptions(IntPtr hwnd, int element_id, IntPtr size, IntPtr show_password_toggle, IntPtr show_word_limit, IntPtr autosize, IntPtr min_rows, IntPtr max_rows);
```
## EU_SetInputSelection

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputSelection(IntPtr hwnd, int element_id, int start, int end);
```
## EU_GetInputSelection

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputSelection(IntPtr hwnd, int element_id, IntPtr start, IntPtr end);
```
## EU_SetInputContextMenuEnabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputContextMenuEnabled(IntPtr hwnd, int element_id, int enabled);
```
## EU_GetInputContextMenuEnabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputContextMenuEnabled(IntPtr hwnd, int element_id);
```
## EU_GetInputState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputState(IntPtr hwnd, int element_id, IntPtr cursor, IntPtr length, IntPtr clearable, IntPtr @readonly, IntPtr password, IntPtr multiline, IntPtr validate_state);
```
## EU_SetInputScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputScroll(IntPtr hwnd, int element_id, int scroll_y);
```
## EU_GetInputScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputScroll(IntPtr hwnd, int element_id, IntPtr scroll_y, IntPtr max_scroll_y, IntPtr content_height, IntPtr viewport_height);
```
## EU_SetInputMaxLength

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputMaxLength(IntPtr hwnd, int element_id, int max_length);
```
## EU_GetInputMaxLength

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputMaxLength(IntPtr hwnd, int element_id);
```
## EU_SetInputTextCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputTextCallback(IntPtr hwnd, int element_id, ElementTextCallback cb);
```
## EU_SetInputGroupValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputGroupValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_GetInputGroupValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputGroupValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetInputGroupOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputGroupOptions(IntPtr hwnd, int element_id, int size, int clearable, int password, int show_word_limit, int autosize, int min_rows, int max_rows);
```
## EU_GetInputGroupOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputGroupOptions(IntPtr hwnd, int element_id, IntPtr size, IntPtr clearable, IntPtr password, IntPtr show_word_limit, IntPtr autosize, IntPtr min_rows, IntPtr max_rows);
```
## EU_SetInputGroupTextAddon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputGroupTextAddon(IntPtr hwnd, int element_id, int side, byte[] text_bytes, int text_len);
```
## EU_SetInputGroupButtonAddon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputGroupButtonAddon(IntPtr hwnd, int element_id, int side, byte[] emoji_bytes, int emoji_len, byte[] text_bytes, int text_len, int variant);
```
## EU_SetInputGroupSelectAddon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputGroupSelectAddon(IntPtr hwnd, int element_id, int side, byte[] items_bytes, int items_len, int selected_index, byte[] placeholder_bytes, int placeholder_len);
```
## EU_ClearInputGroupAddon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearInputGroupAddon(IntPtr hwnd, int element_id, int side);
```
## EU_GetInputGroupInputElementId

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputGroupInputElementId(IntPtr hwnd, int element_id);
```
## EU_GetInputGroupAddonElementId

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputGroupAddonElementId(IntPtr hwnd, int element_id, int side);
```
## EU_SetInputTagTags

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputTagTags(IntPtr hwnd, int element_id, byte[] tags_bytes, int tags_len);
```
## EU_SetInputTagPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputTagPlaceholder(IntPtr hwnd, int element_id, byte[] placeholder_bytes, int placeholder_len);
```
## EU_SetInputTagOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputTagOptions(IntPtr hwnd, int element_id, int max_count, int allow_duplicates);
```
## EU_GetInputTagCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputTagCount(IntPtr hwnd, int element_id);
```
## EU_GetInputTagOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputTagOptions(IntPtr hwnd, int element_id, IntPtr max_count, IntPtr allow_duplicates);
```
## EU_AddInputTagItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_AddInputTagItem(IntPtr hwnd, int element_id, byte[] tag_bytes, int tag_len);
```
## EU_RemoveInputTagItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_RemoveInputTagItem(IntPtr hwnd, int element_id, int tag_index);
```
## EU_SetInputTagInputValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputTagInputValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_GetInputTagInputValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputTagInputValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetInputTagItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInputTagItem(IntPtr hwnd, int element_id, int tag_index, byte[] buffer, int buffer_size);
```
## EU_SetInputTagChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInputTagChangeCallback(IntPtr hwnd, int element_id, ElementTextCallback cb);
```
## EU_SetSelectOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectOptions(IntPtr hwnd, int element_id, byte[] options_bytes, int options_len);
```
## EU_SetSelectIndex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectIndex(IntPtr hwnd, int element_id, int index);
```
## EU_GetSelectIndex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectIndex(IntPtr hwnd, int element_id);
```
## EU_SetSelectOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectOpen(IntPtr hwnd, int element_id, int open);
```
## EU_GetSelectOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectOpen(IntPtr hwnd, int element_id);
```
## EU_SetSelectSearch

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectSearch(IntPtr hwnd, int element_id, byte[] search_bytes, int search_len);
```
## EU_SetSelectOptionDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectOptionDisabled(IntPtr hwnd, int element_id, int option_index, int disabled);
```
## EU_SetSelectOptionAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectOptionAlignment(IntPtr hwnd, int element_id, int alignment);
```
## EU_GetSelectOptionAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectOptionAlignment(IntPtr hwnd, int element_id);
```
## EU_SetSelectValueAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectValueAlignment(IntPtr hwnd, int element_id, int alignment);
```
## EU_GetSelectValueAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectValueAlignment(IntPtr hwnd, int element_id);
```
## EU_GetSelectOptionCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectOptionCount(IntPtr hwnd, int element_id);
```
## EU_GetSelectMatchedCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectMatchedCount(IntPtr hwnd, int element_id);
```
## EU_GetSelectOptionDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectOptionDisabled(IntPtr hwnd, int element_id, int option_index);
```
## EU_SetSelectMultiple

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectMultiple(IntPtr hwnd, int element_id, int multiple);
```
## EU_GetSelectMultiple

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectMultiple(IntPtr hwnd, int element_id);
```
## EU_SetSelectSelectedIndices

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectSelectedIndices(IntPtr hwnd, int element_id, byte[] indices_bytes, int indices_len);
```
## EU_GetSelectSelectedCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectSelectedCount(IntPtr hwnd, int element_id);
```
## EU_GetSelectSelectedAt

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectSelectedAt(IntPtr hwnd, int element_id, int position);
```
## EU_SetSelectChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetSelectV2Options

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2Options(IntPtr hwnd, int element_id, byte[] options_bytes, int options_len);
```
## EU_SetSelectV2Index

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2Index(IntPtr hwnd, int element_id, int index);
```
## EU_SetSelectV2VisibleCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2VisibleCount(IntPtr hwnd, int element_id, int visible_count);
```
## EU_GetSelectV2Index

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2Index(IntPtr hwnd, int element_id);
```
## EU_GetSelectV2VisibleCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2VisibleCount(IntPtr hwnd, int element_id);
```
## EU_SetSelectV2Open

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2Open(IntPtr hwnd, int element_id, int open);
```
## EU_GetSelectV2Open

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2Open(IntPtr hwnd, int element_id);
```
## EU_SetSelectV2Search

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2Search(IntPtr hwnd, int element_id, byte[] search_bytes, int search_len);
```
## EU_SetSelectV2OptionDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2OptionDisabled(IntPtr hwnd, int element_id, int option_index, int disabled);
```
## EU_SetSelectV2OptionAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2OptionAlignment(IntPtr hwnd, int element_id, int alignment);
```
## EU_GetSelectV2OptionAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2OptionAlignment(IntPtr hwnd, int element_id);
```
## EU_SetSelectV2ValueAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2ValueAlignment(IntPtr hwnd, int element_id, int alignment);
```
## EU_GetSelectV2ValueAlignment

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2ValueAlignment(IntPtr hwnd, int element_id);
```
## EU_GetSelectV2OptionCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2OptionCount(IntPtr hwnd, int element_id);
```
## EU_GetSelectV2MatchedCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2MatchedCount(IntPtr hwnd, int element_id);
```
## EU_GetSelectV2OptionDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2OptionDisabled(IntPtr hwnd, int element_id, int option_index);
```
## EU_SetSelectV2ScrollIndex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2ScrollIndex(IntPtr hwnd, int element_id, int scroll_index);
```
## EU_GetSelectV2ScrollIndex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSelectV2ScrollIndex(IntPtr hwnd, int element_id);
```
## EU_SetSelectV2ChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSelectV2ChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetRateValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateValue(IntPtr hwnd, int element_id, int value);
```
## EU_GetRateValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRateValue(IntPtr hwnd, int element_id);
```
## EU_SetRateMax

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateMax(IntPtr hwnd, int element_id, int max_value);
```
## EU_GetRateMax

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRateMax(IntPtr hwnd, int element_id);
```
## EU_SetRateValueX2

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateValueX2(IntPtr hwnd, int element_id, int value_x2);
```
## EU_GetRateValueX2

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRateValueX2(IntPtr hwnd, int element_id);
```
## EU_SetRateOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateOptions(IntPtr hwnd, int element_id, int allow_clear, int allow_half, int @readonly);
```
## EU_GetRateOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRateOptions(IntPtr hwnd, int element_id, IntPtr allow_clear, IntPtr allow_half, IntPtr @readonly, IntPtr show_score);
```
## EU_SetRateTexts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateTexts(IntPtr hwnd, int element_id, byte[] low_bytes, int low_len, byte[] high_bytes, int high_len, int show_score);
```
## EU_SetRateColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateColors(IntPtr hwnd, int element_id, uint low_color, uint mid_color, uint high_color);
```
## EU_GetRateColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRateColors(IntPtr hwnd, int element_id, IntPtr low_color, IntPtr mid_color, IntPtr high_color);
```
## EU_SetRateIcons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateIcons(IntPtr hwnd, int element_id, byte[] full_bytes, int full_len, byte[] void_bytes, int void_len, byte[] low_bytes, int low_len, byte[] mid_bytes, int mid_len, byte[] high_bytes, int high_len);
```
## EU_GetRateIcons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRateIcons(IntPtr hwnd, int element_id, byte[] full_buffer, int full_buffer_size, byte[] void_buffer, int void_buffer_size, byte[] low_buffer, int low_buffer_size, byte[] mid_buffer, int mid_buffer_size, byte[] high_buffer, int high_buffer_size);
```
## EU_SetRateTextItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateTextItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetRateDisplayOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateDisplayOptions(IntPtr hwnd, int element_id, int show_text, int show_score, uint text_color, byte[] template_bytes, int template_len);
```
## EU_GetRateDisplayOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRateDisplayOptions(IntPtr hwnd, int element_id, IntPtr show_text, IntPtr show_score, IntPtr text_color, byte[] template_buffer, int template_buffer_size);
```
## EU_SetRateChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRateChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetColorPickerColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetColorPickerColor(IntPtr hwnd, int element_id, uint color);
```
## EU_GetColorPickerColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetColorPickerColor(IntPtr hwnd, int element_id);
```
## EU_SetColorPickerAlpha

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetColorPickerAlpha(IntPtr hwnd, int element_id, int alpha);
```
## EU_GetColorPickerAlpha

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetColorPickerAlpha(IntPtr hwnd, int element_id);
```
## EU_SetColorPickerHex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_SetColorPickerHex(IntPtr hwnd, int element_id, byte[] hex_bytes, int hex_len);
```
## EU_GetColorPickerHex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetColorPickerHex(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetColorPickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetColorPickerOpen(IntPtr hwnd, int element_id, int open);
```
## EU_GetColorPickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetColorPickerOpen(IntPtr hwnd, int element_id);
```
## EU_SetColorPickerPalette

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetColorPickerPalette(IntPtr hwnd, int element_id, IntPtr colors, int count);
```
## EU_GetColorPickerPaletteCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetColorPickerPaletteCount(IntPtr hwnd, int element_id);
```
## EU_SetColorPickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetColorPickerOptions(IntPtr hwnd, int element_id, int show_alpha, int size_mode, int clearable);
```
## EU_GetColorPickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetColorPickerOptions(IntPtr hwnd, int element_id, IntPtr show_alpha, IntPtr size_mode, IntPtr clearable);
```
## EU_ClearColorPicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearColorPicker(IntPtr hwnd, int element_id);
```
## EU_GetColorPickerHasValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetColorPickerHasValue(IntPtr hwnd, int element_id);
```
## EU_SetColorPickerChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetColorPickerChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetTagType

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTagType(IntPtr hwnd, int element_id, int tag_type);
```
## EU_SetTagEffect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTagEffect(IntPtr hwnd, int element_id, int effect);
```
## EU_SetTagClosable

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTagClosable(IntPtr hwnd, int element_id, int closable);
```
## EU_SetTagClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTagClosed(IntPtr hwnd, int element_id, int closed);
```
## EU_GetTagClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTagClosed(IntPtr hwnd, int element_id);
```
## EU_GetTagOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTagOptions(IntPtr hwnd, int element_id, IntPtr tag_type, IntPtr effect, IntPtr closable, IntPtr closed);
```
## EU_SetTagSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTagSize(IntPtr hwnd, int element_id, int size_preset);
```
## EU_SetTagThemeColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTagThemeColor(IntPtr hwnd, int element_id, uint color);
```
## EU_GetTagVisualOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTagVisualOptions(IntPtr hwnd, int element_id, IntPtr size_preset, IntPtr theme_color);
```
## EU_SetTagCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTagCloseCallback(IntPtr hwnd, int element_id, ElementClickCallback cb);
```
## EU_SetBadgeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBadgeValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_SetBadgeMax

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBadgeMax(IntPtr hwnd, int element_id, int max_value);
```
## EU_SetBadgeType

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBadgeType(IntPtr hwnd, int element_id, int badge_type);
```
## EU_SetBadgeDot

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBadgeDot(IntPtr hwnd, int element_id, int dot);
```
## EU_SetBadgeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBadgeOptions(IntPtr hwnd, int element_id, int dot, int show_zero, int offset_x, int offset_y);
```
## EU_GetBadgeHidden

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBadgeHidden(IntPtr hwnd, int element_id);
```
## EU_GetBadgeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBadgeOptions(IntPtr hwnd, int element_id, IntPtr max_value, IntPtr dot, IntPtr show_zero, IntPtr offset_x, IntPtr offset_y);
```
## EU_GetBadgeType

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBadgeType(IntPtr hwnd, int element_id);
```
## EU_SetBadgeLayoutOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBadgeLayoutOptions(IntPtr hwnd, int element_id, int placement, int standalone);
```
## EU_GetBadgeLayoutOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBadgeLayoutOptions(IntPtr hwnd, int element_id, IntPtr placement, IntPtr standalone);
```
## EU_SetProgressPercentage

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressPercentage(IntPtr hwnd, int element_id, int percentage);
```
## EU_GetProgressPercentage

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressPercentage(IntPtr hwnd, int element_id);
```
## EU_SetProgressStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressStatus(IntPtr hwnd, int element_id, int status);
```
## EU_GetProgressStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressStatus(IntPtr hwnd, int element_id);
```
## EU_SetProgressShowText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressShowText(IntPtr hwnd, int element_id, int show_text);
```
## EU_SetProgressOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressOptions(IntPtr hwnd, int element_id, int progress_type, int stroke_width, int show_text);
```
## EU_GetProgressOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressOptions(IntPtr hwnd, int element_id, IntPtr progress_type, IntPtr stroke_width, IntPtr show_text);
```
## EU_SetProgressFormatOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressFormatOptions(IntPtr hwnd, int element_id, int text_format, int striped);
```
## EU_GetProgressFormatOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressFormatOptions(IntPtr hwnd, int element_id, IntPtr text_format, IntPtr striped);
```
## EU_SetProgressTextInside

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressTextInside(IntPtr hwnd, int element_id, int text_inside);
```
## EU_GetProgressTextInside

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressTextInside(IntPtr hwnd, int element_id);
```
## EU_SetProgressColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressColors(IntPtr hwnd, int element_id, uint fill, uint track, uint text);
```
## EU_GetProgressColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressColors(IntPtr hwnd, int element_id, IntPtr fill, IntPtr track, IntPtr text);
```
## EU_SetProgressColorStops

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressColorStops(IntPtr hwnd, int element_id, byte[] stops_bytes, int stops_len);
```
## EU_GetProgressColorStopCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressColorStopCount(IntPtr hwnd, int element_id);
```
## EU_GetProgressColorStop

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressColorStop(IntPtr hwnd, int element_id, int index, IntPtr color, IntPtr percentage);
```
## EU_SetProgressCompleteText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressCompleteText(IntPtr hwnd, int element_id, byte[] bytes, int len);
```
## EU_GetProgressCompleteText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressCompleteText(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetProgressTextTemplate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetProgressTextTemplate(IntPtr hwnd, int element_id, byte[] bytes, int len);
```
## EU_GetProgressTextTemplate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetProgressTextTemplate(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetAvatarShape

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAvatarShape(IntPtr hwnd, int element_id, int shape);
```
## EU_SetAvatarSource

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAvatarSource(IntPtr hwnd, int element_id, byte[] src_bytes, int src_len);
```
## EU_SetAvatarFallbackSource

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAvatarFallbackSource(IntPtr hwnd, int element_id, byte[] src_bytes, int src_len);
```
## EU_SetAvatarIcon

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAvatarIcon(IntPtr hwnd, int element_id, byte[] icon_bytes, int icon_len);
```
## EU_SetAvatarErrorText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAvatarErrorText(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetAvatarFit

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAvatarFit(IntPtr hwnd, int element_id, int fit);
```
## EU_GetAvatarImageStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAvatarImageStatus(IntPtr hwnd, int element_id);
```
## EU_GetAvatarOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAvatarOptions(IntPtr hwnd, int element_id, IntPtr shape, IntPtr fit);
```
## EU_SetEmptyDescription

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEmptyDescription(IntPtr hwnd, int element_id, byte[] desc_bytes, int desc_len);
```
## EU_SetEmptyOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEmptyOptions(IntPtr hwnd, int element_id, byte[] icon_bytes, int icon_len, byte[] action_bytes, int action_len);
```
## EU_SetEmptyActionClicked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEmptyActionClicked(IntPtr hwnd, int element_id, int clicked);
```
## EU_GetEmptyActionClicked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetEmptyActionClicked(IntPtr hwnd, int element_id);
```
## EU_SetEmptyActionCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEmptyActionCallback(IntPtr hwnd, int element_id, ElementClickCallback cb);
```
## EU_SetEmptyImage

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEmptyImage(IntPtr hwnd, int element_id, byte[] image_bytes, int image_len);
```
## EU_SetEmptyImageSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetEmptyImageSize(IntPtr hwnd, int element_id, int image_size);
```
## EU_GetEmptyImageStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetEmptyImageStatus(IntPtr hwnd, int element_id);
```
## EU_GetEmptyImageSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetEmptyImageSize(IntPtr hwnd, int element_id);
```
## EU_SetSkeletonRows

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSkeletonRows(IntPtr hwnd, int element_id, int rows);
```
## EU_SetSkeletonAnimated

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSkeletonAnimated(IntPtr hwnd, int element_id, int animated);
```
## EU_SetSkeletonLoading

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSkeletonLoading(IntPtr hwnd, int element_id, int loading);
```
## EU_SetSkeletonOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSkeletonOptions(IntPtr hwnd, int element_id, int rows, int animated, int loading, int show_avatar);
```
## EU_GetSkeletonLoading

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSkeletonLoading(IntPtr hwnd, int element_id);
```
## EU_GetSkeletonOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSkeletonOptions(IntPtr hwnd, int element_id, IntPtr rows, IntPtr animated, IntPtr loading, IntPtr show_avatar);
```
## EU_SetDescriptionsItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetDescriptionsColumns

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsColumns(IntPtr hwnd, int element_id, int columns);
```
## EU_SetDescriptionsBordered

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsBordered(IntPtr hwnd, int element_id, int bordered);
```
## EU_SetDescriptionsLayout

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsLayout(IntPtr hwnd, int element_id, int direction, int size, int columns, int bordered);
```
## EU_SetDescriptionsItemsEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsItemsEx(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetDescriptionsOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsOptions(IntPtr hwnd, int element_id, int columns, int bordered, int label_width, int min_row_height, int wrap_values);
```
## EU_GetDescriptionsItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDescriptionsItemCount(IntPtr hwnd, int element_id);
```
## EU_SetDescriptionsAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsAdvancedOptions(IntPtr hwnd, int element_id, int responsive, int last_item_span);
```
## EU_SetDescriptionsColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsColors(IntPtr hwnd, int element_id, uint border, uint label_bg, uint content_bg, uint label_fg, uint content_fg, uint title_fg);
```
## EU_SetDescriptionsExtra

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDescriptionsExtra(IntPtr hwnd, int element_id, byte[] emoji_bytes, int emoji_len, byte[] text_bytes, int text_len, int visible, int variant);
```
## EU_GetDescriptionsOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDescriptionsOptions(IntPtr hwnd, int element_id, IntPtr columns, IntPtr bordered, IntPtr label_width, IntPtr min_row_height, IntPtr wrap_values, IntPtr responsive, IntPtr last_item_span);
```
## EU_GetDescriptionsFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDescriptionsFullState(IntPtr hwnd, int element_id, IntPtr direction, IntPtr size, IntPtr columns, IntPtr bordered, IntPtr item_count, IntPtr extra_click_count, IntPtr responsive, IntPtr wrap_values);
```
## EU_SetTableData

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableData(IntPtr hwnd, int element_id, byte[] columns_bytes, int columns_len, byte[] rows_bytes, int rows_len);
```
## EU_SetTableStriped

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableStriped(IntPtr hwnd, int element_id, int striped);
```
## EU_SetTableBordered

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableBordered(IntPtr hwnd, int element_id, int bordered);
```
## EU_SetTableEmptyText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableEmptyText(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetTableSelectedRow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableSelectedRow(IntPtr hwnd, int element_id, int row_index);
```
## EU_GetTableSelectedRow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTableSelectedRow(IntPtr hwnd, int element_id);
```
## EU_GetTableRowCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTableRowCount(IntPtr hwnd, int element_id);
```
## EU_GetTableColumnCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTableColumnCount(IntPtr hwnd, int element_id);
```
## EU_SetTableOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableOptions(IntPtr hwnd, int element_id, int striped, int bordered, int row_height, int header_height, int selectable);
```
## EU_SetTableSort

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableSort(IntPtr hwnd, int element_id, int column_index, int desc);
```
## EU_SetTableScrollRow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableScrollRow(IntPtr hwnd, int element_id, int scroll_row);
```
## EU_SetTableColumnWidth

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableColumnWidth(IntPtr hwnd, int element_id, int column_width);
```
## EU_GetTableOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTableOptions(IntPtr hwnd, int element_id, IntPtr striped, IntPtr bordered, IntPtr row_height, IntPtr header_height, IntPtr selectable, IntPtr sort_column, IntPtr sort_desc, IntPtr scroll_row, IntPtr column_width);
```
## EU_SetTableColumnsEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableColumnsEx(IntPtr hwnd, int element_id, byte[] columns_bytes, int columns_len);
```
## EU_SetTableRowsEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableRowsEx(IntPtr hwnd, int element_id, byte[] rows_bytes, int rows_len);
```
## EU_AddTableRow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_AddTableRow(IntPtr hwnd, int element_id, byte[] row_bytes, int row_len);
```
## EU_InsertTableRow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_InsertTableRow(IntPtr hwnd, int element_id, int row_index, byte[] row_bytes, int row_len);
```
## EU_DeleteTableRow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_DeleteTableRow(IntPtr hwnd, int element_id, int row_index);
```
## EU_ClearTableRows

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ClearTableRows(IntPtr hwnd, int element_id);
```
## EU_SetTableCellEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableCellEx(IntPtr hwnd, int element_id, int row, int col, int type, byte[] value_bytes, int value_len, byte[] options_bytes, int options_len);
```
## EU_SetTableRowStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableRowStyle(IntPtr hwnd, int element_id, int row, uint bg, uint fg, int align, int font_flags, int font_size);
```
## EU_SetTableCellStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableCellStyle(IntPtr hwnd, int element_id, int row, int col, uint bg, uint fg, int align, int font_flags, int font_size);
```
## EU_SetTableSelectionMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableSelectionMode(IntPtr hwnd, int element_id, int mode);
```
## EU_SetTableSelectedRows

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableSelectedRows(IntPtr hwnd, int element_id, byte[] rows_bytes, int rows_len);
```
## EU_SetTableFilter

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableFilter(IntPtr hwnd, int element_id, int col, byte[] value_bytes, int value_len);
```
## EU_ClearTableFilter

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearTableFilter(IntPtr hwnd, int element_id, int col);
```
## EU_SetTableSearch

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableSearch(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_SetTableSpan

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableSpan(IntPtr hwnd, int element_id, int row, int col, int rowspan, int colspan);
```
## EU_ClearTableSpans

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearTableSpans(IntPtr hwnd, int element_id);
```
## EU_SetTableSummary

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableSummary(IntPtr hwnd, int element_id, byte[] values_bytes, int values_len);
```
## EU_SetTableRowExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableRowExpanded(IntPtr hwnd, int element_id, int row, int expanded);
```
## EU_SetTableTreeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableTreeOptions(IntPtr hwnd, int element_id, int enabled, int indent, int lazy);
```
## EU_SetTableViewportOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableViewportOptions(IntPtr hwnd, int element_id, int max_height, int fixed_header, int horizontal_scroll, int show_summary);
```
## EU_SetTableScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableScroll(IntPtr hwnd, int element_id, int scroll_row, int scroll_x);
```
## EU_SetTableHeaderDragOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableHeaderDragOptions(IntPtr hwnd, int element_id, int column_resize, int header_height_resize, int min_col_width, int max_col_width, int min_header_height, int max_header_height);
```
## EU_ExportTableExcel

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ExportTableExcel(IntPtr hwnd, int element_id, byte[] path_bytes, int path_len, int flags);
```
## EU_ImportTableExcel

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ImportTableExcel(IntPtr hwnd, int element_id, byte[] path_bytes, int path_len, int flags);
```
## EU_SetTableCellClickCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableCellClickCallback(IntPtr hwnd, int element_id, TableCellCallback cb);
```
## EU_SetTableCellActionCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableCellActionCallback(IntPtr hwnd, int element_id, TableCellCallback cb);
```
## EU_SetTableVirtualOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableVirtualOptions(IntPtr hwnd, int element_id, int enabled, int row_count, int cache_window);
```
## EU_SetTableVirtualRowProvider

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTableVirtualRowProvider(IntPtr hwnd, int element_id, TableVirtualRowCallback cb);
```
## EU_ClearTableVirtualCache

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearTableVirtualCache(IntPtr hwnd, int element_id);
```
## EU_GetTableCellValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTableCellValue(IntPtr hwnd, int element_id, int row, int col, byte[] buffer, int buffer_size);
```
## EU_GetTableFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTableFullState(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetCardTitle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardTitle(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len);
```
## EU_SetCardBody

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardBody(IntPtr hwnd, int element_id, byte[] body_bytes, int body_len);
```
## EU_SetCardFooter

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardFooter(IntPtr hwnd, int element_id, byte[] footer_bytes, int footer_len);
```
## EU_SetCardItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetCardActions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardActions(IntPtr hwnd, int element_id, byte[] actions_bytes, int actions_len);
```
## EU_GetCardItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCardItemCount(IntPtr hwnd, int element_id);
```
## EU_GetCardAction

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCardAction(IntPtr hwnd, int element_id);
```
## EU_ResetCardAction

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ResetCardAction(IntPtr hwnd, int element_id);
```
## EU_SetCardShadow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardShadow(IntPtr hwnd, int element_id, int shadow);
```
## EU_SetCardOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardOptions(IntPtr hwnd, int element_id, int shadow, int hoverable);
```
## EU_SetCardStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardStyle(IntPtr hwnd, int element_id, uint bg, uint border, float border_width, float radius, int padding);
```
## EU_GetCardStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCardStyle(IntPtr hwnd, int element_id, IntPtr bg, IntPtr border, IntPtr border_width, IntPtr radius, IntPtr padding);
```
## EU_SetCardBodyStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCardBodyStyle(IntPtr hwnd, int element_id, int pad_left, int pad_top, int pad_right, int pad_bottom, float font_size, int item_gap, int item_padding_y, int divider);
```
## EU_GetCardBodyStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCardBodyStyle(IntPtr hwnd, int element_id, IntPtr pad_left, IntPtr pad_top, IntPtr pad_right, IntPtr pad_bottom, IntPtr font_size, IntPtr item_gap, IntPtr item_padding_y, IntPtr divider);
```
## EU_GetCardOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCardOptions(IntPtr hwnd, int element_id, IntPtr shadow, IntPtr hoverable, IntPtr action_count);
```
## EU_SetCollapseItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCollapseItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetCollapseItemsEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCollapseItemsEx(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetCollapseActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCollapseActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_GetCollapseActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCollapseActive(IntPtr hwnd, int element_id);
```
## EU_SetCollapseActiveItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCollapseActiveItems(IntPtr hwnd, int element_id, byte[] indices_bytes, int indices_len);
```
## EU_GetCollapseActiveItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCollapseActiveItems(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetCollapseItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCollapseItemCount(IntPtr hwnd, int element_id);
```
## EU_SetCollapseOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCollapseOptions(IntPtr hwnd, int element_id, int accordion, int allow_collapse, byte[] disabled_bytes, int disabled_len);
```
## EU_SetCollapseAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCollapseAdvancedOptions(IntPtr hwnd, int element_id, int accordion, int allow_collapse, int animated, byte[] disabled_bytes, int disabled_len);
```
## EU_GetCollapseOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCollapseOptions(IntPtr hwnd, int element_id, IntPtr accordion, IntPtr allow_collapse, IntPtr animated, IntPtr disabled_count);
```
## EU_GetCollapseStateJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCollapseStateJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetTimelineItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimelineItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetTimelineOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimelineOptions(IntPtr hwnd, int element_id, int position, int show_time);
```
## EU_GetTimelineItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimelineItemCount(IntPtr hwnd, int element_id);
```
## EU_GetTimelineOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimelineOptions(IntPtr hwnd, int element_id, IntPtr position, IntPtr show_time);
```
## EU_SetTimelineAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimelineAdvancedOptions(IntPtr hwnd, int element_id, int position, int show_time, int reverse, int default_placement);
```
## EU_GetTimelineAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimelineAdvancedOptions(IntPtr hwnd, int element_id, IntPtr position, IntPtr show_time, IntPtr reverse, IntPtr default_placement);
```
## EU_SetStatisticValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_SetStatisticFormat

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticFormat(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len, byte[] prefix_bytes, int prefix_len, byte[] suffix_bytes, int suffix_len);
```
## EU_SetStatisticOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticOptions(IntPtr hwnd, int element_id, int precision, int animated);
```
## EU_GetStatisticOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStatisticOptions(IntPtr hwnd, int element_id, IntPtr precision, IntPtr animated);
```
## EU_SetStatisticNumberOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticNumberOptions(IntPtr hwnd, int element_id, int precision, int animated, int use_group_separator, byte[] group_separator_bytes, int group_separator_len, byte[] decimal_separator_bytes, int decimal_separator_len);
```
## EU_SetStatisticAffixOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticAffixOptions(IntPtr hwnd, int element_id, byte[] prefix_bytes, int prefix_len, byte[] suffix_bytes, int suffix_len, uint prefix_color, uint suffix_color, uint value_color, int suffix_clickable);
```
## EU_SetStatisticDisplayText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticDisplayText(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetStatisticCountdown

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticCountdown(IntPtr hwnd, int element_id, long target_unix_ms, byte[] format_bytes, int format_len);
```
## EU_SetStatisticCountdownState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticCountdownState(IntPtr hwnd, int element_id, int paused);
```
## EU_AddStatisticCountdownTime

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_AddStatisticCountdownTime(IntPtr hwnd, int element_id, long delta_ms);
```
## EU_SetStatisticFinishCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticFinishCallback(IntPtr hwnd, int element_id, ElementClickCallback cb);
```
## EU_SetStatisticSuffixClickCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatisticSuffixClickCallback(IntPtr hwnd, int element_id, ElementClickCallback cb);
```
## EU_GetStatisticFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStatisticFullState(IntPtr hwnd, int element_id, IntPtr mode, IntPtr precision, IntPtr animated, IntPtr use_group_separator, IntPtr countdown_paused, IntPtr countdown_finished, IntPtr suffix_click_count, IntPtr remaining_ms);
```
## EU_SetKpiCardData

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetKpiCardData(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len, byte[] subtitle_bytes, int subtitle_len, byte[] trend_bytes, int trend_len, int trend_type);
```
## EU_SetKpiCardOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetKpiCardOptions(IntPtr hwnd, int element_id, int loading, byte[] helper_bytes, int helper_len);
```
## EU_GetKpiCardOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetKpiCardOptions(IntPtr hwnd, int element_id, IntPtr loading, IntPtr trend_type);
```
## EU_SetTrendData

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTrendData(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len, byte[] percent_bytes, int percent_len, byte[] detail_bytes, int detail_len, int direction);
```
## EU_SetTrendOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTrendOptions(IntPtr hwnd, int element_id, int inverse, int show_icon);
```
## EU_GetTrendDirection

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTrendDirection(IntPtr hwnd, int element_id);
```
## EU_GetTrendOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTrendOptions(IntPtr hwnd, int element_id, IntPtr inverse, IntPtr show_icon);
```
## EU_SetStatusDot

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatusDot(IntPtr hwnd, int element_id, byte[] label_bytes, int label_len, byte[] desc_bytes, int desc_len, int status);
```
## EU_SetStatusDotOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStatusDotOptions(IntPtr hwnd, int element_id, int pulse, int compact);
```
## EU_GetStatusDotStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStatusDotStatus(IntPtr hwnd, int element_id);
```
## EU_GetStatusDotOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStatusDotOptions(IntPtr hwnd, int element_id, IntPtr pulse, IntPtr compact);
```
## EU_SetGaugeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetGaugeValue(IntPtr hwnd, int element_id, int value, byte[] caption_bytes, int caption_len, int status);
```
## EU_SetGaugeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetGaugeOptions(IntPtr hwnd, int element_id, int min_value, int max_value, int warning_value, int danger_value, int stroke_width);
```
## EU_GetGaugeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetGaugeValue(IntPtr hwnd, int element_id);
```
## EU_GetGaugeStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetGaugeStatus(IntPtr hwnd, int element_id);
```
## EU_GetGaugeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetGaugeOptions(IntPtr hwnd, int element_id, IntPtr min_value, IntPtr max_value, IntPtr warning_value, IntPtr danger_value, IntPtr stroke_width);
```
## EU_SetRingProgressValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRingProgressValue(IntPtr hwnd, int element_id, int value, byte[] label_bytes, int label_len, int status);
```
## EU_SetRingProgressOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetRingProgressOptions(IntPtr hwnd, int element_id, int stroke_width, int show_center);
```
## EU_GetRingProgressValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRingProgressValue(IntPtr hwnd, int element_id);
```
## EU_GetRingProgressStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRingProgressStatus(IntPtr hwnd, int element_id);
```
## EU_GetRingProgressOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetRingProgressOptions(IntPtr hwnd, int element_id, IntPtr stroke_width, IntPtr show_center);
```
## EU_SetBulletProgressValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBulletProgressValue(IntPtr hwnd, int element_id, int value, int target, byte[] desc_bytes, int desc_len, int status);
```
## EU_SetBulletProgressOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBulletProgressOptions(IntPtr hwnd, int element_id, int good_threshold, int warn_threshold, int show_target);
```
## EU_GetBulletProgressValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBulletProgressValue(IntPtr hwnd, int element_id);
```
## EU_GetBulletProgressTarget

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBulletProgressTarget(IntPtr hwnd, int element_id);
```
## EU_GetBulletProgressStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBulletProgressStatus(IntPtr hwnd, int element_id);
```
## EU_GetBulletProgressOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBulletProgressOptions(IntPtr hwnd, int element_id, IntPtr good_threshold, IntPtr warn_threshold, IntPtr show_target);
```
## EU_SetLineChartData

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLineChartData(IntPtr hwnd, int element_id, byte[] points_bytes, int points_len);
```
## EU_SetLineChartSeries

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLineChartSeries(IntPtr hwnd, int element_id, byte[] series_bytes, int series_len);
```
## EU_SetLineChartOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLineChartOptions(IntPtr hwnd, int element_id, int chart_style, int show_axis, int show_area, int show_tooltip);
```
## EU_SetLineChartSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLineChartSelected(IntPtr hwnd, int element_id, int selected_index);
```
## EU_GetLineChartPointCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLineChartPointCount(IntPtr hwnd, int element_id);
```
## EU_GetLineChartSeriesCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLineChartSeriesCount(IntPtr hwnd, int element_id);
```
## EU_GetLineChartSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLineChartSelected(IntPtr hwnd, int element_id);
```
## EU_GetLineChartOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLineChartOptions(IntPtr hwnd, int element_id, IntPtr chart_style, IntPtr show_axis, IntPtr show_area, IntPtr show_tooltip);
```
## EU_SetBarChartData

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBarChartData(IntPtr hwnd, int element_id, byte[] bars_bytes, int bars_len);
```
## EU_SetBarChartSeries

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBarChartSeries(IntPtr hwnd, int element_id, byte[] series_bytes, int series_len);
```
## EU_SetBarChartOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBarChartOptions(IntPtr hwnd, int element_id, int orientation, int show_values, int show_axis);
```
## EU_SetBarChartSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBarChartSelected(IntPtr hwnd, int element_id, int selected_index);
```
## EU_GetBarChartBarCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBarChartBarCount(IntPtr hwnd, int element_id);
```
## EU_GetBarChartSeriesCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBarChartSeriesCount(IntPtr hwnd, int element_id);
```
## EU_GetBarChartSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBarChartSelected(IntPtr hwnd, int element_id);
```
## EU_GetBarChartOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBarChartOptions(IntPtr hwnd, int element_id, IntPtr orientation, IntPtr show_values, IntPtr show_axis);
```
## EU_SetDonutChartData

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDonutChartData(IntPtr hwnd, int element_id, byte[] slices_bytes, int slices_len, int active_index);
```
## EU_SetDonutChartOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDonutChartOptions(IntPtr hwnd, int element_id, int show_legend, int ring_width);
```
## EU_SetDonutChartAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDonutChartAdvancedOptions(IntPtr hwnd, int element_id, int show_legend, int ring_width, int show_labels);
```
## EU_SetDonutChartActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDonutChartActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_GetDonutChartSliceCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDonutChartSliceCount(IntPtr hwnd, int element_id);
```
## EU_GetDonutChartActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDonutChartActive(IntPtr hwnd, int element_id);
```
## EU_GetDonutChartOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDonutChartOptions(IntPtr hwnd, int element_id, IntPtr show_legend, IntPtr ring_width);
```
## EU_GetDonutChartAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDonutChartAdvancedOptions(IntPtr hwnd, int element_id, IntPtr show_legend, IntPtr ring_width, IntPtr show_labels);
```
## EU_SetCalendarDate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarDate(IntPtr hwnd, int element_id, int year, int month, int selected_day);
```
## EU_SetCalendarRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarRange(IntPtr hwnd, int element_id, int min_yyyymmdd, int max_yyyymmdd);
```
## EU_SetCalendarOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarOptions(IntPtr hwnd, int element_id, int today_yyyymmdd, int show_today);
```
## EU_CalendarMoveMonth

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_CalendarMoveMonth(IntPtr hwnd, int element_id, int delta_months);
```
## EU_GetCalendarValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarValue(IntPtr hwnd, int element_id);
```
## EU_GetCalendarRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarRange(IntPtr hwnd, int element_id, IntPtr min_yyyymmdd, IntPtr max_yyyymmdd);
```
## EU_GetCalendarOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarOptions(IntPtr hwnd, int element_id, IntPtr today_yyyymmdd, IntPtr show_today);
```
## EU_SetCalendarSelectionRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarSelectionRange(IntPtr hwnd, int element_id, int start_yyyymmdd, int end_yyyymmdd, int enabled);
```
## EU_GetCalendarSelectionRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarSelectionRange(IntPtr hwnd, int element_id, IntPtr start_yyyymmdd, IntPtr end_yyyymmdd, IntPtr enabled);
```
## EU_SetCalendarDisplayRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarDisplayRange(IntPtr hwnd, int element_id, int start_yyyymmdd, int end_yyyymmdd);
```
## EU_GetCalendarDisplayRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarDisplayRange(IntPtr hwnd, int element_id, IntPtr start_yyyymmdd, IntPtr end_yyyymmdd);
```
## EU_SetCalendarCellItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarCellItems(IntPtr hwnd, int element_id, byte[] spec_bytes, int spec_len);
```
## EU_GetCalendarCellItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarCellItems(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_ClearCalendarCellItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearCalendarCellItems(IntPtr hwnd, int element_id);
```
## EU_SetCalendarVisualOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarVisualOptions(IntPtr hwnd, int element_id, int show_header, int show_week_header, int label_mode, int show_adjacent_days, float cell_radius);
```
## EU_GetCalendarVisualOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarVisualOptions(IntPtr hwnd, int element_id, IntPtr show_header, IntPtr show_week_header, IntPtr label_mode, IntPtr show_adjacent_days, IntPtr cell_radius);
```
## EU_SetCalendarStateColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarStateColors(IntPtr hwnd, int element_id, uint selected_bg, uint selected_fg, uint range_bg, uint today_border, uint hover_bg, uint disabled_fg, uint adjacent_fg);
```
## EU_GetCalendarStateColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCalendarStateColors(IntPtr hwnd, int element_id, IntPtr selected_bg, IntPtr selected_fg, IntPtr range_bg, IntPtr today_border, IntPtr hover_bg, IntPtr disabled_fg, IntPtr adjacent_fg);
```
## EU_SetCalendarSelectedMarker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarSelectedMarker(IntPtr hwnd, int element_id, byte[] marker_bytes, int marker_len);
```
## EU_SetCalendarChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCalendarChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetTreeItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetTreeSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelected(IntPtr hwnd, int element_id, int selected_index);
```
## EU_GetTreeSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelected(IntPtr hwnd, int element_id);
```
## EU_SetTreeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeOptions(IntPtr hwnd, int element_id, int show_checkbox, int keyboard_navigation, int lazy_mode);
```
## EU_GetTreeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeOptions(IntPtr hwnd, int element_id, IntPtr show_checkbox, IntPtr keyboard_navigation, IntPtr lazy_mode, IntPtr checked_count, IntPtr last_lazy_index);
```
## EU_SetTreeItemExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeItemExpanded(IntPtr hwnd, int element_id, int item_index, int expanded);
```
## EU_ToggleTreeItemExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ToggleTreeItemExpanded(IntPtr hwnd, int element_id, int item_index);
```
## EU_GetTreeItemExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeItemExpanded(IntPtr hwnd, int element_id, int item_index);
```
## EU_SetTreeItemChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeItemChecked(IntPtr hwnd, int element_id, int item_index, int @checked);
```
## EU_GetTreeItemChecked

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeItemChecked(IntPtr hwnd, int element_id, int item_index);
```
## EU_SetTreeItemLazy

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeItemLazy(IntPtr hwnd, int element_id, int item_index, int lazy);
```
## EU_GetTreeItemLazy

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeItemLazy(IntPtr hwnd, int element_id, int item_index);
```
## EU_GetTreeVisibleCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeVisibleCount(IntPtr hwnd, int element_id);
```
## EU_SetTreeSelectItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetTreeSelectSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectSelected(IntPtr hwnd, int element_id, int selected_index);
```
## EU_GetTreeSelectSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectSelected(IntPtr hwnd, int element_id);
```
## EU_SetTreeSelectOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectOpen(IntPtr hwnd, int element_id, int open);
```
## EU_GetTreeSelectOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectOpen(IntPtr hwnd, int element_id);
```
## EU_SetTreeSelectOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectOptions(IntPtr hwnd, int element_id, int multiple, int clearable, int searchable);
```
## EU_GetTreeSelectOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectOptions(IntPtr hwnd, int element_id, IntPtr multiple, IntPtr clearable, IntPtr searchable, IntPtr selected_count, IntPtr matched_count);
```
## EU_SetTreeSelectSearch

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectSearch(IntPtr hwnd, int element_id, byte[] search_bytes, int search_len);
```
## EU_GetTreeSelectSearch

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectSearch(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_ClearTreeSelect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearTreeSelect(IntPtr hwnd, int element_id);
```
## EU_SetTreeSelectSelectedItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectSelectedItems(IntPtr hwnd, int element_id, byte[] indices_bytes, int indices_len);
```
## EU_GetTreeSelectSelectedCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectSelectedCount(IntPtr hwnd, int element_id);
```
## EU_GetTreeSelectSelectedItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectSelectedItem(IntPtr hwnd, int element_id, int position);
```
## EU_SetTreeSelectItemExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectItemExpanded(IntPtr hwnd, int element_id, int item_index, int expanded);
```
## EU_ToggleTreeSelectItemExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ToggleTreeSelectItemExpanded(IntPtr hwnd, int element_id, int item_index);
```
## EU_GetTreeSelectItemExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectItemExpanded(IntPtr hwnd, int element_id, int item_index);
```
## EU_SetTreeDataJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeDataJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeDataJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeDataJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetTreeOptionsJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeOptionsJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeStateJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeStateJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetTreeCheckedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeCheckedKeysJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeCheckedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeCheckedKeysJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetTreeExpandedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeExpandedKeysJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeExpandedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeExpandedKeysJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_AppendTreeNodeJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_AppendTreeNodeJson(IntPtr hwnd, int element_id, byte[] parent_key_bytes, int parent_key_len, byte[] json_bytes, int json_len);
```
## EU_UpdateTreeNodeJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_UpdateTreeNodeJson(IntPtr hwnd, int element_id, byte[] key_bytes, int key_len, byte[] json_bytes, int json_len);
```
## EU_RemoveTreeNodeByKey

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_RemoveTreeNodeByKey(IntPtr hwnd, int element_id, byte[] key_bytes, int key_len);
```
## EU_SetTreeNodeEventCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeNodeEventCallback(IntPtr hwnd, int element_id, TreeNodeEventCallback cb);
```
## EU_SetTreeLazyLoadCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeLazyLoadCallback(IntPtr hwnd, int element_id, TreeNodeEventCallback cb);
```
## EU_SetTreeDragCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeDragCallback(IntPtr hwnd, int element_id, TreeNodeEventCallback cb);
```
## EU_SetTreeAllowDragCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeAllowDragCallback(IntPtr hwnd, int element_id, TreeNodeAllowDragCallback cb);
```
## EU_SetTreeAllowDropCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeAllowDropCallback(IntPtr hwnd, int element_id, TreeNodeAllowDropCallback cb);
```
## EU_SetTreeSelectDataJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectDataJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeSelectDataJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectDataJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetTreeSelectOptionsJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectOptionsJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeSelectStateJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectStateJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetTreeSelectSelectedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectSelectedKeysJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeSelectSelectedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectSelectedKeysJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetTreeSelectExpandedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectExpandedKeysJson(IntPtr hwnd, int element_id, byte[] json_bytes, int json_len);
```
## EU_GetTreeSelectExpandedKeysJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTreeSelectExpandedKeysJson(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_AppendTreeSelectNodeJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_AppendTreeSelectNodeJson(IntPtr hwnd, int element_id, byte[] parent_key_bytes, int parent_key_len, byte[] json_bytes, int json_len);
```
## EU_UpdateTreeSelectNodeJson

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_UpdateTreeSelectNodeJson(IntPtr hwnd, int element_id, byte[] key_bytes, int key_len, byte[] json_bytes, int json_len);
```
## EU_RemoveTreeSelectNodeByKey

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_RemoveTreeSelectNodeByKey(IntPtr hwnd, int element_id, byte[] key_bytes, int key_len);
```
## EU_SetTreeSelectNodeEventCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectNodeEventCallback(IntPtr hwnd, int element_id, TreeNodeEventCallback cb);
```
## EU_SetTreeSelectLazyLoadCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectLazyLoadCallback(IntPtr hwnd, int element_id, TreeNodeEventCallback cb);
```
## EU_SetTreeSelectDragCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectDragCallback(IntPtr hwnd, int element_id, TreeNodeEventCallback cb);
```
## EU_SetTreeSelectAllowDragCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectAllowDragCallback(IntPtr hwnd, int element_id, TreeNodeAllowDragCallback cb);
```
## EU_SetTreeSelectAllowDropCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTreeSelectAllowDropCallback(IntPtr hwnd, int element_id, TreeNodeAllowDropCallback cb);
```
## EU_SetTransferItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferItems(IntPtr hwnd, int element_id, byte[] left_bytes, int left_len, byte[] right_bytes, int right_len);
```
## EU_TransferMoveRight

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TransferMoveRight(IntPtr hwnd, int element_id);
```
## EU_TransferMoveLeft

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TransferMoveLeft(IntPtr hwnd, int element_id);
```
## EU_TransferMoveAllRight

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TransferMoveAllRight(IntPtr hwnd, int element_id);
```
## EU_TransferMoveAllLeft

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TransferMoveAllLeft(IntPtr hwnd, int element_id);
```
## EU_SetTransferSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferSelected(IntPtr hwnd, int element_id, int side, int selected_index);
```
## EU_GetTransferSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferSelected(IntPtr hwnd, int element_id, int side);
```
## EU_GetTransferCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferCount(IntPtr hwnd, int element_id, int side);
```
## EU_SetTransferFilters

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferFilters(IntPtr hwnd, int element_id, byte[] left_bytes, int left_len, byte[] right_bytes, int right_len);
```
## EU_GetTransferMatchedCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferMatchedCount(IntPtr hwnd, int element_id, int side);
```
## EU_SetTransferItemDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferItemDisabled(IntPtr hwnd, int element_id, int side, int item_index, int disabled);
```
## EU_GetTransferItemDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferItemDisabled(IntPtr hwnd, int element_id, int side, int item_index);
```
## EU_GetTransferDisabledCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferDisabledCount(IntPtr hwnd, int element_id, int side);
```
## EU_SetTransferDataEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferDataEx(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len, byte[] target_bytes, int target_len);
```
## EU_SetTransferOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferOptions(IntPtr hwnd, int element_id, int filterable, int multiple, int show_footer, int show_select_all, int show_count, int render_mode);
```
## EU_GetTransferOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferOptions(IntPtr hwnd, int element_id, IntPtr filterable, IntPtr multiple, IntPtr show_footer, IntPtr show_select_all, IntPtr show_count, IntPtr render_mode);
```
## EU_SetTransferTitles

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferTitles(IntPtr hwnd, int element_id, byte[] left_bytes, int left_len, byte[] right_bytes, int right_len);
```
## EU_SetTransferButtonTexts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferButtonTexts(IntPtr hwnd, int element_id, byte[] left_bytes, int left_len, byte[] right_bytes, int right_len);
```
## EU_SetTransferFormat

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferFormat(IntPtr hwnd, int element_id, byte[] no_checked_bytes, int no_checked_len, byte[] has_checked_bytes, int has_checked_len);
```
## EU_SetTransferItemTemplate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferItemTemplate(IntPtr hwnd, int element_id, byte[] template_bytes, int template_len);
```
## EU_SetTransferFooterTexts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferFooterTexts(IntPtr hwnd, int element_id, byte[] left_bytes, int left_len, byte[] right_bytes, int right_len);
```
## EU_SetTransferFilterPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferFilterPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetTransferCheckedKeys

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTransferCheckedKeys(IntPtr hwnd, int element_id, byte[] left_bytes, int left_len, byte[] right_bytes, int right_len);
```
## EU_GetTransferCheckedCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferCheckedCount(IntPtr hwnd, int element_id, int side);
```
## EU_GetTransferValueKeys

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferValueKeys(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetTransferText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTransferText(IntPtr hwnd, int element_id, int text_type, byte[] buffer, int buffer_size);
```
## EU_SetAutocompleteSuggestions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteSuggestions(IntPtr hwnd, int element_id, byte[] suggestions_bytes, int suggestions_len);
```
## EU_SetAutocompleteValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_SetAutocompletePlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompletePlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_GetAutocompletePlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompletePlaceholder(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetAutocompleteIcons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteIcons(IntPtr hwnd, int element_id, byte[] prefix_icon_bytes, int prefix_icon_len, byte[] suffix_icon_bytes, int suffix_icon_len);
```
## EU_GetAutocompleteIcons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompleteIcons(IntPtr hwnd, int element_id, byte[] prefix_icon_buffer, int prefix_icon_buffer_size, byte[] suffix_icon_buffer, int suffix_icon_buffer_size);
```
## EU_SetAutocompleteBehaviorOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteBehaviorOptions(IntPtr hwnd, int element_id, int trigger_on_focus);
```
## EU_GetAutocompleteBehaviorOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompleteBehaviorOptions(IntPtr hwnd, int element_id, IntPtr trigger_on_focus);
```
## EU_SetAutocompleteOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetAutocompleteSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteSelected(IntPtr hwnd, int element_id, int selected_index);
```
## EU_SetAutocompleteAsyncState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteAsyncState(IntPtr hwnd, int element_id, int loading, int request_id);
```
## EU_SetAutocompleteEmptyText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAutocompleteEmptyText(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_GetAutocompleteValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompleteValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetAutocompleteOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompleteOpen(IntPtr hwnd, int element_id);
```
## EU_GetAutocompleteSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompleteSelected(IntPtr hwnd, int element_id);
```
## EU_GetAutocompleteSuggestionCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompleteSuggestionCount(IntPtr hwnd, int element_id);
```
## EU_GetAutocompleteOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAutocompleteOptions(IntPtr hwnd, int element_id, IntPtr open, IntPtr selected_index, IntPtr suggestion_count, IntPtr loading, IntPtr request_id);
```
## EU_SetMentionsValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMentionsValue(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len);
```
## EU_SetMentionsSuggestions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMentionsSuggestions(IntPtr hwnd, int element_id, byte[] suggestions_bytes, int suggestions_len);
```
## EU_SetMentionsOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMentionsOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetMentionsSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMentionsSelected(IntPtr hwnd, int element_id, int selected_index);
```
## EU_SetMentionsOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMentionsOptions(IntPtr hwnd, int element_id, byte[] trigger_bytes, int trigger_len, int filter_enabled, int insert_space);
```
## EU_SetMentionsFilter

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMentionsFilter(IntPtr hwnd, int element_id, byte[] filter_bytes, int filter_len);
```
## EU_InsertMentionsSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_InsertMentionsSelected(IntPtr hwnd, int element_id);
```
## EU_GetMentionsValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMentionsValue(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetMentionsOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMentionsOpen(IntPtr hwnd, int element_id);
```
## EU_GetMentionsSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMentionsSelected(IntPtr hwnd, int element_id);
```
## EU_GetMentionsSuggestionCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMentionsSuggestionCount(IntPtr hwnd, int element_id);
```
## EU_GetMentionsOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMentionsOptions(IntPtr hwnd, int element_id, IntPtr open, IntPtr selected_index, IntPtr suggestion_count, IntPtr matched_count, IntPtr trigger_code);
```
## EU_SetCascaderOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCascaderOptions(IntPtr hwnd, int element_id, byte[] options_bytes, int options_len);
```
## EU_SetCascaderValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCascaderValue(IntPtr hwnd, int element_id, byte[] selected_bytes, int selected_len);
```
## EU_SetCascaderOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCascaderOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetCascaderAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCascaderAdvancedOptions(IntPtr hwnd, int element_id, int searchable, int lazy_mode);
```
## EU_SetCascaderSearch

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCascaderSearch(IntPtr hwnd, int element_id, byte[] search_bytes, int search_len);
```
## EU_GetCascaderOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCascaderOpen(IntPtr hwnd, int element_id);
```
## EU_GetCascaderOptionCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCascaderOptionCount(IntPtr hwnd, int element_id);
```
## EU_GetCascaderSelectedDepth

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCascaderSelectedDepth(IntPtr hwnd, int element_id);
```
## EU_GetCascaderLevelCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCascaderLevelCount(IntPtr hwnd, int element_id);
```
## EU_GetCascaderAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCascaderAdvancedOptions(IntPtr hwnd, int element_id, IntPtr searchable, IntPtr lazy_mode, IntPtr matched_count, IntPtr last_lazy_level);
```
## EU_SetDatePickerDate

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerDate(IntPtr hwnd, int element_id, int year, int month, int selected_day);
```
## EU_SetDatePickerRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerRange(IntPtr hwnd, int element_id, int min_yyyymmdd, int max_yyyymmdd);
```
## EU_SetDatePickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerOptions(IntPtr hwnd, int element_id, int today_yyyymmdd, int show_today, int date_format);
```
## EU_SetDatePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerOpen(IntPtr hwnd, int element_id, int open);
```
## EU_ClearDatePicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearDatePicker(IntPtr hwnd, int element_id);
```
## EU_DatePickerSelectToday

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_DatePickerSelectToday(IntPtr hwnd, int element_id);
```
## EU_GetDatePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDatePickerOpen(IntPtr hwnd, int element_id);
```
## EU_GetDatePickerValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDatePickerValue(IntPtr hwnd, int element_id);
```
## EU_DatePickerMoveMonth

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_DatePickerMoveMonth(IntPtr hwnd, int element_id, int delta_months);
```
## EU_GetDatePickerRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDatePickerRange(IntPtr hwnd, int element_id, IntPtr min_yyyymmdd, IntPtr max_yyyymmdd);
```
## EU_GetDatePickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDatePickerOptions(IntPtr hwnd, int element_id, IntPtr today_yyyymmdd, IntPtr show_today, IntPtr date_format);
```
## EU_SetDatePickerSelectionRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerSelectionRange(IntPtr hwnd, int element_id, int start_yyyymmdd, int end_yyyymmdd, int enabled);
```
## EU_GetDatePickerSelectionRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDatePickerSelectionRange(IntPtr hwnd, int element_id, IntPtr start_yyyymmdd, IntPtr end_yyyymmdd, IntPtr enabled);
```
## EU_SetDatePickerPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetDatePickerRangeSeparator

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerRangeSeparator(IntPtr hwnd, int element_id, byte[] sep_bytes, int sep_len);
```
## EU_SetDatePickerStartPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerStartPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetDatePickerEndPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerEndPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetDatePickerFormat

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerFormat(IntPtr hwnd, int element_id, byte[] fmt_bytes, int fmt_len);
```
## EU_SetDatePickerAlign

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerAlign(IntPtr hwnd, int element_id, int align);
```
## EU_SetDatePickerMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerMode(IntPtr hwnd, int element_id, int mode);
```
## EU_GetDatePickerMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDatePickerMode(IntPtr hwnd, int element_id);
```
## EU_SetDatePickerMultiSelect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerMultiSelect(IntPtr hwnd, int element_id, int enabled);
```
## EU_GetDatePickerSelectedDates

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDatePickerSelectedDates(IntPtr hwnd, int element_id, byte[] buffer, int buf_size);
```
## EU_SetDatePickerShortcuts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerShortcuts(IntPtr hwnd, int element_id, byte[] shortcuts_bytes, int shortcuts_len);
```
## EU_SetDatePickerDisabledDateCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDatePickerDisabledDateCallback(IntPtr hwnd, int element_id, DateDisabledCallback cb);
```
## EU_CreateDateRangePicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CreateDateRangePicker(IntPtr hwnd, int parent_id, int start_yyyymmdd, int end_yyyymmdd, int x, int y, int w, int h);
```
## EU_SetDateRangePickerValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerValue(IntPtr hwnd, int element_id, int start, int end);
```
## EU_GetDateRangePickerValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateRangePickerValue(IntPtr hwnd, int element_id, IntPtr start, IntPtr end);
```
## EU_SetDateRangePickerRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerRange(IntPtr hwnd, int element_id, int min, int max);
```
## EU_SetDateRangePickerPlaceholders

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerPlaceholders(IntPtr hwnd, int element_id, byte[] start_bytes, int start_len, byte[] end_bytes, int end_len);
```
## EU_SetDateRangePickerSeparator

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerSeparator(IntPtr hwnd, int element_id, byte[] sep_bytes, int sep_len);
```
## EU_SetDateRangePickerFormat

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerFormat(IntPtr hwnd, int element_id, int fmt);
```
## EU_SetDateRangePickerAlign

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerAlign(IntPtr hwnd, int element_id, int align);
```
## EU_SetDateRangePickerShortcuts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerShortcuts(IntPtr hwnd, int element_id, byte[] sc_bytes, int sc_len);
```
## EU_SetDateRangePickerDisabledDateCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerDisabledDateCallback(IntPtr hwnd, int element_id, DateDisabledCallback cb);
```
## EU_SetDateRangePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateRangePickerOpen(IntPtr hwnd, int element_id, int open);
```
## EU_GetDateRangePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateRangePickerOpen(IntPtr hwnd, int element_id);
```
## EU_DateRangePickerClear

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_DateRangePickerClear(IntPtr hwnd, int element_id);
```
## EU_SetTimePickerTime

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerTime(IntPtr hwnd, int element_id, int hour, int minute);
```
## EU_SetTimePickerRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerRange(IntPtr hwnd, int element_id, int min_hhmm, int max_hhmm);
```
## EU_SetTimePickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerOptions(IntPtr hwnd, int element_id, int step_minutes, int time_format);
```
## EU_SetTimePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetTimePickerScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerScroll(IntPtr hwnd, int element_id, int hour_scroll, int minute_scroll);
```
## EU_GetTimePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimePickerOpen(IntPtr hwnd, int element_id);
```
## EU_GetTimePickerValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimePickerValue(IntPtr hwnd, int element_id);
```
## EU_GetTimePickerRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimePickerRange(IntPtr hwnd, int element_id, IntPtr min_hhmm, IntPtr max_hhmm);
```
## EU_GetTimePickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimePickerOptions(IntPtr hwnd, int element_id, IntPtr step_minutes, IntPtr time_format);
```
## EU_GetTimePickerScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimePickerScroll(IntPtr hwnd, int element_id, IntPtr hour_scroll, IntPtr minute_scroll);
```
## EU_SetTimePickerArrowControl

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerArrowControl(IntPtr hwnd, int element_id, int enabled);
```
## EU_GetTimePickerArrowControl

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimePickerArrowControl(IntPtr hwnd, int element_id);
```
## EU_SetTimePickerRangeSelect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerRangeSelect(IntPtr hwnd, int element_id, int enabled, int start_hhmm, int end_hhmm);
```
## EU_SetTimePickerStartPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerStartPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetTimePickerEndPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerEndPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetTimePickerRangeSeparator

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimePickerRangeSeparator(IntPtr hwnd, int element_id, byte[] sep_bytes, int sep_len);
```
## EU_GetTimePickerRangeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimePickerRangeValue(IntPtr hwnd, int element_id, IntPtr start_hhmm, IntPtr end_hhmm, IntPtr enabled);
```
## EU_SetTimeSelectPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimeSelectPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetDateTimePickerDateTime

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerDateTime(IntPtr hwnd, int element_id, int year, int month, int day, int hour, int minute);
```
## EU_SetDateTimePickerRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerRange(IntPtr hwnd, int element_id, int min_yyyymmdd, int max_yyyymmdd, int min_hhmm, int max_hhmm);
```
## EU_SetDateTimePickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerOptions(IntPtr hwnd, int element_id, int today_yyyymmdd, int show_today, int minute_step, int date_format);
```
## EU_SetDateTimePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerOpen(IntPtr hwnd, int element_id, int open);
```
## EU_ClearDateTimePicker

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearDateTimePicker(IntPtr hwnd, int element_id);
```
## EU_DateTimePickerSelectToday

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_DateTimePickerSelectToday(IntPtr hwnd, int element_id);
```
## EU_DateTimePickerSelectNow

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_DateTimePickerSelectNow(IntPtr hwnd, int element_id);
```
## EU_SetDateTimePickerScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerScroll(IntPtr hwnd, int element_id, int hour_scroll, int minute_scroll);
```
## EU_GetDateTimePickerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateTimePickerOpen(IntPtr hwnd, int element_id);
```
## EU_GetDateTimePickerDateValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateTimePickerDateValue(IntPtr hwnd, int element_id);
```
## EU_GetDateTimePickerTimeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateTimePickerTimeValue(IntPtr hwnd, int element_id);
```
## EU_DateTimePickerMoveMonth

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_DateTimePickerMoveMonth(IntPtr hwnd, int element_id, int delta_months);
```
## EU_GetDateTimePickerRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateTimePickerRange(IntPtr hwnd, int element_id, IntPtr min_yyyymmdd, IntPtr max_yyyymmdd, IntPtr min_hhmm, IntPtr max_hhmm);
```
## EU_GetDateTimePickerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateTimePickerOptions(IntPtr hwnd, int element_id, IntPtr today_yyyymmdd, IntPtr show_today, IntPtr minute_step, IntPtr date_format);
```
## EU_GetDateTimePickerScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateTimePickerScroll(IntPtr hwnd, int element_id, IntPtr hour_scroll, IntPtr minute_scroll);
```
## EU_SetDateTimePickerShortcuts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerShortcuts(IntPtr hwnd, int element_id, byte[] shortcuts_bytes, int shortcuts_len);
```
## EU_SetDateTimePickerStartPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerStartPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetDateTimePickerEndPlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerEndPlaceholder(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetDateTimePickerDefaultTime

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerDefaultTime(IntPtr hwnd, int element_id, int hour, int minute);
```
## EU_SetDateTimePickerRangeDefaultTime

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerRangeDefaultTime(IntPtr hwnd, int element_id, int start_hour, int start_minute, int end_hour, int end_minute);
```
## EU_SetDateTimePickerRangeSeparator

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerRangeSeparator(IntPtr hwnd, int element_id, byte[] sep_bytes, int sep_len);
```
## EU_SetDateTimePickerRangeSelect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDateTimePickerRangeSelect(IntPtr hwnd, int element_id, int enabled, int start_date, int start_time, int end_date, int end_time);
```
## EU_GetDateTimePickerRangeValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDateTimePickerRangeValue(IntPtr hwnd, int element_id, IntPtr start_date, IntPtr start_time, IntPtr end_date, IntPtr end_time, IntPtr enabled);
```
## EU_SetTimeSelectTime

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimeSelectTime(IntPtr hwnd, int element_id, int hour, int minute);
```
## EU_SetTimeSelectRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimeSelectRange(IntPtr hwnd, int element_id, int min_hhmm, int max_hhmm);
```
## EU_SetTimeSelectOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimeSelectOptions(IntPtr hwnd, int element_id, int step_minutes, int time_format);
```
## EU_SetTimeSelectOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimeSelectOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetTimeSelectScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTimeSelectScroll(IntPtr hwnd, int element_id, int scroll_row);
```
## EU_GetTimeSelectOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimeSelectOpen(IntPtr hwnd, int element_id);
```
## EU_GetTimeSelectValue

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimeSelectValue(IntPtr hwnd, int element_id);
```
## EU_GetTimeSelectRange

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimeSelectRange(IntPtr hwnd, int element_id, IntPtr min_hhmm, IntPtr max_hhmm);
```
## EU_GetTimeSelectOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimeSelectOptions(IntPtr hwnd, int element_id, IntPtr step_minutes, IntPtr time_format);
```
## EU_GetTimeSelectState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTimeSelectState(IntPtr hwnd, int element_id, IntPtr scroll_row, IntPtr candidate_count, IntPtr group_count, IntPtr active_index);
```
## EU_SetDropdownItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetDropdownSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownSelected(IntPtr hwnd, int element_id, int selected_index);
```
## EU_GetDropdownSelected

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDropdownSelected(IntPtr hwnd, int element_id);
```
## EU_SetDropdownOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownOpen(IntPtr hwnd, int element_id, int open);
```
## EU_GetDropdownOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDropdownOpen(IntPtr hwnd, int element_id);
```
## EU_GetDropdownItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDropdownItemCount(IntPtr hwnd, int element_id);
```
## EU_SetDropdownDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownDisabled(IntPtr hwnd, int element_id, IntPtr indices, int count);
```
## EU_GetDropdownState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDropdownState(IntPtr hwnd, int element_id, IntPtr selected_index, IntPtr item_count, IntPtr disabled_count, IntPtr selected_level, IntPtr hover_index);
```
## EU_SetDropdownOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownOptions(IntPtr hwnd, int element_id, int trigger_mode, int hide_on_click, int split_button, int button_variant, int size, int trigger_style);
```
## EU_GetDropdownOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDropdownOptions(IntPtr hwnd, int element_id, IntPtr trigger_mode, IntPtr hide_on_click, IntPtr split_button, IntPtr button_variant, IntPtr size, IntPtr trigger_style);
```
## EU_SetDropdownItemMeta

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownItemMeta(IntPtr hwnd, int element_id, byte[] icons_bytes, int icons_len, byte[] commands_bytes, int commands_len, IntPtr divided_indices, int divided_count);
```
## EU_GetDropdownItemMeta

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDropdownItemMeta(IntPtr hwnd, int element_id, int item_index, byte[] icon_buffer, int icon_buffer_size, byte[] command_buffer, int command_buffer_size, IntPtr divided, IntPtr disabled, IntPtr level);
```
## EU_SetDropdownCommandCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownCommandCallback(IntPtr hwnd, int element_id, DropdownCommandCallback cb);
```
## EU_SetDropdownMainClickCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDropdownMainClickCallback(IntPtr hwnd, int element_id, ElementClickCallback cb);
```
## EU_SetMenuItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetMenuActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_GetMenuActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuActive(IntPtr hwnd, int element_id);
```
## EU_SetMenuOrientation

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuOrientation(IntPtr hwnd, int element_id, int orientation);
```
## EU_GetMenuOrientation

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuOrientation(IntPtr hwnd, int element_id);
```
## EU_GetMenuItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuItemCount(IntPtr hwnd, int element_id);
```
## EU_SetMenuExpanded

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuExpanded(IntPtr hwnd, int element_id, IntPtr indices, int count);
```
## EU_GetMenuState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr orientation, IntPtr active_level, IntPtr visible_count, IntPtr expanded_count, IntPtr hover_index);
```
## EU_GetMenuActivePath

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuActivePath(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_SetMenuColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuColors(IntPtr hwnd, int element_id, uint bg, uint text_color, uint active_text_color, uint hover_bg, uint disabled_text_color, uint border);
```
## EU_GetMenuColors

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuColors(IntPtr hwnd, int element_id, IntPtr bg, IntPtr text_color, IntPtr active_text_color, IntPtr hover_bg, IntPtr disabled_text_color, IntPtr border);
```
## EU_SetMenuCollapsed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuCollapsed(IntPtr hwnd, int element_id, int collapsed);
```
## EU_GetMenuCollapsed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuCollapsed(IntPtr hwnd, int element_id);
```
## EU_SetMenuItemMeta

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuItemMeta(IntPtr hwnd, int element_id, byte[] icons_bytes, int icons_len, IntPtr group_indices, int group_count, byte[] hrefs_bytes, int hrefs_len, byte[] targets_bytes, int targets_len, byte[] commands_bytes, int commands_len);
```
## EU_GetMenuItemMeta

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMenuItemMeta(IntPtr hwnd, int element_id, int item_index, byte[] icon_buffer, int icon_buffer_size, byte[] href_buffer, int href_buffer_size, byte[] target_buffer, int target_buffer_size, byte[] command_buffer, int command_buffer_size, IntPtr is_group, IntPtr disabled, IntPtr level);
```
## EU_SetMenuSelectCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMenuSelectCallback(IntPtr hwnd, int element_id, MenuSelectCallback cb);
```
## EU_SetAnchorItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAnchorItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetAnchorActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAnchorActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_GetAnchorActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAnchorActive(IntPtr hwnd, int element_id);
```
## EU_GetAnchorItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAnchorItemCount(IntPtr hwnd, int element_id);
```
## EU_SetAnchorTargets

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAnchorTargets(IntPtr hwnd, int element_id, IntPtr positions, int count);
```
## EU_SetAnchorOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAnchorOptions(IntPtr hwnd, int element_id, int scroll_offset, int target_container_id);
```
## EU_SetAnchorScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAnchorScroll(IntPtr hwnd, int element_id, int scroll_position);
```
## EU_GetAnchorState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAnchorState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr scroll_position, IntPtr offset, IntPtr target_position, IntPtr container_id, IntPtr hover_index);
```
## EU_SetBacktopState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBacktopState(IntPtr hwnd, int element_id, int scroll_position, int threshold, int target_position);
```
## EU_GetBacktopVisible

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBacktopVisible(IntPtr hwnd, int element_id);
```
## EU_GetBacktopState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBacktopState(IntPtr hwnd, int element_id, IntPtr scroll_position, IntPtr threshold, IntPtr target_position);
```
## EU_SetBacktopOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBacktopOptions(IntPtr hwnd, int element_id, int scroll_position, int threshold, int target_position, int container_id, int duration_ms);
```
## EU_SetBacktopScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBacktopScroll(IntPtr hwnd, int element_id, int scroll_position);
```
## EU_TriggerBacktop

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerBacktop(IntPtr hwnd, int element_id);
```
## EU_GetBacktopFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBacktopFullState(IntPtr hwnd, int element_id, IntPtr scroll_position, IntPtr threshold, IntPtr target_position, IntPtr container_id, IntPtr visible, IntPtr duration_ms, IntPtr last_scroll_before_jump, IntPtr activated_count);
```
## EU_SetSegmentedItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSegmentedItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetSegmentedActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSegmentedActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_GetSegmentedActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSegmentedActive(IntPtr hwnd, int element_id);
```
## EU_GetSegmentedItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSegmentedItemCount(IntPtr hwnd, int element_id);
```
## EU_SetSegmentedDisabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetSegmentedDisabled(IntPtr hwnd, int element_id, IntPtr indices, int count);
```
## EU_GetSegmentedState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetSegmentedState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr disabled_count, IntPtr hover_index);
```
## EU_SetPageHeaderText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPageHeaderText(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len, byte[] subtitle_bytes, int subtitle_len);
```
## EU_SetPageHeaderBreadcrumbs

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPageHeaderBreadcrumbs(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetPageHeaderActions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPageHeaderActions(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_GetPageHeaderAction

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPageHeaderAction(IntPtr hwnd, int element_id);
```
## EU_SetPageHeaderBackText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPageHeaderBackText(IntPtr hwnd, int element_id, byte[] back_bytes, int back_len);
```
## EU_SetPageHeaderActiveAction

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPageHeaderActiveAction(IntPtr hwnd, int element_id, int action_index);
```
## EU_SetPageHeaderBreadcrumbActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPageHeaderBreadcrumbActive(IntPtr hwnd, int element_id, int breadcrumb_index);
```
## EU_TriggerPageHeaderBack

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerPageHeaderBack(IntPtr hwnd, int element_id);
```
## EU_ResetPageHeaderResult

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ResetPageHeaderResult(IntPtr hwnd, int element_id);
```
## EU_GetPageHeaderState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPageHeaderState(IntPtr hwnd, int element_id, IntPtr active_action, IntPtr action_count, IntPtr active_breadcrumb, IntPtr breadcrumb_count, IntPtr back_clicked_count, IntPtr back_hovered, IntPtr action_hover, IntPtr breadcrumb_hover);
```
## EU_SetAffixText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAffixText(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len, byte[] body_bytes, int body_len);
```
## EU_SetAffixState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAffixState(IntPtr hwnd, int element_id, int scroll_position, int offset);
```
## EU_GetAffixFixed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAffixFixed(IntPtr hwnd, int element_id);
```
## EU_GetAffixState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAffixState(IntPtr hwnd, int element_id, IntPtr scroll_position, IntPtr offset, IntPtr @fixed);
```
## EU_SetAffixOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAffixOptions(IntPtr hwnd, int element_id, int scroll_position, int offset, int container_id, int placeholder_height, int z_index);
```
## EU_GetAffixOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAffixOptions(IntPtr hwnd, int element_id, IntPtr scroll_position, IntPtr offset, IntPtr @fixed, IntPtr container_id, IntPtr placeholder_height, IntPtr fixed_top, IntPtr z_index);
```
## EU_SetWatermarkContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWatermarkContent(IntPtr hwnd, int element_id, byte[] content_bytes, int content_len);
```
## EU_SetWatermarkOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWatermarkOptions(IntPtr hwnd, int element_id, int gap_x, int gap_y, int rotation_degrees, int alpha);
```
## EU_GetWatermarkOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetWatermarkOptions(IntPtr hwnd, int element_id, IntPtr gap_x, IntPtr gap_y, IntPtr rotation_degrees, IntPtr alpha);
```
## EU_SetWatermarkLayer

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWatermarkLayer(IntPtr hwnd, int element_id, int container_id, int overlay, int pass_through, int z_index);
```
## EU_GetWatermarkFullOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetWatermarkFullOptions(IntPtr hwnd, int element_id, IntPtr gap_x, IntPtr gap_y, IntPtr rotation_degrees, IntPtr alpha, IntPtr container_id, IntPtr overlay, IntPtr pass_through, IntPtr z_index, IntPtr tile_count_x, IntPtr tile_count_y);
```
## EU_SetTourSteps

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTourSteps(IntPtr hwnd, int element_id, byte[] steps_bytes, int steps_len);
```
## EU_SetTourActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTourActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_SetTourOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTourOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetTourOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTourOptions(IntPtr hwnd, int element_id, int open, int mask, int target_x, int target_y, int target_w, int target_h);
```
## EU_SetTourTargetElement

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTourTargetElement(IntPtr hwnd, int element_id, int target_element_id, int padding);
```
## EU_SetTourMaskBehavior

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTourMaskBehavior(IntPtr hwnd, int element_id, int pass_through, int close_on_mask);
```
## EU_GetTourActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTourActive(IntPtr hwnd, int element_id);
```
## EU_GetTourOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTourOpen(IntPtr hwnd, int element_id);
```
## EU_GetTourStepCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTourStepCount(IntPtr hwnd, int element_id);
```
## EU_GetTourOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTourOptions(IntPtr hwnd, int element_id, IntPtr open, IntPtr mask, IntPtr target_x, IntPtr target_y, IntPtr target_w, IntPtr target_h);
```
## EU_GetTourFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTourFullState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr step_count, IntPtr open, IntPtr mask, IntPtr target_x, IntPtr target_y, IntPtr target_w, IntPtr target_h, IntPtr target_element_id, IntPtr mask_passthrough, IntPtr close_on_mask, IntPtr last_action, IntPtr change_count);
```
## EU_SetImageSource

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImageSource(IntPtr hwnd, int element_id, byte[] src_bytes, int src_len, byte[] alt_bytes, int alt_len);
```
## EU_SetImageFit

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImageFit(IntPtr hwnd, int element_id, int fit);
```
## EU_SetImagePreview

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImagePreview(IntPtr hwnd, int element_id, int open);
```
## EU_SetImagePreviewEnabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImagePreviewEnabled(IntPtr hwnd, int element_id, int enabled);
```
## EU_SetImagePreviewTransform

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImagePreviewTransform(IntPtr hwnd, int element_id, int scale_percent, int offset_x, int offset_y);
```
## EU_SetImageCacheEnabled

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImageCacheEnabled(IntPtr hwnd, int element_id, int enabled);
```
## EU_SetImageLazy

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImageLazy(IntPtr hwnd, int element_id, int lazy);
```
## EU_SetImagePlaceholder

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImagePlaceholder(IntPtr hwnd, int element_id, byte[] icon_bytes, int icon_len, byte[] text_bytes, int text_len, uint fg, uint bg);
```
## EU_SetImageErrorContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImageErrorContent(IntPtr hwnd, int element_id, byte[] icon_bytes, int icon_len, byte[] text_bytes, int text_len, uint fg, uint bg);
```
## EU_SetImagePreviewList

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImagePreviewList(IntPtr hwnd, int element_id, byte[] sources_bytes, int sources_len, int selected_index);
```
## EU_SetImagePreviewIndex

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetImagePreviewIndex(IntPtr hwnd, int element_id, int index);
```
## EU_GetImageStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetImageStatus(IntPtr hwnd, int element_id);
```
## EU_GetImagePreviewOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetImagePreviewOpen(IntPtr hwnd, int element_id);
```
## EU_GetImageOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetImageOptions(IntPtr hwnd, int element_id, IntPtr fit, IntPtr preview_enabled, IntPtr preview_open, IntPtr status);
```
## EU_GetImageFullOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetImageFullOptions(IntPtr hwnd, int element_id, IntPtr fit, IntPtr preview_enabled, IntPtr preview_open, IntPtr status, IntPtr scale_percent, IntPtr offset_x, IntPtr offset_y, IntPtr cache_enabled, IntPtr reload_count, IntPtr bitmap_width, IntPtr bitmap_height);
```
## EU_GetImageAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetImageAdvancedOptions(IntPtr hwnd, int element_id, IntPtr fit, IntPtr lazy, IntPtr preview_enabled, IntPtr preview_open, IntPtr preview_index, IntPtr preview_count, IntPtr status, IntPtr scale_percent, IntPtr offset_x, IntPtr offset_y);
```
## EU_SetCarouselItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCarouselItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetCarouselActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCarouselActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_SetCarouselOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCarouselOptions(IntPtr hwnd, int element_id, int loop, int indicator_position, int show_arrows, int show_indicators);
```
## EU_SetCarouselBehavior

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCarouselBehavior(IntPtr hwnd, int element_id, int trigger_mode, int arrow_mode, int direction, int carousel_type, int pause_on_hover);
```
## EU_GetCarouselBehavior

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCarouselBehavior(IntPtr hwnd, int element_id, IntPtr trigger_mode, IntPtr arrow_mode, IntPtr direction, IntPtr carousel_type, IntPtr pause_on_hover);
```
## EU_SetCarouselVisual

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCarouselVisual(IntPtr hwnd, int element_id, uint text_color, int text_alpha, int text_font_size, uint odd_bg, uint even_bg, uint panel_bg, uint active_indicator, uint inactive_indicator, int card_scale_percent);
```
## EU_GetCarouselVisual

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCarouselVisual(IntPtr hwnd, int element_id, IntPtr text_color, IntPtr text_alpha, IntPtr text_font_size, IntPtr odd_bg, IntPtr even_bg, IntPtr panel_bg, IntPtr active_indicator, IntPtr inactive_indicator, IntPtr card_scale_percent);
```
## EU_SetCarouselAutoplay

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCarouselAutoplay(IntPtr hwnd, int element_id, int enabled, int interval_ms);
```
## EU_SetCarouselAnimation

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetCarouselAnimation(IntPtr hwnd, int element_id, int transition_ms);
```
## EU_CarouselAdvance

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_CarouselAdvance(IntPtr hwnd, int element_id, int delta);
```
## EU_CarouselTick

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_CarouselTick(IntPtr hwnd, int element_id, int elapsed_ms);
```
## EU_GetCarouselActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCarouselActive(IntPtr hwnd, int element_id);
```
## EU_GetCarouselItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCarouselItemCount(IntPtr hwnd, int element_id);
```
## EU_GetCarouselOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCarouselOptions(IntPtr hwnd, int element_id, IntPtr loop, IntPtr indicator_position, IntPtr show_arrows, IntPtr show_indicators, IntPtr autoplay, IntPtr interval_ms);
```
## EU_GetCarouselFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetCarouselFullState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr previous_index, IntPtr item_count, IntPtr loop, IntPtr indicator_position, IntPtr show_arrows, IntPtr show_indicators, IntPtr autoplay, IntPtr interval_ms, IntPtr autoplay_tick, IntPtr autoplay_elapsed_ms, IntPtr transition_ms, IntPtr transition_progress, IntPtr transition_direction, IntPtr last_action, IntPtr change_count);
```
## EU_SetUploadFiles

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadFiles(IntPtr hwnd, int element_id, byte[] files_bytes, int files_len);
```
## EU_SetUploadFileItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadFileItems(IntPtr hwnd, int element_id, byte[] files_bytes, int files_len);
```
## EU_SetUploadOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadOptions(IntPtr hwnd, int element_id, int multiple, int auto_upload);
```
## EU_SetUploadStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadStyle(IntPtr hwnd, int element_id, int style_mode, int show_file_list, int show_tip, int show_actions, int drop_enabled);
```
## EU_GetUploadStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadStyle(IntPtr hwnd, int element_id, IntPtr style_mode, IntPtr show_file_list, IntPtr show_tip, IntPtr show_actions, IntPtr drop_enabled);
```
## EU_SetUploadTexts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadTexts(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len, byte[] tip_bytes, int tip_len, byte[] trigger_bytes, int trigger_len, byte[] submit_bytes, int submit_len);
```
## EU_SetUploadConstraints

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadConstraints(IntPtr hwnd, int element_id, int limit, int max_size_kb, byte[] accept_bytes, int accept_len);
```
## EU_GetUploadConstraints

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadConstraints(IntPtr hwnd, int element_id, IntPtr limit, IntPtr max_size_kb, byte[] accept_buffer, int accept_buffer_size);
```
## EU_SetUploadPreviewOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadPreviewOpen(IntPtr hwnd, int element_id, int file_index, int open);
```
## EU_GetUploadPreviewState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadPreviewState(IntPtr hwnd, int element_id, IntPtr file_index, IntPtr open);
```
## EU_SetUploadSelectedFiles

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadSelectedFiles(IntPtr hwnd, int element_id, byte[] files_bytes, int files_len);
```
## EU_SetUploadFileStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadFileStatus(IntPtr hwnd, int element_id, int file_index, int status, int progress);
```
## EU_RemoveUploadFile

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_RemoveUploadFile(IntPtr hwnd, int element_id, int file_index);
```
## EU_RetryUploadFile

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_RetryUploadFile(IntPtr hwnd, int element_id, int file_index);
```
## EU_ClearUploadFiles

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearUploadFiles(IntPtr hwnd, int element_id);
```
## EU_OpenUploadFileDialog

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_OpenUploadFileDialog(IntPtr hwnd, int element_id);
```
## EU_StartUpload

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_StartUpload(IntPtr hwnd, int element_id, int file_index);
```
## EU_GetUploadFileCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadFileCount(IntPtr hwnd, int element_id);
```
## EU_GetUploadFileStatus

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadFileStatus(IntPtr hwnd, int element_id, int file_index, IntPtr status, IntPtr progress);
```
## EU_GetUploadSelectedFiles

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadSelectedFiles(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetUploadFileName

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadFileName(IntPtr hwnd, int element_id, int file_index, byte[] buffer, int buffer_size);
```
## EU_GetUploadFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetUploadFullState(IntPtr hwnd, int element_id, IntPtr file_count, IntPtr selected_count, IntPtr last_selected_count, IntPtr upload_request_count, IntPtr retry_count, IntPtr remove_count, IntPtr last_action, IntPtr waiting_count, IntPtr uploading_count, IntPtr success_count, IntPtr failed_count, IntPtr multiple, IntPtr auto_upload);
```
## EU_SetUploadSelectCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadSelectCallback(IntPtr hwnd, int element_id, ElementTextCallback cb);
```
## EU_SetUploadActionCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetUploadActionCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetInfiniteScrollItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfiniteScrollItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_AppendInfiniteScrollItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_AppendInfiniteScrollItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_ClearInfiniteScrollItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearInfiniteScrollItems(IntPtr hwnd, int element_id);
```
## EU_SetInfiniteScrollState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfiniteScrollState(IntPtr hwnd, int element_id, int loading, int no_more, int disabled);
```
## EU_SetInfiniteScrollOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfiniteScrollOptions(IntPtr hwnd, int element_id, int item_height, int gap, int threshold, int style_mode, int show_scrollbar, int show_index);
```
## EU_SetInfiniteScrollTexts

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfiniteScrollTexts(IntPtr hwnd, int element_id, byte[] loading_bytes, int loading_len, byte[] no_more_bytes, int no_more_len, byte[] empty_bytes, int empty_len);
```
## EU_SetInfiniteScrollScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfiniteScrollScroll(IntPtr hwnd, int element_id, int scroll_y);
```
## EU_GetInfiniteScrollFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetInfiniteScrollFullState(IntPtr hwnd, int element_id, IntPtr item_count, IntPtr scroll_y, IntPtr max_scroll, IntPtr content_height, IntPtr viewport_height, IntPtr loading, IntPtr no_more, IntPtr disabled, IntPtr load_count, IntPtr change_count, IntPtr last_action, IntPtr threshold, IntPtr style_mode, IntPtr show_scrollbar, IntPtr show_index);
```
## EU_SetInfiniteScrollLoadCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetInfiniteScrollLoadCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetBreadcrumbItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBreadcrumbItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetBreadcrumbSeparator

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBreadcrumbSeparator(IntPtr hwnd, int element_id, byte[] separator_bytes, int separator_len);
```
## EU_SetBreadcrumbCurrent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBreadcrumbCurrent(IntPtr hwnd, int element_id, int current_index);
```
## EU_TriggerBreadcrumbClick

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerBreadcrumbClick(IntPtr hwnd, int element_id, int item_index);
```
## EU_GetBreadcrumbCurrent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBreadcrumbCurrent(IntPtr hwnd, int element_id);
```
## EU_GetBreadcrumbItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBreadcrumbItemCount(IntPtr hwnd, int element_id);
```
## EU_GetBreadcrumbState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBreadcrumbState(IntPtr hwnd, int element_id, IntPtr current_index, IntPtr item_count);
```
## EU_GetBreadcrumbItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBreadcrumbItem(IntPtr hwnd, int element_id, int item_index, byte[] buffer, int buffer_size);
```
## EU_GetBreadcrumbFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetBreadcrumbFullState(IntPtr hwnd, int element_id, IntPtr current_index, IntPtr item_count, IntPtr hover_index, IntPtr press_index, IntPtr last_clicked_index, IntPtr click_count, IntPtr last_action);
```
## EU_SetBreadcrumbSelectCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetBreadcrumbSelectCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetTabsItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetTabsItemsEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsItemsEx(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetTabsActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_SetTabsActiveName

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsActiveName(IntPtr hwnd, int element_id, byte[] name_bytes, int name_len);
```
## EU_SetTabsType

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsType(IntPtr hwnd, int element_id, int tab_type);
```
## EU_SetTabsPosition

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsPosition(IntPtr hwnd, int element_id, int tab_position);
```
## EU_SetTabsHeaderAlign

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsHeaderAlign(IntPtr hwnd, int element_id, int align);
```
## EU_SetTabsOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsOptions(IntPtr hwnd, int element_id, int tab_type, int closable, int addable);
```
## EU_SetTabsEditable

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsEditable(IntPtr hwnd, int element_id, int editable);
```
## EU_SetTabsContentVisible

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsContentVisible(IntPtr hwnd, int element_id, int visible);
```
## EU_AddTabsItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_AddTabsItem(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_CloseTabsItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_CloseTabsItem(IntPtr hwnd, int element_id, int item_index);
```
## EU_SetTabsScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsScroll(IntPtr hwnd, int element_id, int offset);
```
## EU_TabsScroll

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TabsScroll(IntPtr hwnd, int element_id, int delta);
```
## EU_GetTabsActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsActive(IntPtr hwnd, int element_id);
```
## EU_GetTabsHeaderAlign

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsHeaderAlign(IntPtr hwnd, int element_id);
```
## EU_GetTabsItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsItemCount(IntPtr hwnd, int element_id);
```
## EU_GetTabsState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr tab_type);
```
## EU_GetTabsItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsItem(IntPtr hwnd, int element_id, int item_index, byte[] buffer, int buffer_size);
```
## EU_GetTabsActiveName

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsActiveName(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetTabsItemContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsItemContent(IntPtr hwnd, int element_id, int item_index, byte[] buffer, int buffer_size);
```
## EU_GetTabsFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsFullState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr tab_type, IntPtr closable, IntPtr addable, IntPtr scroll_offset, IntPtr max_scroll_offset, IntPtr hover_index, IntPtr press_index, IntPtr hover_part, IntPtr press_part, IntPtr last_closed_index, IntPtr last_added_index, IntPtr close_count, IntPtr add_count, IntPtr select_count, IntPtr scroll_count, IntPtr last_action);
```
## EU_GetTabsFullStateEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTabsFullStateEx(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr tab_type, IntPtr closable, IntPtr addable, IntPtr scroll_offset, IntPtr max_scroll_offset, IntPtr hover_index, IntPtr press_index, IntPtr hover_part, IntPtr press_part, IntPtr last_closed_index, IntPtr last_added_index, IntPtr close_count, IntPtr add_count, IntPtr select_count, IntPtr scroll_count, IntPtr last_action, IntPtr tab_position, IntPtr editable, IntPtr content_visible, IntPtr active_disabled, IntPtr active_closable);
```
## EU_SetTabsChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetTabsCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsCloseCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetTabsAddCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTabsAddCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetPagination

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPagination(IntPtr hwnd, int element_id, int total, int page_size, int current_page);
```
## EU_SetPaginationCurrent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPaginationCurrent(IntPtr hwnd, int element_id, int current_page);
```
## EU_SetPaginationPageSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPaginationPageSize(IntPtr hwnd, int element_id, int page_size);
```
## EU_SetPaginationOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPaginationOptions(IntPtr hwnd, int element_id, int show_jumper, int show_size_changer, int visible_page_count);
```
## EU_SetPaginationAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPaginationAdvancedOptions(IntPtr hwnd, int element_id, int background, int small_style, int hide_on_single_page);
```
## EU_SetPaginationPageSizeOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPaginationPageSizeOptions(IntPtr hwnd, int element_id, IntPtr sizes, int count);
```
## EU_SetPaginationJumpPage

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPaginationJumpPage(IntPtr hwnd, int element_id, int jump_page);
```
## EU_TriggerPaginationJump

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerPaginationJump(IntPtr hwnd, int element_id);
```
## EU_NextPaginationPageSize

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_NextPaginationPageSize(IntPtr hwnd, int element_id);
```
## EU_GetPaginationCurrent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPaginationCurrent(IntPtr hwnd, int element_id);
```
## EU_GetPaginationPageCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPaginationPageCount(IntPtr hwnd, int element_id);
```
## EU_GetPaginationState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPaginationState(IntPtr hwnd, int element_id, IntPtr total, IntPtr page_size, IntPtr current_page, IntPtr page_count);
```
## EU_GetPaginationFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPaginationFullState(IntPtr hwnd, int element_id, IntPtr total, IntPtr page_size, IntPtr current_page, IntPtr page_count, IntPtr jump_page, IntPtr visible_page_count, IntPtr show_jumper, IntPtr show_size_changer, IntPtr hover_part, IntPtr press_part, IntPtr change_count, IntPtr size_change_count, IntPtr jump_count, IntPtr last_action);
```
## EU_GetPaginationAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPaginationAdvancedOptions(IntPtr hwnd, int element_id, IntPtr background, IntPtr small_style, IntPtr hide_on_single_page);
```
## EU_SetPaginationChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPaginationChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetStepsItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetStepsDetailItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsDetailItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetStepsIconItems

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsIconItems(IntPtr hwnd, int element_id, byte[] items_bytes, int items_len);
```
## EU_SetStepsActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsActive(IntPtr hwnd, int element_id, int active_index);
```
## EU_SetStepsDirection

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsDirection(IntPtr hwnd, int element_id, int direction);
```
## EU_SetStepsOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsOptions(IntPtr hwnd, int element_id, int space, int align_center, int simple, int finish_status, int process_status);
```
## EU_GetStepsOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStepsOptions(IntPtr hwnd, int element_id, IntPtr space, IntPtr align_center, IntPtr simple, IntPtr finish_status, IntPtr process_status);
```
## EU_SetStepsStatuses

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsStatuses(IntPtr hwnd, int element_id, IntPtr statuses, int count);
```
## EU_TriggerStepsClick

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerStepsClick(IntPtr hwnd, int element_id, int item_index);
```
## EU_GetStepsActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStepsActive(IntPtr hwnd, int element_id);
```
## EU_GetStepsItemCount

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStepsItemCount(IntPtr hwnd, int element_id);
```
## EU_GetStepsState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStepsState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr direction);
```
## EU_GetStepsItem

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStepsItem(IntPtr hwnd, int element_id, int item_index, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetStepsFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStepsFullState(IntPtr hwnd, int element_id, IntPtr active_index, IntPtr item_count, IntPtr direction, IntPtr hover_index, IntPtr press_index, IntPtr last_clicked_index, IntPtr click_count, IntPtr change_count, IntPtr last_action, IntPtr active_status, IntPtr failed_count);
```
## EU_GetStepsVisualState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetStepsVisualState(IntPtr hwnd, int element_id, IntPtr space, IntPtr align_center, IntPtr simple, IntPtr finish_status, IntPtr process_status, IntPtr icon_count);
```
## EU_SetStepsChangeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetStepsChangeCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetAlertDescription

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertDescription(IntPtr hwnd, int element_id, byte[] desc_bytes, int desc_len);
```
## EU_SetAlertType

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertType(IntPtr hwnd, int element_id, int alert_type);
```
## EU_SetAlertEffect

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertEffect(IntPtr hwnd, int element_id, int effect);
```
## EU_SetAlertClosable

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertClosable(IntPtr hwnd, int element_id, int closable);
```
## EU_SetAlertAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertAdvancedOptions(IntPtr hwnd, int element_id, int show_icon, int center, int wrap_description);
```
## EU_GetAlertAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAlertAdvancedOptions(IntPtr hwnd, int element_id, IntPtr show_icon, IntPtr center, IntPtr wrap_description);
```
## EU_SetAlertCloseText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertCloseText(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_GetAlertText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAlertText(IntPtr hwnd, int element_id, int text_type, byte[] out_bytes, int out_len);
```
## EU_SetAlertClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertClosed(IntPtr hwnd, int element_id, int closed);
```
## EU_TriggerAlertClose

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerAlertClose(IntPtr hwnd, int element_id);
```
## EU_GetAlertClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAlertClosed(IntPtr hwnd, int element_id);
```
## EU_GetAlertOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAlertOptions(IntPtr hwnd, int element_id, IntPtr alert_type, IntPtr effect, IntPtr closable, IntPtr closed);
```
## EU_GetAlertFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetAlertFullState(IntPtr hwnd, int element_id, IntPtr alert_type, IntPtr effect, IntPtr closable, IntPtr closed, IntPtr close_hover, IntPtr close_down, IntPtr close_count, IntPtr last_action);
```
## EU_SetAlertCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetAlertCloseCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetResultSubtitle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetResultSubtitle(IntPtr hwnd, int element_id, byte[] subtitle_bytes, int subtitle_len);
```
## EU_SetResultType

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetResultType(IntPtr hwnd, int element_id, int result_type);
```
## EU_SetResultActions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetResultActions(IntPtr hwnd, int element_id, byte[] actions_bytes, int actions_len);
```
## EU_GetResultAction

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetResultAction(IntPtr hwnd, int element_id);
```
## EU_GetResultOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetResultOptions(IntPtr hwnd, int element_id, IntPtr result_type, IntPtr action_count, IntPtr last_action);
```
## EU_SetResultExtraContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetResultExtraContent(IntPtr hwnd, int element_id, byte[] content_bytes, int content_len);
```
## EU_TriggerResultAction

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerResultAction(IntPtr hwnd, int element_id, int action_index);
```
## EU_GetResultText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetResultText(IntPtr hwnd, int element_id, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetResultActionText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetResultActionText(IntPtr hwnd, int element_id, int action_index, byte[] buffer, int buffer_size);
```
## EU_GetResultFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetResultFullState(IntPtr hwnd, int element_id, IntPtr result_type, IntPtr action_count, IntPtr last_action, IntPtr hover_action, IntPtr press_action, IntPtr action_click_count, IntPtr last_action_source, IntPtr has_extra_content);
```
## EU_SetResultActionCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetResultActionCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetMessageBoxBeforeClose

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMessageBoxBeforeClose(IntPtr hwnd, int element_id, int delay_ms, byte[] loading_bytes, int loading_len);
```
## EU_SetMessageBoxInput

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMessageBoxInput(IntPtr hwnd, int element_id, byte[] value_bytes, int value_len, byte[] placeholder_bytes, int placeholder_len, byte[] pattern_bytes, int pattern_len, byte[] error_bytes, int error_len);
```
## EU_GetMessageBoxInput

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMessageBoxInput(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetMessageBoxFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMessageBoxFullState(IntPtr hwnd, int element_id, IntPtr box_type, IntPtr show_cancel, IntPtr center, IntPtr rich, IntPtr distinguish, IntPtr prompt, IntPtr confirm_loading, IntPtr input_error_visible, IntPtr last_action, IntPtr timer_elapsed_ms);
```
## EU_SetMessageText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMessageText(IntPtr hwnd, int element_id, byte[] bytes, int len);
```
## EU_SetMessageOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMessageOptions(IntPtr hwnd, int element_id, int message_type, int closable, int center, int rich, int duration_ms, int offset);
```
## EU_SetMessageClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMessageClosed(IntPtr hwnd, int element_id, int closed);
```
## EU_GetMessageOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMessageOptions(IntPtr hwnd, int element_id, IntPtr message_type, IntPtr closable, IntPtr center, IntPtr rich, IntPtr duration_ms, IntPtr closed, IntPtr offset);
```
## EU_GetMessageFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetMessageFullState(IntPtr hwnd, int element_id, IntPtr message_type, IntPtr closable, IntPtr center, IntPtr rich, IntPtr duration_ms, IntPtr closed, IntPtr close_hover, IntPtr close_down, IntPtr close_count, IntPtr last_action, IntPtr timer_elapsed_ms, IntPtr timer_running, IntPtr stack_index, IntPtr stack_gap, IntPtr offset);
```
## EU_TriggerMessageClose

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerMessageClose(IntPtr hwnd, int element_id);
```
## EU_SetMessageCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetMessageCloseCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetNotificationBody

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationBody(IntPtr hwnd, int element_id, byte[] body_bytes, int body_len);
```
## EU_SetNotificationType

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationType(IntPtr hwnd, int element_id, int notify_type);
```
## EU_SetNotificationClosable

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationClosable(IntPtr hwnd, int element_id, int closable);
```
## EU_SetNotificationPlacement

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationPlacement(IntPtr hwnd, int element_id, int placement, int offset);
```
## EU_SetNotificationRichMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationRichMode(IntPtr hwnd, int element_id, int rich);
```
## EU_SetNotificationOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationOptions(IntPtr hwnd, int element_id, int notify_type, int closable, int duration_ms);
```
## EU_SetNotificationClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationClosed(IntPtr hwnd, int element_id, int closed);
```
## EU_GetNotificationClosed

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetNotificationClosed(IntPtr hwnd, int element_id);
```
## EU_GetNotificationOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetNotificationOptions(IntPtr hwnd, int element_id, IntPtr notify_type, IntPtr closable, IntPtr duration_ms, IntPtr closed);
```
## EU_SetNotificationStack

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationStack(IntPtr hwnd, int element_id, int stack_index, int stack_gap);
```
## EU_TriggerNotificationClose

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerNotificationClose(IntPtr hwnd, int element_id);
```
## EU_GetNotificationText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetNotificationText(IntPtr hwnd, int element_id, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetNotificationFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetNotificationFullState(IntPtr hwnd, int element_id, IntPtr notify_type, IntPtr closable, IntPtr duration_ms, IntPtr closed, IntPtr close_hover, IntPtr close_down, IntPtr close_count, IntPtr last_action, IntPtr timer_elapsed_ms, IntPtr timer_running, IntPtr stack_index, IntPtr stack_gap);
```
## EU_GetNotificationFullStateEx

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetNotificationFullStateEx(IntPtr hwnd, int element_id, IntPtr notify_type, IntPtr closable, IntPtr duration_ms, IntPtr closed, IntPtr close_hover, IntPtr close_down, IntPtr close_count, IntPtr last_action, IntPtr timer_elapsed_ms, IntPtr timer_running, IntPtr stack_index, IntPtr stack_gap, IntPtr placement, IntPtr offset, IntPtr rich);
```
## EU_SetNotificationCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetNotificationCloseCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetLoadingActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLoadingActive(IntPtr hwnd, int element_id, int active);
```
## EU_SetLoadingText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLoadingText(IntPtr hwnd, int element_id, byte[] text_bytes, int text_len);
```
## EU_SetLoadingOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLoadingOptions(IntPtr hwnd, int element_id, int active, int fullscreen, int progress);
```
## EU_SetLoadingStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLoadingStyle(IntPtr hwnd, int element_id, uint background, uint spinner_color, uint text_color, int spinner_type, int lock_input);
```
## EU_GetLoadingActive

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLoadingActive(IntPtr hwnd, int element_id);
```
## EU_GetLoadingOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLoadingOptions(IntPtr hwnd, int element_id, IntPtr active, IntPtr fullscreen, IntPtr progress);
```
## EU_SetLoadingTarget

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetLoadingTarget(IntPtr hwnd, int element_id, int target_element_id, int padding);
```
## EU_GetLoadingText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLoadingText(IntPtr hwnd, int element_id, byte[] buffer, int buffer_size);
```
## EU_GetLoadingStyle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLoadingStyle(IntPtr hwnd, int element_id, IntPtr background, IntPtr spinner_color, IntPtr text_color, IntPtr spinner_type, IntPtr lock_input);
```
## EU_ShowLoading

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_ShowLoading(IntPtr hwnd, int target_element_id, byte[] text_bytes, int text_len, int fullscreen, int lock_input, uint background, uint spinner_color, uint text_color, int spinner_type);
```
## EU_CloseLoading

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_CloseLoading(IntPtr hwnd, int loading_id);
```
## EU_GetLoadingFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetLoadingFullState(IntPtr hwnd, int element_id, IntPtr active, IntPtr fullscreen, IntPtr progress, IntPtr target_element_id, IntPtr target_padding, IntPtr animation_angle, IntPtr tick_count, IntPtr timer_running, IntPtr last_action);
```
## EU_SetDialogOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetDialogTitle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogTitle(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len);
```
## EU_SetDialogBody

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogBody(IntPtr hwnd, int element_id, byte[] body_bytes, int body_len);
```
## EU_SetDialogOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogOptions(IntPtr hwnd, int element_id, int open, int modal, int closable, int close_on_mask, int draggable, int w, int h);
```
## EU_GetDialogOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogOpen(IntPtr hwnd, int element_id);
```
## EU_GetDialogOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogOptions(IntPtr hwnd, int element_id, IntPtr open, IntPtr modal, IntPtr closable, IntPtr close_on_mask, IntPtr draggable, IntPtr w, IntPtr h);
```
## EU_SetDialogButtons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogButtons(IntPtr hwnd, int element_id, byte[] buttons_bytes, int buttons_len);
```
## EU_TriggerDialogButton

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerDialogButton(IntPtr hwnd, int element_id, int button_index);
```
## EU_GetDialogText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogText(IntPtr hwnd, int element_id, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetDialogButtonText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogButtonText(IntPtr hwnd, int element_id, int button_index, byte[] buffer, int buffer_size);
```
## EU_GetDialogFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDialogFullState(IntPtr hwnd, int element_id, IntPtr open, IntPtr modal, IntPtr closable, IntPtr close_on_mask, IntPtr draggable, IntPtr w, IntPtr h, IntPtr button_count, IntPtr active_button, IntPtr last_button, IntPtr button_click_count, IntPtr close_count, IntPtr last_action, IntPtr offset_x, IntPtr offset_y, IntPtr hover_part, IntPtr press_part);
```
## EU_SetDialogButtonCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDialogButtonCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetDrawerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetDrawerTitle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerTitle(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len);
```
## EU_SetDrawerBody

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerBody(IntPtr hwnd, int element_id, byte[] body_bytes, int body_len);
```
## EU_SetDrawerPlacement

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerPlacement(IntPtr hwnd, int element_id, int placement);
```
## EU_SetDrawerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerOptions(IntPtr hwnd, int element_id, int placement, int open, int modal, int closable, int close_on_mask, int size);
```
## EU_SetDrawerAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerAdvancedOptions(IntPtr hwnd, int element_id, int show_header, int show_close, int close_on_escape, int content_padding, int footer_height, int size_mode, int size_value);
```
## EU_GetDrawerAdvancedOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDrawerAdvancedOptions(IntPtr hwnd, int element_id, IntPtr show_header, IntPtr show_close, IntPtr close_on_escape, IntPtr content_padding, IntPtr footer_height, IntPtr size_mode, IntPtr size_value, IntPtr content_parent_id, IntPtr footer_parent_id, IntPtr close_pending);
```
## EU_GetDrawerContentParent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDrawerContentParent(IntPtr hwnd, int element_id);
```
## EU_GetDrawerFooterParent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDrawerFooterParent(IntPtr hwnd, int element_id);
```
## EU_SetDrawerBeforeCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerBeforeCloseCallback(IntPtr hwnd, int element_id, ElementBeforeCloseCallback cb);
```
## EU_ConfirmDrawerClose

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ConfirmDrawerClose(IntPtr hwnd, int element_id, int allow);
```
## EU_GetDrawerOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDrawerOpen(IntPtr hwnd, int element_id);
```
## EU_GetDrawerOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDrawerOptions(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr modal, IntPtr closable, IntPtr close_on_mask, IntPtr size);
```
## EU_SetDrawerAnimation

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerAnimation(IntPtr hwnd, int element_id, int duration_ms);
```
## EU_TriggerDrawerClose

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerDrawerClose(IntPtr hwnd, int element_id);
```
## EU_GetDrawerText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDrawerText(IntPtr hwnd, int element_id, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetDrawerFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetDrawerFullState(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr modal, IntPtr closable, IntPtr close_on_mask, IntPtr size, IntPtr animation_progress, IntPtr animation_ms, IntPtr tick_count, IntPtr timer_running, IntPtr close_count, IntPtr last_action, IntPtr hover_part, IntPtr press_part);
```
## EU_SetDrawerCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDrawerCloseCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetTooltipContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTooltipContent(IntPtr hwnd, int element_id, byte[] content_bytes, int content_len);
```
## EU_SetTooltipOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTooltipOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetTooltipOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTooltipOptions(IntPtr hwnd, int element_id, int placement, int open, int max_width);
```
## EU_GetTooltipOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTooltipOpen(IntPtr hwnd, int element_id);
```
## EU_GetTooltipOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTooltipOptions(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr max_width);
```
## EU_SetTooltipBehavior

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetTooltipBehavior(IntPtr hwnd, int element_id, int show_delay, int hide_delay, int trigger_mode, int show_arrow);
```
## EU_TriggerTooltip

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerTooltip(IntPtr hwnd, int element_id, int open);
```
## EU_GetTooltipText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTooltipText(IntPtr hwnd, int element_id, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetTooltipFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetTooltipFullState(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr max_width, IntPtr show_arrow, IntPtr show_delay, IntPtr hide_delay, IntPtr trigger_mode, IntPtr timer_running, IntPtr timer_phase, IntPtr open_count, IntPtr close_count, IntPtr last_action, IntPtr popup_x, IntPtr popup_y, IntPtr popup_w, IntPtr popup_h);
```
## EU_SetPopoverOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopoverOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetPopoverContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopoverContent(IntPtr hwnd, int element_id, byte[] content_bytes, int content_len);
```
## EU_SetPopoverTitle

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopoverTitle(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len);
```
## EU_SetPopoverOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopoverOptions(IntPtr hwnd, int element_id, int placement, int open, int popup_width, int popup_height, int closable);
```
## EU_GetPopoverOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopoverOpen(IntPtr hwnd, int element_id);
```
## EU_GetPopoverOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopoverOptions(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr popup_width, IntPtr popup_height, IntPtr closable);
```
## EU_TriggerPopover

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerPopover(IntPtr hwnd, int element_id, int open);
```
## EU_GetPopoverText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopoverText(IntPtr hwnd, int element_id, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetPopoverFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopoverFullState(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr popup_width, IntPtr popup_height, IntPtr closable, IntPtr open_count, IntPtr close_count, IntPtr last_action, IntPtr focus_part, IntPtr close_hover, IntPtr popup_x, IntPtr popup_y, IntPtr popup_w, IntPtr popup_h);
```
## EU_SetPopoverActionCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopoverActionCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetPopconfirmOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopconfirmOpen(IntPtr hwnd, int element_id, int open);
```
## EU_SetPopconfirmOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopconfirmOptions(IntPtr hwnd, int element_id, int placement, int open, int popup_width, int popup_height);
```
## EU_SetPopconfirmContent

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopconfirmContent(IntPtr hwnd, int element_id, byte[] title_bytes, int title_len, byte[] content_bytes, int content_len);
```
## EU_SetPopconfirmButtons

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopconfirmButtons(IntPtr hwnd, int element_id, byte[] confirm_bytes, int confirm_len, byte[] cancel_bytes, int cancel_len);
```
## EU_ResetPopconfirmResult

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ResetPopconfirmResult(IntPtr hwnd, int element_id);
```
## EU_GetPopconfirmOpen

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopconfirmOpen(IntPtr hwnd, int element_id);
```
## EU_GetPopconfirmResult

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopconfirmResult(IntPtr hwnd, int element_id);
```
## EU_GetPopconfirmOptions

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopconfirmOptions(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr popup_width, IntPtr popup_height, IntPtr result);
```
## EU_TriggerPopconfirmResult

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_TriggerPopconfirmResult(IntPtr hwnd, int element_id, int result);
```
## EU_GetPopconfirmText

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopconfirmText(IntPtr hwnd, int element_id, int text_kind, byte[] buffer, int buffer_size);
```
## EU_GetPopconfirmFullState

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopconfirmFullState(IntPtr hwnd, int element_id, IntPtr placement, IntPtr open, IntPtr popup_width, IntPtr popup_height, IntPtr result, IntPtr confirm_count, IntPtr cancel_count, IntPtr result_action, IntPtr focus_part, IntPtr hover_button, IntPtr press_button, IntPtr popup_x, IntPtr popup_y, IntPtr popup_w, IntPtr popup_h);
```
## EU_SetPopconfirmResultCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopconfirmResultCallback(IntPtr hwnd, int element_id, ElementValueCallback cb);
```
## EU_SetElementClickCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementClickCallback(IntPtr hwnd, int element_id, ElementClickCallback cb);
```
## EU_SetElementKeyCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementKeyCallback(IntPtr hwnd, int element_id, ElementKeyCallback cb);
```
## EU_SetWindowResizeCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWindowResizeCallback(IntPtr hwnd, WindowResizeCallback cb);
```
## EU_SetWindowCloseCallback

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWindowCloseCallback(IntPtr hwnd, WindowCloseCallback cb);
```
## EU_SetDarkMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetDarkMode(IntPtr hwnd, int dark_mode);
```
## EU_SetThemeMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetThemeMode(IntPtr hwnd, int mode);
```
## EU_GetThemeMode

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetThemeMode(IntPtr hwnd);
```
## EU_SetThemeColor

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_SetThemeColor(IntPtr hwnd, byte[] token_bytes, int token_len, uint value);
```
## EU_ResetTheme

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ResetTheme(IntPtr hwnd);
```
## EU_InvalidateElement

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_InvalidateElement(IntPtr hwnd, int element_id);
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

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopupAnchorElement(IntPtr hwnd, int popup_id, int anchor_element_id);
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopupPlacement(IntPtr hwnd, int popup_id, int placement, int offset_x, int offset_y);
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopupOpen(IntPtr hwnd, int popup_id, int open);
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetPopupOpen(IntPtr hwnd, int popup_id);
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetPopupDismissBehavior(IntPtr hwnd, int popup_id, int close_on_outside, int close_on_escape);
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetElementPopup(IntPtr hwnd, int element_id, int popup_id, int trigger);
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_ClearElementPopup(IntPtr hwnd, int element_id, int trigger);
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern int EU_GetElementPopup(IntPtr hwnd, int element_id, int trigger);
```

`EU_SetPopup*` 支持 `Popover`、`Menu` 和 `Dropdown`。`EU_SetElementPopup` 的 `trigger`：`0=左键`、`1=右键`、`2=悬停`、`3=聚焦`、`4=手动`。

`EU_SetTabsChromeMode`、`EU_GetTabsChromeMode`、`EU_SetTabsItemChromeState`、`EU_GetTabsItemChromeState`、`EU_SetMenuItemIcon`、`EU_SetMenuItemShortcut`、`EU_SetMenuItemChecked`、`EU_SetPopoverAnchorElement`、`EU_SetPopoverDismissBehavior`、`EU_SetPopupAnchorElement`、`EU_SetPopupPlacement`、`EU_SetPopupOpen`、`EU_GetPopupOpen`、`EU_SetPopupDismissBehavior`、`EU_SetElementPopup`、`EU_ClearElementPopup`、`EU_GetElementPopup`、`EU_SetWindowDragRegion`、`EU_SetContainerFlexLayout`、`EU_SetChromeThemePreset`、`EU_SetThemeToken`、`EU_GetThemeToken`、`EU_SetHighContrastMode`、`EU_SetIncognitoMode`。

易语言命令左侧可使用中文名，例如 `创建工具栏图标按钮`、`创建地址栏`、`创建浏览内容占位区`；右侧 DLL 入口名保持上述 `EU_` 导出名。
## Window Frame 通用窗口框架 API

C# P/Invoke 应补充以下入口：

```text
EU_CreateWindowEx
EU_GetWindowFrameFlags
EU_SetWindowFrameFlags
EU_SetWindowRoundedCorners
EU_SetWindowResizeBorder
EU_GetWindowResizeBorder
EU_SetWindowNoDragRegion
EU_ClearWindowNoDragRegions
EU_SetElementWindowCommand
EU_GetElementWindowCommand
```

圆角窗口绑定：

```csharp
[DllImport("new_emoji.dll", CallingConvention = CallingConvention.StdCall)]
public static extern void EU_SetWindowRoundedCorners(IntPtr hwnd, int enabled, int radius);
```

命名统一使用 Window Frame / 窗口框架，不使用 ChromeFlags；浏览器式外壳只是 `frame_flags` 的推荐组合。

`EU_SetWindowRoundedCorners(hwnd, enabled, radius)` 会设置 Windows 窗口外形圆角；支持 DWM 圆角的系统会优先使用系统抗锯齿圆角，Win10 回退到 per-pixel alpha 分层窗口并通过 `UpdateLayeredWindow(ULW_ALPHA)` 提交，内部按当前 DPI / 屏幕缩放换算逻辑半径。`enabled=0` 或 `radius<=0` 会恢复矩形窗口。
