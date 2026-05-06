# Avatar 头像

## 简介

`Avatar` 是 new_emoji 的数据展示组件。当前状态：**已完成**。

已补齐圆形/方形、不同尺寸、图片/图标/文字三种内容、本地与 http/https 图片源、失败备用图片、错误文本、五种图片适配方式、状态读回、Python 封装、易语言命令和 `component_gallery.py` 专属中文 emoji 演示页。

## 创建

| 项目 | 值 |
|---|---|
| 创建导出 | `EU_CreateAvatar` |
| 组件分类 | 数据展示 |
| Python helper | `examples/python/new_emoji_ui.py` 中的 `create_avatar` |
| 易语言命令 | 见 `DLL命令/易语言DLL命令.md` |

## 相关 API

| API | 说明 |
|---|---|
| `EU_CreateAvatar` | 创建头像，传入文本、形状和逻辑坐标尺寸 |
| `EU_SetAvatarShape` | 设置形状：`0` 圆形，`1` 方形/圆角方形 |
| `EU_SetAvatarSource` | 设置主图片源，支持本地路径和 `http://` / `https://` |
| `EU_SetAvatarFallbackSource` | 设置备用图片源，主图片失败后显示 |
| `EU_SetAvatarIcon` | 设置图标/emoji 内容，无图片或等待状态时显示 |
| `EU_SetAvatarErrorText` | 设置错误文本，图片失败且无备用图时显示 |
| `EU_SetAvatarFit` | 设置图片适配：`0 contain`、`1 cover`、`2 fill`、`3 none`、`4 scale-down` |
| `EU_GetAvatarImageStatus` | 读取图片状态：`0` 空/未加载，`1` 成功，`2` 失败，`3` 加载中 |
| `EU_GetAvatarOptions` | 读取形状和适配方式 |

内容优先级：主图片 → 备用图片 → 错误文本（仅失败时）→ 图标/emoji → 文本 → 默认错误符号。

## Python 使用

```python
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui

hwnd = ui.create_window("😀 头像样式演示", 240, 120, 860, 560)
root = ui.create_container(hwnd, 0, 0, 0, 820, 500)

ui.create_avatar(hwnd, root, "小易", 0, 40, 40, 64, 64)
ui.create_avatar(hwnd, root, "", 1, 130, 40, 64, 64, icon="👤")
ui.create_avatar(
    hwnd, root, "", 0, 220, 40, 80, 80,
    source=r"C:\images\avatar.png",
    fallback_source=r"C:\images\avatar-fallback.png",
    fit="cover",
    error_text="离线",
)

ui.dll.EU_ShowWindow(hwnd, 1)
```

## 易语言调用

易语言侧以 `DLL命令/易语言DLL命令.md` 为准。命令名使用中文，例如 `创建头像`、`设置头像备用图片源`、`设置头像图标`；DLL 入口名保持真实 `EU_` 导出名。

## DPI 与首次窗口尺寸

示例窗口传入逻辑尺寸。新增或调整 Avatar 示例时，窗口和容器必须覆盖首屏全部控件，并保留至少 20px 逻辑余量。所有界面文案保持中文，并在标题、按钮或核心展示项中加入 emoji。

## 测试

优先运行：

```powershell
python tests/python/test_avatar_complete_components.py
python tests/python/test_display_status_complete_components.py
python tests/python/test_display_status_state_components.py
python tests/python/test_image_complete_components.py
python tests/python/test_new_emoji.py
```

图库页可用：

```powershell
$env:NEW_EMOJI_GALLERY_PAGE="data"
$env:NEW_EMOJI_GALLERY_COMPONENT="Avatar"
python examples/python/component_gallery.py
```

## 文档维护

如果 `Avatar` 新增、删除、重命名或修改 API，必须同步更新本文件、`docs/components/README.md`、`docs/api-index.md`、`examples/python/new_emoji_ui.py`、`tests/python/test_new_emoji.py`、`component_gallery.py` 和 `DLL命令/易语言DLL命令.md`。
