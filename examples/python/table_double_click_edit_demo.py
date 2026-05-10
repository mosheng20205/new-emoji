import ctypes
import time
from ctypes import wintypes

import new_emoji_ui as ui


BG = 0xFF101522
PANEL = 0xFF172033
PANEL_2 = 0xFF1E2A42
PANEL_3 = 0xFF24314D
BORDER = 0xFF33415F
TEXT = 0xFFE3EAF7
MUTED = 0xFFAAB7D4
ACCENT = 0xFF6EA8FE
GREEN = 0xFF69D28D
GOLD = 0xFFE0B15C
RED = 0xFFE36A6A

STATE = {
    "hwnd": 0,
    "table": 0,
    "virtual_table": 0,
    "status": 0,
    "log": 0,
    "table_enabled": True,
    "name_column_override": 0,
    "first_name_override": 1,
}

CALLBACKS = []
LOG_LINES = []


def keep_callback(cb):
    CALLBACKS.append(cb)
    return cb


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


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


def add_text(hwnd, parent, text, x, y, w, h, color=TEXT):
    element_id = ui.create_text(hwnd, parent, text, x, y, w, h)
    ui.set_element_color(hwnd, element_id, 0, color)
    return element_id


def add_panel(hwnd, parent, x, y, w, h, color=PANEL):
    element_id = ui.create_panel(hwnd, parent, x, y, w, h, color)
    ui.set_element_color(hwnd, element_id, color, TEXT)
    return element_id


def add_button(hwnd, parent, emoji, text, x, y, w, h, bg=PANEL_3, fg=TEXT):
    element_id = ui.create_button(hwnd, parent, emoji, text, x, y, w, h)
    ui.set_element_color(hwnd, element_id, bg, fg)
    return element_id


def bind_click(hwnd, element_id, fn):
    ui.dll.EU_SetElementClickCallback(hwnd, element_id, keep_callback(ui.ClickCallback(fn)))


def apply_dark_theme(hwnd):
    ui.set_theme_token(hwnd, "panel_bg", BG)
    ui.set_theme_token(hwnd, "panel_bg_light", PANEL)
    ui.set_theme_token(hwnd, "button_bg", PANEL_3)
    ui.set_theme_token(hwnd, "button_hover", 0xFF2C3C5D)
    ui.set_theme_token(hwnd, "button_press", 0xFF324B78)
    ui.set_theme_token(hwnd, "edit_bg", 0xFF151C2B)
    ui.set_theme_token(hwnd, "edit_border", BORDER)
    ui.set_theme_token(hwnd, "edit_focus", ACCENT)
    ui.set_theme_token(hwnd, "text_primary", TEXT)
    ui.set_theme_token(hwnd, "text_secondary", MUTED)
    ui.set_theme_token(hwnd, "text_muted", 0xFF7F8AA8)
    ui.set_theme_token(hwnd, "titlebar_bg", 0xFF0C111D)
    ui.set_theme_token(hwnd, "titlebar_text", TEXT)
    ui.set_theme_token(hwnd, "border_default", BORDER)
    ui.set_theme_token(hwnd, "accent", ACCENT)
    ui.dll.EU_SetTitleBarButtonStyle(hwnd, 46, 30, TEXT, 0xFF202B42, 0xFF5B2530)


def make_columns():
    return [
        {"title": "编号 🔢", "key": "id", "width": 92, "align": "center"},
        {"title": "姓名 😊", "key": "name", "width": 170},
        {"title": "备注 ✍️", "key": "note", "width": 270, "tooltip": True},
        {"title": "启用 🟢", "key": "enabled", "type": "switch", "width": 92, "align": "center"},
        {"title": "状态 ✅", "key": "status", "type": "status", "width": 96, "align": "center"},
        {"title": "分组 📦", "key": "group", "type": "select", "width": 130},
        {"title": "操作 🛠️", "key": "actions", "type": "buttons", "width": 164, "align": "center"},
    ]


