# -*- coding: utf-8 -*-
"""
抖音多账号浏览器外壳示例。

右侧浏览器区域使用 BrowserViewport 占位组件，明确标注这里需要宿主程序自行
接入 WebView2、CEF 或外部浏览器句柄；new_emoji.dll 负责纯 D2D UI 外壳。
"""
import ctypes
import time
from ctypes import wintypes

import new_emoji_ui as ui


WINDOW_W = 1600
WINDOW_H = 860
LEFT_W = 700
GAP = 18
RIGHT_X = LEFT_W + GAP
RIGHT_W = WINDOW_W - RIGHT_X - 14

BLUE = 0xFF2563EB
GREEN = 0xFF16A34A
ORANGE = 0xFFF59E0B
RED = 0xFFFF5D6C
PINK = 0xFFFF2F68
DOUYIN_BG = 0xFF11131D
DOUYIN_TEXT = 0xFFE9ECF3
DOUYIN_MUTED = 0xFF9AA3B2

LIGHT = {
    "page": 0xFFF3F6FB,
    "surface": 0xFFFFFFFF,
    "subtle": 0xFFF8FAFE,
    "border": 0xFFDCE4F0,
    "text": 0xFF1F2937,
    "muted": 0xFF667085,
    "chip": 0xFFEAF7EF,
    "chip_border": 0xFFCBEED8,
    "selected": 0xFFE8F3FF,
    "alt": 0xFFFAFCFF,
}

DARK = {
    "page": 0xFF111827,
    "surface": 0xFF1F2937,
    "subtle": 0xFF273244,
    "border": 0xFF3B4658,
    "text": 0xFFE5E7EB,
    "muted": 0xFF9CA3AF,
    "chip": 0xFF123322,
    "chip_border": 0xFF256D40,
    "selected": 0xFF1E3A5F,
    "alt": 0xFF182231,
}


def make_accounts():
    rows = [
        {"name": "💻 笔记本电脑", "state": "未打开", "total": 128, "todo": 0},
        {"name": "📱 智能手机", "state": "未打开", "total": 256, "todo": 0},
        {"name": "🎧 无线耳机", "state": "未打开", "total": 512, "todo": 0},
        {"name": "🖥️ 4K显示器", "state": "未打开", "total": 89, "todo": 0},
        {"name": "⌨️ 机械键盘", "state": "未打开", "total": 0, "todo": 0},
    ]
    names = ["游戏手柄", "直播小号", "短剧账号", "美食账号", "旅行账号", "亲子账号", "汽车账号", "知识账号"]
    for index in range(1, 121):
        rows.append({
            "name": f"🎮 {names[(index - 1) % len(names)]} {index}",
            "state": "未打开",
            "total": 1024 if index % 9 else 768,
            "todo": 0 if index % 7 else 3,
        })
    return rows


STATE = {
    "hwnd": 0,
    "root": 0,
    "dark": False,
    "accounts": make_accounts(),
    "selected": {0, 3},
    "next_no": 57,
    "root_bg": 0,
    "left_bg": 0,
    "card": 0,
    "card_head": 0,
    "chip": 0,
    "current_text": 0,
    "count_text": 0,
    "total_text": 0,
    "theme_btn": 0,
    "table": 0,
}


def palette():
    return DARK if STATE["dark"] else LIGHT


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_add_account(_element_id):
    no = STATE["next_no"]
    STATE["next_no"] += 1
    STATE["accounts"].append({"name": f"🆕 新增账号 {no}", "state": "未打开", "total": 0, "todo": 0})
    new_index = len(STATE["accounts"]) - 1
    STATE["selected"] = {new_index}
    refresh_table(scroll_to=new_index)
    ui.message_success(STATE["hwnd"], f"已添加账号：新增账号 {no}", center=False)


@ui.ClickCallback
def on_delete_account(_element_id):
    if not STATE["selected"]:
        ui.message_warning(STATE["hwnd"], "请先在表格中勾选要删除的账号", center=False)
        return
    count = len(STATE["selected"])
    names = "、".join(STATE["accounts"][i]["name"] for i in sorted(STATE["selected"])[:3])
    suffix = "等账号" if count > 3 else ""
    ui.show_confirm_box(
        STATE["hwnd"],
        "🗑️ 删除账号",
        f"确定删除已选的 {count} 个账号吗？\n{names}{suffix}\n此操作只影响当前示例数据。",
        confirm="确认删除",
        cancel="取消",
        box_type=2,
        center=True,
        callback=on_delete_confirm,
    )


