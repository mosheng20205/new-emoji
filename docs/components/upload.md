# Upload 上传

## 简介

`Upload` 是纯 D2D 上传入口组件，已补齐 Element Upload 常见样式：普通列表、头像上传、图片卡片、自定义图片卡片、图片列表、拖拽上传和手动上传。

组件负责系统文件选择、单选/多选、文件类型过滤、数量/大小限制、系统拖入、缩略图展示、状态读回和动作回调。真实上传网络请求由宿主程序处理。

## 样式模式

| 值 | 样式 | 说明 |
|---|---|---|
| `0` | 普通列表 | 按钮 + 提示 + 文件列表 |
| `1` | 头像上传 | 方形头像入口，适合单文件图片 |
| `2` | 图片卡片 | 图片墙 + 加号卡片 |
| `3` | 自定义图片卡片 | 图片墙 + 预览/下载/删除操作层 |
| `4` | 图片列表 | 缩略图 + 文件名 + 状态 |
| `5` | 拖拽上传 | 虚线拖拽区域，支持系统拖入 |
| `6` | 手动上传 | 选择文件 + 上传到服务器按钮 |

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateUpload` |
| 组件分类 | 媒体/工具 |
| Python helper | `create_upload` |
| 易语言命令 | `创建上传` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_SetUploadOptions` | 设置单选/多选、是否自动上传 |
| `EU_SetUploadStyle` / `EU_GetUploadStyle` | 设置/读取样式模式、文件列表、提示、操作按钮和系统拖拽开关 |
| `EU_SetUploadTexts` | 设置标题、提示、选择按钮、手动上传按钮文案 |
| `EU_SetUploadConstraints` / `EU_GetUploadConstraints` | 设置/读取数量限制、大小限制和类型过滤 |
| `EU_OpenUploadFileDialog` | 打开系统文件选择框，支持单选/多选和文件类型过滤 |
| `EU_SetUploadSelectedFiles` | 由宿主写入已选文件，走同一套限制校验 |
| `EU_SetUploadFileItems` | 写入带状态的文件列表 |
| `EU_SetUploadFileStatus` | 更新单个文件状态和进度 |
| `EU_StartUpload` | 将等待/失败文件置为上传中，并触发上传动作回调 |
| `EU_SetUploadPreviewOpen` / `EU_GetUploadPreviewState` | 打开/读取图片预览层 |
| `EU_RemoveUploadFile` / `EU_RetryUploadFile` / `EU_ClearUploadFiles` | 删除、重试、清空 |
| `EU_GetUploadFileCount` / `EU_GetUploadFileStatus` / `EU_GetUploadFileName` / `EU_GetUploadSelectedFiles` / `EU_GetUploadFullState` | 状态读回 |
| `EU_SetUploadSelectCallback` / `EU_SetUploadActionCallback` | 选择回调和动作回调 |

## 类型过滤

`accept` 支持 `.jpg,.png`、`jpg|png`、`image/*`、`image/jpeg`、`image/png` 等写法。过滤同时作用于：

- 系统文件选择对话框
- `EU_SetUploadSelectedFiles`
- Windows 系统文件拖入

## 动作码

| 动作码 | 含义 |
|---|---|
| `1` | 打开系统选择框 |
| `2` | 已选择文件 |
| `3` | 开始上传 |
| `4` | 重试 |
| `5` | 删除 |
| `6` | 清空 |
| `7` | 状态更新 |
| `8` | 预览 |
| `9` | 下载 |
| `10` | 超出数量限制 |
| `11` | 校验失败，`value=1` 表示类型不匹配，`value=2` 表示大小超限 |
| `12` | 系统拖入 |

## Python 示例

```python
upload = ui.create_upload(
    hwnd, root,
    "📤 点击或拖拽文件到此处上传",
    "只能上传 JPG/PNG 图片，且不超过 500KB",
    [],
    40, 80, 520, 240,
)
ui.set_upload_options(hwnd, upload, multiple=True, auto_upload=False)
ui.set_upload_style(hwnd, upload, style_mode=5, drop_enabled=True)
ui.set_upload_constraints(hwnd, upload, limit=3, max_size_kb=500, accept=".jpg,.png")
```

## 测试

优先运行 `tests/python/test_upload_complete_components.py`。该测试覆盖样式 Set/Get、单选/多选限制、类型过滤、大小限制、预览、状态更新和手动上传动作。
