import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tabs_id = 0
g_add_button_id = 0
g_close_button_id = 0
g_scroll_button_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 标签页完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_tabs_change(element_id, value, item_count, action):
    g_events.append(("change", value, item_count, action))
    print(f"[标签页选择回调] 元素={element_id} 激活={value} 总数={item_count} 动作={action}")


@ui.ValueCallback
def on_tabs_close(element_id, value, item_count, active):
    g_events.append(("close", value, item_count, active))
    print(f"[标签页关闭回调] 元素={element_id} 关闭={value} 剩余={item_count} 激活={active}")


@ui.ValueCallback
def on_tabs_add(element_id, value, item_count, active):
    g_events.append(("add", value, item_count, active))
    print(f"[标签页新增回调] 元素={element_id} 新增={value} 总数={item_count} 激活={active}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_add_button_id:
        ui.add_tabs_item(g_hwnd, g_tabs_id, "✨ 手动新增")
        print("[按钮] 新增标签：", ui.get_tabs_full_state(g_hwnd, g_tabs_id))
    elif element_id == g_close_button_id:
        state = ui.get_tabs_full_state(g_hwnd, g_tabs_id)
        ui.close_tabs_item(g_hwnd, g_tabs_id, state["active_index"])
        print("[按钮] 关闭当前：", ui.get_tabs_full_state(g_hwnd, g_tabs_id))
    elif element_id == g_scroll_button_id:
        ui.tabs_scroll(g_hwnd, g_tabs_id, 180)
        print("[按钮] 滚动标签：", ui.get_tabs_full_state(g_hwnd, g_tabs_id))


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
    global g_hwnd, g_tabs_id, g_add_button_id, g_close_button_id, g_scroll_button_id

    hwnd = ui.create_window("🧭 标签页完整组件验证", 220, 80, 1000, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 620)

    ui.create_text(hwnd, content_id, "🧭 Tabs 标签页完整封装", 28, 24, 520, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证关闭标签、新增标签、溢出滚动、滚轮/键盘导航、选择/关闭/新增回调、项目文本和完整状态读回。",
        28, 72, 860, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_tabs_id = ui.create_tabs(
        hwnd,
        content_id,
        [
            "🏠 总览", "📊 数据", "🧪 实验", "🎨 主题", "🔔 通知",
            "📁 文件", "🛡️ 权限", "⚙️ 设置", "✨ 洞察",
        ],
        1,
        1,
        46,
        152,
        800,
        48,
    )
    ui.set_tabs_options(hwnd, g_tabs_id, tab_type=1, closable=True, addable=True)
    ui.set_tabs_change_callback(hwnd, g_tabs_id, on_tabs_change)
    ui.set_tabs_close_callback(hwnd, g_tabs_id, on_tabs_close)
    ui.set_tabs_add_callback(hwnd, g_tabs_id, on_tabs_add)

    ui.create_infobox(
        hwnd,
        content_id,
        "✅ 验证提示",
        "标签栏右侧有新增按钮，标签内有关闭按钮；项目较多会横向溢出，可用滚轮、Page 键或下方按钮滚动。",
        46,
        236,
        800,
        92,
    )

    g_scroll_button_id = ui.create_button(hwnd, content_id, "➡️", "滚动标签", 46, 374, 140, 42)
    g_add_button_id = ui.create_button(hwnd, content_id, "➕", "新增标签", 210, 374, 140, 42)
    g_close_button_id = ui.create_button(hwnd, content_id, "✖️", "关闭当前", 374, 374, 140, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_scroll_button_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_add_button_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_close_button_id, on_click)

    initial = ui.get_tabs_full_state(hwnd, g_tabs_id)
    print("[初始状态]", initial)
    if not initial or initial["active_index"] != 1 or initial["item_count"] != 9:
        raise RuntimeError("标签页初始状态读回失败")
    if initial["closable"] != 1 or initial["addable"] != 1 or initial["max_scroll_offset"] <= 0:
        raise RuntimeError("标签页选项或溢出滚动状态读回失败")
    if "总览" not in ui.get_tabs_item(hwnd, g_tabs_id, 0):
        raise RuntimeError("标签页项目文本读回失败")

    ui.tabs_scroll(hwnd, g_tabs_id, 160)
    scrolled = ui.get_tabs_full_state(hwnd, g_tabs_id)
    print("[程序滚动]", scrolled)
    if scrolled["scroll_offset"] <= 0 or scrolled["scroll_count"] < 1 or scrolled["last_action"] != 6:
        raise RuntimeError("标签页程序滚动失败")

    ui.add_tabs_item(hwnd, g_tabs_id, "✨ 新增洞察")
    added = ui.get_tabs_full_state(hwnd, g_tabs_id)
    print("[程序新增]", added)
    if added["item_count"] != 10 or added["add_count"] < 1 or added["last_added_index"] != 9:
        raise RuntimeError("标签页新增状态读回失败")
    if "新增洞察" not in ui.get_tabs_item(hwnd, g_tabs_id, 9):
        raise RuntimeError("标签页新增项目文本读回失败")
    if not any(event[0] == "add" for event in g_events):
        raise RuntimeError("标签页新增回调未触发")

    ui.close_tabs_item(hwnd, g_tabs_id, 2)
    closed = ui.get_tabs_full_state(hwnd, g_tabs_id)
    print("[程序关闭]", closed)
    if closed["item_count"] != 9 or closed["close_count"] < 1 or closed["last_closed_index"] != 2:
        raise RuntimeError("标签页关闭状态读回失败")
    if not any(event[0] == "close" for event in g_events):
        raise RuntimeError("标签页关闭回调未触发")

    ui.set_tabs_active(hwnd, g_tabs_id, 4)
    selected = ui.get_tabs_full_state(hwnd, g_tabs_id)
    print("[程序选择]", selected)
    if selected["active_index"] != 4 or selected["select_count"] < 1:
        raise RuntimeError("标签页选择状态读回失败")
    if not any(event[0] == "change" for event in g_events):
        raise RuntimeError("标签页选择回调未触发")

    ui.dll.EU_SetElementFocus(hwnd, g_tabs_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)
    pump_messages(user32, msg, 0.25)
    key_state = ui.get_tabs_full_state(hwnd, g_tabs_id)
    print("[键盘右移]", key_state)
    if key_state["active_index"] != 5 or key_state["last_action"] != 3:
        raise RuntimeError("标签页键盘导航失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("标签页完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    auto_clicked = False
    while running and time.time() - start < 60:
        if not auto_clicked and time.time() - start > 1.0:
            on_click(g_scroll_button_id)
            auto_clicked = True
        running = pump_messages(user32, msg, 0.05)

    print("标签页完整组件示例结束。")


if __name__ == "__main__":
    main()
