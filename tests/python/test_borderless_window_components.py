import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_borderless_window("无标题栏窗口 🪟", 240, 140, 640, 360)
    assert_state(hwnd, "无标题栏窗口创建失败")
    flags = ui.get_window_frame_flags(hwnd)
    assert_state(flags & ui.EU_WINDOW_FRAME_BORDERLESS, "缺少 BORDERLESS 标记")
    assert_state(flags & ui.EU_WINDOW_FRAME_HIDE_TITLEBAR, "缺少 HIDE_TITLEBAR 标记")

    root = ui.create_container(hwnd, 0, 0, 0, 620, 320)
    ui.create_text(hwnd, root, "首个元素应从 y=0 显示 🌐", 0, 0, 320, 32)
    x, y, w, h = ui.get_element_bounds(hwnd, root)
    assert_state(y == 0, f"无标题栏根容器未从 y=0 开始：{y}")

    ui.dll.EU_DestroyWindow(hwnd)
    print("Borderless Window 组件验证通过")


if __name__ == "__main__":
    main()
