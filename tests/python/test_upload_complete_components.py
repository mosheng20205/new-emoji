import base64
import ctypes
import os
import tempfile
import time
from ctypes import wintypes

import test_new_emoji as ui


g_hwnd = None
g_selected_text = ""
g_action_events = []
g_callbacks = []


PNG_1X1 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt", wintypes.POINT),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


@ui.TextCallback
def on_select(element_id, data, length):
    global g_selected_text
    raw = ctypes.string_at(data, length) if data and length > 0 else b""
    g_selected_text = raw.decode("utf-8", errors="replace")
    print(f"[选择回调] 元素={element_id} 文件={g_selected_text}")


@ui.ValueCallback
def on_upload_action(element_id, action, index, value):
    g_action_events.append((action, index, value))
    print(f"[上传动作] 元素={element_id} 动作={action} 索引={index} 值={value}")


def keep_callbacks():
    g_callbacks.extend([on_close, on_select, on_upload_action])


def make_sample_files():
    folder = tempfile.mkdtemp(prefix="new_emoji_upload_")
    png1 = os.path.join(folder, "封面图片.png")
    png2 = os.path.join(folder, "头像素材.png")
    txt = os.path.join(folder, "说明文档.txt")
    big = os.path.join(folder, "超大图片.png")
    with open(png1, "wb") as f:
        f.write(base64.b64decode(PNG_1X1))
    with open(png2, "wb") as f:
        f.write(base64.b64decode(PNG_1X1))
    with open(txt, "w", encoding="utf-8") as f:
        f.write("📤 上传组件测试文件\n")
    with open(big, "wb") as f:
        f.write(base64.b64decode(PNG_1X1) + b"x" * 4096)
    return folder, png1, png2, txt, big


def pump_messages(duration=0.1):
    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    end = time.time() + duration
    while time.time() < end:
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.01)


def make_lparam(x, y):
    return (int(y) << 16) | (int(x) & 0xFFFF)


def client_size(hwnd):
    rect = wintypes.RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
    return rect.right - rect.left, rect.bottom - rect.top


def preview_close_point(hwnd):
    w, h = client_size(hwnd)
    margin_x = max(28.0, min(96.0, w * 0.06))
    margin_y = max(34.0, min(96.0, h * 0.07))
    panel_w = max(280.0, w - margin_x * 2.0)
    panel_h = max(220.0, h - margin_y * 2.0)
    if panel_w > w:
        panel_w = w
    if panel_h > h:
        panel_h = h
    panel_left = (w - panel_w) * 0.5
    panel_top = (h - panel_h) * 0.5
    panel_right = panel_left + panel_w
    return int(panel_right - 28), int(panel_top + 24)


def send_escape(hwnd):
    send_message = ctypes.windll.user32.SendMessageW
    send_message.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    send_message.restype = wintypes.LPARAM
    send_message(hwnd, 0x0100, 0x1B, 0)
    pump_messages(0.05)


def send_left_click(hwnd, x, y):
    send_message = ctypes.windll.user32.SendMessageW
    send_message.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    send_message.restype = wintypes.LPARAM
    lp = make_lparam(x, y)
    send_message(hwnd, 0x0201, 1, lp)
    send_message(hwnd, 0x0202, 0, lp)
    pump_messages(0.05)


