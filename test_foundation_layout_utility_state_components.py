import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_layout_id = 0
g_space_id = 0
g_border_id = 0
g_divider_id = 0
g_toggle_id = 0
g_vertical = False


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 布局工具状态验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_vertical
    if element_id != g_toggle_id:
        return
    g_vertical = not g_vertical
    ui.set_layout_options(g_hwnd, g_layout_id, orientation=1 if g_vertical else 0,
                          gap=14 if g_vertical else 8, stretch=False, align=1, wrap=False)
    ui.set_space_size(g_hwnd, g_space_id, 28 if g_vertical else 60, 34 if g_vertical else 36)
    ui.set_border_options(g_hwnd, g_border_id, sides=15 if g_vertical else 13,
                          color=0xFF16A34A if g_vertical else 0xFF2563EB,
                          width=2.0, radius=14.0, title="🧩 状态边框")
    ui.set_divider_options(g_hwnd, g_divider_id, direction=0,
                           content_position=2 if g_vertical else 1,
                           color=0xFF16A34A if g_vertical else 0xFF2563EB,
                           width=2.0, dashed=g_vertical, text="✨ 状态分割线")
    print("[读取] Layout:", ui.get_layout_options(g_hwnd, g_layout_id))
    print("[读取] Space:", ui.get_space_size(g_hwnd, g_space_id))
    print("[读取] Border:", ui.get_border_options(g_hwnd, g_border_id))
    print("[读取] Divider:", ui.get_divider_options(g_hwnd, g_divider_id))


def main():
    global g_hwnd, g_layout_id, g_space_id, g_border_id, g_divider_id, g_toggle_id

    hwnd = ui.create_window("📐 布局工具状态验证", 220, 90, 940, 640)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 590)
    ui.set_panel_style(hwnd, content_id, 0x00000000, 0x00000000, 0.0, 0.0, 0)

    ui.create_text(hwnd, content_id, "📐 Space / Container / Layout / Border / Divider", 28, 24, 720, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐基础布局工具组件的状态读回：Layout 的方向/间距/对齐，Space 的逻辑尺寸，"
        "Border 的边线掩码与圆角，Divider 的位置/颜色/虚线状态。",
        28, 70, 760, 64,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_border_id = ui.create_border(hwnd, content_id, 28, 156, 390, 170)
    ui.set_panel_style(hwnd, g_border_id, 0x1016A34A, 0xFF2563EB, 1.0, 14.0, 18)
    ui.set_border_options(hwnd, g_border_id, sides=13, color=0xFF2563EB, width=2.0, radius=14.0, title="🧩 状态边框")
    ui.create_text(hwnd, g_border_id, "边框支持指定边线、颜色、宽度与圆角。", 0, 28, 300, 36)
    ui.create_text(hwnd, g_border_id, "读取结果会输出到控制台。", 0, 74, 260, 30)

    g_divider_id = ui.create_divider(hwnd, content_id, "✨ 状态分割线", 0, 1, 458, 164, 400, 42)
    ui.set_divider_options(hwnd, g_divider_id, 0, 1, 0xFF2563EB, 2.0, False, "✨ 状态分割线")

    g_layout_id = ui.create_layout(hwnd, content_id, 0, 8, 458, 236, 400, 90)
    ui.set_panel_style(hwnd, g_layout_id, 0x10F59E0B, 0x55F59E0B, 1.0, 12.0, 10)
    ui.set_layout_options(hwnd, g_layout_id, orientation=0, gap=8, stretch=False, align=1, wrap=False)
    ui.create_button(hwnd, g_layout_id, "🧱", "左侧", 0, 0, 92, 36)
    g_space_id = ui.create_space(hwnd, g_layout_id, 0, 0, 60, 36)
    ui.create_button(hwnd, g_layout_id, "🎯", "右侧", 0, 0, 92, 36)

    status_id = ui.create_text(hwnd, content_id, "🔎 初始状态已通过 Get API 读回，点击按钮切换后再次读取。", 28, 370, 720, 34)
    ui.set_text_options(hwnd, status_id, align=0, valign=1, wrap=False, ellipsis=False)

    g_toggle_id = ui.create_button(hwnd, content_id, "🔁", "切换布局状态", 28, 428, 160, 42)
    ui.set_button_variant(hwnd, g_toggle_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("布局工具状态验证已显示。窗口会保持 60 秒。")
    print("[初始读取] Layout:", ui.get_layout_options(hwnd, g_layout_id))
    print("[初始读取] Space:", ui.get_space_size(hwnd, g_space_id))
    print("[初始读取] Border:", ui.get_border_options(hwnd, g_border_id))
    print("[初始读取] Divider:", ui.get_divider_options(hwnd, g_divider_id))

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_done = False
    while running and time.time() - start < 60:
        if not auto_done and time.time() - start > 1.0:
            on_click(g_toggle_id)
            auto_done = True
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

    print("布局工具状态验证结束。")


if __name__ == "__main__":
    main()
