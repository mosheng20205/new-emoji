"""
new_emoji 84 component gallery.

Run from the repository root:
    python examples/python/component_gallery.py
"""
import base64
import ctypes
import os
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
nav_buttons = {}
category_buttons = {}
component_buttons = {}
category_components = {}
panel_roles = []
text_roles = []
gallery_errors = []
status_text_id = 0
current_page_name = ""
current_category_name = ""
current_theme_mode = 1
upload_sample_cache = None

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
    if current_category_name and "/" in current_page_name:
        _category, component = current_page_name.split("/", 1)
        show_component(hwnd, current_category_name, component)


def show_component(hwnd, category_name, component_name):
    global current_page_name, current_category_name
    colors = palette()
    page_name = f"{category_name}/{component_name}"
    current_page_name = page_name
    current_category_name = category_name
    for name, page_id in page_ids:
        ui.set_element_visible(hwnd, page_id, name == page_name)
    for name, button_id in category_buttons.items():
        ui.set_element_color(hwnd, button_id, colors["active"] if name == category_name else colors["nav_bg"], colors["active_text"] if name == category_name else colors["muted"])
    for category, buttons in component_buttons.items():
        for name, button_id in buttons.items():
            ui.set_element_visible(hwnd, button_id, category == category_name)
            if category == category_name and name == component_name:
                ui.set_element_color(hwnd, button_id, colors["active"], colors["active_text"])
            elif category == category_name:
                ui.set_element_color(hwnd, button_id, colors["nav_item"], colors["muted"])
    if status_text_id:
        ui.set_element_text(hwnd, status_text_id, f"当前组件：{category_name} / {component_name} · 共 84 个组件 · 左侧二级菜单切换演示")
        ui.set_element_color(hwnd, status_text_id, 0, colors["muted"])


def show_category(hwnd, category_name):
    components = category_components.get(category_name, [])
    if components:
        show_component(hwnd, category_name, components[0][0])


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
    outer = add_demo_panel(hwnd, stage, "📦 外层容器", 28, 30, w - 56, 300)
    ui.set_panel_style(hwnd, outer, palette()["panel_canvas"], palette()["panel_canvas_border"], 1.0, 10.0, 12)
    register_panel(outer, "panel_canvas", "panel_canvas_border", 1.0, 10.0, 12)
    add_text(hwnd, outer, "外层容器", 28, 66, 160, 24, TEXT)
    add_text(hwnd, outer, "用于承载内容区、卡片区或多列组合。", 28, 98, 280, 24, MUTED)

    add_themed_panel(hwnd, outer, 26, 136, w - 108, 118, "panel_neutral", "panel_neutral_border", 1.0, 10.0, 10)
    inner = ui.create_container(hwnd, outer, 26, 136, w - 108, 118)
    add_themed_panel(hwnd, inner, 18, 18, 220, 82, "panel_blue", "panel_blue_border", 1.0, 8.0, 10)
    add_themed_panel(hwnd, inner, 260, 18, 220, 82, "panel_gold", "panel_gold_border", 1.0, 8.0, 10)
    add_themed_panel(hwnd, inner, 502, 18, 220, 82, "panel_green", "panel_green_border", 1.0, 8.0, 10)
    add_role_text(hwnd, inner, "内容块 A", 36, 48, 120, 24, "panel_blue_text")
    add_role_text(hwnd, inner, "内容块 B", 278, 48, 120, 24, "panel_gold_text")
    add_role_text(hwnd, inner, "内容块 C", 520, 48, 120, 24, "panel_green_text")

    note = add_demo_panel(hwnd, stage, "🧩 容器用途说明", 28, 354, w - 56, 150)
    add_text(hwnd, note, "Container 更像一个透明骨架。它本身负责收纳和分层，真正的视觉通常来自内部内容卡、布局块和状态块。", 28, 72, w - 116, 44, MUTED)


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
    base = add_demo_panel(hwnd, stage, "🔗 prepend / append 组合输入", 28, 30, w - 56, 260)
    ui.create_input_group(hwnd, base, value="", placeholder="请输入域名",
                          prepend={"type": "text", "text": "Http://"},
                          append={"type": "text", "text": ".com"},
                          x=36, y=76, w=420, h=40)
    ui.create_input_group(hwnd, base, value="", placeholder="请输入内容",
                          prepend={"type": "select", "items": [("餐厅名", "1"), ("订单号", "2"), ("用户电话", "3")], "selected": 0, "placeholder": "请选择"},
                          append={"type": "button", "emoji": "🔎", "text": "", "variant": 1},
                          x=492, y=76, w=540, h=40)
    ui.create_input_group(hwnd, base, value="可清空内容", placeholder="组合输入",
                          prepend={"type": "text", "text": "前置"},
                          append={"type": "button", "emoji": "🚀", "text": "发送", "variant": 1},
                          size=1, clearable=True, x=36, y=146, w=460, h=40)
    ui.create_input_group(hwnd, base, value="小尺寸组合", placeholder="mini 组",
                          prepend={"type": "text", "text": "标签"},
                          append={"type": "button", "emoji": "✅", "text": "", "variant": 2},
                          size=3, x=522, y=150, w=360, h=30)
    add_text(hwnd, base, "InputGroup 会暴露内部 element id，外部可以继续用现有 Input / Button / Select 的 Set/Get 和回调。", 36, 212, 900, 24, MUTED)


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
    card = add_demo_panel(hwnd, stage, "📚 数据列表分页", 28, 30, w - 56, 260)
    ui.create_pagination(hwnd, card, 128, 10, 3, 30, 72, min(w - 116, 860), 42)
    ui.create_pagination(hwnd, card, 520, 20, 8, 30, 140, min(w - 116, 920), 42)
    add_text(hwnd, card, "用于表格、日志、搜索结果等长列表场景，可展示页码、跳转和总数。", 30, 202, w - 116, 30, MUTED)
    table = add_demo_panel(hwnd, stage, "📊 配套列表预览", 28, 320, w - 56, 220)
    ui.create_table(hwnd, table, ["组件", "分类", "状态"], [["Pagination", "反馈流程", "当前页 3"], ["Table", "数据展示", "可分页"], ["Search", "业务场景", "结果 128 条"]], True, True, 30, 70, min(w - 116, 760), 120)


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


