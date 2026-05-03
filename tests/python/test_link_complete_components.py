import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_clicks = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Link 完整组件验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_link_click(element_id):
    g_clicks.append(element_id)
    print(f"[链接回调] 元素={element_id}")


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


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


def logical_point(hwnd, x, y):
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    scale = dpi / 96.0 if dpi else 1.0
    titlebar_h = int(round(30 * scale))
    return int(round(x * scale)), titlebar_h + int(round(y * scale))


def send_mouse_move(user32, hwnd, x, y):
    px, py = logical_point(hwnd, x, y)
    user32.SendMessageW(hwnd, 0x0200, 0, make_lparam(px, py))  # WM_MOUSEMOVE


def click_logical_rect(user32, hwnd, x, y, w, h):
    px, py = logical_point(hwnd, x + w / 2.0, y + h / 2.0)
    user32.SendMessageW(hwnd, 0x0201, 0x0001, make_lparam(px, py))  # WM_LBUTTONDOWN
    user32.SendMessageW(hwnd, 0x0202, 0, make_lparam(px, py))       # WM_LBUTTONUP


def require_options(hwnd, element_id, expected):
    state = ui.get_link_options(hwnd, element_id)
    print("[链接选项]", element_id, state)
    if state is None:
        raise RuntimeError("链接选项读回失败")
    for key, value in expected.items():
        if state[key] != value:
            raise RuntimeError(f"链接选项 {key} 预期 {value}，实际 {state[key]}")
    return state


def require_content(hwnd, element_id, expected):
    state = ui.get_link_content(hwnd, element_id)
    print("[链接内容]", element_id, state)
    if state is None:
        raise RuntimeError("链接内容读回失败")
    for key, value in expected.items():
        if state[key] != value:
            raise RuntimeError(f"链接内容 {key} 预期 {value}，实际 {state[key]}")
    return state


def main():
    hwnd = ui.create_window("🔗 Link 链接完整组件验证", 220, 80, 1180, 760)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1140, 700)

    ui.create_text(hwnd, content, "🔗 Link 链接完整封装", 34, 26, 520, 40)
    intro = ui.create_text(
        hwnd, content,
        "验证默认/主要/成功/警告/危险/信息、禁用、下划线、前后缀图标、href/target、访问态和键鼠触发。",
        34, 76, 980, 54,
    )
    ui.set_text_options(hwnd, intro, align=0, valign=0, wrap=True, ellipsis=False)

    labels = [
        ("默认链接 🔗", 0),
        ("主要链接 🚀", 1),
        ("成功链接 ✅", 2),
        ("警告链接 ⚠️", 3),
        ("危险链接 🧯", 4),
        ("信息链接 💬", 5),
    ]
    links = []
    for i, (text, link_type) in enumerate(labels):
        link = ui.create_link(
            hwnd, content, text,
            50 + i * 170, 154, 140, 32,
            type=link_type,
            href="https://element.eleme.io",
            target="_blank",
        )
        links.append(link)

    for i, (text, link_type) in enumerate(labels):
        link = ui.create_link(
            hwnd, content, text,
            50 + i * 170, 210, 140, 32,
            type=link_type,
        )
        ui.set_element_enabled(hwnd, link, False)

    no_underline = ui.create_link(hwnd, content, "无下划线", 50, 286, 140, 32, underline=False)
    with_icon = ui.create_link(
        hwnd, content, "查看详情", 230, 286, 180, 32,
        type=1, prefix_icon="✏️", suffix_icon="👀",
        href="https://element.eleme.io", target="_blank",
    )
    auto_empty = ui.create_link(hwnd, content, "自动打开开关", 450, 286, 180, 32, type=5, auto_open=True)
    visited = ui.create_link(hwnd, content, "已访问链接", 670, 286, 160, 32, type=1, visited=True)
    disabled_click = ui.create_link(hwnd, content, "禁用点击", 870, 286, 160, 32, type=4)
    ui.set_element_enabled(hwnd, disabled_click, False)

    key_link = ui.create_link(hwnd, content, "键盘触发链接 ⌨️", 50, 370, 220, 36, type=2)
    mouse_link = links[1]
    for link in (mouse_link, key_link, disabled_click):
        ui.dll.EU_SetElementClickCallback(hwnd, link, on_link_click)

    require_options(hwnd, links[5], {"type": 5, "underline": True, "auto_open": False, "visited": False})
    require_options(hwnd, no_underline, {"type": 0, "underline": False, "auto_open": False, "visited": False})
    require_options(hwnd, auto_empty, {"type": 5, "underline": True, "auto_open": True, "visited": False})
    require_options(hwnd, visited, {"type": 1, "underline": True, "auto_open": False, "visited": True})
    require_content(hwnd, with_icon, {
        "prefix_icon": "✏️",
        "suffix_icon": "👀",
        "href": "https://element.eleme.io",
        "target": "_blank",
    })

    ui.set_link_visited(hwnd, visited, False)
    if ui.get_link_visited(hwnd, visited):
        raise RuntimeError("旧访问态接口设置/读回失败")
    require_options(hwnd, visited, {"visited": False})
    if ui.get_element_enabled(hwnd, disabled_click):
        raise RuntimeError("禁用链接通用状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.25)

    send_mouse_move(user32, hwnd, 50 + 170 + 70, 154 + 16)
    pump_messages(user32, msg, 0.15)
    click_logical_rect(user32, hwnd, 50 + 170, 154, 140, 32)
    pump_messages(user32, msg, 0.25)
    if mouse_link not in g_clicks:
        raise RuntimeError("鼠标点击链接未触发回调")
    require_options(hwnd, mouse_link, {"visited": True})

    ui.dll.EU_SetElementFocus(hwnd, key_link)
    user32.SendMessageW(hwnd, 0x0100, 0x0D, 0)  # WM_KEYDOWN VK_RETURN
    user32.SendMessageW(hwnd, 0x0101, 0x0D, 0)  # WM_KEYUP VK_RETURN
    pump_messages(user32, msg, 0.25)
    if key_link not in g_clicks:
        raise RuntimeError("键盘触发链接回调失败")

    before = len(g_clicks)
    click_logical_rect(user32, hwnd, 870, 286, 160, 32)
    pump_messages(user32, msg, 0.25)
    if len(g_clicks) != before:
        raise RuntimeError("禁用链接不应触发点击回调")

    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、链接类型、hover、下划线和访问态。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