@ui.MessageBoxExCallback
def on_delete_confirm(_messagebox_id, action, _value_ptr, _value_len):
    if action != 1:
        return
    removed = len(STATE["selected"])
    STATE["accounts"] = [row for index, row in enumerate(STATE["accounts"]) if index not in STATE["selected"]]
    STATE["selected"].clear()
    refresh_table(scroll_to=0)
    ui.message_success(STATE["hwnd"], f"已删除 {removed} 个账号", center=False)


@ui.ClickCallback
def on_toggle_theme(_element_id):
    STATE["dark"] = not STATE["dark"]
    ui.dll.EU_SetThemeMode(STATE["hwnd"], 1 if STATE["dark"] else 0)
    apply_theme()
    ui.message_info(STATE["hwnd"], "已切换为深色模式" if STATE["dark"] else "已切换为明亮模式", center=False)


@ui.TableCellCallback
def on_table_action(_table_id, row, col, action, value):
    if action == 2 or col == 0:
        if value:
            STATE["selected"].add(row)
        else:
            STATE["selected"].discard(row)
        refresh_summary()
    elif col == 5:
        if 0 <= row < len(STATE["accounts"]):
            STATE["selected"] = {row}
            refresh_table(scroll_to=row)
            ui.message_info(STATE["hwnd"], f"正在查看：{STATE['accounts'][row]['name']}", center=False)


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


def panel(hwnd, parent, x, y, w, h, bg, border=None, radius=4, border_width=1.0):
    eid = ui.create_panel(hwnd, parent, x, y, w, h, bg)
    ui.set_panel_style(hwnd, eid, bg=bg, border=bg if border is None else border,
                       border_width=border_width, radius=radius, padding=0)
    return eid


def label(hwnd, parent, text, x, y, w, h, color, align=0, wrap=False):
    eid = ui.create_text(hwnd, parent, text, x, y, w, h)
    ui.set_element_color(hwnd, eid, 0x00000000, color)
    ui.set_text_options(hwnd, eid, align=align, valign=1, wrap=wrap, ellipsis=not wrap)
    return eid


def button(hwnd, parent, emoji, text, x, y, w, h, variant, callback=None):
    eid = ui.create_button(hwnd, parent, emoji, text, x, y, w, h, variant=variant)
    if callback:
        ui.dll.EU_SetElementClickCallback(hwnd, eid, callback)
    return eid


def columns():
    return [
        {"title": "选择", "key": "select", "type": "selection", "width": 48, "min_width": 48, "align": 1, "fixed": "left"},
        {"title": "账号名称", "key": "name", "width": 220, "min_width": 180, "align": 1, "tooltip": True},
        {"title": "状态", "key": "state", "width": 64, "min_width": 64, "align": 1},
        {"title": "消息总数", "key": "total", "width": 104, "min_width": 88, "align": 1, "sortable": True},
        {"title": "待处理", "key": "todo", "width": 72, "min_width": 72, "align": 1},
        {"title": "操作", "key": "action", "type": "buttons", "width": 128, "min_width": 128, "align": 1, "fixed": "right"},
    ]


def table_rows():
    rows = []
    for index, item in enumerate(STATE["accounts"]):
        rows.append({
            "cells": [
                {"type": "selection", "checked": index in STATE["selected"]},
                item["name"],
                item["state"],
                str(item["total"]),
                str(item["todo"]),
                {"type": "buttons", "value": "🔍 查看"},
            ]
        })
    return rows


def refresh_summary():
    colors = palette()
    selected = len(STATE["selected"])
    total = len(STATE["accounts"])
    current = "、".join(STATE["accounts"][i]["name"] for i in sorted(STATE["selected"])[:2]) if selected else "未选择账号"
    if selected > 2:
        current += " 等"
    ui.set_element_text(STATE["hwnd"], STATE["current_text"], f"当前选中：{current}")
    ui.set_element_text(STATE["hwnd"], STATE["count_text"], f"已选 {selected} 个")
    ui.set_element_text(STATE["hwnd"], STATE["total_text"], f"共 {total} 个账号 · 滚轮可浏览更多")
    ui.set_element_color(STATE["hwnd"], STATE["current_text"], 0, colors["text"])
    ui.set_element_color(STATE["hwnd"], STATE["count_text"], 0, colors["muted"])
    ui.set_element_color(STATE["hwnd"], STATE["total_text"], 0, colors["muted"])


