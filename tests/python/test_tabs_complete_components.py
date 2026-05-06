import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tabs_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_tabs_change(element_id, value, item_count, action):
    g_events.append(("change", value, item_count, action))


@ui.ValueCallback
def on_tabs_close(element_id, value, item_count, active):
    g_events.append(("close", value, item_count, active))


@ui.ValueCallback
def on_tabs_add(element_id, value, item_count, active):
    g_events.append(("add", value, item_count, active))


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


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    global g_hwnd, g_tabs_id

    hwnd = ui.create_window("📑 标签页完整样式验证", 220, 80, 1180, 820)
    assert_state(hwnd, "窗口创建失败")
    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1140, 760)

    items = [
        {"label": "用户管理", "name": "users", "content": "👥 用户管理内容", "icon": "👥"},
        {"label": "配置管理", "name": "config", "content": "⚙️ 配置管理内容", "icon": "⚙️"},
        {"label": "角色管理", "name": "roles", "content": "🛡️ 角色管理内容", "icon": "🛡️"},
        {"label": "定时任务补偿", "name": "jobs", "content": "⏰ 定时任务补偿内容", "icon": "⏰"},
        {"label": "禁用页", "name": "locked", "content": "🔒 禁用内容", "icon": "🔒", "disabled": True, "closable": False},
    ]

    ui.create_tabs_ex(hwnd, root, items, active=0, tab_type=0, tab_position="top",
                      content_visible=True, x=36, y=34, w=520, h=132)
    ui.create_tabs_ex(hwnd, root, items, active=1, tab_type=1, tab_position="top",
                      content_visible=True, x=590, y=34, w=520, h=132)
    ui.create_tabs_ex(hwnd, root, items, active=2, tab_type=2, tab_position="top",
                      closable=True, content_visible=True, x=36, y=200, w=1074, h=150)
    ui.create_tabs_ex(hwnd, root, items, active=0, tab_type=2, tab_position="left",
                      content_visible=True, x=36, y=386, w=340, h=220)
    ui.create_tabs_ex(hwnd, root, items, active=1, tab_type=2, tab_position="right",
                      content_visible=True, x=406, y=386, w=340, h=220)
    ui.create_tabs_ex(hwnd, root, items, active=2, tab_type=1, tab_position="bottom",
                      content_visible=True, x=776, y=386, w=334, h=220)

    g_tabs_id = ui.create_tabs_ex(
        hwnd, root, items, active=1, tab_type=1, tab_position="top",
        closable=True, addable=True, editable=True, content_visible=True,
        x=36, y=640, w=840, h=92,
    )
    ui.set_tabs_change_callback(hwnd, g_tabs_id, on_tabs_change)
    ui.set_tabs_close_callback(hwnd, g_tabs_id, on_tabs_close)
    ui.set_tabs_add_callback(hwnd, g_tabs_id, on_tabs_add)

    initial = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(initial["tab_type"] == 1, "卡片类型读回失败")
    assert_state(initial["tab_position"] == 0, "顶部位置读回失败")
    assert_state(initial["closable"] == 1 and initial["addable"] == 1 and initial["editable"] == 1, "editable 选项读回失败")
    assert_state(initial["content_visible"] == 1 and initial["item_count"] == 5, "内容区或项目数读回失败")
    assert_state(ui.get_tabs_active_name(hwnd, g_tabs_id) == "config", "active name 初始读回失败")
    assert_state("配置管理" in ui.get_tabs_item_content(hwnd, g_tabs_id, 1), "内容文本读回失败")

    ui.set_tabs_active_name(hwnd, g_tabs_id, "roles")
    by_name = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(by_name["active_index"] == 2 and ui.get_tabs_active_name(hwnd, g_tabs_id) == "roles", "按 name 激活失败")

    ui.set_tabs_position(hwnd, g_tabs_id, "left")
    left_state = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(left_state["tab_position"] == 3, "左侧位置设置失败")

    ui.set_tabs_header_align(hwnd, g_tabs_id, "center")
    assert_state(ui.get_tabs_header_align(hwnd, g_tabs_id) == 1, "表头居中对齐设置失败")
    ui.set_tabs_header_align(hwnd, g_tabs_id, "right")
    assert_state(ui.get_tabs_header_align(hwnd, g_tabs_id) == 2, "表头右对齐设置失败")
    ui.set_tabs_header_align(hwnd, g_tabs_id, "left")
    assert_state(ui.get_tabs_header_align(hwnd, g_tabs_id) == 0, "表头左对齐恢复失败")

    ui.set_tabs_type(hwnd, g_tabs_id, 2)
    border_state = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(border_state["tab_type"] == 2, "边框卡片类型设置失败")

    ui.tabs_scroll(hwnd, g_tabs_id, 120)
    scrolled = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(scrolled["last_action"] == 6, "程序滚动状态读回失败")

    ui.add_tabs_item(hwnd, g_tabs_id, "✨ 新增洞察")
    added = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(added["item_count"] == 6 and added["add_count"] >= 1, "新增标签失败")
    assert_state(any(event[0] == "add" for event in g_events), "新增回调未触发")

    ui.close_tabs_item(hwnd, g_tabs_id, 0)
    closed = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(closed["item_count"] == 5 and closed["close_count"] >= 1, "关闭标签失败")
    assert_state(any(event[0] == "close" for event in g_events), "关闭回调未触发")

    ui.set_tabs_active(hwnd, g_tabs_id, 2)
    selected = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(selected["active_index"] == 2 and any(event[0] == "change" for event in g_events), "索引选择或回调失败")

    user32 = ctypes.windll.user32
    user32.SetFocus.argtypes = [wintypes.HWND]
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    msg = wintypes.MSG()
    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(user32, msg, 0.2)
    ui.dll.EU_SetElementFocus(hwnd, g_tabs_id)
    user32.SetFocus(hwnd)
    user32.SendMessageW(hwnd, 0x0100, 0x26, 0)  # VK_UP for left tabs
    pump_messages(user32, msg, 0.25)
    key_state = ui.get_tabs_full_state_ex(hwnd, g_tabs_id)
    assert_state(key_state["last_action"] == 3, f"纵向键盘导航失败：{key_state}")

    pump_messages(user32, msg, 1.0)
    ui.dll.EU_DestroyWindow(hwnd)
    print("📑 Tabs 完整样式组件验证通过")


if __name__ == "__main__":
    main()
