# -*- coding: utf-8 -*-
"""
PDD 多账号采集面板草图。

中间区域只是“手机浏览器放置区域”占位，不嵌入真实 WebView、不加载网页。
"""
import ctypes
import time
from ctypes import wintypes

import new_emoji_ui as ui


WINDOW_W = 1398
WINDOW_H = 900

TABLE_X = 24
TABLE_Y = 180
TABLE_W = 640
TABLE_H = 1000

LIGHT = {
    "bg": 0xFFF4F7FB,
    "panel": 0xFFFFFFFF,
    "border": 0xFFD8DFEA,
    "text": 0xFF263445,
    "muted": 0xFF708097,
    "row_alt": 0xFFFAFCFF,
    "row_selected": 0xFFE5F2FF,
    "tip": 0xFFE8F3FF,
    "tip_border": 0xFF9DD0FF,
    "scan": 0xFFFFF5F1,
    "scan_border": 0xFFFFBBAE,
}

DARK = {
    "bg": 0xFF111827,
    "panel": 0xFF1F2937,
    "border": 0xFF3B4658,
    "text": 0xFFE5E7EB,
    "muted": 0xFF9CA3AF,
    "row_alt": 0xFF182231,
    "row_selected": 0xFF1E3A5F,
    "tip": 0xFF172C46,
    "tip_border": 0xFF2F6FA8,
    "scan": 0xFF33211F,
    "scan_border": 0xFF8F4A3F,
}

BLUE = 0xFF409EFF
GREEN = 0xFF63C234
RED = 0xFFFF5D5D
ORANGE = 0xFFFFA726


def make_accounts():
    rows = [
        ("💻账号莫生", "未开始", 128, 0),
        ("📱坏男人", "未开始", 256, 0),
        ("🎧账号3", "未开始", 512, 0),
        ("🖥️ 账号4", "未开始", 89, 0),
        ("🖥️ 账号5", "未开始", 0, 0),
    ]
    for index in range(1, 57):
        rows.append((f"🎮账号{index}", "未开始", 1024 if index % 9 else 768, 0 if index % 7 else 3))
    return rows


STATE = {
    "hwnd": 0,
    "root": 0,
    "dark": False,
    "accounts": make_accounts(),
    "selected": {0, 3},
    "current_row": 0,
    "next_no": 57,
    "root_bg": 0,
    "current_text": 0,
    "selected_count_text": 0,
    "table": 0,
    "panels": [],
    "texts": [],
}


def palette():
    return DARK if STATE["dark"] else LIGHT


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_toggle_theme(_element_id):
    STATE["dark"] = not STATE["dark"]
    ui.dll.EU_SetThemeMode(STATE["hwnd"], 1 if STATE["dark"] else 0)
    apply_theme()


@ui.ClickCallback
def on_add_account(_element_id):
    no = STATE["next_no"]
    STATE["next_no"] += 1
    STATE["accounts"].append((f"🆕新账号{no}", "未开始", 0, 0))
    STATE["current_row"] = len(STATE["accounts"]) - 1
    STATE["selected"].add(STATE["current_row"])
    refresh_table(scroll_to=STATE["current_row"])


@ui.ClickCallback
def on_delete_account(_element_id):
    if not STATE["accounts"]:
        ui.show_alert_box(STATE["hwnd"], "提示", "当前没有可删除的账号。", "知道了")
        return
    name = STATE["accounts"][STATE["current_row"]][0]
    ui.show_confirm_box(
        STATE["hwnd"],
        "🗑️ 删除账号",
        f"确定要删除「{name}」吗？删除后仅影响当前示例数据。",
        confirm="删除",
        cancel="取消",
        box_type=2,
        center=True,
        callback=on_delete_confirm,
    )


@ui.MessageBoxExCallback
def on_delete_confirm(_box_id, action, _value_ptr, _value_len):
    if action != 1 or not STATE["accounts"]:
        return
    row = STATE["current_row"]
    del STATE["accounts"][row]
    STATE["selected"] = {r - 1 if r > row else r for r in STATE["selected"] if r != row}
    STATE["current_row"] = min(row, max(0, len(STATE["accounts"]) - 1))
    refresh_table(scroll_to=STATE["current_row"])


@ui.TableCellCallback
def on_table_click(_table_id, row, col, _action, _value):
    if not (0 <= row < len(STATE["accounts"])):
        return
    STATE["current_row"] = row
    refresh_summary()
    style_table_rows()


@ui.TableCellCallback
def on_table_action(_table_id, row, col, action, value):
    if not (0 <= row < len(STATE["accounts"])):
        return
    STATE["current_row"] = row
    if col == 0:
        if value:
            STATE["selected"].add(row)
        else:
            STATE["selected"].discard(row)
    elif col == 5:
        print(f"查看账号：{STATE['accounts'][row][0]}，行={row} 列=5")
    refresh_table(scroll_to=None)


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


def panel(hwnd, parent, x, y, w, h, role="panel", border_role="border", radius=4, border_width=1.0):
    colors = palette()
    eid = ui.create_panel(hwnd, parent, x, y, w, h, colors[role])
    ui.set_panel_style(hwnd, eid, colors[role], colors[border_role], border_width, radius, 0)
    STATE["panels"].append((eid, role, border_role, radius, border_width))
    return eid


