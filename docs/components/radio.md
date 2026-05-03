# Radio 单选框 🔘

`Radio` 用于在一组选项中选择一个值。当前封装已覆盖 Element 常见用法：普通单选、禁用态、选中禁用、原生 `RadioGroup`、按钮型单选、边框样式、尺寸、value/label 语义、整组禁用、单项禁用、鼠标与键盘交互。

## 能力概览

| 能力 | 状态 |
|---|---|
| 独立 Radio | 已完成 |
| checked / group_name 兼容 API | 已完成 |
| value / label 语义 | 已完成，显示文本为 text，业务值为 value |
| border 外观 | 已完成 |
| size=default/medium/small/mini | 已完成 |
| 原生 RadioGroup | 已完成 |
| RadioButton 按钮样式 | 已完成，作为 RadioGroup 的 `style=1` |
| 单项 disabled | 已完成 |
| group disabled | 已完成 |
| 键盘方向键、Home/End、Enter/Space | 已完成 |

## C API

### 独立 Radio

| API | 说明 |
|---|---|
| `EU_CreateRadio` | 创建普通单选框 |
| `EU_SetRadioChecked` / `EU_GetRadioChecked` | 设置/读取选中状态 |
| `EU_SetRadioGroup` / `EU_GetRadioGroup` | 设置/读取旧版分组名，保留兼容 |
| `EU_SetRadioValue` / `EU_GetRadioValue` | 设置/读取业务值 |
| `EU_SetRadioOptions` / `EU_GetRadioOptions` | 设置/读取 `border` 与 `size` |

### 原生 RadioGroup

| API | 说明 |
|---|---|
| `EU_CreateRadioGroup` | 创建原生单选组 |
| `EU_SetRadioGroupItems` | 设置组内项目 |
| `EU_SetRadioGroupValue` / `EU_GetRadioGroupValue` | 设置/读取当前选中 value |
| `EU_GetRadioGroupSelectedIndex` | 读取当前选中索引 |
| `EU_SetRadioGroupOptions` / `EU_GetRadioGroupOptions` | 设置/读取整组禁用、样式、尺寸 |
| `EU_GetRadioGroupState` | 读取完整状态：选中索引、项目数、禁用数、hover、press、last_action |
| `EU_SetRadioGroupChangeCallback` | 设置选中变化回调 |

`RadioGroup` 的 items 文本格式为 UTF-8，每行一项，列用 Tab 分隔：

```text
显示文本\t值\t禁用(0/1)
上海 🏙️\t上海\t0
北京 🏛️\t北京\t1
深圳 🌊\t深圳\t0
```

Python helper 会自动把 tuple/list/dict 转成该格式。

## Python 示例

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🔘 Radio 单选示例", 240, 120, 1180, 760)
root = ui.create_container(hwnd, 0, 0, 0, 1140, 700)

ui.create_radio(hwnd, root, "备选项 A 🚀", True, 40, 50, 150, 36, value="1")
ui.create_radio(hwnd, root, "备选项 B ✨", False, 210, 50, 150, 36, value="2", border=True)

ui.create_radio_group(
    hwnd, root,
    [("上海 🏙️", "上海", False), ("北京 🏛️", "北京", True), ("深圳 🌊", "深圳", False)],
    value="上海",
    style=1,   # 0 普通，1 按钮，2 边框
    size=2,    # 0 default，1 medium，2 small，3 mini
    x=40, y=110, w=520, h=38,
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。所有文本都按 UTF-8 字节数组 + 长度传递。

## 测试

优先运行：

```powershell
python .\tests\python\test_radio_complete_components.py
```

该测试覆盖创建、value 读写、options 读写、旧 group_name 互斥、原生 RadioGroup、按钮样式、边框样式、单项禁用、整组禁用、鼠标点击、键盘切换、中文与 emoji 首屏展示。
