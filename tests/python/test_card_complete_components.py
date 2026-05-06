import time
from ctypes import wintypes

import test_new_emoji as ui


g_hwnd = None


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages(seconds=2.0):
    user32 = ui.ctypes.windll.user32
    msg = wintypes.MSG()
    start = time.time()
    while time.time() - start < seconds:
        handled = False
        while user32.PeekMessageW(ui.ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                return
            user32.TranslateMessage(ui.ctypes.byref(msg))
            user32.DispatchMessageW(ui.ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def client_scale(hwnd, logical_width):
    rect = wintypes.RECT()
    ui.ctypes.windll.user32.GetClientRect(hwnd, ui.ctypes.byref(rect))
    return rect.right / float(logical_width) if logical_width else 1.0


def click_client(hwnd, x, y, scale=1.0):
    user32 = ui.ctypes.windll.user32
    x = int(round(x * scale))
    y = int(round(y * scale))
    lparam = (y << 16) | (x & 0xFFFF)
    user32.SendMessageW(hwnd, 0x0200, 0, lparam)
    user32.SendMessageW(hwnd, 0x0201, 1, lparam)
    user32.SendMessageW(hwnd, 0x0202, 0, lparam)


def click_card_footer_action(hwnd, element_id, scale=1.0):
    for y in range(180, 380, 10):
        for x in range(180, 460, 10):
            ui.reset_card_action(hwnd, element_id)
            click_client(hwnd, x, y, scale)
            action = ui.get_card_action(hwnd, element_id)
            if action >= 0:
                return action
    return -1


def main():
    global g_hwnd
    hwnd = ui.create_window("🪪 Card 卡片完整样式验证", 180, 80, 1060, 760)
    assert hwnd, "窗口创建失败"
    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1020, 700)

    title_card = ui.create_card(hwnd, root, "🪪 标题卡片", "旧正文", 1, 30, 36, 300, 180)
    ui.set_card_title(hwnd, title_card, "🪪 头部操作卡片")
    ui.set_card_body(hwnd, title_card, "正文支持中文、emoji 和样式读回。")
    ui.set_card_footer(hwnd, title_card, "📌 最近更新")
    ui.set_card_actions(hwnd, title_card, ["查看", "同步"])
    ui.set_card_style(hwnd, title_card, 0xFFFFFFFF, 0xFFDCDFF0, 1.0, 6.0, 18)
    ui.set_card_options(hwnd, title_card, shadow=2, hoverable=True)
    header_btn = ui.create_button(hwnd, title_card, "", "操作按钮", 198, 9, 86, 28, variant=5)
    assert header_btn > 0, "头部按钮插槽创建失败"

    list_card = ui.create_card(hwnd, root, "", "", 1, 360, 36, 300, 220)
    ui.set_card_items(hwnd, list_card, ["📄 列表内容 1", "📄 列表内容 2", "📄 列表内容 3", "📄 列表内容 4"])
    ui.set_card_body_style(hwnd, list_card, 18, 18, 18, 18, 14.0, 18, 0, False)
    assert ui.get_card_item_count(hwnd, list_card) == 4, "列表项数量读回失败"

    padded_card = ui.create_card(hwnd, root, "", "", 0, 690, 36, 300, 220)
    ui.set_card_items(hwnd, padded_card, ["✅ 列表内容 1", "✅ 列表内容 2", "✅ 列表内容 3", "✅ 列表内容 4"])
    ui.set_card_body_style(hwnd, padded_card, 18, 0, 18, 0, 14.0, 0, 18, True)

    image_card = ui.create_image_card(
        hwnd, root, "", "🍔 好吃的汉堡", "2026-05-06 09:30", "操作按钮",
        1, 30, 290, 300, 240
    )
    assert image_card > 0, "图片卡片插槽创建失败"

    style = ui.get_card_style(hwnd, title_card)
    assert style and style[0] == 0xFFFFFFFF and style[1] == 0xFFDCDFF0
    assert round(style[2], 1) == 1.0 and round(style[3], 1) == 6.0 and style[4] == 18
    body_style = ui.get_card_body_style(hwnd, padded_card)
    assert body_style and body_style["item_padding_y"] == 18 and body_style["divider"]
    assert ui.get_card_options(hwnd, title_card) == (2, True, 2)

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(0.2)
    scale = client_scale(hwnd, 1060)
    assert click_card_footer_action(hwnd, title_card, scale) >= 0, "页脚操作点击读回失败"
    ui.reset_card_action(hwnd, title_card)
    assert ui.get_card_action(hwnd, title_card) == -1, "页脚操作重置失败"
    print("[Card] 完整样式 API、读回和插槽组合创建成功。")
    pump_messages(2.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