def label(hwnd, parent, text, x, y, w, h, role="text", align=0, wrap=False):
    colors = palette()
    eid = ui.create_text(hwnd, parent, text, x, y, w, h)
    ui.set_element_color(hwnd, eid, 0, colors[role])
    ui.set_text_options(hwnd, eid, align=align, valign=1, wrap=wrap, ellipsis=not wrap)
    STATE["texts"].append((eid, role))
    return eid


def button(hwnd, parent, emoji, text, x, y, w, h, variant=1, callback=None):
    eid = ui.create_button(hwnd, parent, emoji, text, x, y, w, h, variant=variant)
    if callback:
        ui.dll.EU_SetElementClickCallback(hwnd, eid, callback)
    return eid


def table_columns():
    return [
        {"title": "选择", "key": "select", "type": "selection", "width": 56, "min_width": 48, "align": "center"},
        {"title": "账号名称", "key": "name", "width": 130, "min_width": 118, "align": "center", "tooltip": True},
        {"title": "状态", "key": "state", "width": 68, "min_width": 62, "align": "center"},
        {"title": "采集总数", "key": "total", "width": 119, "min_width": 108, "align": "center", "sortable": True},
        {"title": "执行数", "key": "done", "width": 92, "min_width": 88, "align": "center"},
        {"title": "操作", "key": "action", "type": "buttons", "width": 481, "min_width": 455, "align": "center"},
    ]


def table_rows():
    rows = []
    for index, (name, state, total, done) in enumerate(STATE["accounts"]):
        rows.append({
            "cells": [
                {"type": "selection", "checked": index in STATE["selected"]},
                name,
                state,
                str(total),
                str(done),
                {"type": "buttons", "value": ["🔍 查看"]},
            ]
        })
    return rows


def refresh_summary():
    colors = palette()
    if STATE["accounts"]:
        current = STATE["accounts"][STATE["current_row"]][0]
        ui.set_element_text(STATE["hwnd"], STATE["current_text"], f"当前选中：{current}  [行={STATE['current_row']} 列=5]")
    else:
        ui.set_element_text(STATE["hwnd"], STATE["current_text"], "当前选中：暂无账号")
    ui.set_element_text(STATE["hwnd"], STATE["selected_count_text"], f"已选账号：{len(STATE['selected'])} 个")
    ui.set_element_color(STATE["hwnd"], STATE["current_text"], 0, colors["text"])
    ui.set_element_color(STATE["hwnd"], STATE["selected_count_text"], 0, colors["muted"])


def style_table_rows():
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    colors = palette()
    for row, item in enumerate(STATE["accounts"]):
        bg = colors["row_alt"] if row % 2 else colors["panel"]
        if row == STATE["current_row"] or row in STATE["selected"]:
            bg = colors["row_selected"]
        ui.set_table_row_style(hwnd, table, row, bg=bg, fg=colors["text"], align=-1, font_flags=0, font_size=0)
        ui.set_table_cell_style(hwnd, table, row, 1, fg=colors["text"], align=0, font_flags=0)
        ui.set_table_cell_style(hwnd, table, row, 2, fg=colors["text"], align=1)
        total = int(item[2])
        total_color = GREEN if total >= 1000 else (RED if total <= 100 else colors["text"])
        ui.set_table_cell_style(hwnd, table, row, 3, fg=total_color, align=1, font_flags=1)
        ui.set_table_cell_style(hwnd, table, row, 4, fg=ORANGE, align=1, font_flags=1)
        ui.set_table_cell_style(hwnd, table, row, 5, align=1)


def refresh_table(scroll_to=None):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    cols = table_columns()
    ui.set_table_columns_ex(hwnd, table, cols)
    ui.set_table_rows_ex(hwnd, table, table_rows(), cols)
    ui.set_table_selected_rows(hwnd, table, sorted(STATE["selected"]))
    if scroll_to is not None:
        ui.set_table_scroll(hwnd, table, max(0, scroll_to - 8), 0)
    style_table_rows()
    refresh_summary()


def apply_theme():
    colors = palette()
    hwnd = STATE["hwnd"]
    for eid, role, border_role, radius, border_width in STATE["panels"]:
        ui.set_panel_style(hwnd, eid, colors[role], colors[border_role], border_width, radius, 0)
    for eid, role in STATE["texts"]:
        ui.set_element_color(hwnd, eid, 0, colors[role])
    refresh_table()


