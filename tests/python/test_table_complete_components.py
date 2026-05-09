import ctypes
from ctypes import wintypes
import os
import tempfile
import time

import test_new_emoji as ui


WINDOW_W = 1220
WINDOW_H = 780
CONTENT_W = 1180
CONTENT_H = 700

g_hwnd = None
g_table_id = 0
g_action_count = 0
g_click_count = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 📊 Table 高级能力验证正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.TableCellCallback
def on_table_cell_action(table_id, row, col, action, value):
    global g_action_count
    g_action_count += 1
    print(f"[表格回调] table={table_id} row={row} col={col} action={action} value={value}")


@ui.TableCellCallback
def on_table_cell_click(table_id, row, col, action, value):
    global g_click_count
    g_click_count += 1
    print(f"[表格点击] table={table_id} row={row} col={col} action={action} value={value}")


def build_columns():
    return [
        {"title": "选择", "key": "sel", "type": "selection", "width": 52, "fixed": "left", "align": "center"},
        {"title": "展开", "key": "open", "type": "expand", "width": 52, "fixed": "left", "align": "center"},
        {"title": "序号", "key": "idx", "type": "index", "width": 64, "fixed": "left", "align": "center"},
        {"title": "日期", "key": "date", "width": 116, "sortable": True, "filterable": True},
        {"title": "姓名", "key": "name", "width": 120, "sortable": True, "searchable": True},
        {"title": "地址", "key": "address", "parent": "配送信息", "width": 260, "tooltip": True},
        {"title": "标签", "key": "tag", "parent": "配送信息", "type": "tag", "width": 96, "align": "center", "filterable": True},
        {"title": "启用", "key": "enabled", "type": "switch", "width": 96, "align": "center"},
        {"title": "选择框", "key": "choice", "type": "select", "width": 150},
        {"title": "进度", "key": "progress", "type": "progress", "width": 132},
        {"title": "状态", "key": "status", "type": "status", "width": 108, "align": "center"},
        {"title": "操作", "key": "actions", "type": "buttons", "width": 156, "fixed": "right", "align": "center"},
    ]


def build_rows():
    def row(key, date, name, address, tag, checked, progress, status, parent="", level=0, expanded=False, lazy=False):
        return {
            "key": key,
            "parent": parent,
            "level": level,
            "expanded": expanded,
            "children": expanded,
            "lazy": lazy,
            "cells": [
                {"type": "selection"},
                {"type": "expand"},
                {"type": "index"},
                date,
                name,
                address,
                {"type": "tag", "value": tag},
                {"type": "switch", "value": "1" if checked else "0", "options": {"checked": checked}},
                {"type": "select", "value": ["待处理 ⏳", "配送中 🚚", "已完成 ✅"]},
                {"type": "progress", "value": progress},
                {"type": "status", "value": status, "options": {"status": status}},
                {"type": "buttons", "value": ["查看 👀", "编辑 ✏️", "移除 🗑️"]},
            ],
        }

    rows = [
        row("r0", "2016-05-02", "王小虎 🎯", "上海市普陀区金沙江路 1518 弄", "家 🏠", True, 88, 1, expanded=True),
        row("r0-1", "2016-05-02", "王小虎-明细", "厨房备货、门店复核、骑手揽收", "明细 📦", True, 54, 2, parent="r0", level=1),
        row("r1", "2016-05-04", "李小花 🌸", "上海市普陀区金沙江路 1517 弄", "公司 🏢", False, 42, 0, lazy=True),
        row("r2", "2016-05-01", "陈小云 ☁️", "上海市普陀区金沙江路 1519 弄", "家 🏠", True, 100, 1),
        row("r3", "2016-05-03", "赵小星 ⭐", "上海市普陀区金沙江路 1516 弄", "公司 🏢", True, 72, 2),
        row("r4", "2016-05-08", "周小竹 🎋", "上海市长宁区愚园路 88 号", "仓库 🧺", False, 35, 0),
    ]
    rows[3]["bg"] = 0xFFF0F9EB
    rows[3]["fg"] = 0xFF1F6F3A
    rows[3]["align"] = "center"
    rows[3]["font_flags"] = 1
    rows[3]["font_size"] = 15
    return rows


def dump_state(prefix):
    cell_value = ui.get_table_cell_value(g_hwnd, g_table_id, 0, 4)
    full_state = ui.get_table_full_state(g_hwnd, g_table_id)
    print(f"{prefix} 单元格(0,4)={cell_value} 状态={full_state} 回调次数={g_action_count}")


