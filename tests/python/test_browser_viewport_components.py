import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_window("浏览区验证 🌐", 220, 120, 760, 460)
    assert_state(hwnd, "窗口创建失败")
    root = ui.create_container(hwnd, 0, 0, 0, 720, 400)
    viewport = ui.create_browser_viewport(hwnd, root, 24, 24, 660, 320)
    assert_state(viewport > 0, "BrowserViewport 创建失败")

    ui.set_browser_viewport_placeholder(hwnd, viewport, "新标签页 🌐", "内容区占位", "🌐")
    ui.set_browser_viewport_state(hwnd, viewport, 4)
    ui.set_browser_viewport_loading(hwnd, viewport, True, 42)
    state = ui.get_browser_viewport_state(hwnd, viewport)
    assert_state(state and state["state"] == 1 and state["loading"] and state["progress"] == 42, "加载状态读回失败")

    ui.set_browser_viewport_loading(hwnd, viewport, False, 100)
    state = ui.get_browser_viewport_state(hwnd, viewport)
    assert_state(state and not state["loading"] and state["progress"] == 100, "完成状态读回失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("BrowserViewport 组件验证通过")


if __name__ == "__main__":
    main()
