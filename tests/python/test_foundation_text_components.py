import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_link_id = 0
g_icon_id = 0
g_update_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 基础文本组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_link_id:
        print("[链接] 已点击并切换为访问态")
    elif element_id == g_update_id:
        ui.set_link_visited(g_hwnd, g_link_id, True)
        ui.set_icon_options(g_hwnd, g_icon_id, 1.55, 18.0)
        print("[更新] 链接访问态、图标缩放和旋转已更新")


def main():
    global g_hwnd, g_link_id, g_icon_id, g_update_id

    hwnd = ui.create_window("✨ 基础文本组件示例", 240, 100, 860, 560)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 840, 510)

    ui.create_text(hwnd, content_id, "📝 文本排版能力", 28, 24, 420, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "这批补齐了文本对齐、自动换行、单行省略、链接访问态，以及 emoji 图标缩放旋转。下面的长句会在固定宽度内自动换行，首屏尺寸已预留右侧和底部余量。",
        28, 72, 510, 92
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    center_id = ui.create_text(hwnd, content_id, "🎯 居中显示的标题文本", 28, 184, 300, 48)
    ui.set_text_options(hwnd, center_id, align=1, valign=1, wrap=False, ellipsis=False)
    ui.dll.EU_SetElementColor(hwnd, center_id, 0x00000000, 0xFF2563EB)

    ellipsis_id = ui.create_text(
        hwnd, content_id,
        "📌 这是一段很长的单行文本，用来验证省略号裁切不会撑破元素边界",
        28, 250, 360, 34
    )
    ui.set_text_options(hwnd, ellipsis_id, align=0, valign=1, wrap=False, ellipsis=True)

    g_link_id = ui.create_link(hwnd, content_id, "🔗 查看组件封装进度", 28, 314, 260, 32)
    ui.set_text_options(hwnd, g_link_id, align=0, valign=1, wrap=False, ellipsis=False)

    g_icon_id = ui.create_icon(hwnd, content_id, "🌈", 610, 82, 120, 120)
    ui.set_icon_options(hwnd, g_icon_id, 2.4, -12.0)

    ui.create_text(hwnd, content_id, "图标可缩放和旋转", 560, 214, 230, 32)
    icon_note_id = ui.create_text(hwnd, content_id, "💡 使用彩色 emoji 字体渲染，保持纯 D2D 绘制。", 520, 254, 280, 64)
    ui.set_text_options(hwnd, icon_note_id, align=1, valign=1, wrap=True, ellipsis=False)

    g_update_id = ui.create_button(hwnd, content_id, "🚀", "更新状态", 28, 378, 150, 42)

    ui.dll.EU_SetElementClickCallback(hwnd, g_link_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("基础文本组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("基础文本组件示例结束。")


if __name__ == "__main__":
    main()
