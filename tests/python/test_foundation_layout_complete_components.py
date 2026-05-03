import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_panel_id = 0
g_layout_id = 0
g_fill_panel_id = 0
g_weight_button_id = 0
g_toggle_id = 0
g_content_layout = True


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 基础布局完成验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_content_layout
    if element_id != g_toggle_id:
        return
    g_content_layout = not g_content_layout
    ui.set_panel_layout(g_hwnd, g_panel_id, fill_parent=False, content_layout=g_content_layout)
    ui.set_layout_child_weight(g_hwnd, g_layout_id, g_weight_button_id, 2 if g_content_layout else 1)
    ui.set_button_variant(g_hwnd, g_weight_button_id, 2 if g_content_layout else 3)
    print("[读取] Panel 布局:", ui.get_panel_layout(g_hwnd, g_panel_id))
    print("[读取] 填充面板:", ui.get_panel_layout(g_hwnd, g_fill_panel_id))
    print("[读取] Layout 权重:", ui.get_layout_child_weight(g_hwnd, g_layout_id, g_weight_button_id))


def main():
    global g_hwnd, g_panel_id, g_layout_id, g_fill_panel_id, g_weight_button_id, g_toggle_id

    hwnd = ui.create_window("🧱 基础布局完成验证", 180, 80, 980, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 630)
    ui.set_panel_style(hwnd, content_id, 0x00000000, 0x00000000, 0.0, 0.0, 0)

    ui.create_text(hwnd, content_id, "🧱 Panel / Layout 完整布局能力", 28, 24, 720, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证面板子元素按内边距内容区布局、子面板填充父内容区、Layout 子项权重分配和 Get API 读回。",
        28, 70, 790, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_panel_id = ui.create_panel(hwnd, content_id, 28, 150, 430, 230)
    ui.set_panel_style(hwnd, g_panel_id, 0x182563EB, 0xAA2563EB, 1.5, 16.0, 24)
    ui.set_panel_layout(hwnd, g_panel_id, fill_parent=False, content_layout=True)
    ui.create_text(hwnd, g_panel_id, "📦 子元素从内边距内容区开始绘制", 0, 0, 330, 34)
    ui.create_button(hwnd, g_panel_id, "✨", "内容区按钮", 0, 52, 150, 40)

    outer_id = ui.create_panel(hwnd, content_id, 502, 150, 390, 230)
    ui.set_panel_style(hwnd, outer_id, 0x14F59E0B, 0xAAF59E0B, 1.5, 16.0, 22)
    g_fill_panel_id = ui.create_panel(hwnd, outer_id, 0, 0, 100, 100)
    ui.set_panel_style(hwnd, g_fill_panel_id, 0x2216A34A, 0xAA16A34A, 1.5, 14.0, 18)
    ui.set_panel_layout(hwnd, g_fill_panel_id, fill_parent=True, content_layout=True)
    ui.create_text(hwnd, g_fill_panel_id, "🪟 子面板填充父内容区", 0, 0, 280, 34)
    ui.create_button(hwnd, g_fill_panel_id, "✅", "填充验证", 0, 52, 136, 40)

    g_layout_id = ui.create_layout(hwnd, content_id, 0, 10, 28, 430, 864, 74)
    ui.set_panel_style(hwnd, g_layout_id, 0x100EA5E9, 0x550EA5E9, 1.0, 12.0, 10)
    ui.set_layout_options(hwnd, g_layout_id, orientation=0, gap=10, stretch=True, align=1, wrap=False)
    ui.create_button(hwnd, g_layout_id, "📌", "固定宽度", 0, 0, 130, 42)
    g_weight_button_id = ui.create_button(hwnd, g_layout_id, "📏", "权重空间 x2", 0, 0, 120, 42)
    ui.create_button(hwnd, g_layout_id, "🎯", "固定尾部", 0, 0, 130, 42)
    ui.set_layout_child_weight(hwnd, g_layout_id, g_weight_button_id, 2)
    ui.set_button_variant(hwnd, g_weight_button_id, 2)

    status_id = ui.create_text(hwnd, content_id, "🔎 点击按钮会切换内容区布局状态并调整 Layout 权重。", 28, 548, 600, 34)
    ui.set_text_options(hwnd, status_id, align=0, valign=1, wrap=False, ellipsis=False)
    g_toggle_id = ui.create_button(hwnd, content_id, "🔁", "切换布局验证", 720, 542, 172, 44)
    ui.set_button_variant(hwnd, g_toggle_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("基础布局完成验证已显示。窗口会保持 60 秒。")
    print("[初始读取] Panel:", ui.get_panel_layout(hwnd, g_panel_id))
    print("[初始读取] 填充面板:", ui.get_panel_layout(hwnd, g_fill_panel_id))
    print("[初始读取] Layout:", ui.get_layout_options(hwnd, g_layout_id))
    print("[初始读取] Layout 权重:", ui.get_layout_child_weight(hwnd, g_layout_id, g_weight_button_id))

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

    print("基础布局完成验证结束。")


if __name__ == "__main__":
    main()
