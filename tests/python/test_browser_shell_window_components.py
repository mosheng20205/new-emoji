import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_browser_shell_window("浏览器式外壳 🌐", 260, 160, 760, 420)
    assert_state(hwnd, "浏览器式外壳窗口创建失败")
    flags = ui.get_window_frame_flags(hwnd)
    assert_state(flags == ui.EU_WINDOW_FRAME_BROWSER_SHELL, "浏览器式 frame flags 读回失败")

    root = ui.create_container(hwnd, 0, 0, 0, 740, 380)
    tabs = ui.create_tabs(hwnd, root, ["新标签页", "文档"], 0, 0, 8, 0, 420, 36)
    ui.set_tabs_chrome_mode(hwnd, tabs, True)
    assert_state(ui.get_tabs_chrome_mode(hwnd, tabs), "Tabs Chrome 模式读回失败")

    close_btn = ui.create_icon_button(hwnd, root, "×", "关闭", 700, 0, 46, 32)
    ui.set_element_window_command(hwnd, close_btn, ui.EU_WINDOW_COMMAND_CLOSE)
    assert_state(ui.get_element_window_command(hwnd, close_btn) == ui.EU_WINDOW_COMMAND_CLOSE, "关闭按钮命令读回失败")
    more_btn = ui.create_icon_button(hwnd, root, "⋮", "更多", 650, 40, 34, 34)
    more_menu = ui.create_menu(hwnd, root, ["新标签页", "设置"], 0, 1, -900, 0, 220, 100)
    ui.set_icon_button_dropdown(hwnd, more_btn, more_menu)
    assert_state(ui.get_element_popup(hwnd, more_btn, "click") == more_menu, "工具按钮左键弹层绑定失败")

    context_menu = ui.create_menu(hwnd, root, ["新建标签页", "关闭标签页"], 0, 1, -900, 0, 220, 100)
    ui.set_element_popup(hwnd, tabs, context_menu, "right_click")
    assert_state(ui.get_element_popup(hwnd, tabs, "right_click") == context_menu, "标签栏右键菜单绑定失败")

    ui.set_window_drag_region(hwnd, 0, 0, 650, 36, True)
    ui.set_window_no_drag_region(hwnd, 8, 0, 420, 36, True)
    ui.set_window_resize_border(hwnd, 6, 6, 6, 6)
    assert_state(ui.get_window_resize_border(hwnd) == (6, 6, 6, 6), "浏览器式 resize border 读回失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("Browser Shell Window 组件验证通过")


if __name__ == "__main__":
    main()
