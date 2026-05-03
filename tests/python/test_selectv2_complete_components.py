import ctypes
from ctypes import wintypes
import sys
import time

import test_new_emoji as ui


WINDOW_W = 940
WINDOW_H = 660
CONTENT_W = 920
CONTENT_H = 610
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120
MOUSEEVENTF_WHEEL = 0x0800
user32 = ctypes.windll.user32
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM
user32.GetDpiForWindow.argtypes = [wintypes.HWND]
user32.GetDpiForWindow.restype = wintypes.UINT

g_hwnd = None
g_select_id = 0
g_status_id = 0
g_apply_id = 0
g_reset_id = 0
g_change_callback = None
g_callback_events = []
g_failed = None


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] SelectV2 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_select_v2_change(element_id, current_index, matched_count, open_state):
    g_callback_events.append((element_id, current_index, matched_count, open_state))
    print(
        f"[增强选择器回调] 元素={element_id} 当前={current_index} "
        f"匹配={matched_count} 打开={open_state}"
    )


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


def make_lparam_from_screen(hwnd, client_x, client_y):
    pt = wintypes.POINT(client_x, client_y)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return ((pt.y & 0xFFFF) << 16) | (pt.x & 0xFFFF)


def send_wheel(hwnd, client_x, client_y, notches):
    delta = WHEEL_DELTA * notches
    pt = wintypes.POINT(client_x, client_y)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    user32.SetForegroundWindow(hwnd)
    user32.SetCursorPos(pt.x, pt.y)
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)


def pump_messages(duration=0.2):
    msg = wintypes.MSG()
    end = time.time() + duration
    while time.time() < end:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def logical_client(hwnd, x, y):
    scale = max(1.0, float(user32.GetDpiForWindow(hwnd)) / 96.0)
    return int(x * scale), int(y * scale)


def print_state(prefix):
    print(
        f"{prefix} 索引={ui.get_select_v2_index(g_hwnd, g_select_id)} "
        f"可见={ui.get_select_v2_visible_count(g_hwnd, g_select_id)} "
        f"滚动={ui.get_select_v2_scroll_index(g_hwnd, g_select_id)} "
        f"数量={ui.get_select_v2_option_count(g_hwnd, g_select_id)} "
        f"匹配={ui.get_select_v2_matched_count(g_hwnd, g_select_id)} "
        f"禁用10={ui.get_select_v2_option_disabled(g_hwnd, g_select_id, 10)} "
        f"打开={ui.get_select_v2_open(g_hwnd, g_select_id)} "
        f"回调次数={len(g_callback_events)}"
    )


@ui.ClickCallback
def on_click(element_id):
    global g_failed
    if element_id == g_apply_id:
        ui.set_select_v2_open(g_hwnd, g_select_id, True)
        ui.set_select_v2_visible_count(g_hwnd, g_select_id, 6)
        ui.set_select_v2_option_disabled(g_hwnd, g_select_id, 10, True)
        ui.set_select_v2_scroll_index(g_hwnd, g_select_id, 40)
        wheel_x, wheel_y = logical_client(g_hwnd, 231, 197)
        send_wheel(g_hwnd, wheel_x, wheel_y, -3)
        pump_messages(0.25)
        after_wheel = ui.get_select_v2_scroll_index(g_hwnd, g_select_id)
        if after_wheel <= 40:
            g_failed = f"滚轮滚动未生效：起点仍为 {after_wheel}，坐标=({wheel_x},{wheel_y})"
            print("[失败]", g_failed)
            return
        ui.set_select_v2_index(g_hwnd, g_select_id, 120)
        after_select = ui.get_select_v2_scroll_index(g_hwnd, g_select_id)
        ui.set_select_v2_search(g_hwnd, g_select_id, "城市 12")
        matched = ui.get_select_v2_matched_count(g_hwnd, g_select_id)
        update_status(f"✅ 滚轮后起点 {after_wheel}，选中 120 后起点 {after_select}，搜索匹配 {matched} 项。")
        print_state("[应用状态]")
        print(f"[滚轮验证] 设置起点 40，滚轮后 {after_wheel}，选中 120 后可视起点 {after_select}")
    elif element_id == g_reset_id:
        ui.set_select_v2_search(g_hwnd, g_select_id, "")
        ui.set_select_v2_open(g_hwnd, g_select_id, True)
        ui.set_select_v2_visible_count(g_hwnd, g_select_id, 7)
        ui.set_select_v2_option_disabled(g_hwnd, g_select_id, 10, False)
        ui.set_select_v2_scroll_index(g_hwnd, g_select_id, 0)
        ui.set_select_v2_index(g_hwnd, g_select_id, 3)
        update_status("↩ 已恢复增强选择器默认窗口和选中项。")
        print_state("[恢复状态]")


def main():
    global g_hwnd, g_select_id, g_status_id, g_apply_id, g_reset_id, g_change_callback

    hwnd = ui.create_window("🚀 SelectV2 完整封装验证", 220, 100, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_change_callback = on_select_v2_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    ui.create_text(hwnd, content_id, "🚀 增强选择器大列表能力", 28, 24, 420, 34)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证 200 项虚拟列表、滚轮派发、滚动索引读写、Page/Home/End 基础、搜索过滤、禁用项和变化回调。",
        28,
        68,
        840,
        52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    options = [f"城市 {i:03d} 🚇" for i in range(1, 201)]
    g_select_id = ui.create_select_v2(
        hwnd,
        content_id,
        "城市",
        options,
        3,
        7,
        36,
        146,
        390,
        42,
    )
    ui.set_select_v2_open(hwnd, g_select_id, True)
    ui.set_select_v2_option_disabled(hwnd, g_select_id, 10, True)
    ui.dll.EU_SetSelectV2ChangeCallback(hwnd, g_select_id, g_change_callback)

    panel_id = ui.create_panel(hwnd, content_id, 480, 146, 390, 224)
    ui.set_panel_style(hwnd, panel_id, 0x101E66F5, 0x661E66F5, 1.0, 12.0, 18)
    ui.create_text(hwnd, panel_id, "🔎 大列表状态", 0, 0, 220, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待自动滚动和搜索验证。", 0, 48, 320, 110)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "滚动并读取", 480, 400, 150, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "↩", "恢复默认", 650, 400, 140, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_alert(
        hwnd,
        content_id,
        "📐 首屏尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 870，最下内容约 442，首屏留出 20px 以上逻辑余量。",
        0,
        0,
        False,
        36,
        490,
        820,
        60,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("SelectV2 完整封装验证已显示。窗口会保持 60 秒。")
    print_state("[初始状态]")

    msg = wintypes.MSG()
    start = time.time()
    running = True
    auto_stage = 0
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if auto_stage == 0 and elapsed > 1.0:
            on_click(g_apply_id)
            auto_stage = 1
        elif auto_stage == 1 and elapsed > 3.0:
            on_click(g_reset_id)
            auto_stage = 2
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

    print("SelectV2 完整封装验证结束。")
    if g_failed:
        sys.exit(g_failed)


if __name__ == "__main__":
    main()
