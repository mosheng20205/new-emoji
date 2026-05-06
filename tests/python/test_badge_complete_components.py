import ctypes
from ctypes import wintypes
import os
import time

import test_new_emoji as ui


WINDOW_W = 1120
WINDOW_H = 700
CONTENT_W = 1090
CONTENT_H = 650

g_hwnd = None
g_base_id = 0
g_max_id = 0
g_dot_id = 0
g_type_id = 0
g_custom_id = 0
g_apply_id = 0
g_reset_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[close] Badge window closing")
    ui.dll.EU_DestroyWindow(hwnd)


def dump_state(prefix):
    print(
        f"{prefix} "
        f"base={ui.get_badge_options(g_hwnd, g_base_id)} "
        f"base_layout={ui.get_badge_layout_options(g_hwnd, g_base_id)} "
        f"base_type={ui.get_badge_type(g_hwnd, g_base_id)} "
        f"max={ui.get_badge_options(g_hwnd, g_max_id)} "
        f"max_type={ui.get_badge_type(g_hwnd, g_max_id)} "
        f"dot={ui.get_badge_options(g_hwnd, g_dot_id)} "
        f"dot_type={ui.get_badge_type(g_hwnd, g_dot_id)} "
        f"type={ui.get_badge_options(g_hwnd, g_type_id)} "
        f"type_kind={ui.get_badge_type(g_hwnd, g_type_id)} "
        f"custom={ui.get_badge_options(g_hwnd, g_custom_id)} "
        f"custom_type={ui.get_badge_type(g_hwnd, g_custom_id)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_badge_value(g_hwnd, g_base_id, "18")
        ui.set_badge_options(g_hwnd, g_base_id, dot=False, show_zero=True, offset_x=0, offset_y=0)
        ui.set_badge_layout_options(g_hwnd, g_base_id, placement=0, standalone=False)
        ui.set_badge_max(g_hwnd, g_max_id, 99)
        ui.set_badge_value(g_hwnd, g_max_id, "200")
        ui.set_badge_type(g_hwnd, g_max_id, 1)
        ui.set_badge_dot(g_hwnd, g_dot_id, True)
        ui.set_badge_type(g_hwnd, g_dot_id, 3)
        ui.set_badge_type(g_hwnd, g_type_id, 2)
        ui.set_badge_value(g_hwnd, g_type_id, "new")
        ui.set_badge_type(g_hwnd, g_custom_id, 4)
        ui.dll.EU_SetElementColor(g_hwnd, g_custom_id, 0xFFEFF6FF, 0xFF1D4ED8)
        dump_state("[apply]")
    elif element_id == g_reset_id:
        ui.set_badge_value(g_hwnd, g_base_id, "12")
        ui.set_badge_max(g_hwnd, g_max_id, 99)
        ui.set_badge_value(g_hwnd, g_max_id, "200")
        ui.set_badge_type(g_hwnd, g_max_id, 0)
        ui.set_badge_dot(g_hwnd, g_dot_id, False)
        ui.set_badge_type(g_hwnd, g_type_id, 1)
        ui.set_badge_value(g_hwnd, g_type_id, "hot")
        ui.set_badge_type(g_hwnd, g_custom_id, 0)
        ui.dll.EU_SetElementColor(g_hwnd, g_custom_id, 0, 0)
        dump_state("[reset]")


def main():
    global g_hwnd, g_base_id, g_max_id, g_dot_id, g_type_id, g_custom_id, g_apply_id, g_reset_id

    hwnd = ui.create_window("\U0001F502 Badge \u5b8c\u6574\u6837\u5f0f\u6d4b\u8bd5", 200, 120, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("\u9519\u8bef\uff1a\u7a97\u53e3\u521b\u5efa\u5931\u8d25")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "\U0001F502 Badge \u5b8c\u6574\u6837\u5f0f\u6d4b\u8bd5", 28, 18, 360, 34)
    ui.create_divider(hwnd, content_id, "\u6570\u503c / \u6700\u5927\u503c / \u6587\u672c / dot / \u4f4d\u7f6e / \u7c7b\u578b / \u81ea\u5b9a\u4e49\u8272", 0, 1, 28, 56, 960, 30)

    base_panel = ui.create_panel(hwnd, content_id, 28, 100, 1060, 154)
    ui.set_panel_style(hwnd, base_panel, 0xFF23283E, 0xFF3D4668, 1.0, 8.0, 10)
    g_base_id = ui.create_badge(hwnd, base_panel, "\u6d88\u606f\u4e2d\u5fc3", "12", 99, False, 28, 58, 210, 38, badge_type=1)
    g_max_id = ui.create_badge(hwnd, base_panel, "\u8ba2\u5355\u4e2d\u5fc3", "200", 99, False, 266, 58, 210, 38, badge_type=3)
    g_dot_id = ui.create_badge(hwnd, base_panel, "\u6570\u636e\u67e5\u8be2", "", 99, True, 504, 58, 210, 38, badge_type=2)
    g_type_id = ui.create_badge(hwnd, base_panel, "\u72b6\u6001\u63d0\u9192", "hot", 99, False, 742, 58, 210, 38, badge_type=4)
    g_custom_id = ui.create_badge(hwnd, base_panel, "\u81ea\u5b9a\u4e49\u8272", "42", 99, False, 28, 108, 210, 38)
    ui.dll.EU_SetElementColor(hwnd, g_custom_id, 0xFFEDE9FE, 0xFF7C3AED)
    ui.create_badge(hwnd, base_panel, "", "1", 99, False, 266, 108, 54, 28, placement=0, standalone=True, badge_type=0)
    ui.create_badge(hwnd, base_panel, "", "2", 99, False, 330, 108, 54, 28, placement=1, standalone=True, badge_type=1)
    ui.create_badge(hwnd, base_panel, "", "3", 99, False, 394, 108, 54, 28, placement=2, standalone=True, badge_type=2)
    ui.create_badge(hwnd, base_panel, "", "4", 99, False, 458, 108, 54, 28, placement=3, standalone=True, badge_type=3)
    ui.create_badge(hwnd, base_panel, "\u6700\u5927 99", "200", 99, False, 542, 108, 210, 38, badge_type=3)
    ui.create_badge(hwnd, base_panel, "new / hot", "new", 99, False, 782, 108, 120, 38, badge_type=2)

    g_apply_id = ui.create_button(hwnd, content_id, "\u2705", "\u5e94\u7528\u72b6\u6001", 728, 584, 150, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "\U0001F504", "\u6062\u590d\u9ed8\u8ba4", 896, 584, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "\U0001F50D \u89c2\u5bdf\u70b9",
        "\u68c0\u67e5\u6570\u5b57\u622a\u65ad\u3001dot \u663e\u793a\u3001\u89d2\u6807\u56db\u65b9\u4f4d\u3001\u8bed\u4e49\u8272\u4e0e\u81ea\u5b9a\u4e49\u8272\u662f\u5426\u90fd\u80fd\u6b63\u5e38\u6e32\u67d3\u3002",
        28, 586, 660, 72
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    dump_state("[initial]")

    duration = int(os.environ.get("EU_TEST_SECONDS", "30"))
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
    print("Badge complete style test finished")


if __name__ == "__main__":
    main()
