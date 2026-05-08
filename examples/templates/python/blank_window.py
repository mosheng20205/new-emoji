import ctypes
from ctypes import wintypes
import sys

sys.path.insert(0, "examples/python")
import new_emoji_ui as ui


def main():
    hwnd = ui.create_window("✨ Python 空白窗口", 240, 120, 860, 560)
    root = ui.create_container(hwnd, 0, 0, 0, 820, 500)

    ui.create_text(hwnd, root, "欢迎使用 new_emoji 🚀", 32, 32, 460, 40)
    ui.create_button(hwnd, root, "✅", "确认操作", 32, 96, 160, 42)

    ui.dll.EU_ShowWindow(hwnd, 1)

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


if __name__ == "__main__":
    main()