SPECIAL_SHOWCASES = {
    "Panel": showcase_panel,
    "Button": showcase_button,
    "Link": showcase_link,
    "Radio": showcase_radio,
    "Container": showcase_container,
    "Layout": showcase_layout,
    "Watermark": showcase_watermark,
    "Checkbox": showcase_checkbox,
    "Input": showcase_input,
    "InputGroup": showcase_input_group,
    "InputNumber": showcase_inputnumber,
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
    "Gauge": showcase_gauge,
    "Pagination": showcase_pagination,
    "Upload": showcase_upload,
    "Message": showcase_message,
    "MessageBox": showcase_messagebox,
    "Notification": showcase_notification,
    "Dialog": showcase_dialog,
    "Tooltip": showcase_tooltip,
    "Popover": showcase_popover,
    "Popconfirm": showcase_popconfirm,
}


COMPACT_SHOWCASE = {
    "Button", "EditBox", "InfoBox", "Text", "Link", "Icon", "Space", "Checkbox", "Radio", "Switch",
    "Slider", "Input", "InputGroup", "Rate", "Tag", "Badge", "Progress", "Avatar", "Statistic",
    "StatusDot", "Backtop", "Segmented", "Scrollbar", "Breadcrumb", "Tabs", "Alert", "Loading",
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


def make_media_page(hwnd, root):
    make_page(hwnd, root, "选择媒体", "日期时间、树形选择、穿梭框、上传、图片和轮播等较完整的业务组件。", [
        ("Calendar", "📅", "日历", lambda h, p, x, y, w, hh: ui.create_calendar(h, p, 2026, 5, 3, x, y, min(w, 920), min(hh, 420))),
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
        ("Image", "🖼️", "图片容器", lambda h, p, x, y, w, hh: ui.create_image(h, p, "", "图片预览", 0, x, y, min(w, 760), min(hh, 320))),
        ("Carousel", "🎠", "轮播", lambda h, p, x, y, w, hh: ui.create_carousel(h, p, ["第一屏 🚀", "第二屏 🌈", "第三屏 ✨"], 0, 0, x, y, min(w, 760), min(hh, 320))),
    ])


def build_pages(hwnd, root):
    make_page(hwnd, root, "基础布局", "窗口、布局、文本和基础视觉元素，适合快速理解单 HWND + D2D 的渲染风格。", [
        ("Panel", "🧱", "面板容器", lambda h, p, x, y, w, hh: ui.set_panel_style(h, ui.create_panel(h, p, x, y, w, 58), 0xFFEAF4FF, 0xFF74A7E8, 1.0, 8.0, 8)),
        ("Button", "🚀", "按钮交互", demo_button),
        ("EditBox", "✍️", "基础编辑框", lambda h, p, x, y, w, hh: (lambda eid: ui.set_editbox_text(h, eid, "中文输入 + emoji 🎉"))(ui.create_editbox(h, p, x, y, w, 34))),
        ("InfoBox", "💡", "信息提示", lambda h, p, x, y, w, hh: ui.create_infobox(h, p, "💡 提示", "支持中文与 emoji", x, y, w, 64)),
        ("Text", "🔤", "文本渲染", lambda h, p, x, y, w, hh: ui.create_text(h, p, "彩色 emoji 文本 🌈", x, y, w, 34)),
        ("Link", "🔗", "链接状态", lambda h, p, x, y, w, hh: ui.create_link(h, p, "打开文档导航 🔗", x, y, w, 30)),
        ("Icon", "⭐", "图标/emoji", lambda h, p, x, y, w, hh: ui.create_icon(h, p, "⭐", x, y, 46, 46)),
        ("Space", "↔️", "占位间距", lambda h, p, x, y, w, hh: ui.create_space(h, p, x, y, 90, 36)),
        ("Container", "📦", "内容容器", lambda h, p, x, y, w, hh: ui.create_container(h, p, x, y, w, 58)),
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
        ("InputTag", "🏷️", "标签输入", lambda h, p, x, y, w, hh: ui.create_input_tag(h, p, ["设计", "D2D", "emoji"], "输入标签", x, y, w, 42), True),
        ("Select", "📋", "下拉选择", lambda h, p, x, y, w, hh: ui.create_select(h, p, "选择城市", ["北京", "上海", "深圳"], 1, x, y, w, 36), True),
        ("SelectV2", "🧾", "虚拟选择", lambda h, p, x, y, w, hh: ui.create_select_v2(h, p, "选择组件", ["按钮", "表格", "弹窗", "日历"], 2, 5, x, y, w, 36), True),
        ("Rate", "⭐", "评分", lambda h, p, x, y, w, hh: ui.create_rate(h, p, "体验评分", 4, 5, x, y, w, 36)),
        ("ColorPicker", "🎨", "颜色选择", lambda h, p, x, y, w, hh: ui.create_colorpicker(h, p, "主题色", 0xFF3B82F6, x, y, w, 36), True),
        ("Autocomplete", "🔎", "自动完成", lambda h, p, x, y, w, hh: ui.create_autocomplete(h, p, "北", ["北京", "北海", "北极星"], x, y, w, 38), True),
        ("Mentions", "@", "提及输入", lambda h, p, x, y, w, hh: ui.create_mentions(h, p, "@设计师", ["设计师", "开发者", "测试同学"], x, y, w, 38), True),
        ("Cascader", "🪜", "级联选择", lambda h, p, x, y, w, hh: ui.create_cascader(h, p, ["华东/上海/浦东", "华南/广东/深圳"], [0, 0, 0], x, y, w, 38), True),
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
        ("Descriptions", "📋", "描述列表", lambda h, p, x, y, w, hh: ui.create_descriptions(h, p, "项目信息", [("组件", "84"), ("许可", "MIT")], 2, True, x, y, w, 76)),
        ("Table", "📊", "表格", lambda h, p, x, y, w, hh: ui.create_table(h, p, ["组件", "状态"], [["Button", "完成"], ["Tabs", "完成"]], True, True, x, y, w, 84)),
        ("Card", "🪪", "卡片", lambda h, p, x, y, w, hh: ui.create_card(h, p, "🪪 项目卡片", "用于组织信息块", 1, x, y, w, 84)),
        ("Collapse", "📂", "折叠面板", lambda h, p, x, y, w, hh: ui.create_collapse(h, p, [("基础组件", "按钮/文本/面板"), ("反馈组件", "弹窗/提示/通知")], 0, True, x, y, w, 84)),
        ("Timeline", "🕒", "时间线", lambda h, p, x, y, w, hh: ui.create_timeline(h, p, ["启动", "封装", "开源"], x, y, w, 84)),
        ("Statistic", "📌", "统计数值", lambda h, p, x, y, w, hh: ui.create_statistic(h, p, "组件数", "84", suffix="个", x=x, y=y, w=w, h=62)),
        ("KPI Card", "🎯", "指标卡", lambda h, p, x, y, w, hh: ui.create_kpi_card(h, p, "完成率", "100%", "全部组件已封装", x=x, y=y, w=w, h=76)),
        ("Trend", "📈", "趋势", lambda h, p, x, y, w, hh: ui.create_trend(h, p, "星标增长", "+128", "12%", "本周", 1, x, y, w, 62)),
        ("StatusDot", "🟢", "状态点", lambda h, p, x, y, w, hh: ui.create_status_dot(h, p, "运行正常", "DLL 已加载", 1, x, y, w, 48)),
    ])

    make_page(hwnd, root, "图表导航", "图表、菜单、锚点、页头、滚动与标签页，展示复杂信息组织能力。", [
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
        ("Scrollbar", "🧵", "滚动条", lambda h, p, x, y, w, hh: ui.create_scrollbar(h, p, 35, 100, 0, x, y, w, 28)),
        ("Breadcrumb", "🍞", "面包屑", lambda h, p, x, y, w, hh: ui.create_breadcrumb(h, p, ["首页", "组件", "导航"], "/", 2, x, y, w, 32)),
        ("Tabs", "📑", "标签页", lambda h, p, x, y, w, hh: ui.create_tabs(h, p, ["预览", "代码", "文档"], 0, 0, x, y, w, 38)),
    ])

    make_page(hwnd, root, "反馈流程", "提示、弹层、确认、引导、分页和步骤条，覆盖常见业务反馈流程。", [
        ("Pagination", "📚", "分页", lambda h, p, x, y, w, hh: ui.create_pagination(h, p, 128, 10, 3, x, y, w, 38)),
        ("Steps", "👣", "步骤条", lambda h, p, x, y, w, hh: ui.create_steps(h, p, ["创建", "构建", "发布"], 1, x, y, w, 70)),
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
    hwnd = ui.create_window("🧩 new_emoji 84 个组件总览", 20, 0, WINDOW_W, WINDOW_H)
    root = ui.create_container(hwnd, 0, 0, 0, ROOT_W, ROOT_H)
    add_text(hwnd, root, "🧩 new_emoji 组件总览", 28, 18, 250, 34, TEXT)
    add_text(hwnd, root, "单 HWND + 纯 D2D 渲染\n中文/emoji · 主题/DPI\n84 个组件", 28, 54, 250, 72, MUTED)
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

    nav_panel = ui.create_panel(hwnd, root, 22, 196, 380, 314)
    ui.set_panel_style(hwnd, nav_panel, 0xFF1F2338, BORDER_SOFT, 1.0, 8.0, 8)
    register_panel(nav_panel, "nav", "border_soft", 1.0, 8.0, 8)
    add_text(hwnd, nav_panel, "📁 一级分类", 14, 12, 180, 24, TEXT)

    component_panel = ui.create_panel(hwnd, root, 22, 526, 380, 350)
    ui.set_panel_style(hwnd, component_panel, 0xFF1F2338, BORDER_SOFT, 1.0, 8.0, 8)
    register_panel(component_panel, "nav", "border_soft", 1.0, 8.0, 8)
    add_text(hwnd, component_panel, "🧩 二级组件", 14, 12, 180, 24, TEXT)

    build_pages(hwnd, root)

    y = 46
    for name in category_components:
        btn = ui.create_button(hwnd, nav_panel, "📁", name, 18, y, 344, 36)
        category_buttons[name] = btn
        set_click(hwnd, btn, lambda _eid, category=name: show_category(hwnd, category))
        y += 43

    for category, components in category_components.items():
        buttons = {}
        for i, (name, emoji, _summary) in enumerate(components):
            col = i % 2
            row = i // 2
            x = 18 + col * 172
            y = 46 + row * 36
            btn = ui.create_button(hwnd, component_panel, emoji, name, x, y, 162, 30)
            ui.set_element_visible(hwnd, btn, False)
            buttons[name] = btn
            set_click(hwnd, btn, lambda _eid, c=category, n=name: show_component(hwnd, c, n))
        component_buttons[category] = buttons

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
    print(f"new_emoji 组件总览已启动：84 个组件，窗口将保持 {VISIBLE_SECONDS} 秒。")
    if gallery_errors:
        print("以下组件卡片创建失败：")
        for name, error in gallery_errors:
            print(f"- {name}: {error}")
    else:
        print("全部组件卡片创建成功。")
    message_loop(VISIBLE_SECONDS)


if __name__ == "__main__":
    main()
