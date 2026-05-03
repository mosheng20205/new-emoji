import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dropdown_id = 0
g_menu_id = 0
g_anchor_id = 0
g_segmented_id = 0
g_open_id = 0
g_update_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 导航状态组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_open_id:
        ui.set_dropdown_open(g_hwnd, g_dropdown_id, True)
        print(
            "[打开] "
            f"下拉={ui.get_dropdown_open(g_hwnd, g_dropdown_id)} "
            f"下拉项={ui.get_dropdown_item_count(g_hwnd, g_dropdown_id)}"
        )
    elif element_id == g_update_id:
        ui.set_dropdown_items(g_hwnd, g_dropdown_id, ["📄 详情", "✏️ 编辑", "🧹 清理", "📦 归档"])
        ui.set_dropdown_selected(g_hwnd, g_dropdown_id, 2)
        ui.set_dropdown_open(g_hwnd, g_dropdown_id, True)
        ui.set_menu_items(g_hwnd, g_menu_id, ["🏠 首页", "🧩 组件", "📚 文档", "⚙ 设置"])
        ui.set_menu_active(g_hwnd, g_menu_id, 3)
        ui.set_menu_orientation(g_hwnd, g_menu_id, 0)
        ui.set_anchor_items(g_hwnd, g_anchor_id, ["概览", "安装", "示例", "状态 API"])
        ui.set_anchor_active(g_hwnd, g_anchor_id, 3)
        ui.set_segmented_items(g_hwnd, g_segmented_id, ["今日", "本周", "本月", "全年"])
        ui.set_segmented_active(g_hwnd, g_segmented_id, 1)
        print(
            "[状态] "
            f"下拉选中={ui.get_dropdown_selected(g_hwnd, g_dropdown_id)} "
            f"下拉项={ui.get_dropdown_item_count(g_hwnd, g_dropdown_id)} "
            f"菜单激活={ui.get_menu_active(g_hwnd, g_menu_id)} "
            f"菜单方向={ui.get_menu_orientation(g_hwnd, g_menu_id)} "
            f"菜单项={ui.get_menu_item_count(g_hwnd, g_menu_id)} "
            f"锚点={ui.get_anchor_active(g_hwnd, g_anchor_id)}/"
            f"{ui.get_anchor_item_count(g_hwnd, g_anchor_id)} "
            f"分段={ui.get_segmented_active(g_hwnd, g_segmented_id)}/"
            f"{ui.get_segmented_item_count(g_hwnd, g_segmented_id)}"
        )


def main():
    global g_hwnd, g_dropdown_id, g_menu_id, g_anchor_id, g_segmented_id
    global g_open_id, g_update_id

    hwnd = ui.create_window("🧭 导航状态组件示例", 220, 80, 980, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 610)

    ui.create_text(hwnd, content_id, "🧭 导航状态组件", 28, 24, 360, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐下拉菜单、菜单、锚点和分段控件的运行时状态 API：打开状态、项目数量、方向读取和选中项读取。",
        28, 68, 800, 48,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_menu_id = ui.create_menu(
        hwnd, content_id, ["🏠 首页", "🧩 组件", "📚 文档"], 1, 0,
        28, 134, 560, 54,
    )
    g_dropdown_id = ui.create_dropdown(
        hwnd, content_id, "🛠 更多操作", ["查看", "编辑", "删除"], 0,
        640, 142, 180, 40,
    )

    ui.create_text(hwnd, content_id, "📌 锚点导航", 28, 226, 180, 28)
    g_anchor_id = ui.create_anchor(
        hwnd, content_id, ["概览", "安装", "示例"], 1,
        28, 264, 230, 180,
    )

    ui.create_text(hwnd, content_id, "📊 分段切换", 330, 226, 180, 28)
    g_segmented_id = ui.create_segmented(
        hwnd, content_id, ["今日", "本周", "本月"], 0,
        330, 264, 360, 46,
    )

    g_open_id = ui.create_button(hwnd, content_id, "🔓", "打开下拉", 740, 264, 150, 42)
    g_update_id = ui.create_button(hwnd, content_id, "🚀", "更新状态", 740, 322, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_open_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "验证提示",
        "示例会在 1 秒后打开下拉菜单，2 秒后更新导航数据并打印状态读取结果。",
        28, 488, 780, 82,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("导航状态组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_open = False
    auto_update = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_open and elapsed > 1.0:
            on_click(g_open_id)
            auto_open = True
        if not auto_update and elapsed > 2.0:
            on_click(g_update_id)
            auto_update = True
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

    print("导航状态组件示例结束。")


if __name__ == "__main__":
    main()
