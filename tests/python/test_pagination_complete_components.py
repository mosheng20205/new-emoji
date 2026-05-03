import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_pagination_id = 0
g_next_id = 0
g_size_id = 0
g_jump_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 分页完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_pagination_change(element_id, value, page_size, action):
    g_events.append((value, page_size, action))
    print(f"[分页变化回调] 元素={element_id} 当前页={value} 每页={page_size} 动作={action}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_next_id:
        state = ui.get_pagination_full_state(g_hwnd, g_pagination_id)
        ui.set_pagination_current(g_hwnd, g_pagination_id, state["current_page"] + 1)
        print("[按钮] 下一页：", ui.get_pagination_full_state(g_hwnd, g_pagination_id))
    elif element_id == g_size_id:
        ui.next_pagination_page_size(g_hwnd, g_pagination_id)
        print("[按钮] 切换每页数量：", ui.get_pagination_full_state(g_hwnd, g_pagination_id))
    elif element_id == g_jump_id:
        ui.set_pagination_jump_page(g_hwnd, g_pagination_id, 12)
        ui.trigger_pagination_jump(g_hwnd, g_pagination_id)
        print("[按钮] 跳转页码：", ui.get_pagination_full_state(g_hwnd, g_pagination_id))


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
    global g_hwnd, g_pagination_id, g_next_id, g_size_id, g_jump_id

    hwnd = ui.create_window("📄 分页完整组件验证", 220, 80, 1040, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1000, 600)

    ui.create_text(hwnd, content_id, "📄 Pagination 分页完整封装", 28, 24, 560, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证省略页码、上一页/下一页、每页数量切换、跳转页、键盘导航、变化回调和完整状态读回。",
        28, 72, 900, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_pagination_id = ui.create_pagination(
        hwnd,
        content_id,
        total=368,
        page_size=10,
        current=6,
        x=46,
        y=156,
        w=900,
        h=48,
    )
    ui.set_pagination_options(hwnd, g_pagination_id, show_jumper=True, show_size_changer=True, visible_page_count=7)
    ui.set_pagination_page_size_options(hwnd, g_pagination_id, [10, 20, 50])
    ui.set_pagination_change_callback(hwnd, g_pagination_id, on_pagination_change)

    ui.create_infobox(
        hwnd,
        content_id,
        "✅ 验证提示",
        "分页条包含页码、省略号、每页数量和跳转按钮；可用方向键、Home/End、PageUp/PageDown、数字键和回车操作。",
        46,
        250,
        840,
        92,
    )

    g_next_id = ui.create_button(hwnd, content_id, "➡️", "下一页", 46, 386, 130, 42)
    g_size_id = ui.create_button(hwnd, content_id, "📦", "切换每页", 198, 386, 150, 42)
    g_jump_id = ui.create_button(hwnd, content_id, "🎯", "跳到 12 页", 370, 386, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_next_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_size_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_jump_id, on_click)

    initial = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[初始状态]", initial)
    if not initial or initial["total"] != 368 or initial["page_count"] != 37 or initial["current_page"] != 6:
        raise RuntimeError("分页初始状态读回失败")
    if initial["show_jumper"] != 1 or initial["show_size_changer"] != 1 or initial["visible_page_count"] != 7:
        raise RuntimeError("分页完整选项读回失败")

    ui.set_pagination_jump_page(hwnd, g_pagination_id, 12)
    ui.trigger_pagination_jump(hwnd, g_pagination_id)
    jumped = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[程序跳转]", jumped)
    if jumped["current_page"] != 12 or jumped["jump_count"] < 1 or jumped["last_action"] != 5:
        raise RuntimeError("分页跳转失败")

    ui.next_pagination_page_size(hwnd, g_pagination_id)
    sized = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[每页数量切换]", sized)
    if sized["page_size"] != 20 or sized["page_count"] != 19 or sized["size_change_count"] < 1:
        raise RuntimeError("分页每页数量切换失败")

    ui.set_pagination_current(hwnd, g_pagination_id, 3)
    selected = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[程序选页]", selected)
    if selected["current_page"] != 3 or not g_events:
        raise RuntimeError("分页选择回调失败")

    ui.dll.EU_SetElementFocus(hwnd, g_pagination_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)
    pump_messages(user32, msg, 0.25)
    key_state = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[键盘右移]", key_state)
    if key_state["current_page"] != 4 or key_state["last_action"] != 3:
        raise RuntimeError("分页键盘导航失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("分页完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    auto_clicked = False
    while running and time.time() - start < 60:
        if not auto_clicked and time.time() - start > 1.0:
            on_click(g_jump_id)
            auto_clicked = True
        running = pump_messages(user32, msg, 0.05)

    print("分页完整组件示例结束。")


if __name__ == "__main__":
    main()
