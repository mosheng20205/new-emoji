import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_events = []
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
MK_LBUTTON = 0x0001
VK_CONTROL = 0x11
VK_LEFT = 0x25
VK_HOME = 0x24
KEYEVENTF_KEYUP = 0x0002


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] MessageBox 完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.MessageBoxExCallback
def on_messagebox_ex(messagebox_id, action, value_ptr, value_len):
    value = ""
    if value_ptr and value_len > 0:
        value = ctypes.string_at(value_ptr, value_len).decode("utf-8", errors="replace")
    g_events.append((messagebox_id, action, value))
    print(f"[消息框回调] 元素={messagebox_id} 动作={action} 输入={value}")


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


def press_key(hwnd, user32, vk):
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 0)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, 0)


def post_text(hwnd, user32, msg, text):
    for ch in text:
        user32.PostMessageW(hwnd, WM_CHAR, ord(ch), 0)
    pump_messages(user32, msg, 0.08)


def make_lparam(x, y):
    return (y & 0xFFFF) << 16 | (x & 0xFFFF)


def click_prompt_input(hwnd, user32, msg):
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    dpi = user32.GetDpiForWindow(hwnd) if hasattr(user32, "GetDpiForWindow") else 96
    scale = dpi / 96.0 if dpi else 1.0
    width = round((rect.right - rect.left) * scale)
    height = round((rect.bottom - rect.top) * scale)
    margin = round(24 * scale)
    dialog_w = round(420 * scale)
    dialog_h = round(284 * scale)
    min_w = round(280 * scale)
    max_w = width - margin * 2
    if max_w < min_w:
        max_w = width if width > 0 else min_w
    if max_w < dialog_w:
        dialog_w = max_w
    if dialog_w < min_w and width >= min_w:
        dialog_w = min_w
    if dialog_w > width:
        dialog_w = width
    max_h = height - margin * 2
    if 0 < max_h < dialog_h:
        dialog_h = max_h
    if dialog_h > height:
        dialog_h = height
    dialog_x = max(0, (width - dialog_w) // 2)
    dialog_y = max(0, (height - dialog_h) // 2)
    input_x = dialog_x + round(20 * scale)
    input_y = dialog_y + dialog_h - round(20 * scale) - round(32 * scale) - round(62 * scale)
    x = input_x + round(12 * scale)
    y = input_y + round(17 * scale)
    user32.SendMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, make_lparam(x, y))
    user32.SendMessageW(hwnd, WM_LBUTTONUP, 0, make_lparam(x, y))
    pump_messages(user32, msg, 0.08)


def press_ctrl_key(hwnd, user32, msg, vk):
    user32.SetForegroundWindow(hwnd)
    pump_messages(user32, msg, 0.05)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.03)
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 0)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, 0)
    pump_messages(user32, msg, 0.08)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    pump_messages(user32, msg, 0.05)