def make_rows():
    return [
        {
            "cells": [
                "001",
                "阿狸 😊",
                "首行姓名被单元格级重新启用，可双击编辑",
                {"type": "switch", "value": "1", "options": {"checked": True}},
                {"type": "status", "value": "1", "options": {"status": 1}},
                {"type": "select", "value": ["研发组 🌙", "设计组 🎨", "运维组 🧰"]},
                {"type": "buttons", "value": ["查看 👁️", "标记 ⭐"]},
            ]
        },
        {
            "cells": [
                "002",
                "小蓝 🌊",
                "姓名列被列级禁用，这一格默认不能编辑",
                {"type": "switch", "value": "0", "options": {"checked": False}},
                {"type": "status", "value": "2", "options": {"status": 2}},
                {"type": "select", "value": ["设计组 🎨", "研发组 🌙", "运维组 🧰"]},
                {"type": "buttons", "value": ["查看 👁️", "归档 📦"]},
            ]
        },
        {
            "cells": [
                "003",
                "木木 🌲",
                "备注列继承默认可编辑，适合测试 Enter 提交",
                {"type": "switch", "value": "1", "options": {"checked": True}},
                {"type": "status", "value": "0", "options": {"status": 0}},
                {"type": "select", "value": ["运维组 🧰", "研发组 🌙", "设计组 🎨"]},
                {"type": "buttons", "value": ["查看 👁️", "提醒 🔔"]},
            ]
        },
        {
            "cells": [
                "004",
                "星河 ✨",
                "双击后输入中文或 emoji，再点击右侧面板可失焦提交",
                {"type": "switch", "value": "1", "options": {"checked": True}},
                {"type": "status", "value": "1", "options": {"status": 1}},
                {"type": "select", "value": ["研发组 🌙", "设计组 🎨", "运维组 🧰"]},
                {"type": "buttons", "value": ["查看 👁️", "完成 ✅"]},
            ]
        },
        {
            "cells": [
                "005",
                "青柠 🍋",
                "滚轮或程序滚动会先提交正在编辑的单元格",
                {"type": "switch", "value": "0", "options": {"checked": False}},
                {"type": "status", "value": "2", "options": {"status": 2}},
                {"type": "select", "value": ["设计组 🎨", "研发组 🌙", "运维组 🧰"]},
                {"type": "buttons", "value": ["查看 👁️", "暂停 ⏸️"]},
            ]
        },
        {
            "cells": [
                "006",
                "夜航 🚀",
                "这一行用于滚动可见性与编辑提交回归",
                {"type": "switch", "value": "1", "options": {"checked": True}},
                {"type": "status", "value": "1", "options": {"status": 1}},
                {"type": "select", "value": ["运维组 🧰", "研发组 🌙", "设计组 🎨"]},
                {"type": "buttons", "value": ["查看 👁️", "同步 🔄"]},
            ]
        },
    ]


def style_table(hwnd, table):
    ui.set_element_color(hwnd, table, 0xFF141B2A, TEXT)
    for row in range(ui.get_table_row_count(hwnd, table)):
        bg = 0xFF182238 if row % 2 == 0 else 0xFF151D30
        ui.set_table_row_style(hwnd, table, row, bg, TEXT, -1, -1, 14)
    ui.set_table_cell_style(hwnd, table, 0, 1, 0xFF20395F, TEXT, -1, 1, 14)
    ui.set_table_cell_style(hwnd, table, 1, 1, 0xFF2A2234, MUTED, -1, -1, 14)
    ui.set_table_cell_style(hwnd, table, 0, 2, 0xFF18344A, TEXT, -1, -1, 14)


def push_log(message):
    LOG_LINES.insert(0, message)
    del LOG_LINES[9:]
    ui.set_element_text(STATE["hwnd"], STATE["log"], "\n".join(LOG_LINES))


def editable_label(row, col):
    ok = ui.get_table_cell_double_click_editable(STATE["hwnd"], STATE["table"], row, col)
    return "可编辑" if ok else "不可编辑"


def refresh_status(note="状态已刷新"):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    enabled, editing_row, editing_col = ui.get_table_double_click_edit_state(hwnd, table)
    virtual_ok = ui.get_table_cell_double_click_editable(hwnd, STATE["virtual_table"], 0, 1)
    text = (
        f"{note}\n"
        f"总开关：{'开启' if enabled else '关闭'}    当前编辑：行 {editing_row} / 列 {editing_col}\n"
        f"覆盖：姓名列={STATE['name_column_override']}    首行姓名={STATE['first_name_override']}\n"
        f"可编辑查询：首行姓名 {editable_label(0, 1)}；第二行姓名 {editable_label(1, 1)}；首行备注 {editable_label(0, 2)}；状态列 {editable_label(0, 4)}\n"
        f"虚表文本单元格：{'可编辑' if virtual_ok else '不可编辑'}    首行备注值：{ui.get_table_cell_value(hwnd, table, 0, 2)}"
    )
    ui.set_element_text(hwnd, STATE["status"], text)


