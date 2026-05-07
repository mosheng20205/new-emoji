import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_window("地址栏验证 🔍", 220, 120, 760, 360)
    assert_state(hwnd, "窗口创建失败")
    root = ui.create_container(hwnd, 0, 0, 0, 720, 300)
    omnibox = ui.create_omnibox(hwnd, root, "https://example.test", "搜索或输入网址 🔍", 24, 24, 620, 38)
    assert_state(omnibox > 0, "Omnibox 创建失败")

    ui.set_omnibox_value(hwnd, omnibox, "new_emoji Chrome 外壳")
    ui.set_omnibox_placeholder(hwnd, omnibox, "搜索或输入网址 🔍")
    ui.set_omnibox_security_state(hwnd, omnibox, 5, "搜索")
    ui.set_omnibox_prefix_chip(hwnd, omnibox, "🔍", "搜索")
    ui.set_omnibox_action_icons(hwnd, omnibox, [("☆", "收藏"), ("↗", "分享")])
    ui.set_omnibox_suggestion_items(hwnd, omnibox)
    ui.set_omnibox_suggestion_open(hwnd, omnibox, True)
    ui.set_omnibox_suggestion_selected(hwnd, omnibox, 1)

    assert_state(ui.get_omnibox_value(hwnd, omnibox) == "new_emoji Chrome 外壳", "Omnibox 值读回失败")
    state = ui.get_omnibox_suggestion_state(hwnd, omnibox)
    assert_state(state and state["open"] and state["selected"] == 1 and state["count"] >= 2, "Omnibox 建议状态读回失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("Omnibox 组件验证通过")


if __name__ == "__main__":
    main()
