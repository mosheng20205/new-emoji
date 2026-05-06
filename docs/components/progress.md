# Progress 进度条

## 简介

`Progress` 是 new_emoji 的数据展示组件，当前状态：**已完成**。

本轮已补齐 Element UI `el-progress` 对应样式：条形、文字内显、状态色、自定义颜色、颜色分段、圆形进度、仪表盘进度、完成文本、模板文本、Set/Get、Python 封装、易语言 DLL 命令、独立测试和 `component_gallery.py` 专属桌面端演示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateProgress` |
| 组件分类 | 数据展示 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_progress` |
| 易语言命令 | `DLL命令/易语言DLL命令.md` |

## 类型与状态

`progress_type`：

| 值 | 样式 |
|---|---|
| `0` | 条形进度条 |
| `1` | 圆形进度条 |
| `2` | 仪表盘进度条，270 度弧线，底部留缺口 |

`status`：

| 值 | 状态 |
|---|---|
| `0` | 默认 |
| `1` | 成功 |
| `2` | 警告 |
| `3` | 异常 |

颜色优先级：颜色分段 > 静态填充色 > 状态色 > 主题默认色。轨道色、文字色只有显式设置时覆盖主题。

## 文本格式

`EU_SetProgressFormatOptions(text_format, striped)` 的 `text_format`：

| 值 | 文本 |
|---|---|
| `0` | 百分比，例如 `70%` |
| `1` | 中文状态 + 百分比 |
| `2` | 组件标签 + 百分比 |
| `3` | 满值文本，`100%` 显示完成文本，非满显示百分比 |
| `4` | 模板文本，支持 `{percentage}`、`{percent}`、`{status}` |

`text_inside` 只影响条形进度条；圆形和仪表盘始终把文本绘制在中心。

## 颜色分段协议

`EU_SetProgressColorStops` 使用 UTF-8 字节集：

```text
颜色<TAB>百分比|颜色<TAB>百分比
```

颜色支持 `0xAARRGGBB` 和 `#RRGGBB`；百分比会钳制到 `0-100`，内部按百分比升序使用。传入空文本会清空分段并恢复默认颜色链路。

示例：

```text
#F56C6C	20|#E6A23C	40|#5CB87A	60|#1989FA	80|#6F7AD3	100
```

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateProgress` | 创建 Progress |
| `EU_SetProgressPercentage` / `EU_GetProgressPercentage` | 设置/读取百分比，自动钳制到 `0-100` |
| `EU_SetProgressStatus` / `EU_GetProgressStatus` | 设置/读取状态 |
| `EU_SetProgressShowText` | 显示或隐藏文本 |
| `EU_SetProgressOptions` / `EU_GetProgressOptions` | 设置/读取类型、线宽和文本显示 |
| `EU_SetProgressFormatOptions` / `EU_GetProgressFormatOptions` | 设置/读取文本格式和条纹标记 |
| `EU_SetProgressTextInside` / `EU_GetProgressTextInside` | 设置/读取条形文字内显 |
| `EU_SetProgressColors` / `EU_GetProgressColors` | 设置/读取填充色、轨道色、文字色 |
| `EU_SetProgressColorStops` | 设置颜色分段 |
| `EU_GetProgressColorStopCount` | 读取颜色分段数量 |
| `EU_GetProgressColorStop` | 按索引读取颜色分段项 |
| `EU_SetProgressCompleteText` / `EU_GetProgressCompleteText` | 设置/读取满值文本 |
| `EU_SetProgressTextTemplate` / `EU_GetProgressTextTemplate` | 设置/读取模板文本 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("📈 进度条演示", 240, 120, 980, 680)
root = ui.create_container(hwnd, 0, 0, 0, 940, 620)

ui.create_progress(hwnd, root, "构建进度", 50, 0, 40, 40, 420, 34)
ui.create_progress(hwnd, root, "完成文本", 100, 0, 40, 88, 420, 34, text_format=3, complete_text="满")
ui.create_progress(hwnd, root, "内显文本", 70, 0, 40, 136, 420, 34, stroke_width=26, text_inside=True)
ui.create_progress(hwnd, root, "圆形", 100, 1, 520, 40, 120, 120, progress_type=1, stroke_width=10)
ui.create_progress(
    hwnd, root, "仪表盘", 66, 0, 680, 40, 140, 120,
    progress_type=2,
    stroke_width=12,
    color_stops=[
        (0xFFF56C6C, 20),
        (0xFFE6A23C, 40),
        (0xFF5CB87A, 60),
        (0xFF1989FA, 80),
        (0xFF6F7AD3, 100),
    ],
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，例如“设置进度条颜色”“设置进度条颜色分段”“设置进度条文本内显”“设置进度条完成文本”“设置进度条文本模板”；DLL 入口名保持真实 `EU_` 导出名。

## 测试

优先运行：

```powershell
python tests/python/test_progress_complete_components.py
python tests/python/test_new_emoji.py
```

Gallery 专页验证：

```powershell
$env:NEW_EMOJI_GALLERY_PAGE='data'
$env:NEW_EMOJI_GALLERY_COMPONENT='Progress'
$env:NEW_EMOJI_GALLERY_SECONDS='8'
python examples/python/component_gallery.py
```

## 文档维护

如果 `Progress` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`DLL命令/易语言DLL命令.md` 和 `src/new_emoji.def`。
