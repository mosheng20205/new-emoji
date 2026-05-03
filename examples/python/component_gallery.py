"""
new_emoji 82 component gallery.

Run from the repository root:
    python examples/python/component_gallery.py
"""
import ctypes
import os
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


@ui.MessageBoxCallback
def on_gallery_messagebox(_messagebox_id, _result):
    pass


def keep_callback(cb):
    callbacks.append(cb)
    return cb


def set_click(hwnd, element_id, fn):
    cb = keep_callback(ui.ClickCallback(fn))
    ui.dll.EU_SetElementClickCallback(hwnd, element_id, cb)


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
        ui.set_element_text(hwnd, status_text_id, f"当前组件：{category_name} / {component_name} · 共 82 个组件 · 左侧二级菜单切换演示")
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
    "Autocomplete": showcase_autocomplete,
    "Tag": showcase_tag,
    "Gauge": showcase_gauge,
    "Pagination": showcase_pagination,
}


COMPACT_SHOWCASE = {
    "Button", "EditBox", "InfoBox", "Text", "Link", "Icon", "Space", "Checkbox", "Radio", "Switch",
    "Slider", "InputNumber", "Input", "InputGroup", "Rate", "Tag", "Badge", "Progress", "Avatar", "Statistic",
    "StatusDot", "Backtop", "Segmented", "Scrollbar", "Breadcrumb", "Tabs", "Alert", "Loading",
    "Tooltip", "Popover", "Popconfirm",
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
        ("Descriptions", "📋", "描述列表", lambda h, p, x, y, w, hh: ui.create_descriptions(h, p, "项目信息", [("组件", "82"), ("许可", "MIT")], 2, True, x, y, w, 76)),
        ("Table", "📊", "表格", lambda h, p, x, y, w, hh: ui.create_table(h, p, ["组件", "状态"], [["Button", "完成"], ["Tabs", "完成"]], True, True, x, y, w, 84)),
        ("Card", "🪪", "卡片", lambda h, p, x, y, w, hh: ui.create_card(h, p, "🪪 项目卡片", "用于组织信息块", 1, x, y, w, 84)),
        ("Collapse", "📂", "折叠面板", lambda h, p, x, y, w, hh: ui.create_collapse(h, p, [("基础组件", "按钮/文本/面板"), ("反馈组件", "弹窗/提示/通知")], 0, True, x, y, w, 84)),
        ("Timeline", "🕒", "时间线", lambda h, p, x, y, w, hh: ui.create_timeline(h, p, ["启动", "封装", "开源"], x, y, w, 84)),
        ("Statistic", "📌", "统计数值", lambda h, p, x, y, w, hh: ui.create_statistic(h, p, "组件数", "82", suffix="个", x=x, y=y, w=w, h=62)),
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
        ("Notification", "🔔", "通知", lambda h, p, x, y, w, hh: ui.create_notification(h, p, "构建完成", "Release DLL 已生成", 1, True, x, y, w, 72)),
        ("Loading", "⏳", "加载", lambda h, p, x, y, w, hh: ui.create_loading(h, p, "加载组件中", True, x, y, w, 76)),
        ("Dialog", "💬", "对话框", demo_dialog_button),
        ("Drawer", "📚", "抽屉", demo_drawer_button),
        ("Tooltip", "💭", "文字提示", lambda h, p, x, y, w, hh: ui.create_tooltip(h, p, "悬停我 💭", "这是 Tooltip 内容", 2, x, y, 130, 36)),
        ("Popover", "🗯️", "气泡卡片", lambda h, p, x, y, w, hh: ui.create_popover(h, p, "打开气泡", "Popover", "支持标题和内容", 3, x, y, 140, 36)),
        ("Popconfirm", "❓", "确认气泡", lambda h, p, x, y, w, hh: ui.create_popconfirm(h, p, "删除确认", "确认操作", "是否继续？", "确定", "取消", 3, x, y, 140, 36)),
        ("Tour", "🧭", "引导", lambda h, p, x, y, w, hh: ui.create_tour(h, p, ["第一步：选择分类", "第二步：查看组件", "第三步：运行示例"], 0, True, x, y, w, 86)),
    ])


def main():
    hwnd = ui.create_window("🧩 new_emoji 82 个组件总览", 20, 0, WINDOW_W, WINDOW_H)
    root = ui.create_container(hwnd, 0, 0, 0, ROOT_W, ROOT_H)
    add_text(hwnd, root, "🧩 new_emoji 组件总览", 28, 18, 250, 34, TEXT)
    add_text(hwnd, root, "单 HWND + 纯 D2D 渲染\n中文/emoji · 主题/DPI\n82 个组件", 28, 54, 250, 72, MUTED)
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
    print(f"new_emoji 组件总览已启动：82 个组件，窗口将保持 {VISIBLE_SECONDS} 秒。")
    if gallery_errors:
        print("以下组件卡片创建失败：")
        for name, error in gallery_errors:
            print(f"- {name}: {error}")
    else:
        print("全部组件卡片创建成功。")
    message_loop(VISIBLE_SECONDS)


if __name__ == "__main__":
    main()