def send_drop_files(hwnd, paths, x, y):
    payload = ("\0".join(paths) + "\0\0").encode("utf-16le")
    header_size = ctypes.sizeof(DROPFILES)
    total_size = header_size + len(payload)
    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL
    handle = kernel32.GlobalAlloc(0x0042, total_size)
    if not handle:
        raise RuntimeError("创建拖拽内存失败")
    ptr = kernel32.GlobalLock(handle)
    if not ptr:
        raise RuntimeError("锁定拖拽内存失败")
    drop = DROPFILES()
    drop.pFiles = header_size
    drop.pt.x = int(x)
    drop.pt.y = int(y)
    drop.fNC = False
    drop.fWide = True
    ctypes.memmove(ptr, ctypes.byref(drop), header_size)
    ctypes.memmove(ptr + header_size, payload, len(payload))
    kernel32.GlobalUnlock(handle)

    send_message = ctypes.windll.user32.SendMessageW
    send_message.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    send_message.restype = wintypes.LPARAM
    send_message(hwnd, 0x0233, handle, 0)
    pump_messages(0.05)


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    global g_hwnd
    keep_callbacks()
    folder, png1, png2, txt, big = make_sample_files()

    hwnd = ui.create_window("📤 上传组件完整验证", 180, 80, 1060, 720)
    assert_state(hwnd, "窗口创建失败")
    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1020, 660)

    upload_id = ui.create_upload(
        hwnd, root,
        "📤 点击或拖拽文件到此处上传",
        "只能选择 PNG 图片，最多 2 个，单文件不超过 2KB",
        [],
        32, 72, 760, 330,
    )
    ui.set_upload_select_callback(hwnd, upload_id, on_select)
    ui.set_upload_action_callback(hwnd, upload_id, on_upload_action)

    ui.set_upload_options(hwnd, upload_id, multiple=True, auto_upload=False)
    ui.set_upload_style(hwnd, upload_id, style_mode=5, show_file_list=True,
                        show_tip=True, show_actions=True, drop_enabled=True)
    ui.set_upload_texts(
        hwnd, upload_id,
        "📤 拖拽或点击上传图片",
        "支持系统文件选择、系统拖入、数量限制和类型过滤",
        "📤 点击上传",
        "🚀 上传到服务器",
    )
    ui.set_upload_constraints(hwnd, upload_id, limit=2, max_size_kb=2, accept=".png")
    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(0.1)

    style = ui.get_upload_style(hwnd, upload_id)
    assert_state(style["style_mode"] == 5 and style["drop_enabled"], "上传样式读回失败")
    constraints = ui.get_upload_constraints(hwnd, upload_id)
    assert_state(constraints == {"limit": 2, "max_size_kb": 2, "accept": ".png"}, "上传限制读回失败")

    send_drop_files(hwnd, [png1], 50, 180)
    dropped = ui.get_upload_full_state(hwnd, upload_id)
    assert_state(dropped["file_count"] == 1 and any(event[0] == 12 for event in g_action_events), "系统拖入接收失败")

    ui.set_upload_selected_files(hwnd, upload_id, [png1, png2])
    selected = ui.get_upload_full_state(hwnd, upload_id)
    assert_state(selected["file_count"] == 2 and selected["waiting_count"] == 2, "多文件选择写入失败")
    assert_state(png1 in ui.get_upload_selected_files(hwnd, upload_id), "已选文件读回失败")

    ui.start_upload(hwnd, upload_id, -1)
    uploading = ui.get_upload_full_state(hwnd, upload_id)
    assert_state(uploading["uploading_count"] == 2, "手动开始上传失败")
    ui.dll.EU_SetUploadFileStatus(hwnd, upload_id, 0, 1, 100)
    ui.dll.EU_SetUploadFileStatus(hwnd, upload_id, 1, 3, 45)
    mixed = ui.get_upload_full_state(hwnd, upload_id)
    assert_state(mixed["success_count"] == 1 and mixed["failed_count"] == 1, "状态更新失败")

    ui.set_upload_preview_open(hwnd, upload_id, 0, True)
    preview = ui.get_upload_preview_state(hwnd, upload_id)
    assert_state(preview["open"] and preview["file_index"] == 0, "预览状态打开失败")
    send_escape(hwnd)
    assert_state(not ui.get_upload_preview_state(hwnd, upload_id)["open"], "ESC 关闭预览失败")
    ui.set_upload_preview_open(hwnd, upload_id, 0, True)
    close_x, close_y = preview_close_point(hwnd)
    send_left_click(hwnd, close_x, close_y)
    assert_state(not ui.get_upload_preview_state(hwnd, upload_id)["open"], "点击关闭按钮关闭预览失败")

    ui.set_upload_selected_files(hwnd, upload_id, [png1, png2, txt])
    assert_state(any(event[0] == 10 for event in g_action_events), "超出限制回调未触发")
    ui.set_upload_selected_files(hwnd, upload_id, [txt])
    assert_state(any(event[0] == 11 and event[2] == 1 for event in g_action_events), "类型过滤回调未触发")
    ui.set_upload_selected_files(hwnd, upload_id, [big])
    assert_state(any(event[0] == 11 and event[2] == 2 for event in g_action_events), "大小限制回调未触发")

    ui.set_upload_options(hwnd, upload_id, multiple=False, auto_upload=False)
    ui.set_upload_selected_files(hwnd, upload_id, [png1, png2])
    assert_state(any(event[0] == 10 for event in g_action_events), "单文件模式限制未触发")

    ui.set_upload_options(hwnd, upload_id, multiple=True, auto_upload=True)
    ui.set_upload_selected_files(hwnd, upload_id, [png1])
    auto_state = ui.get_upload_full_state(hwnd, upload_id)
    assert_state(auto_state["auto_upload"] and auto_state["uploading_count"] == 1, "自动上传状态失败")

    for mode in range(7):
        x = 32 + (mode % 4) * 245
        y = 430 + (mode // 4) * 112
        eid = ui.create_upload(hwnd, root, f"📤 样式 {mode}", "中文提示 + emoji", [png1], x, y, 220, 90)
        ui.set_upload_style(hwnd, eid, mode, True, True, True, mode == 5)
        readback = ui.get_upload_style(hwnd, eid)
        assert_state(readback["style_mode"] == mode, f"样式 {mode} 读回失败")

    pump_messages(0.2)
    print("✅ 上传组件样式、限制、预览和状态 API 验证通过")
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
