import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_clicks = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 按钮完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_button_click(element_id):
    g_clicks.append(element_id)
    print(f"[按钮回调] 元素={element_id}")


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


def click_at(user32, hwnd, x, y):
    user32.SendMessageW(hwnd, 0x0201, 0x0001, make_lparam(x, y))  # WM_LBUTTONDOWN
    user32.SendMessageW(hwnd, 0x0202, 0, make_lparam(x, y))       # WM_LBUTTONUP


def logical_point(hwnd, x, y):
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    scale = dpi / 96.0 if dpi else 1.0
    titlebar_h = int(round(30 * scale))
    return int(round(x * scale)), titlebar_h + int(round(y * scale))


def click_logical_rect(user32, hwnd, x, y, w, h):
    px, py = logical_point(hwnd, x + w / 2.0, y + h / 2.0)
    click_at(user32, hwnd, px, py)


def require_options(hwnd, element_id, expected):
    state = ui.get_button_options(hwnd, element_id)
    print("[按钮选项]", element_id, state)
    if state is None:
        raise RuntimeError("按钮选项读回失败")
    for key, value in expected.items():
        if state[key] != value:
            raise RuntimeError(f"按钮选项 {key} 预期 {value}，实际 {state[key]}")
    return state


def main():
    global g_hwnd

    hwnd = ui.create_window("🚀 Button 按钮完整组件验证", 220, 80, 1120, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1080, 700)

    ui.create_text(hwnd, content_id, "🚀 Button 按钮完整封装", 34, 26, 520, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证默认/主要/成功/信息/警告/危险/文字、朴素、圆角、圆形、加载中、尺寸、禁用、鼠标和键盘交互。",
        34, 76, 920, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    labels = [
        ("默认按钮", "⚪", 0),
        ("主要按钮", "🚀", 1),
        ("成功按钮", "✅", 2),
        ("信息按钮", "💬", 6),
        ("警告按钮", "⚠️", 3),
        ("危险按钮", "🧯", 4),
    ]
    x0 = 50
    y0 = 150
    buttons = []
    for row, (caption, plain, rounded, disabled) in enumerate([
        ("基础按钮", False, False, False),
        ("朴素按钮", True, False, False),
        ("圆角按钮", False, True, False),
        ("禁用按钮", False, False, True),
    ]):
        ui.create_text(hwnd, content_id, caption, x0, y0 + row * 56 + 8, 110, 28)
        for i, (text, emoji, variant) in enumerate(labels):
            btn = ui.create_button(
                hwnd, content_id, emoji, text,
                x0 + 126 + i * 150, y0 + row * 56, 126, 38,
                variant=variant, plain=plain, round=rounded,
            )
            if disabled:
                ui.set_element_enabled(hwnd, btn, False)
            buttons.append(btn)

    circle_id = ui.create_button(hwnd, content_id, "🔎", "", 176, 402, 44, 44, variant=1, circle=True)
    text_id = ui.create_button(hwnd, content_id, "", "文字按钮", 248, 406, 100, 34, variant=5)
    loading_id = ui.create_button(hwnd, content_id, "⏳", "加载中", 378, 402, 128, 40, variant=1, loading=True)
    small_id = ui.create_button(hwnd, content_id, "📏", "小型按钮", 540, 406, 104, 32, variant=2, size=2, round=True)
    mini_id = ui.create_button(hwnd, content_id, "📐", "超小按钮", 670, 408, 96, 28, variant=6, size=3, plain=True)

    ui.create_text(hwnd, content_id, "⭕ 圆形  |  📝 文字  |  ⏳ 加载  |  📏 尺寸", 50, 462, 720, 32)
    normal_click_id = ui.create_button(hwnd, content_id, "✅", "鼠标点击测试", 50, 520, 160, 42, variant=1)
    keyboard_id = ui.create_button(hwnd, content_id, "⌨️", "键盘触发测试", 236, 520, 170, 42, variant=2)
    loading_click_id = ui.create_button(hwnd, content_id, "⏳", "加载中不可点", 432, 520, 170, 42, variant=1, loading=True)
    for eid in (normal_click_id, keyboard_id, loading_click_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_button_click)

    require_options(hwnd, buttons[1], {"variant": 1, "plain": False, "round": False, "circle": False, "loading": False, "size": 0})
    require_options(hwnd, buttons[6 + 3], {"variant": 6, "plain": True, "round": False, "circle": False, "loading": False, "size": 0})
    require_options(hwnd, circle_id, {"variant": 1, "plain": False, "round": False, "circle": True, "loading": False, "size": 0})
    require_options(hwnd, loading_id, {"variant": 1, "plain": False, "round": False, "circle": False, "loading": True, "size": 0})
    require_options(hwnd, small_id, {"variant": 2, "plain": False, "round": True, "circle": False, "loading": False, "size": 2})
    require_options(hwnd, mini_id, {"variant": 6, "plain": True, "round": False, "circle": False, "loading": False, "size": 3})

    state = ui.get_button_state(hwnd, text_id)
    if state is None or state[2] != 5:
        raise RuntimeError("文字按钮旧状态接口读回失败")
    if ui.get_element_enabled(hwnd, buttons[-1]):
        raise RuntimeError("禁用按钮通用状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.2)

    click_logical_rect(user32, hwnd, 50, 520, 160, 42)
    pump_messages(user32, msg, 0.25)
    if normal_click_id not in g_clicks:
        raise RuntimeError("鼠标点击回调未触发")

    ui.dll.EU_SetElementFocus(hwnd, keyboard_id)
    user32.PostMessageW(hwnd, 0x0100, 0x0D, 0)  # WM_KEYDOWN VK_RETURN
    user32.PostMessageW(hwnd, 0x0101, 0x0D, 0)  # WM_KEYUP VK_RETURN
    pump_messages(user32, msg, 0.25)
    if keyboard_id not in g_clicks:
        raise RuntimeError("键盘触发按钮回调失败")

    before = len(g_clicks)
    click_logical_rect(user32, hwnd, 432, 520, 170, 42)
    pump_messages(user32, msg, 0.25)
    if len(g_clicks) != before:
        raise RuntimeError("加载中按钮不应触发点击回调")

    ui.set_button_options(hwnd, loading_click_id, variant=1, plain=False, round=False,
                          circle=False, loading=False, size=0)
    require_options(hwnd, loading_click_id, {"variant": 1, "plain": False, "round": False, "circle": False, "loading": False, "size": 0})
    click_logical_rect(user32, hwnd, 432, 520, 170, 42)
    pump_messages(user32, msg, 0.25)
    if loading_click_id not in g_clicks:
        raise RuntimeError("取消加载后按钮点击未恢复")

    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、全套按钮样式和首次窗口尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
