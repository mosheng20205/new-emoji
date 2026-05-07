import ctypes
import time
from ctypes import wintypes

import new_emoji_ui as ui


STATE = {
    "root": 0,
    "tab_bg": 0,
    "toolbar_bg": 0,
    "tabs": 0,
    "new_tab": 0,
    "omnibox": 0,
    "viewport": 0,
    "min": 0,
    "max": 0,
    "close": 0,
    "download": 0,
    "extensions": 0,
    "more": 0,
    "download_popup": 0,
    "extensions_popup": 0,
    "more_menu": 0,
    "omnibox_menu": 0,
    "tabs_menu": 0,
    "viewport_menu": 0,
    "tab_count": 1,
}

TAB_LEFT = 16
TAB_Y = 4
TAB_WIDTH = 220
NEW_TAB_GAP = 8
OMNIBOX_X = 132
TOOLBAR_BUTTON_SIZE = 34
TOOLBAR_BUTTON_GAP = 8
TOOLBAR_RIGHT_MARGIN = 24


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


@ui.TextCallback
def on_commit(element_id, text_ptr, text_len):
    text = bytes(text_ptr[:text_len]).decode("utf-8", errors="replace") if text_len > 0 else ""
    print(f"[地址栏] 提交：{text}")


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    scale = window_scale(hwnd)
    layout_shell(hwnd, int(width / scale), int(height / scale))


@ui.ClickCallback
def on_new_tab(element_id):
    hwnd = STATE.get("hwnd", 0)
    tabs = STATE.get("tabs", 0)
    if not hwnd or not tabs:
        return
    STATE["tab_count"] += 1
    index = STATE["tab_count"] - 1
    ui.add_tabs_item(hwnd, tabs, f"新标签页 {STATE['tab_count']}")
    ui.set_tabs_item_icon(hwnd, tabs, index, "🌐")
    ui.set_tabs_item_closable(hwnd, tabs, index, True)
    layout_shell(hwnd, STATE.get("layout_w", 1160), STATE.get("layout_h", 760))


@ui.ValueCallback
def on_tab_closed(element_id, closed_index, count, active_index):
    STATE["tab_count"] = max(1, int(count))
    hwnd = STATE.get("hwnd", 0)
    if hwnd:
        layout_shell(hwnd, STATE.get("layout_w", 1160), STATE.get("layout_h", 760))


def pump_messages():
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    running = True
    while running:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                running = False
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def set_bounds(hwnd, element_id, x, y, w, h):
    if element_id:
        ui.dll.EU_SetElementBounds(hwnd, element_id, x, y, w, h)


def window_scale(hwnd):
    try:
        dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
        return max(1.0, float(dpi) / 96.0)
    except Exception:
        return 1.0


def icon_button(hwnd, parent, icon, tip, x, y, checked=False, badge="", command=0):
    btn = ui.create_icon_button(hwnd, parent, icon, tip, x, y, 34, 34)
    ui.set_icon_button_shape(hwnd, btn, 1, 17)
    ui.set_icon_button_icon_size(hwnd, btn, 17)
    ui.set_icon_button_colors(
        hwnd, btn,
        normal_bg=0x00000000,
        hover_bg=0x1AFFFFFF,
        pressed_bg=0x26FFFFFF,
        checked_bg=0x26000000,
        disabled_bg=0x00000000,
        icon_color=0xFFE8EAED,
        disabled_icon_color=0xFF5F6368,
    )
    if checked:
        ui.set_icon_button_checked(hwnd, btn, True)
    if badge:
        ui.set_icon_button_badge(hwnd, btn, badge, True)
    if command:
        ui.set_element_window_command(hwnd, btn, command)
    return btn


def caption_button(hwnd, parent, icon, tip, x, y, command, close=False):
    btn = ui.create_icon_button(hwnd, parent, icon, tip, x, y, 46, 32)
    ui.set_icon_button_shape(hwnd, btn, 0, 0)
    ui.set_icon_button_padding(hwnd, btn, 0, 0, 0, 0)
    ui.set_icon_button_icon_size(hwnd, btn, 16)
    ui.set_icon_button_colors(
        hwnd, btn,
        normal_bg=0x00000000,
        hover_bg=0xFFE81123 if close else 0x1AFFFFFF,
        pressed_bg=0xFFD7001B if close else 0x26FFFFFF,
        checked_bg=0x00000000,
        disabled_bg=0x00000000,
        icon_color=0xFFE8EAED,
        disabled_icon_color=0xFF5F6368,
    )
    ui.set_element_window_command(hwnd, btn, command)
    return btn


