import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_layout_id = 0
g_toggle_id = 0
g_vertical = False


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 基础布局组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_vertical
    if element_id == g_toggle_id:
        g_vertical = not g_vertical
        ui.set_layout_options(
            g_hwnd,
            g_layout_id,
            orientation=1 if g_vertical else 0,
            gap=10,
            stretch=False,
            align=1,
            wrap=not g_vertical,
        )
        print("[布局] 已切换为" + ("垂直居中布局" if g_vertical else "横向自动换行布局"))


def main():
    global g_hwnd, g_layout_id, g_toggle_id

    hwnd = ui.create_window("📦 基础布局组件示例", 220, 90, 900, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 570)
    ui.set_panel_style(hwnd, content_id, 0x00000000, 0x00000000, 0.0, 0.0, 0)

    ui.create_text(hwnd, content_id, "📦 容器、布局与边框", 28, 24, 420, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐了 Panel/Container 的统一样式、Layout 的对齐与自动换行、Border 的标题和边线方向。所有控件仍然在单一 HWND 内纯 D2D 绘制。",
        28, 68, 640, 64,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    panel_id = ui.create_panel(hwnd, content_id, 28, 154, 820, 118)
    ui.set_panel_style(hwnd, panel_id, 0x182563EB, 0x663B82F6, 1.0, 14.0, 16)
    ui.create_text(hwnd, panel_id, "✨ 样式化面板", 0, 0, 180, 32)
    ui.create_text(hwnd, panel_id, "背景、圆角、边框和内边距现在可以通过专用 API 动态设置。", 0, 42, 500, 36)

    border_id = ui.create_border(hwnd, content_id, 28, 306, 380, 168)
    ui.set_panel_style(hwnd, border_id, 0x1016A34A, 0xFF16A34A, 1.5, 12.0, 18)
    ui.set_border_options(hwnd, border_id, sides=13, color=0xFF16A34A, width=2.0, radius=12.0, title="🧩 分组边框")
    ui.create_text(hwnd, border_id, "只绘制上、下、左边线", 0, 20, 250, 30)
    ui.create_text(hwnd, border_id, "标题会覆盖边线空隙，适合分组和表单区域。", 0, 62, 300, 46)

    ui.create_text(hwnd, content_id, "🧭 自动布局区域", 450, 306, 220, 28)
    g_layout_id = ui.create_layout(hwnd, content_id, 0, 10, 450, 346, 390, 128)
    ui.set_panel_style(hwnd, g_layout_id, 0x10F59E0B, 0x55F59E0B, 1.0, 12.0, 10)
    ui.set_layout_options(hwnd, g_layout_id, orientation=0, gap=10, stretch=False, align=1, wrap=True)

    labels = ["🚀 创建", "🎨 主题", "🧱 布局", "🔒 边界", "✅ 验证", "📄 文档"]
    for label in labels:
        item = ui.create_button(hwnd, g_layout_id, "", label, 0, 0, 92, 34)
        ui.dll.EU_SetElementEnabled(hwnd, item, 1)

    g_toggle_id = ui.create_button(hwnd, content_id, "🔁", "切换布局", 690, 500, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("基础布局组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("基础布局组件示例结束。")


if __name__ == "__main__":
    main()
