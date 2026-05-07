import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_window_ex("窗口框架验证 🪟", 220, 120, 640, 360)
    assert_state(hwnd, "扩展窗口创建失败")
    assert_state(ui.get_window_frame_flags(hwnd) == ui.EU_WINDOW_FRAME_DEFAULT, "默认 frame flags 读回失败")

    flags = ui.EU_WINDOW_FRAME_BORDERLESS | ui.EU_WINDOW_FRAME_RESIZABLE | ui.EU_WINDOW_FRAME_HIDE_TITLEBAR
    ui.set_window_frame_flags(hwnd, flags)
    assert_state(ui.get_window_frame_flags(hwnd) == flags, "frame flags 设置读回失败")

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
