import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_window("组件弹层绑定测试 🖱️", 260, 160, 760, 460)
    assert_state(hwnd, "窗口创建失败")
    root = ui.create_container(hwnd, 0, 0, 0, 740, 400)

    panel = ui.create_panel(hwnd, root, 30, 60, 180, 76)
    button = ui.create_button(hwnd, root, "🚀", "普通按钮", 250, 70, 140, 38)
    omnibox = ui.create_omnibox(hwnd, root, "", "右键地址栏 🔍", 30, 170, 340, 38)

    menu_a = ui.create_menu(hwnd, root, ["复制", "粘贴", "全选"], 0, 1, -900, 0, 220, 138)
    menu_b = ui.create_menu(hwnd, root, ["按钮动作", "检查属性"], 0, 1, -900, 0, 220, 100)
    menu_c = ui.create_menu(hwnd, root, ["复制网址", "编辑搜索引擎"], 0, 1, -900, 0, 230, 100)
    popover_click = ui.create_popover(hwnd, root, "", "左键气泡 🗯️", "左键打开", 3, -900, 0, 1, 1)
    popover_hover = ui.create_popover(hwnd, root, "", "悬停气泡 🖱️", "悬停打开", 3, -900, 0, 1, 1)
    dropdown = ui.create_dropdown(hwnd, root, "📂 操作", ["打开", "重命名", "删除"], 0, -900, 0, 180, 36)
    ui.set_dropdown_options(hwnd, dropdown, trigger_mode=2)

    ui.set_popup_placement(hwnd, menu_a, 5, 0, 6)
    ui.set_popup_dismiss_behavior(hwnd, menu_a, True, True)
    ui.set_element_popup(hwnd, panel, menu_a, "right_click")
    assert_state(ui.get_element_popup(hwnd, panel, "right_click") == menu_a, "Panel 右键 Menu 绑定读回失败")

    ui.set_popup_placement(hwnd, popover_click, 5, 0, 6)
    ui.set_popup_dismiss_behavior(hwnd, popover_click, True, True)
    ui.set_element_popup(hwnd, button, popover_click, "click")
    assert_state(ui.get_element_popup(hwnd, button, "click") == popover_click, "Button 左键 Popover 绑定读回失败")

    ui.set_popup_placement(hwnd, popover_hover, 5, 0, 6)
    ui.set_popup_dismiss_behavior(hwnd, popover_hover, True, True)
    ui.set_element_popup(hwnd, button, popover_hover, "hover")
    assert_state(ui.get_element_popup(hwnd, button, "hover") == popover_hover, "Button hover Popover 绑定读回失败")

    ui.set_element_popup(hwnd, omnibox, menu_c, "right_click")
    assert_state(ui.get_element_popup(hwnd, omnibox, "right_click") == menu_c, "Omnibox 右键 Menu 绑定读回失败")

    ui.set_popup_anchor_element(hwnd, dropdown, panel)
    ui.set_popup_placement(hwnd, dropdown, 5, 0, 6)
    ui.set_popup_dismiss_behavior(hwnd, dropdown, True, True)
    ui.set_element_popup(hwnd, panel, dropdown, "manual")
    assert_state(ui.get_element_popup(hwnd, panel, "manual") == dropdown, "Dropdown manual 绑定读回失败")

    ui.set_element_popup(hwnd, panel, dropdown, "right_click")
    assert_state(ui.get_element_popup(hwnd, panel, "right_click") == dropdown, "同 trigger 覆盖绑定失败")
    ui.clear_element_popup(hwnd, panel, "right_click")
    assert_state(ui.get_element_popup(hwnd, panel, "right_click") == 0, "清除绑定失败")

    ui.set_element_popup(hwnd, panel, menu_a, "right_click")
    ui.set_element_popup(hwnd, button, menu_b, "right_click")
    assert_state(ui.get_element_popup(hwnd, panel, "right_click") == menu_a, "Panel 重新绑定失败")
    assert_state(ui.get_element_popup(hwnd, button, "right_click") == menu_b, "Button 右键绑定失败")

    for popup in (menu_a, menu_b, menu_c, popover_click, popover_hover, dropdown):
        ui.set_popup_open(hwnd, popup, True)
        assert_state(ui.get_popup_open(hwnd, popup), f"Popup #{popup} 打开读回失败")
        ui.set_popup_open(hwnd, popup, False)
        assert_state(not ui.get_popup_open(hwnd, popup), f"Popup #{popup} 关闭读回失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("Element Popup 绑定组件测试通过")


if __name__ == "__main__":
    main()
