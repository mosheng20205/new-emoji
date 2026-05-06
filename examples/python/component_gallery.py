"""
new_emoji 88 component gallery.

Run from the repository root:
    python examples/python/component_gallery.py
"""
import base64
import ctypes
import os
import struct
import tempfile
import time
from ctypes import wintypes

import new_emoji_ui as ui


WINDOW_W = 2240
WINDOW_H = 1380
ROOT_W = 2200
ROOT_H = 1320
PAGE_X = 430
PAGE_Y = 20
PAGE_W = 1746
PAGE_H = 1300
CARD_W = 318
CARD_H = 148
CARD_GAP = 12
VISIBLE_SECONDS = int(os.environ.get("NEW_EMOJI_GALLERY_SECONDS", "180"))
START_PAGE = os.environ.get("NEW_EMOJI_GALLERY_PAGE", "")
START_COMPONENT = os.environ.get("NEW_EMOJI_GALLERY_COMPONENT", "")
START_THEME = os.environ.get("NEW_EMOJI_GALLERY_THEME", "")
SURFACE = 0xFF20243A
SURFACE_2 = 0xFF282D45
BORDER = 0xFF3D4668
BORDER_SOFT = 0xFF343B5C
TEXT = 0xFFEAF0FF
MUTED = 0xFFB9C5E8
ACCENT = 0xFF7AA7FF
NAV_BG = 0xFF252A42
NAV_ACTIVE = 0xFF355FAE

DARK_THEME = {
    "surface": SURFACE,
    "surface_2": SURFACE_2,
    "stage": 0xFF242941,
    "nav": 0xFF1F2338,
    "nav_bg": NAV_BG,
    "nav_item": 0xFF2B304A,
    "active": NAV_ACTIVE,
    "border": BORDER,
    "border_soft": BORDER_SOFT,
    "text": TEXT,
    "muted": MUTED,
    "active_text": 0xFFFFFFFF,
    "panel_canvas": 0xFF27314D,
    "panel_canvas_border": BORDER,
    "panel_blue": 0xFF253654,
    "panel_blue_border": 0xFF5C86D6,
    "panel_blue_text": 0xFFEAF2FF,
    "panel_gold": 0xFF443725,
    "panel_gold_border": 0xFFD19A3D,
    "panel_gold_text": 0xFFFFE4B5,
    "panel_green": 0xFF213D2F,
    "panel_green_border": 0xFF63B77C,
    "panel_green_text": 0xFFE6F7EC,
    "panel_neutral": 0xFF22283D,
    "panel_neutral_border": 0xFF465473,
    "panel_neutral_text": 0xFFEAF0FF,
}
LIGHT_THEME = {
    "surface": 0xFFF7FAFF,
    "surface_2": 0xFFFFFFFF,
    "stage": 0xFFFFFFFF,
    "nav": 0xFFFFFFFF,
    "nav_bg": 0xFFFFFFFF,
    "nav_item": 0xFFF1F5FF,
    "active": 0xFF2F6FD6,
    "border": 0xFFD2DCEB,
    "border_soft": 0xFFC8D4E8,
    "text": 0xFF162033,
    "muted": 0xFF53627A,
    "active_text": 0xFFFFFFFF,
    "panel_canvas": 0xFFF4F7FE,
    "panel_canvas_border": 0xFFD2DCEB,
    "panel_blue": 0xFFEBF5FF,
    "panel_blue_border": 0xFF78A8F8,
    "panel_blue_text": 0xFF1F3D64,
    "panel_gold": 0xFFFFF7E7,
    "panel_gold_border": 0xFFF1B85B,
    "panel_gold_text": 0xFF7A4B00,
    "panel_green": 0xFFEAF8EF,
    "panel_green_border": 0xFF69C587,
    "panel_green_text": 0xFF185A2F,
    "panel_neutral": 0xFFF8FBFF,
    "panel_neutral_border": 0xFFB6C6DE,
    "panel_neutral_text": 0xFF34435A,
}

callbacks = []
page_ids = []
category_components = {}
nav_menu_id = 0
nav_menu_items = []
nav_menu_icons = []
nav_menu_commands = []
nav_menu_expanded = []
nav_menu_page_index = {}
panel_roles = []
text_roles = []
gallery_errors = []
status_text_id = 0
gallery_hwnd = None
current_page_name = ""
current_category_name = ""
current_theme_mode = 1
upload_sample_cache = None
image_sample_cache = None

PNG_1X1 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def upload_sample_files():
    global upload_sample_cache
    if upload_sample_cache:
        return upload_sample_cache
    folder = tempfile.mkdtemp(prefix="new_emoji_gallery_upload_")
    files = []
    for name in ("封面图片.png", "头像素材.png", "相册照片.png"):
        path = os.path.join(folder, name)
        with open(path, "wb") as f:
            f.write(base64.b64decode(PNG_1X1))
        files.append(path)
    doc = os.path.join(folder, "上传说明.txt")
    with open(doc, "w", encoding="utf-8") as f:
        f.write("📤 上传组件示例文件\n")
    files.append(doc)
    upload_sample_cache = files
    return files


def _write_demo_bmp(path, width, height, palette_index):
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            if palette_index == 1:
                b = 80 + (y * 150 // max(1, height - 1))
                g = 120 + (x * 80 // max(1, width - 1))
                r = 230 - (y * 90 // max(1, height - 1))
            elif palette_index == 2:
                b = 210 - (x * 110 // max(1, width - 1))
                g = 90 + (y * 120 // max(1, height - 1))
                r = 90 + (x * 120 // max(1, width - 1))
            else:
                b = 120 + (x * 90 // max(1, width - 1))
                g = 210 - (y * 80 // max(1, height - 1))
                r = 110 + ((x + y) * 70 // max(1, width + height - 2))
            pixels.extend([b & 0xFF, g & 0xFF, r & 0xFF, 255])
    file_size = 54 + len(pixels)
    with open(path, "wb") as f:
        f.write(struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54))
        f.write(struct.pack("<IiiHHIIiiII", 40, width, height, 1, 32, 0, len(pixels), 2835, 2835, 0, 0))
        f.write(pixels)


def image_sample_files():
    global image_sample_cache
    if image_sample_cache:
        return image_sample_cache
    folder = tempfile.mkdtemp(prefix="new_emoji_gallery_image_")
    wide = os.path.join(folder, "横向风景.bmp")
    tall = os.path.join(folder, "竖向海报.bmp")
    small = os.path.join(folder, "小图标.bmp")
    _write_demo_bmp(wide, 180, 108, 1)
    _write_demo_bmp(tall, 72, 150, 2)
    _write_demo_bmp(small, 46, 34, 3)
    image_sample_cache = (wide, tall, small)
    return image_sample_cache


@ui.MessageBoxCallback
def on_gallery_messagebox(_messagebox_id, _result):
    pass


def keep_callback(cb):
    callbacks.append(cb)
    return cb


def set_click(hwnd, element_id, fn):
    cb = keep_callback(ui.ClickCallback(fn))
    ui.dll.EU_SetElementClickCallback(hwnd, element_id, cb)

def _create_and(element_id, setup):
    setup(element_id)
    return element_id

def _make_tr(h, p, x, y, w, hh):
    tid = ui.create_timepicker(h, p, 9, 0, x, y, min(w, 400), 42)
    ui.set_timepicker_range_select(h, tid, True, 900, 1800)
    return tid

def _make_dtr(h, p, x, y, w, hh):
    did = ui.create_datetimepicker(h, p, 2026, 5, 1, 9, 0, x, y, min(w, 480), 42)
    ui.set_datetimepicker_range_select(h, did, True, 20260501, 900, 20260510, 1800)
    ui.set_datetimepicker_default_time(h, did, 9, 0)
    return did


def palette():
    return LIGHT_THEME if current_theme_mode == 0 else DARK_THEME


def register_panel(element_id, fill_role, border_role="border", stroke=1.0, radius=8.0, padding=8):
    panel_roles.append((element_id, fill_role, border_role, stroke, radius, padding))


def register_text(element_id, role):
    text_roles.append((element_id, role))


def apply_gallery_theme(hwnd, mode):
    global current_theme_mode
    current_theme_mode = 0 if mode == 0 else 1
    ui.dll.EU_SetThemeMode(hwnd, mode)
    colors = palette()
    for element_id, fill_role, border_role, stroke, radius, padding in panel_roles:
        ui.set_panel_style(hwnd, element_id, colors[fill_role], colors[border_role], stroke, radius, padding)
    for element_id, role in text_roles:
        ui.set_element_color(hwnd, element_id, 0, colors[role])
    apply_nav_menu_theme(hwnd)
    if current_category_name and "/" in current_page_name:
        _category, component = current_page_name.split("/", 1)
        show_component(hwnd, current_category_name, component)


def apply_nav_menu_theme(hwnd):
    if not nav_menu_id:
        return
    colors = palette()
    ui.set_menu_colors(
        hwnd, nav_menu_id,
        colors["nav"], colors["muted"], colors["active"],
        colors["nav_item"], colors["muted"], colors["border_soft"],
    )


def show_component(hwnd, category_name, component_name):
    global current_page_name, current_category_name
    colors = palette()
    page_name = f"{category_name}/{component_name}"
    current_page_name = page_name
    current_category_name = category_name
    for name, page_id in page_ids:
        ui.set_element_visible(hwnd, page_id, name == page_name)
    menu_index = nav_menu_page_index.get(page_name, -1)
    if nav_menu_id and menu_index >= 0:
        ui.set_menu_active(hwnd, nav_menu_id, menu_index)
    if status_text_id:
        ui.set_element_text(hwnd, status_text_id, f"当前组件：{category_name} / {component_name} · 推荐演示 87 个组件 · 编辑内核 API 兼容保留")
        ui.set_element_color(hwnd, status_text_id, 0, colors["muted"])


def show_category(hwnd, category_name):
    components = category_components.get(category_name, [])
    if components:
        show_component(hwnd, category_name, components[0][0])


def build_nav_menu_model():
    global nav_menu_items, nav_menu_icons, nav_menu_commands, nav_menu_expanded, nav_menu_page_index
    nav_menu_items = []
    nav_menu_icons = []
    nav_menu_commands = []
    nav_menu_expanded = []
    nav_menu_page_index = {}
    for category_name, components in category_components.items():
        category_index = len(nav_menu_items)
        nav_menu_items.append(category_name)
        nav_menu_icons.append("📁")
        nav_menu_commands.append(f"cat::{category_name}")
        nav_menu_expanded.append(category_index)
        for component_name, emoji, _summary in components:
            item_index = len(nav_menu_items)
            nav_menu_items.append(f"> {component_name}")
            nav_menu_icons.append(emoji)
            nav_menu_commands.append(f"cmp::{category_name}::{component_name}")
            nav_menu_page_index[f"{category_name}/{component_name}"] = item_index


@ui.MenuSelectCallback
def on_gallery_nav_select(_element_id, item_index, _path_ptr, _path_len, command_ptr, command_len):
    global nav_menu_expanded
    if not gallery_hwnd:
        return
    command = ctypes.string_at(command_ptr, command_len).decode("utf-8", errors="replace") if command_ptr and command_len > 0 else ""
    if command.startswith("cmp::"):
        parts = command.split("::", 2)
        if len(parts) == 3:
            show_component(gallery_hwnd, parts[1], parts[2])
    elif command.startswith("cat::"):
        category_name = command[5:]
        was_expanded = item_index in nav_menu_expanded
        if was_expanded:
            nav_menu_expanded = [index for index in nav_menu_expanded if index != item_index]
        else:
            nav_menu_expanded = sorted(nav_menu_expanded + [item_index])
        if nav_menu_id:
            ui.set_menu_expanded(gallery_hwnd, nav_menu_id, nav_menu_expanded)
        if was_expanded:
            if status_text_id:
                ui.set_element_text(gallery_hwnd, status_text_id, f"已收起分类：{category_name} · 点击一级菜单可展开/收起")
                ui.set_element_color(gallery_hwnd, status_text_id, 0, palette()["muted"])
        else:
            show_category(gallery_hwnd, category_name)


def add_text(hwnd, parent, text, x, y, w, h, color=TEXT):
    element_id = ui.create_text(hwnd, parent, text, x, y, w, h)
    if color == MUTED:
        register_text(element_id, "muted")
        ui.set_element_color(hwnd, element_id, 0, palette()["muted"])
    elif color == TEXT:
        register_text(element_id, "text")
        ui.set_element_color(hwnd, element_id, 0, palette()["text"])
    else:
        ui.set_element_color(hwnd, element_id, 0, color)
    return element_id


def add_role_text(hwnd, parent, text, x, y, w, h, role):
    element_id = ui.create_text(hwnd, parent, text, x, y, w, h)
    register_text(element_id, role)
    ui.set_element_color(hwnd, element_id, 0, palette()[role])
    return element_id


def add_themed_panel(hwnd, parent, x, y, w, h, fill_role, border_role, stroke=1.0, radius=8.0, padding=10):
    panel = ui.create_panel(hwnd, parent, x, y, w, h)
    ui.set_panel_style(hwnd, panel, palette()[fill_role], palette()[border_role], stroke, radius, padding)
    register_panel(panel, fill_role, border_role, stroke, radius, padding)
    return panel


def message_loop(seconds=180):
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pm_remove = 1
    start = time.time()
    while time.time() - start < seconds:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, pm_remove):
            if time.time() - start >= seconds:
                return
            handled = True
            if msg.message == 0x0012:
                return
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def add_card(hwnd, page, index, name, emoji, summary, builder, floating=False, cols=4, card_w=CARD_W, card_h=CARD_H, gap=CARD_GAP):
    col = index % cols
    row = index // cols
    x = 10 + col * (card_w + gap)
    y = 76 + row * (card_h + gap)
    return add_card_at(hwnd, page, x, y, card_w, card_h, name, emoji, summary, builder, floating)


def add_card_at(hwnd, page, x, y, card_w, card_h, name, emoji, summary, builder, floating=False):
    body_h = max(34, card_h - 62)
    card = ui.create_panel(hwnd, page, x, y, card_w, card_h)
    ui.set_panel_style(hwnd, card, SURFACE_2, BORDER, 1.0, 6.0, 8)
    register_panel(card, "surface_2", "border", 1.0, 6.0, 8)
    add_text(hwnd, card, f"{emoji} {name}", 10, 8, card_w - 20, 24, TEXT)
    add_text(hwnd, card, summary, 10, 31, card_w - 20, 22, MUTED)
    try:
        if floating:
            builder(hwnd, page, x + 10, y + 55, card_w - 20, body_h)
        else:
            builder(hwnd, card, 10, 55, card_w - 20, body_h)
    except Exception as exc:
        gallery_errors.append((name, str(exc)))
        ui.create_alert(hwnd, card, "演示创建失败", str(exc), 2, 0, False, 10, 58, card_w - 20, min(78, body_h))
    return card


def add_demo_panel(hwnd, parent, title, x, y, w, h):
    panel = ui.create_panel(hwnd, parent, x, y, w, h)
    ui.set_panel_style(hwnd, panel, SURFACE_2, BORDER, 1.0, 8.0, 10)
    register_panel(panel, "surface_2", "border", 1.0, 8.0, 10)
    add_text(hwnd, panel, title, 16, 14, w - 32, 26, TEXT)
    return panel


def add_feature_panel(hwnd, parent, category_name, summary, x, y, w, h):
    panel = add_demo_panel(hwnd, parent, "✨ 展示重点", x, y, w, h)
    add_text(hwnd, panel, f"分类：{category_name}", 18, 54, w - 36, 26, MUTED)
    add_text(hwnd, panel, f"能力：{summary}", 18, 88, w - 36, 26, MUTED)
    add_text(hwnd, panel, "✅ 中文文案与 emoji\n✅ 主题切换预览\n✅ DPI 首屏适配\n✅ 键鼠交互演示", 18, 132, w - 36, 126, TEXT)
    return panel


def showcase_button(hwnd, stage, w, h):
    labels = [
        ("默认按钮", "⚪", 0),
        ("主要按钮", "🚀", 1),
        ("成功按钮", "✅", 2),
        ("信息按钮", "💬", 6),
        ("警告按钮", "⚠️", 3),
        ("危险按钮", "🧯", 4),
    ]

    def add_variant_row(parent, title, y, *, plain=False, round=False, disabled=False,
                        button_w=128, button_h=36, col_w=148):
        add_text(hwnd, parent, title, 24, y + 6, 88, 24, MUTED)
        for i, (text, emoji, variant) in enumerate(labels):
            x = 112 + i * col_w
            btn = ui.create_button(
                hwnd, parent, emoji, text, x, y, button_w, button_h,
                variant=variant, plain=plain, round=round,
            )
            if disabled:
                ui.set_element_enabled(hwnd, btn, False)
            if i == 1 and not disabled:
                set_click(hwnd, btn, button_action(hwnd, "按钮回调 🚀", f"{text} 已触发。"))

    matrix = add_demo_panel(hwnd, stage, "🚀 基础、悬停、朴素、圆角与禁用", 28, 30, w - 56, 330)
    add_text(hwnd, matrix, "把鼠标移到第一行彩色按钮上，观察更明显的悬停反馈。", 1040, 68, 520, 28, MUTED)
    add_variant_row(matrix, "悬停", 62, button_w=136, button_h=42, col_w=154)
    add_variant_row(matrix, "基础", 116)
    add_variant_row(matrix, "朴素", 168, plain=True)
    add_variant_row(matrix, "圆角", 220, round=True)
    add_variant_row(matrix, "禁用", 272, disabled=True)

    circle_panel = add_demo_panel(hwnd, stage, "⭕ 圆形图标按钮", 28, 382, w - 56, 112)
    for i, (_text, emoji, variant) in enumerate(labels):
        x = 40 + i * 74
        ui.create_button(hwnd, circle_panel, emoji, "", x, 58, 44, 44, variant=variant, circle=True)
    add_text(hwnd, circle_panel, "工具栏与列表图标入口。", 466, 66, 260, 26, MUTED)

    advanced = add_demo_panel(hwnd, stage, "🧩 文字、图标、加载、尺寸与按钮组", 28, 516, w - 56, 220)
    ui.create_button(hwnd, advanced, "", "文字按钮", 36, 66, 96, 34, variant=5)
    disabled_text = ui.create_button(hwnd, advanced, "", "禁用文字", 146, 66, 104, 34, variant=5)
    ui.set_element_enabled(hwnd, disabled_text, False)
    ui.create_button(hwnd, advanced, "✏️", "", 280, 64, 42, 38, variant=1)
    ui.create_button(hwnd, advanced, "🔗", "", 334, 64, 42, 38, variant=1)
    ui.create_button(hwnd, advanced, "🗑️", "", 388, 64, 42, 38, variant=1)
    ui.create_button(hwnd, advanced, "🔎", "搜索", 456, 64, 112, 38, variant=1)
    ui.create_button(hwnd, advanced, "📤", "上传", 586, 64, 112, 38, variant=1)
    ui.create_button(hwnd, advanced, "⏳", "加载中", 720, 64, 126, 38, variant=1, loading=True)

    size_specs = [
        ("默认按钮", 0, 126, 38),
        ("中等按钮", 1, 118, 36),
        ("小型按钮", 2, 104, 32),
        ("超小按钮", 3, 96, 28),
    ]
    x = 36
    for text, size, bw, bh in size_specs:
        ui.create_button(hwnd, advanced, "📏", text, x, 124, bw, bh, size=size, round=True)
        x += bw + 16

    group_x = 640
    ui.create_button(hwnd, advanced, "⬅️", "上一页", group_x, 124, 112, 36, variant=1)
    ui.create_button(hwnd, advanced, "➡️", "下一页", group_x + 112, 124, 112, 36, variant=1)
    ui.create_button(hwnd, advanced, "✏️", "", group_x, 170, 48, 36, variant=1)
    ui.create_button(hwnd, advanced, "🔗", "", group_x + 48, 170, 48, 36, variant=1)
    ui.create_button(hwnd, advanced, "🗑️", "", group_x + 96, 170, 48, 36, variant=1)
    add_text(hwnd, advanced, "按钮组为组合展示，不新增 native 组件。", 36, 174, 480, 26, MUTED)


def showcase_link(hwnd, stage, w, h):
    labels = [
        ("默认链接", "🔗", 0),
        ("主要链接", "🚀", 1),
        ("成功链接", "✅", 2),
        ("警告链接", "⚠️", 3),
        ("危险链接", "🧯", 4),
        ("信息链接", "💬", 5),
    ]

    def add_link_row(parent, title, y, *, disabled=False, underline=True):
        add_text(hwnd, parent, title, 30, y + 2, 120, 26, MUTED)
        for i, (text, emoji, link_type) in enumerate(labels):
            x = 150 + i * 190
            link = ui.create_link(
                hwnd, parent, f"{text} {emoji}", x, y, 150, 30,
                type=link_type, underline=underline,
                href="https://element.eleme.io", target="_blank",
            )
            if disabled:
                ui.set_element_enabled(hwnd, link, False)
            if i == 1 and not disabled:
                set_click(hwnd, link, button_action(hwnd, "链接回调 🔗", "主要链接点击事件已触发。"))

    matrix = add_demo_panel(hwnd, stage, "🔗 类型、禁用与下划线", 28, 30, w - 56, 250)
    add_text(hwnd, matrix, "把鼠标移到链接上可查看悬停颜色，点击后会进入访问态。", 30, 58, 520, 28, MUTED)
    add_link_row(matrix, "基础类型", 96)
    add_link_row(matrix, "禁用类型", 142, disabled=True)
    add_link_row(matrix, "无下划线", 188, underline=False)

    behavior = add_demo_panel(hwnd, stage, "✨ 图标、href/target 与访问态", 28, 310, w - 56, 250)
    ui.create_link(hwnd, behavior, "编辑资料", 44, 78, 160, 32, type=1, prefix_icon="✏️")
    ui.create_link(hwnd, behavior, "查看详情", 230, 78, 160, 32, type=5, suffix_icon="👀")
    ui.create_link(
        hwnd, behavior, "打开 Element 文档", 420, 78, 240, 32,
        type=1, prefix_icon="📚", suffix_icon="↗",
        href="https://element.eleme.io", target="_blank",
    )
    visited = ui.create_link(hwnd, behavior, "已访问链接", 700, 78, 160, 32, type=1, visited=True)
    disabled = ui.create_link(hwnd, behavior, "禁用链接", 900, 78, 150, 32, type=4)
    ui.set_element_enabled(hwnd, disabled, False)
    add_text(hwnd, behavior, "href/target 已写入状态，可通过 get_link_content 读回；gallery 默认不自动打开浏览器。", 44, 138, 900, 28, MUTED)
    add_text(hwnd, behavior, "支持前缀 emoji、后缀 emoji、键盘回车/空格触发和点击回调。", 44, 176, 760, 28, MUTED)


def showcase_panel(hwnd, stage, w, h):
    hero = add_demo_panel(hwnd, stage, "🧱 品牌信息面板", 28, 30, w - 56, 190)
    add_themed_panel(hwnd, hero, 24, 60, 340, 86, "panel_blue", "panel_blue_border", 1.0, 10.0, 12)
    add_themed_panel(hwnd, hero, 390, 60, 320, 86, "panel_gold", "panel_gold_border", 1.0, 10.0, 12)
    add_themed_panel(hwnd, hero, 736, 60, 320, 86, "panel_green", "panel_green_border", 1.0, 10.0, 12)
    add_role_text(hwnd, hero, "项目总览 🚀", 44, 78, 220, 28, "panel_blue_text")
    add_role_text(hwnd, hero, "主题配置 🎨", 410, 78, 220, 28, "panel_gold_text")
    add_role_text(hwnd, hero, "发布状态 ✅", 756, 78, 220, 28, "panel_green_text")

    grid = add_demo_panel(hwnd, stage, "📦 嵌套布局组合", 28, 242, w - 56, min(250, h - 270))
    blocks = [
        ("导航区 🧭", "panel_blue", "panel_blue_border", "panel_blue_text"),
        ("内容区 📄", "panel_neutral", "panel_neutral_border", "panel_neutral_text"),
        ("操作区 ⚙️", "panel_gold", "panel_gold_border", "panel_gold_text"),
    ]
    for i, (label, fill_role, border_role, text_role) in enumerate(blocks):
        x = 24 + i * 350
        add_themed_panel(hwnd, grid, x, 68, 320, 120, fill_role, border_role, 1.0, 8.0, 10)
        add_role_text(hwnd, grid, label, x + 20, 112, 180, 26, text_role)


def showcase_container(hwnd, stage, w, h):
    add_text(hwnd, stage, "📦 Container 套件覆盖顶栏、侧边栏、主要区域、底栏、自动方向、显式横纵向、间距和嵌套后台壳。", 36, 28, w - 72, 28, MUTED)

    def make_flow(parent, x, y, cw, ch, direction=0, gap=0, bg=0):
        cid = ui.create_container(hwnd, parent, x, y, cw, ch)
        ui.set_panel_layout(hwnd, cid, fill_parent=False, content_layout=False)
        ui.set_panel_style(hwnd, cid, bg, 0x00000000, 0.0, 0.0, 0)
        ui.set_container_layout(hwnd, cid, True, direction, gap)
        return cid

    def layout_card(parent, title, index, builder):
        card_w = (w - 116) // 4
        card_h = 142
        col = index % 4
        row = index // 4
        x = 20 + col * (card_w + 12)
        y = 54 + row * (card_h + 12)
        card = add_themed_panel(hwnd, parent, x, y, card_w, card_h, "panel_canvas", "panel_canvas_border", 1.0, 8.0, 8)
        add_text(hwnd, card, title, 10, 8, card_w - 20, 22, MUTED)
        root = make_flow(card, 10, 38, card_w - 20, card_h - 52)
        builder(root)
        return root

    matrix = add_demo_panel(hwnd, stage, "📐 七种官方 Container 布局", 28, 70, w - 56, 372)

    def case_header_main(root):
        ui.create_header(hwnd, root, "📌 顶栏", h=42)
        ui.create_main(hwnd, root, "📄 主要区域")

    def case_header_main_footer(root):
        ui.create_header(hwnd, root, "📌 顶栏", h=36)
        ui.create_main(hwnd, root, "📄 主要区域")
        ui.create_footer(hwnd, root, "✅ 底栏", h=34)

    def case_aside_main(root):
        ui.create_aside(hwnd, root, "🧭 侧边栏", w=118)
        ui.create_main(hwnd, root, "📄 主要区域")

    def case_header_aside_main(root):
        ui.create_header(hwnd, root, "📌 顶栏", h=34)
        body = make_flow(root, 0, 0, 0, 0, direction=1)
        ui.create_aside(hwnd, body, "🧭 侧边栏", w=112)
        ui.create_main(hwnd, body, "📄 主要区域")

    def case_header_aside_main_footer(root):
        ui.create_header(hwnd, root, "📌 顶栏", h=32)
        body = make_flow(root, 0, 0, 0, 0, direction=1)
        ui.create_aside(hwnd, body, "🧭 侧边栏", w=108)
        content = make_flow(body, 0, 0, 0, 0, direction=2)
        ui.create_main(hwnd, content, "📄 主要区域")
        ui.create_footer(hwnd, content, "✅ 底栏", h=30)

    def case_aside_header_main(root):
        ui.set_container_layout(hwnd, root, True, 1, 0)
        ui.create_aside(hwnd, root, "🧭 侧边栏", w=112)
        content = make_flow(root, 0, 0, 0, 0, direction=2)
        ui.create_header(hwnd, content, "📌 顶栏", h=34)
        ui.create_main(hwnd, content, "📄 主要区域")

    def case_aside_header_main_footer(root):
        ui.set_container_layout(hwnd, root, True, 1, 0)
        ui.create_aside(hwnd, root, "🧭 侧边栏", w=104)
        content = make_flow(root, 0, 0, 0, 0, direction=2)
        ui.create_header(hwnd, content, "📌 顶栏", h=30)
        ui.create_main(hwnd, content, "📄 主要区域")
        ui.create_footer(hwnd, content, "✅ 底栏", h=28)

    for i, (title, builder) in enumerate([
        ("顶栏 + 主要区域", case_header_main),
        ("顶栏 + 主要区域 + 底栏", case_header_main_footer),
        ("侧边栏 + 主要区域", case_aside_main),
        ("顶栏 + 侧边栏 + 主要区域", case_header_aside_main),
        ("顶栏 + 侧边栏 + 主要区域 + 底栏", case_header_aside_main_footer),
        ("侧边栏 + 顶栏 + 主要区域", case_aside_header_main),
        ("侧边栏 + 顶栏 + 主要区域 + 底栏", case_aside_header_main_footer),
    ]):
        layout_card(matrix, title, i, builder)

    style_panel = add_demo_panel(hwnd, stage, "🎨 样式覆盖与布局读回", 28, 464, w - 56, 176)
    custom = make_flow(style_panel, 28, 58, 620, 96, direction=1, gap=10, bg=0x00000000)
    aside = ui.create_aside(hwnd, custom, "🧭 左对齐", w=150)
    main = ui.create_main(hwnd, custom, "📄 自定义主区")
    footer_like = ui.create_footer(hwnd, custom, "➡️ 右下", w=150, h=0)
    ui.set_panel_style(hwnd, aside, 0xFFEEF5FF, 0xFF7AA7FF, 1.0, 8.0, 8)
    ui.set_panel_style(hwnd, main, 0xFFFFFAE8, 0xFFE6A23C, 1.0, 8.0, 8)
    ui.set_panel_style(hwnd, footer_like, 0xFFEAF8EF, 0xFF63B77C, 1.0, 8.0, 8)
    ui.set_container_region_text_options(hwnd, aside, 0, 1)
    ui.set_container_region_text_options(hwnd, footer_like, 2, 2)
    readback = ui.get_container_layout(hwnd, custom)
    add_text(hwnd, style_panel, f"📌 当前布局：启用={readback['enabled']} 方向={readback['direction']} 实际={readback['actual_direction']} 间距={readback['gap']}", 690, 64, 620, 30, TEXT)
    add_text(hwnd, style_panel, "区域文本可设置起始/居中/末尾对齐；颜色、边框、圆角和 padding 复用 Panel 样式 API。", 690, 102, 760, 30, MUTED)

    app_panel = add_demo_panel(hwnd, stage, "🖥️ 桌面后台布局：侧栏菜单 + 顶栏工具 + 表格主区", 28, 666, w - 56, 430)
    shell = make_flow(app_panel, 28, 58, w - 112, 342, direction=1)
    sidebar = ui.create_aside(hwnd, shell, "", w=250)
    ui.set_panel_style(hwnd, sidebar, 0xFFEEF1F6, 0xFFD8DEE8, 1.0, 0.0, 0)
    menu_items = ["导航一", "> 分组一", "> > 选项1", "> > 选项2", "> 分组二", "> > 选项3", "> 选项4", "> > 选项4-1", "导航二", "导航三"]
    menu = ui.create_menu(hwnd, sidebar, menu_items, 2, 1, 0, 0, 250, 324)
    ui.set_menu_expanded(hwnd, menu, [0, 6])
    blank_meta = [""] * len(menu_items)
    ui.set_menu_item_meta(hwnd, menu, ["🧭", "📁", "•", "•", "📁", "•", "📦", "•", "📊", "⚙️"], [1, 4], blank_meta, blank_meta, blank_meta)

    workspace = make_flow(shell, 0, 0, 0, 0, direction=2)
    top = ui.create_header(hwnd, workspace, "", h=54)
    ui.set_panel_style(hwnd, top, 0xFFB3C0D1, 0x00000000, 0.0, 0.0, 0)
    add_text(hwnd, top, "⚙️ 系统设置", 690, 16, 110, 24, 0xFF333333)
    add_text(hwnd, top, "王小虎 👤", 818, 16, 120, 24, 0xFF333333)
    main_area = ui.create_main(hwnd, workspace, "")
    ui.set_panel_style(hwnd, main_area, 0xFFE9EEF3, 0x00000000, 0.0, 0.0, 18)
    columns = ["日期", "姓名", "地址"]
    rows = [
        ["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"],
        ["2016-05-04", "王小虎", "上海市普陀区金沙江路 1518 弄"],
        ["2016-05-01", "王小虎", "上海市普陀区金沙江路 1518 弄"],
        ["2016-05-03", "王小虎", "上海市普陀区金沙江路 1518 弄"],
    ]
    ui.create_table(hwnd, main_area, columns, rows, True, True, 0, 0, min(w - 430, 1180), 216)


def showcase_header(hwnd, stage, w, h):
    intro = add_demo_panel(hwnd, stage, "📌 Header：页面顶栏与工具区", 28, 30, w - 56, 220)
    add_text(hwnd, intro, "Header 适合放页面标题、全局搜索、状态入口和主要操作，通常固定在内容区顶部。", 30, 58, w - 110, 28, MUTED)
    header = ui.create_header(hwnd, intro, "📌 项目看板", 30, 104, w - 116, 64)
    ui.set_panel_style(hwnd, header, 0xFF2F4F7F, 0xFF78A8F8, 1.0, 8.0, 10)
    ui.create_button(hwnd, header, "🔍", "搜索", w - 430, 14, 112, 36, variant=5)
    ui.create_button(hwnd, header, "➕", "新建", w - 300, 14, 112, 36, variant=1)
    ui.create_button(hwnd, header, "⚙", "设置", w - 170, 14, 112, 36, variant=5)

    matrix = add_demo_panel(hwnd, stage, "🧩 常见顶栏高度", 28, 284, w - 56, 250)
    for i, (label, hh) in enumerate([("紧凑顶栏", 42), ("标准顶栏", 56), ("强调顶栏", 72)]):
        y = 62 + i * 58
        ui.create_header(hwnd, matrix, f"📌 {label}", 32, y, min(620, w - 130), hh)
        add_text(hwnd, matrix, f"{hh}px", 690, y + 10, 100, 24, MUTED)
    add_text(hwnd, matrix, "顶栏可以单独使用，也可以和 Aside / Main / Footer 组合成完整后台壳。", 32, 214, w - 120, 28, MUTED)


def showcase_aside(hwnd, stage, w, h):
    shell = add_demo_panel(hwnd, stage, "🧭 Aside：侧边导航区域", 28, 30, w - 56, 430)
    add_text(hwnd, shell, "Aside 通常承载导航、分组菜单或筛选条件，重点是稳定宽度和纵向扫描。", 30, 58, w - 110, 28, MUTED)
    aside = ui.create_aside(hwnd, shell, "", 30, 102, 260, 280)
    ui.set_panel_style(hwnd, aside, 0xFF263552, 0xFF5C86D6, 1.0, 8.0, 10)
    menu_items = ["总览 🏠", "组件库 🧩", "> 基础布局", "> 表单输入", "> 数据展示", "设置 ⚙"]
    menu = ui.create_menu(hwnd, aside, menu_items, 1, 1, 10, 10, 238, 250)
    ui.set_menu_expanded(hwnd, menu, [1])
    main = ui.create_main(hwnd, shell, "📄 右侧主工作区", 318, 102, min(760, w - 410), 280)
    ui.set_panel_style(hwnd, main, 0xFF27314D, 0xFF465473, 1.0, 8.0, 12)
    add_text(hwnd, shell, "左侧 Aside 保持固定宽度，右侧 Main 承接主要内容。", 318, 392, w - 410, 28, MUTED)

    sizes = add_demo_panel(hwnd, stage, "📐 常见侧栏宽度", 28, 500, w - 56, 210)
    for i, (label, ww) in enumerate([("窄导航", 160), ("标准导航", 220), ("筛选面板", 300)]):
        x = 32 + i * 360
        ui.create_aside(hwnd, sizes, f"🧭 {label}", x, 62, ww, 90)
        add_text(hwnd, sizes, f"宽度 {ww}px", x, 164, 180, 24, MUTED)


def showcase_main(hwnd, stage, w, h):
    workspace = add_demo_panel(hwnd, stage, "📄 Main：主要内容工作区", 28, 30, w - 56, 430)
    add_text(hwnd, workspace, "Main 用于承载表格、表单、图表、详情页等核心内容，通常占据布局里的剩余空间。", 30, 58, w - 110, 28, MUTED)
    main = ui.create_main(hwnd, workspace, "", 30, 102, w - 116, 270)
    ui.set_panel_style(hwnd, main, 0xFF27314D, 0xFF5C86D6, 1.0, 8.0, 16)
    add_text(hwnd, main, "📄 当前任务", 24, 22, 180, 28, TEXT)
    ui.create_progress(hwnd, main, "构建进度", 68, 1, 24, 72, min(520, w - 190), 36)
    columns = ["模块", "状态", "负责人"]
    rows = [["布局", "已完成 ✅", "小林"], ["输入", "进行中 🔧", "小周"], ["反馈", "待验证 🔍", "小陈"]]
    ui.create_table(hwnd, main, columns, rows, True, True, 24, 130, min(760, w - 180), 112)

    split = add_demo_panel(hwnd, stage, "🧱 与其他区域组合", 28, 500, w - 56, 250)
    ui.create_header(hwnd, split, "📌 顶栏", 30, 62, w - 116, 44)
    ui.create_aside(hwnd, split, "🧭 侧栏", 30, 118, 190, 88)
    ui.create_main(hwnd, split, "📄 Main 自动成为视觉重心", 238, 118, min(620, w - 340), 88)


def showcase_footer(hwnd, stage, w, h):
    page = add_demo_panel(hwnd, stage, "✅ Footer：底部状态与操作区", 28, 30, w - 56, 300)
    add_text(hwnd, page, "Footer 适合放版权、状态提示、分页、确认操作或向导按钮，通常贴在内容底部。", 30, 58, w - 110, 28, MUTED)
    content = ui.create_main(hwnd, page, "📄 表单内容区域", 30, 104, w - 116, 90)
    ui.set_panel_style(hwnd, content, 0xFF27314D, 0xFF465473, 1.0, 8.0, 10)
    footer = ui.create_footer(hwnd, page, "", 30, 206, w - 116, 58)
    ui.set_panel_style(hwnd, footer, 0xFF263552, 0xFF5C86D6, 1.0, 8.0, 10)
    add_text(hwnd, footer, "✅ 已自动保存草稿", 18, 18, 240, 24, TEXT)
    ui.create_button(hwnd, footer, "", "取消", w - 350, 12, 112, 36, variant=0)
    ui.create_button(hwnd, footer, "✅", "提交", w - 220, 12, 112, 36, variant=1)

    variants = add_demo_panel(hwnd, stage, "📐 常见底栏用途", 28, 390, w - 56, 260)
    examples = [("状态底栏", "同步完成 ✅"), ("分页底栏", "第 1 / 12 页 📄"), ("向导底栏", "上一步 / 下一步 ➡")]
    for i, (label, text) in enumerate(examples):
        y = 64 + i * 58
        add_text(hwnd, variants, label, 32, y + 8, 120, 24, MUTED)
        ui.create_footer(hwnd, variants, text, 170, y, min(620, w - 260), 40)


def showcase_border(hwnd, stage, w, h):
    intro = add_demo_panel(hwnd, stage, "▣ Border：边框、标题与区域分组", 28, 30, w - 56, 250)
    add_text(hwnd, intro, "Border 用来表达区域边界、表单分组、焦点范围和轻量容器，不负责复杂内容布局。", 30, 58, w - 110, 28, MUTED)
    specs = [
        ("全部边框", 15, 0xFF78A8F8, 1.0, 8.0, False, "基础信息"),
        ("顶部边框", 1, 0xFFFFC24D, 2.0, 0.0, False, "状态提示"),
        ("左侧强调", 8, 0xFF69D282, 3.0, 0.0, False, "成功步骤"),
        ("虚线边框", 15, 0xFFFF9BC2, 1.5, 10.0, True, "可拖放区域"),
    ]
    for i, (label, sides, color, width_v, radius, dashed, title) in enumerate(specs):
        x = 32 + i * 330
        add_text(hwnd, intro, title, x + 6, 106, 220, 24, TEXT)
        b = ui.create_border(hwnd, intro, x, 136, 292, 64)
        ui.set_border_options(hwnd, b, sides, color, width_v, radius, "")
        ui.set_border_dashed(hwnd, b, dashed)
        add_text(hwnd, intro, label, x + 14, 214, 220, 24, TEXT)

    matrix = add_demo_panel(hwnd, stage, "🧾 表单分组和状态区域", 28, 314, w - 56, 300)
    add_text(hwnd, matrix, "账号资料", 40, 72, 220, 24, TEXT)
    account = ui.create_border(hwnd, matrix, 34, 106, min(520, w // 3), 134)
    ui.set_border_options(hwnd, account, 15, 0xFF78A8F8, 1.0, 8.0, "")
    add_text(hwnd, matrix, "👤 用户名称：小林", 62, 132, 240, 26, TEXT)
    add_text(hwnd, matrix, "📧 邮箱：team@example.com", 62, 168, 280, 26, MUTED)
    add_text(hwnd, matrix, "🔒 权限：编辑者", 62, 204, 240, 26, MUTED)

    warning_x = 590
    add_text(hwnd, matrix, "左边框强调", warning_x, 72, 220, 24, TEXT)
    warning = ui.create_border(hwnd, matrix, warning_x, 106, min(520, w - 700), 134)
    ui.set_border_options(hwnd, warning, 8, 0xFFFFC24D, 4.0, 6.0, "")
    add_text(hwnd, matrix, "⚠️ 发布前检查", warning_x + 28, 132, 260, 28, TEXT)
    add_text(hwnd, matrix, "缺少说明文案时，可以只用左侧边框强调状态，不必放一个完整卡片。", warning_x + 28, 172, min(430, w - warning_x - 90), 52, MUTED)

    readback = add_demo_panel(hwnd, stage, "🔎 Set/Get 与虚线状态", 28, 656, w - 56, 160)
    add_text(hwnd, readback, "读回样例", 40, 62, 180, 24, TEXT)
    sample = ui.create_border(hwnd, readback, 34, 96, 360, 44)
    ui.set_border_options(hwnd, sample, 15, 0xFF69D282, 2.0, 12.0, "")
    ui.set_border_dashed(hwnd, sample, True)
    sides, color, width_v, radius = ui.get_border_options(hwnd, sample)
    add_text(hwnd, readback, f"当前边框：sides={sides} · color=0x{color:08X} · width={width_v:.1f} · radius={radius:.1f} · dashed={ui.get_border_dashed(hwnd, sample)}", 430, 102, w - 540, 30, TEXT)


def showcase_affix(hwnd, stage, w, h):
    intro = add_demo_panel(hwnd, stage, "📌 Affix：固定操作和吸顶状态", 28, 30, w - 56, 250)
    add_text(hwnd, intro, "Affix 用于让关键操作在滚动后仍保持可见，适合保存栏、目录入口、返回顶部和审核动作。", 30, 58, w - 110, 28, MUTED)
    free = ui.create_affix(hwnd, intro, "📌 未固定", "滚动位置低于阈值，仍在文档流中。", 80, 34, 106, 420, 88)
    ui.set_affix_options(hwnd, free, 40, 80, 0, 88, 5)
    fixed = ui.create_affix(hwnd, intro, "📌 已固定", "滚动超过阈值，操作区吸附到顶部。", 80, 500, 106, 420, 88)
    ui.set_affix_options(hwnd, fixed, 160, 80, 0, 88, 12)
    free_state = ui.get_affix_options(hwnd, free)
    fixed_state = ui.get_affix_options(hwnd, fixed)
    add_text(hwnd, intro, f"未固定：scroll={free_state['scroll_position']} / offset={free_state['offset']} / fixed={free_state['fixed']}", 34, 206, 480, 28, MUTED)
    add_text(hwnd, intro, f"已固定：scroll={fixed_state['scroll_position']} / offset={fixed_state['offset']} / fixed={fixed_state['fixed']}", 500, 206, 520, 28, TEXT)

    toolbar = add_demo_panel(hwnd, stage, "🧰 真实页面：吸顶操作条", 28, 314, w - 56, 230)
    add_text(hwnd, toolbar, "向下滚动后，保存、发布、预览这类操作通常需要保持在顶部可触达。", 34, 58, w - 120, 28, MUTED)
    top_bar = ui.create_affix(hwnd, toolbar, "📌 固定操作条", "草稿已保存 · 阈值 96px · 层级 20", 96, 34, 104, w - 124, 64)
    ui.set_affix_options(hwnd, top_bar, 168, 96, 0, 64, 20)
    action_x = w - 650
    ui.create_button(hwnd, toolbar, "👁", "预览", action_x, 118, 104, 36, variant=5)
    ui.create_button(hwnd, toolbar, "💾", "保存", action_x + 120, 118, 104, 36, variant=1)
    ui.create_button(hwnd, toolbar, "🚀", "发布", action_x + 240, 118, 104, 36, variant=1)

    positions = add_demo_panel(hwnd, stage, "🎯 侧边固定动作与层级", 28, 590, w - 56, 260)
    add_text(hwnd, positions, "不同 Affix 可以用不同 offset 和 z-index 表达优先级：目录入口靠上，返回顶部靠下，危险操作单独分组。", 34, 58, w - 120, 28, MUTED)
    items = [("📚 目录", "固定在 24px", 24, 10), ("⬆ 返回顶部", "固定在 96px", 96, 30), ("⚠️ 审核提醒", "固定在 168px", 168, 40)]
    for i, (title, body, offset, z) in enumerate(items):
        x = 34 + i * 380
        aff = ui.create_affix(hwnd, positions, title, body, offset, x, 112, 330, 78)
        ui.set_affix_options(hwnd, aff, offset + 120, offset, 0, 78, z)
        state = ui.get_affix_options(hwnd, aff)
        add_text(hwnd, positions, f"z-index {state['z_index']} · fixed={state['fixed']}", x, 202, 260, 24, MUTED)


def showcase_layout(hwnd, stage, w, h):
    header = add_demo_panel(hwnd, stage, "🧭 自动布局示意", 28, 30, w - 56, 250)
    layout = ui.create_layout(hwnd, header, 0, 18, 28, 70, w - 112, 148)
    add_themed_panel(hwnd, header, 28, 70, w - 112, 148, "panel_canvas", "panel_canvas_border", 1.0, 10.0, 10)
    add_themed_panel(hwnd, header, 48, 92, 210, 100, "panel_blue", "panel_blue_border", 1.0, 8.0, 10)
    add_themed_panel(hwnd, header, 280, 92, 280, 100, "panel_gold", "panel_gold_border", 1.0, 8.0, 10)
    add_themed_panel(hwnd, header, 582, 92, 220, 100, "panel_green", "panel_green_border", 1.0, 8.0, 10)
    add_role_text(hwnd, header, "左 -> 中 -> 右的流式排列", 52, 110, 220, 24, "panel_blue_text")
    add_role_text(hwnd, header, "固定间距 18", 310, 110, 160, 24, "panel_gold_text")
    add_role_text(hwnd, header, "对齐一致", 608, 110, 120, 24, "panel_green_text")

    stack = add_demo_panel(hwnd, stage, "🧱 纵向堆叠示意", 28, 302, w - 56, 210)
    col = ui.create_layout(hwnd, stack, 1, 12, 28, 70, 260, 118)
    add_themed_panel(hwnd, stack, 28, 70, 260, 118, "panel_canvas", "panel_canvas_border", 1.0, 10.0, 10)
    add_themed_panel(hwnd, stack, 48, 92, 220, 28, "panel_blue", "panel_blue_border", 1.0, 8.0, 8)
    add_themed_panel(hwnd, stack, 48, 132, 220, 28, "panel_gold", "panel_gold_border", 1.0, 8.0, 8)
    add_themed_panel(hwnd, stack, 48, 172, 220, 28, "panel_green", "panel_green_border", 1.0, 8.0, 8)
    add_role_text(hwnd, stack, "标题条", 68, 98, 120, 20, "panel_blue_text")
    add_role_text(hwnd, stack, "内容条", 68, 138, 120, 20, "panel_gold_text")
    add_role_text(hwnd, stack, "底部条", 68, 178, 120, 20, "panel_green_text")

    tip = add_demo_panel(hwnd, stage, "✨ 适合场景", 318, 302, min(w - 346, 320), 210)
    add_text(hwnd, tip, "自动布局适合表单、列表、卡片栅格和配置区。", 18, 72, 260, 24, MUTED)
    add_text(hwnd, tip, "这里展示横排、竖排和间距控制。", 18, 104, 260, 24, MUTED)


def showcase_divider(hwnd, stage, w, h):
    add_text(
        hwnd, stage,
        "➗ Divider 覆盖横线、文字位置、图标内容、竖向分隔、线型、颜色、线宽和间距，适合桌面端表单、工具栏和属性面板。",
        36, 28, w - 72, 28, MUTED,
    )

    basics = add_demo_panel(hwnd, stage, "🧾 基础横向样式", 28, 70, w - 56, 240)
    ui.create_text(hwnd, basics, "青春是一个短暂的美梦，当你醒来时，它早已消失无踪", 36, 58, w - 128, 28)
    plain = ui.create_divider(hwnd, basics, "", 0, 1, 36, 94, w - 128, 26)
    ui.set_divider_options(hwnd, plain, 0, 1, palette()["border_soft"], 1.0, False, "")
    ui.create_text(hwnd, basics, "少量的邪恶足以抵消全部高贵的品质，害得人声名狼藉", 36, 126, w - 128, 28)

    left = ui.create_divider(hwnd, basics, "少年包青天", 0, 0, 36, 166, 440, 34)
    ui.set_divider_options(hwnd, left, 0, 0, 0xFF409EFF, 1.5, False, "少年包青天")
    ui.set_divider_content(hwnd, left, "⚖️", "少年包青天")
    center_icon = ui.create_divider(hwnd, basics, "", 0, 1, 500, 166, 280, 34)
    ui.set_divider_options(hwnd, center_icon, 0, 1, 0xFF67C23A, 2.0, False, "")
    ui.set_divider_content(hwnd, center_icon, "📱", "")
    right = ui.create_divider(hwnd, basics, "阿里云", 0, 2, 810, 166, 440, 34)
    ui.set_divider_options(hwnd, right, 0, 2, 0xFFE6A23C, 1.5, False, "阿里云")
    ui.set_divider_content(hwnd, right, "☁️", "阿里云")

    vertical = add_demo_panel(hwnd, stage, "↕️ 竖向与工具栏分隔", 28, 330, 800, 260)
    ui.create_text(hwnd, vertical, "雨纷纷", 36, 72, 86, 30)
    v1 = ui.create_divider(hwnd, vertical, "", 1, 1, 132, 58, 24, 62)
    ui.set_divider_options(hwnd, v1, 1, 1, 0xFF909399, 1.0, False, "")
    ui.create_text(hwnd, vertical, "旧故里", 166, 72, 86, 30)
    v2 = ui.create_divider(hwnd, vertical, "", 1, 1, 262, 58, 24, 62)
    ui.set_divider_options(hwnd, v2, 1, 1, 0xFF909399, 1.0, False, "")
    ui.create_text(hwnd, vertical, "草木深", 296, 72, 86, 30)

    toolbar = add_themed_panel(hwnd, vertical, 36, 142, 700, 74, "panel_canvas", "panel_canvas_border", 1.0, 8.0, 8)
    ui.create_button(hwnd, toolbar, "📄", "新建", 18, 18, 92, 36)
    tv1 = ui.create_divider(hwnd, toolbar, "", 1, 1, 126, 16, 20, 42)
    ui.set_divider_options(hwnd, tv1, 1, 1, 0xFFC0C4CC, 1.0, False, "")
    ui.create_button(hwnd, toolbar, "💾", "保存", 162, 18, 92, 36)
    tv2 = ui.create_divider(hwnd, toolbar, "", 1, 1, 270, 16, 20, 42)
    ui.set_divider_options(hwnd, tv2, 1, 1, 0xFFC0C4CC, 1.0, False, "")
    ui.create_button(hwnd, toolbar, "🚀", "发布", 306, 18, 92, 36)
    tv3 = ui.create_divider(hwnd, toolbar, "", 1, 1, 414, 16, 20, 42)
    ui.set_divider_options(hwnd, tv3, 1, 1, 0xFFC0C4CC, 1.0, False, "")
    ui.create_button(hwnd, toolbar, "⚙️", "设置", 450, 18, 92, 36)

    styles = add_demo_panel(hwnd, stage, "🎨 线型颜色矩阵", 856, 330, w - 884, 260)
    style_specs = [
        ("实线", "🎯", 0, 0xFF409EFF, 1.0),
        ("虚线", "🧵", 1, 0xFFE6A23C, 1.5),
        ("点线", "✨", 2, 0xFF67C23A, 2.0),
        ("双线", "🛤️", 3, 0xFFF56C6C, 1.2),
    ]
    for i, (label, icon, style, color, width_value) in enumerate(style_specs):
        y = 62 + i * 42
        add_text(hwnd, styles, f"{icon} {label}", 36, y + 2, 92, 24, TEXT)
        divider = ui.create_divider(hwnd, styles, label, 0, 1, 128, y, w - 1060, 30)
        ui.set_divider_options(hwnd, divider, 0, 1, color, width_value, False, label)
        ui.set_divider_line_style(hwnd, divider, style)
        ui.set_divider_content(hwnd, divider, icon, label)

    spacing = add_demo_panel(hwnd, stage, "📐 线宽、边距与文本间隙", 28, 620, w - 56, 250)
    spacing_specs = [
        ("细线小间距", "📏", 0xFF409EFF, 1.0, 0, 6, 62),
        ("粗线大间距", "🧱", 0xFFE6A23C, 3.0, 32, 18, 112),
        ("点线留白", "🌟", 0xFF67C23A, 2.0, 56, 24, 162),
    ]
    last_spacing = 0
    for label, icon, color, width_value, margin, gap, y in spacing_specs:
        add_text(hwnd, spacing, f"{icon} {label}：外边距 {margin}，文本间隙 {gap}", 36, y + 2, 360, 24, TEXT)
        last_spacing = ui.create_divider(hwnd, spacing, label, 0, 1, 430, y, w - 548, 34)
        ui.set_divider_options(hwnd, last_spacing, 0, 1, color, width_value, False, label)
        ui.set_divider_content(hwnd, last_spacing, icon, label)
        ui.set_divider_spacing(hwnd, last_spacing, margin=margin, gap=gap)
        if label == "点线留白":
            ui.set_divider_line_style(hwnd, last_spacing, 2)

    readback = add_demo_panel(hwnd, stage, "📤 状态读回", 28, 890, w - 56, 190)
    ui.create_text(hwnd, readback, "当前选项读回用于确认易语言/Python 调用拿到的是逻辑尺寸和值枚举。", 32, 56, w - 120, 28)
    ui.create_text(hwnd, readback, f"左侧标题选项：{ui.get_divider_options(hwnd, left)}", 32, 92, 620, 28)
    ui.create_text(hwnd, readback, f"图标内容：{ui.get_divider_content(hwnd, center_icon)}", 680, 92, 520, 28)
    ui.create_text(hwnd, readback, f"点线线型：{ui.get_divider_line_style(hwnd, last_spacing)}，间距：{ui.get_divider_spacing(hwnd, last_spacing)}", 32, 128, 740, 28)


def showcase_watermark(hwnd, stage, w, h):
    card = add_demo_panel(hwnd, stage, "💧 水印背景", 28, 30, w - 56, 330)
    sample = ui.create_panel(hwnd, card, 36, 92, w - 128, 176)
    ui.set_panel_style(hwnd, sample, 0xFF25324C, 0xFF5C769F, 1.0, 8.0, 10)
    wm = ui.create_watermark(hwnd, card, "new_emoji 💧 Demo", 120, 76, 18, 66, w - 92, 220)
    ui.set_watermark_options(hwnd, wm, 120, 76, -18, 96)
    add_text(hwnd, card, "文档抄送 / 内部预览 / 仅供展示", 56, 126, 260, 24, TEXT)
    add_text(hwnd, card, "水印内容会以重复纹理铺在背景上，用于表示归属、敏感等级或品牌标识。", 56, 160, w - 160, 44, MUTED)

    spec = add_demo_panel(hwnd, stage, "📎 水印参数", 28, 384, w - 56, 126)
    add_text(hwnd, spec, "内容：new_emoji 💧 Demo", 28, 68, 320, 24, MUTED)
    add_text(hwnd, spec, "间距：120 / 76", 360, 68, 220, 24, MUTED)
    add_text(hwnd, spec, "旋转：-18°", 560, 68, 160, 24, MUTED)
    add_text(hwnd, spec, "透明度：96", 720, 68, 180, 24, MUTED)


def showcase_checkbox(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "☑️ 基础、禁用与半选", 28, 30, w - 56, 150)
    ui.create_checkbox(hwnd, basics, "备选项 ✅", True, 36, 70, 150, 34)
    unchecked = ui.create_checkbox(hwnd, basics, "备选项 🔔", False, 210, 70, 150, 34)
    disabled_a = ui.create_checkbox(hwnd, basics, "禁用项 🔒", False, 390, 70, 150, 34)
    disabled_b = ui.create_checkbox(hwnd, basics, "选中且禁用 ✅", True, 570, 70, 190, 34)
    partial = ui.create_checkbox(hwnd, basics, "全选：部分城市 🌆", False, 790, 70, 230, 34)
    ui.dll.EU_SetCheckboxIndeterminate(hwnd, partial, 1)
    ui.set_element_enabled(hwnd, disabled_a, False)
    ui.set_element_enabled(hwnd, disabled_b, False)
    ui.set_checkbox_options(hwnd, unchecked, border=True, size=1)
    add_text(hwnd, basics, "独立 Checkbox 已支持 checked、disabled、indeterminate、border 和 size。", 36, 116, 760, 24, MUTED)

    groups = add_demo_panel(hwnd, stage, "🧩 CheckboxGroup 多选组", 28, 204, w - 56, 170)
    city_items = [
        ("上海 🏙️", "上海", False),
        ("北京 🏛️", "北京", False),
        ("广州 🌿", "广州", False),
        ("深圳 🚀", "深圳", False),
    ]
    normal = ui.create_checkbox_group(hwnd, groups, city_items, ["上海", "北京"],
                                      style=0, x=36, y=68, w=620, h=40)
    limited = ui.create_checkbox_group(hwnd, groups, city_items, ["上海", "北京"],
                                       style=0, min_checked=1, max_checked=2,
                                       x=36, y=116, w=620, h=40)
    add_text(hwnd, groups, "基础组选中值：" + "、".join(ui.get_checkbox_group_value(hwnd, normal)), 700, 70, 360, 24, MUTED)
    add_text(hwnd, groups, "第二行限制最少 1 项、最多 2 项。", 700, 118, 360, 24, MUTED)

    buttons = add_demo_panel(hwnd, stage, "🎛️ CheckboxButton 按钮样式", 28, 398, w - 56, 190)
    sizes = [("默认", 0), ("中等", 1), ("小型", 2), ("超小", 3)]
    for row, (label, size) in enumerate(sizes):
        y = 60 + row * 32
        add_text(hwnd, buttons, label, 36, y + 4, 70, 22, MUTED)
        ui.create_checkbox_group(
            hwnd, buttons, city_items, ["上海"], style=1, size=size,
            x=112, y=y, w=500, h=30 if size >= 2 else 34,
        )
    ui.create_checkbox_group(
        hwnd, buttons,
        [("上海 🏙️", "上海", False), ("北京 🔒", "北京", True), ("广州 🌿", "广州", False), ("深圳 🚀", "深圳", False)],
        ["上海"], style=1, size=2, x=660, y=70, w=500, h=32,
    )
    ui.create_checkbox_group(hwnd, buttons, city_items, ["上海"], style=1, size=3,
                             disabled=True, x=660, y=118, w=500, h=30)
    add_text(hwnd, buttons, "右侧展示单项禁用与整组禁用。", 660, 154, 360, 24, MUTED)

    bordered = add_demo_panel(hwnd, stage, "📦 边框样式与尺寸", 28, 612, w - 56, 190)
    ui.create_checkbox(hwnd, bordered, "备选项1 📌", True, 36, 68, 150, 38, border=True)
    ui.create_checkbox(hwnd, bordered, "备选项2 📎", False, 208, 68, 150, 38, border=True)
    ui.create_checkbox(hwnd, bordered, "中等尺寸 🧭", True, 386, 68, 160, 36, border=True, size=1)
    small_disabled = ui.create_checkbox(hwnd, bordered, "小型禁用 🔒", False, 570, 70, 160, 34, border=True, size=2)
    ui.set_element_enabled(hwnd, small_disabled, False)
    ui.create_checkbox_group(hwnd, bordered, city_items, ["上海", "深圳"], style=2, size=2,
                             x=36, y=124, w=620, h=36)
    ui.create_checkbox_group(hwnd, bordered, city_items, [], style=2, size=3, disabled=True,
                             x=690, y=124, w=520, h=32)
    add_text(hwnd, bordered, "边框样式覆盖独立 Checkbox 与 CheckboxGroup，按钮式不额外新增 native 组件。", 760, 72, 520, 24, MUTED)


def showcase_radio(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🔘 基础单选与 value", 28, 30, w - 56, 170)
    radio_a = ui.create_radio(hwnd, basics, "备选项 A 🚀", True, 36, 74, 150, 34, value="1")
    radio_b = ui.create_radio(hwnd, basics, "备选项 B ✨", False, 210, 74, 150, 34, value="2")
    ui.set_radio_group(hwnd, radio_a, "基础方案")
    ui.set_radio_group(hwnd, radio_b, "基础方案")
    disabled_a = ui.create_radio(hwnd, basics, "禁用项 💤", False, 406, 74, 150, 34, value="disabled")
    disabled_b = ui.create_radio(hwnd, basics, "选中且禁用 ✅", True, 584, 74, 180, 34, value="checked-disabled")
    ui.set_element_enabled(hwnd, disabled_a, False)
    ui.set_element_enabled(hwnd, disabled_b, False)
    add_text(hwnd, basics, "旧 Radio 保留 checked/group_name，同时新增 value、border、size 读写。", 36, 122, 760, 28, MUTED)

    normal = add_demo_panel(hwnd, stage, "🧩 原生 RadioGroup", 28, 230, w - 56, 150)
    ui.create_radio_group(
        hwnd, normal,
        [("上海 🏙️", "上海", False), ("北京 🏛️", "北京", False), ("广州 🌆", "广州", False), ("深圳 🌊", "深圳", False)],
        value="上海", style=0, size=0, x=36, y=76, w=720, h=42,
    )
    add_text(hwnd, normal, "整组保存 selected_value / selected_index，键盘方向键可在可用项之间切换。", 790, 82, 520, 28, MUTED)

    buttons = add_demo_panel(hwnd, stage, "🎛️ RadioButton 按钮样式", 28, 410, w - 56, 280)
    rows = [
        ("默认", 0, False, 72),
        ("中等", 1, False, 118),
        ("小型，禁用北京", 2, False, 164),
        ("超小，整组禁用", 3, True, 204),
    ]
    for title, size, disabled, y in rows:
        add_text(hwnd, buttons, title, 34, y + 4, 120, 24, MUTED)
        items = [
            ("上海", "上海", False),
            ("北京", "北京", size == 2),
            ("广州", "广州", False),
            ("深圳", "深圳", False),
        ]
        ui.create_radio_group(hwnd, buttons, items, value="上海", style=1, size=size,
                              disabled=disabled, x=160, y=y, w=480, h=34 if size >= 2 else 38)
    add_text(hwnd, buttons, "按钮型单选是 RadioGroup 的 style=button，不额外新增 native 组件。", 700, 112, 520, 28, MUTED)

    bordered = add_demo_panel(hwnd, stage, "📦 Border 边框样式与尺寸", 28, 732, w - 56, 220)
    ui.create_radio(hwnd, bordered, "备选项 1 📌", True, 36, 76, 150, 40, value="1", border=True)
    ui.create_radio(hwnd, bordered, "备选项 2 📎", False, 210, 76, 150, 40, value="2", border=True)
    ui.create_radio(hwnd, bordered, "中等尺寸 🧭", True, 390, 76, 150, 38, value="m", border=True, size=1)
    small_disabled = ui.create_radio(hwnd, bordered, "小型禁用 🔒", False, 570, 78, 150, 34, value="s", border=True, size=2)
    ui.set_element_enabled(hwnd, small_disabled, False)
    ui.create_radio_group(
        hwnd, bordered,
        [("备选 1", "1", False), ("备选 2", "2", True), ("备选 3", "3", False)],
        value="1", style=2, size=2, x=36, y=142, w=520, h=38,
    )
    add_text(hwnd, bordered, "边框样式覆盖独立 Radio 和原生 RadioGroup，单项禁用与整组禁用语义分离。", 600, 148, 640, 28, MUTED)


def showcase_input(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "⌨️ 基础、禁用、清空与密码", 28, 30, w - 56, 210)
    ui.create_input(hwnd, basics, value="", placeholder="请输入昵称 👋", clearable=False, x=36, y=72, w=260, h=40)
    disabled = ui.create_input(hwnd, basics, value="已禁用", placeholder="请输入内容", x=320, y=72, w=240, h=40)
    ui.set_element_enabled(hwnd, disabled, False)
    ui.create_input(hwnd, basics, value="可清空的输入", placeholder="支持 clearable", clearable=True, x=584, y=72, w=260, h=40)
    ui.create_input(hwnd, basics, value="secret-emoji", placeholder="请输入密码", show_password=True, x=868, y=72, w=260, h=40)
    ui.create_input(hwnd, basics, value="前后缀", placeholder="带图标与文案", prefix="Http://", suffix=".com",
                    prefix_icon="🌐", suffix_icon="🔎", x=36, y=132, w=430, h=40)
    ui.create_input(hwnd, basics, value="计数字段", placeholder="最多 20 字", clearable=True,
                    show_word_limit=True, max_length=20, x=492, y=132, w=300, h=40)
    add_text(hwnd, basics, "支持 Ctrl+A 全选、鼠标拖选文字；右键菜单可通过 Input API 开关。", 820, 166, 420, 28, MUTED)
    add_text(hwnd, basics, "Input 已补齐 prefix/suffix 文案、prefix/suffix icon、clearable、密码显隐和字数统计。", 820, 136, 360, 28, MUTED)

    textarea = add_demo_panel(hwnd, stage, "📝 多行、autosize 与字数限制", 28, 264, w - 56, 230)
    ui.create_input(hwnd, textarea, value="第一行：支持中文和 emoji ✨\n第二行：保留 Element 风格边框。",
                    placeholder="请输入多行内容", multiline=True, x=36, y=72, w=420, h=110)
    ui.create_input(hwnd, textarea, value="自动高度会随内容增长。\n继续输入第三行。\n第四行也会被容纳。",
                    placeholder="autosize 文本域", multiline=True, autosize=True,
                    min_rows=2, max_rows=4, x=486, y=72, w=420, h=110)
    ui.create_input(hwnd, textarea, value="带字数统计的说明文本。", placeholder="最多 30 字",
                    multiline=True, show_word_limit=True, max_length=30, x=936, y=72, w=250, h=110)
    add_text(hwnd, textarea, "autosize 只对 multiline 生效，min_rows / max_rows 会限制自动增长范围。", 36, 194, 760, 24, MUTED)

    sizes = add_demo_panel(hwnd, stage, "📏 四尺寸与 InputGroup", 28, 520, w - 56, 320)
    ui.create_input(hwnd, sizes, placeholder="默认尺寸", suffix_icon="📅", x=36, y=70, w=240, h=40)
    ui.create_input(hwnd, sizes, placeholder="medium", size=1, suffix_icon="📅", x=302, y=70, w=240, h=40)
    ui.create_input(hwnd, sizes, placeholder="small", size=2, suffix_icon="📅", x=568, y=74, w=240, h=34)
    ui.create_input(hwnd, sizes, placeholder="mini", size=3, suffix_icon="📅", x=834, y=76, w=240, h=30)
    add_text(hwnd, sizes, "InputGroup", 36, 146, 180, 24, TEXT)
    ui.create_input_group(hwnd, sizes, value="", placeholder="请输入地址",
                          prepend={"type": "text", "text": "Http://"},
                          append={"type": "text", "text": ".com"},
                          x=36, y=178, w=420, h=40)
    ui.create_input_group(hwnd, sizes, value="", placeholder="选择检索范围",
                          prepend={"type": "select", "items": [("餐厅名", "1"), ("订单号", "2"), ("用户电话", "3")], "selected": 0, "placeholder": "请选择"},
                          append={"type": "button", "emoji": "🔎", "text": "", "variant": 1},
                          x=490, y=178, w=520, h=40)
    ui.create_input_group(hwnd, sizes, value="emoji-ui", placeholder="账号",
                          prepend={"type": "text", "text": "账号"},
                          append={"type": "button", "emoji": "✅", "text": "提交", "variant": 2},
                          size=2, clearable=True, x=36, y=240, w=500, h=36)
    add_text(hwnd, sizes, "InputGroup 用原生子元素承接 prepend / append，内部 Input / Button / Select 都能拿到真实 element id。", 568, 244, 620, 28, MUTED)


def showcase_input_group(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "📌 状态：等待操作。", 36, h - 58, w - 72, 28, MUTED)

    def set_status(message, group_id=0):
        if group_id:
            options = ui.get_input_group_options(hwnd, group_id) or {}
            value = ui.get_input_group_value(hwnd, group_id)
            input_id = ui.get_input_group_input_element_id(hwnd, group_id)
            left_id = ui.get_input_group_addon_element_id(hwnd, group_id, 0)
            right_id = ui.get_input_group_addon_element_id(hwnd, group_id, 1)
            ui.set_element_text(
                hwnd, status,
                f"{message} · 值「{value or '空'}」 · size {options.get('size', '-')}"
                f" · input={input_id} · 左={left_id} · 右={right_id}"
            )
        else:
            ui.set_element_text(hwnd, status, message)

    base = add_demo_panel(hwnd, stage, "🔗 附加项组合：文本、按钮、选择器", 28, 30, w - 56, 238)
    ui.create_input_group(hwnd, base, value="new-emoji", placeholder="请输入域名",
                          prepend={"type": "text", "text": "https://"},
                          append={"type": "text", "text": ".cn"},
                          clearable=True, x=36, y=70, w=420, h=40)
    search_group = ui.create_input_group(hwnd, base, value="", placeholder="请输入订单、电话或客户名",
                                         prepend={"type": "select", "items": [("餐厅名 🍜", "1"), ("订单号 🧾", "2"), ("用户电话 📞", "3")], "selected": 0, "placeholder": "检索范围"},
                                         append={"type": "button", "emoji": "🔎", "text": "搜索  ", "variant": 1},
                                         x=492, y=70, w=620, h=40)
    ui.create_input_group(hwnd, base, value="emoji-ui", placeholder="请输入账号",
                          prepend={"type": "button", "emoji": "👤", "text": "账号  ", "variant": 6},
                          append={"type": "button", "emoji": "✅", "text": "提交", "variant": 2},
                          size=1, clearable=True, x=36, y=138, w=520, h=40)
    ui.create_input_group(hwnd, base, value="A-1024", placeholder="请输入编号",
                          prepend={"type": "text", "text": "工单"},
                          append={"type": "select", "items": [("待处理 🧾", "todo"), ("处理中 🚀", "doing"), ("已完成 ✅", "done")], "selected": 1, "placeholder": "状态"},
                          x=592, y=138, w=560, h=40)
    add_text(hwnd, base, "prepend / append 可分别挂载文本、按钮或 Select；按钮和选择器都是可继续绑定回调的真实子元素。", 36, 194, 1040, 24, MUTED)

    sizes = add_demo_panel(hwnd, stage, "📏 尺寸与输入行为：clearable、密码、字数统计、autosize", 28, 292, w - 56, 238)
    for i, (label, size, y, height) in enumerate([
        ("默认尺寸", 0, 68, 40),
        ("medium", 1, 68, 40),
        ("small", 2, 132, 36),
        ("mini", 3, 134, 30),
    ]):
        x = 36 + i * 278
        ui.create_input_group(hwnd, sizes, value="", placeholder=label,
                              prepend={"type": "text", "text": f"{label}"},
                              append={"type": "button", "emoji": "✨", "text": "", "variant": 1},
                              size=size, x=x, y=y, w=250, h=height)
    ui.create_input_group(hwnd, sizes, value="secret-emoji", placeholder="请输入密码",
                          prepend={"type": "text", "text": "密码 🔐"},
                          append={"type": "text", "text": "可显隐"},
                          size=0, clearable=True, password=True, show_word_limit=True,
                          x=36, y=178, w=440, h=40)
    ui.create_input_group(hwnd, sizes, value="第一行：组合输入也能承接多行。\n第二行：用于备注、地址或说明。", placeholder="请输入多行备注",
                          prepend={"type": "text", "text": "备注 📝"},
                          append={"type": "button", "emoji": "💾", "text": "保存  ", "variant": 1},
                          size=0, clearable=True, show_word_limit=True, autosize=True,
                          min_rows=2, max_rows=4, x=506, y=174, w=640, h=52)

    api = add_demo_panel(hwnd, stage, "🎛️ 运行时 API：Set/Get、切换附加项、读回内部 ID", 28, 554, w - 56, 250)
    api_group = ui.create_input_group(hwnd, api, value="浦东会议室", placeholder="请输入地点",
                                      prepend={"type": "text", "text": "地点 📍"},
                                      append={"type": "button", "emoji": "🚀", "text": "预约", "variant": 1},
                                      clearable=True, x=36, y=70, w=580, h=40)
    id_text = add_text(hwnd, api, "", 660, 74, 760, 28, TEXT)

    def refresh_ids(prefix="📊 当前结构"):
        input_id = ui.get_input_group_input_element_id(hwnd, api_group)
        left_id = ui.get_input_group_addon_element_id(hwnd, api_group, 0)
        right_id = ui.get_input_group_addon_element_id(hwnd, api_group, 1)
        ui.set_element_text(hwnd, id_text, f"{prefix}：input={input_id} · prepend={left_id} · append={right_id}")
        set_status(prefix, api_group)

    def write_value(_eid):
        ui.set_input_group_value(hwnd, api_group, "深圳设计评审 ✨")
        refresh_ids("✍️ 已通过 EU_SetInputGroupValue 写入")

    def read_value(_eid):
        refresh_ids("📖 已通过 EU_GetInputGroupValue 读回")

    def toggle_left(_eid):
        if ui.get_input_group_addon_element_id(hwnd, api_group, 0):
            ui.clear_input_group_addon(hwnd, api_group, 0)
            refresh_ids("🧹 已清空左侧附加项")
        else:
            ui.set_input_group_text_addon(hwnd, api_group, 0, "地点 📍")
            refresh_ids("↩️ 已恢复左侧文本附加项")

    def switch_right(_eid):
        ui.set_input_group_select_addon(hwnd, api_group, 1, [("会议室 🏢", "room"), ("线上会议 💻", "online"), ("外出拜访 🚗", "visit")], 0, "类型")
        select_id = ui.get_input_group_addon_element_id(hwnd, api_group, 1)
        if select_id:
            ui.set_select_open(hwnd, select_id, True)
        refresh_ids("🔄 右侧已切换为 Select")

    def use_input_child(_eid):
        input_id = ui.get_input_group_input_element_id(hwnd, api_group)
        if input_id:
            ui.set_input_value(hwnd, input_id, "内部 Input 直接改值 ✅")
        refresh_ids("🧩 已通过内部 Input ID 改值")

    for i, (emoji, text, handler) in enumerate([
        ("✍️", "写入值", write_value),
        ("📖", "读回值", read_value),
        ("🧹", "清空/恢复左侧", toggle_left),
        ("🔄", "右侧改为选择", switch_right),
        ("🧩", "内部 Input 改值", use_input_child),
    ]):
        btn = ui.create_button(hwnd, api, emoji, text, 36 + i * 150, 136, 132, 36, variant=1 if i != 2 else 3)
        set_click(hwnd, btn, handler)
    refresh_ids()

    callbacks_panel = add_demo_panel(hwnd, stage, "🧷 子元素回调与禁用态", 28, 828, w - 56, 214)
    callback_group = ui.create_input_group(hwnd, callbacks_panel, value="年度报表", placeholder="请输入文件名",
                                           prepend={"type": "select", "items": [("文档 📄", "doc"), ("图片 🖼️", "image"), ("压缩包 📦", "zip")], "selected": 0, "placeholder": "类型"},
                                           append={"type": "button", "emoji": "📤", "text": "上传  ", "variant": 1},
                                           x=36, y=70, w=620, h=40)
    callback_note = add_text(hwnd, callbacks_panel, "点击「上传」会触发 append Button 回调；选择器可直接用 Select API 打开和改选。", 696, 76, 700, 26, MUTED)
    select_id = ui.get_input_group_addon_element_id(hwnd, callback_group, 0)
    button_id = ui.get_input_group_addon_element_id(hwnd, callback_group, 1)
    if select_id:
        ui.set_select_open(hwnd, select_id, True)
    if button_id:
        set_click(hwnd, button_id, lambda _eid: set_status("📤 上传按钮回调已触发", callback_group))

    disabled_group = ui.create_input_group(hwnd, callbacks_panel, value="只读组合", placeholder="禁用态",
                                           prepend={"type": "text", "text": "禁用"},
                                           append={"type": "button", "emoji": "🔒", "text": "锁定", "variant": 5},
                                           x=36, y=134, w=420, h=40)
    ui.set_element_enabled(hwnd, disabled_group, False)
    add_text(hwnd, callbacks_panel, "禁用 InputGroup 会让内部输入与附加项一起进入禁用态，适合只读表单、权限不足和提交中状态。", 492, 140, 760, 26, MUTED)
    ui.set_element_text(hwnd, callback_note, f"内部 ID：select={select_id} · button={button_id}；它们可继续绑定 Select / Button API。")


def showcase_input_tag(hwnd, stage, w, h):
    add_text(hwnd, stage, "🏷️ InputTag 覆盖中文/emoji 输入、回车提交、逗号提交、删除按钮悬停、去重、数量限制、允许重复和运行时 Set/Get。", 36, 28, w - 72, 30, MUTED)

    status = add_text(hwnd, stage, "📌 状态：等待操作。", 36, h - 66, w - 72, 30, MUTED)

    def tag_items(tag_id):
        count = ui.get_input_tag_count(hwnd, tag_id)
        return [ui.get_input_tag_item(hwnd, tag_id, i) for i in range(count)]

    def refresh_status(message, tag_id):
        items = tag_items(tag_id)
        opts = ui.get_input_tag_options(hwnd, tag_id) or (0, False)
        draft = ui.get_input_tag_input_value(hwnd, tag_id)
        ui.set_element_text(
            hwnd, status,
            f"{message} · 数量 {len(items)} · 上限 {opts[0] or '不限'} · 允许重复 {'是' if opts[1] else '否'} · 草稿「{draft or '空'}」 · 标签：{'、'.join(items) or '无'}"
        )

    def set_tags(tag_id, values):
        data = ui.make_utf8("|".join(values))
        ui.dll.EU_SetInputTagTags(hwnd, tag_id, ui.bytes_arg(data), len(data))

    main = add_demo_panel(hwnd, stage, "⭐ 基础输入：中文、emoji、回车与删除", 28, 70, w - 56, 220)
    main_tag = ui.create_input_tag(
        hwnd, main,
        ["设计", "D2D", "emoji"],
        "输入中文、emoji 或数字，按回车提交 🏷️",
        34, 70, w - 128, 72,
    )
    ui.set_input_tag_options(hwnd, main_tag, max_count=8, allow_duplicates=False)
    add_text(hwnd, main, "把鼠标移到每个标签右侧 x 上可看到 hover；输入「原型✨」后按回车会追加为标签，退格可删除空输入前的最后一项。", 34, 158, w - 128, 28, MUTED)

    def on_main_change(_element_id, payload_ptr, payload_len):
        payload = ctypes.string_at(payload_ptr, payload_len).decode("utf-8", errors="replace") if payload_ptr and payload_len > 0 else ""
        ui.set_element_text(hwnd, status, f"📣 change 回调：{payload or '无标签'}")

    ui.dll.EU_SetInputTagChangeCallback(hwnd, main_tag, keep_callback(ui.TextCallback(on_main_change)))

    rules = add_demo_panel(hwnd, stage, "🧩 规则矩阵：去重、上限与允许重复", 28, 318, w - 56, 240)
    strict = ui.create_input_tag(
        hwnd, rules,
        ["前端", "动效", "测试"],
        "最多 4 个，不允许重复",
        34, 72, min(700, w - 160), 82,
    )
    ui.set_input_tag_options(hwnd, strict, max_count=4, allow_duplicates=False)
    loose_x = min(780, w // 2 + 24)
    loose = ui.create_input_tag(
        hwnd, rules,
        ["热点", "热点", "活动"],
        "允许重复，适合搜索词历史",
        loose_x, 72, max(520, w - loose_x - 72), 82,
    )
    ui.set_input_tag_options(hwnd, loose, max_count=0, allow_duplicates=True)
    add_text(hwnd, rules, "左侧：重复值会被拒绝，上限满后新增失败。右侧：相同标签可共存，适合保留用户输入历史。", 34, 172, w - 112, 28, MUTED)

    api = add_demo_panel(hwnd, stage, "🎛️ 运行时 API：增删、预填草稿、重置与聚焦", 28, 586, w - 56, 240)
    api_tag = ui.create_input_tag(
        hwnd, api,
        ["产品", "视觉", "发布"],
        "API 按钮会操作这一组标签",
        34, 70, w - 128, 72,
    )
    ui.set_input_tag_options(hwnd, api_tag, max_count=6, allow_duplicates=False)

    def add_review(_eid):
        ok = ui.add_input_tag_item(hwnd, api_tag, "评审✅")
        refresh_status("✅ 已尝试追加「评审✅」" if ok else "⚠️ 追加失败：重复或超过上限", api_tag)

    def add_duplicate(_eid):
        ok = ui.add_input_tag_item(hwnd, api_tag, "产品")
        refresh_status("✅ 已追加重复标签" if ok else "🚫 去重生效：重复的「产品」未加入", api_tag)

    def remove_first(_eid):
        ok = ui.remove_input_tag_item(hwnd, api_tag, 0)
        refresh_status("🧹 已删除第一项" if ok else "⚠️ 没有可删除的第一项", api_tag)

    def preset_draft(_eid):
        ui.set_input_tag_input_value(hwnd, api_tag, "待提交✨")
        ui.dll.EU_SetElementFocus(hwnd, api_tag)
        refresh_status("✏️ 已预填草稿并聚焦，按回车可提交", api_tag)

    def reset_api(_eid):
        set_tags(api_tag, ["产品", "视觉", "发布"])
        ui.set_input_tag_input_value(hwnd, api_tag, "")
        refresh_status("🔄 已重置为默认标签", api_tag)

    actions = [
        ("➕", "追加评审", add_review),
        ("🚫", "测试重复", add_duplicate),
        ("🧹", "删除第一项", remove_first),
        ("✏️", "预填草稿", preset_draft),
        ("🔄", "重置", reset_api),
    ]
    for i, (emoji, label, handler) in enumerate(actions):
        btn = ui.create_button(hwnd, api, emoji, label, 34 + i * 138, 166, 122, 36, variant=1 if i == 0 else 0)
        set_click(hwnd, btn, handler)
    add_text(hwnd, api, "按钮覆盖 EU_AddInputTagItem、EU_RemoveInputTagItem、EU_SetInputTagInputValue、EU_SetInputTagTags、EU_SetElementFocus。", 750, 170, max(360, w - 840), 36, MUTED)

    states = add_demo_panel(hwnd, stage, "📚 状态读回与禁用态", 28, 854, w - 56, 190)
    disabled = ui.create_input_tag(hwnd, states, ["只读展示", "不可编辑"], "禁用态不会接收输入", 34, 70, 520, 66)
    ui.set_element_enabled(hwnd, disabled, False)
    read_btn = ui.create_button(hwnd, states, "📤", "读取 API 组状态", 590, 82, 170, 38, variant=1)
    focus_btn = ui.create_button(hwnd, states, "🎯", "聚焦基础输入", 782, 82, 150, 38)
    set_click(hwnd, read_btn, lambda _eid: refresh_status("📤 已读取 API 组状态", api_tag))
    set_click(hwnd, focus_btn, lambda _eid: (ui.dll.EU_SetElementFocus(hwnd, main_tag), refresh_status("🎯 已聚焦基础输入", main_tag)))
    add_text(hwnd, states, "禁用态用于表单详情页只读展示；读回区会显示标签数量、配置、草稿输入值和每个标签文本。", 34, 142, w - 112, 28, MUTED)

    refresh_status("✅ InputTag 完整演示已加载", main_tag)


def showcase_select(hwnd, stage, w, h):
    add_text(hwnd, stage, "📋 Select 覆盖基础选择、禁用项、可搜索、多选、程序打开/关闭、动态选项和状态读回。", 36, 28, w - 72, 30, MUTED)
    status = add_text(hwnd, stage, "📌 状态：等待选择。", 36, h - 66, w - 72, 30, MUTED)

    city_options = ["北京 🏛️", "上海 🌃", "深圳 🌊", "杭州 🌿", "成都 🐼", "西安 🏯"]

    def label_at(options, index):
        return options[index] if 0 <= index < len(options) else "未选择"

    def selected_labels(select_id, options):
        indices = ui.get_select_selected_indices(hwnd, select_id)
        return "、".join(label_at(options, i) for i in indices) or "无"

    def align_name(value):
        return {0: "左对齐", 1: "居中", 2: "右对齐"}.get(value, "左对齐")

    def refresh_status(message, select_id, options, multiple=False):
        if multiple:
            selected = selected_labels(select_id, options)
        else:
            selected = label_at(options, ui.get_select_index(hwnd, select_id))
        ui.set_element_text(
            hwnd, status,
            f"{message} · 当前：{selected} · 选项 {ui.get_select_option_count(hwnd, select_id)} · "
            f"匹配 {ui.get_select_matched_count(hwnd, select_id)} · 表项{align_name(ui.get_select_option_alignment(hwnd, select_id))} · "
            f"已选值{align_name(ui.get_select_value_alignment(hwnd, select_id))} · 打开 {'是' if ui.get_select_open(hwnd, select_id) else '否'}"
        )

    basics = add_demo_panel(hwnd, stage, "⭐ 标准演示：默认值、占位符、禁用项、整控件禁用与表项对齐", 28, 70, w - 56, 230)
    basic = ui.create_select(hwnd, basics, "选择城市", city_options, 1, 36, 72, 360, 40)
    ui.set_select_open(hwnd, basic, True)
    ui.set_select_option_disabled(hwnd, basic, 4, True)
    center = ui.create_select(hwnd, basics, "居中表项", city_options, -1, 430, 72, 360, 40)
    ui.set_select_option_alignment(hwnd, center, 1)
    ui.set_select_value_alignment(hwnd, center, 1)
    ui.set_select_open(hwnd, center, True)
    disabled = ui.create_select(hwnd, basics, "只读城市", ["南京 📍", "苏州 🧵", "无锡 🌉"], 0, 824, 72, 330, 40)
    ui.set_element_enabled(hwnd, disabled, False)
    add_text(hwnd, basics, "左侧保持默认左对齐；中间表项居中；成都被设为禁用项，方便首屏直接检查浮层样式。", 36, 174, w - 128, 28, MUTED)

    @ui.ValueCallback
    def on_basic_change(_element_id, value, count, action):
        ui.set_element_text(hwnd, status, f"📣 基础 Select 回调：索引 {value} · 数量 {count} · 动作 {action} · {label_at(city_options, value)}")

    keep_callback(on_basic_change)
    ui.dll.EU_SetSelectChangeCallback(hwnd, basic, on_basic_change)

    search = add_demo_panel(hwnd, stage, "🔎 搜索过滤与长文本选项", 28, 330, w - 56, 210)
    search_options = [
        "前端组件库维护计划 ✨",
        "后端接口联调任务 🔌",
        "设计走查与视觉验收 🎨",
        "发布前冒烟测试 ✅",
        "用户反馈整理 📮",
        "性能分析与渲染优化 🚀",
    ]
    searchable = ui.create_select(hwnd, search, "选择任务类型", search_options, 0, 36, 72, 520, 40)
    ui.set_select_search(hwnd, searchable, "测试")
    ui.set_select_open(hwnd, searchable, True)
    ui.set_select_option_alignment(hwnd, searchable, 2)
    ui.set_select_value_alignment(hwnd, searchable, 2)
    add_text(hwnd, search, "通过 EU_SetSelectSearch 预填「测试」，下拉中只保留匹配项；输入框仍显示当前已选项。", 590, 80, max(420, w - 730), 48, MUTED)
    add_text(hwnd, search, f"当前匹配数量：{ui.get_select_matched_count(hwnd, searchable)} · 表项右对齐", 36, 154, 480, 26, TEXT)

    multi = add_demo_panel(hwnd, stage, "☑️ 多选模式：预选、追加与清空", 28, 570, w - 56, 230)
    tag_options = ["需求 📝", "设计 🎨", "开发 💻", "测试 ✅", "发布 🚀", "复盘 📊"]
    multi_id = ui.create_select(hwnd, multi, "选择流程标签", tag_options, 0, 36, 72, 520, 40)
    ui.set_select_multiple(hwnd, multi_id, True)
    ui.set_select_selected_indices(hwnd, multi_id, [0, 2, 4])
    ui.set_select_open(hwnd, multi_id, True)
    ui.set_select_option_alignment(hwnd, multi_id, 1)

    def add_test(_eid):
        ui.set_select_selected_indices(hwnd, multi_id, [0, 2, 3, 4])
        refresh_status("✅ 已追加「测试」", multi_id, tag_options, True)

    def clear_multi(_eid):
        ui.set_select_selected_indices(hwnd, multi_id, [])
        refresh_status("🧹 已清空多选", multi_id, tag_options, True)

    def read_multi(_eid):
        refresh_status("📤 已读取多选状态", multi_id, tag_options, True)

    buttons = [
        ("➕", "追加测试", add_test),
        ("🧹", "清空", clear_multi),
        ("📤", "读取状态", read_multi),
    ]
    for i, (emoji, label, handler) in enumerate(buttons):
        btn = ui.create_button(hwnd, multi, emoji, label, 600 + i * 132, 74, 116, 36, variant=1 if i == 0 else 0)
        set_click(hwnd, btn, handler)
    add_text(hwnd, multi, "多选值通过 EU_SetSelectSelectedIndices 写入，勾选列保留在左侧，表项文本区域可独立居中/右对齐。", 36, 154, w - 128, 28, MUTED)

    api = add_demo_panel(hwnd, stage, "🎛️ 运行时 API：选项替换、索引、打开状态和禁用项", 28, 830, w - 56, 210)
    api_options = ["标准套餐 🍱", "专业套餐 🚀", "企业套餐 🏢"]
    api_select = ui.create_select(hwnd, api, "购买方案", api_options, 1, 36, 72, 380, 40)

    def replace_options(_eid):
        api_options[:] = ["个人版 🌱", "团队版 🤝", "旗舰版 👑", "教育版 🎓"]
        ui.set_select_options(hwnd, api_select, api_options)
        ui.set_select_index(hwnd, api_select, 2)
        ui.set_select_open(hwnd, api_select, True)
        refresh_status("🔄 已替换选项并选中旗舰版", api_select, api_options)

    def toggle_open(_eid):
        ui.set_select_open(hwnd, api_select, not bool(ui.get_select_open(hwnd, api_select)))
        refresh_status("📂 已切换打开状态", api_select, api_options)

    def disable_second(_eid):
        disabled_now = not bool(ui.get_select_option_disabled(hwnd, api_select, 1))
        ui.set_select_option_disabled(hwnd, api_select, 1, disabled_now)
        refresh_status("🔒 已切换第二项禁用状态", api_select, api_options)

    def cycle_align(_eid):
        next_align = (ui.get_select_option_alignment(hwnd, api_select) + 1) % 3
        ui.set_select_option_alignment(hwnd, api_select, next_align)
        ui.set_select_value_alignment(hwnd, api_select, next_align)
        ui.set_select_open(hwnd, api_select, True)
        refresh_status(f"↔️ 已切换表项和已选值{align_name(next_align)}", api_select, api_options)

    for i, (emoji, label, handler) in enumerate([
        ("🔄", "替换选项", replace_options),
        ("📂", "开关浮层", toggle_open),
        ("🔒", "禁用第二项", disable_second),
        ("↔️", "切换对齐", cycle_align),
        ("📤", "读取状态", lambda _eid: refresh_status("📤 已读取 API 选择器", api_select, api_options)),
    ]):
        btn = ui.create_button(hwnd, api, emoji, label, 444 + i * 122, 74, 108, 36, variant=1 if i == 0 else 0)
        set_click(hwnd, btn, handler)
    add_text(hwnd, api, "这些按钮覆盖 SetOptions / SetIndex / SetOpen / SetOptionDisabled / SetOptionAlignment / SetValueAlignment。", 36, 154, w - 128, 28, MUTED)
    refresh_status("✅ Select 完整演示已加载", basic, city_options)


def showcase_select_v2(hwnd, stage, w, h):
    add_text(hwnd, stage, "🧾 SelectV2 重点展示大量候选、虚拟滚动、可见数量、搜索匹配、禁用项、滚动索引、回调和状态读回。", 36, 28, w - 72, 30, MUTED)
    status = add_text(hwnd, stage, "📌 状态：等待操作。", 36, h - 66, w - 72, 30, MUTED)

    components = [
        f"{i:02d} · {'基础' if i <= 8 else '业务'}组件 {emoji}"
        for i, emoji in enumerate([
            "🧱", "🚀", "⌨️", "📋", "🧾", "⭐", "🎨", "🔎", "📅", "🌳",
            "🔁", "📤", "🖼️", "🎠", "📊", "💬", "🔔", "📚", "🧭", "✅",
            "📌", "🪪", "🕒", "📈", "🎯", "🍩", "📑", "🧩", "🛠️", "✨",
        ], start=1)
    ]

    def label_at(options, index):
        return options[index] if 0 <= index < len(options) else "未选择"

    def align_name(value):
        return {0: "左对齐", 1: "居中", 2: "右对齐"}.get(value, "左对齐")

    def refresh_status(message, select_id, options):
        ui.set_element_text(
            hwnd, status,
            f"{message} · 当前：{label_at(options, ui.get_select_v2_index(hwnd, select_id))} · "
            f"总数 {ui.get_select_v2_option_count(hwnd, select_id)} · 匹配 {ui.get_select_v2_matched_count(hwnd, select_id)} · "
            f"可见 {ui.get_select_v2_visible_count(hwnd, select_id)} · 表项{align_name(ui.get_select_v2_option_alignment(hwnd, select_id))} · "
            f"已选值{align_name(ui.get_select_v2_value_alignment(hwnd, select_id))} · 滚动 {ui.get_select_v2_scroll_index(hwnd, select_id)} · "
            f"打开 {'是' if ui.get_select_v2_open(hwnd, select_id) else '否'}"
        )

    large = add_demo_panel(hwnd, stage, "⭐ 大量候选与虚拟列表", 28, 70, w - 56, 250)
    large_id = ui.create_select_v2(hwnd, large, "选择组件", components, 14, 6, 36, 72, 520, 40)
    ui.set_select_v2_open(hwnd, large_id, True)
    ui.set_select_v2_scroll_index(hwnd, large_id, 10)
    ui.set_select_v2_option_disabled(hwnd, large_id, 17, True)
    add_text(hwnd, large, "默认左对齐并滚动到第 11 项附近；第 18 项被禁用，适合检查虚拟列表和禁用态绘制。", 590, 82, max(420, w - 730), 52, MUTED)

    @ui.ValueCallback
    def on_large_change(_element_id, value, count, action):
        ui.set_element_text(hwnd, status, f"📣 SelectV2 回调：索引 {value} · 数量 {count} · 动作 {action} · {label_at(components, value)}")

    keep_callback(on_large_change)
    ui.dll.EU_SetSelectV2ChangeCallback(hwnd, large_id, on_large_change)

    search = add_demo_panel(hwnd, stage, "🔎 搜索匹配与可见数量", 28, 350, w - 56, 220)
    search_id = ui.create_select_v2(hwnd, search, "搜索组件", components, 0, 5, 36, 72, 520, 40)
    ui.set_select_v2_search(hwnd, search_id, "图")
    ui.set_select_v2_open(hwnd, search_id, True)
    ui.set_select_v2_visible_count(hwnd, search_id, 4)
    ui.set_select_v2_option_alignment(hwnd, search_id, 2)
    ui.set_select_v2_value_alignment(hwnd, search_id, 2)
    add_text(hwnd, search, f"搜索词「图」当前匹配 {ui.get_select_v2_matched_count(hwnd, search_id)} 项；可见数量设为 4，表项与已选值右对齐。", 590, 80, max(420, w - 730), 28, MUTED)

    size_panel = add_demo_panel(hwnd, stage, "📏 可见数量矩阵：3 / 6 / 9", 28, 600, w - 56, 230)
    small = ui.create_select_v2(hwnd, size_panel, "紧凑列表", components, 2, 3, 36, 72, 340, 40)
    normal = ui.create_select_v2(hwnd, size_panel, "常规列表", components, 8, 6, 416, 72, 340, 40)
    tall = ui.create_select_v2(hwnd, size_panel, "长列表", components, 20, 9, 796, 72, 340, 40)
    ui.set_select_v2_option_alignment(hwnd, normal, 1)
    ui.set_select_v2_option_alignment(hwnd, tall, 2)
    ui.set_select_v2_value_alignment(hwnd, normal, 1)
    ui.set_select_v2_value_alignment(hwnd, tall, 2)
    for sid, scroll in ((small, 0), (normal, 6), (tall, 18)):
        ui.set_select_v2_open(hwnd, sid, True)
        ui.set_select_v2_scroll_index(hwnd, sid, scroll)
    add_text(hwnd, size_panel, "三列分别为左对齐、居中、右对齐；同一数据源用不同 visible_count 呈现不同高度。", 36, 166, w - 128, 28, MUTED)

    api = add_demo_panel(hwnd, stage, "🎛️ 运行时 API：替换数据、滚动定位、开关浮层和禁用项", 28, 860, w - 56, 180)
    api_options = [f"客户 {i:03d} · {'重点' if i % 7 == 0 else '普通'}客户 {'⭐' if i % 7 == 0 else '📇'}" for i in range(1, 81)]
    api_id = ui.create_select_v2(hwnd, api, "选择客户", api_options, 6, 7, 36, 70, 520, 40)

    def jump_middle(_eid):
        ui.set_select_v2_scroll_index(hwnd, api_id, 38)
        ui.set_select_v2_index(hwnd, api_id, 42)
        ui.set_select_v2_open(hwnd, api_id, True)
        refresh_status("🎯 已定位到客户 043", api_id, api_options)

    def filter_vip(_eid):
        ui.set_select_v2_search(hwnd, api_id, "重点")
        ui.set_select_v2_open(hwnd, api_id, True)
        refresh_status("⭐ 已筛选重点客户", api_id, api_options)

    def toggle_open(_eid):
        ui.set_select_v2_open(hwnd, api_id, not bool(ui.get_select_v2_open(hwnd, api_id)))
        refresh_status("📂 已切换浮层", api_id, api_options)

    def replace_data(_eid):
        api_options[:] = [f"工单 {i:03d} · {'紧急' if i % 5 == 0 else '待处理'} {'🚨' if i % 5 == 0 else '🧾'}" for i in range(1, 61)]
        ui.set_select_v2_options(hwnd, api_id, api_options)
        ui.set_select_v2_search(hwnd, api_id, "")
        ui.set_select_v2_index(hwnd, api_id, 4)
        ui.set_select_v2_open(hwnd, api_id, True)
        refresh_status("🔄 已替换为工单数据", api_id, api_options)

    def cycle_align(_eid):
        next_align = (ui.get_select_v2_option_alignment(hwnd, api_id) + 1) % 3
        ui.set_select_v2_option_alignment(hwnd, api_id, next_align)
        ui.set_select_v2_value_alignment(hwnd, api_id, next_align)
        ui.set_select_v2_open(hwnd, api_id, True)
        refresh_status(f"↔️ 已切换表项和已选值{align_name(next_align)}", api_id, api_options)

    for i, (emoji, label, handler) in enumerate([
        ("🎯", "跳到中段", jump_middle),
        ("⭐", "筛选重点", filter_vip),
        ("📂", "开关浮层", toggle_open),
        ("↔️", "切换对齐", cycle_align),
        ("🔄", "替换数据", replace_data),
        ("📤", "读取状态", lambda _eid: refresh_status("📤 已读取 SelectV2 状态", api_id, api_options)),
    ]):
        btn = ui.create_button(hwnd, api, emoji, label, 592 + i * 112, 72, 100, 36, variant=1 if i == 0 else 0)
        set_click(hwnd, btn, handler)
    add_text(hwnd, api, "SelectV2 的滚动索引、匹配数量和表项对齐适合大数据候选；当前演示用客户和工单模拟。", 36, 142, w - 128, 28, MUTED)
    refresh_status("✅ SelectV2 完整演示已加载", large_id, components)


def showcase_inputnumber(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🔢 基础、精度与范围", 28, 30, w - 56, 170)
    ui.create_input_number(hwnd, basics, "数量 📦", 8, 0, 99, 1, 36, 70, 200, 42)
    amount_id = ui.create_input_number(hwnd, basics, "金额 💰", 9900, 0, 20000, 25, 280, 70, 220, 42)
    ui.set_input_number_precision(hwnd, amount_id, 2)
    ui.create_input_number(hwnd, basics, "百分比 %", 68, 0, 100, 1, 550, 70, 180, 42)
    ui.create_input_number(hwnd, basics, "温度 🌡️", 25, -20, 60, 5, 36, 120, 200, 42)
    ui.create_input_number(hwnd, basics, "页码 📄", 1, 1, 500, 1, 280, 120, 160, 42)
    add_text(hwnd, basics, "支持整数与小数精度、正负范围、步长可配。数值默认居中显示。", 520, 120, 450, 24, MUTED)

    states = add_demo_panel(hwnd, stage, "🚫 禁用与严格步进", 28, 224, w - 56, 140)
    disabled = ui.create_input_number(hwnd, states, "禁用态 🔒", 5, 0, 10, 1, 36, 66, 200, 42)
    ui.set_element_enabled(hwnd, disabled, False)
    strict2 = ui.create_input_number(hwnd, states, "步进×2 🔒", 4, 0, 10, 2, 280, 66, 200, 42)
    ui.set_input_number_step_strictly(hwnd, strict2, True)
    strict5 = ui.create_input_number(hwnd, states, "步进×5 🔒", 10, 0, 50, 5, 530, 66, 200, 42)
    ui.set_input_number_step_strictly(hwnd, strict5, True)
    add_text(hwnd, states, "禁用后不可交互、视觉灰化；严格步进确保值始终为步长整数倍。", 36, 106, 760, 24, MUTED)

    edit = add_demo_panel(hwnd, stage, "⌨️ 键盘编辑与校验", 28, 388, w - 56, 180)
    key1 = ui.create_input_number(hwnd, edit, "键盘操作 ⌨️", 5, 1, 20, 1, 36, 66, 220, 42)
    key2 = ui.create_input_number(hwnd, edit, "小数精度 🎯", 1250, 0, 9999, 50, 300, 66, 240, 42)
    ui.set_input_number_precision(hwnd, key2, 2)
    add_text(hwnd, edit, "支持 ↑↓←→ / PageUp / PageDown / Home / End / Enter / Esc / Backspace 全键盘操作。", 36, 126, 900, 24, MUTED)
    add_text(hwnd, edit, "点击数值区域进入编辑模式，可直接键入数字、小数点、负号；失焦或回车提交，Esc 取消。", 36, 148, 900, 24, MUTED)


def showcase_switch(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🎚️ 基础、文字与禁用", 28, 30, w - 56, 160)
    sw1 = ui.create_switch(hwnd, basics, "通知提醒 🔔", True, 36, 68, 200, 36)
    ui.set_switch_texts(hwnd, sw1, "开", "关")
    ui.create_switch(hwnd, basics, "自动更新 ⚡", True, 260, 68, 200, 36)
    disabled = ui.create_switch(hwnd, basics, "禁用态 🔒", True, 500, 68, 200, 36)
    ui.set_element_enabled(hwnd, disabled, False)
    off_disabled = ui.create_switch(hwnd, basics, "禁用关闭 🔒", False, 730, 68, 200, 36)
    ui.set_element_enabled(hwnd, off_disabled, False)
    add_text(hwnd, basics, "开关支持自定义文字标签、加载动画和禁用态，点击或 Space/Enter 切换。", 36, 118, 900, 24, MUTED)

    colors = add_demo_panel(hwnd, stage, "🎨 自定义颜色", 28, 214, w - 56, 150)
    green_on = ui.create_switch(hwnd, colors, "按月付费 💰", True, 36, 68, 220, 36)
    ui.set_switch_active_color(hwnd, green_on, 0xFF13CE66)
    ui.set_switch_inactive_color(hwnd, green_on, 0xFFFF4949)
    ui.set_switch_texts(hwnd, green_on, "月付", "年付")
    red_off = ui.create_switch(hwnd, colors, "状态监控 🟢", False, 360, 68, 220, 36)
    ui.set_switch_active_color(hwnd, red_off, 0xFF34D399)
    ui.set_switch_inactive_color(hwnd, red_off, 0xFF6B7280)
    yellow_on = ui.create_switch(hwnd, colors, "性能模式 ⚡", True, 690, 68, 220, 36)
    ui.set_switch_active_color(hwnd, yellow_on, 0xFFF59E0B)
    ui.set_switch_inactive_color(hwnd, yellow_on, 0xFF4B5563)
    add_text(hwnd, colors, "自定义选中/未选中颜色覆盖主题默认色，0 值恢复主题色。", 36, 114, 900, 24, MUTED)

    custom = add_demo_panel(hwnd, stage, "🔢 自定义值与尺寸", 28, 388, w - 56, 150)
    s1 = ui.create_switch(hwnd, custom, "默认尺寸", True, 36, 66, 180, 36)
    s2 = ui.create_switch(hwnd, custom, "中等尺寸", True, 260, 66, 180, 36)
    ui.set_switch_size(hwnd, s2, 1)
    s3 = ui.create_switch(hwnd, custom, "小型尺寸", True, 480, 66, 180, 36)
    ui.set_switch_size(hwnd, s3, 2)
    val_switch = ui.create_switch(hwnd, custom, "值=100", True, 700, 66, 180, 36)
    ui.set_switch_value(hwnd, val_switch, 100)
    val = ui.get_switch_value(hwnd, val_switch)
    add_text(hwnd, custom, f"自定义开关值：{'开' if val == 100 else '关'} (value={val}) · 尺寸：默认/中等/小型", 36, 114, 900, 24, MUTED)


def showcase_datepicker(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "📆 基础日期、区间与格式", 28, 30, w - 56, 170)
    ui.create_datepicker(hwnd, basics, 2026, 5, 3, 30, 60, 240, 42)
    dpr = ui.create_datepicker(hwnd, basics, 2026, 5, 1, 360, 60, 260, 42)
    ui.dll.EU_SetDatePickerSelectionRange(hwnd, dpr, 20260501, 20260510, 1)
    ui.set_datepicker_range_separator(hwnd, dpr, " ~ ")
    ui.create_datepicker(hwnd, basics, 2026, 5, 15, 700, 60, 220, 42)
    ui.set_datepicker_align(hwnd, dpr, 1)
    add_text(hwnd, basics, "DatePicker 支持单日、区间选择、自定义分隔符和对齐方式。", 30, 118, w - 116, 24, MUTED)

    modes = add_demo_panel(hwnd, stage, "🔀 月/年模式与多选", 28, 224, w - 56, 150)
    dm = ui.create_datepicker(hwnd, modes, 2026, 5, 3, 30, 60, 220, 42)
    ui.set_datepicker_mode(hwnd, dm, 1)
    dy = ui.create_datepicker(hwnd, modes, 2026, 5, 3, 360, 60, 220, 42)
    ui.set_datepicker_mode(hwnd, dy, 2)
    dms = ui.create_datepicker(hwnd, modes, 2026, 5, 3, 660, 60, 220, 42)
    ui.set_datepicker_multi_select(hwnd, dms, True)
    add_text(hwnd, modes, "点击标题可切换日期→月→年模式；多选模式下点击日期增删选中项。", 30, 116, w - 116, 24, MUTED)

    extra = add_demo_panel(hwnd, stage, "⚡ 快捷选项与占位符", 28, 398, w - 56, 150)
    ds = ui.create_datepicker(hwnd, extra, 2026, 5, 3, 30, 60, 260, 42)
    ui.set_datepicker_shortcuts(hwnd, ds, "📍 今天|20260504\n📆 昨天|20260503\n📅 一周前|20260427")
    dp = ui.create_datepicker(hwnd, extra, 2026, 5, 3, 390, 60, 240, 42)
    ui.set_datepicker_placeholder(hwnd, dp, "请选择日期 📅")
    ui.dll.EU_ClearDatePicker(hwnd, dp)
    dpf = ui.create_datepicker(hwnd, extra, 2026, 5, 3, 700, 60, 200, 42)
    ui.set_datepicker_format(hwnd, dpf, "YYYY/MM/DD")
    add_text(hwnd, extra, "快捷选项替换默认「今天/清空」按钮；占位符在无值时显示；格式支持自定义。", 30, 116, w - 116, 24, MUTED)


def showcase_datetimepicker(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🗓️ 基础日期时间与默认时间", 28, 30, w - 56, 160)
    d1 = ui.create_datetimepicker(hwnd, basics, 2026, 5, 3, 9, 30, 30, 60, 320, 42)
    d2 = ui.create_datetimepicker(hwnd, basics, 2026, 5, 3, 14, 0, 400, 60, 320, 42)
    ui.set_datetimepicker_default_time(hwnd, d2, 12, 0)
    add_text(hwnd, basics, "DateTimePicker 整合日期网格和时间列；default-time 指定选取日期后的默认时刻。", 30, 120, w - 116, 24, MUTED)

    extra = add_demo_panel(hwnd, stage, "⚡ 快捷选项与日期时间区间", 28, 214, w - 56, 160)
    ds = ui.create_datetimepicker(hwnd, extra, 2026, 5, 3, 10, 0, 30, 60, 320, 42)
    ui.set_datetimepicker_shortcuts(hwnd, ds, "📍 今天|20260504\n📆 昨天|20260503\n📅 一周前|20260427")
    dr = ui.create_datetimepicker(hwnd, extra, 2026, 5, 1, 9, 0, 420, 60, 420, 42)
    ui.set_datetimepicker_range_select(hwnd, dr, True, 20260501, 900, 20260510, 1800)
    add_text(hwnd, extra, "快捷选项与 DatePicker 格式一致；区间模式支持开始/结束日期时间。", 30, 120, w - 116, 24, MUTED)


def showcase_timepicker(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "⏰ 基础时间与箭头控制", 28, 30, w - 56, 160)
    ui.create_timepicker(hwnd, basics, 9, 30, 30, 60, 220, 42)
    ui.create_timepicker(hwnd, basics, 14, 0, 300, 60, 220, 42)
    ta = ui.create_timepicker(hwnd, basics, 18, 45, 580, 60, 220, 42)
    ui.set_timepicker_arrow_control(hwnd, ta, True)
    add_text(hwnd, basics, "TimePicker 双列（小时/分钟）滚动选择；arrow-control 模式在列顶部显示箭头按钮。", 30, 120, w - 116, 24, MUTED)

    extra = add_demo_panel(hwnd, stage, "📏 范围约束与时间区间", 28, 214, w - 56, 160)
    tr1 = ui.create_timepicker(hwnd, extra, 10, 0, 30, 60, 240, 42)
    ui.set_timepicker_range(hwnd, tr1, 900, 1800)
    tr2 = ui.create_timepicker(hwnd, extra, 9, 0, 340, 60, 240, 42)
    ui.set_timepicker_range_select(hwnd, tr2, True, 900, 1800)
    tr3 = ui.create_timepicker(hwnd, extra, 12, 0, 650, 60, 200, 42)
    ui.set_timepicker_options(hwnd, tr3, 30, 1)
    add_text(hwnd, extra, "范围约束仅允许工作时间选择；区间模式支持开始/结束时间；格式切换中文显示。", 30, 120, w - 116, 24, MUTED)


def showcase_timeselect(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🕘 基础候选与分组", 28, 30, w - 56, 160)
    ui.create_time_select(hwnd, basics, 10, 0, 30, 60, 220, 42)
    ts2 = ui.create_time_select(hwnd, basics, 14, 30, 300, 60, 220, 42)
    ui.set_time_select_options(hwnd, ts2, 15, 1)
    ts3 = ui.create_time_select(hwnd, basics, 18, 0, 580, 60, 240, 42)
    ui.set_time_select_range(hwnd, ts3, 800, 2000)
    add_text(hwnd, basics, "TimeSelect 下拉候选列表，凌晨/上午/下午/晚上自动分组；步进和范围可配。", 30, 120, w - 116, 24, MUTED)

    extra = add_demo_panel(hwnd, stage, "📝 占位符与格式", 28, 214, w - 56, 140)
    tsp = ui.create_time_select(hwnd, extra, 9, 0, 30, 60, 280, 42)
    ui.set_time_select_placeholder(hwnd, tsp, "请选择时间 🕐")
    tsf = ui.create_time_select(hwnd, extra, 12, 0, 380, 60, 240, 42)
    ui.set_time_select_options(hwnd, tsf, 30, 1)
    ui.set_time_select_placeholder(hwnd, tsf, "会议时间 📋")
    add_text(hwnd, extra, "占位符文本替代默认时间显示；格式切换支持 HH时MM分 中文格式。", 30, 106, w - 116, 24, MUTED)


def showcase_daterangepicker(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "📅 双面板日期范围", 28, 30, w - 56, 170)
    d1 = ui.create_date_range_picker(hwnd, basics, 20260501, 20260510, 30, 60, 400, 42)
    d2 = ui.create_date_range_picker(hwnd, basics, 20260501, 20260515, 520, 60, 380, 42)
    ui.set_date_range_picker_format(hwnd, d2, 1)
    ui.set_date_range_picker_separator(hwnd, d2, " ~ ")
    add_text(hwnd, basics, "双面板日历：左面板选开始日期、右面板选结束日期，一次操作完成。格式和分隔符可自定义。", 30, 120, w - 116, 24, MUTED)

    extra = add_demo_panel(hwnd, stage, "⚡ 快捷选项与占位符", 28, 224, w - 56, 150)
    d3 = ui.create_date_range_picker(hwnd, extra, 0, 0, 30, 60, 400, 42)
    ui.set_date_range_picker_placeholders(hwnd, d3, "入住日期", "离店日期")
    ui.set_date_range_picker_shortcuts(hwnd, d3, "📍 本月|20260501|20260531\n📅 本周|20260504|20260510")
    d4 = ui.create_date_range_picker(hwnd, extra, 0, 0, 520, 60, 360, 42)
    ui.set_date_range_picker_placeholders(hwnd, d4, "开始日期", "结束日期")
    ui.set_date_range_picker_align(hwnd, d4, 1)
    add_text(hwnd, extra, "快捷选项支持单日和范围；占位符在未选时分别显示起止提示。", 30, 116, w - 116, 24, MUTED)


def showcase_timerange(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🕐 时间范围选择", 28, 30, w - 56, 170)
    tr1 = ui.create_timepicker(hwnd, basics, 9, 0, 30, 60, 320, 42)
    ui.set_timepicker_range_select(hwnd, tr1, True, 900, 1200)
    tr2 = ui.create_timepicker(hwnd, basics, 14, 0, 420, 60, 320, 42)
    ui.set_timepicker_range_select(hwnd, tr2, True, 1400, 1800)
    add_text(hwnd, basics, "TimePicker range 模式：点击开始时间 → 点击结束时间，一次性完成时间段选择。", 30, 120, w - 116, 24, MUTED)

    extra = add_demo_panel(hwnd, stage, "📏 约束与格式", 28, 224, w - 56, 150)
    tr3 = ui.create_timepicker(hwnd, extra, 8, 0, 30, 60, 300, 42)
    ui.set_timepicker_range_select(hwnd, tr3, True, 800, 1200)
    ui.set_timepicker_range(hwnd, tr3, 800, 2000)
    tr4 = ui.create_timepicker(hwnd, extra, 13, 0, 430, 60, 300, 42)
    ui.set_timepicker_range_select(hwnd, tr4, True, 1300, 1700)
    ui.set_timepicker_options(hwnd, tr4, 30, 1)
    add_text(hwnd, extra, "结合 min/max 约束和步进，可限定工作时间段选择；格式支持 HH时MM分。", 30, 116, w - 116, 24, MUTED)


def showcase_datetimerange(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🗓️ 日期时间范围", 28, 30, w - 56, 170)
    dr1 = ui.create_datetimepicker(hwnd, basics, 2026, 5, 1, 9, 0, 30, 60, 480, 42)
    ui.set_datetimepicker_range_select(hwnd, dr1, True, 20260501, 900, 20260510, 1800)
    dr2 = ui.create_datetimepicker(hwnd, basics, 2026, 5, 5, 14, 0, 580, 60, 360, 42)
    ui.set_datetimepicker_range_select(hwnd, dr2, True, 20260505, 1400, 20260515, 1700)
    ui.set_datetimepicker_default_time(hwnd, dr2, 14, 0)
    add_text(hwnd, basics, "DateTimePicker range 模式：日期网格 + 时间列，起止各独立选择日期和时间。", 30, 120, w - 116, 24, MUTED)

    extra = add_demo_panel(hwnd, stage, "⚡ 快捷选项与示例", 28, 224, w - 56, 150)
    dr3 = ui.create_datetimepicker(hwnd, extra, 2026, 5, 3, 10, 0, 30, 60, 480, 42)
    ui.set_datetimepicker_range_select(hwnd, dr3, True, 20260503, 1000, 20260510, 1600)
    ui.set_datetimepicker_shortcuts(hwnd, dr3, "📍 今天全天|20260504|20260504\n📅 本周工作日|20260504|20260508")
    add_text(hwnd, extra, "快捷选项复用 DatePicker 格式；default-time 设置日期的默认时间。", 30, 116, w - 116, 24, MUTED)


def showcase_autocomplete(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "🔎 激活即列出 / 输入后匹配", 28, 30, w - 56, 220)
    ui.create_autocomplete(hwnd, basics, value="", placeholder="激活即列出建议",
                           suggestions=["北京", "上海", "广州", "深圳"],
                           trigger_on_focus=True, prefix_icon="🔍",
                           x=36, y=76, w=360, h=40)
    ui.create_autocomplete(hwnd, basics, value="", placeholder="输入后再展开",
                           suggestions=["西安", "西宁", "西双版纳", "西湖"],
                           trigger_on_focus=False, prefix_icon="🔍",
                           x=430, y=76, w=360, h=40)
    ui.create_autocomplete(hwnd, basics, value="餐", placeholder="右侧图标可点击",
                           suggestions=["餐厅名", "餐品", "餐桌号"],
                           suffix_icon="✏️", x=824, y=76, w=300, h=40)
    add_text(hwnd, basics, "trigger_on_focus 可控制是否在聚焦时直接展开建议层。", 36, 150, 620, 24, MUTED)

    detailed = add_demo_panel(hwnd, stage, "📋 双行建议项", 28, 276, w - 56, 230)
    ui.create_autocomplete(
        hwnd, detailed, value="三",
        suggestions=[
            ("三全鲜食（北新泾店）", "长宁区新渔路144号", "三全鲜食（北新泾店）"),
            ("新旺角茶餐厅", "普陀区真北路988号", "新旺角茶餐厅"),
            ("Monica 摩托主题咖啡店", "嘉定区曹安公路2409号", "Monica 摩托主题咖啡店"),
        ],
        placeholder="请输入餐厅名", prefix_icon="🍜", x=36, y=78, w=520, h=40
    )
    add_text(hwnd, detailed, "双行建议项固定为“主标题 + 副信息 + 写回值”，适合地址、联系人、门店等结构化提示。", 594, 86, 620, 28, MUTED)
    ui.create_autocomplete(hwnd, detailed, value="", placeholder="暂时没有匹配项",
                           suggestions=[], trigger_on_focus=True, x=594, y=146, w=360, h=40)
    ui.set_autocomplete_empty_text(hwnd, ui.create_autocomplete(hwnd, detailed, value="", placeholder="异步加载中",
                           suggestions=["加载占位"], trigger_on_focus=True, x=984, y=146, w=220, h=40), "⌛ 正在加载建议...")

    async_panel = add_demo_panel(hwnd, stage, "⏳ 异步与空状态", 28, 534, w - 56, 190)
    loading = ui.create_autocomplete(hwnd, async_panel, value="杭", placeholder="模拟异步请求",
                                     suggestions=["杭州", "杭州西湖", "杭州东站"],
                                     trigger_on_focus=True, suffix_icon="🔄",
                                     x=36, y=74, w=360, h=40)
    ui.set_autocomplete_async_state(hwnd, loading, True, 20260504)
    empty = ui.create_autocomplete(hwnd, async_panel, value="", placeholder="无匹配建议",
                                   suggestions=[], trigger_on_focus=True, x=430, y=74, w=360, h=40)
    ui.set_autocomplete_empty_text(hwnd, empty, "🫥 没有匹配建议")
    add_text(hwnd, async_panel, "Autocomplete 保留上下键、回车、ESC 的键盘路径，同时补齐 placeholder、图标和双行视觉。", 826, 80, 380, 28, MUTED)


def showcase_tag(hwnd, stage, w, h):
    card = add_demo_panel(hwnd, stage, "🏷️ 状态标签组", 28, 30, w - 56, 210)
    tags = [
        ("已完成 🟢", 1, 30, 72), ("构建中 🔵", 0, 174, 72), ("需复查 🟡", 2, 318, 72),
        ("已发布 🚀", 1, 462, 72), ("MIT 许可 📄", 0, 606, 72), ("中文 emoji ✅", 1, 750, 72),
    ]
    for text, kind, x, y in tags:
        ui.create_tag(hwnd, card, text, kind, 0, True, x, y, 128, 34)
    add_text(hwnd, card, "标签适合做状态、分类、筛选条件和可关闭条件项。", 30, 130, w - 116, 30, MUTED)
    filters = add_demo_panel(hwnd, stage, "🔎 筛选条件条", 28, 270, w - 56, 180)
    for i, text in enumerate(["组件：表单", "状态：完成", "主题：深色", "平台：Win32", "语言：中文"]):
        ui.create_tag(hwnd, filters, text, i % 3, 0, True, 30 + i * 170, 72, 140, 34)
    add_text(hwnd, filters, "把 Tag 放成筛选条，比单个标签更接近真实业务界面。", 30, 128, w - 116, 28, MUTED)


def showcase_badge(hwnd, stage, w, h):
    basics = add_demo_panel(hwnd, stage, "\U0001F516 Badge \u6837\u5f0f\u4e0e\u5c42\u6b21", 28, 30, w - 56, 176)
    buy_btn = ui.create_button(hwnd, basics, "\U0001F4E9", "\u65b0\u589e\u6d88\u606f", 36, 72, 160, 38)
    buy_badge = ui.create_badge(hwnd, buy_btn, "", "12", 99, False, 112, 4, 42, 24, placement=0, standalone=True, badge_type=1)
    reply_btn = ui.create_button(hwnd, basics, "\U0001F4AC", "\u65b0\u56de\u590d\u6d88\u606f", 220, 72, 180, 38)
    reply_badge = ui.create_badge(hwnd, reply_btn, "", "200", 99, False, 128, 4, 54, 24, placement=0, standalone=True, badge_type=3)
    ui.create_badge(hwnd, basics, "\u5173\u6ce8", "new", 99, False, 436, 72, 160, 38, badge_type=2)
    ui.create_badge(hwnd, basics, "\u8ba2\u5355", "hot", 99, False, 618, 72, 160, 38, badge_type=3)
    ui.create_badge(hwnd, basics, "\u5168\u90e8\u6d88\u606f", "", 99, True, 800, 72, 210, 38)
    action_state = {"buy": 12, "reply": 200}
    action_status = add_text(hwnd, basics, "\U0001F4CC \u5f53\u524d\u72b6\u6001\uff1a\u5f85\u5904\u7406\u6d88\u606f 12 \u6761\uff0c\u56de\u590d 200 \u6761", 36, 124, w - 116, 28, MUTED)

    def on_buy_click(_eid):
        action_state["buy"] += 1
        ui.set_badge_value(hwnd, buy_badge, str(action_state["buy"]))
        ui.set_element_text(hwnd, action_status, f"\U0001F4E9 \u5df2\u6536\u5230\u65b0\u6d88\u606f\uff1a{action_state['buy']} \u6761")

    def on_reply_click(_eid):
        action_state["reply"] += 5
        ui.set_badge_value(hwnd, reply_badge, str(action_state["reply"]))
        ui.set_element_text(hwnd, action_status, f"\U0001F4AC \u56de\u590d\u961f\u5217\u5df2\u66f4\u65b0\uff1a{action_state['reply']} \u6761")

    set_click(hwnd, buy_btn, on_buy_click)
    set_click(hwnd, reply_btn, on_reply_click)

    layout = add_demo_panel(hwnd, stage, "\U0001F4CD \u89d2\u6807\u4f4d\u7f6e\u4e0e\u72ec\u7acb\u5fbd\u6807", 28, 224, w - 56, 224)
    ui.create_badge(hwnd, layout, "\u53f3\u4e0a\u89d2", "9", 99, False, 36, 68, 180, 40, placement=0, standalone=False, badge_type=1)
    ui.create_badge(hwnd, layout, "\u5de6\u4e0a\u89d2", "9", 99, False, 248, 68, 180, 40, placement=1, standalone=False, badge_type=2)
    ui.create_badge(hwnd, layout, "\u53f3\u4e0b\u89d2", "9", 99, False, 460, 68, 180, 40, placement=2, standalone=False, badge_type=3)
    ui.create_badge(hwnd, layout, "\u5de6\u4e0b\u89d2", "9", 99, False, 672, 68, 180, 40, placement=3, standalone=False, badge_type=4)
    ui.create_badge(hwnd, layout, "", "1", 99, False, 884, 62, 54, 28, placement=0, standalone=True, badge_type=0)
    ui.create_badge(hwnd, layout, "", "2", 99, False, 948, 62, 54, 28, placement=0, standalone=True, badge_type=1)
    ui.create_badge(hwnd, layout, "", "3", 99, False, 1012, 62, 54, 28, placement=0, standalone=True, badge_type=2)
    ui.create_badge(hwnd, layout, "", "4", 99, False, 1076, 62, 54, 28, placement=0, standalone=True, badge_type=3)
    add_text(hwnd, layout, "\u72ec\u7acb\u5fbd\u6807\u9002\u5408\u5355\u72ec\u4fe1\u606f\u70b9\uff1bplacement \u63a7\u5236\u89d2\u6807\u843d\u70b9\uff0cstandalone \u63a7\u5236\u5fbd\u6807\u81ea\u8eab\u5bbd\u5ea6\u8ba1\u7b97\u3002", 36, 132, 980, 28, MUTED)

    semantic = add_demo_panel(hwnd, stage, "\U0001F3A8 \u8bed\u4e49\u914d\u8272 / dropdown mark", 28, 468, w - 56, 270)
    dropdown_id = ui.create_dropdown(hwnd, semantic, "\u70b9\u6211\u67e5\u770b", ["\u8bc4\u8bba", "\u56de\u590d", "\u5df2\u8bfb", "\u672a\u8bfb"], 0, 36, 72, 180, 36)
    ui.set_dropdown_item_meta(hwnd, dropdown_id, ["\U0001F4AC", "\U0001F501", "\u2705", "\U0001F534"], ["comment", "reply", "read", "unread"], [])
    mark_panel = ui.create_panel(hwnd, semantic, 246, 60, 416, 156)
    ui.set_panel_style(hwnd, mark_panel, 0xFF2B3149, BORDER_SOFT, 1.0, 8.0, 10)
    register_panel(mark_panel, "surface_2", "border_soft", 1.0, 8.0, 10)
    comment_mark = ui.create_badge(hwnd, mark_panel, "\u8bc4\u8bba", "12", 99, False, 20, 20, 170, 34, badge_type=1)
    reply_mark = ui.create_badge(hwnd, mark_panel, "\u56de\u590d", "3", 99, False, 20, 62, 170, 34, badge_type=3)
    notice_mark = ui.create_badge(hwnd, mark_panel, "\u901a\u77e5", "new", 99, False, 208, 20, 170, 34, badge_type=2)
    status_mark = ui.create_badge(hwnd, mark_panel, "\u72b6\u6001", "hot", 99, False, 208, 62, 170, 34, badge_type=4)
    custom = ui.create_badge(hwnd, mark_panel, "\u81ea\u5b9a\u4e49", "42", 99, False, 20, 104, 170, 34, badge_type=0)
    ui.set_element_color(hwnd, custom, 0xFFEEE8FF, 0xFF6D28D9)
    dropdown_status = add_text(hwnd, semantic, "\U0001F4CB \u4e0b\u62c9\u9009\u62e9\uff1a\u8bc4\u8bba", 36, 220, 980, 24, MUTED)

    dropdown_rows = [
        ("\u8bc4\u8bba", "12", "3", "new", "hot", "42", 1, 3, 2, 4),
        ("\u56de\u590d", "8", "16", "reply", "todo", "18", 3, 1, 3, 4),
        ("\u5df2\u8bfb", "0", "0", "ok", "done", "99", 2, 2, 2, 4),
        ("\u672a\u8bfb", "24", "5", "new", "!", "128", 0, 3, 2, 0),
    ]

    def apply_dropdown_selection(item_index):
        if item_index < 0 or item_index >= len(dropdown_rows):
            item_index = 0
        label, comments, replies, notice, status, custom_value, comment_type, reply_type, notice_type, status_type = dropdown_rows[item_index]
        ui.set_element_text(hwnd, dropdown_id, f"\u5f53\u524d\uff1a{label}")
        ui.set_badge_value(hwnd, comment_mark, comments)
        ui.set_badge_value(hwnd, reply_mark, replies)
        ui.set_badge_value(hwnd, notice_mark, notice)
        ui.set_badge_value(hwnd, status_mark, status)
        ui.set_badge_value(hwnd, custom, custom_value)
        ui.set_badge_type(hwnd, comment_mark, comment_type)
        ui.set_badge_type(hwnd, reply_mark, reply_type)
        ui.set_badge_type(hwnd, notice_mark, notice_type)
        ui.set_badge_type(hwnd, status_mark, status_type)
        ui.set_element_text(hwnd, dropdown_status, f"\U0001F4CB \u4e0b\u62c9\u9009\u62e9\uff1a{label}\uff0c\u53f3\u4fa7 mark \u5df2\u540c\u6b65")

    @ui.DropdownCommandCallback
    def on_badge_dropdown(_element_id, item_index, _command_bytes, _command_len):
        apply_dropdown_selection(item_index)

    def on_badge_dropdown_click(_element_id):
        if not ui.get_dropdown_open(hwnd, dropdown_id):
            apply_dropdown_selection(ui.get_dropdown_selected(hwnd, dropdown_id))

    keep_callback(on_badge_dropdown)
    ui.set_dropdown_command_callback(hwnd, dropdown_id, on_badge_dropdown)
    set_click(hwnd, dropdown_id, on_badge_dropdown_click)
    add_text(hwnd, semantic, "\u8bed\u4e49\u8272\u901a\u8fc7 BadgeType \u63d0\u4f9b\u9884\u8bbe\u914d\u8272\uff1bEU_SetElementColor \u4ecd\u53ef\u8986\u76d6\u6210\u4efb\u610f\u81ea\u5b9a\u4e49\u8272\u3002", 36, 242, 980, 24, MUTED)


def showcase_progress(hwnd, stage, w, h):
    stops = [
        (0xFFF56C6C, 20),
        (0xFFE6A23C, 40),
        (0xFF5CB87A, 60),
        (0xFF1989FA, 80),
        (0xFF6F7AD3, 100),
    ]
    method_stops = [
        (0xFF909399, 30),
        (0xFFE6A23C, 70),
        (0xFF67C23A, 100),
    ]
    col_gap = 20
    col_w = (w - 56 - col_gap) // 2
    left_x = 28
    right_x = left_x + col_w + col_gap

    def status_for(value):
        if value >= 100:
            return 1
        if value >= 80:
            return 2
        if value <= 30:
            return 3
        return 0

    basic = add_demo_panel(hwnd, stage, "📈 基础与状态", left_x, 30, col_w, 246)
    basic_specs = [
        ("默认进度", 50, 0, None, None),
        ("完成文本", 100, 0, 3, "满"),
        ("成功状态", 100, 1, None, None),
        ("警告状态", 100, 2, None, None),
        ("异常状态", 50, 3, None, None),
    ]
    for i, (label, pct, status, text_format, complete_text) in enumerate(basic_specs):
        ui.create_progress(
            hwnd, basic, label, pct, status,
            24, 58 + i * 34, col_w - 60, 28,
            text_format=text_format, complete_text=complete_text
        )

    inside = add_demo_panel(hwnd, stage, "🧱 文字内显与线宽", right_x, 30, col_w, 246)
    inside_specs = [
        ("发布任务", 70, 0, 26),
        ("同步完成", 100, 1, 24),
        ("容量预警", 80, 2, 22),
        ("构建异常", 50, 3, 20),
    ]
    for i, (label, pct, status, stroke) in enumerate(inside_specs):
        ui.create_progress(
            hwnd, inside, label, pct, status,
            24, 60 + i * 40, col_w - 60, 30,
            stroke_width=stroke, text_inside=True
        )

    custom = add_demo_panel(hwnd, stage, "🎨 自定义颜色", left_x, 300, col_w, 238)
    ui.create_progress(
        hwnd, custom, "静态填充色", 20, 0, 24, 62, col_w - 60, 34,
        fill_color=0xFF409EFF, track_color=0xFFE9EEF5
    )
    ui.create_progress(
        hwnd, custom, "方法式阈值", 66, 0, 24, 110, col_w - 60, 34,
        color_stops=method_stops
    )
    ui.create_progress(
        hwnd, custom, "数组式分段", 88, 0, 24, 158, col_w - 60, 34,
        color_stops=stops, text_format=4, text_template="进度 {percent}"
    )
    add_text(hwnd, custom, "颜色优先级：分段 > 静态色 > 状态色 > 主题默认。", 24, 200, col_w - 60, 24, MUTED)

    interactive = add_demo_panel(hwnd, stage, "🎛️ 交互调节", right_x, 300, col_w, 238)
    state = {"value": 20}
    line = ui.create_progress(
        hwnd, interactive, "部署进度", state["value"], status_for(state["value"]),
        24, 64, col_w - 250, 34,
        color_stops=stops, text_format=4, text_template="{status} {percent}"
    )
    dash = ui.create_progress(
        hwnd, interactive, "仪表盘", state["value"], status_for(state["value"]),
        col_w - 190, 52, 138, 138,
        progress_type=2, stroke_width=12, color_stops=stops
    )
    readout = add_text(hwnd, interactive, "📋 当前：20% · 状态读回 3 · 分段 5", 24, 112, col_w - 260, 26, MUTED)
    minus_btn = ui.create_button(hwnd, interactive, "➖", "", 24, 154, 42, 36, variant=1)
    plus_btn = ui.create_button(hwnd, interactive, "➕", "", 76, 154, 42, 36, variant=1)

    def refresh_interactive():
        value = max(0, min(100, state["value"]))
        state["value"] = value
        status = status_for(value)
        ui.set_progress_percentage(hwnd, line, value)
        ui.set_progress_percentage(hwnd, dash, value)
        ui.set_progress_status(hwnd, line, status)
        ui.set_progress_status(hwnd, dash, status)
        percent = ui.get_progress_percentage(hwnd, line)
        read_status = ui.get_progress_status(hwnd, line)
        stop_count = ui.get_progress_color_stop_count(hwnd, line)
        ui.set_element_text(hwnd, readout, f"📋 当前：{percent}% · 状态读回 {read_status} · 分段 {stop_count}")

    def decrease(_element_id):
        state["value"] -= 10
        refresh_interactive()

    def increase(_element_id):
        state["value"] += 10
        refresh_interactive()

    set_click(hwnd, minus_btn, decrease)
    set_click(hwnd, plus_btn, increase)
    refresh_interactive()

    circle = add_demo_panel(hwnd, stage, "⭕ 圆形进度", left_x, 562, col_w, 242)
    circle_specs = [
        ("0%", 0, 0),
        ("25%", 25, 0),
        ("100% 成功", 100, 1),
        ("70% 警告", 70, 2),
        ("50% 异常", 50, 3),
    ]
    circle_gap = 18
    circle_size = min(124, (col_w - 72 - circle_gap * 4) // 5)
    for i, (label, pct, status) in enumerate(circle_specs):
        x = 24 + i * (circle_size + circle_gap)
        ui.create_progress(
            hwnd, circle, label, pct, status, x, 66, circle_size, circle_size,
            progress_type=1, stroke_width=10
        )
        add_text(hwnd, circle, label, x - 6, 66 + circle_size + 12, circle_size + 12, 24, MUTED)

    dashboard = add_demo_panel(hwnd, stage, "📟 仪表盘进度", right_x, 562, col_w, 242)
    dash_state = {"value": 10}
    dash_main = ui.create_progress(
        hwnd, dashboard, "主仪表盘", dash_state["value"], 0,
        36, 54, 162, 148,
        progress_type=2, stroke_width=13, color_stops=stops,
        text_format=4, text_template="{percent}"
    )
    dash_text = add_text(hwnd, dashboard, "📊 阈值分段已启用：低红、中黄、高绿蓝紫。", 230, 72, col_w - 270, 28, MUTED)
    dash_minus = ui.create_button(hwnd, dashboard, "➖", "", 230, 120, 42, 36, variant=1)
    dash_plus = ui.create_button(hwnd, dashboard, "➕", "", 282, 120, 42, 36, variant=1)
    for i, pct in enumerate([25, 60, 100]):
        ui.create_progress(
            hwnd, dashboard, f"{pct}%", pct, status_for(pct),
            360 + i * 116, 108, 92, 84,
            progress_type=2, stroke_width=8, color_stops=stops
        )

    def refresh_dashboard():
        value = max(0, min(100, dash_state["value"]))
        dash_state["value"] = value
        ui.set_progress_percentage(hwnd, dash_main, value)
        ui.set_progress_status(hwnd, dash_main, status_for(value))
        ui.set_element_text(hwnd, dash_text, f"📊 仪表盘：{value}% · 分段 {ui.get_progress_color_stop_count(hwnd, dash_main)}")

    def dash_decrease(_element_id):
        dash_state["value"] -= 10
        refresh_dashboard()

    def dash_increase(_element_id):
        dash_state["value"] += 10
        refresh_dashboard()

    set_click(hwnd, dash_minus, dash_decrease)
    set_click(hwnd, dash_plus, dash_increase)
    refresh_dashboard()


def showcase_gauge(hwnd, stage, w, h):
    card = add_demo_panel(hwnd, stage, "🎯 质量仪表盘", 28, 30, w - 56, 270)
    ui.create_gauge(hwnd, card, "质量分", 92, "运行良好", 1, 30, 70, 320, 150)
    ui.create_gauge(hwnd, card, "覆盖率", 78, "继续补测", 0, 390, 70, 320, 150)
    ui.create_gauge(hwnd, card, "稳定性", 98, "非常稳", 1, 750, 70, 320, 150)
    rows = add_demo_panel(hwnd, stage, "📈 指标解读", 28, 330, w - 56, 190)
    for i, (title, value, desc) in enumerate([("构建质量", "92%", "Release 通过"), ("测试覆盖", "78%", "重点补交互"), ("运行稳定", "98%", "无闪烁")]):
        x = 30 + i * 350
        panel = ui.create_panel(hwnd, rows, x, 70, 300, 78)
        ui.set_panel_style(hwnd, panel, 0xFF2D3452, BORDER, 1.0, 8.0, 10)
        register_panel(panel, "surface_2", "border", 1.0, 8.0, 10)
        add_text(hwnd, rows, title, x + 18, 82, 160, 24, TEXT)
        add_text(hwnd, rows, value, x + 190, 82, 80, 24, ACCENT)
        add_text(hwnd, rows, desc, x + 18, 114, 230, 24, MUTED)


def showcase_pagination(hwnd, stage, w, h):
    work = add_demo_panel(hwnd, stage, "🔎 搜索结果与审计分页", 28, 30, w - 56, 250)
    add_text(hwnd, work, "搜索结果：共 50 条，页数较少时直接展示全部页码。", 30, 56, w - 116, 24, MUTED)
    basic = ui.create_pagination(hwnd, work, 50, 10, 2, 30, 86, min(w - 116, 620), 40)
    ui.set_pagination_options(hwnd, basic, show_jumper=False, show_size_changer=False, visible_page_count=7)

    add_text(hwnd, work, "审计日志：共 1000 条，超过 7 页时自动折叠为省略号。", 30, 138, w - 116, 24, MUTED)
    audit = ui.create_pagination(hwnd, work, 1000, 20, 18, 30, 168, min(w - 116, 760), 42)
    ui.set_pagination_options(hwnd, audit, show_jumper=False, show_size_changer=False, visible_page_count=7)

    admin = add_demo_panel(hwnd, stage, "📊 后台列表完整分页", 28, 304, w - 56, 210)
    add_text(hwnd, admin, "工单列表：显示总数、每页数量、页码、跳转页，适合桌面端表格页底部工具栏。", 30, 54, w - 116, 24, MUTED)
    full = ui.create_pagination(hwnd, admin, 400, 100, 4, 30, 88, min(w - 116, 900), 46)
    ui.set_pagination_options(hwnd, full, show_jumper=True, show_size_changer=True, visible_page_count=7)
    ui.set_pagination_page_size_options(hwnd, full, [100, 200, 300, 400])
    ui.set_pagination_advanced_options(hwnd, full, background=True, small=False, hide_on_single_page=False)
    ui.create_table(
        hwnd, admin,
        ["模块", "场景", "当前效果"],
        [["Pagination", "后台工单", "完整功能 ✅"], ["Table", "数据展示", "页脚分页 📄"], ["Search", "结果列表", "共 400 条 🔎"]],
        True, True, 30, 144, min(w - 116, 760), 52,
    )

    styles = add_demo_panel(hwnd, stage, "🎨 样式态与隐藏规则", 28, 544, w - 56, 210)
    add_text(hwnd, styles, "背景分页：页码按钮使用色块，更适合工具栏和表格底部。", 30, 48, w - 116, 22, MUTED)
    bg = ui.create_pagination(hwnd, styles, 1000, 20, 9, 30, 74, min(w - 116, 760), 40)
    ui.set_pagination_options(hwnd, bg, show_jumper=False, show_size_changer=False, visible_page_count=11)
    ui.set_pagination_advanced_options(hwnd, bg, background=True, small=False, hide_on_single_page=False)

    add_text(hwnd, styles, "小尺寸：适合紧凑筛选栏；单页隐藏：结果不足一页时不占用界面空间。", 30, 126, w - 116, 22, MUTED)
    small = ui.create_pagination(hwnd, styles, 50, 10, 3, 30, 152, 360, 32)
    ui.set_pagination_options(hwnd, small, show_jumper=False, show_size_changer=False, visible_page_count=7)
    ui.set_pagination_advanced_options(hwnd, small, background=False, small=True, hide_on_single_page=False)
    hidden = ui.create_pagination(hwnd, styles, 5, 20, 1, 430, 152, 260, 32)
    ui.set_pagination_advanced_options(hwnd, hidden, background=True, small=True, hide_on_single_page=True)


def showcase_table(hwnd, stage, w, h):
    add_text(hwnd, stage, "📊 Table 高级样式图库", 34, 28, 420, 30, TEXT)
    status = add_text(hwnd, stage, "✅ 点击表格内按钮、开关、选择框、展开箭头可触发 TableCellCallback。", 34, h - 40, w - 80, 28, MUTED)
    groups = []

    def attach_click(table_id, label):
        ui.set_table_cell_click_callback(hwnd, table_id, keep_callback(ui.TableCellCallback(
            lambda table_id, row, col, action, value: ui.set_element_text(
                hwnd, status, f"🖱️ {label}：Table #{table_id} 行 {row} 列 {col}"
            )
        )))
        print(f"[Table] 已挂载点击回调：{label} #{table_id}")

    def make_order_rows():
        return [
            {"cells": [{"type": "index"}, "2016-05-02", "王小虎 🎯", "上海市普陀区金沙江路 1518 弄", {"type": "tag", "value": "家 🏠"}]},
            {"cells": [{"type": "index"}, "2016-05-04", "李小花 🌸", "上海市普陀区金沙江路 1517 弄", {"type": "tag", "value": "公司 🏢"}]},
            {"cells": [{"type": "index"}, "2016-05-01", "陈小云 ☁️", "上海市普陀区金沙江路 1519 弄", {"type": "tag", "value": "家 🏠"}]},
            {"cells": [{"type": "index"}, "2016-05-03", "赵小星 ⭐", "上海市普陀区金沙江路 1516 弄", {"type": "tag", "value": "公司 🏢"}]},
        ]

    def make_order_columns(extra=False):
        cols = [
            {"title": "序号", "key": "idx", "type": "index", "width": 64, "align": "center"},
            {"title": "日期", "key": "date", "width": 150, "sortable": True, "filterable": True},
            {"title": "姓名", "key": "name", "width": 130, "sortable": True},
            {"title": "地址", "key": "address", "width": 360, "tooltip": True},
            {"title": "标签", "key": "tag", "type": "tag", "width": 120, "align": "center"},
        ]
        if extra:
            cols[0]["fixed"] = "left"
            cols.extend([
                {"title": "省份", "key": "province", "parent": "配送信息", "width": 130},
                {"title": "市区", "key": "city", "parent": "配送信息", "width": 130},
                {"title": "邮编", "key": "zip", "parent": "配送信息", "width": 130},
                {"title": "操作", "key": "action", "type": "buttons", "width": 230, "fixed": "right", "align": "center"},
            ])
        return cols

    def fill_basic(panel):
        table_w = min((w - 132) // 2, 740)
        t1 = ui.create_table_ex(hwnd, panel, make_order_columns(), make_order_rows(), False, False, 28, 76, table_w, 290, row_height=48, header_height=50)
        t2 = ui.create_table_ex(hwnd, panel, make_order_columns(), make_order_rows(), True, True, 56 + table_w, 76, table_w, 290, row_height=48, header_height=50)
        attach_click(t1, "基础样式")
        attach_click(t2, "基础样式")
        ui.set_table_row_style(hwnd, t2, 1, 0xFFFFF7E6, 0xFF7A4B00, 0, 0, 14)
        ui.set_table_row_style(hwnd, t2, 3, 0xFFEAF8EF, 0xFF185A2F, 0, 1, 15)
        ui.set_table_cell_style(hwnd, t2, 0, 3, 0xFFEAF2FF, 0xFF1F3D64, 0, 1, 15)
        add_text(hwnd, panel, "覆盖基础表格、斑马纹、边框、行颜色、单元格颜色、对齐、粗体和字号。", 28, 368, 1040, 28, MUTED)

    def fill_fixed(panel):
        rows = []
        for row in make_order_rows() * 4:
            cells = row["cells"] + ["上海", "普陀区", "200333", {"type": "buttons", "value": ["查看 👀", "编辑 ✏️"]}]
            rows.append({"cells": cells})
        table = ui.create_table_ex(
            hwnd, panel, make_order_columns(extra=True), rows,
            True, True, 28, 76, min(w - 112, 1180), 430,
            selection_mode=1, max_height=430, horizontal_scroll=True,
            row_height=48, header_height=50,
        )
        attach_click(table, "固定滚动")
        ui.set_table_scroll(hwnd, table, 3, 180)
        add_text(hwnd, panel, "固定左列/右列、横向滚动、多级表头、固定表头和最大高度同时开启。", 28, 520, 1040, 28, MUTED)

    def fill_select_filter(panel):
        columns = [
            {"title": "选择", "key": "sel", "type": "selection", "width": 56, "fixed": "left", "align": "center"},
            {"title": "日期", "key": "date", "width": 148, "sortable": True, "filterable": True},
            {"title": "姓名", "key": "name", "width": 140, "sortable": True, "searchable": True},
            {"title": "地址", "key": "address", "width": 380, "tooltip": True},
            {"title": "标签", "key": "tag", "type": "tag", "width": 120, "align": "center", "filterable": True},
            {"title": "操作", "key": "action", "type": "buttons", "width": 230, "fixed": "right"},
        ]
        rows = []
        for row in make_order_rows() + make_order_rows():
            rows.append({"cells": [{"type": "selection"}] + row["cells"][1:] + [{"type": "buttons", "value": ["查看 👀", "删除 🗑️"]}]})
        table = ui.create_table_ex(hwnd, panel, columns, rows, True, True, 28, 76, min(w - 112, 1380), 360, selection_mode=2, max_height=360, row_height=48, header_height=50)
        attach_click(table, "选择筛选")
        ui.set_table_selected_rows(hwnd, table, [0, 2, 4])
        ui.set_table_filter(hwnd, table, 4, "家 🏠")
        ui.set_table_search(hwnd, table, "王")
        ui.set_table_sort(hwnd, table, 1, desc=True)
        add_text(hwnd, panel, "多选列、单选/多选状态、排序、筛选、表头搜索语义和操作列在同一张表中展示。", 28, 438, 1100, 28, MUTED)

    def fill_controls(panel):
        columns = [
            {"title": "任务", "key": "task", "width": 160, "fixed": "left"},
            {"title": "组合款", "key": "combo", "type": "combo", "width": 200},
            {"title": "开关", "key": "enabled", "type": "switch", "width": 80, "align": "center"},
            {"title": "选择框", "key": "choice", "type": "select", "width": 180},
            {"title": "进度", "key": "progress", "type": "progress", "width": 440},
            {"title": "状态", "key": "status", "type": "status", "width": 100},
            {"title": "标签提示", "key": "tag", "type": "popover_tag", "width": 170, "align": "center"},
            {"title": "按钮组", "key": "buttons", "type": "buttons", "width": 220, "fixed": "right"},
        ]
        rows = [
            {"cells": ["🍜 备菜", {"type": "combo", "value": ["待处理", "查看"]}, {"type": "switch", "value": "1", "options": {"checked": True}}, {"type": "select", "value": ["待处理 ⏳", "配送中 🚚", "已完成 ✅"]}, {"type": "progress", "value": 66}, {"type": "status", "value": 2, "options": {"status": 2}}, {"type": "popover_tag", "value": "备货 🧾"}, {"type": "buttons", "value": ["查看 👀", "编辑 ✏️"]}]},
            {"cells": ["🚚 配送", {"type": "combo", "value": ["配送中", "催单"]}, {"type": "switch", "value": "0"}, {"type": "select", "value": ["同城 🚚", "自提 🛍️", "快递 📦"]}, {"type": "progress", "value": 88}, {"type": "status", "value": 1, "options": {"status": 1}}, {"type": "popover_tag", "value": "准时 ✅"}, {"type": "buttons", "value": ["跟踪 📍", "签收 ✅"]}]},
            {"cells": ["🧾 复核", {"type": "combo", "value": ["已完成", "归档"]}, {"type": "switch", "value": "1"}, {"type": "select", "value": ["低 🌿", "中 🔶", "高 🔴"]}, {"type": "progress", "value": 100}, {"type": "status", "value": 1, "options": {"status": 1}}, {"type": "popover_tag", "value": "完成 🎉"}, {"type": "buttons", "value": ["详情 📄", "归档 🗃️"]}]},
        ]
        table = ui.create_table_ex(hwnd, panel, columns, rows, True, True, 28, 76, min(w - 96, 1540), 500, selection_mode=0, max_height=500, row_height=62, header_height=60)
        attach_click(table, "单元格控件")
        ui.set_table_cell_click_callback(hwnd, table, keep_callback(ui.TableCellCallback(
            lambda table_id, row, col, action, value: print(f"[Table点击] table={table_id} row={row} col={col} action={action} value={value}")
            or ui.set_element_text(hwnd, status, f"🖱️ Table #{table_id} 单元格点击：行 {row} 列 {col}")
        )))
        ui.set_table_cell_action_callback(hwnd, table, keep_callback(ui.TableCellCallback(
            lambda table_id, row, col, action, value: print(f"[Table动作] table={table_id} row={row} col={col} action={action} value={value}")
            or ui.set_element_text(hwnd, status, f"🖱️ Table #{table_id} 行 {row} 列 {col} 动作 {action} 值 {value}")
        )))
        add_text(hwnd, panel, "内置 text/index/selection/expand/button/buttons/combo/switch/select/progress/status/tag/popover_tag 都由 Table 原生绘制和命中。", 28, 592, 1120, 28, MUTED)

    def fill_tree_summary(panel):
        columns = [
            {"title": "展开", "key": "open", "type": "expand", "width": 60, "fixed": "left", "align": "center"},
            {"title": "序号", "key": "idx", "type": "index", "width": 64, "fixed": "left", "align": "center"},
            {"title": "项目", "key": "name", "width": 200},
            {"title": "说明", "key": "desc", "width": 380, "tooltip": True},
            {"title": "进度", "key": "progress", "type": "progress", "width": 260},
            {"title": "状态", "key": "status", "type": "status", "width": 110},
        ]
        rows = [
            {"key": "a", "expanded": True, "children": True, "cells": [{"type": "expand"}, {"type": "index"}, "📦 华东仓", "默认展开，下面两行是子项", {"type": "progress", "value": 82}, {"type": "status", "value": 1, "options": {"status": 1}}]},
            {"key": "a1", "parent": "a", "level": 1, "cells": [{"type": "expand"}, {"type": "index"}, "上海站", "子行：同层排序不会打乱父子结构", {"type": "progress", "value": 77}, {"type": "status", "value": 2, "options": {"status": 2}}]},
            {"key": "a2", "parent": "a", "level": 1, "cells": [{"type": "expand"}, {"type": "index"}, "杭州站", "子行：支持独立样式", {"type": "progress", "value": 91}, {"type": "status", "value": 1, "options": {"status": 1}}]},
            {"key": "b", "lazy": True, "children": True, "cells": [{"type": "expand"}, {"type": "index"}, "🚚 华南仓", "懒加载标记，点击展开会触发回调", {"type": "progress", "value": 36}, {"type": "status", "value": 0, "options": {"status": 0}}]},
            {"key": "c", "cells": [{"type": "expand"}, {"type": "index"}, "🧾 合并示例", "这一行说明列向右合并，并单独设置字体。", {"type": "progress", "value": 58}, {"type": "status", "value": 2, "options": {"status": 2}}]},
        ]
        table = ui.create_table_ex(hwnd, panel, columns, rows, True, True, 28, 76, min(w - 112, 1380), 380, tree=True, lazy=True, max_height=380, summary=["合计 🧮", "", "3 个仓", "5 行数据", "344%", ""], row_height=52, header_height=54)
        attach_click(table, "树形合计")
        ui.set_table_row_style(hwnd, table, 2, 0xFFEAF8EF, 0xFF185A2F, 0, 1, 15)
        ui.set_table_cell_style(hwnd, table, 4, 3, 0xFFEAF2FF, 0xFF1F3D64, 0, 1, 15)
        ui.set_table_span(hwnd, table, 4, 3, 1, 2)
        add_text(hwnd, panel, "展开行、树形行、懒加载标记、合计行、自定义合计、索引列和行列合并集中展示。", 28, 460, 1120, 28, MUTED)

    def fill_virtual(panel):
        columns = [
            {"title": "序号", "key": "idx", "type": "index", "width": 68, "fixed": "left", "align": "center"},
            {"title": "日期", "key": "date", "width": 140, "sortable": True},
            {"title": "姓名", "key": "name", "width": 140, "searchable": True},
            {"title": "地址", "key": "address", "width": 360, "tooltip": True},
            {"title": "标签", "key": "tag", "type": "tag", "width": 124, "align": "center"},
            {"title": "进度", "key": "progress", "type": "progress", "width": 220},
            {"title": "状态", "key": "status", "type": "status", "width": 110, "align": "center"},
            {"title": "操作", "key": "actions", "type": "buttons", "width": 180, "fixed": "right", "align": "center"},
        ]
        names = ["王小虎 🎯", "李小花 🌸", "陈小云 ☁️", "赵小星 ⭐", "周小宇 🎮", "孙小满 🍀"]

        def provider(table_id, row):
            day = 1 + (row % 28)
            progress = 24 + (row * 11 % 72)
            tag = "家 🏠" if row % 2 == 0 else "公司 🏢"
            status = row % 4
            actions = ["查看 👀", "编辑 ✏️"] if row % 3 else ["详情 📄", "归档 🗃️"]
            return (
                f"key=v{row}\t"
                f"c0={row + 1}\t"
                f"c1=2026-05-{day:02d}\t"
                f"c2={names[row % len(names)]}\t"
                f"c3=上海市普陀区金沙江路 {1516 + (row % 5)} 弄\t"
                f"c4={tag}\t"
                f"c5={progress}\t"
                f"c6={status}\t"
                f"c6_options=status={status}\t"
                f"c7={'|'.join(actions)}"
            )

        table = ui.create_table_ex(
            hwnd, panel, columns, [], True, True, 28, 76, min(w - 96, 1540), 500,
            selection_mode=1, max_height=500, row_height=54, header_height=56,
        )
        attach_click(table, "虚表")
        ui.set_table_virtual_options(hwnd, table, True, 240, 48)
        ui.set_table_virtual_row_provider(hwnd, table, provider)
        ui.set_table_selected_rows(hwnd, table, [0, 12, 24])
        ui.set_table_scroll(hwnd, table, 18, 0)
        add_text(hwnd, panel, "虚表模式：由 row provider 按行索引同步返回 UTF-8 高级行协议，支持缓存、滚动和原生单元格命中。", 28, 592, 1120, 28, MUTED)

    def fill_excel_drag(panel):
        excel_path = os.path.join(tempfile.gettempdir(), "new_emoji_table_gallery.xlsx")
        drag_state = {"column": True, "header": True}

        def apply_drag(table_id):
            ui.set_table_header_drag_options(
                hwnd, table_id,
                drag_state["column"], drag_state["header"],
                72, 360, 48, 132,
            )

        def update_header_button(button_id):
            ui.set_element_text(
                hwnd, button_id,
                f"↔️ 列宽拖拽：{'开' if drag_state['column'] else '关'}" if button_id == btn_col
                else f"↕️ 表头高度：{'开' if drag_state['header'] else '关'}"
            )

        def set_status(text):
            ui.set_element_text(hwnd, status, text)

        columns = [
            {"title": "订单号", "key": "id", "type": "index", "width": 72, "fixed": "left", "align": "center"},
            {"title": "客户", "key": "customer", "width": 130},
            {"title": "订单时间", "key": "time", "parent": "订单信息", "width": 150},
            {"title": "商品", "key": "product", "parent": "订单信息", "width": 180, "tooltip": True},
            {"title": "城市", "key": "city", "parent": "配送信息", "width": 130},
            {"title": "地址", "key": "address", "parent": "配送信息", "width": 300, "tooltip": True},
            {"title": "标签", "key": "tag", "type": "tag", "width": 120, "align": "center"},
            {"title": "金额", "key": "amount", "width": 120, "align": "right"},
            {"title": "操作", "key": "actions", "type": "buttons", "width": 180, "fixed": "right", "align": "center"},
        ]
        rows = []
        for i in range(1, 9):
            rows.append({
                "key": f"ord-{i}",
                "cells": [
                    {"type": "index"},
                    f"王小{i}号",
                    f"2026-05-{i:02d} 10:{10 + i:02d}",
                    "办公套装 📦" if i % 2 else "茶具礼盒 🍵",
                    "上海",
                    f"上海市普陀区金沙江路 {1510 + i} 弄",
                    {"type": "tag", "value": "家 🏠" if i % 2 else "公司 🏢"},
                    f"{98 + i * 12}.00",
                    {"type": "buttons", "value": ["导出 📤", "编辑 ✏️"] if i % 2 else ["导入 📥", "归档 🗃️"]},
                ],
            })

        table = ui.create_table_ex(
            hwnd, panel, columns, rows, True, True, 28, 118, min(w - 104, 1440), 430,
            selection_mode=1, max_height=430, horizontal_scroll=True, row_height=50, header_height=62,
        )
        attach_click(table, "表头拖拽 + Excel")
        apply_drag(table)

        btn_col = ui.create_button(hwnd, panel, "↔️", "列宽拖拽：开", 30, 72, 170, 34)
        btn_head = ui.create_button(hwnd, panel, "↕️", "表头高度：开", 214, 72, 170, 34)
        btn_export = ui.create_button(hwnd, panel, "📤", "导出 Excel", 398, 72, 150, 34)
        btn_import = ui.create_button(hwnd, panel, "📥", "导入 Excel", 562, 72, 150, 34)

        def sync_state():
            update_header_button(btn_col)
            update_header_button(btn_head)
            set_status(f"📗 表头拖拽：列宽{'开' if drag_state['column'] else '关'} / 高度{'开' if drag_state['header'] else '关'} ｜ 文件：{os.path.basename(excel_path)}")

        def toggle_col(_eid):
            drag_state["column"] = not drag_state["column"]
            apply_drag(table)
            sync_state()

        def toggle_head(_eid):
            drag_state["header"] = not drag_state["header"]
            apply_drag(table)
            sync_state()

        def do_export(_eid):
            ok = ui.export_table_excel(hwnd, table, excel_path)
            sync_state()
            set_status("📤 已导出 Excel：" + excel_path if ok else "📤 导出失败")

        def do_import(_eid):
            ok = ui.import_table_excel(hwnd, table, excel_path)
            apply_drag(table)
            sync_state()
            set_status("📥 已导入 Excel：" + excel_path if ok else "📥 导入失败（请先导出）")

        set_click(hwnd, btn_col, toggle_col)
        set_click(hwnd, btn_head, toggle_head)
        set_click(hwnd, btn_export, do_export)
        set_click(hwnd, btn_import, do_import)
        sync_state()
        add_text(hwnd, panel, "支持列宽拖拽、表头总高度拖拽、多行表头合并导出/导入，Excel 里能直接看到父级表头和叶子表头。", 28, 582, 1240, 28, MUTED)

    builders = [
        ("基础样式 ✨", fill_basic),
        ("固定滚动 🧭", fill_fixed),
        ("选择筛选 🔎", fill_select_filter),
        ("单元格控件 🎛️", fill_controls),
        ("树形合计 🧮", fill_tree_summary),
        ("虚表 🚀", fill_virtual),
        ("表头拖拽 + Excel 📗", fill_excel_drag),
    ]

    panel_h = min(h - 132, 760)
    for index, (title, builder) in enumerate(builders):
        panel = add_demo_panel(hwnd, stage, title, 28, 88, w - 56, panel_h)
        builder(panel)
        ui.set_element_visible(hwnd, panel, index == 0)
        groups.append(panel)

    def show_group(active_index):
        def handler(_eid):
            for i, panel in enumerate(groups):
                ui.set_element_visible(hwnd, panel, i == active_index)
            ui.set_element_text(hwnd, status, f"📊 当前分组：{builders[active_index][0]}")
        return handler

    for index, (title, _builder) in enumerate(builders):
        btn = ui.create_button(hwnd, stage, "📊", title, 34 + index * 180, 58, 160, 34)
        set_click(hwnd, btn, show_group(index))


def showcase_timeline(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "🕒 当前排序：倒序；节点、卡片和位置样式都在同一页展示。", 36, 28, w - 72, 28, MUTED)
    toolbar = add_demo_panel(hwnd, stage, "🔁 排序与基础时间线", 28, 70, w - 56, 132)

    base_items = [
        {"timestamp": "2018-04-15", "content": "🎉 活动按期开始", "type": 1, "icon": "✅"},
        {"timestamp": "2018-04-13", "content": "🧾 通过审核", "type": 0, "icon": "📌"},
        {"timestamp": "2018-04-11", "content": "🚀 创建成功", "type": 0, "icon": "🚀"},
    ]
    base_timeline = ui.create_timeline(hwnd, toolbar, base_items, 34, 58, min(560, w - 540), 64)
    ui.set_timeline_advanced_options(hwnd, base_timeline, position=0, show_time=True, reverse=True, default_placement="top")

    def set_reverse(value):
        def handler(_eid):
            ui.set_timeline_advanced_options(hwnd, base_timeline, position=0, show_time=True, reverse=value, default_placement="top")
            ui.set_element_text(hwnd, status, "🕒 当前排序：倒序；最新事项在上方。" if value else "🕒 当前排序：正序；创建事项在上方。")
        return handler

    forward_btn = ui.create_button(hwnd, toolbar, "⬆️", "正序", 650, 66, 118, 38)
    reverse_btn = ui.create_button(hwnd, toolbar, "⬇️", "倒序", 788, 66, 118, 38)
    set_click(hwnd, forward_btn, set_reverse(False))
    set_click(hwnd, reverse_btn, set_reverse(True))
    add_text(hwnd, toolbar, "左侧为同一个 Timeline；按钮只切换 reverse，不重排原始数据。", 934, 72, max(260, w - 1020), 34, MUTED)

    left_w = min(640, max(560, (w - 84) // 2))
    right_x = left_w + 56
    right_w = max(520, w - right_x - 28)
    node_panel = add_demo_panel(hwnd, stage, "🎨 节点图标、颜色与尺寸", 28, 222, left_w, 238)
    card_panel = add_demo_panel(hwnd, stage, "🪪 顶部时间戳卡片", right_x, 222, right_w, 238)

    node_items = [
        {"timestamp": "2018-04-12 20:46", "content": "✨ 支持使用图标", "type": 0, "size": "large", "icon": "el-icon-more"},
        {"timestamp": "2018-04-03 20:46", "content": "🟢 支持自定义颜色", "color": "#0bbd87"},
        {"timestamp": "2018-04-03 20:46", "content": "📏 支持自定义尺寸", "size": "large", "type": 2},
        {"timestamp": "2018-04-03 20:46", "content": "⚪ 默认样式的节点", "type": 0},
    ]
    node_timeline = ui.create_timeline(hwnd, node_panel, node_items, 34, 60, left_w - 68, 156)
    ui.set_timeline_advanced_options(hwnd, node_timeline, position=0, show_time=True, reverse=False, default_placement="bottom")

    card_items = [
        {"timestamp": "2018/4/12", "content": "更新模板", "type": 0, "icon": "🧩", "placement": "top",
         "card_title": "更新项目模板 🧩", "card_body": "王小虎 提交于 2018/4/12 20:46"},
        {"timestamp": "2018/4/3", "content": "同步文档", "type": 1, "icon": "📚", "placement": "top",
         "card_title": "同步组件文档 📚", "card_body": "王小虎 提交于 2018/4/3 20:46"},
    ]
    card_timeline = ui.create_timeline(hwnd, card_panel, card_items, 34, 60, right_w - 68, 156)
    ui.set_timeline_advanced_options(hwnd, card_timeline, position=0, show_time=True, reverse=False, default_placement="top")

    position_panel = add_demo_panel(hwnd, stage, "🧭 左侧、右侧与交替布局", 28, 488, w - 56, 250)
    compact_items = [
        {"timestamp": "09:00", "content": "🚀 创建任务", "type": 0, "icon": "🚀"},
        {"timestamp": "10:30", "content": "✅ 完成复核", "type": 1, "icon": "✅"},
        {"timestamp": "14:20", "content": "📦 发布版本", "type": 2, "icon": "📦"},
    ]
    col_w = max(300, (w - 134) // 3)
    left_tl = ui.create_timeline(hwnd, position_panel, compact_items, 34, 62, col_w, 152)
    right_tl = ui.create_timeline(hwnd, position_panel, compact_items, 64 + col_w, 62, col_w, 152)
    alt_tl = ui.create_timeline(hwnd, position_panel, compact_items, 94 + col_w * 2, 62, col_w, 152)
    ui.set_timeline_advanced_options(hwnd, left_tl, position=0, show_time=True, reverse=False, default_placement="top")
    ui.set_timeline_advanced_options(hwnd, right_tl, position=1, show_time=True, reverse=False, default_placement="top")
    ui.set_timeline_advanced_options(hwnd, alt_tl, position=2, show_time=True, reverse=False, default_placement="top")
    add_text(hwnd, position_panel, "左侧", 34, 214, 100, 24, MUTED)
    add_text(hwnd, position_panel, "右侧", 64 + col_w, 214, 100, 24, MUTED)
    add_text(hwnd, position_panel, "交替", 94 + col_w * 2, 214, 100, 24, MUTED)


def showcase_upload(hwnd, stage, w, h):
    img1, img2, img3, doc = upload_sample_files()

    top = add_demo_panel(hwnd, stage, "📤 普通列表、多选和手动上传", 28, 30, w - 56, 250)
    normal = ui.create_upload(hwnd, top, "📤 选择文件", "支持单选/多选、数量限制和类型过滤", [img1, doc], 30, 66, 500, 150)
    ui.set_upload_style(hwnd, normal, 0, True, True, True, False)
    ui.set_upload_options(hwnd, normal, multiple=True, auto_upload=False)
    ui.set_upload_constraints(hwnd, normal, limit=3, max_size_kb=500, accept=".png,.txt")

    manual = ui.create_upload(hwnd, top, "📤 手动上传", "先选择文件，再上传到服务器", [img1, img2], 560, 66, 520, 150)
    ui.set_upload_style(hwnd, manual, 6, True, True, True, False)
    ui.set_upload_options(hwnd, manual, multiple=True, auto_upload=False)
    ui.set_upload_texts(hwnd, manual, "📤 手动上传", "文件会等待宿主程序处理", "选取文件", "🚀 上传到服务器")
    ui.set_upload_file_items(hwnd, manual, [
        ("封面图片.png", 0, 0, img1, img1, 0),
        ("头像素材.png", 3, 45, img2, img2, 0),
    ])

    media = add_demo_panel(hwnd, stage, "🖼️ 头像、图片列表和图片卡片", 28, 310, w - 56, 330)
    avatar = ui.create_upload(hwnd, media, "😀 上传头像", "只显示一个头像入口", [img2], 30, 70, 190, 210)
    ui.set_upload_style(hwnd, avatar, 1, False, False, True, False)
    ui.set_upload_options(hwnd, avatar, multiple=False, auto_upload=False)
    ui.set_upload_constraints(hwnd, avatar, limit=1, max_size_kb=2048, accept="image/*")

    picture = ui.create_upload(hwnd, media, "🖼️ 图片列表", "缩略图 + 文件状态", [img1, img2], 250, 70, 370, 210)
    ui.set_upload_style(hwnd, picture, 4, True, True, True, False)
    ui.set_upload_constraints(hwnd, picture, limit=4, max_size_kb=2048, accept=".png,.jpg")

    cards = ui.create_upload(hwnd, media, "🧩 图片卡片", "预览 / 下载 / 删除动作", [img1, img2, img3], 650, 70, 460, 210)
    ui.set_upload_style(hwnd, cards, 3, True, True, True, False)
    ui.set_upload_constraints(hwnd, cards, limit=6, max_size_kb=2048, accept="image/*")

    drag = add_demo_panel(hwnd, stage, "🧲 系统拖拽上传", 28, 670, w - 56, 270)
    drop = ui.create_upload(hwnd, drag, "🧲 将文件拖到此处，或点击选择", "支持从资源管理器拖入；这里只接收 PNG 图片，最多 3 个", [img1], 30, 66, 660, 160)
    ui.set_upload_style(hwnd, drop, 5, True, True, True, True)
    ui.set_upload_options(hwnd, drop, multiple=True, auto_upload=False)
    ui.set_upload_constraints(hwnd, drop, limit=3, max_size_kb=2048, accept=".png")
    add_text(hwnd, drag, "✅ 点击会打开系统文件选择框\n✅ 多选由上传选项控制\n✅ 文件类型过滤会同时作用于对话框、API 写入和系统拖入", 730, 78, 520, 116, TEXT)


def showcase_image(hwnd, stage, w, h):
    wide, tall, small = image_sample_files()
    missing = os.path.join(tempfile.gettempdir(), "new_emoji_gallery_missing_image.bmp")
    remote = "https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg"

    fit_panel = add_demo_panel(hwnd, stage, "🧩 五种适配方式", 28, 30, w - 56, 220)
    fit_specs = [
        ("fill", "拉伸填满"),
        ("contain", "完整包含"),
        ("cover", "覆盖裁切"),
        ("none", "原图居中"),
        ("scale-down", "按需缩小"),
    ]
    for index, (fit, label) in enumerate(fit_specs):
        x = 26 + index * 214
        add_text(hwnd, fit_panel, f"🖼️ {label}", x, 48, 170, 24, MUTED)
        ui.create_image(hwnd, fit_panel, wide, f"🖼️ {label}", fit, x, 78, 176, 118)

    state_panel = add_demo_panel(hwnd, stage, "⏳ 占位与失败状态", 28, 278, w - 56, 220)
    ui.create_image(hwnd, state_panel, "", "🕒 默认占位", "contain", 28, 64, 210, 130)
    custom_placeholder = ui.create_image(hwnd, state_panel, "", "🎨 自定义占位", "contain", 268, 64, 210, 130)
    ui.set_image_placeholder(hwnd, custom_placeholder, "⏳", "正在生成缩略图", 0xFF409EFF, 0xFFEAF4FF)
    ui.create_image(hwnd, state_panel, missing, "⚠️ 默认失败", "contain", 508, 64, 210, 130)
    custom_error = ui.create_image(hwnd, state_panel, missing, "🧯 自定义失败", "contain", 748, 64, 210, 130)
    ui.set_image_error_content(hwnd, custom_error, "🧯", "图片读取失败", 0xFFF56C6C, 0xFFFFF0F0)

    source_panel = add_demo_panel(hwnd, stage, "🌐 本地、远程与懒加载", 28, 526, w - 56, 220)
    ui.create_image(hwnd, source_panel, tall, "📁 本地竖图", "contain", 28, 64, 190, 130)
    remote_image = ui.create_image(hwnd, source_panel, remote, "🌐 HTTPS 远程图", "cover", 248, 64, 230, 130)
    ui.set_image_placeholder(hwnd, remote_image, "🌐", "远程图片加载中", 0xFF409EFF, 0)
    for i, (path, label) in enumerate([(wide, "懒加载一"), (tall, "懒加载二"), (small, "懒加载三")]):
        item = ui.create_image(hwnd, source_panel, path, f"🛗 {label}", "scale-down",
                               520 + i * 156, 64, 136, 130)
        ui.set_image_lazy(hwnd, item, True)

    preview_panel = add_demo_panel(hwnd, stage, "🔍 预览列表、切换、缩放和关闭", 28, 774, w - 56, 310)
    preview_image = ui.create_image(hwnd, preview_panel, wide, "🔍 预览列表示例", "contain", 28, 64, 260, 190)
    ui.set_image_preview_list(hwnd, preview_image, [wide, tall, remote], selected_index=0)
    ui.set_image_preview_enabled(hwnd, preview_image, True)
    status = add_text(hwnd, preview_panel, "🔍 当前预览：第 1 张 / 3 张", 330, 64, 520, 28, MUTED)

    def refresh_status():
        state = ui.get_image_advanced_options(hwnd, preview_image) or {}
        ui.set_element_text(hwnd, status, f"🔍 当前预览：第 {state.get('preview_index', 0) + 1} 张 / {state.get('preview_count', 0)} 张 · 缩放 {state.get('scale_percent', 100)}%")

    def open_preview(_eid):
        ui.set_image_preview(hwnd, preview_image, True)
        refresh_status()

    def prev_preview(_eid):
        state = ui.get_image_advanced_options(hwnd, preview_image) or {}
        count = max(1, state.get("preview_count", 1))
        ui.set_image_preview_index(hwnd, preview_image, (state.get("preview_index", 0) - 1) % count)
        ui.set_image_preview(hwnd, preview_image, True)
        refresh_status()

    def next_preview(_eid):
        state = ui.get_image_advanced_options(hwnd, preview_image) or {}
        count = max(1, state.get("preview_count", 1))
        ui.set_image_preview_index(hwnd, preview_image, (state.get("preview_index", 0) + 1) % count)
        ui.set_image_preview(hwnd, preview_image, True)
        refresh_status()

    def zoom_preview(_eid):
        state = ui.get_image_advanced_options(hwnd, preview_image) or {}
        ui.set_image_preview_transform(hwnd, preview_image, min(220, state.get("scale_percent", 100) + 30), 18, -12)
        ui.set_image_preview(hwnd, preview_image, True)
        refresh_status()

    def close_preview(_eid):
        ui.set_image_preview(hwnd, preview_image, False)
        refresh_status()

    actions = [
        ("🔍", "打开预览", open_preview),
        ("⬅️", "上一张", prev_preview),
        ("➡️", "下一张", next_preview),
        ("➕", "放大", zoom_preview),
        ("✅", "关闭", close_preview),
    ]
    for index, (emoji, label, handler) in enumerate(actions):
        btn = ui.create_button(hwnd, preview_panel, emoji, label, 330 + index * 132, 110, 116, 38)
        set_click(hwnd, btn, handler)
    ui.create_descriptions(
        hwnd, preview_panel, "🧭 图片状态",
        [
            ("适配", "fill / contain / cover / none / scale-down"),
            ("占位", "默认文案 + 自定义 emoji / 文本 / 颜色"),
            ("来源", "本地文件 + HTTPS 远程异步加载"),
            ("预览", "列表索引、左右切换、缩放、Esc 关闭"),
        ],
        2, True, 330, 166, 760, 112,
    )
    refresh_status()


def showcase_avatar(hwnd, stage, w, h):
    wide, tall, small = image_sample_files()
    missing = os.path.join(tempfile.gettempdir(), "new_emoji_gallery_missing_avatar.bmp")
    remote = "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"

    size_panel = add_demo_panel(hwnd, stage, "😀 基础形状与尺寸", 28, 30, w - 56, 220)
    size_specs = [
        ("圆形 50", 0, 50, "圆"),
        ("圆形 large", 0, 64, "大"),
        ("圆形 medium", 0, 48, "中"),
        ("圆形 small", 0, 36, "小"),
        ("方形 50", 1, 50, "方"),
        ("方形 large", 1, 64, "大"),
        ("方形 medium", 1, 48, "中"),
        ("方形 small", 1, 36, "小"),
    ]
    for index, (label, shape, size, text) in enumerate(size_specs):
        x = 28 + index * 138
        ui.create_avatar(hwnd, size_panel, text, shape, x + 28, 68, size, size)
        add_text(hwnd, size_panel, label, x, 146, 120, 24, MUTED)

    type_panel = add_demo_panel(hwnd, stage, "👤 内容类型：图标、图片、文字与 emoji", 28, 278, w - 56, 220)
    type_specs = [
        ("用户图标", {"icon": "👤", "text": "", "shape": 0}),
        ("本地图片", {"source": wide, "text": "", "shape": 0, "fit": "cover"}),
        ("远程图片", {"source": remote, "text": "", "shape": 0, "fit": "cover", "icon": "🌐"}),
        ("中文文字", {"text": "小易", "shape": 0}),
        ("emoji 内容", {"text": "🚀", "shape": 1}),
    ]
    for index, (label, options) in enumerate(type_specs):
        x = 36 + index * 210
        ui.create_avatar(
            hwnd, type_panel,
            options.get("text", ""),
            options.get("shape", 0),
            x, 70, 78, 78,
            source=options.get("source", ""),
            fit=options.get("fit", "contain"),
            icon=options.get("icon", ""),
        )
        add_text(hwnd, type_panel, f"✨ {label}", x - 14, 160, 136, 26, MUTED)

    fallback_panel = add_demo_panel(hwnd, stage, "🛟 加载失败与回退", 28, 526, w - 56, 220)
    ui.create_avatar(
        hwnd, fallback_panel, "", 0, 42, 72, 82, 82,
        source=missing, icon="👤", error_text="!"
    )
    add_text(hwnd, fallback_panel, "失败后显示错误文本", 20, 164, 160, 26, MUTED)
    ui.create_avatar(
        hwnd, fallback_panel, "", 0, 246, 72, 82, 82,
        source=missing, fallback_source=small, fit="scale-down", icon="🛟"
    )
    add_text(hwnd, fallback_panel, "失败后显示备用图片", 218, 164, 170, 26, MUTED)
    ui.create_avatar(
        hwnd, fallback_panel, "访客", 1, 450, 72, 82, 82,
        source=missing, error_text="离线"
    )
    add_text(hwnd, fallback_panel, "失败后显示中文占位", 420, 164, 180, 26, MUTED)
    ui.create_avatar(
        hwnd, fallback_panel, "", 0, 654, 72, 82, 82,
        icon="🧑‍💼"
    )
    add_text(hwnd, fallback_panel, "无图片时显示图标", 628, 164, 160, 26, MUTED)

    fit_panel = add_demo_panel(hwnd, stage, "🖼️ 图片适配方式", 28, 774, w - 56, 270)
    fit_specs = [
        ("fill", "拉伸填满"),
        ("contain", "完整包含"),
        ("cover", "覆盖裁切"),
        ("none", "原图居中"),
        ("scale-down", "按需缩小"),
    ]
    for index, (fit, label) in enumerate(fit_specs):
        x = 34 + index * 216
        ui.create_avatar(hwnd, fit_panel, "", 1, x + 28, 72, 100, 100, source=tall, fit=fit)
        add_text(hwnd, fit_panel, f"🖼️ {label}", x, 184, 170, 26, MUTED)
        add_text(hwnd, fit_panel, fit, x, 214, 170, 24, MUTED)


def showcase_alert(hwnd, stage, w, h):
    type_names = {0: "信息", 1: "成功", 2: "警告", 3: "错误"}
    action_names = {0: "无", 1: "设置", 2: "鼠标", 3: "键盘", 4: "程序"}
    tracked = {"target": 0, "type": 1, "effect": 0, "show_icon": True, "center": False}

    status_id = add_text(hwnd, stage, "🚨 Alert 警告提示：展示页面内重要信息，支持中文与 emoji。", 36, 28, w - 72, 28, MUTED)

    basic = add_demo_panel(hwnd, stage, "🌈 基础类型：浅色 success / info / warning / error", 28, 70, 820, 294)
    basic_specs = [
        ("✅ 成功提示的文案", 1),
        ("ℹ️ 消息提示的文案", 0),
        ("⚠️ 警告提示的文案", 2),
        ("❌ 错误提示的文案", 3),
    ]
    for i, (title, alert_type) in enumerate(basic_specs):
        ui.create_alert_ex(
            hwnd, basic, title, "", alert_type, 0, True,
            True, False, False, "", 24, 58 + i * 54, 748, 42,
        )

    dark = add_demo_panel(hwnd, stage, "🌙 深色效果：effect=dark", 878, 70, w - 906, 294)
    for i, (title, alert_type) in enumerate(basic_specs):
        ui.create_alert_ex(
            hwnd, dark, title.replace("文案", "深色文案"), "", alert_type, 1, True,
            True, False, False, "", 24, 58 + i * 54, w - 970, 42,
        )

    close_panel = add_demo_panel(hwnd, stage, "🧯 关闭能力：不可关闭、自定义文字与关闭回调", 28, 392, 820, 250)
    no_close = ui.create_alert_ex(
        hwnd, close_panel, "✅ 不可关闭的 alert", "", 1, 0, False,
        True, False, False, "", 24, 58, 748, 44,
    )
    custom_close = ui.create_alert_ex(
        hwnd, close_panel, "ℹ️ 自定义 close-text", "右侧关闭区域显示「知道了」。", 0, 0, True,
        True, False, False, "知道了", 24, 116, 748, 58,
    )
    callback_id = ui.create_alert_ex(
        hwnd, close_panel, "⚠️ 设置了回调的 alert", "关闭后会在右侧状态区显示来源和次数。", 2, 0, True,
        True, False, False, "", 24, 188, 748, 58,
    )

    advanced = add_demo_panel(hwnd, stage, "🎯 图标与居中：show-icon / hide-icon / center", 878, 392, w - 906, 250)
    ui.create_alert_ex(hwnd, advanced, "✅ 带图标的成功提示", "", 1, 0, True, True, False, False, "", 24, 58, w - 970, 42)
    ui.create_alert_ex(hwnd, advanced, "ℹ️ 隐藏图标的信息提示", "", 0, 0, True, False, False, False, "", 24, 112, w - 970, 42)
    ui.create_alert_ex(hwnd, advanced, "⚠️ 居中且带图标的警告提示", "", 2, 0, True, True, True, False, "", 24, 166, w - 970, 42)

    desc_panel = add_demo_panel(hwnd, stage, "📝 辅助说明：短描述、长中文换行、多类型描述", 28, 670, 1080, 344)
    long_desc = "这是一句绕口令：黑灰化肥会挥发发灰黑化肥挥发；灰黑化肥会挥发发黑灰化肥发挥。黑灰化肥会挥发发灰黑化肥黑灰挥发化为灰。"
    ui.create_alert_ex(
        hwnd, desc_panel, "✅ 带辅助性文字介绍", long_desc, 1, 0, True,
        True, False, True, "", 24, 58, 1018, 88,
    )
    desc_specs = [
        ("✅ 成功提示的文案", "文字说明文字说明文字说明文字说明文字说明文字说明", 1),
        ("ℹ️ 消息提示的文案", "文字说明文字说明文字说明文字说明文字说明文字说明", 0),
        ("⚠️ 警告提示的文案", "文字说明文字说明文字说明文字说明文字说明文字说明", 2),
        ("❌ 错误提示的文案", "文字说明文字说明文字说明文字说明文字说明文字说明", 3),
    ]
    for i, (title, desc, alert_type) in enumerate(desc_specs):
        ui.create_alert_ex(
            hwnd, desc_panel, title, desc, alert_type, 0, True,
            True, False, True, "", 24 + (i % 2) * 510, 166 + (i // 2) * 76, 488, 60,
        )

    control = add_demo_panel(hwnd, stage, "🎛️ 交互与读回：动态切换样式、程序关闭和重新显示", 1138, 670, w - 1166, 344)
    state_id = add_text(hwnd, control, "📋 状态读回：等待操作。", 24, 56, w - 1214, 116, TEXT)
    target = ui.create_alert_ex(
        hwnd, control, "✅ 可交互目标", "按钮会修改这条 Alert 的类型、深浅、图标、居中和关闭文字。", 1, 0, True,
        True, False, True, "", 24, 186, w - 1214, 76,
    )
    tracked["target"] = target

    @ui.ValueCallback
    def on_alert_close(element_id, close_count, alert_type, action):
        ui.set_element_text(hwnd, status_id, f"🧯 关闭回调：#{element_id} · {type_names.get(alert_type, '信息')} · {action_names.get(action, '未知')} · 第 {close_count} 次")

    keep_callback(on_alert_close)
    for aid in (custom_close, callback_id, target):
        ui.set_alert_close_callback(hwnd, aid, on_alert_close)

    def refresh_state(label):
        state = ui.get_alert_full_state(hwnd, target) or {}
        advanced_state = ui.get_alert_advanced_options(hwnd, target) or (False, False, False)
        title = ui.get_alert_text(hwnd, target, 0)
        desc = ui.get_alert_text(hwnd, target, 1)
        close_text = ui.get_alert_text(hwnd, target, 2) or "X"
        ui.set_element_text(
            hwnd,
            state_id,
            f"📋 {label}\n类型={type_names.get(state.get('alert_type', 0), '信息')} · effect={'dark' if state.get('effect') else 'light'} · "
            f"图标={advanced_state[0]} · 居中={advanced_state[1]} · 换行={advanced_state[2]}\n"
            f"关闭={state.get('closed', 0)} · hover={state.get('close_hover', 0)} · down={state.get('close_down', 0)} · "
            f"次数={state.get('close_count', 0)} · 来源={action_names.get(state.get('last_action', 0), '无')}\n"
            f"标题：{title}\n描述：{desc}\n关闭文字：{close_text}",
        )

    def cycle_type(_eid):
        tracked["type"] = (tracked["type"] + 1) % 4
        ui.set_alert_type(hwnd, target, tracked["type"])
        ui.set_element_text(hwnd, target, f"{['ℹ️', '✅', '⚠️', '❌'][tracked['type']]} 已切换为{type_names[tracked['type']]}")
        refresh_state("已切换类型")

    def toggle_dark(_eid):
        tracked["effect"] = 0 if tracked["effect"] else 1
        ui.set_alert_effect(hwnd, target, tracked["effect"])
        refresh_state("已切换深浅效果")

    def toggle_icon(_eid):
        tracked["show_icon"] = not tracked["show_icon"]
        ui.set_alert_advanced_options(hwnd, target, tracked["show_icon"], tracked["center"], True)
        refresh_state("已切换图标显示")

    def toggle_center(_eid):
        tracked["center"] = not tracked["center"]
        ui.set_alert_advanced_options(hwnd, target, tracked["show_icon"], tracked["center"], True)
        refresh_state("已切换居中")

    def set_close_text(_eid):
        current = ui.get_alert_text(hwnd, target, 2)
        ui.set_alert_close_text(hwnd, target, "" if current else "知道了")
        refresh_state("已切换关闭文字")

    def close_target(_eid):
        ui.trigger_alert_close(hwnd, target)
        refresh_state("程序触发关闭")

    def reopen_target(_eid):
        ui.set_alert_closed(hwnd, target, False)
        refresh_state("重新显示")

    buttons = [
        ("🔄", "切换类型", cycle_type),
        ("🌙", "深浅效果", toggle_dark),
        ("👁️", "显示图标", toggle_icon),
        ("🎯", "居中", toggle_center),
        ("📝", "关闭文字", set_close_text),
        ("🧯", "程序关闭", close_target),
        ("🔁", "重新显示", reopen_target),
    ]
    for i, (emoji, label, handler) in enumerate(buttons):
        btn = ui.create_button(hwnd, control, emoji, label, 24 + (i % 4) * 124, 278 + (i // 4) * 42, 112, 34)
        set_click(hwnd, btn, handler)
    refresh_state("初始状态")


def showcase_message(hwnd, stage, w, h):
    last_message = {"id": 0}
    status_id = add_text(hwnd, stage, "💬 最近消息：点击任一按钮开始演示", 44, 28, w - 88, 26, MUTED)

    @ui.ValueCallback
    def on_message_close(element_id, close_count, message_type, action):
        action_text = {
            2: "手动点击关闭",
            3: "键盘关闭",
            4: "程序触发关闭",
            5: "到时自动关闭",
        }.get(action, "状态更新")
        type_text = {0: "信息", 1: "成功", 2: "警告", 3: "错误"}.get(message_type, "消息")
        ui.set_element_text(hwnd, status_id, f"💬 最近关闭：#{element_id} · {type_text} · {action_text} · 第 {close_count} 次")

    close_cb = keep_callback(on_message_close)

    def remember(message_id):
        if message_id > 0:
            last_message["id"] = message_id
            ui.set_message_close_callback(hwnd, message_id, close_cb)
        return message_id

    def show_info(_eid):
        mid = ui.message_info(hwnd, "ℹ️ 信息提示：手动关闭，持续时间=0", closable=True, duration_ms=0, offset=34)
        remember(mid)
        ui.set_element_text(hwnd, status_id, "ℹ️ 已显示信息提示：不自动关闭，可点右侧关闭")

    def show_success(_eid):
        mid = ui.message_success(hwnd, "✅ 成功提示：2 秒后自动关闭", duration_ms=2000, offset=34)
        remember(mid)
        ui.set_element_text(hwnd, status_id, "✅ 已显示成功提示：2 秒后自动关闭")

    def show_warning(_eid):
        mid = ui.message_warning(hwnd, "⚠️ 居中警告：3 秒后自动关闭", center=True, duration_ms=3000, offset=34)
        remember(mid)
        ui.set_element_text(hwnd, status_id, "⚠️ 已显示居中警告：文本居中，3 秒后自动关闭")

    def show_error(_eid):
        mid = ui.message_error(
            hwnd,
            "❌ 富文本错误：<span style=\"color: teal\"><strong>VNode</strong></span> 高亮",
            rich=True,
            closable=True,
            duration_ms=0,
            offset=34,
        )
        remember(mid)
        ui.set_element_text(hwnd, status_id, "❌ 已显示富文本错误：手动关闭")

    def show_stack(_eid):
        ids = [
            ui.message_info(hwnd, "ℹ️ 堆叠 1：信息提示，4 秒自动关闭", duration_ms=4000, offset=34),
            ui.message_success(hwnd, "✅ 堆叠 2：成功提示，3 秒自动关闭", duration_ms=3000, offset=34),
            ui.message_warning(hwnd, "⚠️ 堆叠 3：警告提示，居中文本", center=True, duration_ms=3500, offset=34),
            ui.message_error(hwnd, "❌ 堆叠 4：可关闭错误提示", closable=True, duration_ms=0, offset=34),
        ]
        for mid in ids:
            remember(mid)
        ui.set_element_text(hwnd, status_id, "📚 已演示多条消息堆叠：每条都有独立类型和关闭策略")

    def close_last(_eid):
        mid = last_message.get("id", 0)
        if mid > 0:
            ui.trigger_message_close(hwnd, mid)
            ui.set_element_text(hwnd, status_id, f"🧹 已请求程序关闭最近消息：#{mid}")
        else:
            ui.set_element_text(hwnd, status_id, "🧹 还没有可关闭的消息")

    type_panel = add_demo_panel(hwnd, stage, "🎨 四种类型与文本能力", 28, 68, w - 56, 210)
    type_specs = [
        ("ℹ️", "信息·手动关", show_info),
        ("✅", "成功·2秒", show_success),
        ("⚠️", "警告·居中3秒", show_warning),
        ("❌", "错误·富文本", show_error),
    ]
    for i, (emoji, label, handler) in enumerate(type_specs):
        btn = ui.create_button(hwnd, type_panel, emoji, label, 28 + i * 172, 70, 150, 36)
        set_click(hwnd, btn, handler)
    add_text(hwnd, type_panel, "每个按钮只触发一种消息，分别覆盖信息、成功、警告、错误、居中、富文本和可关闭。", 28, 128, w - 112, 28, MUTED)

    duration_panel = add_demo_panel(hwnd, stage, "⏱ 自动关闭时间", 28, 310, w - 56, 190)
    quick = ui.create_button(hwnd, duration_panel, "⚡", "1 秒自动关", 28, 70, 142, 36)
    normal = ui.create_button(hwnd, duration_panel, "⏱️", "5 秒自动关", 188, 70, 142, 36)
    persist = ui.create_button(hwnd, duration_panel, "📌", "不自动关闭", 348, 70, 142, 36)
    set_click(hwnd, quick, lambda _eid: remember(ui.message_success(hwnd, "⚡ 1 秒自动关闭的成功消息", duration_ms=1000, offset=34)))
    set_click(hwnd, normal, lambda _eid: remember(ui.message_info(hwnd, "⏱️ 5 秒自动关闭的信息消息", duration_ms=5000, offset=34)))
    set_click(hwnd, persist, lambda _eid: remember(ui.message_warning(hwnd, "📌 持续时间=0，不自动关闭", closable=True, duration_ms=0, offset=34)))
    add_text(hwnd, duration_panel, "关闭回调会在上方状态行显示“到时自动关闭 / 手动点击关闭 / 程序触发关闭”。", 28, 126, w - 112, 28, MUTED)

    stack_panel = add_demo_panel(hwnd, stage, "📚 堆叠与程序关闭", 28, 532, w - 56, 190)
    stack_btn = ui.create_button(hwnd, stack_panel, "📚", "一键堆叠四类", 28, 70, 150, 36)
    close_btn = ui.create_button(hwnd, stack_panel, "🧹", "关闭最近消息", 196, 70, 150, 36)
    set_click(hwnd, stack_btn, show_stack)
    set_click(hwnd, close_btn, close_last)
    add_text(hwnd, stack_panel, "堆叠按钮专门用于验证多条消息同时出现；普通类型按钮不会再一次弹出四条消息。", 28, 126, w - 112, 28, MUTED)


def showcase_messagebox(hwnd, stage, w, h):
    status_id = add_text(hwnd, stage, "🪟 最近消息框：点击任一按钮开始演示", 44, 28, w - 88, 26, MUTED)
    email_pattern = r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?"

    @ui.MessageBoxExCallback
    def on_box_result(messagebox_id, action, value_ptr, value_len):
        action_text = {1: "确认", 0: "取消", -1: "关闭"}.get(action, "状态")
        value = ""
        if value_ptr and value_len > 0:
            value = ctypes.string_at(value_ptr, value_len).decode("utf-8", errors="replace")
        suffix = f" · 输入：{value}" if value else ""
        ui.set_element_text(hwnd, status_id, f"🪟 最近结果：#{messagebox_id} · {action_text}{suffix}")

    box_cb = keep_callback(on_box_result)

    def set_opened(label):
        ui.set_element_text(hwnd, status_id, f"🪟 已打开：{label}")

    def add_show_button(parent, emoji, label, x, y, bw, handler):
        btn = ui.create_button(hwnd, parent, emoji, label, x, y, bw, 36)
        set_click(hwnd, btn, handler)
        return btn

    def open_alert(_eid):
        ui.show_alert_box(
            hwnd,
            "📌 提示消息",
            "用于只告知结果的单确认消息框。",
            confirm="知道了 ✅",
            callback=box_cb,
        )
        set_opened("提示消息 · 单确认按钮")

    def open_confirm(_eid):
        ui.show_confirm_box(
            hwnd,
            "⚠️ 确认操作",
            "检测到未保存内容，是否立即保存修改？",
            confirm="保存 ✅",
            cancel="放弃修改",
            box_type=2,
            distinguish_cancel_and_close=True,
            callback=box_cb,
        )
        set_opened("确认操作 · 确认/取消/关闭")

    def open_prompt(_eid):
        ui.show_prompt_box(
            hwnd,
            "📧 输入邮箱",
            "请输入邮箱地址",
            placeholder="name@example.com",
            pattern=email_pattern,
            error="邮箱格式不正确",
            confirm="提交 ✅",
            cancel="取消",
            callback=box_cb,
        )
        set_opened("输入消息框 · 占位文字与校验")

    def open_msgbox(_eid):
        ui.show_msgbox(
            hwnd,
            "🚀 通用消息",
            "通用消息框可以自定义按钮、类型、居中和富文本。",
            confirm="执行 ✅",
            cancel="取消",
            show_cancel=True,
            callback=box_cb,
        )
        set_opened("通用消息框 · 自定义按钮")

    flow_panel = add_demo_panel(hwnd, stage, "⭐ 标准演示：四种入口", 28, 68, w - 56, 210)
    add_show_button(flow_panel, "📌", "提示框", 28, 70, 142, open_alert)
    add_show_button(flow_panel, "⚠️", "确认框", 196, 70, 142, open_confirm)
    add_show_button(flow_panel, "📧", "输入框", 364, 70, 142, open_prompt)
    add_show_button(flow_panel, "🚀", "通用框", 532, 70, 142, open_msgbox)
    add_text(hwnd, flow_panel, "分别覆盖提示、确认、输入、通用四种消息框入口；每个按钮只打开对应的一种消息框。", 28, 128, w - 112, 28, MUTED)

    def open_plain_type(_eid):
        ui.show_msgbox(
            hwnd,
            "ℹ️ 普通信息",
            "普通信息样式适合轻量说明，默认不显示类型图标。",
            confirm="明白了",
            show_cancel=False,
            callback=box_cb,
        )
        set_opened("普通信息样式")

    def open_success_type(_eid):
        ui.show_msgbox(
            hwnd,
            "✅ 成功状态",
            "操作已经完成，用户只需要确认即可。",
            confirm="完成 ✅",
            box_type=1,
            show_cancel=False,
            callback=box_cb,
        )
        set_opened("成功类型图标")

    def open_warning_type(_eid):
        ui.show_msgbox(
            hwnd,
            "⚠️ 风险提醒",
            "继续操作可能覆盖当前配置，请确认后再执行。",
            confirm="继续",
            cancel="返回",
            box_type=2,
            show_cancel=True,
            callback=box_cb,
        )
        set_opened("警告类型图标")

    def open_error_type(_eid):
        ui.show_msgbox(
            hwnd,
            "❌ 处理失败",
            "保存失败，请检查网络后重试。",
            confirm="重试",
            cancel="稍后处理",
            box_type=3,
            show_cancel=True,
            callback=box_cb,
        )
        set_opened("错误类型图标")

    type_panel = add_demo_panel(hwnd, stage, "🎨 类型图标样式", 28, 310, w - 56, 210)
    add_show_button(type_panel, "ℹ️", "普通信息", 28, 70, 142, open_plain_type)
    add_show_button(type_panel, "✅", "成功", 196, 70, 142, open_success_type)
    add_show_button(type_panel, "⚠️", "警告", 364, 70, 142, open_warning_type)
    add_show_button(type_panel, "❌", "错误", 532, 70, 142, open_error_type)
    add_text(hwnd, type_panel, "覆盖普通、成功、警告、错误四类视觉状态，并展示单按钮与双按钮组合。", 28, 128, w - 112, 28, MUTED)

    def open_centered(_eid):
        ui.show_msgbox(
            hwnd,
            "🎯 居中展示",
            "标题与正文居中，适合短句确认和结果反馈。",
            confirm="好的",
            box_type=1,
            show_cancel=False,
            center=True,
            callback=box_cb,
        )
        set_opened("居中展示")

    def open_rich(_eid):
        ui.show_msgbox(
            hwnd,
            "🎨 富文本片段",
            "正文支持 <strong>加粗</strong>、<i>斜体</i> 与 <span style=\"color: teal\">彩色文字</span>。",
            confirm="查看完成",
            cancel="关闭",
            box_type=0,
            show_cancel=True,
            rich=True,
            callback=box_cb,
        )
        set_opened("富文本片段")

    def open_distinguish(_eid):
        ui.show_confirm_box(
            hwnd,
            "🧭 区分关闭来源",
            "点击取消返回 0，点击右上角关闭或按 Esc 返回 -1。",
            confirm="确认",
            cancel="取消",
            box_type=2,
            distinguish_cancel_and_close=True,
            callback=box_cb,
        )
        set_opened("区分取消与关闭")

    def open_validation(_eid):
        ui.show_prompt_box(
            hwnd,
            "📧 校验失败示例",
            "默认填入错误邮箱，点击确定会显示红色校验提示。",
            placeholder="name@example.com",
            value="错误邮箱",
            pattern=email_pattern,
            error="邮箱格式不正确",
            confirm="验证 ✅",
            cancel="取消",
            box_type=3,
            callback=box_cb,
        )
        set_opened("输入校验失败")

    def open_loading(_eid):
        mid = ui.show_msgbox(
            hwnd,
            "🚀 延迟执行",
            "点击确认后按钮进入加载状态，延迟结束再关闭。",
            confirm="开始执行 ✅",
            cancel="取消",
            box_type=0,
            show_cancel=True,
            callback=box_cb,
        )
        ui.set_messagebox_before_close(hwnd, mid, 1200, "执行中...")
        set_opened("确认前加载")

    scene_panel = add_demo_panel(hwnd, stage, "🎛️ 场景变化与交互状态", 28, 552, w - 56, 238)
    add_show_button(scene_panel, "🎯", "居中", 28, 70, 142, open_centered)
    add_show_button(scene_panel, "🎨", "富文本", 196, 70, 142, open_rich)
    add_show_button(scene_panel, "🧭", "区分关闭", 364, 70, 142, open_distinguish)
    add_show_button(scene_panel, "📧", "输入校验", 532, 70, 142, open_validation)
    add_show_button(scene_panel, "🚀", "延迟关闭", 700, 70, 142, open_loading)
    add_text(hwnd, scene_panel, "这里不再复用标准四按钮，而是单独展示居中、富文本、关闭来源区分、输入校验和关闭前延迟处理。", 28, 128, w - 112, 48, MUTED)


def showcase_notification(hwnd, stage, w, h):
    type_names = {0: "信息", 1: "成功", 2: "警告", 3: "错误"}
    action_names = {
        0: "无动作",
        1: "属性设置",
        2: "鼠标关闭",
        3: "键盘关闭",
        4: "程序关闭",
        5: "定时关闭",
    }
    placement_names = {0: "右上角", 1: "右下角", 2: "左下角", 3: "左上角"}
    tracked = {"target": 0, "auto": 0, "keyboard": 0, "rich": 0, "last_service": 0, "rich_closable": False}

    status_id = add_text(hwnd, stage, "🔔 最近通知：页面已展示嵌入式通知，点击按钮可触发服务式通知。", 44, 28, w - 88, 26, MUTED)

    @ui.ValueCallback
    def on_notification_close(element_id, close_count, notify_type, action):
        action_text = action_names.get(action, "状态更新")
        type_text = type_names.get(notify_type, "通知")
        ui.set_element_text(hwnd, status_id, f"🔔 最近关闭：#{element_id} · {type_text} · {action_text} · 第 {close_count} 次")

    notify_cb = keep_callback(on_notification_close)

    left_w = min(1052, w - 646)
    control_x = 28 + left_w + 28
    control_w = w - control_x - 28

    embedded = add_demo_panel(hwnd, stage, "🧩 嵌入式通知：创建、类型、关闭按钮与自动关闭", 28, 68, left_w, 448)
    type_specs = [
        ("ℹ️ 信息通知", "type=0，适合轻量说明。", 0),
        ("✅ 成功通知", "type=1，左侧强调色为成功绿。", 1),
        ("⚠️ 警告通知", "type=2，适合风险提醒。", 2),
        ("❌ 错误通知", "type=3，适合失败反馈。", 3),
    ]
    type_ids = []
    notify_w = 238
    for i, (title, body, notify_type) in enumerate(type_specs):
        nid = ui.create_notification(
            hwnd, embedded, title, body, notify_type, True,
            26 + i * (notify_w + 14), 68, notify_w, 106,
        )
        type_ids.append(nid)

    stack_ids = []
    for idx, (title, body, notify_type) in enumerate([
        ("📚 堆叠 1", "EU_SetNotificationStack index=0", 0),
        ("📚 堆叠 2", "同一基准点自动下移", 1),
        ("📚 堆叠 3", "gap 控制垂直间距", 2),
    ]):
        nid = ui.create_notification(hwnd, embedded, title, body, notify_type, True, 28, 210, 460, 70)
        ui.set_notification_stack(hwnd, nid, idx, 8)
        stack_ids.append(nid)

    auto_id = ui.create_notification(
        hwnd, embedded,
        "⏱️ 自动关闭进度条",
        "duration=15000ms，底部进度条会随定时器减少。",
        0, True, 528, 210, 470, 90,
    )
    ui.set_notification_options(hwnd, auto_id, notify_type=0, closable=True, duration_ms=15000)

    rich_id = ui.create_notification(
        hwnd, embedded,
        "🎨 富文本 + 无关闭按钮",
        "<strong>加粗</strong>、<i>斜体</i> 与 <span style=\"color: teal\">彩色文字</span> 同屏展示。",
        1, False, 528, 314, 470, 90,
    )
    ui.set_notification_rich_mode(hwnd, rich_id, True)
    ui.set_notification_placement(hwnd, rich_id, "bottom-left", 36)

    tracked["target"] = type_ids[0]
    tracked["auto"] = auto_id
    tracked["keyboard"] = stack_ids[1]
    tracked["rich"] = rich_id

    for nid in type_ids + stack_ids + [auto_id, rich_id]:
        ui.set_notification_close_callback(hwnd, nid, notify_cb)

    control = add_demo_panel(hwnd, stage, "🎛️ Set/Get、关闭来源与回调", control_x, 68, control_w, 448)
    callback_hint_id = add_text(hwnd, control, "📣 关闭回调：等待触发", 24, 54, control_w - 48, 28, MUTED)
    state_id = add_text(hwnd, control, "📋 状态读回：点击「读回状态」查看完整字段。", 24, 92, control_w - 48, 132, TEXT)

    def refresh_state(label, element_id=None):
        nid = element_id or tracked["last_service"] or tracked["target"]
        if not nid:
            return
        title = ui.get_notification_text(hwnd, nid, 0)
        body = ui.get_notification_text(hwnd, nid, 1)
        options = ui.get_notification_options(hwnd, nid)
        base = ui.get_notification_full_state(hwnd, nid) or {}
        state = ui.get_notification_full_state_ex(hwnd, nid) or {}
        closed = ui.dll.EU_GetNotificationClosed(hwnd, nid)
        type_text = type_names.get(state.get("notify_type", base.get("notify_type", 0)), "通知")
        action_text = action_names.get(state.get("last_action", base.get("last_action", 0)), "状态更新")
        place_text = placement_names.get(state.get("placement", 0), "右上角")
        option_text = "读取失败" if not options else f"type={options[0]} / closable={int(options[1])} / duration={options[2]} / closed={int(options[3])}"
        ui.set_element_text(
            hwnd,
            state_id,
            f"📋 {label}\n元素 #{nid} · {type_text} · {place_text} · rich={state.get('rich', 0)}\n"
            f"closed={closed} · timer={state.get('timer_running', base.get('timer_running', 0))} · "
            f"stack={state.get('stack_index', base.get('stack_index', 0))}/{state.get('stack_gap', base.get('stack_gap', 0))}\n"
            f"last={action_text} · 标题：{title}\n正文：{body}\n选项：{option_text}",
        )

    def remember_service(nid, label):
        if nid > 0:
            tracked["last_service"] = nid
            ui.set_notification_close_callback(hwnd, nid, notify_cb)
            refresh_state(label, nid)
        return nid

    def update_target(_eid):
        ui.set_element_text(hwnd, tracked["target"], "❌ 已切换为错误")
        ui.set_notification_body(hwnd, tracked["target"], "正文通过 EU_SetNotificationBody 更新；类型通过 EU_SetNotificationType 切换。")
        ui.set_notification_type(hwnd, tracked["target"], 3)
        refresh_state("已更新嵌入式通知", tracked["target"])

    def toggle_rich_closable(_eid):
        tracked["rich_closable"] = not tracked["rich_closable"]
        ui.set_notification_closable(hwnd, tracked["rich"], tracked["rich_closable"])
        label = "显示关闭按钮" if tracked["rich_closable"] else "隐藏关闭按钮"
        refresh_state(label, tracked["rich"])

    def close_auto(_eid):
        ui.trigger_notification_close(hwnd, tracked["auto"])
        refresh_state("程序关闭自动通知", tracked["auto"])

    def reopen_auto(_eid):
        ui.set_notification_closed(hwnd, tracked["auto"], False)
        ui.set_notification_options(hwnd, tracked["auto"], notify_type=0, closable=True, duration_ms=15000)
        refresh_state("重新打开并重启定时器", tracked["auto"])

    def focus_keyboard(_eid):
        ui.dll.EU_SetElementFocus(hwnd, tracked["keyboard"])
        ui.set_element_text(hwnd, callback_hint_id, "⌨️ 已聚焦第二条堆叠通知，可按 Enter / Esc / Space / Delete 关闭。")
        refresh_state("键盘关闭目标已聚焦", tracked["keyboard"])

    def read_target(_eid):
        refresh_state("手动读回完整状态", tracked["target"])

    def add_control_button(emoji, label, x, y, handler):
        btn = ui.create_button(hwnd, control, emoji, label, x, y, 154, 34)
        set_click(hwnd, btn, handler)
        return btn

    add_control_button("✏️", "更新正文", 24, 250, update_target)
    add_control_button("🚫", "切换关闭", 194, 250, toggle_rich_closable)
    add_control_button("🧯", "程序关闭", 364, 250, close_auto)
    add_control_button("🔁", "重开定时", 24, 296, reopen_auto)
    add_control_button("⌨️", "键盘目标", 194, 296, focus_keyboard)
    add_control_button("📋", "读回状态", 364, 296, read_target)
    add_text(hwnd, control, "关闭按钮、键盘关闭、定时关闭和程序关闭都会进入同一个关闭回调。", 24, 354, control_w - 48, 42, MUTED)

    service = add_demo_panel(hwnd, stage, "🚀 服务式通知：四角位置、自动堆叠、富文本与隐藏关闭按钮", 28, 540, w - 56, 250)

    def show_corners(_eid):
        remember_service(ui.notify_success(hwnd, "✅ 右上角", "保存成功，默认从右上角向下堆叠。", duration_ms=0, position="top-right", offset=56), "服务式右上角")
        remember_service(ui.notify_warning(hwnd, "⚠️ 右下角", "底部位置从下往上堆叠。", duration_ms=0, position="bottom-right", offset=56), "服务式右下角")
        remember_service(ui.notify_info(hwnd, "ℹ️ 左下角", "左下角适合低优先级提醒。", duration_ms=0, position="bottom-left", offset=56), "服务式左下角")
        remember_service(ui.notify_error(hwnd, "❌ 左上角", "左上角用于覆盖四角定位验证。", duration_ms=0, position="top-left", offset=56), "服务式左上角")

    def show_stack(_eid):
        for i in range(3):
            remember_service(
                ui.notify_success(
                    hwnd,
                    f"📚 右上堆叠 {i + 1}",
                    "连续创建会读取同位置可见数量，并自动计算 stack_index。",
                    duration_ms=0,
                    position="top-right",
                    offset=86,
                    w=360,
                    h=92,
                ),
                f"右上堆叠第 {i + 1} 条",
            )

    def show_rich(_eid):
        remember_service(
            ui.notify_info(
                hwnd,
                "🎨 富文本通知",
                "<strong>HTML</strong> 片段、<i>斜体</i> 和 <span style=\"color: teal\">teal</span> 文本可直接绘制。",
                rich=True,
                duration_ms=0,
                position="bottom-left",
                offset=72,
                w=390,
                h=110,
            ),
            "服务式富文本通知",
        )

    def show_hidden(_eid):
        remember_service(
            ui.notify_success(
                hwnd,
                "✅ 无关闭按钮",
                "closable=False，鼠标不能关闭，但程序关闭仍有效。",
                closable=False,
                duration_ms=0,
                position="top-right",
                offset=126,
                w=370,
                h=96,
            ),
            "服务式隐藏关闭按钮",
        )

    def show_auto(_eid):
        remember_service(
            ui.show_notification(
                hwnd,
                title="⏱️ 短时自动关闭",
                message="duration=2800ms，关闭动作为定时关闭。",
                notify_type=0,
                duration_ms=2800,
                position="top-right",
                offset=166,
                w=370,
                h=96,
            ),
            "服务式自动关闭",
        )

    def close_last_service(_eid):
        if tracked["last_service"]:
            ui.trigger_notification_close(hwnd, tracked["last_service"])
            refresh_state("程序关闭最近服务通知", tracked["last_service"])

    service_buttons = [
        ("🧭", "四角通知", show_corners),
        ("📚", "右上堆叠", show_stack),
        ("🎨", "富文本", show_rich),
        ("🚫", "隐藏关闭", show_hidden),
        ("⏱️", "自动关闭", show_auto),
        ("🧯", "关闭最近", close_last_service),
    ]
    for i, (emoji, label, handler) in enumerate(service_buttons):
        btn = ui.create_button(hwnd, service, emoji, label, 28 + i * 158, 72, 142, 36)
        set_click(hwnd, btn, handler)
    add_text(hwnd, service, "这些按钮调用 EU_ShowNotification；通知直接挂到根元素，按 position/offset 在窗口四角浮出。", 28, 132, w - 112, 28, MUTED)
    add_text(hwnd, service, "右上堆叠按钮会一次创建三条同位置通知，用于验证服务式自动 stack_index 和 stack_gap。", 28, 168, w - 112, 28, MUTED)

    fields = add_demo_panel(hwnd, stage, "📋 已覆盖的 Notification 导出能力", 28, 814, w - 56, 270)
    field_specs = [
        ("创建", "EU_CreateNotification / EU_ShowNotification", "嵌入式卡片与服务式浮层同页展示。"),
        ("属性", "SetBody / SetType / SetClosable / SetOptions", "正文、类型、关闭按钮和 duration 可动态修改。"),
        ("位置", "SetPlacement / SetStack", "四角 position、offset 与 stack_index/gap 都有可见演示。"),
        ("富文本", "SetRichMode", "strong、i、span color 在通知正文内渲染。"),
        ("关闭", "SetClosed / TriggerClose / CloseCallback", "鼠标、键盘、程序和定时关闭会记录动作来源。"),
        ("读回", "GetText / GetOptions / GetFullStateEx", "右侧状态区读回文本、选项和完整内部状态。"),
    ]
    for i, (title, api, desc) in enumerate(field_specs):
        col = i % 3
        row = i // 3
        card_x = 28 + col * 520
        card_y = 66 + row * 92
        card = add_themed_panel(hwnd, fields, card_x, card_y, 488, 76, "panel_neutral", "panel_neutral_border", 1.0, 8.0, 10)
        add_role_text(hwnd, card, f"🔔 {title}", 14, 10, 160, 24, "panel_neutral_text")
        add_text(hwnd, card, api, 14, 34, 450, 22, MUTED)
        add_text(hwnd, card, desc, 180, 10, 286, 48, MUTED)

    refresh_state("初始嵌入式通知", tracked["target"])


def showcase_dialog(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "💬 点击任意按钮打开对应 Dialog；表格、表单和页脚按钮都挂在真实 slot 容器中。", 36, 28, w - 72, 28, MUTED)
    top = add_demo_panel(hwnd, stage, "💬 Dialog 样式与 slot 容器", 28, 70, w - 56, 330)
    bottom = add_demo_panel(hwnd, stage, "🧩 嵌套内容场景", 28, 430, w - 56, 360)

    def open_basic(_eid):
        dlg = ui.create_dialog(hwnd, "💬 提示", "这是一段信息，支持中文与 emoji。", True, True, 460, 250)
        ui.set_dialog_buttons(hwnd, dlg, ["确定 ✅", "取消 ❌"])
        ui.set_dialog_options(hwnd, dlg, open=True, modal=True, closable=True, close_on_mask=True, draggable=True, w=460, h=250)
        ui.set_element_text(hwnd, status, "💬 已打开基础提示 Dialog")

    def open_center(_eid):
        dlg = ui.create_dialog(hwnd, "🎯 居中提示", "标题和页脚按钮居中，内容保持常规阅读排版。", True, True, 460, 250)
        ui.set_dialog_buttons(hwnd, dlg, ["确定 ✅", "取消 ❌"])
        ui.set_dialog_advanced_options(hwnd, dlg, width_mode=0, width_value=460, center=True, footer_center=True, content_padding=22, footer_height=62)
        ui.set_dialog_options(hwnd, dlg, open=True, modal=True, closable=True, close_on_mask=True, draggable=True, w=460, h=250)
        ui.set_element_text(hwnd, status, "🎯 已打开居中 Dialog")

    before_holder = {"dialog": 0}

    @ui.BeforeCloseCallback
    def before_close(element_id, action):
        ui.set_element_text(hwnd, status, f"🛡️ before-close 已拦截 #{element_id}，动作={action}；点击确认关闭继续。")
        return 0

    keep_callback(before_close)

    def open_before_close(_eid):
        dlg = ui.create_dialog(hwnd, "🛡️ 关闭前确认", "关闭动作会先进入 before-close，外部确认后再继续关闭。", False, True, 500, 260)
        before_holder["dialog"] = dlg
        ui.set_dialog_buttons(hwnd, dlg, ["尝试关闭 ✅", "取消 ❌"])
        ui.set_dialog_before_close_callback(hwnd, dlg, before_close)
        ui.set_dialog_options(hwnd, dlg, open=True, modal=False, closable=True, close_on_mask=False, draggable=True, w=500, h=260)
        ui.set_element_text(hwnd, status, "🛡️ 已打开 before-close Dialog，关闭会先被拦截。")

    def confirm_blocked(_eid):
        dlg = before_holder["dialog"]
        if not dlg:
            ui.set_element_text(hwnd, status, "🛡️ 请先打开 before-close Dialog。")
            return
        options = ui.get_dialog_options(hwnd, dlg)
        if options and not options[0]:
            before_holder["dialog"] = 0
            ui.set_element_text(hwnd, status, "✅ before-close Dialog 已经关闭。")
            return
        advanced = ui.get_dialog_advanced_options(hwnd, dlg)
        if not advanced or not advanced.get("close_pending"):
            ui.trigger_dialog_button(hwnd, dlg, 0)
            advanced = ui.get_dialog_advanced_options(hwnd, dlg)
        if advanced and advanced.get("close_pending"):
            ui.confirm_dialog_close(hwnd, dlg, True)
            before_holder["dialog"] = 0
            ui.set_element_text(hwnd, status, "✅ 已确认继续关闭 before-close Dialog。")
        else:
            ui.set_element_text(hwnd, status, "🛡️ 请先点击弹窗里的尝试关闭，再确认关闭。")

    def open_table(_eid):
        dlg = ui.create_dialog(hwnd, "📦 收货地址", "", True, True, 680, 360)
        ui.set_dialog_buttons(hwnd, dlg, ["确定 ✅", "取消 ❌"])
        ui.set_dialog_advanced_options(hwnd, dlg, width_mode=0, width_value=680, center=False, footer_center=False, content_padding=22, footer_height=62)
        parent_id = ui.get_dialog_content_parent(hwnd, dlg)
        ui.create_table(
            hwnd, parent_id,
            ["日期", "姓名", "地址"],
            [
                ["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"],
                ["2016-05-04", "王小虎", "上海市普陀区金沙江路 1518 弄"],
                ["2016-05-01", "王小虎", "上海市普陀区金沙江路 1518 弄"],
                ["2016-05-03", "王小虎", "上海市普陀区金沙江路 1518 弄"],
            ],
            True, True, 0, 0, 620, 190,
        )
        ui.set_dialog_options(hwnd, dlg, open=True, modal=True, closable=True, close_on_mask=True, draggable=True, w=680, h=360)
        ui.set_element_text(hwnd, status, "📦 已打开带真实 Table slot 的 Dialog。")

    def open_form(_eid):
        dlg = ui.create_dialog(hwnd, "🧾 活动表单", "", True, True, 620, 380)
        ui.set_dialog_buttons(hwnd, dlg, ["确定 ✅", "取消 ❌"])
        ui.set_dialog_advanced_options(hwnd, dlg, width_mode=0, width_value=620, center=False, footer_center=False, content_padding=24, footer_height=62)
        parent_id = ui.get_dialog_content_parent(hwnd, dlg)
        add_text(hwnd, parent_id, "活动名称", 0, 10, 94, 28, TEXT)
        ui.create_input(hwnd, parent_id, "", "请输入活动名称 🎉", x=110, y=4, w=360, h=38)
        add_text(hwnd, parent_id, "活动区域", 0, 66, 94, 28, TEXT)
        ui.create_select(hwnd, parent_id, "请选择活动区域", ["区域一：上海", "区域二：北京"], 0, 110, 60, 360, 38)
        add_text(hwnd, parent_id, "备注", 0, 122, 94, 28, TEXT)
        ui.create_input(hwnd, parent_id, "", "补充说明，可留空 ✍️", x=110, y=116, w=360, h=38)
        ui.set_dialog_options(hwnd, dlg, open=True, modal=True, closable=True, close_on_mask=True, draggable=True, w=620, h=380)
        ui.set_element_text(hwnd, status, "🧾 已打开 Text + Input + Select 组合表单 Dialog。")

    def open_nested(_eid):
        outer = ui.create_dialog(hwnd, "🪟 外层 Dialog", "外层页脚按钮可继续打开内层 Dialog。", True, True, 560, 300)
        footer = ui.get_dialog_footer_parent(hwnd, outer)
        ui.set_dialog_advanced_options(hwnd, outer, width_mode=0, width_value=560, center=False, footer_center=True, content_padding=22, footer_height=64)
        btn_cancel = ui.create_button(hwnd, footer, "❌", "取消", 118, 14, 110, 36)
        btn_inner = ui.create_button(hwnd, footer, "🪟", "打开内层", 244, 14, 130, 36)
        set_click(hwnd, btn_cancel, lambda _id: ui.set_dialog_options(hwnd, outer, open=False, modal=True, closable=True, close_on_mask=True, draggable=True, w=560, h=300))
        def open_inner(_id):
            inner = ui.create_dialog(hwnd, "🪟 内层 Dialog", "内层 Dialog 追加到窗口根部，显示在外层之上。", True, True, 360, 210)
            ui.set_dialog_buttons(hwnd, inner, ["知道了 ✅"])
            ui.set_dialog_options(hwnd, inner, open=True, modal=True, closable=True, close_on_mask=True, draggable=True, w=360, h=210)
        set_click(hwnd, btn_inner, open_inner)
        ui.set_dialog_options(hwnd, outer, open=True, modal=True, closable=True, close_on_mask=True, draggable=True, w=560, h=300)
        ui.set_element_text(hwnd, status, "🪟 已打开外层 Dialog，可继续打开内层。")

    buttons = [
        ("💬", "基础提示", open_basic),
        ("🎯", "居中 Dialog", open_center),
        ("🛡️", "before-close", open_before_close),
        ("✅", "确认关闭", confirm_blocked),
    ]
    for i, (emoji, label, handler) in enumerate(buttons):
        btn = ui.create_button(hwnd, top, emoji, label, 30 + i * 170, 74, 146, 38)
        set_click(hwnd, btn, handler)
    add_text(hwnd, top, "支持遮罩关闭、拖拽、百分比宽度、居中标题/页脚、关闭前拦截。", 30, 140, w - 120, 28, MUTED)

    complex_buttons = [
        ("📦", "嵌套表格", open_table),
        ("🧾", "嵌套表单", open_form),
        ("🪟", "外层/内层", open_nested),
    ]
    for i, (emoji, label, handler) in enumerate(complex_buttons):
        btn = ui.create_button(hwnd, bottom, emoji, label, 30 + i * 180, 76, 150, 40)
        set_click(hwnd, btn, handler)
    add_text(hwnd, bottom, "表格和表单不再用假截图或纯文本替代，而是挂到 Dialog 内容 slot 中真实绘制和交互。", 30, 144, w - 120, 28, MUTED)
    ui.create_table(hwnd, bottom, ["能力", "状态", "说明"], [["content slot", "✅", "可挂载 Table/Input/Select"], ["footer slot", "✅", "可替换默认按钮区"], ["before-close", "✅", "支持拦截后继续关闭"]], True, True, 30, 198, min(w - 120, 760), 116)


def showcase_drawer(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "📚 选择左侧入口打开抽屉；内容区、页脚区和关闭确认都是真实组件。", 36, 28, w - 72, 28, MUTED)
    directions = add_demo_panel(hwnd, stage, "🧭 方向与尺寸", 28, 70, 760, 288)
    slots = add_demo_panel(hwnd, stage, "📋 内容 slot：表格与表单", 820, 70, w - 848, 288)
    closing = add_demo_panel(hwnd, stage, "🛡️ 关闭确认与嵌套抽屉", 28, 386, 820, 292)
    style_panel = add_demo_panel(hwnd, stage, "🎨 桌面属性面板风格", 880, 386, w - 908, 292)
    api_panel = add_demo_panel(hwnd, stage, "📌 Drawer 样式覆盖", 28, 706, w - 56, 330)

    close_stats = {"count": 0}
    confirm_holder = {"drawer": 0, "dialog": 0}

    @ui.ValueCallback
    def on_drawer_closed(element_id, close_count, placement, action):
        close_stats["count"] = close_count
        ui.set_element_text(hwnd, status, f"✅ 抽屉 #{element_id} 已关闭；方向={placement}，动作={action}，累计={close_count}")

    @ui.BeforeCloseCallback
    def before_close(element_id, action):
        confirm_holder["drawer"] = element_id
        ui.set_element_text(hwnd, status, f"🛡️ 抽屉 #{element_id} 请求关闭，动作={action}；等待确认 Dialog。")
        old_dialog = confirm_holder.get("dialog", 0)
        if old_dialog:
            options = ui.get_dialog_options(hwnd, old_dialog)
            if options and options[0]:
                return 0
        dlg = ui.create_dialog(hwnd, "🛡️ 确认关闭抽屉", "抽屉里还有未提交内容，确定关闭吗？", True, True, 480, 240)
        confirm_holder["dialog"] = dlg
        ui.set_dialog_buttons(hwnd, dlg, ["确认关闭 ✅", "继续编辑 ✍️"])
        ui.set_dialog_advanced_options(hwnd, dlg, width_mode=0, width_value=480, center=True, footer_center=True, content_padding=22, footer_height=62)

        @ui.ValueCallback
        def on_confirm(_dialog_id, button_index, _count, _dialog_action):
            target = confirm_holder.get("drawer", element_id)
            allow = button_index == 0
            ui.confirm_drawer_close(hwnd, target, allow)
            ui.set_element_text(hwnd, status, "✅ 已确认关闭抽屉。" if allow else "✍️ 已取消关闭，继续编辑。")

        keep_callback(on_confirm)
        ui.set_dialog_button_callback(hwnd, dlg, on_confirm)
        ui.set_dialog_options(hwnd, dlg, open=True, modal=True, closable=True, close_on_mask=False, draggable=True, w=480, h=240)
        return 0

    keep_callback(on_drawer_closed)
    keep_callback(before_close)

    def add_footer_buttons(drawer, ok_text="确定 ✅"):
        footer = ui.get_drawer_footer_parent(hwnd, drawer)
        cancel = ui.create_button(hwnd, footer, "❌", "取消", 36, 12, 92, 36)
        ok = ui.create_button(hwnd, footer, "✅", ok_text, 144, 12, 118, 36)
        set_click(hwnd, cancel, lambda _id: ui.trigger_drawer_close(hwnd, drawer))
        set_click(hwnd, ok, lambda _id: ui.trigger_drawer_close(hwnd, drawer))

    def open_direction(placement, size_mode, size_value, label):
        drawer = ui.create_drawer(hwnd, f"🧭 {label}", "", placement, True, True, size_value if size_mode == 0 else 420)
        ui.set_drawer_close_callback(hwnd, drawer, on_drawer_closed)
        ui.set_drawer_options(hwnd, drawer, placement=placement, open=True, modal=True, closable=True, close_on_mask=True, size=size_value if size_mode == 0 else 420)
        ui.set_drawer_advanced_options(hwnd, drawer, show_header=True, show_close=True, close_on_escape=True, content_padding=22, footer_height=58, size_mode=size_mode, size_value=size_value)
        content = ui.get_drawer_content_parent(hwnd, drawer)
        add_text(hwnd, content, f"{label}\n尺寸模式：{'百分比 50%' if size_mode == 1 else str(size_value) + 'px'}", 0, 0, 320, 58, TEXT)
        ui.create_table(hwnd, content, ["项目", "状态"], [["中文标题", "✅"], ["emoji 渲染", "🌈"], ["遮罩关闭", "✅"]], True, True, 0, 76, 330, 122)
        add_footer_buttons(drawer)
        ui.set_element_text(hwnd, status, f"🧭 已打开：{label}")
        return drawer

    def open_no_header(_eid):
        drawer = ui.create_drawer(hwnd, "", "", 1, True, True, 360)
        ui.set_drawer_close_callback(hwnd, drawer, on_drawer_closed)
        ui.set_drawer_options(hwnd, drawer, placement=1, open=True, modal=True, closable=True, close_on_mask=True, size=360)
        ui.set_drawer_advanced_options(hwnd, drawer, show_header=False, show_close=False, close_on_escape=True, content_padding=24, footer_height=58, size_mode=0, size_value=360)
        content = ui.get_drawer_content_parent(hwnd, drawer)
        add_text(hwnd, content, "📚 无标题栏抽屉\n内容从顶部 padding 开始，程序仍可关闭。", 0, 0, 304, 76, TEXT)
        done_btn = ui.create_button(hwnd, content, "✅", "完成并关闭", 0, 104, 150, 38)
        set_click(hwnd, done_btn, lambda _id: ui.trigger_drawer_close(hwnd, drawer))
        set_click(hwnd, ui.create_button(hwnd, content, "🧭", "更新状态", 162, 104, 134, 38), lambda _id: ui.set_element_text(hwnd, status, "🧭 无标题栏抽屉仍可响应内部按钮。"))
        add_footer_buttons(drawer)
        ui.set_element_text(hwnd, status, "📚 已打开无标题栏抽屉。")

    def open_table_drawer(_eid):
        drawer = ui.create_drawer(hwnd, "📦 收货地址", "", 1, True, True, 520)
        ui.set_drawer_close_callback(hwnd, drawer, on_drawer_closed)
        ui.set_drawer_options(hwnd, drawer, placement=1, open=True, modal=True, closable=True, close_on_mask=True, size=520)
        ui.set_drawer_advanced_options(hwnd, drawer, content_padding=24, footer_height=62, size_mode=1, size_value=50)
        content = ui.get_drawer_content_parent(hwnd, drawer)
        ui.create_table(
            hwnd, content,
            ["日期", "姓名", "地址"],
            [
                ["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"],
                ["2016-05-04", "李小萌", "北京市朝阳区望京路 88 号"],
                ["2016-05-01", "陈小南", "杭州市西湖区文三路 99 号"],
                ["2016-05-03", "周小北", "深圳市南山区科技园 5 栋"],
            ],
            True, True, 0, 0, 690, 190,
        )
        add_text(hwnd, content, "📦 表格直接挂在 Drawer 内容 slot 中，可随抽屉一起滑入。", 0, 214, 620, 28, MUTED)
        add_footer_buttons(drawer)
        ui.set_element_text(hwnd, status, "📦 已打开真实表格抽屉。")

    def open_form_drawer(_eid):
        drawer = ui.create_drawer(hwnd, "🧾 活动表单", "", 0, True, True, 460)
        ui.set_drawer_close_callback(hwnd, drawer, on_drawer_closed)
        ui.set_drawer_options(hwnd, drawer, placement=0, open=True, modal=True, closable=True, close_on_mask=True, size=460)
        ui.set_drawer_advanced_options(hwnd, drawer, content_padding=24, footer_height=66, size_mode=0, size_value=460)
        content = ui.get_drawer_content_parent(hwnd, drawer)
        add_text(hwnd, content, "活动名称", 0, 8, 100, 28, TEXT)
        ui.create_input(hwnd, content, "", "请输入活动名称 🎉", x=112, y=2, w=270, h=38)
        add_text(hwnd, content, "活动区域", 0, 66, 100, 28, TEXT)
        ui.create_select(hwnd, content, "请选择活动区域", ["区域一：上海", "区域二：北京", "区域三：深圳"], 0, 112, 60, 270, 38)
        add_text(hwnd, content, "备注", 0, 124, 100, 28, TEXT)
        ui.create_input(hwnd, content, "", "补充说明，可留空 ✍️", x=112, y=118, w=270, h=38)
        add_footer_buttons(drawer, "提交 ✅")
        ui.set_element_text(hwnd, status, "🧾 已打开真实表单抽屉，页脚按钮挂在 footer slot。")

    def open_confirm_drawer(_eid):
        drawer = ui.create_drawer(hwnd, "🛡️ 关闭前确认", "", 1, True, True, 420)
        ui.set_drawer_close_callback(hwnd, drawer, on_drawer_closed)
        ui.set_drawer_before_close_callback(hwnd, drawer, before_close)
        ui.set_drawer_options(hwnd, drawer, placement=1, open=True, modal=True, closable=True, close_on_mask=True, size=420)
        ui.set_drawer_advanced_options(hwnd, drawer, content_padding=24, footer_height=62, size_mode=0, size_value=420)
        content = ui.get_drawer_content_parent(hwnd, drawer)
        add_text(hwnd, content, "🛡️ 点击右上角、遮罩、ESC 或页脚按钮时，会先弹出确认 Dialog。", 0, 0, 350, 72, TEXT)
        ui.create_input(hwnd, content, "未保存的草稿", "请输入草稿内容", x=0, y=94, w=300, h=38)
        add_footer_buttons(drawer, "尝试关闭 ✅")
        ui.set_element_text(hwnd, status, "🛡️ 已打开 before-close 抽屉。")

    def open_nested_drawer(_eid):
        outer = ui.create_drawer(hwnd, "🧳 外层抽屉", "", 1, True, True, 500)
        ui.set_drawer_close_callback(hwnd, outer, on_drawer_closed)
        ui.set_drawer_options(hwnd, outer, placement=1, open=True, modal=True, closable=True, close_on_mask=True, size=500)
        ui.set_drawer_advanced_options(hwnd, outer, content_padding=24, footer_height=62, size_mode=0, size_value=500)
        outer_content = ui.get_drawer_content_parent(hwnd, outer)
        add_text(hwnd, outer_content, "🧳 外层抽屉内容区中有一个按钮，点击后打开根级内层抽屉。", 0, 0, 410, 58, TEXT)
        inner_btn = ui.create_button(hwnd, outer_content, "🪆", "打开里面的抽屉", 0, 86, 180, 40)
        add_footer_buttons(outer)

        def open_inner(_id):
            inner = ui.create_drawer(hwnd, "🪆 内层抽屉", "内层抽屉作为窗口级浮层创建，显示在外层之上。", 1, True, True, 300)
            ui.set_drawer_close_callback(hwnd, inner, on_drawer_closed)
            ui.set_drawer_options(hwnd, inner, placement=1, open=True, modal=True, closable=True, close_on_mask=True, size=300)
            ui.set_drawer_advanced_options(hwnd, inner, content_padding=22, footer_height=58, size_mode=0, size_value=300)
            add_footer_buttons(inner, "知道了 ✅")
            ui.set_element_text(hwnd, status, "🪆 已打开内层抽屉。")

        set_click(hwnd, inner_btn, open_inner)
        ui.set_element_text(hwnd, status, "🧳 已打开外层抽屉。")

    def open_custom_drawer(_eid):
        drawer = ui.create_drawer(hwnd, "🎨 属性面板", "", 1, False, True, 380)
        ui.set_drawer_close_callback(hwnd, drawer, on_drawer_closed)
        ui.set_drawer_options(hwnd, drawer, placement=1, open=True, modal=False, closable=True, close_on_mask=False, size=380)
        ui.set_drawer_advanced_options(hwnd, drawer, show_header=True, show_close=True, close_on_escape=True, content_padding=22, footer_height=64, size_mode=0, size_value=380)
        ui.set_element_color(hwnd, drawer, 0xFF27314D, 0xFFEAF2FF)
        content = ui.get_drawer_content_parent(hwnd, drawer)
        add_text(hwnd, content, "🎛️ 主题设置", 0, 0, 180, 28, TEXT)
        ui.create_switch(hwnd, content, "启用通知 🔔", True, 0, 46, 220, 34)
        ui.create_slider(hwnd, content, "透明度", 0, 100, 82, 0, 96, 260, 36)
        ui.create_select(hwnd, content, "布局密度", ["紧凑", "常规", "宽松"], 1, 0, 150, 260, 38)
        add_footer_buttons(drawer, "应用 ✅")
        ui.set_element_text(hwnd, status, "🎨 已打开桌面属性面板风格抽屉。")

    direction_buttons = [
        ("⬅️", "从左打开", lambda _id: open_direction(0, 0, 360, "从左往右开")),
        ("➡️", "从右打开 50%", lambda _id: open_direction(1, 1, 50, "从右往左开")),
        ("⬇️", "从上打开 50%", lambda _id: open_direction(2, 1, 50, "从上往下开")),
        ("⬆️", "从下打开", lambda _id: open_direction(3, 0, 300, "从下往上开")),
    ]
    for i, (emoji, label, handler) in enumerate(direction_buttons):
        btn = ui.create_button(hwnd, directions, emoji, label, 30 + (i % 2) * 210, 76 + (i // 2) * 62, 180, 40)
        set_click(hwnd, btn, handler)
    no_header_btn = ui.create_button(hwnd, directions, "📚", "无标题栏", 462, 76, 150, 40)
    set_click(hwnd, no_header_btn, open_no_header)
    add_text(hwnd, directions, "方向按钮覆盖 ltr/rtl/ttb/btt；右侧和顶部按钮使用 50% 百分比尺寸。", 30, 210, 660, 32, MUTED)

    table_btn = ui.create_button(hwnd, slots, "📦", "打开表格抽屉", 30, 78, 170, 40)
    form_btn = ui.create_button(hwnd, slots, "🧾", "打开表单抽屉", 220, 78, 170, 40)
    set_click(hwnd, table_btn, open_table_drawer)
    set_click(hwnd, form_btn, open_form_drawer)
    ui.create_table(hwnd, slots, ["内容", "挂载位置"], [["Table", "content slot"], ["Input", "content slot"], ["Button", "footer slot"]], True, True, 30, 150, min(w - 980, 560), 116)

    confirm_btn = ui.create_button(hwnd, closing, "🛡️", "关闭确认", 30, 78, 150, 40)
    nested_btn = ui.create_button(hwnd, closing, "🧳", "外层/内层抽屉", 206, 78, 180, 40)
    set_click(hwnd, confirm_btn, open_confirm_drawer)
    set_click(hwnd, nested_btn, open_nested_drawer)
    add_text(hwnd, closing, "关闭确认使用 before-close 回调进入 pending，Dialog 确认后再调用 EU_ConfirmDrawerClose。", 30, 150, 720, 32, MUTED)
    add_text(hwnd, closing, "内层抽屉作为根级 Drawer 创建，等价 append-to-body，后创建者显示在上层。", 30, 200, 720, 32, MUTED)

    custom_btn = ui.create_button(hwnd, style_panel, "🎨", "打开属性面板", 30, 78, 170, 40)
    set_click(hwnd, custom_btn, open_custom_drawer)
    ui.create_switch(hwnd, style_panel, "紧凑模式 🎚️", True, 30, 150, 220, 34)
    ui.create_slider(hwnd, style_panel, "面板宽度", 300, 520, 380, 30, 202, min(w - 1000, 360), 36)
    add_text(hwnd, style_panel, "使用现有颜色/字体/表单组件组合出桌面端属性面板，不引入 CSS class。", 30, 242, max(300, w - 1010), 28, MUTED)

    ui.create_table(
        hwnd, api_panel,
        ["样式", "API/能力", "状态"],
        [
            ["方向", "placement 0/1/2/3", "✅"],
            ["无标题栏", "show_header=0 / show_close=0", "✅"],
            ["百分比尺寸", "size_mode=1, size_value=50", "✅"],
            ["内容区", "EU_GetDrawerContentParent", "✅"],
            ["页脚区", "EU_GetDrawerFooterParent", "✅"],
            ["关闭确认", "BeforeClose + ConfirmDrawerClose", "✅"],
            ["嵌套抽屉", "根级 Drawer 覆盖外层", "✅"],
        ],
        True, True, 28, 72, min(w - 112, 980), 224,
    )
    add_text(hwnd, api_panel, "📚 所有示例均为中文文案并带 emoji；首次窗口尺寸已覆盖首屏按钮和状态区。", 1040, 86, max(260, w - 1130), 70, TEXT)
    add_text(hwnd, api_panel, f"关闭回调计数：{close_stats['count']}", 1040, 176, max(260, w - 1130), 28, MUTED)


def showcase_tooltip(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "💭 Tooltip 覆盖 12 方位、深色/浅色、多行内容和禁用状态。", 36, 28, w - 72, 28, MUTED)
    matrix = add_demo_panel(hwnd, stage, "📍 12 方位矩阵", 28, 70, w - 56, 390)
    details = add_demo_panel(hwnd, stage, "🎨 主题、多行与禁用", 28, 470, w - 56, 260)
    placements = [
        ("top-start", "上左"), ("top", "上边"), ("top-end", "上右"),
        ("left-start", "左上"), ("left", "左边"), ("left-end", "左下"),
        ("right-start", "右上"), ("right", "右边"), ("right-end", "右下"),
        ("bottom-start", "下左"), ("bottom", "下边"), ("bottom-end", "下右"),
    ]
    anchor_x = 320
    anchor_y = 82
    col_gap = 270
    row_gap = 72
    for i, (placement, label) in enumerate(placements):
        col = i % 3
        row = i // 3
        tip = ui.create_tooltip(hwnd, matrix, f"{label} 📍", f"📍 {label}提示文字", 2, anchor_x + col * col_gap, anchor_y + row * row_gap, 148, 44)
        ui.set_tooltip_advanced_options(hwnd, tip, placement=placement, effect="dark" if i % 2 == 0 else "light", disabled=False, show_arrow=True, offset=8, max_width=180)
    dark = ui.create_tooltip(hwnd, details, "深色提示 💭", "上方居中提示", 2, 34, 74, 150, 38)
    ui.set_tooltip_advanced_options(hwnd, dark, placement="top", effect="dark", disabled=False, show_arrow=True, offset=8, max_width=220)
    light = ui.create_tooltip(hwnd, details, "浅色提示 ✨", "下方居中提示", 3, 214, 74, 150, 38)
    ui.set_tooltip_advanced_options(hwnd, light, placement="bottom", effect="light", disabled=False, show_arrow=True, offset=8, max_width=220)
    multi = ui.create_tooltip(hwnd, details, "多行内容 🧾", "多行信息\n第二行信息\n自动换行中文内容", 2, 394, 74, 150, 38)
    ui.set_tooltip_advanced_options(hwnd, multi, placement="top", effect="dark", disabled=False, show_arrow=True, offset=8, max_width=210)
    disabled_tip = ui.create_tooltip(hwnd, details, "点击开启 🚫", "当前已禁用，不会弹出", 3, 574, 74, 160, 38)
    disabled_state = {"disabled": True}
    ui.set_tooltip_advanced_options(hwnd, disabled_tip, placement="bottom", effect="light", disabled=True, show_arrow=True, offset=8, max_width=220)
    toggle = ui.create_button(hwnd, details, "🚫", "切换禁用", 764, 74, 158, 38)
    def toggle_disabled(_eid):
        disabled_state["disabled"] = not disabled_state["disabled"]
        ui.set_tooltip_advanced_options(hwnd, disabled_tip, placement="bottom", effect="light", disabled=disabled_state["disabled"], show_arrow=True, offset=8, max_width=220)
        ui.set_element_text(hwnd, status, "🚫 Tooltip 禁用已关闭，可悬停查看。" if not disabled_state["disabled"] else "🚫 Tooltip 禁用已开启，触发区仍绘制但不弹出。")
    set_click(hwnd, toggle, toggle_disabled)
    add_text(hwnd, details, "旧 0/1/2/3 placement 仍兼容；新高级 API 使用 top-start 等 12 方位。", 34, 150, w - 124, 32, MUTED)


def showcase_popover(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "🗯️ Popover 支持 hover/click/focus/manual、slot 内容、外部关闭与键盘关闭。", 36, 28, w - 72, 28, MUTED)
    triggers = add_demo_panel(hwnd, stage, "🖱️ 四种触发方式", 28, 70, w - 56, 250)
    slots = add_demo_panel(hwnd, stage, "📊 嵌套表格与删除确认式 Popover", 28, 350, w - 56, 390)

    specs = [
        ("hover", "悬停激活 🖱️", "🖱️ 悬停打开，离开关闭。", "top"),
        ("click", "点击激活 👆", "👆 点击切换打开状态。", "bottom"),
        ("focus", "聚焦激活 ⌨️", "⌨️ 获得焦点时打开。", "right"),
        ("manual", "手动激活 🧭", "🧭 由程序按钮控制。", "left"),
    ]
    manual_holder = {"id": 0, "open": False}
    for i, (trigger, label, content, placement) in enumerate(specs):
        pop = ui.create_popover(hwnd, triggers, label, f"{label}", content, 3, 34 + i * 190, 76, 156, 38)
        ui.set_popover_advanced_options(hwnd, pop, placement=placement, open=False, popup_width=260, popup_height=132, closable=True)
        ui.set_popover_behavior(hwnd, pop, trigger_mode=trigger, close_on_outside=True, show_arrow=True, offset=8)
        if trigger == "manual":
            manual_holder["id"] = pop
    manual_button = ui.create_button(hwnd, triggers, "🧭", "切换手动弹层", 34, 146, 156, 36)
    def toggle_manual(_eid):
        manual_holder["open"] = not manual_holder["open"]
        ui.trigger_popover(hwnd, manual_holder["id"], manual_holder["open"])
        ui.set_element_text(hwnd, status, "🧭 手动 Popover 已打开。" if manual_holder["open"] else "🧭 手动 Popover 已关闭。")
    set_click(hwnd, manual_button, toggle_manual)
    add_text(hwnd, triggers, "click/hover/focus/manual 均复用同一行为 API；Escape、Tab、Enter 可走键盘路径。", 224, 150, w - 330, 28, MUTED)

    table_pop = ui.create_popover(hwnd, slots, "收货地址 📦", "📦 收货地址", "", 3, 34, 78, 160, 38)
    ui.set_popover_advanced_options(hwnd, table_pop, placement="right", open=False, popup_width=430, popup_height=230, closable=True)
    ui.set_popover_behavior(hwnd, table_pop, trigger_mode="click", close_on_outside=True, show_arrow=True, offset=10)
    table_parent = ui.get_popover_content_parent(hwnd, table_pop)
    ui.create_table(hwnd, table_parent, ["日期", "姓名", "地址"], [["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"], ["2016-05-04", "王小虎", "上海市普陀区金沙江路 1518 弄"], ["2016-05-01", "王小虎", "上海市普陀区金沙江路 1518 弄"]], True, True, 0, 0, 380, 128)

    delete_pop = ui.create_popover(hwnd, slots, "删除 🗑️", "🗑️ 删除确认", "", 3, 234, 78, 120, 38)
    ui.set_popover_advanced_options(hwnd, delete_pop, placement="top", open=False, popup_width=260, popup_height=150, closable=False)
    ui.set_popover_behavior(hwnd, delete_pop, trigger_mode="click", close_on_outside=True, show_arrow=True, offset=8)
    delete_parent = ui.get_popover_content_parent(hwnd, delete_pop)
    add_text(hwnd, delete_parent, "这是一段内容，确定删除吗？", 0, 4, 218, 42, TEXT)
    cancel = ui.create_button(hwnd, delete_parent, "❌", "取消", 44, 62, 76, 30)
    ok = ui.create_button(hwnd, delete_parent, "✅", "确定", 132, 62, 76, 30)
    set_click(hwnd, cancel, lambda _id: ui.trigger_popover(hwnd, delete_pop, False))
    set_click(hwnd, ok, lambda _id: ui.trigger_popover(hwnd, delete_pop, False))
    add_text(hwnd, slots, "上方表格 Popover 使用真实 content slot；删除确认式 Popover 使用 Text + Button 组合。", 34, 158, w - 120, 30, MUTED)


def showcase_popconfirm(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "❓ Popconfirm 覆盖默认确认、自定义按钮、自定义图标颜色、键盘和程序触发结果。", 36, 28, w - 72, 28, MUTED)
    panel = add_demo_panel(hwnd, stage, "❓ Popconfirm 样式矩阵", 28, 70, w - 56, 360)
    result_panel = add_demo_panel(hwnd, stage, "⌨️ 结果读回与程序触发", 28, 460, w - 56, 260)

    default_id = ui.create_popconfirm(hwnd, panel, "删除 ❓", "确认操作", "这是一段内容，确定删除吗？", "确定", "取消", 3, 34, 76, 132, 38)
    ui.set_popconfirm_advanced_options(hwnd, default_id, placement="top", open=False, popup_width=286, popup_height=146, trigger_mode="click", close_on_outside=True, show_arrow=True, offset=8)

    custom_id = ui.create_popconfirm(hwnd, panel, "自定义按钮 🧩", "确认删除", "按钮文案可自定义。", "好的 ✅", "不用了 ❌", 3, 204, 76, 158, 38)
    ui.set_popconfirm_advanced_options(hwnd, custom_id, placement="bottom", open=False, popup_width=300, popup_height=150, trigger_mode="click", close_on_outside=True, show_arrow=True, offset=8)

    icon_id = ui.create_popconfirm(hwnd, panel, "红色图标 ⚠️", "危险操作", "图标文本、颜色和显示状态可配置。", "继续 ✅", "取消 ❌", 3, 402, 76, 150, 38)
    ui.set_popconfirm_advanced_options(hwnd, icon_id, placement="right", open=False, popup_width=310, popup_height=158, trigger_mode="click", close_on_outside=True, show_arrow=True, offset=8)
    ui.set_popconfirm_icon(hwnd, icon_id, icon="!", color=0xFFF56C6C, visible=True)

    hidden_icon = ui.create_popconfirm(hwnd, panel, "隐藏图标 👁️", "轻量确认", "可以隐藏左侧图标。", "明白 ✅", "返回 ❌", 3, 592, 76, 150, 38)
    ui.set_popconfirm_advanced_options(hwnd, hidden_icon, placement="left", open=False, popup_width=300, popup_height=150, trigger_mode="click", close_on_outside=True, show_arrow=True, offset=8)
    ui.set_popconfirm_icon(hwnd, hidden_icon, icon="?", color=0xFFE6A23C, visible=False)
    add_text(hwnd, panel, "确认/取消结果可通过 GetResult 读回，也可注册结果回调；Escape 取消，Enter/Space 确认当前焦点按钮。", 34, 154, w - 124, 30, MUTED)

    result_text = add_text(hwnd, result_panel, "⌨️ 最近结果：等待操作", 34, 76, 620, 28, TEXT)

    @ui.ValueCallback
    def on_result(element_id, result, count, action):
        text = "确认 ✅" if result else "取消 ❌"
        ui.set_element_text(hwnd, result_text, f"⌨️ 最近结果：#{element_id} {text}，次数={count}，动作={action}")

    keep_callback(on_result)
    ui.set_popconfirm_result_callback(hwnd, default_id, on_result)
    ui.set_popconfirm_result_callback(hwnd, custom_id, on_result)
    ui.set_popconfirm_result_callback(hwnd, icon_id, on_result)
    ui.set_popconfirm_result_callback(hwnd, hidden_icon, on_result)

    open_btn = ui.create_button(hwnd, result_panel, "❓", "程序打开默认确认", 34, 130, 168, 36)
    ok_btn = ui.create_button(hwnd, result_panel, "✅", "程序确认", 224, 130, 120, 36)
    cancel_btn = ui.create_button(hwnd, result_panel, "❌", "程序取消", 366, 130, 120, 36)
    set_click(hwnd, open_btn, lambda _id: ui.set_popconfirm_open(hwnd, default_id, True))
    set_click(hwnd, ok_btn, lambda _id: ui.trigger_popconfirm_result(hwnd, default_id, True))
    set_click(hwnd, cancel_btn, lambda _id: ui.trigger_popconfirm_result(hwnd, default_id, False))
    add_text(hwnd, result_panel, "程序触发会更新 result、confirm_count/cancel_count 和回调状态。", 34, 186, w - 120, 28, MUTED)


def showcase_rate(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "⭐ Rate 评分覆盖默认、分段颜色、文字、表情图标、禁用分数、半星、清空、只读和分数模板。", 36, 28, w - 72, 28, MUTED)
    form = add_demo_panel(hwnd, stage, "📝 评分设置表单", 28, 72, 740, 520)
    preview = add_demo_panel(hwnd, stage, "📊 用户反馈预览", 796, 72, w - 824, 520)
    matrix = add_demo_panel(hwnd, stage, "🎛️ 桌面端样式矩阵", 28, 622, w - 56, 420)

    add_text(hwnd, form, "服务态度", 30, 70, 100, 28, MUTED)
    default_rate = ui.create_rate(hwnd, form, "默认评分 ⭐", 3, 5, 146, 66, 430, 40)
    ui.set_rate_texts(hwnd, default_rate, "待评分 🙂", "已评分 ⭐", True)

    add_text(hwnd, form, "区分颜色", 30, 130, 100, 28, MUTED)
    color_rate = ui.create_rate(hwnd, form, "体验评分", 4, 5, 146, 126, 430, 40)
    ui.set_rate_colors(hwnd, color_rate, 0xFF99A9BF, 0xFFF7BA2A, 0xFFFF9900)
    ui.set_rate_texts(hwnd, color_rate, "请选择 🙂", "颜色分段 🎨", True)

    add_text(hwnd, form, "显示文字", 30, 190, 100, 28, MUTED)
    text_rate = ui.create_rate(hwnd, form, "满意度", 0, 5, 146, 186, 500, 40)
    ui.set_rate_text_items(hwnd, text_rate, ["很差 😟", "较差 🙁", "一般 🙂", "满意 😄", "惊喜 🤩"])
    ui.set_rate_display_options(hwnd, text_rate, show_text=True, show_score=False, text_color=0xFFFF9900)
    ui.set_rate_value(hwnd, text_rate, 4)

    add_text(hwnd, form, "表情图标", 30, 250, 100, 28, MUTED)
    face_rate = ui.create_rate(hwnd, form, "心情反馈", 3, 5, 146, 246, 500, 40)
    ui.set_rate_colors(hwnd, face_rate, 0xFF99A9BF, 0xFFF7BA2A, 0xFFFF9900)
    ui.set_rate_icons(hwnd, face_rate, full_icon="😊", void_icon="😶", low_icon="😟", mid_icon="🙂", high_icon="🤩")
    ui.set_rate_display_options(hwnd, face_rate, show_text=True, show_score=False, text_color=0xFFFF9900)
    ui.set_rate_text_items(hwnd, face_rate, ["失望 😟", "偏低 🙁", "还可以 🙂", "很好 😄", "超喜欢 🤩"])

    add_text(hwnd, form, "禁用分数", 30, 310, 100, 28, MUTED)
    disabled_rate = ui.create_rate(hwnd, form, "历史评分", 3, 5, 146, 306, 500, 40, value_x2=7)
    ui.set_rate_options(hwnd, disabled_rate, allow_clear=False, allow_half=True, readonly=True)
    ui.set_rate_display_options(hwnd, disabled_rate, show_text=False, show_score=True, text_color=0xFFFF9900, score_template="{value}")
    ui.set_element_enabled(hwnd, disabled_rate, False)

    add_text(hwnd, form, "半星评分", 30, 370, 100, 28, MUTED)
    half_rate = ui.create_rate(hwnd, form, "细分体验", 3, 5, 146, 366, 500, 40, allow_half=True, value_x2=7)
    ui.set_rate_colors(hwnd, half_rate, 0xFF99A9BF, 0xFFF7BA2A, 0xFFFF9900)
    ui.set_rate_display_options(hwnd, half_rate, show_text=False, show_score=True, text_color=0xFFFF9900, score_template="{value}/{max} 分")

    add_text(hwnd, form, "可清空", 30, 430, 100, 28, MUTED)
    clear_rate = ui.create_rate(hwnd, form, "二次点击清空", 2, 5, 146, 426, 500, 40, allow_clear=True)
    ui.set_rate_texts(hwnd, clear_rate, "尚未选择 🫥", "再次点击当前分值可清空 🧹", True)

    summary = ui.create_descriptions(
        hwnd, preview, "📋 评分读回",
        [
            ("默认值", f"{ui.get_rate_value(hwnd, default_rate)}/5"),
            ("半星值", f"{ui.get_rate_value_x2(hwnd, half_rate)}/10"),
            ("颜色", "低 / 中 / 高三段"),
            ("图标", "Unicode emoji"),
            ("模板", "{value}/{max} 分"),
            ("状态", "只读与禁用分离"),
        ],
        2, True, 30, 70, min(620, w - 920), 180,
    )
    ui.set_descriptions_options(hwnd, summary, columns=2, bordered=True, label_width=98, min_row_height=34, wrap_values=True)

    note = ui.create_infobox(
        hwnd, preview,
        "💡 桌面端使用建议",
        "评分通常放在表单行、评价详情、设置页和数据读回区域。这里避免网页式大段说明，直接展示可编辑项、只读项和业务状态。",
        30, 282, min(640, w - 920), 116,
    )
    ui.set_infobox_options(hwnd, note, 0, 0, 0xFF7AA7FF, "⭐")

    readback = add_text(hwnd, preview, "等待操作：点击下方按钮会同步读回半星值、颜色、图标和显示配置。", 30, 430, min(640, w - 920), 42, MUTED)

    def refresh_status(_eid):
        colors = ui.get_rate_colors(hwnd, color_rate)
        icons = ui.get_rate_icons(hwnd, face_rate)
        display = ui.get_rate_display_options(hwnd, half_rate)
        ui.set_element_text(
            hwnd, readback,
            f"📌 半星值 {ui.get_rate_value_x2(hwnd, half_rate)}/10；颜色={colors}；图标={icons[:2]}；显示={display}"
        )
        ui.set_element_text(hwnd, status, "✅ Rate Set/Get 已读回，颜色、图标、模板和半星状态保持一致。")

    refresh_btn = ui.create_button(hwnd, preview, "🔄", "读回当前评分", 30, 474, 150, 36)
    set_click(hwnd, refresh_btn, refresh_status)

    samples = [
        ("默认不区分颜色", lambda parent, x, y: ui.create_rate(hwnd, parent, "产品质量 ⭐", 3, 5, x, y, 420, 40)),
        ("三段颜色", lambda parent, x, y: _create_and(ui.create_rate(hwnd, parent, "服务态度 🎨", 5, 5, x, y, 420, 40), lambda rid: ui.set_rate_colors(hwnd, rid, 0xFF99A9BF, 0xFFF7BA2A, 0xFFFF9900))),
        ("显示文字", lambda parent, x, y: _create_and(ui.create_rate(hwnd, parent, "满意度 💬", 4, 5, x, y, 480, 40), lambda rid: (ui.set_rate_text_items(hwnd, rid, ["很差 😟", "较差 🙁", "一般 🙂", "满意 😄", "惊喜 🤩"]), ui.set_rate_display_options(hwnd, rid, show_text=True, show_score=False, text_color=0xFFFF9900)))),
        ("表情图标", lambda parent, x, y: _create_and(ui.create_rate(hwnd, parent, "心情反馈 😀", 5, 5, x, y, 480, 40), lambda rid: (ui.set_rate_icons(hwnd, rid, full_icon="😊", void_icon="😶", low_icon="😟", mid_icon="🙂", high_icon="🤩"), ui.set_rate_colors(hwnd, rid, 0xFF99A9BF, 0xFFF7BA2A, 0xFFFF9900)))),
        ("禁用显示分数", lambda parent, x, y: _create_and(ui.create_rate(hwnd, parent, "历史评分 🔒", 3, 5, x, y, 480, 40, value_x2=7), lambda rid: (ui.set_rate_options(hwnd, rid, allow_clear=False, allow_half=True, readonly=True), ui.set_rate_display_options(hwnd, rid, show_text=False, show_score=True, text_color=0xFFFF9900, score_template="{value}"), ui.set_element_enabled(hwnd, rid, False)))),
        ("10 分制模板", lambda parent, x, y: _create_and(ui.create_rate(hwnd, parent, "专业评分 🧭", 8, 10, x, y, 560, 40), lambda rid: ui.set_rate_display_options(hwnd, rid, show_text=False, show_score=True, text_color=0xFFFF9900, score_template="{value}/{max} 分"))),
    ]
    for i, (title, builder) in enumerate(samples):
        col = i % 2
        row = i // 2
        x = 30 + col * 700
        y = 72 + row * 104
        add_text(hwnd, matrix, f"⭐ {title}", x, y, 220, 24, TEXT)
        builder(matrix, x, y + 34)


def showcase_dropdown(hwnd, stage, w, h):
    status = add_text(
        hwnd, stage,
        "📂 Dropdown 已补齐链接、按钮、split-button、hover/click/manual、hide-on-click、图标、禁用、分割线、command 和尺寸。",
        36, 28, w - 72, 28, MUTED,
    )

    trigger_panel = add_demo_panel(hwnd, stage, "🔗 触发器样式", 28, 70, 790, 260)
    button_panel = add_demo_panel(hwnd, stage, "🧰 按钮变体", 842, 70, w - 870, 260)
    behavior_panel = add_demo_panel(hwnd, stage, "🧭 交互行为", 28, 350, 790, 410)
    menu_panel = add_demo_panel(hwnd, stage, "🧾 菜单项样式", 842, 350, w - 870, 410)
    size_panel = add_demo_panel(hwnd, stage, "📐 尺寸矩阵", 28, 780, w - 56, 240)
    readback_panel = add_demo_panel(hwnd, stage, "🗂️ 状态读回", 28, 1030, w - 56, 210)

    action_items = ["📄 复制", "✏️ 编辑", "🗑️ 删除"]
    meta_items = [
        "📄 复制",
        "✏️ 编辑",
        "> !🗑️ 删除",
        "📤 导出",
        "> 归档",
        "> > 归档到项目",
    ]
    scroll_items = [f"📁 最近文件 {i:02d}" for i in range(1, 13)]

    def make_dropdown(parent, text, items, x, y, bw, bh):
        return ui.create_dropdown(hwnd, parent, text, items, 0, x, y, bw, bh)

    link_hover = make_dropdown(trigger_panel, "文字链接", action_items, 34, 74, 160, 34)
    ui.set_dropdown_options(hwnd, link_hover, trigger_mode=1, hide_on_click=True, split_button=False, button_variant=0, size=0, trigger_style=1)

    link_click = make_dropdown(trigger_panel, "文字链接", action_items, 214, 74, 160, 34)
    ui.set_dropdown_options(hwnd, link_click, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=0, size=0, trigger_style=1)

    btn_hover = make_dropdown(trigger_panel, "默认按钮", action_items, 394, 74, 160, 34)
    ui.set_dropdown_options(hwnd, btn_hover, trigger_mode=1, hide_on_click=True, split_button=False, button_variant=0, size=0, trigger_style=0)

    btn_click = make_dropdown(trigger_panel, "主要按钮", action_items, 574, 74, 160, 34)
    ui.set_dropdown_options(hwnd, btn_click, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=1, size=0, trigger_style=0)

    add_text(hwnd, trigger_panel, "文字链接更轻，按钮更像桌面软件里的常用命令入口。", 34, 136, 720, 24, MUTED)
    manual_status = add_text(hwnd, trigger_panel, "🧭 手动菜单：已关闭", 34, 160, 320, 24, TEXT)
    ui.set_text_options(hwnd, manual_status, wrap=True, ellipsis=False)
    manual_menu = make_dropdown(trigger_panel, "手动控制", ["开始", "暂停", "结束"], 34, 188, 220, 36)
    ui.set_dropdown_options(hwnd, manual_menu, trigger_mode=2, hide_on_click=True, split_button=False, button_variant=6, size=0, trigger_style=0)
    toggle_manual = ui.create_button(hwnd, trigger_panel, "🧭", "切换手动菜单", 280, 188, 150, 36)

    variant_specs = [
        ("默认", 0, 34),
        ("主色", 1, 178),
        ("成功", 2, 322),
        ("警告", 3, 466),
        ("危险", 4, 34),
        ("文本", 5, 178),
        ("信息", 6, 322),
    ]
    for label, variant, x in variant_specs:
        y = 74 if variant < 4 else 142
        dd = make_dropdown(button_panel, label, action_items, x, y, 120, 34)
        ui.set_dropdown_options(hwnd, dd, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=variant, size=0, trigger_style=0)

    add_text(hwnd, button_panel, "同一组菜单动作，变体只改变按钮皮肤和语义强度。", 34, 198, 720, 24, MUTED)

    command_status = add_text(hwnd, behavior_panel, "📨 最近命令：等待选择", 34, 42, 720, 24, TEXT)
    ui.set_text_options(hwnd, command_status, wrap=True, ellipsis=False)
    main_status = add_text(hwnd, behavior_panel, "🧭 主按钮：等待点击", 34, 64, 720, 24, TEXT)
    ui.set_text_options(hwnd, main_status, wrap=True, ellipsis=False)

    keep_open = make_dropdown(behavior_panel, "保持展开", meta_items, 34, 74, 220, 36)
    ui.set_dropdown_options(hwnd, keep_open, trigger_mode=0, hide_on_click=False, split_button=False, button_variant=2, size=1, trigger_style=0)
    ui.set_dropdown_item_meta(
        hwnd, keep_open,
        ["📄", "✏️", "🗑️", "📤", "🗂️", "🏷️"],
        ["copy", "", "delete", "export", "archive", "archive_project"],
        [3],
    )
    ui.set_dropdown_disabled(hwnd, keep_open, [4])

    split_menu = make_dropdown(behavior_panel, "分裂按钮", action_items, 280, 74, 220, 36)
    ui.set_dropdown_options(hwnd, split_menu, trigger_mode=0, hide_on_click=True, split_button=True, button_variant=1, size=0, trigger_style=0)

    meta_status = add_text(hwnd, menu_panel, "🧾 图标、禁用、分割线、层级与 command 回调", 34, 42, 700, 24, TEXT)
    ui.set_text_options(hwnd, meta_status, wrap=True, ellipsis=False)
    meta_dropdown = make_dropdown(menu_panel, "项目样式", meta_items, 34, 74, 300, 36)
    ui.set_dropdown_options(hwnd, meta_dropdown, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=0, size=0, trigger_style=0)
    ui.set_dropdown_item_meta(
        hwnd, meta_dropdown,
        ["📄", "✏️", "🗑️", "📤", "🗂️", "🏷️"],
        ["copy", "", "delete", "export", "archive", "archive_project"],
        [3],
    )
    ui.set_dropdown_disabled(hwnd, meta_dropdown, [2, 4])

    scroll_dropdown = make_dropdown(menu_panel, "长列表滚动", scroll_items, 348, 74, 470, 36)
    ui.set_dropdown_options(hwnd, scroll_dropdown, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=0, size=2, trigger_style=0)
    ui.set_dropdown_disabled(hwnd, scroll_dropdown, [4])

    meta_read = ui.create_descriptions(
        hwnd, menu_panel, "📚 元数据回读",
        [
            ("第 1 项", "icon=📄 command=copy level=0"),
            ("第 3 项", "icon=🗑️ command=delete disabled=True level=1"),
            ("第 6 项", "icon=🏷️ command=archive_project level=2"),
            ("说明", "空 command 会回传显示文本"),
        ],
        2, True, 34, 328, 290, 70,
    )
    ui.set_descriptions_options(hwnd, meta_read, columns=2, bordered=True, label_width=84, min_row_height=28, wrap_values=True)

    add_text(hwnd, menu_panel, "长列表默认只显示前 8 行，鼠标滚轮可继续翻页。", 348, 354, 470, 44, MUTED)

    size_labels = [
        ("默认", 0, 34),
        ("medium", 1, 458),
        ("small", 2, 882),
        ("mini", 3, 1280),
    ]
    size_buttons = {}
    for label, size_value, x in size_labels:
        add_text(hwnd, size_panel, f"{label} 尺寸", x, 74, 120, 24, MUTED)
        dd = make_dropdown(size_panel, label, action_items, x, 102, 180, 36)
        ui.set_dropdown_options(hwnd, dd, trigger_mode=0, hide_on_click=True, split_button=True, button_variant=1, size=size_value, trigger_style=0)
        size_buttons[size_value] = dd
    size_note = add_text(hwnd, size_panel, "四种尺寸会一起缩放触发器字体、内边距和菜单行高。", 34, 162, w - 120, 24, MUTED)
    ui.set_text_options(hwnd, size_note, wrap=True, ellipsis=False)

    legend = ui.create_descriptions(
        hwnd, readback_panel, "📚 枚举说明",
        [
            ("触发模式", "0 点击 / 1 悬停 / 2 手动"),
            ("触发器样式", "0 按钮 / 1 文字链接"),
            ("按钮变体", "0 默认 / 1 主色 / 2 成功 / 3 警告 / 4 危险 / 5 文本 / 6 信息"),
            ("尺寸", "0 默认 / 1 medium / 2 small / 3 mini"),
            ("元数据", "icon / command / divided / disabled / level"),
        ],
        2, True, 34, 74, w - 220, 104,
    )
    ui.set_descriptions_options(hwnd, legend, columns=2, bordered=True, label_width=108, min_row_height=30, wrap_values=True)

    readback_button = ui.create_button(hwnd, readback_panel, "🔄", "刷新读回", w - 180, 74, 128, 36)
    readback_text = add_text(hwnd, readback_panel, "📘 状态读回：等待刷新", 34, 142, w - 80, 40, TEXT)
    ui.set_text_options(hwnd, readback_text, wrap=True, ellipsis=False)

    state = {
        "command_text": "等待选择",
        "command_item": -1,
        "main_clicks": 0,
    }

    def refresh_readback(_eid=None):
        opts = ui.get_dropdown_options(hwnd, keep_open)
        info = ui.get_dropdown_state(hwnd, keep_open)
        meta3 = ui.get_dropdown_item_meta(hwnd, meta_dropdown, 2)
        meta6 = ui.get_dropdown_item_meta(hwnd, meta_dropdown, 5)
        scroll_state = ui.get_dropdown_state(hwnd, scroll_dropdown)
        ui.set_element_text(
            hwnd, readback_text,
            "保持展开："
            f"trigger={opts['trigger_mode']} hide={opts['hide_on_click']} split={opts['split_button']} "
            f"variant={opts['button_variant']} size={opts['size']} style={opts['trigger_style']}\n"
            f"状态：selected={info['selected']} count={info['count']} disabled={info['disabled']} "
            f"level={info['level']} hover={info['hover']}\n"
            f"第 3 项：icon={meta3['icon']} command={meta3['command']} divided={meta3['divided']} "
            f"disabled={meta3['disabled']} level={meta3['level']}\n"
            f"第 6 项：icon={meta6['icon']} command={meta6['command']} divided={meta6['divided']} "
            f"disabled={meta6['disabled']} level={meta6['level']}\n"
            f"长列表：count={scroll_state['count']} disabled={scroll_state['disabled']}"
        )

    @ui.DropdownCommandCallback
    def on_command(element_id, item_index, command_ptr, command_len):
        command = ""
        if command_ptr and command_len > 0:
            command = ctypes.string_at(command_ptr, command_len).decode("utf-8", errors="replace")
        state["command_text"] = command
        state["command_item"] = item_index
        ui.set_element_text(hwnd, command_status, f"📨 最近命令：#{element_id} 第 {item_index + 1} 项 → {command}")
        refresh_readback()

    @ui.ClickCallback
    def on_main_click(element_id):
        state["main_clicks"] += 1
        ui.set_element_text(hwnd, main_status, f"🧭 主按钮：#{element_id} 已点击 {state['main_clicks']} 次")
        refresh_readback()

    @ui.ClickCallback
    def on_toggle_manual(_element_id):
        now_open = not ui.get_dropdown_open(hwnd, manual_menu)
        ui.set_dropdown_open(hwnd, manual_menu, now_open)
        ui.set_element_text(hwnd, manual_status, f"🧭 手动菜单：{'已打开' if now_open else '已关闭'}")
        refresh_readback()

    keep_callback(on_command)
    keep_callback(on_main_click)
    keep_callback(on_toggle_manual)
    ui.set_dropdown_command_callback(hwnd, keep_open, on_command)
    ui.set_dropdown_command_callback(hwnd, manual_menu, on_command)
    ui.set_dropdown_command_callback(hwnd, meta_dropdown, on_command)
    ui.set_dropdown_command_callback(hwnd, scroll_dropdown, on_command)
    ui.set_dropdown_command_callback(hwnd, split_menu, on_command)
    ui.set_dropdown_main_click_callback(hwnd, split_menu, on_main_click)
    set_click(hwnd, toggle_manual, on_toggle_manual)
    set_click(hwnd, readback_button, lambda _eid: refresh_readback())

    ui.set_dropdown_open(hwnd, keep_open, True)
    ui.set_dropdown_open(hwnd, meta_dropdown, True)
    ui.set_dropdown_open(hwnd, scroll_dropdown, True)
    ui.set_dropdown_open(hwnd, split_menu, True)
    refresh_readback()

    add_text(hwnd, behavior_panel, "保持展开会让菜单项点击后不自动收起，适合连续选择。", 34, 368, 720, 24, MUTED)
    add_text(hwnd, behavior_panel, "手动模式只响应程序开关，适合复杂流程或外部控制。", 34, 392, 720, 24, MUTED)
    add_text(hwnd, button_panel, "同一组菜单动作，仅切换 button_variant 就能覆盖常见桌面风格。", 34, 224, 720, 24, MUTED)


def showcase_menu(hwnd, stage, w, h):
    add_text(
        hwnd, stage,
        "🧭 Menu / NavMenu 覆盖横向默认、横向暗色、纵向默认、纵向暗色、多级子菜单、分组、禁用、链接项和侧栏收起。",
        36, 28, w - 72, 28, MUTED,
    )

    top_panel = add_demo_panel(hwnd, stage, "🧭 顶部横向导航", 28, 70, w - 56, 230)
    side_panel = add_demo_panel(hwnd, stage, "📚 侧边导航与分组", 28, 324, 820, 520)
    collapse_panel = add_demo_panel(hwnd, stage, "📌 收起侧栏", 872, 324, 330, 520)
    state_panel = add_demo_panel(hwnd, stage, "📋 状态读回", 1228, 324, w - 1256, 520)

    top_items = ["处理中心", "我的工作台", "> 选项1", "> 选项2", "> 选项3", "!消息中心", "订单管理"]
    side_items = [
        "导航一",
        "> 分组一",
        "> > 选项1",
        "> > 选项2",
        "> 分组二",
        "> > 选项3",
        "> 选项4",
        "> > 选项1",
        "导航二",
        "!导航三",
        "导航四",
    ]

    def apply_nav_meta(menu_id, items, groups=None, href_index=None):
        groups = groups or []
        icons = [""] * len(items)
        hrefs = [""] * len(items)
        targets = [""] * len(items)
        commands = [""] * len(items)
        for i, text in enumerate(items):
            clean = text.replace(">", "").replace("!", "").strip()
            if "处理" in clean or "首页" in clean:
                icons[i] = "🏠"
            elif "工作台" in clean or "导航一" in clean:
                icons[i] = "🧭"
            elif "消息" in clean:
                icons[i] = "💬"
            elif "订单" in clean:
                icons[i] = "🧾"
            elif "导航二" in clean:
                icons[i] = "📊"
            elif "导航三" in clean:
                icons[i] = "📄"
            elif "导航四" in clean:
                icons[i] = "⚙️"
            elif "选项" in clean:
                icons[i] = "•"
            commands[i] = f"menu_{i}"
        if href_index is not None:
            hrefs[href_index] = "https://www.ele.me"
            targets[href_index] = "_blank"
            commands[href_index] = "open_orders"
        ui.set_menu_item_meta(hwnd, menu_id, icons, groups, hrefs, targets, commands)

    add_text(hwnd, top_panel, "默认颜色", 32, 48, 160, 24, MUTED)
    default_top = ui.create_menu(hwnd, top_panel, top_items, 0, 0, 32, 78, 760, 48)
    apply_nav_meta(default_top, top_items, href_index=6)

    add_text(hwnd, top_panel, "自定义暗色", 836, 48, 160, 24, MUTED)
    dark_top = ui.create_menu(hwnd, top_panel, top_items, 0, 0, 836, 78, 760, 48)
    ui.set_menu_colors(hwnd, dark_top, 0xFF545C64, 0xFFFFFFFF, 0xFFFFD04B, 0xFF646E78, 0xFF9CA3AF, 0xFF545C64)
    apply_nav_meta(dark_top, top_items, href_index=6)

    add_text(hwnd, top_panel, "横向菜单保持桌面工具栏高度，激活项以下划线强调，禁用项会跳过选择。", 32, 154, w - 160, 28, MUTED)

    add_text(hwnd, side_panel, "默认颜色", 32, 48, 160, 24, MUTED)
    default_side = ui.create_menu(hwnd, side_panel, side_items, 2, 1, 32, 78, 230, 390)
    apply_nav_meta(default_side, side_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, default_side, [0, 6])
    ui.set_menu_active(hwnd, default_side, 2)

    add_text(hwnd, side_panel, "自定义暗色", 300, 48, 160, 24, MUTED)
    dark_side = ui.create_menu(hwnd, side_panel, side_items, 8, 1, 300, 78, 230, 390)
    ui.set_menu_colors(hwnd, dark_side, 0xFF545C64, 0xFFFFFFFF, 0xFFFFD04B, 0xFF646E78, 0xFF9CA3AF, 0xFF545C64)
    apply_nav_meta(dark_side, side_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, dark_side, [0, 6])
    ui.set_menu_active(hwnd, dark_side, 8)

    add_text(hwnd, side_panel, "多级分组", 568, 48, 160, 24, MUTED)
    group_side = ui.create_menu(hwnd, side_panel, side_items, 5, 1, 568, 78, 220, 390)
    apply_nav_meta(group_side, side_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, group_side, [0, 6])
    ui.set_menu_active(hwnd, group_side, 5)

    collapsed_menu = ui.create_menu(hwnd, collapse_panel, side_items, 8, 1, 36, 72, 72, 390)
    apply_nav_meta(collapsed_menu, side_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, collapsed_menu, [0, 6])
    ui.set_menu_active(hwnd, collapsed_menu, 8)
    ui.set_menu_collapsed(hwnd, collapsed_menu, True)
    full_menu = ui.create_menu(hwnd, collapse_panel, side_items, 8, 1, 132, 72, 170, 390)
    apply_nav_meta(full_menu, side_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, full_menu, [0, 6])
    ui.set_menu_active(hwnd, full_menu, 8)

    state_text = add_text(hwnd, state_panel, "🧭 最近选择：等待点击菜单项", 28, 52, w - 1320, 36, TEXT)
    readback_text = add_text(hwnd, state_panel, "📌 状态：等待读回", 28, 92, w - 1320, 82, MUTED)
    meta_text = add_text(hwnd, state_panel, "🔗 链接项：订单管理 -> https://www.ele.me", 28, 178, w - 1320, 54, MUTED)

    def refresh_state():
        state = ui.get_menu_state(hwnd, group_side)
        path = ui.get_menu_active_path(hwnd, group_side)
        colors = ui.get_menu_colors(hwnd, dark_top)
        collapsed = ui.get_menu_collapsed(hwnd, collapsed_menu)
        link_meta = ui.get_menu_item_meta(hwnd, default_top, 6)
        ui.set_element_text(
            hwnd, readback_text,
            f"📌 激活={state['active']} 路径={path} 方向={state['orientation']} 可见={state['visible']} 展开={state['expanded']} 收起={collapsed}"
        )
        ui.set_element_text(
            hwnd, meta_text,
            f"🔗 链接={link_meta['href']} 目标={link_meta['target']} 颜色={tuple(hex(c) for c in colors[:3])}"
        )

    @ui.MenuSelectCallback
    def on_menu_select(element_id, item_index, path_ptr, path_len, command_ptr, command_len):
        path = bytes(path_ptr[:path_len]).decode("utf-8", errors="replace") if path_len > 0 else ""
        command = bytes(command_ptr[:command_len]).decode("utf-8", errors="replace") if command_len > 0 else ""
        ui.set_element_text(hwnd, state_text, f"🧭 最近选择：菜单 {element_id} / 第 {item_index} 项 / {path} / {command}")
        refresh_state()

    keep_callback(on_menu_select)
    for mid in (default_top, dark_top, default_side, dark_side, group_side, collapsed_menu, full_menu):
        ui.set_menu_select_callback(hwnd, mid, on_menu_select)

    toggle_btn = ui.create_button(hwnd, collapse_panel, "↔", "切换收起", 36, 472, 130, 36)
    read_btn = ui.create_button(hwnd, state_panel, "🔄", "读回状态", 28, 260, 130, 36)

    def toggle_collapsed(_eid):
        now = not ui.get_menu_collapsed(hwnd, collapsed_menu)
        ui.set_menu_collapsed(hwnd, collapsed_menu, now)
        refresh_state()

    set_click(hwnd, toggle_btn, toggle_collapsed)
    set_click(hwnd, read_btn, lambda _eid: refresh_state())
    refresh_state()


def _infinite_demo_items(prefix, count, tag, start=1):
    owners = ["设计组", "研发组", "测试组", "运营组"]
    rows = []
    for i in range(start, start + count):
        owner = owners[(i - 1) % len(owners)]
        rows.append((
            f"📌 {prefix} {i:02d}",
            f"{owner} · 更新时间 09:{(i * 7) % 60:02d} · 双击可进入详情",
            tag,
        ))
    return rows


def showcase_infinite_scroll(hwnd, stage, w, h):
    add_text(
        hwnd, stage,
        "♾️ InfiniteScroll 覆盖基础无限追加、加载中、禁用、没有更多、空状态、卡片列表、紧凑业务列表和状态读回。",
        36, 28, w - 72, 28, MUTED,
    )

    nav = add_demo_panel(hwnd, stage, "🧭 桌面端样式导航", 28, 70, 250, 500)
    main = add_demo_panel(hwnd, stage, "♾️ 触底加载与状态读回", 300, 70, 650, 500)
    cards = add_demo_panel(hwnd, stage, "🪪 卡片列表", 980, 70, w - 1008, 240)
    compact = add_demo_panel(hwnd, stage, "🧾 紧凑业务列表", 980, 330, w - 1008, 240)
    states = add_demo_panel(hwnd, stage, "⏳ 状态矩阵", 28, 600, w - 56, 230)
    readback = add_demo_panel(hwnd, stage, "📚 状态说明", 28, 860, w - 56, 170)

    add_text(hwnd, nav, "常见桌面软件会把长数据流放在主工作区，旁边保留筛选、状态和快捷动作。", 24, 66, 200, 70, MUTED)
    add_text(hwnd, nav, "当前页使用同一个原生组件演示四种列表密度与三类结束状态。", 24, 156, 200, 58, MUTED)

    main_list = ui.create_infinite_scroll(
        hwnd, main,
        _infinite_demo_items("发布任务", 10, "进行中"),
        24, 78, 596, 306,
    )
    ui.set_infinite_scroll_options(hwnd, main_list, item_height=62, gap=8, threshold=96,
                                   style_mode=3, show_scrollbar=True, show_index=True)
    ui.set_infinite_scroll_texts(hwnd, main_list, "⏳ 正在加载下一批记录...", "✅ 没有更多任务了", "📭 暂无任务")

    status = add_text(hwnd, main, "📘 状态读回：等待触发", 24, 398, 596, 28, TEXT)
    ui.set_text_options(hwnd, status, wrap=True, ellipsis=False)

    state = {"manual": 0, "disabled": False}

    def refresh_state(_eid=None):
        info = ui.get_infinite_scroll_full_state(hwnd, main_list) or {}
        ui.set_element_text(
            hwnd, status,
            "📘 状态读回："
            f"项目 {info.get('item_count', 0)} · 滚动 {info.get('scroll_y', 0)}/{info.get('max_scroll', 0)} · "
            f"加载 {info.get('loading', False)} · 到底 {info.get('no_more', False)} · "
            f"禁用 {info.get('disabled', False)} · 触发 {info.get('load_count', 0)}"
        )

    @ui.ValueCallback
    def on_load(element_id, item_count, scroll_y, max_scroll):
        if item_count >= 18:
            ui.set_infinite_scroll_state(hwnd, element_id, loading=False, no_more=True, disabled=False)
        else:
            ui.append_infinite_scroll_items(
                hwnd, element_id,
                _infinite_demo_items("追加任务", 4, "新加载", item_count + 1),
            )
            ui.set_infinite_scroll_state(hwnd, element_id, loading=False, no_more=False, disabled=False)
        refresh_state()

    keep_callback(on_load)
    ui.set_infinite_scroll_load_callback(hwnd, main_list, on_load)

    def scroll_to_bottom(_eid=None):
        ui.set_infinite_scroll_scroll(hwnd, main_list, 999999)
        refresh_state()

    def append_manual(_eid=None):
        state["manual"] += 1
        info = ui.get_infinite_scroll_full_state(hwnd, main_list) or {}
        ui.append_infinite_scroll_items(
            hwnd, main_list,
            _infinite_demo_items(f"手动补录 {state['manual']}", 2, "手动", info.get("item_count", 0) + 1),
        )
        ui.set_infinite_scroll_state(hwnd, main_list, loading=False, no_more=False, disabled=state["disabled"])
        refresh_state()

    def reset_main(_eid=None):
        state["manual"] = 0
        state["disabled"] = False
        ui.set_infinite_scroll_items(hwnd, main_list, _infinite_demo_items("发布任务", 10, "进行中"))
        ui.set_infinite_scroll_state(hwnd, main_list, loading=False, no_more=False, disabled=False)
        ui.set_infinite_scroll_scroll(hwnd, main_list, 0)
        refresh_state()

    def toggle_disabled(_eid=None):
        state["disabled"] = not state["disabled"]
        ui.set_infinite_scroll_state(hwnd, main_list, loading=False, no_more=False, disabled=state["disabled"])
        refresh_state()

    btn_bottom = ui.create_button(hwnd, main, "⬇️", "滚到底部", 24, 436, 126, 34)
    btn_append = ui.create_button(hwnd, main, "➕", "追加两项", 164, 436, 126, 34)
    btn_reset = ui.create_button(hwnd, main, "🔄", "重置列表", 304, 436, 126, 34)
    btn_disabled = ui.create_button(hwnd, main, "⏸️", "禁用加载", 444, 436, 126, 34)
    set_click(hwnd, btn_bottom, scroll_to_bottom)
    set_click(hwnd, btn_append, append_manual)
    set_click(hwnd, btn_reset, reset_main)
    set_click(hwnd, btn_disabled, toggle_disabled)

    card_list = ui.create_infinite_scroll(
        hwnd, cards,
        [
            ("🪪 客户工单 A-1024", "华东一区 · 今日 13:40 · 优先级高", "待确认"),
        ("🧩 组件回归清单", "88 个组件 · Release x64 构建", "检查中"),
            ("📦 物料同步任务", "3 个仓库 · 12 条记录", "已排队"),
        ],
        24, 70, max(220, w - 1068), 132,
    )
    ui.set_infinite_scroll_options(hwnd, card_list, item_height=62, gap=10, threshold=40,
                                   style_mode=1, show_scrollbar=True, show_index=False)
    ui.set_infinite_scroll_texts(hwnd, card_list, "⏳ 正在同步...", "✅ 卡片已经到底", "📭 暂无卡片")

    compact_list = ui.create_infinite_scroll(
        hwnd, compact,
        [
            ("🧾 订单 20260505001", "北京 · 已付款", "正常"),
            ("🧾 订单 20260505002", "上海 · 待开票", "提醒"),
            ("🧾 订单 20260505003", "深圳 · 售后跟进", "售后"),
            ("🧾 订单 20260505004", "杭州 · 等待出库", "仓库"),
        ],
        24, 70, max(220, w - 1068), 132,
    )
    ui.set_infinite_scroll_options(hwnd, compact_list, item_height=38, gap=0, threshold=32,
                                   style_mode=2, show_scrollbar=True, show_index=True)
    ui.set_infinite_scroll_texts(hwnd, compact_list, "⏳ 加载订单...", "✅ 订单到底", "📭 暂无订单")

    loading_list = ui.create_infinite_scroll(
        hwnd, states,
        _infinite_demo_items("加载状态", 3, "等待"),
        24, 70, 320, 122,
    )
    ui.set_infinite_scroll_options(hwnd, loading_list, item_height=44, gap=6, threshold=30,
                                   style_mode=0, show_scrollbar=False, show_index=False)
    ui.set_infinite_scroll_texts(hwnd, loading_list, "⏳ 加载中...", "✅ 没有更多了", "📭 暂无数据")
    ui.set_infinite_scroll_state(hwnd, loading_list, loading=True, no_more=False, disabled=False)

    no_more_list = ui.create_infinite_scroll(
        hwnd, states,
        _infinite_demo_items("归档记录", 2, "完成"),
        374, 70, 320, 122,
    )
    ui.set_infinite_scroll_options(hwnd, no_more_list, item_height=42, gap=6, threshold=30,
                                   style_mode=3, show_scrollbar=False, show_index=True)
    ui.set_infinite_scroll_texts(hwnd, no_more_list, "⏳ 读取归档...", "✅ 没有更多归档", "📭 暂无归档")
    ui.set_infinite_scroll_state(hwnd, no_more_list, loading=False, no_more=True, disabled=False)

    disabled_list = ui.create_infinite_scroll(
        hwnd, states,
        _infinite_demo_items("冻结队列", 3, "暂停"),
        724, 70, 320, 122,
    )
    ui.set_infinite_scroll_options(hwnd, disabled_list, item_height=40, gap=6, threshold=30,
                                   style_mode=2, show_scrollbar=True, show_index=False)
    ui.set_infinite_scroll_texts(hwnd, disabled_list, "⏳ 等待恢复...", "✅ 队列到底", "📭 暂无队列")
    ui.set_infinite_scroll_state(hwnd, disabled_list, loading=False, no_more=False, disabled=True)

    empty_list = ui.create_infinite_scroll(hwnd, states, [], 1074, 70, 320, 122)
    ui.set_infinite_scroll_options(hwnd, empty_list, item_height=44, gap=8, threshold=30,
                                   style_mode=0, show_scrollbar=False, show_index=False)
    ui.set_infinite_scroll_texts(hwnd, empty_list, "⏳ 正在加载...", "✅ 没有更多了", "📭 当前筛选没有数据")

    ui.create_descriptions(
        hwnd, readback, "📚 API 覆盖",
        [
            ("创建", "EU_CreateInfiniteScroll"),
            ("数据", "设置 / 追加 / 清空项目"),
            ("状态", "loading / no_more / disabled"),
            ("滚动", "滚轮、拖拽、轨道、Home/End/PageUp/PageDown"),
            ("样式", "item_height / gap / threshold / style_mode / index"),
            ("回调", "触底后自动 loading，回调追加数据后结束加载"),
        ],
        2, True, 24, 64, w - 112, 82,
    )
    refresh_state()


def showcase_card(hwnd, stage, w, h):
    wide, tall, small = image_sample_files()
    status = add_text(hwnd, stage, "🪪 Card 卡片：基础、头部操作、正文列表、图片卡片、阴影和桌面业务卡片都由 C++ Card + 子元素插槽完成。", 36, 28, w - 72, 28, MUTED)

    def card_click(label):
        def action(element_id):
            ui.set_element_text(hwnd, status, f"🪪 最近操作：{label} · 卡片操作索引 {ui.get_card_action(hwnd, element_id)}")
        return action

    basics = add_demo_panel(hwnd, stage, "🧩 基础、无头与页脚操作", 28, 70, w - 56, 238)
    basic = ui.create_card(hwnd, basics, "🧩 基础卡片", "用于承载一组说明、状态或快捷入口。", 1, 28, 66, 300, 132)
    no_header = ui.create_card(hwnd, basics, "", "只有正文的轻量卡片，适合密集信息区。", 0, 352, 66, 300, 132)
    action_card = ui.create_card(hwnd, basics, "📌 发布卡片", "页脚区域支持多个可点击操作。", 2, 676, 66, 360, 132)
    ui.set_card_footer(hwnd, action_card, "最近更新：2026-05-06")
    ui.set_card_actions(hwnd, action_card, ["查看", "同步", "归档"])
    ui.set_card_options(hwnd, action_card, shadow=2, hoverable=True)
    set_click(hwnd, action_card, card_click("页脚按钮"))
    add_text(hwnd, basics, "shadow：always / never / hover", 1068, 108, 260, 28, MUTED)
    add_text(hwnd, basics, f"读回：{ui.get_card_options(hwnd, action_card)}", 1068, 148, 260, 28, MUTED)

    header = add_demo_panel(hwnd, stage, "🎛️ Header 插槽：标题 + 右侧操作按钮", 28, 334, 520, 230)
    header_card = ui.create_card(hwnd, header, "🪪 卡片名称", "", 1, 28, 66, 420, 132)
    ui.set_card_items(hwnd, header_card, ["📄 列表内容 1", "📄 列表内容 2", "📄 列表内容 3"])
    ui.set_card_body_style(hwnd, header_card, 18, 12, 18, 12, 14.0, 8, 0, False)
    op = ui.create_button(hwnd, header_card, "", "操作按钮", 318, 9, 82, 28, variant=5)
    set_click(hwnd, op, lambda _eid: ui.set_element_text(hwnd, status, "🪪 最近操作：头部右侧操作按钮"))

    lists = add_demo_panel(hwnd, stage, "📋 正文列表：margin 与 padding 两种桌面密度", 580, 334, w - 608, 230)
    margin_card = ui.create_card(hwnd, lists, "", "", 1, 28, 66, 300, 132)
    ui.set_card_items(hwnd, margin_card, ["📄 列表内容 1", "📄 列表内容 2", "📄 列表内容 3", "📄 列表内容 4"])
    ui.set_card_body_style(hwnd, margin_card, 18, 18, 18, 18, 14.0, 18, 0, False)
    padding_card = ui.create_card(hwnd, lists, "", "", 1, 356, 66, 300, 132)
    ui.set_card_items(hwnd, padding_card, ["✅ 列表内容 1", "✅ 列表内容 2", "✅ 列表内容 3", "✅ 列表内容 4"])
    ui.set_card_body_style(hwnd, padding_card, 18, 0, 18, 0, 14.0, 0, 18, True)
    add_text(hwnd, lists, "左：item_gap=18；右：item_padding_y=18 + divider", 690, 112, 420, 28, MUTED)
    add_text(hwnd, lists, f"列表读回：{ui.get_card_item_count(hwnd, padding_card)} 项", 690, 150, 260, 28, MUTED)

    media = add_demo_panel(hwnd, stage, "🍔 body-style=0 的图片卡片", 28, 590, w - 56, 270)
    food = ui.create_image_card(hwnd, media, wide, "🍔 好吃的汉堡", "2026-05-06 09:30", "操作按钮", 1, 28, 62, 300, 182)
    poster = ui.create_image_card(hwnd, media, tall, "🖼️ 竖向海报", "图片适配 cover", "预览", 1, 352, 62, 260, 182)
    material = ui.create_image_card(hwnd, media, small, "📦 物料缩略图", "可组合 Image/Text/Button", "入库", 2, 636, 62, 300, 182)
    ui.set_card_style(hwnd, food, 0xFFFFFFFF, 0xFFDDE5F2, 1.0, 6.0, 0)
    ui.set_card_style(hwnd, poster, 0xFFFFFFFF, 0xFFDDE5F2, 1.0, 6.0, 0)
    ui.set_card_style(hwnd, material, 0xFFFFFFFF, 0xFFDDE5F2, 1.0, 6.0, 0)
    add_text(hwnd, media, "这些图片卡片使用真实 Card 作为父元素，Image、Text、Button 是子元素插槽。", 976, 112, 520, 48, MUTED)

    business = add_demo_panel(hwnd, stage, "🧭 桌面端业务卡片", 28, 886, w - 56, 216)
    cards = [
        ("🛡️ 审批中心", "待审批 12 项\n高优先级 3 项", 0xFFEBF5FF, 0xFF78A8F8, ["处理"]),
        ("🧾 工单队列", "今日新增 28 条\n平均响应 14 分钟", 0xFFFFF7E7, 0xFFF1B85B, ["查看", "分派"]),
        ("📚 资料卡片", "产品文档 88 篇\n同步状态正常", 0xFFEAF8EF, 0xFF69C587, ["打开"]),
        ("📦 物料卡片", "库存预警 6 项\n等待补货确认", 0xFFF8FBFF, 0xFFB6C6DE, ["详情"]),
    ]
    card_w = max(240, (w - 128) // 4)
    for i, (title, body, bg, border, actions) in enumerate(cards):
        x = 28 + i * (card_w + 18)
        cid = ui.create_card(hwnd, business, title, body, 2 if i == 1 else 1, x, 62, card_w, 126)
        ui.set_card_style(hwnd, cid, bg, border, 1.0, 8.0, 16)
        ui.set_card_body_style(hwnd, cid, 16, 12, 16, 12, 14.0, 0, 0, False)
        ui.set_card_actions(hwnd, cid, actions)
        set_click(hwnd, cid, card_click(title))


def showcase_collapse(hwnd, stage, w, h):
    add_text(hwnd, stage, "📂 Collapse 折叠面板：多展开、手风琴、自定义标题、禁用项和状态读回都由 C++ Collapse 原生渲染。", 36, 28, w - 72, 28, MUTED)
    col_w = max(520, (w - 84) // 2)
    right_x = 56 + col_w
    right_w = max(420, w - right_x - 28)

    multi_panel = add_demo_panel(hwnd, stage, "📚 基础多展开：activeNames 数组", 28, 70, col_w, 330)
    multi_items = [
        ("一致性 Consistency", "与现实生活一致：流程、逻辑保持一致，遵循用户习惯的语言和概念。\n在界面中一致：设计样式、图标、文本和元素位置保持一致。", "🎯", "已展开", 0),
        ("反馈 Feedback", "控制反馈：通过界面样式和交互动效让用户清晰感知自己的操作。\n页面反馈：操作后通过页面元素变化展现当前状态。", "💬", "已展开", 0),
        ("效率 Efficiency", "简化流程：设计简洁直观的操作流程。\n清晰明确：语言表达清晰且表意明确，让用户快速理解并决策。", "⚡", "可展开", 0),
        ("可控 Controllability", "用户决策：给予操作建议或安全提示，但不代替用户决策。\n结果可控：用户可以撤销、回退或终止当前操作。", "🛡️", "可展开", 0),
    ]
    multi = ui.create_collapse(hwnd, multi_panel, multi_items, active=[0, 1], accordion=False, x=24, y=64, w=col_w - 48, h=240)
    ui.set_collapse_options(hwnd, multi, accordion=False, allow_collapse=True, animated=True)

    accordion_panel = add_demo_panel(hwnd, stage, "🪗 手风琴模式：accordion", right_x, 70, right_w, 330)
    accordion = ui.create_collapse(
        hwnd, accordion_panel,
        [
            ("反馈面板", "一次只展开一个区域，适合设置页左侧摘要或帮助中心目录。", "📣", "当前", 0),
            ("效率面板", "点击其他标题时，当前展开项会自动收起。", "⚙️", "候选", 0),
            ("可控面板", "allow_collapse=False 时，已展开项再次点击不会关闭。", "🔒", "锁定", 0),
        ],
        active=0, accordion=True, x=24, y=64, w=right_w - 48, h=220
    )
    ui.set_collapse_options(hwnd, accordion, accordion=True, allow_collapse=False, animated=True)

    custom_panel = add_demo_panel(hwnd, stage, "🎛️ 自定义标题：图标、右侧信息和禁用项", 28, 428, w - 56, 300)
    custom = ui.create_collapse(
        hwnd, custom_panel,
        [
            {"title": "组件规范", "body": "标题区支持 emoji 图标和右侧状态说明，可直接呈现桌面软件里的设置分组。", "icon": "🧩", "suffix": "说明"},
            {"title": "禁用分组", "body": "这个项目禁用，仅展示弱化标题，不响应点击和键盘切换。", "icon": "🚫", "suffix": "禁用", "disabled": True},
            {"title": "发布检查", "body": "正文支持显式换行。\n可用于列出检查项、注意事项或折叠式表单说明。", "icon": "✅", "suffix": "2 项"},
        ],
        active=[0, 2], accordion=False, x=24, y=64, w=w - 104, h=210
    )
    ui.set_collapse_options(hwnd, custom, accordion=False, allow_collapse=True, disabled_indices=[1], animated=True)

    state_panel = add_demo_panel(hwnd, stage, "📤 状态读回与桌面端操作", 28, 756, w - 56, 230)
    state_text = add_text(hwnd, state_panel, "📋 当前状态：等待操作", 28, 70, w - 112, 28, TEXT)
    details = add_text(hwnd, state_panel, "多展开面板读取 activeIndices；手风琴面板读取 activeIndex；自定义面板读取禁用项和标题扩展字段。", 28, 110, w - 112, 28, MUTED)

    def refresh_state(label="刷新状态"):
        multi_state = ui.get_collapse_state_json(hwnd, multi)
        acc_state = ui.get_collapse_state_json(hwnd, accordion)
        custom_state = ui.get_collapse_state_json(hwnd, custom)
        ui.set_element_text(hwnd, state_text, f"📋 {label}：多展开={multi_state.get('activeIndices')} 手风琴={acc_state.get('activeIndex')} 自定义禁用={custom_state.get('disabledIndices')}")
        ui.set_element_text(hwnd, details, f"选项读回：{ui.get_collapse_options(hwnd, custom)}；激活列表：{ui.get_collapse_active_items(hwnd, multi)}")

    buttons = [
        ("📚", "展开全部", lambda _eid: (ui.set_collapse_active_items(hwnd, multi, [0, 1, 2, 3]), refresh_state("展开全部"))),
        ("💬", "只看反馈", lambda _eid: (ui.set_collapse_active_items(hwnd, multi, [1]), refresh_state("只看反馈"))),
        ("🪗", "切换手风琴", lambda _eid: (ui.set_collapse_options(hwnd, multi, accordion=True, allow_collapse=True, animated=True), ui.set_collapse_active_items(hwnd, multi, [2]), refresh_state("切换手风琴"))),
        ("📤", "读取状态", lambda _eid: refresh_state("读取状态")),
    ]
    for i, (emoji, text, action) in enumerate(buttons):
        btn = ui.create_button(hwnd, state_panel, emoji, text, 28 + i * 150, 154, 132, 42)
        set_click(hwnd, btn, action)
    refresh_state("初始状态")


def showcase_tabs(hwnd, stage, w, h):
    common_items = [
        {"label": "用户管理", "name": "users", "content": "👥 用户列表、权限状态和最近登录记录集中在这里。", "icon": "👥"},
        {"label": "配置管理", "name": "config", "content": "⚙️ 系统配置、主题、通知策略和安全选项。", "icon": "⚙️"},
        {"label": "角色管理", "name": "roles", "content": "🛡️ 角色授权、菜单访问范围和数据权限。", "icon": "🛡️"},
        {"label": "定时任务补偿", "name": "jobs", "content": "⏰ 失败任务补偿、重试队列和执行日志。", "icon": "⏰"},
    ]

    top = add_demo_panel(hwnd, stage, "📑 默认线形与卡片式", 28, 30, w - 56, 170)
    ui.create_tabs_ex(hwnd, top, common_items, active=1, tab_type=0, tab_position="top",
                      content_visible=True, x=28, y=62, w=(w - 140) // 2, h=82)
    ui.create_tabs_ex(hwnd, top, [
        {"label": "预览", "name": "preview", "content": "🖥️ 当前窗口预览与状态面板。", "icon": "🖥️"},
        {"label": "代码", "name": "code", "content": "🧩 C++ 与 Python 封装片段。", "icon": "🧩"},
        {"label": "文档", "name": "docs", "content": "📚 组件文档和易语言命令说明。", "icon": "📚"},
        {"label": "设置", "name": "settings", "content": "⚙️ 工具栏、主题和布局设置。", "icon": "⚙️"},
    ], active=0, tab_type=1, tab_position="top", content_visible=True,
        x=(w - 140) // 2 + 56, y=62, w=(w - 140) // 2, h=82)

    border = add_demo_panel(hwnd, stage, "🧾 边框卡片、图标标签与禁用项", 28, 220, w - 56, 205)
    ui.create_tabs_ex(hwnd, border, [
        {"label": "我的行程", "name": "trip", "content": "📅 今天 14:00 评审会议；16:30 发布检查。", "icon": "📅"},
        {"label": "消息中心", "name": "message", "content": "💬 3 条待处理消息，2 条来自构建服务。", "icon": "💬"},
        {"label": "角色管理", "name": "role", "content": "🛡️ 当前角色：管理员、审核员、观察者。", "icon": "🛡️"},
        {"label": "禁用标签", "name": "locked", "content": "🔒 此标签不可选择。", "icon": "🔒", "disabled": True},
    ], active=0, tab_type=2, tab_position="top", closable=True, content_visible=True,
        x=28, y=64, w=w - 112, h=112)

    positions = add_demo_panel(hwnd, stage, "🧭 桌面设置页四方向标签", 28, 454, w - 56, 300)
    settings_items = [
        {"label": "概览", "name": "overview", "content": "🏠 账户、设备和同步状态。", "icon": "🏠"},
        {"label": "安全", "name": "security", "content": "🔐 登录保护、密钥和设备信任。", "icon": "🔐"},
        {"label": "通知", "name": "notice", "content": "🔔 消息提醒、声音和免打扰。", "icon": "🔔"},
    ]
    ui.create_tabs_ex(hwnd, positions, settings_items, active=0, tab_type=2, tab_position="left",
                      content_visible=True, x=28, y=64, w=330, h=180)
    ui.create_tabs_ex(hwnd, positions, settings_items, active=1, tab_type=2, tab_position="right",
                      content_visible=True, x=384, y=64, w=330, h=180)
    ui.create_tabs_ex(hwnd, positions, settings_items, active=2, tab_type=1, tab_position="bottom",
                      content_visible=True, x=740, y=64, w=390, h=180)
    ui.create_tabs_ex(hwnd, positions, settings_items, active=0, tab_type=0, tab_position="top",
                      content_visible=True, x=1156, y=64, w=max(300, w - 1240), h=180)

    edit = add_demo_panel(hwnd, stage, "✏️ 可编辑标签与多文档工作区", 28, 784, w - 56, 220)
    workspace = ui.create_tabs_ex(hwnd, edit, [
        {"label": "订单看板", "name": "orders", "content": "📦 订单看板：待处理 18，配送中 42。", "icon": "📦"},
        {"label": "客户资料", "name": "customers", "content": "👤 客户资料：最近更新 2026-05-05。", "icon": "👤"},
        {"label": "报表中心", "name": "reports", "content": "📊 报表中心：本周营收增长 12%。", "icon": "📊"},
        {"label": "发布日志", "name": "release", "content": "🚀 发布日志：Tabs 全样式封装。", "icon": "🚀"},
        {"label": "巡检记录", "name": "audit", "content": "✅ 巡检记录：所有核心服务正常。", "icon": "✅"},
    ], active=0, tab_type=1, tab_position="top", closable=True, addable=True,
        editable=True, content_visible=True, x=28, y=64, w=w - 260, h=118)
    add_btn = ui.create_button(hwnd, edit, "➕", "新增工作页", w - 206, 70, 150, 38)
    close_btn = ui.create_button(hwnd, edit, "✖️", "关闭当前页", w - 206, 122, 150, 38)
    set_click(hwnd, add_btn, lambda _eid: ui.add_tabs_item(hwnd, workspace, "✨ 临时任务"))
    set_click(hwnd, close_btn, lambda _eid: ui.close_tabs_item(hwnd, workspace, ui.get_tabs_full_state_ex(hwnd, workspace)["active_index"]))


def tree_gallery_data():
    return {
        "props": {"label": "name", "children": "zones", "isLeaf": "leaf"},
        "defaultExpandedKeys": ["root", "design", "remote"],
        "defaultCheckedKeys": ["tree", "table"],
        "currentKey": "tree",
        "data": [
            {
                "key": "root",
                "name": "📦 产品工作台",
                "icon": "📦",
                "tag": "根目录",
                "actions": "查看|新增",
                "zones": [
                    {
                        "key": "design",
                        "name": "🎨 设计资源",
                        "icon": "🎨",
                        "tag": "默认展开",
                        "actions": "追加|删除",
                        "zones": [
                            {"key": "button", "name": "🚀 按钮规范", "leaf": True, "tag": "完成"},
                            {"key": "tree", "name": "🌳 Tree 高级样式", "leaf": True, "tag": "选中"},
                            {"key": "disabled", "name": "🔒 冻结节点", "leaf": True, "disabled": True},
                        ],
                    },
                    {
                        "key": "data",
                        "name": "📊 数据组件",
                        "icon": "📊",
                        "zones": [
                            {"key": "table", "name": "📋 表格联动", "leaf": True, "tag": "半选"},
                            {"key": "chart", "name": "📈 图表看板", "leaf": True},
                        ],
                    },
                    {"key": "remote", "name": "⏳ 懒加载目录", "icon": "⏳", "lazy": True, "leaf": False},
                ],
            }
        ],
    }


def showcase_tree(hwnd, stage, w, h):
    left_w = 336
    bottom_h = 122
    body_h = h - bottom_h - 76
    left = add_demo_panel(hwnd, stage, "🧰 操作区", 28, 30, left_w, body_h)
    right = add_demo_panel(hwnd, stage, "🌳 Tree JSON 全样式", 388, 30, w - 416, body_h)
    readback = add_demo_panel(hwnd, stage, "📤 状态读回", 28, h - bottom_h - 26, w - 56, bottom_h)
    status_id = add_text(hwnd, readback, "", 20, 52, w - 96, 50, MUTED)

    main_tree = ui.create_tree_json(
        hwnd, right, tree_gallery_data(),
        options={
            "showCheckbox": True,
            "keyboardNavigation": True,
            "lazy": True,
            "accordion": False,
            "draggable": True,
            "showActions": True,
            "checkOnClickNode": True,
        },
        x=24, y=64, w=440, h=440,
    )
    ui.create_tree_json(
        hwnd, right,
        [
            {"key": "base", "label": "🌱 基础嵌套树", "expanded": True, "children": [
                {"key": "base-1", "label": "📄 默认展开", "leaf": True},
                {"key": "base-2", "label": "🔒 禁用项", "leaf": True, "disabled": True},
            ]},
            {"key": "accordion", "label": "🪗 手风琴分组", "children": [
                {"key": "accordion-a", "label": "同级只展开一个", "leaf": True},
            ]},
        ],
        options={"showCheckbox": False, "accordion": True, "draggable": True},
        x=500, y=64, w=330, h=210,
    )
    ui.create_tree_json(
        hwnd, right,
        {
            "filterText": "配置",
            "data": [
                {"key": "filter-root", "label": "🔎 过滤根节点", "expanded": True, "children": [
                    {"key": "filter-a", "label": "⚙️ 配置中心", "leaf": True, "tag": "匹配"},
                    {"key": "filter-b", "label": "📦 资源仓库", "leaf": True},
                ]},
            ],
        },
        options={"showCheckbox": True, "filterText": "配置", "showActions": True},
        x=500, y=304, w=330, h=200,
    )
    custom_tree = ui.create_tree_json(
        hwnd, right,
        [
            {"key": "template", "label": "🧩 自定义节点模板", "icon": "🧩", "tag": "桌面模板", "expanded": True, "actions": "打开|归档", "children": [
                {"key": "template-1", "label": "⭐ 图标 + 主文本 + 标签", "icon": "⭐", "tag": "右侧标签", "leaf": True, "actions": "处理"},
                {"key": "template-2", "label": "🧹 支持追加 / 删除 / 更新", "icon": "🧹", "leaf": True, "actions": "清理"},
            ]}
        ],
        options={"showCheckbox": True, "showActions": True},
        x=864, y=64, w=max(320, w - 1320), h=440,
    )
    ui.set_tree_checked_keys_json(hwnd, custom_tree, ["template-1"])

    add_text(hwnd, left, "🌳 主树覆盖：嵌套 JSON、props 映射、复选框、半选、默认 keys、禁用、懒加载、拖拽和固定节点模板。", 18, 54, left_w - 36, 82, MUTED)
    counter = [1]

    def refresh_state():
        state = ui.get_tree_state_json(hwnd, main_tree)
        ui.set_element_text(
            hwnd, status_id,
            f"当前 key：{state.get('currentKey')}  勾选：{state.get('checkedKeys')}  半选：{state.get('halfCheckedKeys')}\n"
            f"展开：{state.get('expandedKeys')}  懒加载索引：{state.get('lastLazyIndex')}  拖拽次数：{state.get('dragEventCount')}"
        )

    def lazy_loader(_eid, _code, _index, payload_ptr, payload_len):
        payload = ui.tree_callback_payload(payload_ptr, payload_len)
        if isinstance(payload, dict) and payload.get("key") == "remote":
            ui.append_tree_node_json(hwnd, main_tree, "remote", [
                {"key": "remote-api", "label": "🌐 远程接口", "leaf": True, "tag": "懒加载"},
                {"key": "remote-log", "label": "🧾 远程日志", "leaf": True},
            ])
        refresh_state()

    ui.set_tree_lazy_load_callback(hwnd, main_tree, lazy_loader)

    buttons = [
        ("📤", "读取状态", lambda _eid: refresh_state()),
        ("✅", "设置勾选", lambda _eid: (ui.set_tree_checked_keys_json(hwnd, main_tree, ["tree", "chart"]), refresh_state())),
        ("📂", "展开懒加载", lambda _eid: (ui.set_tree_expanded_keys_json(hwnd, main_tree, ["root", "remote"]), refresh_state())),
        ("🔎", "过滤配置", lambda _eid: (ui.set_tree_options_json(hwnd, main_tree, {"filterText": "资源"}), refresh_state())),
        ("🪗", "切换手风琴", lambda _eid: (ui.set_tree_options_json(hwnd, main_tree, {"accordion": True}), refresh_state())),
        ("➕", "追加节点", lambda _eid: (
            ui.append_tree_node_json(hwnd, main_tree, "design", {"key": f"new-{counter[0]}", "label": f"✨ 新任务 {counter[0]}", "leaf": True, "tag": "新增"}),
            counter.__setitem__(0, counter[0] + 1),
            refresh_state(),
        )),
        ("✏️", "更新节点", lambda _eid: (ui.update_tree_node_json(hwnd, main_tree, "tree", {"key": "tree", "label": "🌳 Tree 高级样式已更新", "leaf": True, "tag": "更新"}), refresh_state())),
        ("🧹", "删除追加", lambda _eid: (ui.remove_tree_node_by_key(hwnd, main_tree, f"new-{counter[0] - 1}"), refresh_state())),
    ]
    for i, (emoji, label, fn) in enumerate(buttons):
        x = 18 + (i % 2) * 150
        y = 154 + (i // 2) * 54
        btn = ui.create_button(hwnd, left, emoji, label, x, y, 132, 38)
        set_click(hwnd, btn, fn)

    ui.create_descriptions(
        hwnd, left, "📚 JSON 公共 API",
        [
            ("数据", "EU_SetTreeDataJson / EU_GetTreeDataJson"),
            ("状态", "checkedKeys / halfCheckedKeys / expandedKeys"),
            ("节点", "Append / Update / Remove by key"),
            ("交互", "lazy / filter / accordion / drag callbacks"),
        ],
        1, True, 18, 394, left_w - 36, 150,
    )
    refresh_state()


def showcase_tree_select(hwnd, stage, w, h):
    left_w = 336
    bottom_h = 122
    body_h = h - bottom_h - 76
    left = add_demo_panel(hwnd, stage, "🧰 操作区", 28, 30, left_w, body_h)
    right = add_demo_panel(hwnd, stage, "🌲 TreeSelect JSON 高级组件", 388, 30, w - 416, body_h)
    readback = add_demo_panel(hwnd, stage, "📤 状态读回", 28, h - bottom_h - 26, w - 56, bottom_h)
    status_id = add_text(hwnd, readback, "", 20, 52, w - 96, 50, MUTED)

    data = tree_gallery_data()
    main_select = ui.create_tree_select_json(
        hwnd, right, data,
        options={
            "multiple": True,
            "clearable": True,
            "searchable": True,
            "open": True,
            "accordion": False,
            "draggable": True,
            "showActions": True,
            "searchText": "Tree",
        },
        selected_keys=["tree", "table"],
        expanded_keys=["root", "design", "remote"],
        x=24, y=70, w=420, h=40,
    )
    ui.create_tree_select_json(
        hwnd, right,
        [
            {"key": "dept", "label": "🏢 部门", "expanded": True, "children": [
                {"key": "rd", "label": "👩‍💻 研发中心", "leaf": True},
                {"key": "ops", "label": "🛡️ 运维中心", "leaf": True, "disabled": True},
            ]},
        ],
        options={"multiple": False, "clearable": True, "searchable": False},
        selected_keys=["rd"],
        x=500, y=70, w=340, h=40,
    )
    ui.create_tree_select_json(
        hwnd, right,
        {
            "props": {"label": "name", "children": "zones", "isLeaf": "leaf"},
            "data": [
                {"key": "city", "name": "🌏 城市权限", "zones": [
                    {"key": "sh", "name": "🏙️ 上海", "leaf": True, "tag": "默认"},
                    {"key": "bj", "name": "🏛️ 北京", "leaf": True},
                ]}
            ],
        },
        options={"multiple": True, "clearable": True, "searchable": True, "searchText": "上"},
        selected_keys=["sh"],
        x=500, y=160, w=340, h=40,
    )
    ui.create_tree_select_json(
        hwnd, right,
        [
            {"key": "template", "label": "🧩 模板节点", "icon": "🧩", "tag": "标签", "expanded": True, "actions": "打开|归档", "children": [
                {"key": "template-a", "label": "⭐ 右侧操作按钮", "icon": "⭐", "leaf": True, "actions": "处理"},
                {"key": "template-b", "label": "🔒 禁用模板项", "icon": "🔒", "leaf": True, "disabled": True},
            ]}
        ],
        options={"multiple": True, "clearable": True, "showActions": True},
        selected_keys=["template-a"],
        x=500, y=250, w=340, h=40,
    )
    add_text(hwnd, right, "🌲 打开的主选择器展示：搜索框、多选勾选、祖先匹配、懒加载、禁用节点、拖拽标记和桌面模板。", 24, 128, 420, 62, MUTED)
    add_text(hwnd, right, "🏢 单选、字段映射、多选模板分别放在右侧，模拟设置页和权限分配页的桌面端使用习惯。", 500, 318, 420, 62, MUTED)

    def refresh_state():
        state = ui.get_tree_select_state_json(hwnd, main_select)
        ui.set_element_text(
            hwnd, status_id,
            f"打开：{state.get('open')}  搜索：{state.get('searchText')}  匹配：{state.get('matchedCount')}\n"
            f"选中：{state.get('selectedKeys')}  展开：{state.get('expandedKeys')}  拖拽次数：{state.get('dragEventCount')}"
        )

    def lazy_loader(_eid, _code, _index, payload_ptr, payload_len):
        payload = ui.tree_callback_payload(payload_ptr, payload_len)
        if isinstance(payload, dict) and payload.get("key") == "remote":
            ui.append_tree_select_node_json(hwnd, main_select, "remote", [
                {"key": "remote-member", "label": "🧑‍💼 远程成员", "leaf": True, "tag": "加载"},
                {"key": "remote-team", "label": "👥 远程小组", "leaf": True},
            ])
        refresh_state()

    ui.set_tree_select_lazy_load_callback(hwnd, main_select, lazy_loader)

    buttons = [
        ("📂", "打开弹层", lambda _eid: (ui.set_tree_select_state_json(hwnd, main_select, {"open": True}), refresh_state())),
        ("📕", "关闭弹层", lambda _eid: (ui.set_tree_select_state_json(hwnd, main_select, {"open": False}), refresh_state())),
        ("🔎", "搜索资源", lambda _eid: (ui.set_tree_select_state_json(hwnd, main_select, {"open": True, "searchText": "资源"}), refresh_state())),
        ("✅", "设置多选", lambda _eid: (ui.set_tree_select_selected_keys_json(hwnd, main_select, ["tree", "chart"]), refresh_state())),
        ("🧹", "清空选择", lambda _eid: (ui.set_tree_select_selected_keys_json(hwnd, main_select, []), refresh_state())),
        ("⏳", "展开远程", lambda _eid: (ui.set_tree_select_expanded_keys_json(hwnd, main_select, ["root", "remote"]), refresh_state())),
        ("➕", "追加节点", lambda _eid: (ui.append_tree_select_node_json(hwnd, main_select, "design", {"key": "select-added", "label": "✨ 新候选项", "leaf": True, "tag": "新增"}), refresh_state())),
        ("✏️", "更新节点", lambda _eid: (ui.update_tree_select_node_json(hwnd, main_select, "tree", {"key": "tree", "label": "🌳 TreeSelect 已更新", "leaf": True, "tag": "更新"}), refresh_state())),
        ("🗑️", "删除追加", lambda _eid: (ui.remove_tree_select_node_by_key(hwnd, main_select, "select-added"), refresh_state())),
        ("📤", "读取状态", lambda _eid: refresh_state()),
    ]
    add_text(hwnd, left, "🌲 TreeSelect 复用 Tree JSON 数据模型，并额外读写 selectedKeys、searchText、open。", 18, 54, left_w - 36, 70, MUTED)
    for i, (emoji, label, fn) in enumerate(buttons):
        x = 18 + (i % 2) * 150
        y = 144 + (i // 2) * 54
        btn = ui.create_button(hwnd, left, emoji, label, x, y, 132, 38)
        set_click(hwnd, btn, fn)

    ui.create_descriptions(
        hwnd, left, "📚 TreeSelect API",
        [
            ("数据", "EU_SetTreeSelectDataJson"),
            ("状态", "selectedKeys / expandedKeys / open / searchText"),
            ("节点", "Append / Update / Remove by key"),
            ("交互", "搜索、清空、多选、懒加载、拖拽"),
        ],
        1, True, 18, 448, left_w - 36, 150,
    )
    refresh_state()


def showcase_steps(hwnd, stage, w, h):
    add_text(
        hwnd, stage,
        "👣 Steps 步骤条覆盖基础流程、固定间距、长描述、居中、自定义图标、纵向审批和简洁模式。",
        36, 28, w - 72, 28, MUTED,
    )
    matrix_w = min(1088, w - 628)
    side_w = w - matrix_w - 84
    matrix = add_demo_panel(hwnd, stage, "🧩 桌面端样式矩阵", 28, 70, matrix_w, 940)
    inspector = add_demo_panel(hwnd, stage, "📋 交互与状态读回", 52 + matrix_w, 70, side_w, 940)

    state_text = add_text(hwnd, inspector, "等待步骤条交互...", 26, 62, side_w - 52, 96, TEXT)
    hint_text = add_text(
        hwnd, inspector,
        "左侧示例按桌面软件常见流程组织：主流程放在工作区，右侧保留当前状态、程序触发和辅助审批流程。",
        26, 166, side_w - 52, 70, MUTED,
    )
    ui.set_text_options(hwnd, hint_text, align=0, valign=0, wrap=True, ellipsis=False)

    basic = ui.create_steps(
        hwnd, matrix,
        ["📝 填写", "🔍 审核", "🚀 发布"],
        0, 34, 62, 620, 102,
    )
    ui.set_steps_detail_items(
        hwnd, basic,
        [("📝 填写资料", "基础步骤条"), ("🔍 审核内容", "下一步按钮驱动"), ("🚀 发布上线", "自动回到开头")],
    )
    ui.set_steps_statuses(hwnd, basic, [1, 0, 0])
    basic_label = add_text(hwnd, matrix, "基础交互：点击“下一步”循环切换 active。", 680, 82, matrix_w - 716, 48, MUTED)
    ui.set_text_options(hwnd, basic_label, align=0, valign=0, wrap=True, ellipsis=False)

    fixed = ui.create_steps(
        hwnd, matrix,
        ["已完成", "进行中", "步骤 3"],
        1, 34, 198, 680, 86,
        space=200,
    )
    ui.set_steps_statuses(hwnd, fixed, [2, 1, 0])
    add_text(hwnd, matrix, "固定间距：space=200", 740, 220, matrix_w - 776, 28, MUTED)

    long_desc = ui.create_steps(
        hwnd, matrix,
        ["步骤 1", "步骤 2", "步骤 3"],
        1, 34, 324, 820, 122,
    )
    ui.set_steps_detail_items(
        hwnd, long_desc,
        [
            ("步骤 1", "这是一段很长很长很长的描述性文字"),
            ("步骤 2", "这是一段很长很长很长的描述性文字"),
            ("步骤 3", "这段就没那么长了"),
        ],
    )
    ui.set_steps_statuses(hwnd, long_desc, [2, 1, 0])

    centered = ui.create_steps(
        hwnd, matrix,
        ["步骤1", "步骤2", "步骤3", "步骤4"],
        2, 34, 486, 820, 122,
        align_center=True,
    )
    ui.set_steps_detail_items(
        hwnd, centered,
        [
            ("步骤1", "这是一段很长很长很长的描述性文字"),
            ("步骤2", "这是一段很长很长很长的描述性文字"),
            ("步骤3", "这是一段很长很长很长的描述性文字"),
            ("步骤4", "这是一段很长很长很长的描述性文字"),
        ],
    )
    ui.set_steps_statuses(hwnd, centered, [2, 2, 1, 0])

    icons = ui.create_steps(
        hwnd, matrix,
        ["步骤 1", "步骤 2", "步骤 3"],
        1, 34, 648, 700, 98,
        space=200,
    )
    ui.set_steps_icon_items(
        hwnd, icons,
        [
            ("编辑资料", "", "el-icon-edit"),
            ("上传文件", "", "el-icon-upload"),
            ("图片确认", "", "el-icon-picture"),
        ],
    )
    ui.set_steps_statuses(hwnd, icons, [2, 1, 0])
    add_text(hwnd, matrix, "自定义图标：兼容 Element 图标名，也可直接传 emoji。", 760, 670, matrix_w - 796, 48, MUTED)

    simple = ui.create_steps(
        hwnd, matrix,
        ["步骤 1", "步骤 2", "步骤 3"],
        1, 34, 800, 760, 58,
        simple=True,
    )
    ui.set_steps_icon_items(hwnd, simple, [("步骤 1", "", "✏️"), ("步骤 2", "", "⬆️"), ("步骤 3", "", "🖼️")])
    ui.set_steps_statuses(hwnd, simple, [2, 1, 0])
    simple_success = ui.create_steps(
        hwnd, matrix,
        ["收集", "处理", "完成"],
        2, 34, 872, 760, 48,
        simple=True,
    )
    ui.set_steps_icon_items(hwnd, simple_success, [("收集", "", "📥"), ("处理", "", "🧭"), ("完成", "", "✅")])
    ui.set_steps_statuses(hwnd, simple_success, [2, 2, 1])

    vertical = ui.create_steps(
        hwnd, inspector,
        ["提交", "主管审批", "归档"],
        1, 34, 336, 260, 250,
    )
    ui.set_steps_icon_items(
        hwnd, vertical,
        [("提交", "申请已提交", "📨"), ("主管审批", "等待负责人确认", "👤"), ("归档", "自动生成记录", "🗂️")],
    )
    ui.set_steps_direction(hwnd, vertical, 1)
    ui.set_steps_statuses(hwnd, vertical, [2, 1, 0])

    side_simple = ui.create_steps(
        hwnd, inspector,
        ["创建", "校验", "完成"],
        1, 34, 650, side_w - 68, 54,
        simple=True,
    )
    ui.set_steps_icon_items(hwnd, side_simple, [("创建", "", "🧱"), ("校验", "", "🔎"), ("完成", "", "✅")])
    ui.set_steps_statuses(hwnd, side_simple, [2, 1, 0])

    def refresh_state():
        state = ui.get_steps_full_state(hwnd, basic) or {}
        fixed_options = ui.get_steps_options(hwnd, fixed) or {}
        icon_visual = ui.get_steps_visual_state(hwnd, icons) or {}
        simple_visual = ui.get_steps_visual_state(hwnd, simple) or {}
        ui.set_element_text(
            hwnd, state_text,
            "📍 主流程状态\n"
            f"active={state.get('active_index')} / count={state.get('item_count')} / action={state.get('last_action')}\n"
            f"space={fixed_options.get('space')} / align={fixed_options.get('align_center')}\n"
            f"icons={icon_visual.get('icon_count')} / simple={simple_visual.get('simple')}"
        )

    @ui.ValueCallback
    def on_basic_change(_element_id, _value, _count, _action):
        refresh_state()

    keep_callback(on_basic_change)
    ui.set_steps_change_callback(hwnd, basic, on_basic_change)

    def next_step(_element_id):
        state = ui.get_steps_full_state(hwnd, basic)
        if not state:
            return
        next_index = state["active_index"] + 1
        if next_index >= state["item_count"]:
            next_index = 0
        ui.set_steps_active(hwnd, basic, next_index)
        refresh_state()

    def mark_error(_element_id):
        ui.set_steps_statuses(hwnd, basic, [2, 3, 1])
        refresh_state()

    def reset_flow(_element_id):
        ui.set_steps_active(hwnd, basic, 0)
        ui.set_steps_statuses(hwnd, basic, [1, 0, 0])
        refresh_state()

    next_btn = ui.create_button(hwnd, inspector, "➡️", "下一步", 34, 250, 112, 38)
    error_btn = ui.create_button(hwnd, inspector, "⚠️", "标记异常", 166, 250, 126, 38)
    reset_btn = ui.create_button(hwnd, inspector, "🔄", "重置流程", 312, 250, 126, 38)
    set_click(hwnd, next_btn, next_step)
    set_click(hwnd, error_btn, mark_error)
    set_click(hwnd, reset_btn, reset_flow)
    add_text(hwnd, inspector, "纵向审批流程", 34, 304, side_w - 68, 28, TEXT)
    add_text(hwnd, inspector, "简洁模式适合顶部工具区、发布向导和属性面板。", 34, 722, side_w - 68, 44, MUTED)
    refresh_state()


def showcase_loading(hwnd, stage, w, h):
    add_text(hwnd, stage, "⏳ Loading 加载覆盖 Element UI 常见样式：局部遮罩、自定义背景、圆弧图标、脉冲图标、全屏锁定和服务式调用。", 36, 28, w - 72, 30, MUTED)

    actions = add_demo_panel(hwnd, stage, "🧭 操作区", 28, 72, 260, 510)
    work = add_demo_panel(hwnd, stage, "📊 表格数据加载", 310, 72, 690, 510)
    styles = add_demo_panel(hwnd, stage, "🎨 样式矩阵", 1022, 72, max(360, w - 1050), 510)
    status_panel = add_demo_panel(hwnd, stage, "📚 状态读回", 28, 606, w - 56, 150)

    add_text(hwnd, actions, "桌面端通常把加载控制放在工具栏或状态栏，主工作区保持稳定布局。", 22, 62, 210, 66, MUTED)
    status_id = add_text(hwnd, status_panel, "⏳ 当前状态：等待操作", 24, 62, w - 108, 36, TEXT)

    columns = ["日期", "姓名", "地址", "状态"]
    rows = [
        ["2016-05-03", "王小虎", "上海市普陀区金沙江路 1518 弄", "同步中 ⏳"],
        ["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄", "已缓存 ✅"],
        ["2016-05-04", "王小虎", "上海市普陀区金沙江路 1518 弄", "待校验 🔎"],
    ]
    table_id = ui.create_table(hwnd, work, columns, rows, True, True, 24, 74, 640, 178)
    add_text(hwnd, work, "模拟 el-table 的 v-loading：Loading 绑定表格区域，遮罩只覆盖目标控件，不改变表格布局。", 24, 278, 620, 48, MUTED)
    local_loading = ui.create_loading(hwnd, work, "📦 正在加载表格数据", True, 24, 74, 640, 178)
    ui.set_loading_target(hwnd, local_loading, table_id, 0)
    ui.set_loading_style(hwnd, local_loading, background=0xCCFFFFFF, spinner_color=0xFF409EFF,
                         text_color=0xFF2F3A4A, spinner="dots", lock_input=True)

    state = {"current": local_loading, "service": 0, "spinner": 0}

    def refresh_status():
        current = state["current"] or local_loading
        full = ui.get_loading_full_state(hwnd, current)
        style = ui.get_loading_style(hwnd, current)
        text = ui.get_loading_text(hwnd, current)
        if full and style:
            ui.set_element_text(
                hwnd, status_id,
                f"⏳ 文案：{text}  active={full['active']}  fullscreen={full['fullscreen']}  progress={full['progress']}  "
                f"spinner={style['spinner_type']}  lock={int(style['lock_input'])}  ticks={full['tick_count']}"
            )
        else:
            ui.set_element_text(hwnd, status_id, "✅ 服务式加载已关闭，当前无活动遮罩。")

    def open_local(_eid):
        state["current"] = local_loading
        ui.set_loading_text(hwnd, local_loading, "📦 正在加载表格数据")
        ui.set_loading_options(hwnd, local_loading, active=True, fullscreen=False, progress=-1)
        ui.set_loading_style(hwnd, local_loading, background=0xCCFFFFFF, spinner_color=0xFF409EFF,
                             text_color=0xFF2F3A4A, spinner="dots", lock_input=True)
        ui.set_element_visible(hwnd, local_loading, True)
        refresh_status()

    def close_current(_eid):
        if state["service"]:
            ui.close_loading(hwnd, state["service"])
            state["service"] = 0
        ui.set_loading_options(hwnd, local_loading, active=False, fullscreen=False, progress=100)
        ui.set_element_visible(hwnd, local_loading, False)
        state["current"] = local_loading
        refresh_status()

    def open_fullscreen(_eid):
        if state["service"]:
            ui.close_loading(hwnd, state["service"])
        state["service"] = ui.show_loading(
            hwnd, 0, "🔒 正在全屏锁定处理", fullscreen=True, lock_input=True,
            background=0xCC111827, spinner_color=0xFF67C23A, text_color=0xFFFFFFFF,
            spinner="el-icon-loading",
        )
        state["current"] = state["service"]
        refresh_status()

    def open_service(_eid):
        if state["service"]:
            ui.close_loading(hwnd, state["service"])
        state["service"] = ui.show_loading(
            hwnd, table_id, "🚀 服务式加载中", fullscreen=False, lock_input=True,
            background=0xCC000000, spinner_color=0xFFFFD166, text_color=0xFFFFFFFF,
            spinner="arc",
        )
        state["current"] = state["service"]
        refresh_status()

    def switch_spinner(_eid):
        state["spinner"] = (state["spinner"] + 1) % 3
        labels = ["dots", "arc", "pulse"]
        current = state["current"] or local_loading
        ui.set_loading_style(hwnd, current, background=0xCCFFFFFF, spinner_color=0xFF409EFF,
                             text_color=0xFF2F3A4A, spinner=labels[state["spinner"]],
                             lock_input=True)
        ui.set_loading_text(hwnd, current, f"🔄 当前图标：{labels[state['spinner']]}")
        refresh_status()

    buttons = [
        ("📦", "局部加载", open_local),
        ("✅", "关闭加载", close_current),
        ("🔒", "全屏锁定", open_fullscreen),
        ("🚀", "服务方式", open_service),
        ("🔄", "切换图标", switch_spinner),
        ("📤", "读取状态", lambda _eid: refresh_status()),
    ]
    for i, (emoji, label, handler) in enumerate(buttons):
        btn = ui.create_button(hwnd, actions, emoji, label, 24, 150 + i * 52, 190, 38)
        set_click(hwnd, btn, handler)

    default_panel = ui.create_panel(hwnd, styles, 24, 68, 220, 128)
    dark_panel = ui.create_panel(hwnd, styles, 264, 68, 220, 128)
    arc_panel = ui.create_panel(hwnd, styles, 24, 224, 220, 128)
    pulse_panel = ui.create_panel(hwnd, styles, 264, 224, 220, 128)
    progress_panel = ui.create_panel(hwnd, styles, 24, 380, 460, 92)
    for panel in (default_panel, dark_panel, arc_panel, pulse_panel, progress_panel):
        ui.set_panel_style(hwnd, panel, 0xFFF7F9FC, 0xFFD7DEE8, 1.0, 8.0, 8)

    ui.create_loading(hwnd, styles, "默认加载 ⏳", True, 24, 68, 220, 128)
    custom = ui.create_loading(hwnd, styles, "拼命加载中", True, 264, 68, 220, 128)
    ui.set_loading_style(hwnd, custom, background=0xCC000000, spinner_color=0xFFFFFFFF,
                         text_color=0xFFFFFFFF, spinner="el-icon-loading", lock_input=False)
    arc = ui.create_loading(hwnd, styles, "圆弧图标 🔄", True, 24, 224, 220, 128)
    ui.set_loading_style(hwnd, arc, background=0xAAFFFFFF, spinner_color=0xFF409EFF,
                         text_color=0xFF303133, spinner="arc", lock_input=False)
    pulse = ui.create_loading(hwnd, styles, "脉冲状态 🫧", True, 264, 224, 220, 128)
    ui.set_loading_style(hwnd, pulse, background=0xAAFFFFFF, spinner_color=0xFF67C23A,
                         text_color=0xFF303133, spinner="pulse", lock_input=False)
    progress = ui.create_loading(hwnd, styles, "导入进度", True, 24, 380, 460, 92)
    ui.set_loading_options(hwnd, progress, active=True, fullscreen=False, progress=68)
    ui.set_loading_style(hwnd, progress, background=0xDDFFFFFF, spinner_color=0xFFE6A23C,
                         text_color=0xFF303133, spinner="arc", lock_input=False)

    refresh_status()


def showcase_statistic(hwnd, stage, w, h):
    now_ms = int(time.time() * 1000)
    state = {"liked": True, "paused": False}
    status_id = add_text(hwnd, stage, "📊 统计数值：数值格式、前后缀、formatter、可点击后缀和倒计时均由 C++ Statistic 绘制。", 44, 28, w - 88, 28, MUTED)

    grid = add_demo_panel(hwnd, stage, "📌 数值统计样式矩阵", 28, 68, w - 56, 330)
    card_w = max(250, (w - 56 - 72) // 4)
    gap = 16

    growth = ui.create_statistic(hwnd, grid, "📈 增长人数", "1314", "", " 人", 24, 70, card_w, 122)
    ui.set_statistic_number_options(hwnd, growth, precision=2, animated=True, group_separator=True)
    ui.set_statistic_affix_options(hwnd, growth, "", " 人", 0, 0xFF67C23A, 0xFF67C23A)

    ratio = ui.create_statistic(hwnd, grid, "👥 男女比", "0", "", "", 24 + (card_w + gap), 70, card_w, 122)
    ui.set_statistic_display_text(hwnd, ratio, "456/2")
    ui.set_statistic_affix_options(hwnd, ratio, "", "", 0, 0, 0xFFE6A23C)

    flags = ui.create_statistic(hwnd, grid, "🚩 活跃金额", "4154.564", "🚩 ", " 🚩", 24 + (card_w + gap) * 2, 70, card_w, 122)
    ui.set_statistic_number_options(hwnd, flags, precision=2, animated=True, group_separator=True, decimal_separator=".")
    ui.set_statistic_affix_options(hwnd, flags, "🚩 ", " 🚩", 0xFFF56C6C, 0xFF409EFF, 0xFFEAF0FF)

    feedback = ui.create_statistic(hwnd, grid, "⭐ 用户反馈", "521", "", " ★", 24 + (card_w + gap) * 3, 70, card_w, 122)
    ui.set_statistic_number_options(hwnd, feedback, precision=0, animated=True)
    ui.set_statistic_affix_options(hwnd, feedback, "", " ★", 0, 0xFFFFC107, 0xFFEAF0FF, suffix_clickable=True)

    @ui.ClickCallback
    def on_feedback_suffix(_eid):
        state["liked"] = not state["liked"]
        ui.dll.EU_SetStatisticValue(hwnd, feedback, ui.bytes_arg(ui.make_utf8("521" if state["liked"] else "520")), len(ui.make_utf8("521" if state["liked"] else "520")))
        ui.set_statistic_affix_options(hwnd, feedback, "", " ★" if state["liked"] else " ☆", 0, 0xFFFFC107, 0xFFEAF0FF, suffix_clickable=True)
        ui.set_element_text(hwnd, status_id, "⭐ 已切换反馈星标：收藏" if state["liked"] else "☆ 已切换反馈星标：取消收藏")

    ui.set_statistic_suffix_click_callback(hwnd, feedback, keep_callback(on_feedback_suffix))

    add_text(hwnd, grid, "上排覆盖 group-separator、precision、decimal-separator、formatter 文本、前后缀 emoji 与独立颜色。点击“用户反馈”的星标后缀可切换状态。", 24, 218, w - 112, 46, MUTED)

    timers = add_demo_panel(hwnd, stage, "⏱️ 倒计时模式与桌面端操作", 28, 426, w - 56, 520)
    left_w = max(600, (w - 88) // 2)
    right_x = 42 + left_w
    stat_w = left_w - 56

    sale = ui.create_statistic(hwnd, timers, "🎉 商品降价 🎉", "0", "", " 抢购即将开始", 24, 68, stat_w, 118)
    ui.set_statistic_countdown(hwnd, sale, now_ms + 1000 * 60 * 60 * 8)
    ui.set_statistic_affix_options(hwnd, sale, "", " 抢购即将开始", 0, 0xFFF56C6C, 0xFF67C23A)

    game = ui.create_statistic(hwnd, timers, "🎮 时间游戏", "0", "", " 后结束", 24, 214, stat_w, 118)
    ui.set_statistic_countdown(hwnd, game, now_ms + 1000 * 60 * 30)
    ui.set_statistic_affix_options(hwnd, game, "", " 后结束", 0, 0xFF7AA7FF, 0xFFEAF0FF)

    @ui.ClickCallback
    def on_game_finish(_eid):
        ui.set_element_text(hwnd, status_id, "⏰ 时间游戏已到点，finish 回调已触发。")

    ui.set_statistic_finish_callback(hwnd, game, keep_callback(on_game_finish))

    add_btn = ui.create_button(hwnd, timers, "➕", "增加 10 秒", 34, 350, 156, 38, variant=1)
    set_click(hwnd, add_btn, lambda _eid: (ui.add_statistic_countdown_time(hwnd, game, 10000), ui.set_element_text(hwnd, status_id, "➕ 已给时间游戏增加 10 秒")))

    solar = ui.create_statistic(hwnd, timers, "🚩 距离立夏还有", "0", "", "", right_x, 68, stat_w, 118)
    ui.set_statistic_countdown(hwnd, solar, now_ms + 1000 * 60 * 60 * 24 * 18, "DD天HH小时mm分钟")
    ui.set_statistic_affix_options(hwnd, solar, "", "", 0, 0, 0xFFE6A23C)

    tomorrow = ui.create_statistic(hwnd, timers, "📜 距离明日", "0", "", "", right_x, 214, stat_w, 118)
    ui.set_statistic_countdown(hwnd, tomorrow, now_ms + 1000 * 60 * 60 * 6, "HH:mm:ss")
    ui.set_statistic_affix_options(hwnd, tomorrow, "", "", 0, 0, 0xFF67C23A)

    pause_btn = ui.create_button(hwnd, timers, "⏸️", "暂停", right_x + 10, 350, 132, 38, variant=6)

    def toggle_pause(_eid):
        state["paused"] = not state["paused"]
        ui.set_statistic_countdown_state(hwnd, tomorrow, state["paused"])
        ui.set_element_text(hwnd, pause_btn, "继续" if state["paused"] else "暂停")
        ui.set_element_text(hwnd, status_id, "⏸️ 距离明日倒计时已暂停" if state["paused"] else "▶️ 距离明日倒计时已继续")

    set_click(hwnd, pause_btn, toggle_pause)

    add_text(hwnd, timers, "倒计时卡片支持默认中文时分秒、DD天HH小时mm分钟、HH:mm:ss、增加时间、暂停/继续和结束回调。", 24, 426, w - 112, 34, MUTED)


def showcase_empty(hwnd, stage, w, h):
    wide, _tall, small = image_sample_files()
    remote = "https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png"
    state = {"slot": 0, "action": 0}

    status_id = add_text(hwnd, stage, "📭 Empty 状态：等待图片加载与按钮交互。", 32, 24, w - 64, 28, MUTED)
    control = add_demo_panel(hwnd, stage, "🧭 桌面端空状态控制区", 28, 70, 340, h - 250)
    add_text(hwnd, control, "用于表格、搜索结果、文件列表和任务队列为空时的占位提示。右侧覆盖描述、图片、尺寸和默认插槽按钮。", 22, 58, 296, 78, MUTED)

    preview = add_demo_panel(hwnd, stage, "🖥️ 空列表工作台", 396, 70, w - 424, h - 110)
    add_text(hwnd, preview, "搜索结果", 24, 58, 160, 24, TEXT)
    add_text(hwnd, preview, "筛选条件：状态=待处理，时间=本周，负责人=全部", 150, 58, 520, 24, MUTED)

    basic = ui.create_empty(
        hwnd, preview, "暂无数据 📭", "描述文字：当前筛选条件下没有可展示的记录。",
        24, 96, 280, 190, icon="📭"
    )

    remote_empty = ui.create_empty(
        hwnd, preview, "暂无订单 🍔", "自定义图片 URL，远程加载完成后自动刷新。",
        330, 96, 300, 220, image=remote, image_size=128, action="重新加载"
    )

    default_size = ui.create_empty(
        hwnd, preview, "默认尺寸 🖼️", "图片按控件宽度自适应。",
        656, 96, 280, 210, image=small
    )

    large_size = ui.create_empty(
        hwnd, preview, "图片尺寸 200 🖼️", "等价于 :image-size=\"200\"。",
        962, 96, 300, 300, image=wide, image_size=200
    )

    slot_empty = ui.create_empty(
        hwnd, preview, "没有匹配内容 🔎", "默认插槽区域挂载真实 Button 子元素。",
        24, 340, 360, 260, icon="🔎"
    )
    slot_btn = ui.create_button(hwnd, slot_empty, "➕", "创建内容", 106, 198, 148, 42)

    local_fallback = ui.create_empty(
        hwnd, preview, "本地图片回退 🧩", "无网络时也能用本地生成 BMP 演示。",
        420, 340, 360, 260, image=wide, image_size=150, action="重新筛选"
    )

    readback = add_demo_panel(hwnd, stage, "📊 状态读回", 28, h - 170, 340, 130)

    def refresh_status():
        status = (
            f"📭 图片状态：远程={ui.get_empty_image_status(hwnd, remote_empty)} "
            f"默认={ui.get_empty_image_status(hwnd, default_size)} "
            f"200={ui.get_empty_image_status(hwnd, large_size)} "
            f"本地={ui.get_empty_image_status(hwnd, local_fallback)}；"
            f"尺寸={ui.get_empty_image_size(hwnd, large_size)}；"
            f"插槽点击={state['slot']}；内置按钮={state['action']}"
        )
        ui.set_element_text(hwnd, status_id, status)
        ui.set_element_text(hwnd, readback_text, status)

    def on_slot_click(_element_id):
        state["slot"] += 1
        refresh_status()

    def on_action_click(_element_id):
        state["action"] += 1
        refresh_status()

    set_click(hwnd, slot_btn, on_slot_click)
    action_cb = keep_callback(ui.ClickCallback(on_action_click))
    ui.set_empty_action_callback(hwnd, remote_empty, action_cb)
    ui.set_empty_action_callback(hwnd, local_fallback, action_cb)

    refresh_btn = ui.create_button(hwnd, control, "🔄", "刷新状态", 22, 150, 136, 40)
    set_click(hwnd, refresh_btn, lambda _eid: refresh_status())
    add_text(hwnd, control, "样式覆盖", 22, 214, 120, 24, TEXT)
    add_text(hwnd, control, "✅ 描述文字\n✅ 自定义图片 URL\n✅ 图片尺寸 200\n✅ 真实子按钮插槽\n✅ 内置操作按钮回调", 22, 248, 270, 150, TEXT)

    readback_text = add_text(hwnd, readback, "", 18, 52, 300, 64, MUTED)
    refresh_status()


def showcase_descriptions(hwnd, stage, w, h):
    state = {"clicks": 0}
    status_id = add_text(hwnd, stage, "📋 描述列表状态：已展示基础、边框、无边框、垂直、跨列、标签和自定义样式。", 32, 24, w - 64, 28, MUTED)

    control = add_demo_panel(hwnd, stage, "🧭 桌面端样式控制区", 28, 70, 360, 500)
    add_text(hwnd, control, "面向后台资料页、用户详情页、订单属性面板和运维信息卡片。右侧所有样式都由同一个 C++ Descriptions 组件绘制。", 22, 58, 316, 70, MUTED)

    preview = add_demo_panel(hwnd, stage, "🖥️ 用户资料工作台", 416, 70, w - 444, 500)
    base_items = [
        {"label": "用户名", "content": "kooriookami", "label_icon": "👤"},
        {"label": "手机号", "content": "18100000000", "label_icon": "📱"},
        {"label": "居住地", "content": "苏州市", "label_icon": "📍"},
        {"label": "备注", "content": "学校", "label_icon": "🏷️", "content_type": 1, "tag_type": 1},
        {"label": "联系地址", "content": "江苏省苏州市吴中区吴中大道 1188 号", "label_icon": "🏢", "span": 2, "content_align": 2},
    ]
    bordered = ui.create_descriptions(hwnd, preview, "📋 带边框列表", base_items, 3, True, 22, 58, 610, 190,
                                      label_width=104, min_row_height=42, wrap_values=True, responsive=False)
    ui.set_descriptions_extra(hwnd, bordered, "⚙️", "操作", True, 1)
    ui.set_descriptions_items_ex(hwnd, bordered, base_items)
    plain = ui.create_descriptions(hwnd, preview, "🧾 无边框列表", base_items, 3, False, 660, 58, 560, 190,
                                   label_width=100, min_row_height=42, wrap_values=True, responsive=False)
    ui.set_descriptions_items_ex(hwnd, plain, base_items)
    ui.set_descriptions_colors(hwnd, plain, 0, 0, 0, 0xFF9AA6C7, 0, 0)

    def on_extra(_eid):
        state["clicks"] += 1
        full = ui.get_descriptions_full_state(hwnd, bordered)
        count = full["extra_click_count"] if full else state["clicks"]
        ui.set_element_text(hwnd, status_id, f"⚙️ 右上角操作已点击 {count} 次；当前边框列表为 {full['columns'] if full else 3} 列。")

    set_click(hwnd, bordered, on_extra)

    vertical_panel = add_demo_panel(hwnd, stage, "📐 垂直布局与逐项跨列", 28, 596, 820, 250)
    vertical_items = [
        {"label": "用户名", "content": "kooriookami", "label_icon": "👤"},
        {"label": "手机号", "content": "18100000000", "label_icon": "📱"},
        {"label": "居住地", "content": "苏州市", "label_icon": "📍", "span": 2},
        {"label": "备注", "content": "学校", "label_icon": "🏫", "content_type": 1, "tag_type": 2},
        {"label": "联系地址", "content": "江苏省苏州市吴中区吴中大道 1188 号", "label_icon": "🏢", "span": 3},
    ]
    v1 = ui.create_descriptions(hwnd, vertical_panel, "📌 垂直带边框列表", vertical_items, 4, True, 24, 58, 370, 158,
                                label_width=92, min_row_height=64, wrap_values=True, responsive=False)
    ui.set_descriptions_layout(hwnd, v1, direction=1, size=0, columns=4, bordered=True)
    ui.set_descriptions_items_ex(hwnd, v1, vertical_items)
    v2 = ui.create_descriptions(hwnd, vertical_panel, "🪟 垂直无边框列表", vertical_items, 4, False, 420, 58, 370, 158,
                                label_width=92, min_row_height=64, wrap_values=True, responsive=False)
    ui.set_descriptions_layout(hwnd, v2, direction=1, size=2, columns=4, bordered=False)
    ui.set_descriptions_items_ex(hwnd, v2, vertical_items)

    size_panel = add_demo_panel(hwnd, stage, "🎚️ 四种尺寸与业务密度", 876, 596, w - 904, 250)
    for title, size_value, x in [("默认", 0, 24), ("中等", 1, 210), ("小型", 2, 396), ("超小", 3, 582)]:
        did = ui.create_descriptions(
            hwnd, size_panel, f"✨ {title}",
            [{"label": "状态", "content": "已同步", "content_type": 1, "tag_type": 1},
             {"label": "编号", "content": f"NO-{size_value + 1:03d}"}],
            1, True, x, 58, 168, 150,
            label_width=72, min_row_height=38, wrap_values=False, responsive=False,
        )
        ui.set_descriptions_layout(hwnd, did, direction=0, size=size_value, columns=1, bordered=True)
        ui.set_descriptions_items_ex(
            hwnd, did,
            [{"label": "状态", "content": "已同步", "content_type": 1, "tag_type": 1, "label_icon": "✅"},
             {"label": "编号", "content": f"NO-{size_value + 1:03d}", "label_icon": "🔢"}],
        )

    style_panel = add_demo_panel(hwnd, stage, "🎨 自定义 label/content 样式", 28, 872, w - 56, 196)
    styled_items = [
        {"label": "用户名", "content": "kooriookami", "label_icon": "👤", "label_bg": 0xFFE1F3D8, "content_bg": 0xFFFDE2E2},
        {"label": "手机号", "content": "18100000000", "label_icon": "📱"},
        {"label": "居住地", "content": "苏州市", "label_icon": "📍"},
        {"label": "备注", "content": "学校", "label_icon": "🏷️", "content_type": 1, "tag_type": 3},
        {"label": "联系地址", "content": "江苏省苏州市吴中区吴中大道 1188 号", "label_icon": "🏢", "span": 2, "content_align": 2},
    ]
    styled = ui.create_descriptions(hwnd, style_panel, "🎨 自定义样式列表", styled_items, 3, True, 24, 58, w - 104, 106,
                                    label_width=112, min_row_height=42, wrap_values=True, responsive=False)
    ui.set_descriptions_items_ex(hwnd, styled, styled_items)
    ui.set_descriptions_colors(hwnd, styled, BORDER, 0xFFF5F7FA, 0, 0xFF53627A, 0xFF162033, 0xFF162033)
    add_text(hwnd, style_panel, "同一组件覆盖 label 图标、内容标签、右对齐、逐项背景色和全局主题色覆盖；适合桌面端属性面板。", 24, 158, w - 104, 24, MUTED)


def showcase_carousel(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "🎠 走马灯全样式：Hover / Click 指示器、外置指示器、箭头模式、卡片、纵向和自动播放都由 C++ Carousel 绘制。", 32, 24, w - 64, 28, MUTED)

    def items(label):
        return [
            f"🚀 {label} 第一屏",
            f"🎨 {label} 第二屏",
            f"🧭 {label} 第三屏",
            f"✅ {label} 第四屏",
        ]

    def plus_visual(eid, font=18, scale=82):
        ui.set_carousel_visual(
            hwnd, eid,
            text_color=0xFF475669,
            text_alpha=191,
            text_font_size=font,
            odd_bg=0xFFD3DCE6,
            even_bg=0xFF99A9BF,
            panel_bg=0xFFF5F7FA,
            active_indicator=0xFF409EFF,
            inactive_indicator=0x6678909C,
            card_scale_percent=scale,
        )

    trigger_panel = add_demo_panel(hwnd, stage, "🎯 指示器触发方式", 28, 70, w - 56, 250)
    hover = ui.create_carousel(hwnd, trigger_panel, items("Hover"), 0, 0, 28, 62, 620, 150)
    ui.set_carousel_behavior(hwnd, hover, trigger_mode="hover", arrow_mode="hover", direction="horizontal", carousel_type="normal", pause_on_hover=True)
    ui.set_carousel_autoplay(hwnd, hover, False, 3000)
    plus_visual(hover, 14)
    add_text(hwnd, trigger_panel, "🖱️ 默认 Hover 指示器触发", 28, 218, 260, 24, MUTED)

    click = ui.create_carousel(hwnd, trigger_panel, items("Click"), 0, 0, 690, 62, 620, 150)
    ui.set_carousel_behavior(hwnd, click, trigger_mode="click", arrow_mode="hover", direction="horizontal", carousel_type="normal", pause_on_hover=True)
    ui.set_carousel_autoplay(hwnd, click, False, 3000)
    plus_visual(click, 14)
    add_text(hwnd, trigger_panel, "👆 Click 指示器触发", 690, 218, 260, 24, MUTED)

    mode_panel = add_demo_panel(hwnd, stage, "🧩 指示器位置与箭头模式", 28, 344, w - 56, 240)
    outside = ui.create_carousel(hwnd, mode_panel, items("外置"), 0, 1, 28, 62, 390, 140)
    ui.set_carousel_behavior(hwnd, outside, trigger_mode="click", arrow_mode="hover", direction="horizontal", carousel_type="normal", pause_on_hover=True)
    plus_visual(outside, 18)
    add_text(hwnd, mode_panel, "📍 indicator-position=outside", 28, 204, 300, 24, MUTED)

    always = ui.create_carousel(hwnd, mode_panel, items("常显"), 0, 0, 448, 62, 390, 140)
    ui.set_carousel_behavior(hwnd, always, trigger_mode="click", arrow_mode="always", direction="horizontal", carousel_type="normal", pause_on_hover=False)
    ui.set_carousel_autoplay(hwnd, always, True, 5000)
    plus_visual(always, 18)
    add_text(hwnd, mode_panel, "➡️ arrow=always / interval=5000", 448, 204, 330, 24, MUTED)

    never = ui.create_carousel(hwnd, mode_panel, items("无箭头"), 0, 0, 868, 62, 390, 140)
    ui.set_carousel_behavior(hwnd, never, trigger_mode="click", arrow_mode="never", direction="horizontal", carousel_type="normal", pause_on_hover=False)
    plus_visual(never, 18)
    add_text(hwnd, mode_panel, "🚫 arrow=never，仅保留指示器", 868, 204, 310, 24, MUTED)

    layout_panel = add_demo_panel(hwnd, stage, "🃏 卡片模式与纵向模式", 28, 612, w - 56, 330)
    card = ui.create_carousel(hwnd, layout_panel, [
        "📊 运营看板", "🧾 审批队列", "📦 库存预警", "✅ 发布完成", "🎨 主题配置", "🧭 导航入口"
    ], 0, 0, 28, 62, 780, 220)
    ui.set_carousel_behavior(hwnd, card, trigger_mode="click", arrow_mode="always", direction="horizontal", carousel_type="card", pause_on_hover=False)
    ui.set_carousel_autoplay(hwnd, card, True, 4000)
    plus_visual(card, 14, 76)
    add_text(hwnd, layout_panel, "🃏 type=card：上一项、当前项、下一项同屏展示，侧项可点击切换。", 28, 288, 680, 24, MUTED)

    vertical = ui.create_carousel(hwnd, layout_panel, items("纵向"), 0, 0, 848, 62, 360, 220)
    ui.set_carousel_behavior(hwnd, vertical, trigger_mode="click", arrow_mode="always", direction="vertical", carousel_type="normal", pause_on_hover=False)
    ui.set_carousel_autoplay(hwnd, vertical, False, 4000)
    plus_visual(vertical, 14)
    add_text(hwnd, layout_panel, "↕️ direction=vertical / autoplay=false", 848, 288, 360, 24, MUTED)

    control_panel = add_demo_panel(hwnd, stage, "⏯️ 自动播放控制", 28, 970, w - 56, 130)
    live = ui.create_carousel(hwnd, control_panel, items("自动播放"), 0, 0, 28, 50, 520, 62)
    ui.set_carousel_behavior(hwnd, live, trigger_mode="click", arrow_mode="always", direction="horizontal", carousel_type="normal", pause_on_hover=True)
    ui.set_carousel_autoplay(hwnd, live, True, 1200)
    plus_visual(live, 14)

    def pause_live(_eid):
        ui.set_carousel_autoplay(hwnd, live, False, 1200)
        ui.set_element_text(hwnd, status, "⏸️ 已暂停自动播放；配置仍保持 interval=1200，点击继续会从当前项恢复。")

    def resume_live(_eid):
        ui.set_carousel_autoplay(hwnd, live, True, 1200)
        ui.set_element_text(hwnd, status, "▶️ 已继续自动播放；鼠标悬停时会按 pause-on-hover 暂停推进。")

    pause_btn = ui.create_button(hwnd, control_panel, "⏸️", "暂停", 590, 62, 112, 38)
    resume_btn = ui.create_button(hwnd, control_panel, "▶️", "继续", 722, 62, 112, 38)
    set_click(hwnd, pause_btn, pause_live)
    set_click(hwnd, resume_btn, resume_live)
    add_text(hwnd, control_panel, "🧪 这一组用于桌面软件里常见的暂停/继续操作；状态栏会实时说明当前动作。", 862, 62, max(360, w - 960), 38, MUTED)


def showcase_icon(hwnd, stage, w, h):
    hero = add_demo_panel(hwnd, stage, "⭐ Icon：专门绘制 emoji / 符号", 28, 30, w - 56, 250)
    add_text(hwnd, hero, "Icon 是一个轻量视觉元素，适合状态、入口、列表前缀和工具栏符号；它会参与 D2D/DirectWrite 彩色 emoji 渲染。", 30, 58, w - 150, 28, MUTED)
    samples = [
        ("⭐", "常用标记", 1.35, 0, 0xFFFFD54A),
        ("▶", "主要动作", 1.50, 0, 0xFF8CB6FF),
        ("✅", "成功状态", 1.30, 0, 0xFF69D282),
        ("⚠", "警告提示", 1.36, 0, 0xFFFFC24D),
        ("🔒", "权限/安全", 1.25, 0, 0xFFB9C5E8),
        ("☀", "主题外观", 1.48, 0, 0xFFFFD166),
    ]
    for i, (icon, label, scale, rotation, color) in enumerate(samples):
        x = 34 + i * 178
        box = add_themed_panel(hwnd, hero, x, 102, 142, 108, "panel_canvas", "panel_canvas_border", 1.0, 8.0, 8)
        icon_id = ui.create_icon(hwnd, box, icon, 45, 15, 52, 52)
        ui.set_icon_options(hwnd, icon_id, scale, rotation)
        ui.set_element_color(hwnd, icon_id, 0, color)
        label_id = add_text(hwnd, box, label, 12, 76, 118, 24, MUTED)
        ui.set_text_options(hwnd, label_id, align=1, valign=0, wrap=False, ellipsis=False)

    toolbar = add_demo_panel(hwnd, stage, "🧰 在真实界面里的用法", 28, 312, w - 56, 184)
    ui.create_button(hwnd, toolbar, "📁", "打开", 30, 72, 126, 42, variant=5)
    ui.create_button(hwnd, toolbar, "✓", "保存", 174, 72, 126, 42, variant=1)
    ui.create_button(hwnd, toolbar, "🔍", "查找", 318, 72, 126, 42, variant=5)
    ui.create_button(hwnd, toolbar, "⚙", "设置", 462, 72, 126, 42, variant=5)
    add_text(hwnd, toolbar, "Icon 本身只负责画符号；按钮、菜单、列表等组件可以把 emoji 作为图标语义复用。", 30, 132, min(900, w - 110), 28, MUTED)

    readback = add_demo_panel(hwnd, stage, "🔎 尺寸、颜色与旋转读回", 28, 534, w - 56, 170)
    status_icon = ui.create_icon(hwnd, readback, "⭐", 36, 66, 54, 54)
    ui.set_icon_options(hwnd, status_icon, 1.55, -12.0)
    ui.set_element_color(hwnd, status_icon, 0, 0xFFFFD54A)
    scale, rotation = ui.get_icon_options(hwnd, status_icon)
    add_text(hwnd, readback, f"当前图标：⭐  · 缩放 {scale:.2f} · 旋转 {rotation:.0f}° · 前景色 0xFFFFD54A", 112, 80, w - 210, 28, TEXT)
    add_text(hwnd, readback, "这块演示强调：Icon 是可见内容，不是间距；它的工作重点是 emoji 显示质量和视觉状态表达。", 112, 114, w - 210, 28, MUTED)


def showcase_space(hwnd, stage, w, h):
    intro = add_demo_panel(hwnd, stage, "↔️ Space：不可见的占位间距", 28, 30, w - 56, 210)
    add_text(hwnd, intro, "Space 不绘制内容，也不接收鼠标命中；它在 Layout 中占据固定宽高，用来把相邻元素稳定隔开。", 30, 58, w - 130, 28, MUTED)
    btn_w = 112
    btn_h = 40
    row_x = 34
    row_y = 104
    ui.create_button(hwnd, intro, "", "新建", row_x, row_y, btn_w, btn_h, variant=5)
    ui.create_space(hwnd, intro, row_x + btn_w, row_y, 26, btn_h)
    ui.create_button(hwnd, intro, "", "打开", row_x + btn_w + 26, row_y, btn_w, btn_h, variant=5)
    ui.create_space(hwnd, intro, row_x + btn_w * 2 + 26, row_y, 64, btn_h)
    ui.create_button(hwnd, intro, "", "保存", row_x + btn_w * 2 + 26 + 64, row_y, btn_w, btn_h, variant=1)
    add_text(hwnd, intro, "上方两个空白段分别是 26px 和 64px 的 Space；它们本身看不见，但会影响按钮位置。", 34, 160, w - 120, 28, TEXT)

    compare = add_demo_panel(hwnd, stage, "📏 同一组按钮，不同 Space 宽度", 28, 278, w - 56, 260)
    specs = [(24, "紧凑工具栏"), (56, "表单操作区"), (96, "分组强调")]
    for i, (space_w, label) in enumerate(specs):
        y = 62 + i * 62
        add_text(hwnd, compare, label, 32, y + 8, 120, 24, MUTED)
        x = 160
        ui.create_button(hwnd, compare, "", "确认", x, y, 108, 36, variant=1)
        add_themed_panel(hwnd, compare, x + 108, y + 4, space_w, 28, "panel_gold", "panel_gold_border", 1.0, 4.0, 0)
        ui.create_button(hwnd, compare, "", "取消", x + 108 + space_w, y, 108, 36, variant=0)
        add_text(hwnd, compare, f"Space {space_w}px", x + 108 + space_w + 126, y + 6, 140, 24, 0xFFFFE4B5)

    layout_case = add_demo_panel(hwnd, stage, "🧱 纵向占位：留出说明区或呼吸感", 28, 576, w - 56, 220)
    ui.create_button(hwnd, layout_case, "", "第一行信息", 34, 62, 220, 34, variant=5)
    ui.create_space(hwnd, layout_case, 34, 96, 220, 30)
    ui.create_button(hwnd, layout_case, "", "第二行信息", 34, 126, 220, 34, variant=5)
    add_text(hwnd, layout_case, "Space 常用于工具栏分组、表单行距、卡片内部留白。它不是装饰元素，所以需要用周围组件的位置变化来观察效果。", 790, 86, max(360, w - 900), 52, MUTED)


def showcase_skeleton(hwnd, stage, w, h):
    status = add_text(
        hwnd, stage,
        "💀 Skeleton 覆盖加载态/完成态、动画开关、头像占位、行数上限、紧凑场景和 Set/Get 状态读回。",
        36, 28, w - 72, 28, MUTED
    )

    overview = add_demo_panel(hwnd, stage, "⭐ 形态总览", 28, 72, w - 56, 250)
    variants = [
        ("默认骨架", "头像 + 3 行 + 动画", 3, True, True, True),
        ("无头像骨架", "仅文本条，适合表格行", 4, True, True, False),
        ("静态骨架", "关闭扫光，适合低频刷新", 5, False, True, True),
        ("完成态", "loading=false 时显示内容容器", 3, False, False, True),
    ]
    cell_gap = 16
    cell_w = max(260, (w - 56 - 48 - cell_gap * 3) // 4)
    for i, (title, note, rows, animated, loading, avatar) in enumerate(variants):
        x = 24 + i * (cell_w + cell_gap)
        card = add_themed_panel(hwnd, overview, x, 58, cell_w, 158, "panel_canvas", "panel_canvas_border", 1.0, 8.0, 8)
        add_text(hwnd, card, f"💡 {title}", 14, 10, cell_w - 28, 24, TEXT)
        ui.create_skeleton(hwnd, card, rows, animated, 14, 42, cell_w - 28, 74, loading=loading, show_avatar=avatar)
        add_text(hwnd, card, note, 14, 124, cell_w - 28, 24, MUTED)
        if not loading:
            add_text(hwnd, card, "✅ 数据已加载", 26, 62, cell_w - 52, 28, TEXT)

    workbench_w = max(840, w - 516)
    workbench = add_demo_panel(hwnd, stage, "🎛️ 程序化控制台", 28, 352, workbench_w, 342)
    live = ui.create_skeleton(hwnd, workbench, 4, True, 28, 66, min(720, workbench_w - 76), 132)
    readback = add_text(hwnd, workbench, "", 28, 216, workbench_w - 56, 52, TEXT)

    def refresh_state(message="✅ Skeleton 状态已读回。"):
        options = ui.get_skeleton_options(hwnd, live)
        if options:
            rows, animated, loading, show_avatar = options
            text = (
                f"{message}\n"
                f"行数={rows} · 动画={animated} · 加载中={loading} · 显示头像={show_avatar} · "
                f"加载读回={ui.get_skeleton_loading(hwnd, live)}"
            )
        else:
            text = f"{message}\n未读到 Skeleton 状态。"
        ui.set_element_text(hwnd, readback, text)
        ui.set_element_text(hwnd, status, message)

    def set_loading(loading):
        def handler(_eid):
            rows, animated, _old_loading, show_avatar = ui.get_skeleton_options(hwnd, live) or (4, True, True, True)
            ui.set_skeleton_options(hwnd, live, rows, animated, loading, show_avatar)
            refresh_state("📦 已切换为加载中骨架。" if loading else "✅ 已切换为完成态内容容器。")
        return handler

    def set_rows(rows):
        def handler(_eid):
            _old_rows, animated, loading, show_avatar = ui.get_skeleton_options(hwnd, live) or (4, True, True, True)
            ui.set_skeleton_rows(hwnd, live, rows)
            ui.set_skeleton_options(hwnd, live, rows, animated, loading, show_avatar)
            refresh_state(f"📏 已设置为 {rows} 行，C++ 会把行数限制在 1-12。")
        return handler

    def toggle_avatar(_eid):
        rows, animated, loading, show_avatar = ui.get_skeleton_options(hwnd, live) or (4, True, True, True)
        ui.set_skeleton_options(hwnd, live, rows, animated, loading, not show_avatar)
        refresh_state("😀 已切换头像占位显示。")

    def toggle_animation(_eid):
        rows, animated, loading, show_avatar = ui.get_skeleton_options(hwnd, live) or (4, True, True, True)
        ui.set_skeleton_animated(hwnd, live, not animated)
        ui.set_skeleton_options(hwnd, live, rows, not animated, loading, show_avatar)
        refresh_state("✨ 已切换扫光动画。")

    buttons = [
        ("📦", "加载中", set_loading(True), 1),
        ("✅", "完成态", set_loading(False), 2),
        ("1", "1 行", set_rows(1), 5),
        ("5", "5 行", set_rows(5), 5),
        ("12", "12 行", set_rows(12), 5),
        ("😀", "头像", toggle_avatar, 6),
        ("✨", "动画", toggle_animation, 6),
        ("🔎", "读回", lambda _eid: refresh_state("🔎 已手动读取当前 Skeleton 选项。"), 6),
    ]
    for i, (emoji, label, handler, variant) in enumerate(buttons):
        btn = ui.create_button(hwnd, workbench, emoji, label, 28 + i * 104, 286, 88, 34, variant=variant)
        set_click(hwnd, btn, handler)

    feature = add_demo_panel(hwnd, stage, "✨ 展示重点", 52 + workbench_w, 352, 300, 342)
    add_text(hwnd, feature, "分类：数据展示", 18, 54, 264, 26, MUTED)
    add_text(hwnd, feature, "能力：骨架屏", 18, 88, 264, 26, MUTED)
    add_text(
        hwnd, feature,
        "✅ 中文文案与 emoji\n✅ 行数 1-12 限制\n✅ 动画/静态预览\n✅ 头像占位开关\n✅ 加载/完成态切换\n✅ 设置与读取状态",
        18, 132, 264, 170, TEXT
    )

    scenarios = add_demo_panel(hwnd, stage, "📊 业务场景矩阵", 28, 724, w - 56, 330)
    scene_specs = [
        ("表格行加载", "无头像、多行短条", 4, True, True, False),
        ("用户卡片加载", "头像 + 摘要信息", 3, True, True, True),
        ("详情页加载", "长文本占位", 6, False, True, False),
        ("加载完成", "保留完成态容器边界", 2, False, False, True),
    ]
    scene_w = max(300, (w - 56 - 48 - cell_gap * 3) // 4)
    for i, (title, note, rows, animated, loading, avatar) in enumerate(scene_specs):
        x = 24 + i * (scene_w + cell_gap)
        card = add_themed_panel(hwnd, scenarios, x, 62, scene_w, 224, "panel_canvas", "panel_canvas_border", 1.0, 8.0, 8)
        add_text(hwnd, card, f"🧩 {title}", 16, 12, scene_w - 32, 24, TEXT)
        ui.create_skeleton(hwnd, card, rows, animated, 16, 50, scene_w - 32, 108, loading=loading, show_avatar=avatar)
        if not loading:
            add_text(hwnd, card, "🎉 已拿到真实数据", 30, 86, scene_w - 60, 26, TEXT)
        add_text(hwnd, card, note, 16, 170, scene_w - 32, 24, MUTED)

    refresh_state("✅ Skeleton 完整功能演示已加载。")


SPECIAL_SHOWCASES = {
    "Panel": showcase_panel,
    "Button": showcase_button,
    "Link": showcase_link,
    "Icon": showcase_icon,
    "Space": showcase_space,
    "Radio": showcase_radio,
    "Container": showcase_container,
    "Header": showcase_header,
    "Aside": showcase_aside,
    "Main": showcase_main,
    "Footer": showcase_footer,
    "Layout": showcase_layout,
    "Border": showcase_border,
    "Divider": showcase_divider,
    "Affix": showcase_affix,
    "Watermark": showcase_watermark,
    "Checkbox": showcase_checkbox,
    "Input": showcase_input,
    "InputGroup": showcase_input_group,
    "InputTag": showcase_input_tag,
    "Select": showcase_select,
    "SelectV2": showcase_select_v2,
    "InputNumber": showcase_inputnumber,
    "Rate": showcase_rate,
    "Switch": showcase_switch,
    "DatePicker": showcase_datepicker,
    "DateRangePicker": showcase_daterangepicker,
    "TimeRange": showcase_timerange,
    "DateTimeRange": showcase_datetimerange,
    "DateTimePicker": showcase_datetimepicker,
    "TimePicker": showcase_timepicker,
    "TimeSelect": showcase_timeselect,
    "Autocomplete": showcase_autocomplete,
    "Tag": showcase_tag,
    "Badge": showcase_badge,
    "Progress": showcase_progress,
    "Avatar": showcase_avatar,
    "Gauge": showcase_gauge,
    "Pagination": showcase_pagination,
    "Steps": showcase_steps,
    "Empty": showcase_empty,
    "Skeleton": showcase_skeleton,
    "Descriptions": showcase_descriptions,
    "Table": showcase_table,
    "Card": showcase_card,
    "Collapse": showcase_collapse,
    "Timeline": showcase_timeline,
    "Statistic": showcase_statistic,
    "Upload": showcase_upload,
    "Image": showcase_image,
    "Carousel": showcase_carousel,
    "Alert": showcase_alert,
    "Message": showcase_message,
    "MessageBox": showcase_messagebox,
    "Notification": showcase_notification,
    "Loading": showcase_loading,
    "Dialog": showcase_dialog,
    "Drawer": showcase_drawer,
    "Tooltip": showcase_tooltip,
    "Popover": showcase_popover,
    "Popconfirm": showcase_popconfirm,
    "Dropdown": showcase_dropdown,
    "Menu": showcase_menu,
    "InfiniteScroll": showcase_infinite_scroll,
    "Tabs": showcase_tabs,
    "Tree": showcase_tree,
    "TreeSelect": showcase_tree_select,
}


COMPACT_SHOWCASE = {
    "Button", "InfoBox", "Text", "Link", "Icon", "Space", "Checkbox", "Radio", "Switch",
    "Slider", "Input", "InputGroup", "Tag", "Progress", "Avatar", "Statistic",
    "StatusDot", "Backtop", "Segmented", "InfiniteScroll", "Breadcrumb", "Tabs", "Alert", "Loading",
    "Message", "MessageBox", "Tooltip", "Popover", "Popconfirm",
}


def add_component_detail(hwnd, root, category_name, name, emoji, summary, builder, floating=False):
    page = ui.create_panel(hwnd, root, PAGE_X, PAGE_Y, PAGE_W, PAGE_H)
    ui.set_panel_style(hwnd, page, SURFACE, BORDER_SOFT, 1.0, 8.0, 10)
    register_panel(page, "surface", "border_soft", 1.0, 8.0, 10)
    ui.set_element_visible(hwnd, page, False)
    add_text(hwnd, page, f"{emoji} {name}", 24, 20, 560, 34, TEXT)
    add_text(hwnd, page, f"{category_name} · {summary}", 24, 56, 980, 28, MUTED)
    add_text(hwnd, page, "组件演示区", 24, 100, 240, 26, TEXT)

    stage_x = 24
    stage_y = 132
    stage_w = PAGE_W - 48
    stage_h = PAGE_H - 178
    stage = ui.create_panel(hwnd, page, stage_x, stage_y, stage_w, stage_h)
    ui.set_panel_style(hwnd, stage, 0xFF242941, BORDER, 1.0, 8.0, 10)
    register_panel(stage, "stage", "border", 1.0, 8.0, 10)

    try:
        if name in SPECIAL_SHOWCASES:
            SPECIAL_SHOWCASES[name](hwnd, stage, stage_w, stage_h)
        else:
            side_w = 300
            preview_w = stage_w - side_w - 80
            main_h = 230 if name in COMPACT_SHOWCASE and not floating else stage_h - 60
            main = add_demo_panel(hwnd, stage, "⭐ 标准演示", 28, 30, preview_w, main_h)
            add_feature_panel(hwnd, stage, category_name, summary, 52 + preview_w, 30, side_w, min(260, stage_h - 60))

            if floating:
                builder(hwnd, page, stage_x + 52, stage_y + 90, preview_w - 48, main_h - 96)
            else:
                builder(hwnd, main, 24, 64, preview_w - 48, main_h - 92)

            if name in COMPACT_SHOWCASE and not floating:
                variant_y = 282
                variant_h = min(210, stage_h - variant_y - 30)
                if variant_h > 120:
                    compact = add_demo_panel(hwnd, stage, "🎛️ 尺寸与场景变化", 28, variant_y, preview_w, variant_h)
                    builder(hwnd, compact, 24, 62, max(180, preview_w // 2 - 44), 48)
                    builder(hwnd, compact, preview_w // 2 + 8, 62, max(180, preview_w // 2 - 44), 48)
                    add_text(hwnd, compact, "同一组件在紧凑栏、表单行、工具区中都可以保持稳定排版。", 24, 132, preview_w - 48, 28, MUTED)
    except Exception as exc:
        gallery_errors.append((name, str(exc)))
        ui.create_alert(hwnd, stage, "演示创建失败", str(exc), 2, 0, False, 28, 30, stage_w - 56, 92)

    page_ids.append((f"{category_name}/{name}", page))
    return page


def make_page(hwnd, root, name, intro, demos, cols=4, card_w=CARD_W, card_h=CARD_H, gap=CARD_GAP):
    category_components[name] = []
    for demo in demos:
        demo_name, emoji, summary, builder = demo[:4]
        floating = bool(demo[4]) if len(demo) > 4 else False
        category_components[name].append((demo_name, emoji, summary))
        add_component_detail(hwnd, root, name, demo_name, emoji, summary, builder, floating)


def button_action(hwnd, title, body):
    def action(_element_id):
        title_data = ui.make_utf8(title)
        body_data = ui.make_utf8(body)
        ok_data = ui.make_utf8("知道了")
        ui.dll.EU_ShowMessageBox(
            hwnd,
            ui.bytes_arg(title_data), len(title_data),
            ui.bytes_arg(body_data), len(body_data),
            ui.bytes_arg(ok_data), len(ok_data),
            on_gallery_messagebox,
        )
    return action


def showcase_colorpicker(hwnd, stage, w, h):
    status = add_text(hwnd, stage, "🎨 ColorPicker 支持任意色号输入、连续色域、透明度、预设色和四种桌面端尺寸。", 36, 28, w - 72, 28, MUTED)

    predefine_colors = [
        0xFFFF4500, 0xFFFF8C00, 0xFFFFD700, 0xFF90EE90,
        0xFF00CED1, 0xFF1E90FF, 0xFFC71585, 0xADFF4500,
        0xFFFF7800, 0xFFFAE900, 0x8FFFE699, 0xFF00BBC0,
        0xBA1F8EFF, 0x77C71585,
    ]

    left = add_demo_panel(hwnd, stage, "🧾 基础表单", 28, 72, 500, 320)
    add_text(hwnd, left, "有默认值", 28, 58, 112, 28, MUTED)
    cp_default = ui.create_colorpicker(hwnd, left, "主题色", 0xFF409EFF, 150, 52, 300, 42)
    add_text(hwnd, left, "无默认值", 28, 120, 112, 28, MUTED)
    cp_empty = ui.create_colorpicker(hwnd, left, "可选色", None, 150, 114, 300, 42)
    add_text(hwnd, left, "弹层状态", 28, 182, 112, 28, MUTED)
    cp_open = ui.create_colorpicker(hwnd, left, "品牌色", 0xFF1E90FF, 150, 176, 300, 42, open_panel=True)
    add_text(hwnd, left, "桌面表单中空值不会伪装成白色，读回为空字符串和颜色 0。", 28, 252, 430, 44, MUTED)

    middle = add_demo_panel(hwnd, stage, "🌈 任意色号与透明度", 552, 72, 560, 320)
    cp_alpha = ui.create_colorpicker(
        hwnd,
        middle,
        "半透明色",
        0xADFF4500,
        28,
        54,
        360,
        42,
        show_alpha=True,
        palette=predefine_colors,
        open_panel=True,
    )
    add_text(hwnd, middle, "可直接键入 #RRGGBB 或 #AARRGGBB，也可拖动色域与色相条精确取色。", 28, 232, 500, 26, MUTED)
    add_text(hwnd, middle, "预设色仍保留为快捷入口；关闭透明度时只读回 #RRGGBB。", 28, 264, 500, 26, MUTED)

    right_w = max(420, w - 1164)
    right = add_demo_panel(hwnd, stage, "📏 尺寸矩阵", 1136, 72, right_w, 320)
    size_specs = [
        ("默认", 0, 42, "表单行"),
        ("中等", 1, 38, "工具区"),
        ("小型", 2, 34, "属性面板"),
        ("超小", 3, 30, "紧凑栏"),
    ]
    size_ids = []
    for index, (label, size, height, scene) in enumerate(size_specs):
        y = 52 + index * 58
        add_text(hwnd, right, scene, 26, y + 6, 88, 24, MUTED)
        picker_id = ui.create_colorpicker(
            hwnd,
            right,
            f"{label}色",
            0xFF3B82F6,
            118,
            y,
            min(310, right_w - 150),
            height,
            size=size,
        )
        size_ids.append(picker_id)

    readback = add_demo_panel(hwnd, stage, "📋 状态读回与操作", 28, 424, w - 56, 250)
    readback_text = add_text(hwnd, readback, "等待操作。", 28, 56, w - 112, 60, MUTED)

    def color_state(label, picker_id):
        options = ui.get_colorpicker_options(hwnd, picker_id) or {}
        color = ui.get_colorpicker_color(hwnd, picker_id) & 0xFFFFFFFF
        return (
            f"{label}: 有值={ui.get_colorpicker_has_value(hwnd, picker_id)} "
            f"颜色=0x{color:08X} 色号={ui.get_colorpicker_hex(hwnd, picker_id) or '空'} "
            f"alpha={ui.get_colorpicker_alpha(hwnd, picker_id)} "
            f"打开={ui.get_colorpicker_open(hwnd, picker_id)} "
            f"预设={ui.get_colorpicker_palette_count(hwnd, picker_id)} "
            f"尺寸={options.get('size', '-')}"
        )

    def refresh_status(message="📌 已刷新 ColorPicker 状态。"):
        lines = [
            message,
            color_state("默认值", cp_default),
            color_state("空值", cp_empty),
            color_state("透明度", cp_alpha),
        ]
        ui.set_element_text(hwnd, readback_text, "\n".join(lines))
        ui.set_element_text(hwnd, status, message)

    def clear_selected(_eid):
        ui.clear_colorpicker(hwnd, cp_alpha)
        refresh_status("🧹 已清空透明度选择器，空值态读回颜色 0。")

    def set_brand(_eid):
        ui.set_colorpicker_hex(hwnd, cp_empty, "#8843A047")
        ui.set_colorpicker_open(hwnd, cp_empty, True)
        refresh_status("✅ 已把空值选择器设为半透明品牌绿，并打开面板。")

    def open_panel(_eid):
        ui.set_colorpicker_open(hwnd, cp_default, True)
        ui.set_colorpicker_open(hwnd, cp_alpha, True)
        refresh_status("📂 已打开默认值与透明度选择器面板。")

    clear_btn = ui.create_button(hwnd, readback, "🧹", "清空透明度", 28, 148, 150, 40)
    brand_btn = ui.create_button(hwnd, readback, "✅", "设为品牌色", 198, 148, 150, 40)
    open_btn = ui.create_button(hwnd, readback, "📂", "打开面板", 368, 148, 132, 40)
    set_click(hwnd, clear_btn, clear_selected)
    set_click(hwnd, brand_btn, set_brand)
    set_click(hwnd, open_btn, open_panel)

    for picker_id in (cp_default, cp_empty, cp_open, cp_alpha, *size_ids):
        cb = keep_callback(ui.ValueCallback(lambda _id, _color, _alpha, _count: refresh_status("🎨 颜色状态已变化。")))
        ui.set_colorpicker_change_callback(hwnd, picker_id, cb)

    refresh_status("✅ ColorPicker 全样式演示已加载。")


SPECIAL_SHOWCASES["ColorPicker"] = showcase_colorpicker


def showcase_mentions(hwnd, stage, w, h):
    status = add_text(
        hwnd, stage,
        "📣 Mentions 覆盖 @ 提及、# 话题、过滤开关、候选展开、键盘选中、插入与状态读回。",
        36, 28, w - 72, 28, MUTED
    )

    people = [
        "设计师 🎨", "开发者 🧑‍💻", "测试同学 🧪", "产品经理 📋",
        "运营伙伴 📣", "客服同学 🎧", "数据分析师 📊", "项目负责人 🚀",
    ]
    topics = ["性能优化 🚀", "DPI 适配 🖥️", "emoji 渲染 😀", "无闪烁窗口 ✨", "文档补齐 📚", "易语言接入 🔌"]
    teams = ["前端小组", "桌面框架", "组件库", "自动化测试", "发布值班", "用户体验"]

    primary = add_demo_panel(hwnd, stage, "💬 提及输入工作台", 28, 72, max(760, w - 596), 330)
    add_text(hwnd, primary, "人员提及", 28, 62, 112, 26, MUTED)
    mention_people = ui.create_mentions(hwnd, primary, "@设", people, 144, 56, min(720, w - 780), 42)
    ui.set_mentions_open(hwnd, mention_people, True)
    ui.set_mentions_selected(hwnd, mention_people, 0)

    add_text(hwnd, primary, "话题触发", 28, 126, 112, 26, MUTED)
    mention_topic = ui.create_mentions(hwnd, primary, "#D", topics, 144, 120, min(720, w - 780), 42)
    ui.set_mentions_options(hwnd, mention_topic, "#", True, False)
    ui.set_mentions_open(hwnd, mention_topic, True)
    ui.set_mentions_selected(hwnd, mention_topic, 1)

    add_text(hwnd, primary, "不过滤候选", 28, 190, 112, 26, MUTED)
    mention_team = ui.create_mentions(hwnd, primary, "@", teams, 144, 184, min(720, w - 780), 42)
    ui.set_mentions_options(hwnd, mention_team, "@", False, True)
    ui.set_mentions_open(hwnd, mention_team, True)
    ui.set_mentions_selected(hwnd, mention_team, 2)

    add_text(
        hwnd, primary,
        "可以直接点击候选，也可以聚焦后用 ↑/↓ 切换、Enter 插入、Esc 收起。候选弹层会随窗口边界自动向上或向下展开。",
        28, 258, max(520, w - 690), 44, MUTED
    )

    side = add_demo_panel(hwnd, stage, "🧪 功能矩阵", max(820, w - 540), 72, 512, 330)
    readback = add_text(hwnd, side, "等待操作。", 24, 54, 464, 132, TEXT)

    def mention_state(label, element_id):
        options = ui.get_mentions_options(hwnd, element_id)
        trigger = chr(options.get("trigger", 64)) if options and options.get("trigger", 0) else "@"
        return (
            f"{label}: 值={ui.get_mentions_value(hwnd, element_id) or '空'} "
            f"打开={ui.get_mentions_open(hwnd, element_id)} "
            f"选中={ui.get_mentions_selected(hwnd, element_id)} "
            f"候选={ui.get_mentions_suggestion_count(hwnd, element_id)} "
            f"匹配={options.get('matched', 0)} "
            f"触发={trigger}"
        )

    def refresh_status(message="📋 已刷新 Mentions 状态。"):
        lines = [
            message,
            mention_state("人员", mention_people),
            mention_state("话题", mention_topic),
            mention_state("小组", mention_team),
        ]
        ui.set_element_text(hwnd, readback, "\n".join(lines))
        ui.set_element_text(hwnd, status, message)

    def open_all(_eid):
        for element_id in (mention_people, mention_topic, mention_team):
            ui.set_mentions_open(hwnd, element_id, True)
        refresh_status("📂 已展开全部候选列表。")

    def insert_current(_eid):
        ui.insert_mentions_selected(hwnd, mention_people)
        ui.insert_mentions_selected(hwnd, mention_topic)
        ui.insert_mentions_selected(hwnd, mention_team)
        refresh_status("✅ 已插入每个输入框当前选中候选。")

    def cycle_selected(_eid):
        for element_id in (mention_people, mention_topic, mention_team):
            count = max(1, ui.get_mentions_suggestion_count(hwnd, element_id))
            ui.set_mentions_selected(hwnd, element_id, (ui.get_mentions_selected(hwnd, element_id) + 1) % count)
            ui.set_mentions_open(hwnd, element_id, True)
        refresh_status("⬇️ 已切换到下一条候选。")

    def apply_filter(_eid):
        ui.set_mentions_value(hwnd, mention_people, "@测")
        ui.set_mentions_filter(hwnd, mention_people, "测")
        ui.set_mentions_value(hwnd, mention_topic, "#文")
        ui.set_mentions_filter(hwnd, mention_topic, "文")
        ui.set_mentions_value(hwnd, mention_team, "@组")
        ui.set_mentions_filter(hwnd, mention_team, "组")
        for element_id in (mention_people, mention_topic, mention_team):
            ui.set_mentions_open(hwnd, element_id, True)
        refresh_status("🔎 已设置中文过滤文本并展开匹配项。")

    def swap_suggestions(_eid):
        ui.set_mentions_suggestions(hwnd, mention_people, ["交互设计师 🧭", "视觉设计师 🎨", "动效设计师 ✨", "无障碍设计师 ♿"])
        ui.set_mentions_suggestions(hwnd, mention_topic, ["组件验收 ✅", "发布清单 📦", "缺陷复盘 🧯", "体验走查 🔍"])
        ui.set_mentions_suggestions(hwnd, mention_team, ["核心维护组", "示例完善组", "文档翻译组", "高 DPI 验收组"])
        for element_id in (mention_people, mention_topic, mention_team):
            ui.set_mentions_open(hwnd, element_id, True)
            ui.set_mentions_selected(hwnd, element_id, 0)
        refresh_status("🔄 已替换候选数据源。")

    def reset_demo(_eid):
        ui.set_mentions_suggestions(hwnd, mention_people, people)
        ui.set_mentions_suggestions(hwnd, mention_topic, topics)
        ui.set_mentions_suggestions(hwnd, mention_team, teams)
        ui.set_mentions_options(hwnd, mention_people, "@", True, True)
        ui.set_mentions_options(hwnd, mention_topic, "#", True, False)
        ui.set_mentions_options(hwnd, mention_team, "@", False, True)
        ui.set_mentions_value(hwnd, mention_people, "@设")
        ui.set_mentions_value(hwnd, mention_topic, "#D")
        ui.set_mentions_value(hwnd, mention_team, "@")
        ui.set_mentions_open(hwnd, mention_people, True)
        ui.set_mentions_open(hwnd, mention_topic, True)
        ui.set_mentions_open(hwnd, mention_team, True)
        ui.set_mentions_selected(hwnd, mention_people, 0)
        ui.set_mentions_selected(hwnd, mention_topic, 1)
        ui.set_mentions_selected(hwnd, mention_team, 2)
        refresh_status("♻️ 已恢复初始演示状态。")

    actions = [
        ("📂", "展开候选", open_all),
        ("✅", "插入选中", insert_current),
        ("⬇️", "切换选中", cycle_selected),
        ("🔎", "中文过滤", apply_filter),
        ("🔄", "替换数据", swap_suggestions),
        ("♻️", "重置演示", reset_demo),
    ]
    for i, (emoji, label, handler) in enumerate(actions):
        col = i % 2
        row = i // 2
        btn = ui.create_button(hwnd, side, emoji, label, 24 + col * 178, 206 + row * 42, 154, 34, variant=1 if i < 3 else 6)
        set_click(hwnd, btn, handler)

    matrix = add_demo_panel(hwnd, stage, "🎛️ 状态与场景覆盖", 28, 426, w - 56, 294)
    cards = [
        ("默认 @", "@产", people, "@", True, True, 0, "输入 @ 后按中文过滤候选"),
        ("# 话题", "#e", topics, "#", True, False, 2, "可配置触发符，不自动补空格"),
        ("不过滤", "@任意", teams, "@", False, True, 3, "关闭过滤后始终展示完整候选"),
        ("收起态", "准备通知 @开发者", people, "@", True, True, 1, "保持值但收起弹层"),
    ]
    cell_gap = 14
    cell_w = max(290, (w - 56 - 36 - cell_gap * 3) // 4)
    for i, (title, value, items, trigger, filter_enabled, insert_space, selected, tip) in enumerate(cards):
        px = 18 + i * (cell_w + cell_gap)
        card = add_themed_panel(hwnd, matrix, px, 58, cell_w, 202, "panel_canvas", "panel_canvas_border", 1.0, 8.0, 8)
        add_text(hwnd, card, f"✨ {title}", 14, 10, cell_w - 28, 24, TEXT)
        mid = ui.create_mentions(hwnd, card, value, items, 14, 44, cell_w - 28, 38)
        ui.set_mentions_options(hwnd, mid, trigger, filter_enabled, insert_space)
        ui.set_mentions_selected(hwnd, mid, selected)
        ui.set_mentions_open(hwnd, mid, title != "收起态")
        add_text(hwnd, card, tip, 14, 104, cell_w - 28, 48, MUTED)
        add_text(hwnd, card, f"候选 {ui.get_mentions_suggestion_count(hwnd, mid)} · 选中 {ui.get_mentions_selected(hwnd, mid)}", 14, 162, cell_w - 28, 24, MUTED)

    refresh_status("✅ Mentions 完整功能演示已加载。")


SPECIAL_SHOWCASES["Mentions"] = showcase_mentions


def showcase_cascader(hwnd, stage, w, h):
    options = [
        ("华东 🌊", "上海 🏙️", "浦东新区 ✈️"),
        ("华东 🌊", "上海 🏙️", "徐汇区 🎨"),
        ("华东 🌊", "杭州 🌿", "西湖区 🌸"),
        ("华东 🌊", "南京 🏛️", "玄武区 🦌"),
        ("华南 🌴", "广东 🥭", "深圳 🚀", "南山区 🧪"),
        ("华南 🌴", "广东 🥭", "广州 🌺", "天河区 💼"),
        ("西南 🏔️", "四川 🐼", "成都 🍵", "高新区 💻"),
        ("华北 🧭", "北京 🏯", "朝阳区 ☀️"),
    ]

    add_text(
        hwnd, stage,
        "🧭 Cascader 覆盖多级路径、展开方向、搜索过滤、懒加载标记、程序化 Set/Get 和键盘收起。",
        36, 28, w - 72, 28, MUTED
    )

    left_w = max(820, w - 666)
    workbench = add_demo_panel(hwnd, stage, "🧭 级联选择工作台", 28, 72, left_w, 420)
    add_text(hwnd, workbench, "默认选中", 28, 64, 112, 26, MUTED)
    primary = ui.create_cascader(
        hwnd, workbench, options,
        ["华东 🌊", "上海 🏙️", "浦东新区 ✈️"],
        144, 58, min(640, left_w - 190), 42
    )

    add_text(hwnd, workbench, "展开预览", 28, 128, 112, 26, MUTED)
    opened = ui.create_cascader(
        hwnd, workbench, options,
        ["华南 🌴", "广东 🥭"],
        144, 122, min(640, left_w - 190), 42
    )
    ui.set_cascader_open(hwnd, opened, True)

    add_text(hwnd, workbench, "搜索过滤", 28, 230, 112, 26, MUTED)
    searchable = ui.create_cascader(hwnd, workbench, options, [], 144, 224, min(640, left_w - 190), 42)
    ui.set_cascader_advanced_options(hwnd, searchable, True, False)
    ui.set_cascader_search(hwnd, searchable, "深圳")

    add_text(hwnd, workbench, "懒加载标记", 28, 294, 112, 26, MUTED)
    lazy = ui.create_cascader(
        hwnd, workbench, options,
        ["华南 🌴", "广东 🥭"],
        144, 288, min(640, left_w - 190), 42
    )
    ui.set_cascader_advanced_options(hwnd, lazy, True, True)
    ui.set_cascader_value(hwnd, lazy, ["华南 🌴", "广东 🥭"])
    ui.set_cascader_open(hwnd, lazy, True)

    add_text(
        hwnd, workbench,
        "交互提示：点击输入框展开，点击非叶子节点继续进入下一列，点击叶子节点完成选择；聚焦后 Enter/Space 可开关，Esc 可收起。",
        28, 358, left_w - 56, 44, MUTED
    )

    control = add_demo_panel(hwnd, stage, "🎛️ 程序化控制", 28, 518, left_w, 252)
    status = add_text(hwnd, control, "", 28, 62, left_w - 56, 76, TEXT)

    def refresh_status():
        adv = ui.get_cascader_advanced_options(hwnd, searchable)
        lines = [
            f"主选择：打开={ui.get_cascader_open(hwnd, primary)} 叶子路径={ui.get_cascader_option_count(hwnd, primary)} 选中深度={ui.get_cascader_selected_depth(hwnd, primary)}",
            f"搜索选择：显示列={ui.get_cascader_level_count(hwnd, searchable)} 匹配数={adv['matched']} 可搜索={adv['searchable']}",
            f"懒加载：lazy={ui.get_cascader_advanced_options(hwnd, lazy)['lazy_mode']} 最近层级={ui.get_cascader_advanced_options(hwnd, lazy)['last_lazy_level']}",
        ]
        ui.set_element_text(hwnd, status, "\n".join(lines))

    def choose_pudong(_element_id):
        ui.set_cascader_value(hwnd, primary, ["华东 🌊", "上海 🏙️", "浦东新区 ✈️"])
        ui.set_cascader_open(hwnd, primary, False)
        refresh_status()

    def toggle_open(_element_id):
        ui.set_cascader_open(hwnd, primary, not bool(ui.get_cascader_open(hwnd, primary)))
        refresh_status()

    def search_shenzhen(_element_id):
        ui.set_cascader_search(hwnd, searchable, "深圳")
        ui.set_cascader_open(hwnd, searchable, True)
        refresh_status()

    def load_project_paths(_element_id):
        project_options = [
            ("组件库 🧩", "表单输入 ✍️", "Cascader 🧭"),
            ("组件库 🧩", "选择媒体 📅", "TreeSelect 🌲"),
            ("组件库 🧩", "数据展示 📊", "Table 📋"),
            ("文档中心 📚", "API 索引 🔌", "EU_CreateCascader"),
        ]
        ui.set_cascader_options(hwnd, primary, project_options)
        ui.set_cascader_value(hwnd, primary, ["组件库 🧩", "表单输入 ✍️", "Cascader 🧭"])
        refresh_status()

    buttons = [
        ("📍", "设为浦东", choose_pudong),
        ("🔽", "打开/收起", toggle_open),
        ("🔎", "搜索深圳", search_shenzhen),
        ("🧩", "换项目路径", load_project_paths),
    ]
    for i, (emoji, text, fn) in enumerate(buttons):
        btn = ui.create_button(hwnd, control, emoji, text, 28 + i * 144, 152, 124, 36, variant=1 if i == 0 else 5)
        set_click(hwnd, btn, fn)

    add_text(
        hwnd, control,
        "这些按钮分别调用 SetValue、SetOpen、SetSearch、SetOptions，并立即通过 GetOpen / GetOptionCount / GetSelectedDepth / GetLevelCount / GetAdvancedOptions 读回状态。",
        28, 206, left_w - 56, 32, MUTED
    )

    feature = add_demo_panel(hwnd, stage, "✨ 展示重点", 52 + left_w, 72, 300, 360)
    add_text(hwnd, feature, "分类：表单输入", 18, 54, 264, 26, MUTED)
    add_text(hwnd, feature, "能力：级联选择", 18, 88, 264, 26, MUTED)
    add_text(
        hwnd, feature,
        "✅ 中文路径与 emoji\n✅ 多列联动选择\n✅ 搜索结果预览\n✅ 懒加载层级提示\n✅ 程序化设置选项\n✅ 状态读回展示",
        18, 132, 264, 180, TEXT
    )

    readback = add_demo_panel(hwnd, stage, "📌 常见用法", 52 + left_w, 456, 300, 314)
    usages = [
        "🏙️ 省 / 市 / 区选择",
        "🧩 产品 / 模块 / 页面",
        "👥 部门 / 小组 / 成员",
        "📦 仓库 / 货架 / 批次",
        "📚 文档 / 章节 / 条目",
    ]
    add_text(hwnd, readback, "\n".join(usages), 18, 58, 264, 150, TEXT)
    add_text(hwnd, readback, "路径数据使用 UTF-8，并以“/”连接层级、“|”连接叶子路径；Python 封装可直接传入元组列表。", 18, 220, 260, 58, MUTED)

    refresh_status()


SPECIAL_SHOWCASES["Cascader"] = showcase_cascader


def demo_button(hwnd, parent, x, y, w, h):
    btn = ui.create_button(hwnd, parent, "🚀", "立即体验", x, y, min(w, 150), 38)
    set_click(hwnd, btn, button_action(hwnd, "按钮回调 🚀", "Button 点击事件正常触发。"))


def demo_theme_buttons(hwnd, parent, x, y, w, h):
    light = ui.create_button(hwnd, parent, "☀️", "浅色", x, y, 78, 32)
    dark = ui.create_button(hwnd, parent, "🌙", "深色", x + 88, y, 78, 32)
    system = ui.create_button(hwnd, parent, "💻", "系统", x, y + 42, 166, 32)
    set_click(hwnd, light, lambda _eid: apply_gallery_theme(hwnd, 0))
    set_click(hwnd, dark, lambda _eid: apply_gallery_theme(hwnd, 1))
    set_click(hwnd, system, lambda _eid: apply_gallery_theme(hwnd, 0))


def demo_dialog_button(hwnd, parent, x, y, w, h):
    btn = ui.create_button(hwnd, parent, "💬", "打开对话框", x, y, 150, 36)
    set_click(hwnd, btn, lambda _eid: ui.create_dialog(hwnd, "💬 对话框", "这是 Dialog 组件的独立弹层演示。", True, True, 460, 240))


def demo_drawer_button(hwnd, parent, x, y, w, h):
    btn = ui.create_button(hwnd, parent, "📚", "打开抽屉", x, y, 140, 36)
    set_click(hwnd, btn, lambda _eid: ui.create_drawer(hwnd, "📚 抽屉面板", "Drawer 可从侧边滑出展示详情。", 1, True, True, 320))


def demo_message_service(hwnd, parent, x, y, w, h):
    btn = ui.create_button(hwnd, parent, "💬", "弹出消息", x, y, 132, 36)
    def action(_eid):
        ui.message_info(hwnd, "ℹ️ 这是一条消息提示", closable=True, duration_ms=0, offset=26)
        ui.message_success(hwnd, "✅ 恭喜你，这是一条成功消息", duration_ms=3200, offset=26)
        ui.message_warning(hwnd, "⚠️ 警告哦，这是一条警告消息", center=True, duration_ms=3600, offset=26)
        ui.message_error(
            hwnd,
            "❌ 内容可以是 <span style=\"color: teal\"><strong>VNode</strong></span>",
            rich=True,
            closable=True,
            duration_ms=0,
            offset=26,
        )
    set_click(hwnd, btn, action)
    add_text(hwnd, parent, "自动堆叠、可关闭、居中和轻量富文本。", x, y + 48, min(w - 20, 280), 40, MUTED)


def demo_messagebox_service(hwnd, parent, x, y, w, h):
    alert_btn = ui.create_button(hwnd, parent, "📌", "提示", x, y, 82, 32)
    confirm_btn = ui.create_button(hwnd, parent, "⚠️", "确认", x + 92, y, 96, 32)
    prompt_btn = ui.create_button(hwnd, parent, "📧", "输入", x, y + 42, 92, 32)
    loading_btn = ui.create_button(hwnd, parent, "🚀", "执行", x + 102, y + 42, 96, 32)
    set_click(hwnd, alert_btn, lambda _eid: ui.show_alert_box(
        hwnd, "📌 HTML 片段", "<strong>这是 <i>HTML</i> 片段</strong>",
        confirm="确定 ✅", center=True, rich=True,
    ))
    set_click(hwnd, confirm_btn, lambda _eid: ui.show_confirm_box(
        hwnd, "⚠️ 确认信息", "检测到未保存内容，是否保存修改？",
        confirm="保存 ✅", cancel="放弃修改", box_type=2,
        center=True, distinguish_cancel_and_close=True,
    ))
    set_click(hwnd, prompt_btn, lambda _eid: ui.show_prompt_box(
        hwnd, "📧 输入邮箱", "请输入邮箱地址", placeholder="name@example.com",
        pattern=r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?",
        error="邮箱格式不正确",
    ))
    def loading_action(_eid):
        mid = ui.show_msgbox(
            hwnd, "🚀 消息", "内容可以是 <span style=\"color: teal\"><strong>VNode</strong></span>",
            confirm="执行 ✅", cancel="取消", rich=True,
        )
        ui.set_messagebox_before_close(hwnd, mid, 1200, "执行中...")
    set_click(hwnd, loading_btn, loading_action)


def demo_notification_service(hwnd, parent, x, y, w, h):
    pos_btn = ui.create_button(hwnd, parent, "🧭", "四角通知", x, y, 118, 32)
    html_btn = ui.create_button(hwnd, parent, "🎨", "富文本", x + 128, y, 92, 32)
    hide_btn = ui.create_button(hwnd, parent, "🚫", "隐藏关闭", x, y + 42, 118, 32)
    set_click(hwnd, pos_btn, lambda _eid: (
        ui.notify_success(hwnd, "✅ 右上角", "保存成功", position="top-right", offset=34),
        ui.notify_warning(hwnd, "⚠️ 右下角", "请确认设置", position="bottom-right", offset=34),
        ui.notify_info(hwnd, "ℹ️ 左下角", "同步完成", position="bottom-left", offset=34),
        ui.notify_error(hwnd, "❌ 左上角", "处理失败", position="top-left", offset=34),
    ))
    set_click(hwnd, html_btn, lambda _eid: ui.notify_info(
        hwnd, "🎨 HTML 片段",
        "<strong>这是 <i>HTML</i></strong>，含 <span style=\"color: teal\">teal</span> 文本。",
        rich=True,
        duration_ms=0,
    ))
    set_click(hwnd, hide_btn, lambda _eid: ui.notify_success(
        hwnd, "✅ 无关闭按钮", "这条通知不会自动关闭，也不显示关闭按钮。",
        closable=False,
        duration_ms=0,
        position="top-right",
        offset=90,
    ))


def demo_message_button(hwnd, parent, x, y, w, h, title, body):
    btn = ui.create_button(hwnd, parent, "✨", "点击查看", x, y, 130, 36)
    set_click(hwnd, btn, button_action(hwnd, title, body))


def showcase_transfer(hwnd, stage, w, h):
    basic_items = [
        {"key": 1, "label": "📦 备选项 1", "disabled": False},
        {"key": 2, "label": "🧩 备选项 2", "disabled": False},
        {"key": 3, "label": "🎨 备选项 3", "disabled": False},
        {"key": 4, "label": "🔒 备选项 4", "disabled": True},
        {"key": 5, "label": "🚀 备选项 5", "disabled": False},
        {"key": 6, "label": "📊 备选项 6", "disabled": False},
    ]
    basic = add_demo_panel(hwnd, stage, "🔁 基础穿梭、禁用项与初始目标值", 28, 30, w - 56, 230)
    basic_transfer = ui.create_transfer_ex(
        hwnd, basic, basic_items, target_keys=[1, 4],
        titles=("📚 备选列表", "✅ 已选列表"),
        button_texts=("移回", "加入"),
        item_template="{label}",
        x=24, y=64, w=930, h=138,
    )
    state_id = add_text(hwnd, basic, "", 986, 70, max(260, w - 1070), 88, MUTED)

    def refresh_state():
        ui.set_element_text(
            hwnd, state_id,
            f"右侧值：{ui.get_transfer_value_keys(hwnd, basic_transfer)}\n"
            f"左侧 {ui.get_transfer_count(hwnd, basic_transfer, 0)} 项，"
            f"右侧 {ui.get_transfer_count(hwnd, basic_transfer, 1)} 项，"
            f"禁用 {ui.get_transfer_disabled_count(hwnd, basic_transfer, 0)} 项 🔒"
        )

    join_btn = ui.create_button(hwnd, basic, "➡️", "加入选中", 986, 164, 118, 34)
    back_btn = ui.create_button(hwnd, basic, "⬅️", "移回选中", 1118, 164, 118, 34)
    set_click(hwnd, join_btn, lambda _eid: (ui.transfer_move_right(hwnd, basic_transfer), refresh_state()))
    set_click(hwnd, back_btn, lambda _eid: (ui.transfer_move_left(hwnd, basic_transfer), refresh_state()))
    refresh_state()

    search = add_demo_panel(hwnd, stage, "🔎 可搜索：城市中文与拼音过滤", 28, 284, w - 56, 210)
    city_items = [
        {"key": "shanghai", "label": "🏙️ 上海", "pinyin": "shanghai"},
        {"key": "beijing", "label": "🏛️ 北京", "pinyin": "beijing"},
        {"key": "guangzhou", "label": "🌸 广州", "pinyin": "guangzhou"},
        {"key": "shenzhen", "label": "🚄 深圳", "pinyin": "shenzhen"},
        {"key": "nanjing", "label": "🌙 南京", "pinyin": "nanjing"},
        {"key": "xian", "label": "🏮 西安", "pinyin": "xian"},
        {"key": "chengdu", "label": "🐼 成都", "pinyin": "chengdu"},
    ]
    city_transfer = ui.create_transfer_ex(
        hwnd, search, city_items, target_keys=[],
        filterable=True, titles=("🌍 城市备选", "📍 已选城市"),
        item_template="{label}", filter_placeholder="请输入城市拼音 🔎",
        x=24, y=62, w=930, h=124,
    )
    ui.set_transfer_filters(hwnd, city_transfer, "bei", "")
    add_text(hwnd, search, "筛选框可用键盘输入，也可由 API 设置；示例已过滤出拼音包含 bei 的城市。", 986, 72, max(280, w - 1070), 54, MUTED)
    clear_filter = ui.create_button(hwnd, search, "🧹", "清除过滤", 986, 140, 126, 34)
    set_click(hwnd, clear_filter, lambda _eid: ui.set_transfer_filters(hwnd, city_transfer, "", ""))

    custom = add_demo_panel(hwnd, stage, "🎛️ 自定义标题、按钮、统计格式、模板与底部操作", 28, 518, w - 56, 250)
    custom_items = [
        {"key": 1, "label": "备选项 1", "desc": "低风险", "pinyin": "one"},
        {"key": 2, "label": "备选项 2", "desc": "默认勾选", "pinyin": "two"},
        {"key": 3, "label": "备选项 3", "desc": "默认勾选", "pinyin": "three"},
        {"key": 4, "label": "备选项 4", "desc": "禁用", "pinyin": "four", "disabled": True},
        {"key": 5, "label": "备选项 5", "desc": "可移动", "pinyin": "five"},
    ]
    custom_transfer = ui.create_transfer_ex(
        hwnd, custom, custom_items, target_keys=[1],
        filterable=True, show_footer=True,
        titles=("📥 来源", "📤 目标"),
        button_texts=("到左边", "到右边"),
        fmt=("${total}", "${checked}/${total}"),
        item_template="{key} - {label} · {desc}",
        footer_texts=("⚙️ 左侧操作", "✅ 右侧操作"),
        x=24, y=62, w=930, h=164,
    )
    ui.set_transfer_checked_keys(hwnd, custom_transfer, [2, 3], [1])
    add_text(hwnd, custom, "字段模板覆盖 render-content / scoped-slot 场景：{key}、{label}、{desc}、{pinyin} 都可直接组合显示。", 986, 72, max(310, w - 1070), 70, MUTED)
    add_text(hwnd, custom, f"当前勾选：左 {ui.get_transfer_checked_count(hwnd, custom_transfer, 0)} / 右 {ui.get_transfer_checked_count(hwnd, custom_transfer, 1)}", 986, 150, max(280, w - 1070), 34, TEXT)

    props_panel = add_demo_panel(hwnd, stage, "🧾 字段映射：value / desc 模拟 props", 28, 794, w - 56, 230)
    prop_items = [
        {"value": "sku-1", "desc": "🧾 订单字段", "disabled": False},
        {"value": "sku-2", "desc": "📦 商品字段", "disabled": False},
        {"value": "sku-3", "desc": "🔒 只读字段", "disabled": True},
        {"value": "sku-4", "desc": "🚚 配送字段", "disabled": False},
        {"value": "sku-5", "desc": "💬 备注字段", "disabled": False},
    ]
    prop_transfer = ui.create_transfer_ex(
        hwnd, props_panel, prop_items, target_keys=["sku-2"],
        props={"key": "value", "label": "desc"},
        titles=("🗂️ 可用字段", "📌 已选字段"),
        item_template="{label}",
        show_footer=True,
        footer_texts=("批量字段操作", "生成配置 ✅"),
        x=24, y=62, w=930, h=142,
    )
    add_text(hwnd, props_panel, "Python 侧 dict 可通过 props 映射到 C++ 的 key/label；易语言侧使用 key<Tab>label<Tab>value<Tab>desc<Tab>pinyin<Tab>disabled。", 986, 72, max(330, w - 1070), 82, MUTED)
    add_text(hwnd, props_panel, f"目标值：{ui.get_transfer_value_keys(hwnd, prop_transfer)}", 986, 164, max(280, w - 1070), 30, TEXT)


def showcase_calendar(hwnd, stage, w, h):
    today_value = 20260505
    base_items = [
        {
            "date": 20260512, "label": "05-12", "extra": "产品评审",
            "emoji": "✔️", "badge": "会", "bg": "0xFFEAF2FF", "fg": "0xFF1989FA",
            "border": "0xFF1989FA", "badge_bg": "0xFF1989FA",
            "badge_fg": "0xFFFFFFFF", "font_flags": 1,
        },
        {
            "date": 20260515, "label": "05-15", "extra": "客户演示",
            "emoji": "💬", "badge": "客", "bg": "0xFFFFF7E6", "fg": "0xFF9A5B00",
            "border": "0xFFE6A23C", "badge_bg": "0xFFE6A23C",
            "badge_fg": "0xFFFFFFFF", "font_flags": 1,
        },
        {
            "date": 20260518, "label": "05-18", "extra": "不可预约",
            "emoji": "⛔", "badge": "禁", "bg": "0xFF303442", "fg": "0xFFCDD5E4",
            "border": "0xFFD0D7E2", "badge_bg": "0xFF909399",
            "badge_fg": "0xFFFFFFFF", "disabled": 1,
        },
        {
            "date": 20260522, "label": "05-22", "extra": "发布窗口",
            "emoji": "🚀", "badge": "发", "bg": "0xFFEAF8EF", "fg": "0xFF2F855A",
            "border": "0xFF67C23A", "badge_bg": "0xFF67C23A",
            "badge_fg": "0xFFFFFFFF", "font_flags": 1,
        },
    ]

    state = {
        "display_enabled": False,
        "label_mode": 0,
        "custom_enabled": True,
        "last": "等待用户选择日期",
    }

    left_w = 252
    center_w = min(930, max(820, w - 600))
    gap = 14
    right_w = max(420, w - 56 - left_w - center_w - gap * 2)
    top_y = 30
    top_h = 520
    left_x = 28
    center_x = left_x + left_w + gap
    right_x = center_x + center_w + gap

    ops = add_demo_panel(hwnd, stage, "🧭 操作区", left_x, top_y, left_w, top_h)
    add_text(hwnd, ops, "常用桌面操作集中在左侧，点击后会同步更新中间日历和右侧读回。", 18, 54, left_w - 36, 54, MUTED)

    readback = add_demo_panel(hwnd, stage, "📌 状态读回", right_x, top_y, right_w, top_h)
    status_id = add_text(hwnd, readback, "", 18, 56, right_w - 36, 206, MUTED)
    ui.set_text_options(hwnd, status_id, wrap=True, ellipsis=False)
    add_text(hwnd, readback, "显示范围是 Element UI `range` 的桌面端对应能力；可选范围仍由“设置日历范围”控制。", 18, 292, right_w - 36, 58, MUTED)
    add_text(hwnd, readback, "单元格数据使用每行一个日期、字段 Tab 分隔的 UTF-8 文本，可为具体日期覆盖 label、extra、emoji、badge、颜色和禁用态。", 18, 368, right_w - 36, 82, MUTED)

    main = add_demo_panel(hwnd, stage, "📅 日历区", center_x, top_y, center_w, top_h)
    add_text(hwnd, main, "基础绑定、dateCell 自定义内容和显示范围三种能力并列展示。", 18, 52, center_w - 36, 28, MUTED)
    cal_w = max(260, (center_w - 68) // 3)
    cal_h = 330
    x1 = 18
    x2 = x1 + cal_w + 16
    x3 = x2 + cal_w + 16
    add_text(hwnd, main, "基础日历", x1, 90, cal_w, 24, TEXT)
    add_text(hwnd, main, "dateCell 自定义", x2, 90, cal_w, 24, TEXT)
    add_text(hwnd, main, "显示范围", x3, 90, cal_w, 24, TEXT)

    base_cal = ui.create_calendar(hwnd, main, 2026, 5, 12, x1, 120, cal_w, cal_h)
    custom_cal = ui.create_calendar(hwnd, main, 2026, 5, 12, x2, 120, cal_w, cal_h)
    range_cal = ui.create_calendar(hwnd, main, 2026, 5, 12, x3, 120, cal_w, cal_h)

    for cal in (base_cal, custom_cal, range_cal):
        ui.set_calendar_range(hwnd, cal, 20260505, 20260528)
        ui.set_calendar_options(hwnd, cal, today_value, True)
        ui.set_calendar_selection_range(hwnd, cal, 20260510, 20260518, True)
        ui.set_calendar_selected_marker(hwnd, cal, "✔️")
        ui.set_calendar_state_colors(
            hwnd, cal,
            selected_bg=0xFF1989FA, selected_fg=0xFFFFFFFF,
            range_bg=0x332F80ED, today_border=0xFF1989FA,
            hover_bg=0xFFEAF2FF, disabled_fg=0xFF9AA6BA,
            adjacent_fg=0xFF909399,
        )
    ui.set_calendar_visual_options(hwnd, custom_cal, True, True, 3, True, 8.0)
    ui.set_calendar_cell_items(hwnd, custom_cal, base_items)
    ui.set_calendar_display_range(hwnd, range_cal, 20260504, 20260524)
    ui.set_calendar_visual_options(hwnd, range_cal, True, True, 1, True, 8.0)
    add_text(
        hwnd, main,
        "dateCell 图例：05-12 产品评审 / 05-15 客户演示 / 05-18 不可预约 / 05-22 发布窗口",
        18, 462, center_w - 36, 36, MUTED,
    )

    def fmt_date(value):
        if not value:
            return "未设置"
        text = str(value)
        if len(text) == 8:
            return f"{text[:4]}-{text[4:6]}-{text[6:]}"
        return text

    def refresh_status():
        custom_count = len([line for line in ui.get_calendar_cell_items(hwnd, custom_cal).splitlines() if line.strip()])
        display = ui.get_calendar_display_range(hwnd, base_cal)
        range_display = ui.get_calendar_display_range(hwnd, range_cal)
        visual = ui.get_calendar_visual_options(hwnd, base_cal)
        ui.set_element_text(
            hwnd,
            status_id,
            "当前选中："
            f"{fmt_date(ui.get_calendar_value(hwnd, base_cal))}\n"
            f"可选范围：{tuple(fmt_date(v) for v in ui.get_calendar_range(hwnd, base_cal))}\n"
            f"基础显示范围：{tuple(fmt_date(v) for v in display)}\n"
            f"范围日历：{tuple(fmt_date(v) for v in range_display)}\n"
            f"自定义单元格：{custom_count} 条\n"
            f"区间选择：{ui.get_calendar_selection_range(hwnd, base_cal)}\n"
            f"视觉选项：{visual}\n"
            f"最近变化：{state['last']}"
        )

    def on_calendar_change(element_id, value, range_start, range_end):
        state["last"] = f"#{element_id} 选中 {fmt_date(value)}，区间 {fmt_date(range_start)} 至 {fmt_date(range_end)}"
        refresh_status()

    for cal in (base_cal, custom_cal, range_cal):
        ui.set_calendar_change_callback(hwnd, cal, on_calendar_change)

    def set_all_to_today(_eid):
        for cal in (base_cal, custom_cal, range_cal):
            ui.set_calendar_date(hwnd, cal, 2026, 5, 5)
        state["last"] = "已跳转到今天 2026-05-05"
        refresh_status()

    def move_month(delta):
        def action(_eid):
            ui.calendar_move_month(hwnd, base_cal, delta)
            ui.calendar_move_month(hwnd, custom_cal, delta)
            state["last"] = "已切换到上月" if delta < 0 else "已切换到下月"
            refresh_status()
        return action

    def toggle_display(_eid):
        state["display_enabled"] = not state["display_enabled"]
        if state["display_enabled"]:
            ui.set_calendar_display_range(hwnd, base_cal, 20260504, 20260524)
            state["last"] = "基础日历已启用显示范围"
        else:
            ui.set_calendar_display_range(hwnd, base_cal, 0, 0)
            state["last"] = "基础日历已恢复普通月视图"
        refresh_status()

    def toggle_label(_eid):
        state["label_mode"] = 1 if state["label_mode"] == 0 else 0
        for cal in (base_cal, range_cal):
            ui.set_calendar_visual_options(hwnd, cal, True, True, state["label_mode"], True, 8.0)
        state["last"] = "已切换为月-日标签" if state["label_mode"] else "已切换为日号标签"
        refresh_status()

    def toggle_custom(_eid):
        state["custom_enabled"] = not state["custom_enabled"]
        if state["custom_enabled"]:
            ui.set_calendar_cell_items(hwnd, custom_cal, base_items)
            state["last"] = "已恢复 dateCell 自定义数据"
        else:
            ui.clear_calendar_cell_items(hwnd, custom_cal)
            state["last"] = "已清空 dateCell 自定义数据"
        refresh_status()

    actions = [
        ("📍", "今天", set_all_to_today),
        ("⬅️", "上月", move_month(-1)),
        ("➡️", "下月", move_month(1)),
        ("📆", "切换显示范围", toggle_display),
        ("🔤", "切换月日标签", toggle_label),
        ("🧹", "清空/恢复自定义", toggle_custom),
    ]
    for i, (emoji, label, handler) in enumerate(actions):
        btn = ui.create_button(hwnd, ops, emoji, label, 18, 126 + i * 58, left_w - 36, 40, variant=1 if i < 4 else 6)
        set_click(hwnd, btn, handler)

    matrix_y = top_y + top_h + 18
    matrix_h = max(500, h - matrix_y - 30)
    matrix = add_demo_panel(hwnd, stage, "🎨 样式矩阵", 28, matrix_y, w - 56, matrix_h)
    add_text(hwnd, matrix, "覆盖默认、蓝色选中、区间高亮、今天高亮、禁用日期、badge、extra 和 emoji/✔️ 标记。", 18, 50, w - 92, 28, MUTED)
    specs = [
        ("默认", "📅", {}, []),
        ("蓝色选中", "🔵", {"selected_bg": 0xFF1989FA, "selected_fg": 0xFFFFFFFF}, []),
        ("区间高亮", "🟦", {"range_bg": 0x333B82F6}, []),
        ("今天高亮", "📍", {"today_border": 0xFFE6A23C}, []),
        ("禁用日期", "🚫", {"disabled_fg": 0xFFB0B7C3}, [{"date": 20260512, "label": "12", "disabled": 1, "badge": "禁"}]),
        ("带 badge", "🏷️", {}, [{"date": 20260512, "label": "12", "badge": "休", "badge_bg": "0xFF1989FA"}]),
        ("带 extra", "📝", {}, [{"date": 20260512, "label": "12", "extra": "会议", "fg": "0xFF1989FA"}]),
        ("emoji/✔️", "✅", {}, [{"date": 20260512, "label": "05-12", "emoji": "✔️", "extra": "完成"}]),
    ]
    cell_gap = 12
    matrix_w = w - 56
    cell_w = max(300, (matrix_w - 36 - cell_gap * 3) // 4)
    cell_h = 196
    for i, (label, emoji, colors, items) in enumerate(specs):
        col = i % 4
        row = i // 4
        px = 18 + col * (cell_w + cell_gap)
        py = 84 + row * (cell_h + 10)
        p = add_themed_panel(hwnd, matrix, px, py, cell_w, cell_h, "panel_canvas", "panel_canvas_border", 1.0, 8.0, 8)
        add_text(hwnd, p, f"{emoji} {label}", 12, 10, cell_w - 24, 24, TEXT)
        cal = ui.create_calendar(hwnd, p, 2026, 5, 12, 12, 42, min(260, cell_w - 24), 138)
        ui.set_calendar_options(hwnd, cal, today_value, True)
        ui.set_calendar_visual_options(hwnd, cal, False, True, 0, True, 6.0)
        ui.set_calendar_selection_range(hwnd, cal, 20260510, 20260516, True)
        ui.set_calendar_selected_marker(hwnd, cal, "✔️" if label == "emoji/✔️" else "")
        ui.set_calendar_state_colors(
            hwnd, cal,
            selected_bg=colors.get("selected_bg", 0),
            selected_fg=colors.get("selected_fg", 0),
            range_bg=colors.get("range_bg", 0),
            today_border=colors.get("today_border", 0),
            disabled_fg=colors.get("disabled_fg", 0),
        )
        if items:
            ui.set_calendar_cell_items(hwnd, cal, items)
        if label == "禁用日期":
            ui.set_calendar_range(hwnd, cal, 20260505, 20260528)

    refresh_status()


SPECIAL_SHOWCASES["Calendar"] = showcase_calendar
SPECIAL_SHOWCASES["Transfer"] = showcase_transfer


def make_media_page(hwnd, root):
    make_page(hwnd, root, "选择媒体", "日期时间、树形选择、穿梭框、上传、图片和轮播等较完整的业务组件。", [
        ("Calendar", "📅", "日历全样式", lambda h, p, x, y, w, hh: ui.create_calendar(h, p, 2026, 5, 3, x, y, min(w, 920), min(hh, 420))),
        ("Tree", "🌳", "树组件", lambda h, p, x, y, w, hh: ui.create_tree(h, p, [("首页", 0, True), ("组件", 0, True), ("表单", 1, True), ("反馈", 1, True)], 1, x, y, min(w, 620), min(hh, 360))),
        ("TreeSelect", "🌲", "树选择", lambda h, p, x, y, w, hh: ui.create_tree_select(h, p, [("部门", 0, True), ("研发", 1, True), ("设计", 1, True)], 1, x, y, min(w, 620), 42), True),
        ("Transfer", "🔁", "穿梭框", lambda h, p, x, y, w, hh: ui.create_transfer(h, p, ["按钮", "输入框"], ["表格"], x, y, min(w, 900), min(hh, 320))),
        ("DatePicker", "📆", "日期选择", lambda h, p, x, y, w, hh: ui.create_datepicker(h, p, 2026, 5, 3, x, y, min(w, 520), 42), True),
        ("DateRangePicker", "📅", "日期范围", lambda h, p, x, y, w, hh: ui.create_date_range_picker(h, p, 20260501, 20260510, x, y, min(w, 520), 42), True),
        ("TimeRange", "🕐", "时间范围", lambda h, p, x, y, w, hh: _make_tr(h, p, x, y, w, hh), True),
        ("DateTimeRange", "🗓️", "日期时间范围", lambda h, p, x, y, w, hh: _make_dtr(h, p, x, y, w, hh), True),
        ("TimePicker", "⏰", "时间选择", lambda h, p, x, y, w, hh: ui.create_timepicker(h, p, 9, 30, x, y, min(w, 520), 42), True),
        ("DateTimePicker", "🗓️", "日期时间", lambda h, p, x, y, w, hh: ui.create_datetimepicker(h, p, 2026, 5, 3, 9, 30, x, y, min(w, 560), 42), True),
        ("TimeSelect", "🕘", "时间候选", lambda h, p, x, y, w, hh: ui.create_time_select(h, p, 10, 0, x, y, min(w, 520), 42), True),
        ("Upload", "📤", "上传入口", lambda h, p, x, y, w, hh: ui.create_upload(h, p, "📤 选择文件", "支持状态读回", [], x, y, min(w, 900), min(hh, 320))),
        ("Image", "🖼️", "五种适配、占位、失败、懒加载、远程和预览列表", lambda h, p, x, y, w, hh: ui.create_image(h, p, "", "图片预览", 0, x, y, min(w, 760), min(hh, 320))),
        ("Carousel", "🎠", "轮播", lambda h, p, x, y, w, hh: ui.create_carousel(h, p, ["第一屏 🚀", "第二屏 🌈", "第三屏 ✨"], 0, 0, x, y, min(w, 760), min(hh, 320))),
    ])


def build_pages(hwnd, root):
    make_page(hwnd, root, "基础布局", "面板、容器、区域、间距和基础视觉元素，适合快速理解单 HWND + D2D 的布局风格。", [
        ("Panel", "🧱", "面板容器", lambda h, p, x, y, w, hh: ui.set_panel_style(h, ui.create_panel(h, p, x, y, w, 58), 0xFFEAF4FF, 0xFF74A7E8, 1.0, 8.0, 8)),
        ("Button", "🚀", "按钮交互", demo_button),
        ("InfoBox", "💡", "信息提示", lambda h, p, x, y, w, hh: ui.create_infobox(h, p, "💡 提示", "支持中文与 emoji", x, y, w, 64)),
        ("Text", "🔤", "文本渲染", lambda h, p, x, y, w, hh: ui.create_text(h, p, "彩色 emoji 文本 🌈", x, y, w, 34)),
        ("Link", "🔗", "链接状态", lambda h, p, x, y, w, hh: ui.create_link(h, p, "打开文档导航 🔗", x, y, w, 30)),
        ("Icon", "⭐", "图标/emoji", lambda h, p, x, y, w, hh: ui.create_icon(h, p, "⭐", x, y, 46, 46)),
        ("Space", "↔️", "占位间距", lambda h, p, x, y, w, hh: ui.create_space(h, p, x, y, 90, 36)),
        ("Container", "📦", "内容容器", lambda h, p, x, y, w, hh: ui.create_container(h, p, x, y, w, 58)),
        ("Header", "📌", "顶栏容器", lambda h, p, x, y, w, hh: ui.create_header(h, p, "📌 顶栏", x, y, w, 58)),
        ("Aside", "🧭", "侧边栏容器", lambda h, p, x, y, w, hh: ui.create_aside(h, p, "🧭 侧边栏", x, y, min(w, 220), 96)),
        ("Main", "📄", "主要区域容器", lambda h, p, x, y, w, hh: ui.create_main(h, p, "📄 主要区域", x, y, w, 76)),
        ("Footer", "✅", "底栏容器", lambda h, p, x, y, w, hh: ui.create_footer(h, p, "✅ 底栏", x, y, w, 58)),
        ("Layout", "🧭", "自动布局", lambda h, p, x, y, w, hh: ui.create_layout(h, p, 0, 8, x, y, w, 46)),
        ("Border", "▣", "边框区域", lambda h, p, x, y, w, hh: ui.create_border(h, p, x, y, w, 58)),
        ("Divider", "➖", "分割线", lambda h, p, x, y, w, hh: ui.create_divider(h, p, "分区", 0, 1, x, y + 18, w, 24)),
        ("Affix", "📌", "固钉区域", lambda h, p, x, y, w, hh: ui.create_affix(h, p, "📌 固钉", "重要操作始终可见", 12, x, y, w, 72)),
        ("Watermark", "💧", "水印背景", lambda h, p, x, y, w, hh: ui.create_watermark(h, p, "new_emoji 💧", 90, 56, x, y, w, 72)),
    ])

    make_page(hwnd, root, "表单输入", "输入、选择、评分和候选建议组件，重点展示键鼠交互与状态读回能力。", [
        ("Checkbox", "☑️", "复选框", lambda h, p, x, y, w, hh: ui.create_checkbox(h, p, "同意协议 ✅", True, x, y, w, 30)),
        ("Radio", "🔘", "单选项", lambda h, p, x, y, w, hh: ui.create_radio(h, p, "方案 A", True, x, y, w, 30)),
        ("Switch", "🎚️", "开关", lambda h, p, x, y, w, hh: ui.create_switch(h, p, "启用通知", True, x, y, w, 32)),
        ("Slider", "🎛️", "滑块", lambda h, p, x, y, w, hh: ui.create_slider(h, p, "满意度", 0, 100, 68, x, y, w, 36)),
        ("InputNumber", "🔢", "数字输入", lambda h, p, x, y, w, hh: ui.create_input_number(h, p, "数量", 8, 0, 99, 1, x, y, w, 36)),
        ("Input", "⌨️", "增强输入", lambda h, p, x, y, w, hh: ui.create_input(h, p, "你好 👋", "请输入内容", x=x, y=y, w=w, h=38)),
        ("InputTag", "🏷️", "标签输入", lambda h, p, x, y, w, hh: ui.create_input_tag(h, p, ["设计", "D2D", "emoji"], "输入标签", x, y, w, 58), True),
        ("Select", "📋", "下拉选择", lambda h, p, x, y, w, hh: ui.create_select(h, p, "选择城市", ["北京", "上海", "深圳"], 1, x, y, w, 36), True),
        ("SelectV2", "🧾", "虚拟选择", lambda h, p, x, y, w, hh: ui.create_select_v2(h, p, "选择组件", ["按钮", "表格", "弹窗", "日历"], 2, 5, x, y, w, 36), True),
        ("Rate", "⭐", "评分", lambda h, p, x, y, w, hh: ui.create_rate(h, p, "体验评分", 4, 5, x, y, w, 36)),
        ("ColorPicker", "🎨", "颜色选择", lambda h, p, x, y, w, hh: ui.create_colorpicker(h, p, "主题色", 0xFF3B82F6, x, y, w, 36), True),
        ("Autocomplete", "🔎", "自动完成", lambda h, p, x, y, w, hh: ui.create_autocomplete(h, p, "北", ["北京", "北海", "北极星"], x, y, w, 38), True),
        ("Mentions", "@", "提及输入", lambda h, p, x, y, w, hh: ui.create_mentions(h, p, "@设计师", ["设计师", "开发者", "测试同学"], x, y, w, 38), True),
        ("Cascader", "🧭", "级联选择", lambda h, p, x, y, w, hh: ui.create_cascader(h, p, [("华东", "上海", "浦东"), ("华南", "广东", "深圳")], ["华东", "上海", "浦东"], x, y, w, 38), True),
    ])

    category_components["表单输入"].append(("InputGroup", "🔗", "组合输入"))
    add_component_detail(
        hwnd, root, "表单输入", "InputGroup", "🔗", "组合输入",
        lambda h, p, x, y, w, hh: ui.create_input_group(
            h, p, "", "请输入关键词",
            prepend={"type": "text", "text": "前置"},
            append={"type": "button", "emoji": "🔎", "text": "", "variant": 1},
            x=x, y=y, w=w, h=38
        ),
        True,
    )

    make_media_page(hwnd, root)

    make_page(hwnd, root, "数据展示", "状态、卡片、表格、统计指标和加载占位，适合后台工具与业务系统。", [
        ("Tag", "🏷️", "标签", lambda h, p, x, y, w, hh: ui.create_tag(h, p, "已完成 🟢", 1, 0, True, x, y, 120, 30)),
        ("Badge", "🔴", "徽标", lambda h, p, x, y, w, hh: ui.create_badge(h, p, "消息", "12", 99, False, x, y, 130, 34)),
        ("Progress", "📈", "进度条", lambda h, p, x, y, w, hh: ui.create_progress(h, p, "构建进度", 76, 1, x, y, w, 36)),
        ("Avatar", "😀", "头像", lambda h, p, x, y, w, hh: ui.create_avatar(h, p, "新", 0, x, y, 50, 50)),
        ("Empty", "📭", "空状态", lambda h, p, x, y, w, hh: ui.create_empty(h, p, "暂无数据 📭", "请稍后刷新", x, y, w, 76)),
        ("Skeleton", "💀", "骨架屏", lambda h, p, x, y, w, hh: ui.create_skeleton(h, p, 3, True, x, y, w, 76)),
        ("Descriptions", "📋", "描述列表", lambda h, p, x, y, w, hh: ui.create_descriptions(h, p, "项目信息", [("组件", "88"), ("许可", "MIT")], 2, True, x, y, w, 76)),
        ("Table", "📊", "表格", lambda h, p, x, y, w, hh: ui.create_table(h, p, ["组件", "状态"], [["Button", "完成"], ["Tabs", "完成"]], True, True, x, y, w, 84)),
        ("InfiniteScroll", "♾️", "无限滚动", lambda h, p, x, y, w, hh: ui.create_infinite_scroll(h, p, [("📌 任务 01", "触底自动加载", "进行中"), ("📌 任务 02", "支持状态读回", "已同步")], x, y, w, 112)),
        ("Card", "🪪", "基础、列表、图片和插槽卡片", lambda h, p, x, y, w, hh: ui.create_card(h, p, "🪪 项目卡片", "用于组织信息块", 1, x, y, w, 84)),
        ("Collapse", "📂", "折叠面板", lambda h, p, x, y, w, hh: ui.create_collapse(h, p, [("基础组件", "按钮/文本/面板"), ("反馈组件", "弹窗/提示/通知")], 0, True, x, y, w, 84)),
        ("Timeline", "🕒", "时间线", lambda h, p, x, y, w, hh: ui.create_timeline(h, p, [("09:00", "🚀 启动", 0, "🚀"), ("10:30", "✅ 封装", 1, "✅"), ("14:20", "📦 开源", 2, "📦")], x, y, w, 84)),
        ("Statistic", "📌", "统计数值", lambda h, p, x, y, w, hh: ui.create_statistic(h, p, "组件数", "88", suffix="个", x=x, y=y, w=w, h=62)),
        ("KPI Card", "🎯", "指标卡", lambda h, p, x, y, w, hh: ui.create_kpi_card(h, p, "完成率", "100%", "全部组件已封装", x=x, y=y, w=w, h=76)),
        ("Trend", "📈", "趋势", lambda h, p, x, y, w, hh: ui.create_trend(h, p, "星标增长", "+128", "12%", "本周", 1, x, y, w, 62)),
        ("StatusDot", "🟢", "状态点", lambda h, p, x, y, w, hh: ui.create_status_dot(h, p, "运行正常", "DLL 已加载", 1, x, y, w, 48)),
    ])

    make_page(hwnd, root, "图表导航", "图表、菜单、锚点、页头和标签页，展示复杂信息组织能力。", [
        ("Gauge", "🎯", "仪表盘", lambda h, p, x, y, w, hh: ui.create_gauge(h, p, "质量分", 92, "运行良好", 1, x, y, w, 86)),
        ("RingProgress", "⭕", "环形进度", lambda h, p, x, y, w, hh: ui.create_ring_progress(h, p, "完成度", 82, "组件完成", 1, x, y, w, 86)),
        ("BulletProgress", "🧭", "子弹进度", lambda h, p, x, y, w, hh: ui.create_bullet_progress(h, p, "目标", "发布准备", 72, 90, 1, x, y, w, 60)),
        ("LineChart", "📈", "折线图", lambda h, p, x, y, w, hh: ui.create_line_chart(h, p, "访问趋势", [("周一", 12), ("周二", 18), ("周三", 24)], 0, x, y, w, 78)),
        ("BarChart", "📊", "柱状图", lambda h, p, x, y, w, hh: ui.create_bar_chart(h, p, "组件排行", [("表单", 12), ("反馈", 9), ("导航", 7)], x, y, w, 78)),
        ("DonutChart", "🍩", "环形图", lambda h, p, x, y, w, hh: ui.create_donut_chart(h, p, "分类占比", [("基础", 14), ("表单", 14), ("反馈", 12)], x, y, w, 78)),
        ("Dropdown", "📂", "下拉菜单", lambda h, p, x, y, w, hh: ui.create_dropdown(h, p, "📂 更多操作", ["复制", "导出", "删除"], 0, x, y, w, 36)),
        ("Menu", "🧭", "菜单", lambda h, p, x, y, w, hh: ui.create_menu(h, p, ["首页", "组件", "文档"], 1, 0, x, y, w, 40)),
        ("Anchor", "⚓", "锚点", lambda h, p, x, y, w, hh: ui.create_anchor(h, p, ["基础", "表单", "反馈"], 0, x, y, w, 80)),
        ("Backtop", "⬆️", "返回顶部", lambda h, p, x, y, w, hh: ui.create_backtop(h, p, "⬆️", x, y, 44, 44)),
        ("Segmented", "🔀", "分段控制", lambda h, p, x, y, w, hh: ui.create_segmented(h, p, ["日", "周", "月"], 1, x, y, w, 36)),
        ("PageHeader", "📄", "页头", lambda h, p, x, y, w, hh: ui.create_pageheader(h, p, "组件详情", "返回总览", "返回", x, y, w, 62)),
        ("Breadcrumb", "🍞", "面包屑", lambda h, p, x, y, w, hh: ui.create_breadcrumb(h, p, ["首页", "组件", "导航"], "/", 2, x, y, w, 32)),
        ("Tabs", "📑", "标签页", lambda h, p, x, y, w, hh: ui.create_tabs(h, p, ["预览", "代码", "文档"], 0, 0, x, y, w, 38)),
    ])

    make_page(hwnd, root, "反馈流程", "提示、弹层、确认、引导、分页和步骤条，覆盖常见业务反馈流程。", [
        ("Pagination", "📚", "分页", lambda h, p, x, y, w, hh: ui.create_pagination(h, p, 128, 10, 3, x, y, w, 38)),
        ("Steps", "👣", "步骤条全样式", lambda h, p, x, y, w, hh: ui.create_steps(h, p, ["创建", "构建", "发布"], 1, x, y, w, 70)),
        ("Alert", "🚨", "警告提示", lambda h, p, x, y, w, hh: ui.create_alert(h, p, "保存成功", "配置已经同步", 1, 0, True, x, y, w, 58)),
        ("Result", "✅", "结果页", lambda h, p, x, y, w, hh: ui.create_result(h, p, "操作成功", "所有组件加载完成", 1, x, y, w, 86)),
        ("Message", "💬", "消息提示", demo_message_service),
        ("MessageBox", "🪟", "消息框", demo_messagebox_service),
        ("Notification", "🔔", "通知", demo_notification_service),
        ("Loading", "⏳", "加载", lambda h, p, x, y, w, hh: ui.create_loading(h, p, "加载组件中", True, x, y, w, 76)),
        ("Dialog", "💬", "对话框", demo_dialog_button),
        ("Drawer", "📚", "抽屉", demo_drawer_button),
        ("Tooltip", "💭", "文字提示", lambda h, p, x, y, w, hh: ui.create_tooltip(h, p, "悬停我 💭", "这是 Tooltip 内容", 2, x, y, 130, 36)),
        ("Popover", "🗯️", "气泡卡片", lambda h, p, x, y, w, hh: ui.create_popover(h, p, "打开气泡", "Popover", "支持标题和内容", 3, x, y, 140, 36)),
        ("Popconfirm", "❓", "确认气泡", lambda h, p, x, y, w, hh: ui.create_popconfirm(h, p, "删除确认", "确认操作", "是否继续？", "确定", "取消", 3, x, y, 140, 36)),
        ("Tour", "🧭", "引导", lambda h, p, x, y, w, hh: ui.create_tour(h, p, ["第一步：选择分类", "第二步：查看组件", "第三步：运行示例"], 0, True, x, y, w, 86)),
    ])


def main():
    global gallery_hwnd, nav_menu_id
    hwnd = ui.create_window("🧩 new_emoji 组件总览", 20, 0, WINDOW_W, WINDOW_H)
    gallery_hwnd = hwnd
    root = ui.create_container(hwnd, 0, 0, 0, ROOT_W, ROOT_H)
    add_text(hwnd, root, "🧩 new_emoji 组件总览", 28, 18, 250, 34, TEXT)
    add_text(hwnd, root, "单 HWND + 纯 D2D 渲染\n中文/emoji · 主题/DPI\n推荐演示 87 个", 28, 54, 250, 72, MUTED)
    global status_text_id
    status_text_id = add_text(hwnd, root, "正在加载组件演示...", PAGE_X + 20, ROOT_H + 10, PAGE_W - 40, 28, MUTED)

    theme_box = ui.create_panel(hwnd, root, 22, 112, 380, 70)
    ui.set_panel_style(hwnd, theme_box, SURFACE_2, BORDER, 1.0, 8.0, 8)
    register_panel(theme_box, "surface_2", "border", 1.0, 8.0, 8)
    add_text(hwnd, theme_box, "🎨 主题", 14, 12, 76, 24, TEXT)
    light = ui.create_button(hwnd, theme_box, "☀️", "浅色", 96, 18, 78, 32)
    dark = ui.create_button(hwnd, theme_box, "🌙", "深色", 184, 18, 78, 32)
    system = ui.create_button(hwnd, theme_box, "💻", "系统", 272, 18, 78, 32)
    set_click(hwnd, light, lambda _eid: apply_gallery_theme(hwnd, 0))
    set_click(hwnd, dark, lambda _eid: apply_gallery_theme(hwnd, 1))
    set_click(hwnd, system, lambda _eid: apply_gallery_theme(hwnd, 0))

    build_pages(hwnd, root)
    build_nav_menu_model()

    nav_y = 196
    nav_h = ROOT_H - nav_y - 20
    nav_panel = ui.create_panel(hwnd, root, 22, nav_y, 380, nav_h)
    ui.set_panel_style(hwnd, nav_panel, 0xFF1F2338, BORDER_SOFT, 1.0, 8.0, 8)
    register_panel(nav_panel, "nav", "border_soft", 1.0, 8.0, 8)
    add_text(hwnd, nav_panel, "🧭 组件导航", 14, 12, 180, 24, TEXT)
    nav_menu_id = ui.create_menu(hwnd, nav_panel, nav_menu_items, 0, 1, 12, 46, 356, nav_h - 62)
    ui.set_menu_item_meta(hwnd, nav_menu_id, nav_menu_icons, [], [], [], nav_menu_commands)
    ui.set_menu_expanded(hwnd, nav_menu_id, nav_menu_expanded)
    ui.set_menu_select_callback(hwnd, nav_menu_id, keep_callback(on_gallery_nav_select))
    apply_nav_menu_theme(hwnd)

    page_aliases = {
        "foundation": "基础布局",
        "form": "表单输入",
        "media": "选择媒体",
        "data": "数据展示",
        "charts": "图表导航",
        "feedback": "反馈流程",
    }
    start_category = page_aliases.get(START_PAGE.lower(), START_PAGE) if START_PAGE else next(iter(category_components))
    if start_category not in category_components:
        start_category = next(iter(category_components))
    start_component = START_COMPONENT.strip()
    component_names = [name for name, _emoji, _summary in category_components[start_category]]
    if start_component and start_component in component_names:
        show_component(hwnd, start_category, start_component)
    else:
        show_category(hwnd, start_category)
    if START_THEME.lower() in ("light", "0", "浅色"):
        apply_gallery_theme(hwnd, 0)
    elif START_THEME.lower() in ("dark", "1", "深色"):
        apply_gallery_theme(hwnd, 1)
    ui.dll.EU_ShowWindow(hwnd, 1)
    print(f"new_emoji 组件总览已启动：推荐演示 87 个组件，窗口将保持 {VISIBLE_SECONDS} 秒。")
    if gallery_errors:
        print("以下组件卡片创建失败：")
        for name, error in gallery_errors:
            print(f"- {name}: {error}")
    else:
        print("全部组件卡片创建成功。")
    message_loop(VISIBLE_SECONDS)


if __name__ == "__main__":
    main()