def run_row_crud_smoke():
    hwnd = ui.create_window("📊 表格行级增删测试", 180, 140, 760, 420)
    if not hwnd:
        raise RuntimeError("table row crud window create failed")
    try:
        root = ui.create_container(hwnd, 0, 0, 0, 720, 340)
        columns = [
            {"title": "编号 🔢", "key": "id", "width": 100},
            {"title": "姓名 😊", "key": "name", "width": 160},
            {"title": "状态 ✅", "key": "state", "width": 140},
        ]
        table = ui.create_table_ex(hwnd, root, columns, [], True, True, 20, 20, 660, 220, selection_mode=1)

        assert ui.add_table_row(hwnd, table, ["001", "小明 😊", "待处理"]) == 0
        assert ui.add_table_row(hwnd, table, ["002", "小红 🌸", "已完成"]) == 1
        assert ui.get_table_row_count(hwnd, table) == 2
        assert ui.get_table_cell_value(hwnd, table, 1, 1) == "小红 🌸"

        ui.dll.EU_SetTableSelectedRow(hwnd, table, 1)
        assert ui.insert_table_row(hwnd, table, 1, ["001-1", "插入行 ✨", "处理中"]) == 1
        assert ui.get_table_row_count(hwnd, table) == 3
        assert ui.get_table_cell_value(hwnd, table, 1, 1) == "插入行 ✨"
        assert ui.dll.EU_GetTableSelectedRow(hwnd, table) == 2

        assert ui.delete_table_row(hwnd, table, 0)
        assert ui.get_table_row_count(hwnd, table) == 2
        assert ui.get_table_cell_value(hwnd, table, 0, 0) == "001-1"
        assert ui.dll.EU_GetTableSelectedRow(hwnd, table) == 1

        assert ui.delete_table_row(hwnd, table, 1)
        assert ui.get_table_row_count(hwnd, table) == 1
        assert ui.dll.EU_GetTableSelectedRow(hwnd, table) == -1

        assert ui.clear_table_rows(hwnd, table)
        assert ui.get_table_row_count(hwnd, table) == 0
        assert ui.dll.EU_GetTableSelectedRow(hwnd, table) == -1
        assert not ui.delete_table_row(hwnd, table, 0)
    finally:
        ui.dll.EU_DestroyWindow(hwnd)


def run_virtual_table_smoke():
    hwnd = ui.create_window("📊 Table 虚表烟雾测试", 160, 120, 920, 520)
    if not hwnd:
        raise RuntimeError("virtual table smoke window create failed")
    try:
        root = ui.create_container(hwnd, 0, 0, 0, 880, 460)
        columns = [
            {"title": "序号", "key": "idx", "type": "index", "width": 68, "fixed": "left", "align": "center"},
            {"title": "日期", "key": "date", "width": 132, "sortable": True},
            {"title": "姓名", "key": "name", "width": 128, "searchable": True},
            {"title": "地址", "key": "address", "width": 320, "tooltip": True},
            {"title": "标签", "key": "tag", "type": "tag", "width": 120, "align": "center"},
            {"title": "进度", "key": "progress", "type": "progress", "width": 180},
            {"title": "状态", "key": "status", "type": "status", "width": 100, "align": "center"},
            {"title": "操作", "key": "actions", "type": "buttons", "width": 160, "fixed": "right", "align": "center"},
        ]
        hits = {"count": 0}

        def provider(table_id, row):
            hits["count"] += 1
            day = 1 + (row % 28)
            progress = 30 + (row * 9 % 70)
            tag = "家 🏠" if row % 2 == 0 else "公司 🏢"
            status = row % 4
            actions = ["查看 👀", "编辑 ✏️"] if row % 2 == 0 else ["详情 📄", "归档 🗃️"]
            return (
                f"key=v{row}\t"
                f"c0={row + 1}\t"
                f"c1=2026-05-{day:02d}\t"
                f"c2=虚表 {row + 1}\t"
                f"c3=上海市普陀区金沙江路 {1518 + (row % 4)} 弄\t"
                f"c4={tag}\t"
                f"c5={progress}\t"
                f"c6={status}\t"
                f"c6_options=status={status}\t"
                f"c7={'|'.join(actions)}"
            )

        table = ui.create_table_ex(hwnd, root, columns, [], True, True, 20, 20, 860, 300, selection_mode=1, max_height=300)
        ui.set_table_virtual_options(hwnd, table, True, 96, 24)
        ui.set_table_virtual_row_provider(hwnd, table, provider)
        ui.set_table_header_drag_options(hwnd, table, True, True, 72, 360, 48, 132)
        assert ui.get_table_row_count(hwnd, table) == 96
        assert ui.add_table_row(hwnd, table, ["虚表新增失败"]) == -1
        assert ui.insert_table_row(hwnd, table, 0, ["虚表插入失败"]) == -1
        assert not ui.delete_table_row(hwnd, table, 0)
        assert not ui.clear_table_rows(hwnd, table)
        assert ui.get_table_row_count(hwnd, table) == 96
        assert ui.get_table_cell_value(hwnd, table, 0, 1) == "2026-05-01"
        assert ui.get_table_cell_value(hwnd, table, 12, 2) == "虚表 13"
        before = hits["count"]
        ui.clear_table_virtual_cache(hwnd, table)
        assert ui.get_table_cell_value(hwnd, table, 1, 4) in ("家 🏠", "公司 🏢")
        assert hits["count"] > before
        ui.set_table_scroll(hwnd, table, 18, 0)
        xlsx_path = os.path.join(tempfile.gettempdir(), "new_emoji_table_smoke.xlsx")
        assert ui.export_table_excel(hwnd, table, xlsx_path)
        assert os.path.exists(xlsx_path)
        assert os.path.getsize(xlsx_path) > 0

        imported = ui.create_table_ex(hwnd, root, columns, [], True, True, 20, 340, 860, 140, selection_mode=0, max_height=140)
        assert ui.import_table_excel(hwnd, imported, xlsx_path)
        assert ui.get_table_row_count(hwnd, imported) == 96
        assert ui.get_table_cell_value(hwnd, imported, 0, 1) == "2026-05-01"
        state = ui.get_table_full_state(hwnd, table)
        assert "virtual=1" in state
    finally:
        ui.dll.EU_DestroyWindow(hwnd)


