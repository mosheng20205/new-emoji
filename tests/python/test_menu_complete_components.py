import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_menu_id = 0
g_collapsed_id = 0
g_status_id = 0
g_fold_id = 0
g_path_id = 0
g_horizontal_id = 0
g_select_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 菜单完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.MenuSelectCallback
def on_menu_select(element_id, item_index, path_ptr, path_len, command_ptr, command_len):
    path = bytes(path_ptr[:path_len]).decode("utf-8", errors="replace") if path_len > 0 else ""
    command = bytes(command_ptr[:command_len]).decode("utf-8", errors="replace") if command_len > 0 else ""
    g_select_events.append((element_id, item_index, path, command))
    print(f"[菜单选择] id={element_id} index={item_index} path={path} command={command}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_fold_id:
        ui.set_menu_expanded(g_hwnd, g_menu_id, [0, 4])
        print(f"[折叠] 状态={ui.get_menu_state(g_hwnd, g_menu_id)} 路径={ui.get_menu_active_path(g_hwnd, g_menu_id)}")
    elif element_id == g_path_id:
        ui.set_menu_expanded(g_hwnd, g_menu_id, [0, 1, 4])
        ui.set_menu_active(g_hwnd, g_menu_id, 3)
        print(f"[路径] 状态={ui.get_menu_state(g_hwnd, g_menu_id)} 路径={ui.get_menu_active_path(g_hwnd, g_menu_id)}")
    elif element_id == g_horizontal_id:
        collapsed = not ui.get_menu_collapsed(g_hwnd, g_collapsed_id)
        ui.set_menu_collapsed(g_hwnd, g_collapsed_id, collapsed)
        ui.set_element_text(g_hwnd, g_status_id, f"🧭 侧栏状态：{'已收起' if collapsed else '已展开'}")
        print(f"[收起] {ui.get_menu_collapsed(g_hwnd, g_collapsed_id)} 状态={ui.get_menu_state(g_hwnd, g_collapsed_id)}")


def apply_menu_meta(hwnd, menu_id, items, groups=None, href_index=None):
    icons = [""] * len(items)
    hrefs = [""] * len(items)
    targets = [""] * len(items)
    commands = [""] * len(items)
    for i, text in enumerate(items):
        if "首页" in text or "工作台" in text:
            icons[i] = "🏠"
        elif "项目" in text:
            icons[i] = "📦"
        elif "组件" in text:
            icons[i] = "🧩"
        elif "消息" in text:
            icons[i] = "💬"
        elif "订单" in text:
            icons[i] = "🧾"
        elif "设置" in text:
            icons[i] = "⚙️"
        commands[i] = f"menu_{i}"
    if href_index is not None:
        hrefs[href_index] = "https://www.ele.me"
        targets[href_index] = "_blank"
        commands[href_index] = "open_orders"
    ui.set_menu_item_meta(hwnd, menu_id, icons, groups or [], hrefs, targets, commands)


def main():
    global g_hwnd, g_menu_id, g_collapsed_id, g_status_id, g_fold_id, g_path_id, g_horizontal_id

    hwnd = ui.create_window("🧭 菜单完整组件", 220, 80, 1180, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1140, 700)

    ui.create_text(hwnd, content_id, "🧭 NavMenu 导航菜单完整验证", 28, 24, 520, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证横向默认、横向暗色、纵向默认、纵向暗色、多级子菜单、分组、禁用项、链接元数据、收起侧栏、颜色与状态读回。",
        28, 70, 920, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    horizontal_items = ["处理中心", "我的工作台", "> 选项1", "> 选项2", "> 选项3", "!消息中心", "订单管理"]
    horizontal = ui.create_menu(hwnd, content_id, horizontal_items, 0, 0, 32, 132, 520, 48)
    apply_menu_meta(hwnd, horizontal, horizontal_items, href_index=6)

    dark_horizontal = ui.create_menu(hwnd, content_id, horizontal_items, 0, 0, 580, 132, 520, 48)
    ui.set_menu_colors(hwnd, dark_horizontal, 0xFF545C64, 0xFFFFFFFF, 0xFFFFD04B, 0xFF646E78, 0xFF9CA3AF, 0xFF545C64)
    apply_menu_meta(hwnd, dark_horizontal, horizontal_items, href_index=6)

    vertical_items = [
        "导航一",
        "> 分组一",
        "> > 选项1",
        "> > 选项2",
        "> 分组二",
        "> > 选项3",
        "> 选项4",
        "> > 选项1",
        "导航二",
        "!导航三",
        "导航四",
    ]
    g_menu_id = ui.create_menu(hwnd, content_id, vertical_items, 2, 1, 32, 224, 260, 376)
    apply_menu_meta(hwnd, g_menu_id, vertical_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, g_menu_id, [0, 6])
    ui.set_menu_active(hwnd, g_menu_id, 2)
    ui.set_menu_select_callback(hwnd, g_menu_id, on_menu_select)

    dark_vertical = ui.create_menu(hwnd, content_id, vertical_items, 8, 1, 320, 224, 260, 376)
    ui.set_menu_colors(hwnd, dark_vertical, 0xFF545C64, 0xFFFFFFFF, 0xFFFFD04B, 0xFF646E78, 0xFF9CA3AF, 0xFF545C64)
    apply_menu_meta(hwnd, dark_vertical, vertical_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, dark_vertical, [0, 6])
    ui.set_menu_active(hwnd, dark_vertical, 8)

    g_collapsed_id = ui.create_menu(hwnd, content_id, vertical_items, 8, 1, 612, 224, 72, 376)
    apply_menu_meta(hwnd, g_collapsed_id, vertical_items, groups=[1, 4])
    ui.set_menu_expanded(hwnd, g_collapsed_id, [0, 6])
    ui.set_menu_active(hwnd, g_collapsed_id, 8)
    ui.set_menu_collapsed(hwnd, g_collapsed_id, True)

    g_status_id = ui.create_text(hwnd, content_id, "🧭 侧栏状态：已收起", 712, 230, 360, 28)
    g_fold_id = ui.create_button(hwnd, content_id, "📁", "折叠子菜单", 712, 278, 160, 42)
    g_path_id = ui.create_button(hwnd, content_id, "🧭", "读取路径", 890, 278, 150, 42)
    g_horizontal_id = ui.create_button(hwnd, content_id, "↔", "切换收起", 712, 338, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_fold_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_path_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_horizontal_id, on_click)

    colors = ui.get_menu_colors(hwnd, dark_horizontal)
    if colors != (0xFF545C64, 0xFFFFFFFF, 0xFFFFD04B, 0xFF646E78, 0xFF9CA3AF, 0xFF545C64):
        raise RuntimeError("菜单颜色读回失败")
    if not ui.get_menu_collapsed(hwnd, g_collapsed_id):
        raise RuntimeError("菜单收起状态读回失败")

    meta_group = ui.get_menu_item_meta(hwnd, g_menu_id, 1)
    meta_link = ui.get_menu_item_meta(hwnd, horizontal, 6)
    state = ui.get_menu_state(hwnd, g_menu_id)
    path = ui.get_menu_active_path(hwnd, g_menu_id)
    if not state or state["count"] != len(vertical_items) or state["level"] != 2:
        raise RuntimeError("菜单完整状态读回失败")
    if not meta_group or not meta_group["group"] or not meta_group["disabled"]:
        raise RuntimeError("菜单分组元数据读回失败")
    if not meta_link or meta_link["href"] != "https://www.ele.me" or meta_link["target"] != "_blank":
        raise RuntimeError("菜单链接元数据读回失败")
    if "选项1" not in path:
        raise RuntimeError("菜单激活路径读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("菜单完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_fold = False
    auto_path = False
    auto_toggle = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_fold and elapsed > 1.0:
            on_click(g_fold_id)
            auto_fold = True
        if not auto_path and elapsed > 2.0:
            on_click(g_path_id)
            auto_path = True
        if not auto_toggle and elapsed > 3.0:
            on_click(g_horizontal_id)
            auto_toggle = True
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                running = False
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)

    print("菜单完整组件示例结束。")


if __name__ == "__main__":
    main()
