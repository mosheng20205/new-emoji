import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_anchor_id = 0
g_scroll_id = 0
g_jump_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 锚点完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_scroll_id:
        ui.set_anchor_scroll(g_hwnd, g_anchor_id, 850)
        print(f"[滚动定位] 状态={ui.get_anchor_state(g_hwnd, g_anchor_id)}")
    elif element_id == g_jump_id:
        ui.set_anchor_active(g_hwnd, g_anchor_id, 3)
        print(f"[跳转目标] 状态={ui.get_anchor_state(g_hwnd, g_anchor_id)}")


def main():
    global g_hwnd, g_anchor_id, g_scroll_id, g_jump_id

    hwnd = ui.create_window("📌 锚点完整组件", 220, 80, 900, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 860, 600)

    ui.create_text(hwnd, content_id, "📌 锚点完整验证", 28, 24, 340, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证滚动位置绑定、偏移夹取、目标位置读回、鼠标/键盘选择和中文 emoji 锚点展示。",
        28, 70, 760, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    items = ["📋 概览", "🧩 组件", "🎨 主题", "🧪 测试", "🚀 发布"]
    targets = [0, 260, 620, 900, 1280]
    g_anchor_id = ui.create_anchor(hwnd, content_id, items, 0, 48, 152, 260, 260)
    ui.set_anchor_targets(hwnd, g_anchor_id, targets)
    ui.set_anchor_options(hwnd, g_anchor_id, 80, content_id)
    ui.set_anchor_scroll(hwnd, g_anchor_id, 560)

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "当前滚动位置 560 加 80 偏移会激活“主题”。1 秒后滚动到测试区域，2 秒后程序化跳转到测试锚点。",
        350, 154, 420, 94,
    )

    g_scroll_id = ui.create_button(hwnd, content_id, "🧭", "模拟滚动", 350, 294, 150, 42)
    g_jump_id = ui.create_button(hwnd, content_id, "🎯", "跳转测试", 524, 294, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_scroll_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_jump_id, on_click)

    initial = ui.get_anchor_state(hwnd, g_anchor_id)
    print(f"[初始] 状态={initial}")
    if not initial or initial["active"] != 2 or initial["offset"] != 80 or initial["container"] != content_id:
        raise RuntimeError("锚点滚动状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("锚点完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_scroll = False
    auto_jump = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_scroll and elapsed > 1.0:
            on_click(g_scroll_id)
            auto_scroll = True
        if not auto_jump and elapsed > 2.0:
            on_click(g_jump_id)
            auto_jump = True
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

    print("锚点完整组件示例结束。")


if __name__ == "__main__":
    main()
