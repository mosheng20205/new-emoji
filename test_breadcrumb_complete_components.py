import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_breadcrumb_id = 0
g_home_id = 0
g_next_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 面包屑完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_breadcrumb_select(element_id, value, click_count, item_count):
    g_events.append((value, click_count, item_count))
    print(f"[面包屑选择回调] 元素={element_id} 当前={value} 次数={click_count} 总数={item_count}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_home_id:
        ui.trigger_breadcrumb_click(g_hwnd, g_breadcrumb_id, 0)
        print("[按钮] 回到首页：", ui.get_breadcrumb_full_state(g_hwnd, g_breadcrumb_id))
    elif element_id == g_next_id:
        state = ui.get_breadcrumb_full_state(g_hwnd, g_breadcrumb_id)
        ui.trigger_breadcrumb_click(g_hwnd, g_breadcrumb_id, state["current_index"] + 1)
        print("[按钮] 下一层：", ui.get_breadcrumb_full_state(g_hwnd, g_breadcrumb_id))


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
    global g_hwnd, g_breadcrumb_id, g_home_id, g_next_id

    hwnd = ui.create_window("🧭 面包屑完整组件验证", 220, 80, 960, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 560)

    ui.create_text(hwnd, content_id, "🧭 Breadcrumb 面包屑完整封装", 28, 24, 520, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证点击/键盘/程序触发选择、专用回调、分隔符、项目读回和完整状态读回。",
        28, 72, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_breadcrumb_id = ui.create_breadcrumb(
        hwnd,
        content_id,
        ["🏠 首页", "📦 组件库", "🧭 导航组件", "🍞 面包屑详情"],
        "›",
        2,
        46,
        150,
        760,
        44,
    )
    ui.set_breadcrumb_select_callback(hwnd, g_breadcrumb_id, on_breadcrumb_select)

    g_home_id = ui.create_button(hwnd, content_id, "🏠", "触发首页", 46, 245, 130, 40)
    g_next_id = ui.create_button(hwnd, content_id, "➡️", "触发下一层", 196, 245, 150, 40)
    ui.dll.EU_SetElementClickCallback(hwnd, g_home_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_next_id, on_click)

    state = ui.get_breadcrumb_full_state(hwnd, g_breadcrumb_id)
    print("[初始状态] ", state)
    if not state or state["current_index"] != 2 or state["item_count"] != 4:
        raise RuntimeError("面包屑初始状态读回失败")
    if "导航组件" not in ui.get_breadcrumb_item(hwnd, g_breadcrumb_id, 2):
        raise RuntimeError("面包屑项目文本读回失败")

    ui.trigger_breadcrumb_click(hwnd, g_breadcrumb_id, 1)
    clicked = ui.get_breadcrumb_full_state(hwnd, g_breadcrumb_id)
    print("[程序触发点击] ", clicked)
    if clicked["current_index"] != 1 or clicked["last_action"] != 4 or clicked["click_count"] < 1:
        raise RuntimeError("面包屑程序触发点击失败")
    if not g_events or g_events[-1][0] != 1:
        raise RuntimeError("面包屑选择回调失败")

    ui.dll.EU_SetElementFocus(hwnd, g_breadcrumb_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)
    pump_messages(user32, msg, 0.25)
    key_state = ui.get_breadcrumb_full_state(hwnd, g_breadcrumb_id)
    print("[键盘右移] ", key_state)
    if key_state["current_index"] != 2 or key_state["last_action"] != 3:
        raise RuntimeError("面包屑键盘选择失败")

    ui.set_breadcrumb_separator(hwnd, g_breadcrumb_id, " / ")
    ui.set_breadcrumb_items(hwnd, g_breadcrumb_id, ["🏠 首页", "📊 数据中心", "✅ 当前页面"])
    reset_state = ui.get_breadcrumb_full_state(hwnd, g_breadcrumb_id)
    print("[更新项目] ", reset_state)
    if reset_state["item_count"] != 3 or reset_state["current_index"] != 2:
        raise RuntimeError("面包屑项目更新失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("面包屑完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    while running and time.time() - start < 60:
        running = pump_messages(user32, msg, 0.05)

    print("面包屑完整组件示例结束。")


if __name__ == "__main__":
    main()