def main():
    hwnd = ui.create_window("🪟 MessageBox 消息框完整验证", 260, 90, 920, 680)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 620)
    ui.create_text(hwnd, content_id, "🪟 MessageBox 消息框流程", 28, 28, 560, 38)
    ui.create_text(
        hwnd, content_id,
        "验证 alert、confirm、prompt、通用 msgbox、HTML、居中、区分关闭、loading 延迟关闭和输入校验。",
        28, 76, 800, 56,
    )

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    ui.dll.EU_ShowWindow(hwnd, 1)

    alert_id = ui.show_alert_box(
        hwnd,
        "📌 HTML 片段",
        "<strong>这是 <i>HTML</i> 片段</strong>",
        confirm="确定 ✅",
        center=True,
        rich=True,
        callback=on_messagebox_ex,
    )
    state = ui.get_messagebox_full_state(hwnd, alert_id)
    if state["center"] != 1 or state["rich"] != 1 or state["show_cancel"] != 0:
        raise RuntimeError(f"Alert 状态失败: {state}")
    ui.dll.EU_SetElementFocus(hwnd, alert_id)
    press_key(hwnd, user32, 0x0D)
    pump_messages(user32, msg, 0.25)

    confirm_id = ui.show_confirm_box(
        hwnd,
        "⚠️ 确认信息",
        "检测到未保存的内容，是否在离开页面前保存修改？",
        confirm="保存 ✅",
        cancel="放弃修改",
        box_type=2,
        center=True,
        distinguish_cancel_and_close=True,
        callback=on_messagebox_ex,
    )
    confirm_state = ui.get_messagebox_full_state(hwnd, confirm_id)
    if confirm_state["box_type"] != 2 or confirm_state["distinguish"] != 1:
        raise RuntimeError(f"Confirm 状态失败: {confirm_state}")
    ui.dll.EU_SetElementFocus(hwnd, confirm_id)
    press_key(hwnd, user32, 0x1B)
    pump_messages(user32, msg, 0.25)

    prompt_id = ui.show_prompt_box(
        hwnd,
        "📧 输入邮箱",
        "请输入邮箱地址",
        placeholder="name@example.com",
        value="bad-email",
        pattern=r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?",
        error="邮箱格式不正确",
        callback=on_messagebox_ex,
    )
    ui.dll.EU_SetElementFocus(hwnd, prompt_id)
    press_key(hwnd, user32, 0x0D)
    pump_messages(user32, msg, 0.2)
    invalid_state = ui.get_messagebox_full_state(hwnd, prompt_id)
    if invalid_state["prompt"] != 1 or invalid_state["input_error_visible"] != 1:
        raise RuntimeError(f"Prompt 输入校验失败: {invalid_state}")
    ui.set_messagebox_input(
        hwnd, prompt_id,
        value="emoji@example.com",
        placeholder="name@example.com",
        pattern=r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?",
        error="邮箱格式不正确",
    )
    if ui.get_messagebox_input(hwnd, prompt_id) != "emoji@example.com":
        raise RuntimeError("Prompt 输入读回失败")

    ui.set_messagebox_input(hwnd, prompt_id, value="abc", placeholder="请输入内容", pattern="", error="")
    press_key(hwnd, user32, VK_LEFT)
    post_text(hwnd, user32, msg, "X")
    if ui.get_messagebox_input(hwnd, prompt_id) != "abXc":
        raise RuntimeError("Prompt 方向键光标移动失败")

    ui.set_messagebox_input(hwnd, prompt_id, value="abc", placeholder="请输入内容", pattern="", error="")
    click_prompt_input(hwnd, user32, msg)
    post_text(hwnd, user32, msg, "Z")
    mouse_value = ui.get_messagebox_input(hwnd, prompt_id)
    if mouse_value != "Zabc":
        raise RuntimeError(f"Prompt 鼠标点击定位光标失败: {mouse_value}")

    press_ctrl_key(hwnd, user32, msg, ord("A"))
    post_text(hwnd, user32, msg, "q")
    if ui.get_messagebox_input(hwnd, prompt_id) != "q":
        raise RuntimeError("Prompt Ctrl+A 全选失败")

    ui.set_messagebox_input(
        hwnd, prompt_id,
        value="emoji@example.com",
        placeholder="name@example.com",
        pattern=r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?",
        error="邮箱格式不正确",
    )
    press_key(hwnd, user32, 0x0D)
    pump_messages(user32, msg, 0.25)

    msgbox_id = ui.show_msgbox(
        hwnd,
        "🚀 消息",
        "内容可以是 <span style=\"color: teal\"><strong>VNode</strong></span>",
        confirm="执行 ✅",
        cancel="取消",
        box_type=0,
        show_cancel=True,
        rich=True,
        callback=on_messagebox_ex,
    )
    ui.set_messagebox_before_close(hwnd, msgbox_id, delay_ms=220, loading_text="执行中...")
    ui.dll.EU_SetElementFocus(hwnd, msgbox_id)
    press_key(hwnd, user32, 0x0D)
    pump_messages(user32, msg, 0.05)
    loading_state = ui.get_messagebox_full_state(hwnd, msgbox_id)
    if loading_state["confirm_loading"] != 1:
        raise RuntimeError(f"MessageBox loading 状态失败: {loading_state}")
    pump_messages(user32, msg, 0.35)

    actions = [event[1] for event in g_events]
    values = [event[2] for event in g_events]
    if 1 not in actions or -1 not in actions or "emoji@example.com" not in values:
        raise RuntimeError(f"MessageBox 回调动作或输入值不完整: {g_events}")

    print("[提示] MessageBox 验证窗口将保持 1 秒，可检查中文、emoji、HTML 和按钮 loading。")
    pump_messages(user32, msg, 1.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
