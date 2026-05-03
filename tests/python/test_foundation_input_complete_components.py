import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
VK_SPACE = 0x20

g_hwnd = None
g_button_id = 0
g_edit_id = 0
g_button_clicks = 0
g_text_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 输入交互完成验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_button_click(element_id):
    global g_button_clicks
    if element_id == g_button_id:
        g_button_clicks += 1
        print("[按钮] 键盘点击回调次数:", g_button_clicks)


@ui.TextCallback
def on_edit_text(element_id, data, length):
    if element_id != g_edit_id:
        return
    text = ctypes.string_at(data, length).decode("utf-8", errors="replace")
    g_text_events.append(text)
    print("[编辑框] 文本变化:", text)


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
    global g_hwnd, g_button_id, g_edit_id

    hwnd = ui.create_window("⌨️ 输入交互完成验证", 200, 90, 920, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 570)
    ui.set_panel_style(hwnd, content_id, 0x00000000, 0x00000000, 0.0, 0.0, 0)

    ui.create_text(hwnd, content_id, "⌨️ Button / EditBox 完整交互路径", 28, 24, 720, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证按钮 Space/Enter 键盘触发点击回调、编辑框文本变化回调，以及中文输入路径的基础字符处理。",
        28, 70, 780, 58,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_button_id = ui.create_button(hwnd, content_id, "✅", "键盘触发按钮", 28, 158, 190, 44)
    ui.set_button_variant(hwnd, g_button_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_button_id, on_button_click)

    ui.create_text(hwnd, content_id, "📝 编辑框文本回调", 28, 246, 220, 28)
    g_edit_id = ui.create_editbox(hwnd, content_id, 28, 284, 540, 44)
    ui.set_editbox_options(hwnd, g_edit_id, False, False, False, 0xFF16A34A, "请输入中文或 emoji ✨")
    ui.dll.EU_SetEditBoxTextCallback(hwnd, g_edit_id, on_edit_text)

    panel_id = ui.create_panel(hwnd, content_id, 620, 150, 240, 218)
    ui.set_panel_style(hwnd, panel_id, 0x102563EB, 0x552563EB, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "🔎 自动验证", 0, 0, 160, 30)
    desc_id = ui.create_text(
        hwnd,
        panel_id,
        "窗口显示后会自动给按钮发送 Space 键，并向编辑框写入中文字符和 emoji 文本。",
        0, 42, 190, 120,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("输入交互完成验证已显示。窗口会保持 60 秒。")

    user32 = ctypes.windll.user32
    pump_messages(0.5)
    ui.dll.EU_SetElementFocus(hwnd, g_button_id)
    user32.PostMessageW(hwnd, WM_KEYDOWN, VK_SPACE, 0)
    user32.PostMessageW(hwnd, WM_KEYUP, VK_SPACE, 0)
    pump_messages(0.5)

    ui.dll.EU_SetElementFocus(hwnd, g_edit_id)
    user32.PostMessageW(hwnd, WM_CHAR, ord("你"), 0)
    user32.PostMessageW(hwnd, WM_CHAR, ord("好"), 0)
    pump_messages(0.5)
    ui.set_editbox_text(hwnd, g_edit_id, "API 写入：中文 + emoji 🎯")
    pump_messages(0.5)

    print("[读取] Button:", ui.get_button_state(hwnd, g_button_id), "点击次数:", g_button_clicks)
    print("[读取] EditBox:", ui.get_editbox_text(hwnd, g_edit_id))
    print("[读取] EditBox 状态:", ui.get_editbox_state(hwnd, g_edit_id))
    print("[读取] 文本回调次数:", len(g_text_events))

    start = time.time()
    while time.time() - start < 58:
        if not pump_messages(0.2):
            break

    print("输入交互完成验证结束。")


if __name__ == "__main__":
    main()
