import os
import sys
import struct
import tempfile
import ctypes
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


user32 = ctypes.WinDLL("user32", use_last_error=True)
dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)
dwmapi.DwmGetWindowAttribute.argtypes = [wintypes.HWND, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32]
dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long
if hasattr(user32, "GetWindowLongPtrW"):
    get_window_long = user32.GetWindowLongPtrW
else:
    get_window_long = user32.GetWindowLongW
get_window_long.argtypes = [wintypes.HWND, ctypes.c_int]
get_window_long.restype = ctypes.c_size_t


def dwm_corner_preference(hwnd):
    value = ctypes.c_uint32()
    hr = dwmapi.DwmGetWindowAttribute(hwnd, 33, ctypes.byref(value), ctypes.sizeof(value))
    if hr != 0:
        return None
    return value.value


def window_is_layered(hwnd):
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    return bool(get_window_long(hwnd, GWL_EXSTYLE) & WS_EX_LAYERED)


def window_has_rounding(hwnd):
    preference = dwm_corner_preference(hwnd)
    return preference in (2, 3) or window_is_layered(hwnd)


def make_test_ico_bytes():
    width = 16
    height = 16
    pixels = bytearray()
    for _y in range(height):
        for _x in range(width):
            pixels.extend((0x3A, 0xA8, 0xFF, 0xFF))  # BGRA
    and_mask = bytes(4 * height)
    bitmap_info = struct.pack(
        "<IiiHHIIiiII",
        40, width, height * 2, 1, 32, 0, len(pixels), 0, 0, 0, 0
    )
    image = bitmap_info + bytes(pixels) + and_mask
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, len(image), len(header) + 16)
    return header + entry + image


def main():
    hwnd = ui.create_window_ex("窗口框架验证 🪟", 220, 120, 640, 360)
    assert_state(hwnd, "扩展窗口创建失败")
    assert_state(ui.get_window_frame_flags(hwnd) == ui.EU_WINDOW_FRAME_DEFAULT, "默认 frame flags 读回失败")

    icon_bytes = make_test_ico_bytes()
    assert_state(ui.set_window_icon_from_bytes(hwnd, icon_bytes), "窗口图标字节集设置失败")
    icon_path = Path(tempfile.gettempdir()) / "new_emoji_window_icon_test.ico"
    icon_path.write_bytes(icon_bytes)
    try:
        assert_state(ui.set_window_icon(hwnd, icon_path), "窗口图标路径设置失败")
    finally:
        try:
            icon_path.unlink()
        except OSError:
            pass

    flags = ui.EU_WINDOW_FRAME_BORDERLESS | ui.EU_WINDOW_FRAME_RESIZABLE | ui.EU_WINDOW_FRAME_HIDE_TITLEBAR
    ui.set_window_frame_flags(hwnd, flags)
    assert_state(ui.get_window_frame_flags(hwnd) == flags, "frame flags 设置读回失败")

    ui.set_window_rounded_corners(hwnd, True, 18)
    assert_state(window_has_rounding(hwnd), "窗口圆角未设置真实 Windows 圆角")
    ui.set_window_rounded_corners(hwnd, False, 0)
    assert_state(not window_has_rounding(hwnd), "关闭窗口圆角后未清除 Windows 圆角")

    rounded_flags = flags | ui.EU_WINDOW_FRAME_ROUNDED
    ui.set_window_frame_flags(hwnd, rounded_flags)
    assert_state(ui.get_window_frame_flags(hwnd) == rounded_flags, "圆角 frame flags 设置读回失败")
    assert_state(window_has_rounding(hwnd), "EU_WINDOW_FRAME_ROUNDED 未应用真实 Windows 圆角")

    ui.set_window_resize_border(hwnd, 8, 9, 10, 11)
    assert_state(ui.get_window_resize_border(hwnd) == (8, 9, 10, 11), "resize border 读回失败")

    root = ui.create_container(hwnd, 0, 0, 0, 600, 280)
    btn = ui.create_icon_button(hwnd, root, "−", "最小化", 12, 12, 34, 34)
    ui.set_element_window_command(hwnd, btn, ui.EU_WINDOW_COMMAND_MINIMIZE)
    assert_state(ui.get_element_window_command(hwnd, btn) == ui.EU_WINDOW_COMMAND_MINIMIZE, "元素窗口命令读回失败")

    ui.set_window_drag_region(hwnd, 0, 0, 200, 40, True)
    ui.set_window_no_drag_region(hwnd, 12, 12, 34, 34, True)
    ui.clear_window_no_drag_regions(hwnd)
    ui.clear_window_drag_regions(hwnd)

    ui.dll.EU_DestroyWindow(hwnd)
    print("Window Frame 组件验证通过")


if __name__ == "__main__":
    main()
