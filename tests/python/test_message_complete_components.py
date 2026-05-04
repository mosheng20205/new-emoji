import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Message 完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_message_close(element_id, close_count, message_type, action):
    g_events.append((element_id, close_count, message_type, action))
    print(f"[消息关闭回调] 元素={element_id} 次数={close_count} 类型={message_type} 动作={action}")


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
    hwnd = ui.create_window("💬 Message 消息提示完整验证", 260, 100, 900, 620)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 860, 560)
    ui.create_text(hwnd, content_id, "💬 Message 消息提示", 28, 28, 520, 38)
    ui.create_text(
        hwnd, content_id,
        "验证普通消息、四种类型、可关闭、居中、轻量 HTML、自动关闭、堆叠和关闭回调。",
        28, 76, 760, 48,
    )

    m_info = ui.message_info(hwnd, "ℹ️ 这是一条普通消息提示", closable=True, duration_ms=0, offset=24)
    m_success = ui.message_success(hwnd, "✅ 恭喜你，这是一条成功消息", closable=True, duration_ms=0, offset=24)
    m_warning = ui.message_warning(hwnd, "⚠️ 警告哦，这是一条警告消息", center=True, duration_ms=450, offset=24)
    m_error = ui.message_error(
        hwnd,
        "❌ 内容可以是 <span style=\"color: teal\"><strong>VNode</strong></span> 等价富文本",
        closable=True,
        rich=True,
        duration_ms=0,
        offset=24,
    )

    for mid in (m_info, m_success, m_warning, m_error):
        if mid <= 0:
            raise RuntimeError("Message 创建失败")
        ui.set_message_close_callback(hwnd, mid, on_message_close)

    state_error = ui.get_message_full_state(hwnd, m_error)
    print("[富文本错误消息]", state_error)
    if state_error["message_type"] != 3 or state_error["rich"] != 1 or state_error["stack_index"] < 3:
        raise RuntimeError("Message 富文本或堆叠状态失败")

    ui.set_message_text(hwnd, m_success, "✅ 成功消息已更新：支持 SetText")
    ui.set_message_options(hwnd, m_success, message_type=1, closable=True, center=True, rich=False, duration_ms=0, offset=28)
    options = ui.get_message_options(hwnd, m_success)
    if options[:5] != (1, 1, 1, 0, 0):
        raise RuntimeError(f"Message Options 读回失败: {options}")

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(user32, msg, 0.65)

    warning_state = ui.get_message_full_state(hwnd, m_warning)
    print("[自动关闭后]", warning_state)
    if warning_state["closed"] != 1 or warning_state["last_action"] != 5:
        raise RuntimeError("Message 自动关闭失败")

    ui.trigger_message_close(hwnd, m_info)
    info_state = ui.get_message_full_state(hwnd, m_info)
    if info_state["closed"] != 1 or info_state["last_action"] != 4:
        raise RuntimeError("Message 程序关闭失败")

    actions = [event[3] for event in g_events]
    if 5 not in actions or 4 not in actions:
        raise RuntimeError("Message 关闭回调动作不完整")

    ui.set_message_closed(hwnd, m_info, False)
    reopened = ui.get_message_full_state(hwnd, m_info)
    if reopened["closed"] != 0:
        raise RuntimeError("Message 重新显示失败")

    print("[提示] Message 验证窗口将保持 1 秒，可检查中文、emoji、居中和富文本效果。")
    pump_messages(user32, msg, 1.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
