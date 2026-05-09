import ctypes
import time
from ctypes import wintypes

import new_emoji_ui as ui


STATE = {
    "hwnd": 0,
    "table": 0,
    "status": 0,
    "next_no": 4,
}

CALLBACKS = []


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


def refresh_status(message):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    row_count = ui.get_table_row_count(hwnd, table)
    selected = ui.dll.EU_GetTableSelectedRow(hwnd, table)
    sample = ui.get_table_cell_value(hwnd, table, 0, 1) if row_count > 0 else "暂无数据"
    ui.set_element_text(
        hwnd,
        STATE["status"],
        f"{message}\n📌 当前行数：{row_count}  选中行：{selected}  第一行姓名：{sample}",
    )


def make_row(no, name, state):
    return [
        f"{no:03d}",
        name,
        state,
        {"type": "tag", "value": "演示 🧪"},
    ]


def on_add(_element_id):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    no = STATE["next_no"]
    STATE["next_no"] += 1
    index = ui.add_table_row(hwnd, table, make_row(no, f"新增用户 {no} ➕", "刚添加"))
    refresh_status(f"➕ EU_AddTableRow 返回：{index}")


def on_insert(_element_id):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    selected = ui.dll.EU_GetTableSelectedRow(hwnd, table)
    row_count = ui.get_table_row_count(hwnd, table)
    target = selected if selected >= 0 else min(1, row_count)
    no = STATE["next_no"]
    STATE["next_no"] += 1
    index = ui.insert_table_row(hwnd, table, target, make_row(no, f"插入用户 {no} ✨", "插入完成"))
    refresh_status(f"✨ EU_InsertTableRow 目标：{target}，返回：{index}")


def on_delete(_element_id):
    hwnd = STATE["hwnd"]
    table = STATE["table"]
    selected = ui.dll.EU_GetTableSelectedRow(hwnd, table)
    if selected < 0:
        selected = ui.get_table_row_count(hwnd, table) - 1
    ok = ui.delete_table_row(hwnd, table, selected) if selected >= 0 else False
    refresh_status(f"🗑️ EU_DeleteTableRow 行：{selected}，返回：{1 if ok else 0}")


def on_clear(_element_id):
    ok = ui.clear_table_rows(STATE["hwnd"], STATE["table"])
    refresh_status(f"🧹 EU_ClearTableRows 返回：{1 if ok else 0}")


def bind_click(hwnd, element_id, fn):
    cb = keep_callback(ui.ClickCallback(fn))
    ui.dll.EU_SetElementClickCallback(hwnd, element_id, cb)


def main():
    hwnd = ui.create_window("📊 Table 行级增删 API 演示", 180, 120, 980, 620)
    if not hwnd:
        raise RuntimeError("窗口创建失败")
    STATE["hwnd"] = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    root = ui.create_container(hwnd, 0, 0, 0, 940, 540)
    ui.create_text(hwnd, root, "📊 Table 行级增删 API 演示", 28, 22, 500, 34)
    ui.create_text(hwnd, root, "点击表格行可改变选中行；四个按钮分别调用新增的 DLL 方法。", 28, 58, 760, 26)

    columns = [
        {"title": "编号 🔢", "key": "no", "width": 110},
        {"title": "姓名 😊", "key": "name", "width": 220},
        {"title": "状态 ✅", "key": "state", "width": 160},
        {"title": "标签 🏷️", "key": "tag", "type": "tag", "width": 130, "align": "center"},
    ]
    rows = [
        make_row(1, "小明 😊", "待处理"),
        make_row(2, "小红 🌸", "进行中"),
        make_row(3, "小李 🚀", "已完成"),
    ]

    table = ui.create_table_ex(
        hwnd,
        root,
        columns,
        rows,
        striped=True,
        bordered=True,
        x=28,
        y=98,
        w=720,
        h=250,
        selection_mode=1,
        max_height=250,
        row_height=44,
        header_height=46,
    )
    STATE["table"] = table
    ui.dll.EU_SetTableSelectedRow(hwnd, table, 0)

    btn_add = ui.create_button(hwnd, root, "➕", "添加行", 770, 104, 140, 40, variant=1)
    btn_insert = ui.create_button(hwnd, root, "✨", "插入行", 770, 154, 140, 40, variant=0)
    btn_delete = ui.create_button(hwnd, root, "🗑️", "删除行", 770, 204, 140, 40, variant=3)
    btn_clear = ui.create_button(hwnd, root, "🧹", "清空行", 770, 254, 140, 40, variant=2)

    bind_click(hwnd, btn_add, on_add)
    bind_click(hwnd, btn_insert, on_insert)
    bind_click(hwnd, btn_delete, on_delete)
    bind_click(hwnd, btn_clear, on_clear)

    STATE["status"] = ui.create_text(hwnd, root, "", 28, 374, 880, 68)
    ui.create_text(hwnd, root, "✅ 本示例不会自动关闭，请手动关闭窗口结束演示。", 28, 462, 720, 28)
    refresh_status("✅ 初始数据已创建，可开始测试四个新增 DLL 方法。")

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages()


if __name__ == "__main__":
    main()
