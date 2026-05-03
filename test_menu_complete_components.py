import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_menu_id = 0
g_fold_id = 0
g_path_id = 0
g_horizontal_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 菜单完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


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
        ui.set_menu_orientation(g_hwnd, g_menu_id, 0)
        ui.set_menu_active(g_hwnd, g_menu_id, 5)
        print(f"[水平] 状态={ui.get_menu_state(g_hwnd, g_menu_id)} 路径={ui.get_menu_active_path(g_hwnd, g_menu_id)}")


def main():
    global g_hwnd, g_menu_id, g_fold_id, g_path_id, g_horizontal_id

    hwnd = ui.create_window("🧭 菜单完整组件", 220, 80, 980, 700)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 640)

    ui.create_text(hwnd, content_id, "🧭 菜单完整验证", 28, 24, 360, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证多级子菜单、展开/折叠、禁用项跳过、方向切换、键盘选择、激活路径和完整状态读回。",
        28, 70, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    items = [
        "🏠 工作台",
        "> 📦 项目管理",
        "> > 📋 项目列表",
        "> > 📈 项目统计",
        "🧩 组件中心",
        "> 🎛️ 表单组件",
        "> !🚫 已停用模块",
        "> 📊 数据展示",
        "⚙️ 系统设置",
        "> 🔐 权限配置",
    ]

    g_menu_id = ui.create_menu(hwnd, content_id, items, 2, 1, 48, 146, 360, 380)
    ui.set_menu_expanded(hwnd, g_menu_id, [0, 1, 4, 8])

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "菜单项使用 > 表示子级，! 表示禁用。1 秒后折叠部分子菜单，2 秒后恢复并读取路径，3 秒后切换为水平菜单。",
        450, 150, 410, 98,
    )

    g_fold_id = ui.create_button(hwnd, content_id, "📁", "折叠子菜单", 450, 296, 160, 42)
    g_path_id = ui.create_button(hwnd, content_id, "🧭", "读取路径", 632, 296, 150, 42)
    g_horizontal_id = ui.create_button(hwnd, content_id, "↔", "水平菜单", 450, 354, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_fold_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_path_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_horizontal_id, on_click)

    initial = ui.get_menu_state(hwnd, g_menu_id)
    path = ui.get_menu_active_path(hwnd, g_menu_id)
    print(f"[初始] 状态={initial} 路径={path}")
    if not initial or initial["count"] != len(items) or initial["level"] != 2:
        raise RuntimeError("菜单状态读回失败")
    if "项目列表" not in path:
        raise RuntimeError("菜单激活路径读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("菜单完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_fold = False
    auto_path = False
    auto_horizontal = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_fold and elapsed > 1.0:
            on_click(g_fold_id)
            auto_fold = True
        if not auto_path and elapsed > 2.0:
            on_click(g_path_id)
            auto_path = True
        if not auto_horizontal and elapsed > 3.0:
            on_click(g_horizontal_id)
            auto_horizontal = True
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
