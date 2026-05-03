import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_backtop_id = 0
g_show_id = 0
g_trigger_id = 0
g_hide_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 返回顶部完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_show_id:
        ui.set_backtop_scroll(g_hwnd, g_backtop_id, 720)
        print(f"[显示阈值] 状态={ui.get_backtop_full_state(g_hwnd, g_backtop_id)}")
    elif element_id == g_trigger_id:
        ui.trigger_backtop(g_hwnd, g_backtop_id)
        print(f"[触发回顶] 状态={ui.get_backtop_full_state(g_hwnd, g_backtop_id)}")
    elif element_id == g_hide_id:
        ui.set_backtop_scroll(g_hwnd, g_backtop_id, 80)
        print(f"[隐藏阈值] 状态={ui.get_backtop_full_state(g_hwnd, g_backtop_id)}")


def main():
    global g_hwnd, g_backtop_id, g_show_id, g_trigger_id, g_hide_id

    hwnd = ui.create_window("⬆️ 返回顶部完整组件", 220, 80, 900, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 860, 560)

    ui.create_text(hwnd, content_id, "⬆️ 返回顶部完整验证", 28, 24, 380, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证滚动容器绑定、显示阈值、目标位置跳转、鼠标/键盘触发实现、完整状态读回和中文 emoji 展示。",
        28, 70, 780, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "初始滚动 360，大于阈值 240，所以返回顶部按钮可见。1 秒后模拟滚动到 720，2 秒后触发回顶，3 秒后滚动到阈值以下隐藏。",
        48, 150, 620, 92,
    )

    g_backtop_id = ui.create_backtop(hwnd, content_id, "⬆️", 730, 400, 56, 56)
    ui.set_backtop_options(
        hwnd,
        g_backtop_id,
        scroll_position=360,
        threshold=240,
        target_position=0,
        container_id=content_id,
        duration_ms=280,
    )

    g_show_id = ui.create_button(hwnd, content_id, "🧭", "模拟滚动", 48, 300, 150, 42)
    g_trigger_id = ui.create_button(hwnd, content_id, "⬆️", "触发回顶", 220, 300, 150, 42)
    g_hide_id = ui.create_button(hwnd, content_id, "👁️", "低于阈值", 392, 300, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_show_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_trigger_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_hide_id, on_click)

    initial = ui.get_backtop_full_state(hwnd, g_backtop_id)
    print(f"[初始] 状态={initial}")
    if not initial or initial["visible"] != 1 or initial["container"] != content_id or initial["duration"] != 280:
        raise RuntimeError("返回顶部完整状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("返回顶部完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_show = False
    auto_trigger = False
    auto_hide = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_show and elapsed > 1.0:
            on_click(g_show_id)
            auto_show = True
        if not auto_trigger and elapsed > 2.0:
            on_click(g_trigger_id)
            auto_trigger = True
        if not auto_hide and elapsed > 3.0:
            on_click(g_hide_id)
            auto_hide = True
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

    print("返回顶部完整组件示例结束。")


if __name__ == "__main__":
    main()