def main():
    global g_hwnd, g_table_id

    run_row_crud_smoke()
    run_virtual_table_smoke()

    hwnd = ui.create_window("📊 Table 高级样式与单元格控件验证", 140, 70, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "📊 Table 高级样式与单元格控件验证", 28, 18, 620, 34)
    ui.create_divider(hwnd, content_id, "基础/斑马/边框、固定列、多级表头、选择、排序筛选搜索、展开树形、合计合并、内置控件", 0, 1, 28, 58, 1120, 30)

    columns = build_columns()
    rows = build_rows()
    g_table_id = ui.create_table_ex(
        hwnd, content_id, columns, rows,
        striped=True, bordered=True, x=28, y=104, w=1120, h=470,
        selection_mode=2, tree=True, lazy=True,
        max_height=470, fixed_header=True, horizontal_scroll=True,
        summary=["合计 🧮", "", "", "6 条", "", "", "", "", "", "391%", "", "全部可点"],
    )

    ui.set_table_cell_click_callback(hwnd, g_table_id, on_table_cell_click)
    ui.set_table_cell_action_callback(hwnd, g_table_id, on_table_cell_action)
    ui.set_table_selected_rows(hwnd, g_table_id, [0, 2, 3])
    ui.set_table_row_style(hwnd, g_table_id, 1, 0xFFFFF8E8, 0xFF7A4A00, 0, 0, 14)
    ui.set_table_cell_style(hwnd, g_table_id, 0, 5, 0xFFEAF2FF, 0xFF1E4D8F, 0, 1, 15)
    ui.set_table_span(hwnd, g_table_id, 4, 5, 1, 2)
    ui.set_table_row_expanded(hwnd, g_table_id, 0, True)
    ui.set_table_scroll(hwnd, g_table_id, 0, 0)

    ui.set_table_filter(hwnd, g_table_id, 6, "家 🏠")
    dump_state("[筛选后]")
    ui.clear_table_filter(hwnd, g_table_id)
    ui.set_table_search(hwnd, g_table_id, "小")
    dump_state("[搜索后]")
    ui.set_table_search(hwnd, g_table_id, "")
    ui.set_table_sort(hwnd, g_table_id, 3, desc=True)

    ui.create_infobox(
        hwnd, content_id,
        "✅ 覆盖项",
        "已设置高级列/行协议、固定列、多级表头、索引/选择/展开、按钮组、开关、选择框、进度条、状态、标签、行/单元格样式、筛选搜索、合计与合并。",
        28, 600, 1120, 72,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    dump_state("[初始完成状态]")
    duration = int(os.environ.get("EU_TEST_SECONDS", "30"))
    print(f"Table 高级能力验证窗口已显示，请观察 {duration} 秒或手动关闭。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < duration:
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

    ui.dll.EU_DestroyWindow(hwnd)
    print("Table 高级能力验证结束。")


if __name__ == "__main__":
    main()