def set_main_edit_enabled(enabled):
    STATE["table_enabled"] = enabled
    ui.set_table_double_click_edit(STATE["hwnd"], STATE["table"], enabled)
    push_log(f"⚙️ EU_SetTableDoubleClickEdit：{'开启' if enabled else '关闭'}")
    refresh_status("已切换表级双击编辑总开关")


def set_name_column_override(value):
    STATE["name_column_override"] = value
    ui.set_table_column_double_click_edit(STATE["hwnd"], STATE["table"], 1, value)
    push_log(f"📚 EU_SetTableColumnDoubleClickEdit：姓名列 = {value}")
    refresh_status("已设置姓名列覆盖")


def set_first_name_override(value):
    STATE["first_name_override"] = value
    ui.set_table_cell_double_click_edit(STATE["hwnd"], STATE["table"], 0, 1, value)
    push_log(f"📍 EU_SetTableCellDoubleClickEdit：首行姓名 = {value}")
    refresh_status("已设置首行姓名单元格覆盖")


def reset_demo(_element_id=0):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    ui.set_table_rows_ex(hwnd, table, make_rows(), make_columns())
    style_table(hwnd, table)
    ui.set_table_double_click_edit(hwnd, table, True)
    ui.set_table_column_double_click_edit(hwnd, table, 1, 0)
    ui.set_table_cell_double_click_edit(hwnd, table, 0, 1, 1)
    STATE["table_enabled"] = True
    STATE["name_column_override"] = 0
    STATE["first_name_override"] = 1
    push_log("🔄 已重置数据与覆盖规则")
    refresh_status("数据与编辑规则已重置")


def scroll_table(_element_id=0):
    ui.set_table_scroll(STATE["hwnd"], STATE["table"], 3, 0)
    push_log("🧭 已调用 EU_SetTableScroll，若正在编辑会先提交")
    refresh_status("程序滚动已执行")


def query_editable(_element_id=0):
    push_log(
        "🔎 查询："
        f"首行姓名={editable_label(0, 1)}，"
        f"第二行姓名={editable_label(1, 1)}，"
        f"备注={editable_label(0, 2)}，"
        f"状态列={editable_label(0, 4)}"
    )
    refresh_status("已读取可编辑性和编辑状态")


@ui.TableCellEditCallback
def on_cell_edit(table_id, row, col, action, utf8, length):
    if table_id != STATE["table"]:
        return
    text = ctypes.string_at(utf8, length).decode("utf-8", errors="replace") if utf8 and length > 0 else ""
    name = {1: "开始编辑", 2: "提交编辑", 3: "取消编辑"}.get(action, f"未知 {action}")
    push_log(f"✍️ {name}：行 {row} 列 {col}，文本：{text}")
    refresh_status(f"收到编辑回调：{name}")


@ui.TableCellCallback
def on_cell_click(table_id, row, col, action, value):
    if table_id == STATE["table"]:
        push_log(f"🖱️ 单击回调：行 {row} 列 {col}")


@ui.TableCellCallback
def on_cell_action(table_id, row, col, action, value):
    if table_id == STATE["table"]:
        push_log(f"🎛️ 动作回调：行 {row} 列 {col} action={action} value={value}")


def build_virtual_table(hwnd, parent):
    columns = [
        {"title": "虚表序号 🔢", "key": "id", "width": 118, "align": "center"},
        {"title": "虚表文本 🌌", "key": "name", "width": 210},
        {"title": "说明 🧊", "key": "note", "width": 250},
    ]
    table = ui.create_table_ex(
        hwnd, parent, columns, [], True, True,
        18, 50, 572, 92,
        selection_mode=0, max_height=92,
        row_height=34, header_height=38,
    )
    ui.set_element_color(hwnd, table, 0xFF141B2A, TEXT)
    ui.set_table_double_click_edit(hwnd, table, True)
    ui.set_table_virtual_options(hwnd, table, True, 32, 8)

    def provider(_table_id, row):
        return (
            f"key=v{row}\t"
            f"c0={row + 1:03d}\t"
            f"c1=虚表缓存 {row + 1} 🌌\t"
            "c2=虚表默认不进入原地编辑，避免只改缓存"
        )

    ui.set_table_virtual_row_provider(hwnd, table, provider)
    return table


