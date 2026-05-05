# Image 图片

## 简介

`Image` 是 new_emoji 的媒体/工具组件。当前状态：**已完成**。

已补齐 Element UI 图片组件对应能力：`fill / contain / cover / none / scale-down` 五种适配、本地路径、HTTP/HTTPS 远程图片异步加载、默认/自定义占位、默认/自定义失败、视口懒加载、预览图片列表、上一张/下一张、键盘左右切换、Esc 关闭、缩放偏移、状态读回、Python 封装、易语言命令文档、专项测试和 `component_gallery.py` 中文 emoji 全样式演示。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateImage` |
| 组件分类 | 媒体/工具 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_image` |
| 易语言命令 | `DLL命令/易语言DLL命令.md` 中的 `创建图片` |

## 适配枚举

| 值 | 名称 | 说明 |
|---|---|---|
| `0` | `contain` | 保持比例完整显示 |
| `1` | `cover` | 保持比例覆盖容器，超出裁切 |
| `2` | `fill` | 拉伸填满容器 |
| `3` | `none` | 原图尺寸居中显示，超出裁切 |
| `4` | `scale-down` | 原图小于容器时原尺寸显示，否则按 contain 缩小 |

## 状态枚举

| 值 | 状态 |
|---|---|
| `0` | 占位/空 |
| `1` | 已加载 |
| `2` | 加载失败 |
| `3` | 加载中 |
| `4` | 懒加载等待可见 |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateImage` | 创建图片组件 |
| `EU_SetImageSource` | 设置本地或 HTTP/HTTPS 图片来源和替代文本 |
| `EU_SetImageFit` | 设置适配方式，兼容旧值并支持五种 fit |
| `EU_SetImageLazy` | 设置是否启用视口懒加载 |
| `EU_SetImagePlaceholder` | 设置占位图标、文字、前景色和背景色 |
| `EU_SetImageErrorContent` | 设置失败图标、文字、前景色和背景色 |
| `EU_SetImagePreview` | 打开或关闭预览 |
| `EU_SetImagePreviewEnabled` | 启用或禁用预览 |
| `EU_SetImagePreviewTransform` | 设置预览缩放百分比和偏移 |
| `EU_SetImagePreviewList` | 设置预览图片列表和当前索引 |
| `EU_SetImagePreviewIndex` | 切换预览图片索引 |
| `EU_SetImageCacheEnabled` | 设置位图缓存开关 |
| `EU_GetImageStatus` | 读取加载状态 |
| `EU_GetImagePreviewOpen` | 读取预览是否打开 |
| `EU_GetImageOptions` | 读取基础选项 |
| `EU_GetImageFullOptions` | 读取完整旧版选项，保持兼容 |
| `EU_GetImageAdvancedOptions` | 读取 fit、lazy、预览列表、状态、缩放和偏移 |

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("🖼️ 图片 示例", 240, 120, 960, 680)
root = ui.create_container(hwnd, 0, 0, 0, 920, 600)

image_id = ui.create_image(hwnd, root, "C:/demo/cover.png", "🖼️ 本地图片", "cover", 28, 48, 220, 160)
ui.set_image_placeholder(hwnd, image_id, "⏳", "图片加载中", 0xFF409EFF, 0xFFEAF4FF)
ui.set_image_error_content(hwnd, image_id, "🧯", "图片读取失败", 0xFFF56C6C, 0xFFFFF0F0)
ui.set_image_preview_list(hwnd, image_id, ["C:/demo/cover.png", "https://example.com/photo.jpg"], 0)
ui.set_image_preview(hwnd, image_id, True)

ui.dll.EU_ShowWindow(hwnd, 1)
```

Python helper 的 `fit` 参数同时支持整数和字符串：`"fill" / "contain" / "cover" / "none" / "scale-down"`。

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，DLL 入口名保持真实 `EU_` 导出名。

## 测试

优先运行：

- `tests/python/test_image_complete_components.py`
- `tests/python/test_media_components.py`
- `tests/python/test_media_utility_enhanced_components.py`
- `tests/python/test_new_emoji.py`

Gallery 验证可运行：

```powershell
$env:NEW_EMOJI_GALLERY_PAGE="media"
$env:NEW_EMOJI_GALLERY_COMPONENT="Image"
python examples/python/component_gallery.py
```

## 文档维护

如果 `Image` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/components/manifest.json`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`examples/python/component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
