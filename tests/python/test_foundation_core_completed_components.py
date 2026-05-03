import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_info_id = 0
g_primary_button_id = 0
g_link_id = 0
g_icon_id = 0
g_toggle_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 基础组件状态验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_toggle_id:
        closed = not ui.get_infobox_closed(g_hwnd, g_info_id)
        ui.set_infobox_closed(g_hwnd, g_info_id, closed)
        ui.set_link_visited(g_hwnd, g_link_id, closed)
        ui.set_icon_options(g_hwnd, g_icon_id, 1.85 if closed else 1.35, 18.0 if closed else -10.0)
        ui.set_button_variant(g_hwnd, g_primary_button_id, 2 if closed else 1)
        print("[切换] 信息框关闭状态:", closed)
        print("[读取] Link:", ui.get_link_visited(g_hwnd, g_link_id),
              "Icon:", ui.get_icon_options(g_hwnd, g_icon_id),
              "Button:", ui.get_button_state(g_hwnd, g_primary_button_id))
    elif element_id == g_link_id:
        ui.set_link_visited(g_hwnd, g_link_id, True)
        print("[链接] 已设置为访问状态:", ui.get_link_visited(g_hwnd, g_link_id))


def main():
    global g_hwnd, g_info_id, g_primary_button_id, g_link_id, g_icon_id, g_toggle_id

    hwnd = ui.create_window("🧱 基础组件状态验证", 200, 80, 980, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 630)
    ui.set_panel_style(hwnd, content_id, 0x00000000, 0x00000000, 0.0, 0.0, 0)

    ui.create_text(hwnd, content_id, "🧱 Panel / Button / InfoBox / Text / Link / Icon", 28, 24, 760, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批验证基础组件的 C++ 状态能力：面板样式可读回，按钮支持样式变体和焦点状态读取，"
        "信息框支持关闭状态，文本/链接/图标都能通过专用 Get API 读回设置值。",
        28, 70, 760, 72,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    panel_id = ui.create_panel(hwnd, content_id, 28, 160, 420, 150)
    ui.set_panel_style(hwnd, panel_id, 0x182563EB, 0xAA2563EB, 1.5, 16.0, 18)
    panel_style = ui.get_panel_style(hwnd, panel_id)
    ui.create_text(hwnd, panel_id, "🎨 面板样式可读回", 0, 0, 250, 32)
    panel_text_id = ui.create_text(
        hwnd,
        panel_id,
        f"背景与边框已设置，读取结果：padding={panel_style[4] if panel_style else '失败'}",
        0, 46, 330, 54,
    )
    ui.set_text_options(hwnd, panel_text_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_info_id = ui.create_infobox(
        hwnd,
        content_id,
        "✅ 信息框状态",
        "点击右下角按钮会关闭/重新打开这一条提示，并同步更新链接访问状态和图标旋转。",
        492, 160, 420, 112,
    )
    ui.set_infobox_options(hwnd, g_info_id, type=1, closable=True, accent=0xFF16A34A, icon="✅")

    text_id = ui.create_text(hwnd, content_id, "📌 居中短文本", 28, 342, 260, 42)
    ui.set_text_options(hwnd, text_id, align=1, valign=1, wrap=False, ellipsis=False)
    ui.create_text(hwnd, content_id, "读取文本选项：" + str(ui.get_text_options(hwnd, text_id)), 310, 348, 330, 30)

    g_link_id = ui.create_link(hwnd, content_id, "🔗 点击后标记为已访问", 28, 410, 260, 34)
    ui.set_text_options(hwnd, g_link_id, align=0, valign=1, wrap=False, ellipsis=False)
    ui.dll.EU_SetElementClickCallback(hwnd, g_link_id, on_click)

    g_icon_id = ui.create_icon(hwnd, content_id, "🌟", 692, 326, 130, 130)
    ui.set_icon_options(hwnd, g_icon_id, 1.35, -10.0)
    icon_status_id = ui.create_text(hwnd, content_id, "🌟 图标缩放/旋转可读回", 642, 468, 250, 34)
    ui.set_text_options(hwnd, icon_status_id, align=1, valign=1, wrap=False, ellipsis=False)

    variants = [("普通", 0), ("主要", 1), ("成功", 2), ("警告", 3), ("危险", 4)]
    for index, (label, variant) in enumerate(variants):
        button_id = ui.create_button(hwnd, content_id, "✨", label, 28 + index * 122, 520, 104, 42)
        ui.set_button_variant(hwnd, button_id, variant)
        if variant == 1:
            g_primary_button_id = button_id

    g_toggle_id = ui.create_button(hwnd, content_id, "🔁", "切换状态", 792, 520, 120, 42)
    ui.set_button_variant(hwnd, g_toggle_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("基础组件状态验证已显示。窗口会保持 60 秒，可手动点击按钮检查交互。")
    print("[初始读取] Panel:", panel_style)
    print("[初始读取] Text:", ui.get_text_options(hwnd, text_id))
    print("[初始读取] Icon:", ui.get_icon_options(hwnd, g_icon_id))
    print("[初始读取] Button:", ui.get_button_state(hwnd, g_primary_button_id))

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < 60:
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

    print("基础组件状态验证结束。")


if __name__ == "__main__":
    main()