def draw_toolbar(hwnd, root):
    y = 24
    button(hwnd, root, "🏠", "首页", 24, y, 68, 34, variant=0)
    button(hwnd, root, "🔄", "刷新", 100, y, 68, 34, variant=0)
    button(hwnd, root, "⬅", "后退", 176, y, 68, 34, variant=0)
    button(hwnd, root, "➡", "前进", 252, y, 68, 34, variant=0)
    button(hwnd, root, "🌙", "换肤", 328, y, 76, 34, variant=5, callback=on_toggle_theme)

    edit = ui.create_editbox(hwnd, root, 418, y + 1, 860, 32)
    ui.set_editbox_text(
        hwnd,
        edit,
        "https://mobile.yangkeduo.com/goods.html?goods_id=909137407205&oak_rcto=YVWKbBF56Kc78ru8AsYdt6_K-示例参数",
    )
    ui.set_editbox_options(hwnd, edit, readonly=False, password=False, multiline=False, placeholder="请输入商品链接")
    button(hwnd, root, "🚀", "GO", 1288, y, 74, 34, variant=2)


def draw_top_actions(hwnd, root):
    button(hwnd, root, "➕", "添加账号", 24, 86, 240, 46, variant=1, callback=on_add_account)
    button(hwnd, root, "➖", "删除账号", 276, 86, 240, 46, variant=2, callback=on_delete_account)
    STATE["current_text"] = label(hwnd, root, "", 24, 142, 390, 28, "text")


def draw_account_table(hwnd, root):
    STATE["table"] = ui.create_table_ex(
        hwnd, root, table_columns(), table_rows(),
        striped=True, bordered=True,
        x=TABLE_X, y=TABLE_Y, w=TABLE_W, h=TABLE_H,
        selection_mode=2,
        max_height=TABLE_H,
        fixed_header=True,
        horizontal_scroll=False,
        row_height=38,
        header_height=42,
    )
    ui.set_table_viewport_options(hwnd, STATE["table"], max_height=TABLE_H, fixed_header=True, horizontal_scroll=False)
    ui.set_table_cell_click_callback(hwnd, STATE["table"], on_table_click)
    ui.set_table_cell_action_callback(hwnd, STATE["table"], on_table_action)
    refresh_table()


def draw_browser_placeholder(hwnd, root):
    x, y, w, h = 686, 76, 430, 792
    panel(hwnd, root, x, y, w, h, "panel", "border", 0)
    viewport = ui.create_browser_viewport(hwnd, root, x=x + 1, y=y + 1, w=w - 2, h=h - 2)
    ui.set_browser_viewport_placeholder(
        hwnd,
        viewport,
        "🌐 手机浏览器放置区域",
        "这里预留给 WebView2 / CEF / 外部浏览器句柄。当前示例按手机竖屏宽度绘制，只显示占位组件。",
        "📱",
    )
    ui.set_browser_viewport_loading(hwnd, viewport, False, 0)
    label(hwnd, root, "商品页面将在这里显示", x + 115, y + h - 56, 200, 26, "muted", align=1)


def draw_right_actions(hwnd, root):
    x = 1140
    button(hwnd, root, "⚡", "开始采集", x, 86, 230, 46, variant=1)
    button(hwnd, root, "✂️", "停止采集", x, 164, 230, 46, variant=2)

    panel(hwnd, root, x, 260, 230, 100, "scan", "scan_border", 4)
    label(hwnd, root, "📱 手机扫码", x + 20, 276, 190, 26, "text", align=1)
    label(hwnd, root, "请在这里放置二维码", x + 22, 314, 186, 28, "muted", align=1)

    panel(hwnd, root, x, 386, 230, 154, "panel", "border", 4)
    label(hwnd, root, "🎬 商品讲解", x + 20, 404, 190, 28, "text", align=1)
    label(hwnd, root, "视频/图片位", x + 42, 452, 146, 30, "muted", align=1)
    label(hwnd, root, "此处仅做静态占位", x + 20, 502, 190, 24, "muted", align=1)

    panel(hwnd, root, x, 568, 230, 150, "panel", "border", 4)
    label(hwnd, root, "📊 采集状态", x + 20, 586, 190, 28, "text")
    STATE["selected_count_text"] = label(hwnd, root, "", x + 24, 626, 180, 24, "muted")
    label(hwnd, root, "任务状态：待开始", x + 24, 658, 180, 24, "muted")
    label(hwnd, root, "采集进度：0%", x + 24, 690, 180, 24, "muted")

    panel(hwnd, root, x, 742, 230, 126, "tip", "tip_border", 4)
    label(hwnd, root, "💡 提示：中间区域只是浏览器容器标记，真实网页由宿主程序后续接入。", x + 18, 754, 194, 96, "muted", wrap=True)


def main():
    hwnd = ui.create_window_ex("📦 PDD多账号采集面板", 30, 30, WINDOW_W, WINDOW_H, 0xFFE4E9F1)
    if not hwnd:
        print("窗口创建失败")
        return

    STATE["hwnd"] = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetThemeMode(hwnd, 0)

    root = ui.create_container(hwnd, 0, 0, 0, WINDOW_W, WINDOW_H)
    STATE["root"] = root
    STATE["root_bg"] = panel(hwnd, root, 0, 0, WINDOW_W, WINDOW_H, "bg", "bg", 0, 0)
    draw_toolbar(hwnd, root)
    draw_top_actions(hwnd, root)
    draw_account_table(hwnd, root)
    draw_browser_placeholder(hwnd, root)
    draw_right_actions(hwnd, root)
    refresh_table()

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages()


if __name__ == "__main__":
    main()