def refresh_table(scroll_to=None):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    cols = columns()
    ui.set_table_rows_ex(hwnd, table, table_rows(), cols)
    ui.set_table_selected_rows(hwnd, table, sorted(STATE["selected"]))
    if scroll_to is not None:
        ui.set_table_scroll(hwnd, table, max(0, scroll_to - 8), 0)
    colors = palette()
    for row_index, item in enumerate(STATE["accounts"]):
        if row_index % 2:
            ui.set_table_row_style(hwnd, table, row_index, bg=colors["alt"])
        if row_index in STATE["selected"]:
            ui.set_table_row_style(hwnd, table, row_index, bg=colors["selected"])
        ui.set_table_cell_style(hwnd, table, row_index, 1, fg=colors["text"], align=0, font_flags=0, font_size=14)
        ui.set_table_cell_style(hwnd, table, row_index, 2, fg=colors["muted"], align=1)
        total = item["total"]
        total_color = GREEN if total >= 1000 else (RED if total <= 100 else colors["text"])
        ui.set_table_cell_style(hwnd, table, row_index, 3, fg=total_color, align=1, font_flags=1, font_size=14)
        ui.set_table_cell_style(hwnd, table, row_index, 4, fg=ORANGE if item["todo"] else colors["muted"],
                                align=1, font_flags=1, font_size=13)
        ui.set_table_cell_style(hwnd, table, row_index, 5, fg=colors["text"], align=1)
    refresh_summary()


def apply_theme():
    colors = palette()
    hwnd = STATE["hwnd"]
    ui.set_panel_style(hwnd, STATE["root_bg"], bg=colors["page"], border=colors["page"], border_width=0, radius=0, padding=0)
    ui.set_panel_style(hwnd, STATE["left_bg"], bg=colors["page"], border=colors["page"], border_width=0, radius=0, padding=0)
    ui.set_panel_style(hwnd, STATE["card"], bg=colors["surface"], border=colors["border"], border_width=1, radius=8, padding=0)
    ui.set_panel_style(hwnd, STATE["card_head"], bg=colors["subtle"], border=colors["border"], border_width=1, radius=8, padding=0)
    ui.set_panel_style(hwnd, STATE["chip"], bg=colors["chip"], border=colors["chip_border"], border_width=1, radius=13, padding=0)
    ui.set_element_color(hwnd, STATE["theme_btn"], 0, colors["text"])
    refresh_table()


def draw_left_accounts(hwnd, root):
    colors = palette()
    STATE["left_bg"] = panel(hwnd, root, 0, 0, LEFT_W, WINDOW_H, colors["page"], colors["page"], 0, 0)

    button(hwnd, root, "➕", "添加账号", 18, 38, 150, 38, 1, on_add_account)
    button(hwnd, root, "➖", "删除账号", 182, 38, 150, 38, 2, on_delete_account)
    STATE["theme_btn"] = button(hwnd, root, "🌗", "换肤", 346, 38, 96, 38, 5, on_toggle_theme)
    STATE["current_text"] = label(hwnd, root, "", 18, 88, 500, 28, colors["text"])

    STATE["card"] = panel(hwnd, root, 18, 124, LEFT_W - 36, WINDOW_H - 142, colors["surface"], colors["border"], 8, 1)
    STATE["card_head"] = panel(hwnd, root, 18, 124, LEFT_W - 36, 58, colors["subtle"], colors["border"], 8, 1)
    label(hwnd, root, "📋 账号列表", 36, 140, 128, 28, colors["text"])
    STATE["count_text"] = label(hwnd, root, "", 164, 140, 120, 28, colors["muted"])
    STATE["total_text"] = label(hwnd, root, "", 284, 140, 210, 28, colors["muted"])
    STATE["chip"] = panel(hwnd, root, LEFT_W - 126, 140, 90, 26, colors["chip"], colors["chip_border"], 13, 1)
    label(hwnd, root, "🟢 待打开", LEFT_W - 118, 142, 74, 22, GREEN, align=1)

    table_x = 30
    table_y = 186
    table_w = LEFT_W - 42
    table_fill_h = WINDOW_H - table_y - 10
    table_h = table_fill_h
    STATE["table"] = ui.create_table_ex(
        hwnd, root, columns(), table_rows(),
        striped=True, bordered=False, x=table_x, y=table_y, w=table_w, h=table_h,
        selection_mode=2, row_height=34, header_height=40,
        fixed_header=True, horizontal_scroll=False,
    )
    ui.set_table_viewport_options(hwnd, STATE["table"], table_h, True, False, False)
    ui.set_table_cell_action_callback(hwnd, STATE["table"], on_table_action)
    refresh_table()


def draw_browser_toolbar(hwnd, root):
    y = 36
    button(hwnd, root, "🏠", "首页", RIGHT_X, y, 72, 36, 0)
    button(hwnd, root, "🔄", "刷新", RIGHT_X + 78, y, 72, 36, 0)
    button(hwnd, root, "⬅️", "后退", RIGHT_X + 156, y, 72, 36, 0)
    button(hwnd, root, "➡️", "前进", RIGHT_X + 234, y, 72, 36, 0)

    omnibox = ui.create_omnibox(
        hwnd, root,
        "https://www.douyin.com/jingxuan",
        "输入网页地址或搜索内容 🔍",
        RIGHT_X + 314, y, RIGHT_W - 374, 36,
    )
    ui.set_omnibox_security_state(hwnd, omnibox, 2, "网页")
    button(hwnd, root, "🚀", "GO", WINDOW_W - 66, y, 52, 36, 2)


