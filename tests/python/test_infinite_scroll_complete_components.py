import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_list_id = 0
g_disabled_id = 0
g_no_more_id = 0
g_to_top_id = 0
g_to_bottom_id = 0
g_load_events = []


def make_items(start, count, tag="任务"):
    return [
        (f"📌 第 {i} 条桌面任务", f"滚动列表内置数据项，编号 {i}", tag)
        for i in range(start, start + count)
    ]


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 无限滚动完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_load(element_id, item_count, scroll_y, max_scroll):
    g_load_events.append((item_count, scroll_y, max_scroll))
    print(f"[触底加载] 元素={element_id} 项数={item_count} scroll={scroll_y}/{max_scroll}")
    ui.append_infinite_scroll_items(g_hwnd, element_id, make_items(item_count + 1, 2, "新增"))
    ui.set_infinite_scroll_state(g_hwnd, element_id, loading=False, no_more=True, disabled=False)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_to_top_id:
        ui.set_infinite_scroll_scroll(g_hwnd, g_list_id, 0)
        print("[按钮] 回到顶部：", ui.get_infinite_scroll_full_state(g_hwnd, g_list_id))
    elif element_id == g_to_bottom_id:
        state = ui.get_infinite_scroll_full_state(g_hwnd, g_list_id)
        ui.set_infinite_scroll_scroll(g_hwnd, g_list_id, state["max_scroll"])
        print("[按钮] 到达底部：", ui.get_infinite_scroll_full_state(g_hwnd, g_list_id))


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
    global g_hwnd, g_list_id, g_disabled_id, g_no_more_id, g_to_top_id, g_to_bottom_id

    hwnd = ui.create_window("♾️ 无限滚动完整组件验证", 220, 80, 1080, 720)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root_id = ui.create_container(hwnd, 0, 0, 0, 1040, 660)

    ui.create_text(hwnd, root_id, "♾️ InfiniteScroll 无限滚动完整封装", 28, 24, 620, 38)
    intro_id = ui.create_text(
        hwnd,
        root_id,
        "验证内置列表、触底加载、loading/noMore/disabled、滚轮、键盘、状态文本、样式模式和完整状态读回。",
        28, 72, 900, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_list_id = ui.create_infinite_scroll(hwnd, root_id, make_items(1, 12), 42, 150, 520, 330)
    ui.set_infinite_scroll_options(hwnd, g_list_id, 58, 8, 56, 1, True, True)
    ui.set_infinite_scroll_texts(hwnd, g_list_id, "⏳ 正在加载更多任务...", "✅ 没有更多任务了", "🫥 暂无任务")
    ui.set_infinite_scroll_load_callback(hwnd, g_list_id, on_load)

    state = ui.get_infinite_scroll_full_state(hwnd, g_list_id)
    print("[初始状态] ", state)
    if not state or state["item_count"] != 12 or state["style_mode"] != 1 or not state["show_index"]:
        raise RuntimeError("无限滚动初始状态读回失败")

    ui.set_infinite_scroll_scroll(hwnd, g_list_id, state["max_scroll"])
    bottom_state = ui.get_infinite_scroll_full_state(hwnd, g_list_id)
    print("[触底状态] ", bottom_state)
    if bottom_state["load_count"] != 1 or not bottom_state["no_more"] or bottom_state["item_count"] != 14:
        raise RuntimeError("无限滚动触底加载或追加失败")
    if not g_load_events:
        raise RuntimeError("无限滚动触底回调未触发")

    ui.set_infinite_scroll_scroll(hwnd, g_list_id, 0)
    ui.set_infinite_scroll_scroll(hwnd, g_list_id, 116)
    scroll_state = ui.get_infinite_scroll_full_state(hwnd, g_list_id)
    if scroll_state["scroll_y"] != 116 or scroll_state["last_action"] != 6:
        raise RuntimeError("无限滚动程序化滚动失败")

    g_disabled_id = ui.create_infinite_scroll(hwnd, root_id, make_items(1, 5, "禁用"), 610, 150, 340, 150)
    ui.set_infinite_scroll_options(hwnd, g_disabled_id, 46, 6, 24, 2, True, False)
    ui.set_infinite_scroll_state(hwnd, g_disabled_id, loading=False, no_more=False, disabled=True)
    ui.set_infinite_scroll_load_callback(hwnd, g_disabled_id, on_load)
    d_state = ui.get_infinite_scroll_full_state(hwnd, g_disabled_id)
    ui.set_infinite_scroll_scroll(hwnd, g_disabled_id, d_state["max_scroll"])
    if ui.get_infinite_scroll_full_state(hwnd, g_disabled_id)["load_count"] != 0:
        raise RuntimeError("disabled 状态不应触发加载")

    g_no_more_id = ui.create_infinite_scroll(hwnd, root_id, [], 610, 330, 340, 150)
    ui.set_infinite_scroll_texts(hwnd, g_no_more_id, "加载中...", "没有更多了", "🫥 当前没有审计记录")
    ui.set_infinite_scroll_state(hwnd, g_no_more_id, loading=False, no_more=True, disabled=False)
    empty_state = ui.get_infinite_scroll_full_state(hwnd, g_no_more_id)
    if empty_state["item_count"] != 0 or not empty_state["no_more"]:
        raise RuntimeError("空状态或 noMore 状态读回失败")

    g_to_top_id = ui.create_button(hwnd, root_id, "⬆️", "回到顶部", 42, 520, 130, 40)
    g_to_bottom_id = ui.create_button(hwnd, root_id, "⬇️", "到底部", 196, 520, 130, 40)
    ui.dll.EU_SetElementClickCallback(hwnd, g_to_top_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_to_bottom_id, on_click)

    ui.dll.EU_SetElementFocus(hwnd, g_list_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x24, 0)  # Home
    pump_messages(user32, msg, 0.2)
    key_state = ui.get_infinite_scroll_full_state(hwnd, g_list_id)
    if key_state["scroll_y"] != 0 or key_state["last_action"] != 9:
        raise RuntimeError("无限滚动键盘 Home 操作失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("无限滚动完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    while running and time.time() - start < 60:
        running = pump_messages(user32, msg, 0.05)

    print("无限滚动完整组件示例结束。")


if __name__ == "__main__":
    main()
