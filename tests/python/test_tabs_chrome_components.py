import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_window("Chrome 标签验证 🌐", 220, 120, 760, 360)
    assert_state(hwnd, "窗口创建失败")
    root = ui.create_container(hwnd, 0, 0, 0, 720, 300)
    tabs = ui.create_tabs(hwnd, root, ["新标签页 🌐", "文档 📚", "下载 📥"], 0, 0, 16, 16, 680, 42)
    assert_state(tabs > 0, "Tabs 创建失败")

    ui.set_tabs_chrome_mode(hwnd, tabs, True)
    ui.set_tabs_chrome_metrics(hwnd, tabs, 110, 220, 48, 36, 12)
    ui.set_tabs_new_button_visible(hwnd, tabs, True)
    ui.set_tabs_drag_options(hwnd, tabs, True, True)
    ui.set_tabs_item_icon(hwnd, tabs, 1, "📚")
    ui.set_tabs_item_chrome_state(hwnd, tabs, 1, loading=True, pinned=False, muted=True, alerting=True)
    ui.set_tabs_item_pinned(hwnd, tabs, 2, True)
    assert_state(ui.get_tabs_chrome_mode(hwnd, tabs), "Chrome 模式读回失败")
    state = ui.get_tabs_item_chrome_state(hwnd, tabs, 1)
    assert_state(state and state["loading"] and state["muted"] and state["alerting"], "Chrome 标签状态读回失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("Tabs Chrome 组件验证通过")


if __name__ == "__main__":
    main()
