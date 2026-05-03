import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_RETURN = 0x0D

g_hwnd = None
g_link_id = 0
g_link_clicks = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 基础展示完成验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_link_click(element_id):
    global g_link_clicks
    if element_id == g_link_id:
        g_link_clicks += 1
        print("[链接] 键盘点击回调次数:", g_link_clicks)


def pump_messages(seconds=1.0):
    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < seconds:
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
    return running


def main():
    global g_hwnd, g_link_id

    hwnd = ui.create_window("✨ 基础展示完成验证", 220, 90, 940, 650)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 600)
    ui.set_panel_style(hwnd, content_id, 0x00000000, 0x00000000, 0.0, 0.0, 0)

    ui.create_text(hwnd, content_id, "✨ InfoBox / Text / Link / Icon / Space", 28, 24, 740, 36)
    text_id = ui.create_text(
        hwnd,
        content_id,
        "文本支持中文 emoji、换行、省略和对齐；链接支持访问态与键盘点击；图标支持缩放旋转；占位元素可参与布局。",
        28, 70, 780, 64,
    )
    ui.set_text_options(hwnd, text_id, align=0, valign=0, wrap=True, ellipsis=False)

    info_id = ui.create_infobox(
        hwnd,
        content_id,
        "✅ 信息框建议高度",
        "这是一段较长的信息内容，用来验证 InfoBox 可以根据当前文本、图标和关闭按钮估算建议高度，便于调用侧做自适应布局。",
        28, 158, 560, 116,
    )
    ui.set_infobox_options(hwnd, info_id, type=1, closable=True, accent=0xFF16A34A, icon="✅")
    preferred = ui.get_infobox_preferred_height(hwnd, info_id)
    ui.create_text(hwnd, content_id, f"📏 建议高度：{preferred}", 620, 184, 230, 34)

    icon_id = ui.create_icon(hwnd, content_id, "🌈", 638, 252, 120, 120)
    ui.set_icon_options(hwnd, icon_id, 1.7, 18.0)
    ui.create_text(hwnd, content_id, "🌈 图标缩放旋转", 600, 382, 200, 34)

    g_link_id = ui.create_link(hwnd, content_id, "🔗 回车触发访问链接", 28, 318, 260, 36)
    ui.set_text_options(hwnd, g_link_id, align=0, valign=1, wrap=False, ellipsis=False)
    ui.dll.EU_SetElementClickCallback(hwnd, g_link_id, on_link_click)

    layout_id = ui.create_layout(hwnd, content_id, 0, 8, 28, 406, 560, 58)
    ui.set_panel_style(hwnd, layout_id, 0x10F59E0B, 0x55F59E0B, 1.0, 12.0, 10)
    ui.set_layout_options(hwnd, layout_id, orientation=0, gap=8, stretch=True, align=1, wrap=False)
    ui.create_button(hwnd, layout_id, "📦", "左", 0, 0, 96, 38)
    space_id = ui.create_space(hwnd, layout_id, 0, 0, 80, 38)
    ui.create_button(hwnd, layout_id, "🎯", "右", 0, 0, 96, 38)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("基础展示完成验证已显示。窗口会保持 60 秒。")
    print("[读取] Text:", ui.get_text_options(hwnd, text_id))
    print("[读取] InfoBox 建议高度:", preferred)
    print("[读取] Icon:", ui.get_icon_options(hwnd, icon_id))
    print("[读取] Space:", ui.get_space_size(hwnd, space_id))
    print("[读取] Link 初始访问态:", ui.get_link_visited(hwnd, g_link_id))

    user32 = ctypes.windll.user32
    pump_messages(0.5)
    ui.dll.EU_SetElementFocus(hwnd, g_link_id)
    user32.PostMessageW(hwnd, WM_KEYDOWN, VK_RETURN, 0)
    user32.PostMessageW(hwnd, WM_KEYUP, VK_RETURN, 0)
    pump_messages(0.5)
    print("[读取] Link 访问态:", ui.get_link_visited(hwnd, g_link_id), "点击次数:", g_link_clicks)

    start = time.time()
    while time.time() - start < 59:
        if not pump_messages(0.2):
            break

    print("基础展示完成验证结束。")


if __name__ == "__main__":
    main()