def draw_douyin_shell_hint(hwnd, root):
    shell_y = 84
    shell_h = WINDOW_H - shell_y - 16
    panel(hwnd, root, RIGHT_X, shell_y, RIGHT_W, shell_h, DOUYIN_BG, DOUYIN_BG, 0, 0)

    label(hwnd, root, "🎵", RIGHT_X + 24, shell_y + 12, 48, 40, DOUYIN_TEXT, align=1)
    panel(hwnd, root, RIGHT_X + 360, shell_y + 12, 390, 38, 0xFF30323E, 0xFF3D4050, 8, 1)
    label(hwnd, root, "搜索你感兴趣的内容", RIGHT_X + 376, shell_y + 17, 220, 28, DOUYIN_MUTED)
    label(hwnd, root, "🔍 搜索", RIGHT_X + 650, shell_y + 17, 90, 28, DOUYIN_TEXT, align=1)
    button(hwnd, root, "🔐", "登录", WINDOW_W - 112, shell_y + 12, 86, 38, 6)

    categories = ["全部", "公开课", "游戏", "二次元", "音乐", "影视", "美食", "知识", "小剧场", "生活vlog", "体育", "旅行", "亲子", "汽车"]
    x = RIGHT_X + 90
    for index, item in enumerate(categories):
        color = DOUYIN_TEXT if index == 0 else DOUYIN_MUTED
        label(hwnd, root, item, x, shell_y + 70, 72, 28, color, align=1)
        x += 76
    panel(hwnd, root, RIGHT_X + 105, shell_y + 103, 18, 3, PINK, PINK, 2, 0)

    nav_items = ["精选", "推荐", "搜索", "关注", "朋友", "我的", "直播", "放映厅", "短剧"]
    for index, item in enumerate(nav_items):
        y = shell_y + 76 + index * 54
        bg = 0xFF2A2D38 if index == 0 else DOUYIN_BG
        panel(hwnd, root, RIGHT_X + 10, y, 62, 42, bg, bg, 8, 0)
        label(hwnd, root, "●", RIGHT_X + 18, y + 8, 18, 22, DOUYIN_MUTED, align=1)
        label(hwnd, root, item, RIGHT_X + 34, y + 8, 34, 22, DOUYIN_TEXT if index == 0 else DOUYIN_MUTED, align=1)

    viewport = ui.create_browser_viewport(hwnd, root, RIGHT_X + 90, shell_y + 120, RIGHT_W - 112, shell_h - 140)
    ui.set_browser_viewport_placeholder(
        hwnd,
        viewport,
        "🌐 浏览器内嵌区域（宿主接入）",
        "这里不是 WebView2/CEF 内核。请在宿主程序中自行嵌入浏览器组件，或把外部浏览器截图/状态同步到 BrowserViewport；new_emoji.dll 负责左侧账号表格、顶部工具栏和纯 D2D 外壳。",
        "🧩",
    )
    ui.set_browser_viewport_loading(hwnd, viewport, False, 0)

    note_x = RIGHT_X + 132
    note_y = shell_y + 504
    panel(hwnd, root, note_x, note_y, 460, 118, 0xE61F2330, 0xFF3A4052, 6, 1)
    label(hwnd, root, "🧩 接入说明", note_x + 18, note_y + 12, 200, 28, DOUYIN_TEXT)
    label(hwnd, root, "可选方案：WebView2 子窗口、CEF 离屏渲染、外部浏览器句柄。当前示例只保留接入位置和 UI 外壳。",
          note_x + 18, note_y + 46, 420, 48, DOUYIN_MUTED, wrap=True)


def main():
    hwnd = ui.create_window_ex("🎵 TikTok多账号浏览器外壳", 40, 40, WINDOW_W, WINDOW_H, 0xFFF2F4F8)
    if not hwnd:
        print("窗口创建失败")
        return

    STATE["hwnd"] = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetThemeMode(hwnd, 0)

    root = ui.create_container(hwnd, 0, 0, 0, WINDOW_W, WINDOW_H)
    STATE["root"] = root
    colors = palette()
    STATE["root_bg"] = panel(hwnd, root, 0, 0, WINDOW_W, WINDOW_H, colors["page"], colors["page"], 0, 0)
    draw_left_accounts(hwnd, root)
    draw_browser_toolbar(hwnd, root)
    draw_douyin_shell_hint(hwnd, root)

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages()


if __name__ == "__main__":
    main()