def main():
    hwnd = ui.create_window("🌙 Table 双击原地编辑全功能演示", 140, 80, 1320, 820)
    if not hwnd:
        raise RuntimeError("窗口创建失败")
    STATE["hwnd"] = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    apply_dark_theme(hwnd)

    root = ui.create_container(hwnd, 0, 0, 0, 1280, 750)
    ui.set_element_color(hwnd, root, BG, TEXT)

    add_text(hwnd, root, "🌙 Table 双击原地编辑全功能演示", 28, 20, 560, 36, TEXT)
    add_text(
        hwnd, root,
        "双击普通文本单元格进入编辑；Enter 提交，Esc 取消，点击其他区域失焦提交。控制型单元格和虚表不会进入编辑。",
        28, 58, 1050, 28, MUTED,
    )

    main_table_panel = add_panel(hwnd, root, 18, 104, 876, 370, PANEL)
    add_text(hwnd, main_table_panel, "🧾 主表：文本列可编辑，控件列保持原交互", 16, 12, 560, 28, TEXT)
    table = ui.create_table_ex(
        hwnd, main_table_panel,
        make_columns(), make_rows(),
        striped=True, bordered=True,
        x=16, y=50, w=842, h=300,
        selection_mode=1, max_height=300,
        row_height=48, header_height=50,
    )
    STATE["table"] = table
    style_table(hwnd, table)
    ui.set_table_cell_edit_callback(hwnd, table, on_cell_edit)
    ui.set_table_cell_click_callback(hwnd, table, on_cell_click)
    ui.set_table_cell_action_callback(hwnd, table, on_cell_action)

    control_panel = add_panel(hwnd, root, 912, 104, 350, 370, PANEL_2)
    add_text(hwnd, control_panel, "⚙️ 编辑开关与查询", 18, 12, 260, 28, TEXT)
    buttons = [
        ("🟢", "开启总开关", 18, 52, lambda _eid: set_main_edit_enabled(True), GREEN),
        ("🌑", "关闭总开关", 184, 52, lambda _eid: set_main_edit_enabled(False), PANEL_3),
        ("🚫", "禁用姓名列", 18, 102, lambda _eid: set_name_column_override(0), RED),
        ("↩️", "姓名列继承", 184, 102, lambda _eid: set_name_column_override(-1), PANEL_3),
        ("📍", "启用首行姓名", 18, 152, lambda _eid: set_first_name_override(1), ACCENT),
        ("🔒", "禁用首行姓名", 184, 152, lambda _eid: set_first_name_override(0), PANEL_3),
        ("🔎", "查询可编辑性", 18, 202, query_editable, PANEL_3),
        ("🧭", "滚动提交", 184, 202, scroll_table, PANEL_3),
        ("🔄", "重置演示", 18, 252, reset_demo, GOLD),
    ]
    for emoji, text, x, y, fn, color in buttons:
        width = 314 if text == "重置演示" else 148
        btn = add_button(hwnd, control_panel, emoji, text, x, y, width, 38, color, 0xFF111827 if color == GOLD else TEXT)
        bind_click(hwnd, btn, fn)
    add_text(hwnd, control_panel, "提示：编辑时点这里的任意按钮，也会触发表格失焦提交。", 18, 314, 306, 40, MUTED)

    log_panel = add_panel(hwnd, root, 18, 492, 572, 222, 0xFF141C2B)
    add_text(hwnd, log_panel, "📜 回调日志", 18, 12, 220, 28, TEXT)
    STATE["log"] = add_text(hwnd, log_panel, "等待双击编辑或点击表格控件…", 18, 48, 532, 154, MUTED)

    state_panel = add_panel(hwnd, root, 612, 492, 650, 222, 0xFF141C2B)
    add_text(hwnd, state_panel, "🔬 状态与虚表禁用验证", 18, 12, 300, 28, TEXT)
    STATE["virtual_table"] = build_virtual_table(hwnd, state_panel)
    STATE["status"] = add_text(hwnd, state_panel, "", 18, 150, 604, 62, MUTED)

    reset_demo()
    push_log("✅ 窗口不会自动关闭，请手动关闭结束演示")
    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages()


if __name__ == "__main__":
    main()
