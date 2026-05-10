import ctypes
import time
from ctypes import wintypes

import test_new_emoji as ui


user32 = ctypes.windll.user32
user32.SendMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM
user32.PeekMessageW.argtypes = [ctypes.c_void_p, wintypes.HWND, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
user32.PeekMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.c_void_p]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.c_void_p]
user32.DispatchMessageW.restype = wintypes.LPARAM


WM_LBUTTONDBLCLK = 0x0203
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_KEYDOWN = 0x0100
WM_CHAR = 0x0102
MK_LBUTTON = 0x0001
VK_BACK = 0x08
VK_END = 0x23
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
PM_REMOVE = 0x0001


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", ctypes.c_uint),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


def _lparam(x, y):
    return (int(x) & 0xFFFF) | ((int(y) & 0xFFFF) << 16)


def _pump(seconds=0.05):
    deadline = time.time() + seconds
    msg = MSG()
    while time.time() < deadline:
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.005)


def _double_click(hwnd, x, y):
    user32.SendMessageW(hwnd, WM_LBUTTONDBLCLK, 0, _lparam(x, y))
    _pump()


def _click(hwnd, x, y):
    user32.SendMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, _lparam(x, y))
    _pump(0.01)
    user32.SendMessageW(hwnd, WM_LBUTTONUP, 0, _lparam(x, y))
    _pump()


def _key(hwnd, vk):
    user32.SendMessageW(hwnd, WM_KEYDOWN, vk, 0)
    _pump()


def _char(hwnd, text):
    for ch in text:
        user32.SendMessageW(hwnd, WM_CHAR, ord(ch), 0)
        _pump(0.01)


def _cell_point(table_bounds, col):
    x, y, _, _ = table_bounds
    widths = [92, 176, 96]
    col_left = x + sum(widths[:col])
    return col_left + widths[col] // 2, y


def _double_click_cell(hwnd, table, table_bounds, row, col):
    x, base_y = _cell_point(table_bounds, col)
    for y in range(base_y + 72, base_y + 178, 8):
        _double_click(hwnd, x, y)
        state = ui.get_table_double_click_edit_state(hwnd, table)
        if state == (True, row, col):
            return x, y
    raise AssertionError(f"没有命中可编辑单元格 row={row} col={col}")


def test_table_double_click_edit():
    hwnd = ui.create_window("🧪 表格双击编辑测试", 180, 120, 760, 420)
    if not hwnd:
        raise RuntimeError("创建测试窗口失败")
    callback_events = []

    @ui.TableCellEditCallback
    def on_edit(table_id, row, col, action, utf8, length):
        text = ctypes.string_at(utf8, length).decode("utf-8", errors="replace") if utf8 and length > 0 else ""
        callback_events.append((table_id, row, col, action, text))

    try:
        root = ui.create_container(hwnd, 0, 0, 0, 720, 330)
        columns = [
            {"title": "编号 🔢", "key": "id", "width": 92},
            {"title": "名称 😊", "key": "name", "width": 176},
            {"title": "状态 ✅", "key": "state", "type": "status", "width": 96, "align": "center"},
        ]
        rows = [
            {"cells": ["001", "旧值 😊", {"type": "status", "value": "1", "options": {"status": 1}}]},
            {"cells": ["002", "保持不变 🌟", {"type": "status", "value": "2", "options": {"status": 2}}]},
        ]
        table = ui.create_table_ex(hwnd, root, columns, rows, True, True, 24, 64, 420, 190, selection_mode=1)
        ui.set_table_cell_edit_callback(hwnd, table, on_edit)
        ui.dll.EU_ShowWindow(hwnd, 1)
        _pump(0.1)

        assert ui.get_table_cell_double_click_editable(hwnd, table, 0, 1) is False
        ui.set_table_double_click_edit(hwnd, table, True)
        assert ui.get_table_cell_double_click_editable(hwnd, table, 0, 1) is True
        assert ui.get_table_cell_double_click_editable(hwnd, table, 0, 2) is False
        ui.set_table_column_double_click_edit(hwnd, table, 1, 0)
        assert ui.get_table_cell_double_click_editable(hwnd, table, 0, 1) is False
        ui.set_table_cell_double_click_edit(hwnd, table, 0, 1, 1)
        assert ui.get_table_cell_double_click_editable(hwnd, table, 0, 1) is True

        bounds = ui.get_element_bounds(hwnd, table)
        assert bounds is not None
        x, y = _double_click_cell(hwnd, table, bounds, 0, 1)
        assert ui.get_table_double_click_edit_state(hwnd, table) == (True, 0, 1)

        _key(hwnd, VK_END)
        for _ in range(8):
            _key(hwnd, VK_BACK)
        _char(hwnd, "新值完成")
        _key(hwnd, VK_RETURN)
        assert ui.get_table_cell_value(hwnd, table, 0, 1) == "新值完成"
        assert (table, 0, 1, 1, "旧值 😊") in callback_events
        assert (table, 0, 1, 2, "新值完成") in callback_events

        ui.set_table_cell(hwnd, table, 0, 1, "text", "取消前 😊")
        _double_click_cell(hwnd, table, bounds, 0, 1)
        _char(hwnd, "不提交")
        _key(hwnd, VK_ESCAPE)
        assert ui.get_table_cell_value(hwnd, table, 0, 1) == "取消前 😊"
        assert callback_events[-1] == (table, 0, 1, 3, "取消前 😊")

        _double_click_cell(hwnd, table, bounds, 0, 1)
        _key(hwnd, VK_END)
        for _ in range(8):
            _key(hwnd, VK_BACK)
        _char(hwnd, "失焦提交")
        outside_x, outside_y = bounds[0] + bounds[2] + 24, bounds[1] + 20
        _click(hwnd, outside_x, outside_y)
        assert ui.get_table_cell_value(hwnd, table, 0, 1) == "失焦提交"

        ui.set_table_virtual_options(hwnd, table, True, 8, 4)
        assert ui.get_table_cell_double_click_editable(hwnd, table, 0, 1) is False
    finally:
        ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    test_table_double_click_edit()
    print("✅ Table 双击编辑测试通过")
