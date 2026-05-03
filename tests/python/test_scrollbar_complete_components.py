import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_scrollbar_id = 0
g_content_id = 0
g_to_top_id = 0
g_to_bottom_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 滚动条完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_scroll_change(element_id, value, min_value, max_value):
    g_events.append((value, min_value, max_value))
    print(f"[滚动回调] 元素={element_id} 值={value} 范围={min_value}-{max_value}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_to_top_id:
        ui.dll.EU_SetScrollbarValue(g_hwnd, g_scrollbar_id, 0)
        print("[按钮] 回到顶部：", ui.get_scrollbar_full_state(g_hwnd, g_scrollbar_id))
    elif element_id == g_to_bottom_id:
        ui.dll.EU_SetScrollbarValue(g_hwnd, g_scrollbar_id, 420)
        print("[按钮] 到达底部：", ui.get_scrollbar_full_state(g_hwnd, g_scrollbar_id))


def pump_messages(user32, msg, duration):
    start = time.time()
    running = True
    while running and time.time() - start < duration:
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
    global g_hwnd, g_scrollbar_id, g_content_id, g_to_top_id, g_to_bottom_id

    hwnd = ui.create_window("🧭 滚动条完整组件验证", 220, 80, 1000, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root_id = ui.create_container(hwnd, 0, 0, 0, 960, 620)

    ui.create_text(hwnd, root_id, "🧭 Scrollbar 滚动条完整封装", 28, 24, 480, 38)
    intro_id = ui.create_text(
        hwnd,
        root_id,
        "验证真实滚轮派发、内容元素绑定、滚动偏移同步、键盘焦点、步进滚动、完整状态读回和变化回调。",
        28, 72, 860, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    viewport_id = ui.create_container(hwnd, root_id, 46, 150, 520, 300)
    ui.set_panel_style(hwnd, viewport_id, bg=0xFFF7FAFC, border=0xFFCBD5E1, radius=6)
    g_content_id = ui.create_container(hwnd, viewport_id, 0, 0, 500, 720)
    for i in range(12):
        y = 18 + i * 56
        title = f"📌 第 {i + 1} 条滚动内容"
        body = "这里是绑定到滚动条的内容区域，滚动值变化时会同步移动。"
        ui.create_text(hwnd, g_content_id, title, 20, y, 250, 24)
        item_body = ui.create_text(hwnd, g_content_id, body, 42, y + 24, 410, 24)
        ui.set_text_options(hwnd, item_body, align=0, valign=0, wrap=False, ellipsis=True)

    g_scrollbar_id = ui.create_scrollbar(hwnd, root_id, 0, 420, 1, 584, 150, 26, 300)
    ui.set_scrollbar_wheel_step(hwnd, g_scrollbar_id, 45)
    ui.bind_scrollbar_content(hwnd, g_scrollbar_id, g_content_id, 720, 300)
    ui.set_scrollbar_change_callback(hwnd, g_scrollbar_id, on_scroll_change)

    g_to_top_id = ui.create_button(hwnd, root_id, "⬆️", "回到顶部", 46, 490, 130, 40)
    g_to_bottom_id = ui.create_button(hwnd, root_id, "⬇️", "到达底部", 196, 490, 130, 40)
    ui.dll.EU_SetElementClickCallback(hwnd, g_to_top_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_to_bottom_id, on_click)

    state = ui.get_scrollbar_full_state(hwnd, g_scrollbar_id)
    print("[绑定状态] ", state)
    if not state or state["bound_element_id"] != g_content_id or state["max_value"] != 420:
        raise RuntimeError("滚动条内容绑定状态读回失败")
    if state["page_size"] != 300 or state["viewport_size"] != 300 or state["content_size"] != 720:
        raise RuntimeError("滚动条内容尺寸读回失败")

    ui.scrollbar_wheel(hwnd, g_scrollbar_id, -120)
    wheel_state = ui.get_scrollbar_full_state(hwnd, g_scrollbar_id)
    print("[滚轮派发] ", wheel_state)
    if wheel_state["value"] != 45 or wheel_state["wheel_event_count"] != 1 or wheel_state["last_action"] != 3:
        raise RuntimeError("滚动条滚轮派发失败")
    if wheel_state["content_offset"] != 45:
        raise RuntimeError("滚动条内容偏移同步失败")

    ui.scrollbar_scroll(hwnd, g_scrollbar_id, 2)
    api_state = ui.get_scrollbar_full_state(hwnd, g_scrollbar_id)
    print("[API 步进] ", api_state)
    if api_state["value"] != 135 or api_state["last_action"] != 2:
        raise RuntimeError("滚动条 API 步进失败")

    ui.dll.EU_SetElementFocus(hwnd, g_scrollbar_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x23, 0)
    pump_messages(user32, msg, 0.25)
    key_state = ui.get_scrollbar_full_state(hwnd, g_scrollbar_id)
    print("[键盘 End] ", key_state)
    if key_state["value"] != 420 or key_state["last_action"] != 7:
        raise RuntimeError("滚动条键盘操作失败")

    if not g_events:
        raise RuntimeError("滚动条变化回调未触发")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("滚动条完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    while running and time.time() - start < 60:
        running = pump_messages(user32, msg, 0.05)

    print("滚动条完整组件示例结束。")


if __name__ == "__main__":
    main()
