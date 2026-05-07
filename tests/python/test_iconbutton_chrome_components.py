import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_window("图标按钮验证 🧩", 220, 120, 520, 320)
    assert_state(hwnd, "窗口创建失败")
    root = ui.create_container(hwnd, 0, 0, 0, 500, 260)
    btn = ui.create_icon_button(hwnd, root, "📥", "下载", 24, 24, 40, 40)
    assert_state(btn > 0, "IconButton 创建失败")

    ui.set_icon_button_colors(hwnd, btn, normal_bg=0x00000000, hover_bg=0x18000000)
    ui.set_icon_button_shape(hwnd, btn, 1, 20)
    ui.set_icon_button_icon_size(hwnd, btn, 20)
    ui.set_icon_button_padding(hwnd, btn, 6, 6, 6, 6)
    ui.set_icon_button_badge(hwnd, btn, "2", True)
    ui.set_icon_button_checked(hwnd, btn, True)
    assert_state(ui.get_icon_button_checked(hwnd, btn), "checked 状态读回失败")
    state = ui.get_icon_button_state(hwnd, btn)
    assert_state(state and state["checked"] and state["badge_visible"], "IconButton 状态读回失败")

    menu = ui.create_menu(hwnd, root, ["下载内容", "全部显示"], 0, 1, -900, 0, 220, 100)
    ui.set_icon_button_dropdown(hwnd, btn, menu)
    assert_state(ui.get_element_popup(hwnd, btn, "click") == menu, "IconButton Dropdown 兼容绑定失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("IconButton Chrome 组件验证通过")


if __name__ == "__main__":
    main()
