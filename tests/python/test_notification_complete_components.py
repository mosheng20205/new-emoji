import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 通知完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_notification_close(element_id, close_count, notify_type, action):
    g_events.append((element_id, close_count, notify_type, action))
    print(f"[通知关闭回调] 元素={element_id} 次数={close_count} 类型={notify_type} 动作={action}")


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
    global g_hwnd

    hwnd = ui.create_window("🔔 通知完整组件验证", 220, 80, 960, 700)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 640)

    ui.create_text(hwnd, content_id, "🔔 Notification 通知完整封装", 30, 24, 660, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证自动关闭定时器、堆叠布局、关闭回调、鼠标/键盘/程序关闭、文本读回和完整状态读回。",
        30, 70, 840, 52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    n1 = ui.create_notification(
        hwnd, content_id,
        title="✅ 保存成功",
        body="中文和 emoji 正常显示，通知支持程序关闭和状态读回。",
        notify_type=1,
        closable=True,
        x=80,
        y=140,
        w=720,
        h=96,
    )
    n2 = ui.create_notification(
        hwnd, content_id,
        title="⚠️ 需要确认",
        body="这一条被堆叠到第二层，用键盘 Enter 关闭。",
        notify_type=2,
        closable=True,
        x=80,
        y=140,
        w=720,
        h=96,
    )
    n3 = ui.create_notification(
        hwnd, content_id,
        title="⏱️ 自动关闭",
        body="这条通知会由内部定时器自动关闭，并触发关闭回调。",
        notify_type=0,
        closable=True,
        x=80,
        y=140,
        w=720,
        h=96,
    )

    for idx, nid in enumerate((n1, n2, n3)):
        ui.set_notification_stack(hwnd, nid, idx, 14)
        ui.set_notification_close_callback(hwnd, nid, on_notification_close)

    ui.set_notification_options(hwnd, n3, notify_type=0, closable=True, duration_ms=700)
    ui.create_text(hwnd, content_id, "📚 三条通知按堆叠索引自动错开；第三条会先自动关闭。", 90, 482, 720, 34)
    ui.create_button(hwnd, content_id, "🔁", "程序关闭第一条", 90, 534, 170, 42)
    ui.create_button(hwnd, content_id, "⌨️", "键盘关闭第二条", 286, 534, 180, 42)

    if "保存成功" not in ui.get_notification_text(hwnd, n1, 0):
        raise RuntimeError("通知标题读回失败")
    if "程序关闭" not in ui.get_notification_text(hwnd, n1, 1):
        raise RuntimeError("通知正文读回失败")

    state1 = ui.get_notification_full_state(hwnd, n1)
    state2 = ui.get_notification_full_state(hwnd, n2)
    state3 = ui.get_notification_full_state(hwnd, n3)
    print("[初始状态]", state1, state2, state3)
    if state2["stack_index"] != 1 or state3["duration_ms"] != 700 or state3["timer_running"] != 1:
        raise RuntimeError("通知堆叠或定时器状态失败")

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 1.0)
    auto_state = ui.get_notification_full_state(hwnd, n3)
    print("[自动关闭后]", auto_state)
    if auto_state["closed"] != 1 or auto_state["close_count"] != 1 or auto_state["last_action"] != 5:
        raise RuntimeError("通知自动关闭定时器失败")

    ui.trigger_notification_close(hwnd, n1)
    triggered = ui.get_notification_full_state(hwnd, n1)
    print("[程序关闭]", triggered)
    if triggered["closed"] != 1 or triggered["close_count"] != 1 or triggered["last_action"] != 4:
        raise RuntimeError("通知程序关闭失败")

    ui.dll.EU_SetElementFocus(hwnd, n2)
    user32.PostMessageW(hwnd, 0x0100, 0x0D, 0)  # VK_RETURN
    pump_messages(user32, msg, 0.25)
    keyed = ui.get_notification_full_state(hwnd, n2)
    print("[键盘关闭]", keyed)
    if keyed["closed"] != 1 or keyed["close_count"] != 1 or keyed["last_action"] != 3:
        raise RuntimeError("通知键盘关闭失败")

    actions = [event[3] for event in g_events]
    if 5 not in actions or 4 not in actions or 3 not in actions:
        raise RuntimeError("通知关闭回调动作来源不完整")

    ui.set_notification_closed(hwnd, n1, False)
    ui.set_notification_body(hwnd, n1, "🔔 已重新显示：状态、正文和主题绘制仍保持同步。")
    ui.set_notification_type(hwnd, n1, 3)
    reopened = ui.get_notification_full_state(hwnd, n1)
    if reopened["closed"] != 0 or reopened["notify_type"] != 3:
        raise RuntimeError("通知重新显示或类型更新失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、堆叠位置、进度条和尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