def new_tab_button(hwnd, parent, x, y):
    btn = ui.create_icon_button(hwnd, parent, "+", "新建标签页", x, y, 30, 30)
    ui.set_icon_button_shape(hwnd, btn, 1, 15)
    ui.set_icon_button_padding(hwnd, btn, 0, 0, 0, 0)
    ui.set_icon_button_icon_size(hwnd, btn, 18)
    ui.set_icon_button_colors(
        hwnd, btn,
        normal_bg=0x00000000,
        hover_bg=0x1AFFFFFF,
        pressed_bg=0x26FFFFFF,
        checked_bg=0x00000000,
        disabled_bg=0x00000000,
        icon_color=0xFFE8EAED,
        disabled_icon_color=0xFF5F6368,
    )
    return btn


def create_context_menu(hwnd, root, anchor_id, items, icons, width=238, height=180):
    menu = ui.create_menu(hwnd, root, items, active=0, orientation=1, x=-900, y=0, w=width, h=height)
    for index, icon in enumerate(icons):
        if icon:
            ui.set_menu_item_icon(hwnd, menu, index, icon)
    ui.set_popup_anchor_element(hwnd, menu, anchor_id)
    ui.set_popup_placement(hwnd, menu, placement=5, offset_x=0, offset_y=6)
    ui.set_popup_dismiss_behavior(hwnd, menu, True, True)
    ui.set_popup_open(hwnd, menu, False)
    ui.set_element_popup(hwnd, anchor_id, menu, "right_click")
    return menu


