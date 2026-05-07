import os
import sys

EXAMPLES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python"))
if EXAMPLES not in sys.path:
    sys.path.insert(0, EXAMPLES)

import new_emoji_ui as ui


def main():
    hwnd = ui.create_window("Popup 通用能力测试 🫧", 260, 160, 720, 420)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    root = ui.create_container(hwnd, 0, 0, 0, 680, 340)
    button = ui.create_icon_button(hwnd, root, "⇩", "下载", 40, 36, 34, 34)
    popover = ui.create_popover(
        hwnd, root, "", "下载 📥", "最近下载\n📦 new_emoji.dll", 3,
        -900, 0, 1, 1,
    )
    menu = ui.create_menu(
        hwnd, root, ["新标签页", "下载内容", "设置"],
        active=0, orientation=1, x=120, y=80, w=220, h=150,
    )
    dropdown = ui.create_dropdown(hwnd, root, "📂 更多操作", ["复制", "导出", "删除"], 0, -900, 0, 180, 36)
    ui.set_dropdown_options(hwnd, dropdown, trigger_mode=2)

    ui.set_popup_anchor_element(hwnd, popover, button)
    ui.set_popup_placement(hwnd, popover, 5, 0, 6)
    ui.set_popup_dismiss_behavior(hwnd, popover, True, True)
    ui.set_popup_open(hwnd, popover, True)
    if not ui.get_popup_open(hwnd, popover):
        raise RuntimeError("Popover 通用 Popup 打开读回失败")
    ui.set_popup_open(hwnd, popover, False)
    if ui.get_popup_open(hwnd, popover):
        raise RuntimeError("Popover 通用 Popup 关闭读回失败")

    ui.set_popup_anchor_element(hwnd, menu, button)
    ui.set_popup_placement(hwnd, menu, 5, 0, 6)
    ui.set_popup_dismiss_behavior(hwnd, menu, True, True)
    ui.set_popup_open(hwnd, menu, True)
    if not ui.get_popup_open(hwnd, menu):
        raise RuntimeError("Menu 通用 Popup 打开读回失败")
    ui.set_icon_button_dropdown(hwnd, button, menu)
    ui.set_popup_open(hwnd, menu, False)
    if ui.get_popup_open(hwnd, menu):
        raise RuntimeError("Menu 通用 Popup 关闭读回失败")

    ui.set_popup_anchor_element(hwnd, dropdown, button)
    ui.set_popup_placement(hwnd, dropdown, 5, 0, 6)
    ui.set_popup_dismiss_behavior(hwnd, dropdown, True, True)
    ui.set_popup_open(hwnd, dropdown, True)
    if not ui.get_popup_open(hwnd, dropdown):
        raise RuntimeError("Dropdown 通用 Popup 打开读回失败")
    ui.set_popup_open(hwnd, dropdown, False)
    if ui.get_popup_open(hwnd, dropdown):
        raise RuntimeError("Dropdown 通用 Popup 关闭读回失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("Popup 通用组件测试通过")


if __name__ == "__main__":
    main()