def layout_shell(hwnd, width, height):
    width = max(760, int(width))
    height = max(420, int(height))
    tab_h = 34
    toolbar_y = 40
    toolbar_h = 50
    viewport_y = toolbar_y + toolbar_h
    tab_count = max(1, int(STATE.get("tab_count", 1)))
    tab_strip_right = min(width - 184, TAB_LEFT + tab_count * TAB_WIDTH)
    new_tab_x = min(tab_strip_right + NEW_TAB_GAP, width - 176)
    more_x = max(OMNIBOX_X + 260, width - TOOLBAR_RIGHT_MARGIN - TOOLBAR_BUTTON_SIZE)
    extensions_x = more_x - TOOLBAR_BUTTON_SIZE - TOOLBAR_BUTTON_GAP
    download_x = extensions_x - TOOLBAR_BUTTON_SIZE - TOOLBAR_BUTTON_GAP
    omnibox_right = download_x - 16
    omnibox_w = max(220, omnibox_right - OMNIBOX_X)

    STATE["layout_w"] = width
    STATE["layout_h"] = height

    set_bounds(hwnd, STATE["root"], 0, 0, width, height)
    set_bounds(hwnd, STATE["tab_bg"], 0, 0, width, toolbar_y)
    set_bounds(hwnd, STATE["toolbar_bg"], 0, toolbar_y, width, toolbar_h)
    set_bounds(hwnd, STATE["tabs"], TAB_LEFT, TAB_Y, max(TAB_WIDTH, width - 220), tab_h)
    set_bounds(hwnd, STATE["new_tab"], new_tab_x, TAB_Y + 1, 30, 30)
    set_bounds(hwnd, STATE["omnibox"], OMNIBOX_X, 46, omnibox_w, 34)
    set_bounds(hwnd, STATE["download"], download_x, 46, TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
    set_bounds(hwnd, STATE["extensions"], extensions_x, 46, TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
    set_bounds(hwnd, STATE["more"], more_x, 46, TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
    set_bounds(hwnd, STATE["min"], width - 138, 0, 46, 32)
    set_bounds(hwnd, STATE["max"], width - 92, 0, 46, 32)
    set_bounds(hwnd, STATE["close"], width - 46, 0, 46, 32)
    set_bounds(hwnd, STATE["viewport"], 0, viewport_y, width, max(1, height - viewport_y))

    ui.clear_window_drag_regions(hwnd)
    ui.clear_window_no_drag_regions(hwnd)
    ui.set_window_drag_region(hwnd, 0, 0, width - 138, toolbar_y, True)
    ui.set_window_drag_region(hwnd, max(0, width - 184), toolbar_y, 92, 50, True)
    ui.set_window_no_drag_region(hwnd, 0, 0, min(width - 138, new_tab_x + 40), toolbar_y, True)
    ui.set_window_no_drag_region(hwnd, width - 138, 0, 138, 32, True)
    ui.set_window_no_drag_region(hwnd, 0, toolbar_y, width, toolbar_h, True)


def make_shell(hwnd, root):
    scale = window_scale(hwnd)
    tab_metric_w = int(220 * scale)
    tab_metric_h = int(32 * scale)

    STATE["tab_bg"] = ui.create_panel(hwnd, root, 0, 0, 1160, 40, 0xFF202124)
    ui.set_panel_style(hwnd, STATE["tab_bg"], bg=0xFF202124, border=0x00000000, border_width=0.0, radius=0.0, padding=0)
    STATE["toolbar_bg"] = ui.create_panel(hwnd, root, 0, 40, 1160, 50, 0xFF202124)
    ui.set_panel_style(hwnd, STATE["toolbar_bg"], bg=0xFF202124, border=0x00000000, border_width=0.0, radius=0.0, padding=0)

    tabs = ui.create_tabs(hwnd, root, ["新标签页"], active=0, tab_type=0, x=TAB_LEFT, y=TAB_Y, w=760, h=34)
    ui.set_tabs_chrome_mode(hwnd, tabs, True)
    ui.set_tabs_options(hwnd, tabs, tab_type=0, closable=True, addable=False)
    ui.set_tabs_chrome_metrics(hwnd, tabs, min_width=tab_metric_w, max_width=tab_metric_w,
                               pinned_width=int(46 * scale), height=tab_metric_h, overlap=0)
    ui.set_tabs_new_button_visible(hwnd, tabs, False)
    ui.set_tabs_item_icon(hwnd, tabs, 0, "🌐")
    ui.set_tabs_item_closable(hwnd, tabs, 0, True)
    ui.set_tabs_close_callback(hwnd, tabs, on_tab_closed)
    STATE["new_tab"] = new_tab_button(hwnd, root, TAB_LEFT + TAB_WIDTH + NEW_TAB_GAP, TAB_Y + 1)
    ui.dll.EU_SetElementClickCallback(hwnd, STATE["new_tab"], on_new_tab)

    back = icon_button(hwnd, root, "←", "后退", 12, 46)
    forward = icon_button(hwnd, root, "→", "前进", 50, 46)
    refresh = icon_button(hwnd, root, "↻", "刷新", 88, 46)
    ui.set_element_window_command(hwnd, back, ui.EU_WINDOW_COMMAND_NONE)
    ui.set_element_window_command(hwnd, forward, ui.EU_WINDOW_COMMAND_NONE)
    ui.set_element_window_command(hwnd, refresh, ui.EU_WINDOW_COMMAND_NONE)

    omnibox = ui.create_omnibox(hwnd, root, "", "搜索或输入网址", 132, 46, 744, 34)
    ui.set_omnibox_security_state(hwnd, omnibox, 5, "")
    ui.set_omnibox_prefix_chip(hwnd, omnibox, "", "", 0, 0)
    ui.set_omnibox_action_icons(hwnd, omnibox, [("☆", "收藏"), ("↗", "分享")])
    ui.set_omnibox_suggestion_items(hwnd, omnibox, [
        ("搜索", "🔍", "搜索 new_emoji 浏览器式外壳", "默认搜索", "new_emoji 浏览器式外壳"),
        ("历史", "🕘", "组件封装进度", "本地文档", "组件封装进度.md"),
        ("书签", "☆", "API 索引", "docs/api-index.md", "docs/api-index.md"),
    ])
    ui.set_omnibox_commit_callback(hwnd, omnibox, on_commit)

    STATE["download"] = icon_button(hwnd, root, "⇩", "下载", 912, 46, badge="2")
    STATE["extensions"] = icon_button(hwnd, root, "◆", "扩展程序", 950, 46, checked=True)
    STATE["more"] = icon_button(hwnd, root, "⋮", "自定义及控制", 988, 46)

    download_popup = ui.create_popover(
        hwnd, root, "", "下载 📥",
        "最近下载\n📦 new_emoji.dll\n🐍 chrome_shell_demo.py\n✅ 全部下载已完成",
        placement=3, x=-900, y=0, w=1, h=1,
    )
    ui.set_popover_advanced_options(hwnd, download_popup, placement=5, open=False, popup_width=286, popup_height=178, closable=False)
    ui.set_popover_arrow(hwnd, download_popup, True, 8)
    ui.set_popup_anchor_element(hwnd, download_popup, STATE["download"])
    ui.set_popup_placement(hwnd, download_popup, placement=5, offset_x=0, offset_y=6)
    ui.set_popup_dismiss_behavior(hwnd, download_popup, True, True)
    ui.set_icon_button_dropdown(hwnd, STATE["download"], download_popup)

    extensions_popup = ui.create_popover(
        hwnd, root, "", "扩展程序 🧩",
        "已固定扩展\n🧪 组件检查器\n🎨 主题助手\n🔒 权限状态正常",
        placement=3, x=-900, y=0, w=1, h=1,
    )
    ui.set_popover_advanced_options(hwnd, extensions_popup, placement=5, open=False, popup_width=286, popup_height=178, closable=False)
    ui.set_popover_arrow(hwnd, extensions_popup, True, 8)
    ui.set_popup_anchor_element(hwnd, extensions_popup, STATE["extensions"])
    ui.set_popup_placement(hwnd, extensions_popup, placement=5, offset_x=0, offset_y=6)
    ui.set_popup_dismiss_behavior(hwnd, extensions_popup, True, True)
    ui.set_icon_button_dropdown(hwnd, STATE["extensions"], extensions_popup)

    menu = ui.create_menu(
        hwnd, root,
        ["新标签页", "新窗口", "下载内容", "扩展程序", "设置"],
        active=0, orientation=1, x=914, y=90, w=238, h=218,
    )
    ui.set_menu_item_icon(hwnd, menu, 0, "🌐")
    ui.set_menu_item_icon(hwnd, menu, 2, "⇩")
    ui.set_menu_item_icon(hwnd, menu, 3, "◆")
    ui.set_menu_item_shortcut(hwnd, menu, 0, "Ctrl+T")
    ui.set_menu_item_shortcut(hwnd, menu, 1, "Ctrl+N")
    ui.set_menu_item_separator(hwnd, menu, 4, True)
    ui.set_popup_anchor_element(hwnd, menu, STATE["more"])
    ui.set_popup_placement(hwnd, menu, placement=5, offset_x=0, offset_y=6)
    ui.set_popup_dismiss_behavior(hwnd, menu, True, True)
    ui.set_popup_open(hwnd, menu, False)
    ui.set_icon_button_dropdown(hwnd, STATE["more"], menu)
    STATE["download_popup"] = download_popup
    STATE["extensions_popup"] = extensions_popup
    STATE["more_menu"] = menu

    STATE["omnibox_menu"] = create_context_menu(
        hwnd, root, omnibox,
        ["复制网址", "粘贴并转到", "全选文字", "编辑搜索引擎"],
        ["📋", "📥", "✅", "⚙️"],
        width=248, height=174,
    )
    STATE["tabs_menu"] = create_context_menu(
        hwnd, root, tabs,
        ["新建标签页", "关闭标签页", "关闭其他标签页"],
        ["🌐", "✖", "🧹"],
        width=238, height=138,
    )

    STATE["min"] = caption_button(hwnd, root, "−", "最小化", 1000, 0, ui.EU_WINDOW_COMMAND_MINIMIZE)
    STATE["max"] = caption_button(hwnd, root, "□", "最大化", 1046, 0, ui.EU_WINDOW_COMMAND_TOGGLE_MAXIMIZE)
    STATE["close"] = caption_button(hwnd, root, "×", "关闭", 1092, 0, ui.EU_WINDOW_COMMAND_CLOSE, close=True)

    STATE["tabs"] = tabs
    STATE["omnibox"] = omnibox


def main():
    hwnd = ui.create_browser_shell_window("浏览器式外壳 🌐", 160, 80, 1180, 760)
    if not hwnd:
        print("窗口创建失败")
        return

    STATE["hwnd"] = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)
    ui.set_window_resize_border(hwnd, 6, 6, 6, 6)
    ui.set_chrome_theme_preset(hwnd, 1)
    ui.set_theme_token(hwnd, "chrome.frame_bg", 0xFF202124)
    ui.set_theme_token(hwnd, "chrome.toolbar_bg", 0xFF202124)
    ui.set_theme_token(hwnd, "chrome.omnibox_bg", 0xFFF1F3F4)
    ui.set_theme_token(hwnd, "chrome.omnibox_focus_bg", 0xFFFFFFFF)
    ui.set_theme_token(hwnd, "chrome.omnibox_fg", 0xFF202124)
    ui.set_theme_token(hwnd, "chrome.omnibox_placeholder", 0xFF5F6368)
    ui.set_theme_token(hwnd, "chrome.omnibox_border", 0x00000000)
    ui.set_theme_token(hwnd, "chrome.omnibox_focus_border", 0xFF8AB4F8)
    ui.set_theme_token(hwnd, "chrome.icon_button_fg", 0xFFE8EAED)
    ui.set_theme_token(hwnd, "chrome.viewport_bg", 0xFFFFFFFF)
    ui.set_theme_token(hwnd, "chrome.viewport_fg", 0xFF202124)

    root = ui.create_container(hwnd, 0, 0, 0, 1160, 760)
    STATE["root"] = root

    viewport = ui.create_browser_viewport(hwnd, root, x=0, y=90, w=1160, h=670)
    STATE["viewport"] = viewport
    ui.set_browser_viewport_placeholder(
        hwnd, viewport,
        "新标签页 🌐",
        "浏览器式外壳示例：标签栏、地址栏、工具按钮、菜单和内容占位区均由 D2D Element 绘制。",
        "🌐",
    )
    ui.set_browser_viewport_loading(hwnd, viewport, False, 0)
    make_shell(hwnd, root)
    STATE["viewport_menu"] = create_context_menu(
        hwnd, root, viewport,
        ["返回", "重新加载", "查看页面信息"],
        ["←", "↻", "ℹ️"],
        width=238, height=138,
    )
    layout_shell(hwnd, 1160, 760)

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages()


if __name__ == "__main__":
    main()
