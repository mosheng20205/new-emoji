import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_alert_id = 0
g_close_button_id = 0
g_reopen_button_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 警告提示完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_alert_close(element_id, close_count, alert_type, action):
    g_events.append((close_count, alert_type, action))
    print(f"[警告关闭回调] 元素={element_id} 次数={close_count} 类型={alert_type} 动作={action}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_close_button_id:
        ui.trigger_alert_close(g_hwnd, g_alert_id)
        print("[按钮] 程序关闭：", ui.get_alert_full_state(g_hwnd, g_alert_id))
    elif element_id == g_reopen_button_id:
        ui.set_alert_closed(g_hwnd, g_alert_id, False)
        ui.set_alert_type(g_hwnd, g_alert_id, 2)
        ui.set_alert_effect(g_hwnd, g_alert_id, 1)
        print("[按钮] 重新显示：", ui.get_alert_full_state(g_hwnd, g_alert_id))


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
    global g_hwnd, g_alert_id, g_close_button_id, g_reopen_button_id

    hwnd = ui.create_window("🚨 警告提示完整组件验证", 220, 80, 920, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 560)

    ui.create_text(hwnd, content_id, "🚨 Alert 警告提示完整封装", 28, 24, 560, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证类型/效果/描述/可关闭状态、鼠标与键盘关闭、程序触发关闭、关闭回调和完整状态读回。",
        28, 72, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_alert_id = ui.create_alert(
        hwnd,
        content_id,
        title="✅ 操作已完成",
        description="这是一条支持 emoji、中文说明、关闭回调和状态读回的警告提示。",
        alert_type=1,
        effect=0,
        closable=True,
        x=46,
        y=150,
        w=760,
        h=82,
    )
    ui.set_alert_close_callback(hwnd, g_alert_id, on_alert_close)

    ui.create_alert(
        hwnd,
        content_id,
        title="⚠️ 请注意",
        description="深色效果和不同类型颜色会一起适配主题。",
        alert_type=2,
        effect=1,
        closable=False,
        x=46,
        y=258,
        w=760,
        h=72,
    )

    g_close_button_id = ui.create_button(hwnd, content_id, "✖️", "程序关闭", 46, 382, 140, 42)
    g_reopen_button_id = ui.create_button(hwnd, content_id, "🔄", "重新显示", 210, 382, 140, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_close_button_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reopen_button_id, on_click)

    initial = ui.get_alert_full_state(hwnd, g_alert_id)
    print("[初始状态]", initial)
    if not initial or initial["alert_type"] != 1 or initial["closable"] != 1 or initial["closed"] != 0:
        raise RuntimeError("警告提示初始状态读回失败")

    ui.set_alert_description(hwnd, g_alert_id, "✅ 已更新描述：关闭事件和完整状态都能读回。")
    ui.set_alert_type(hwnd, g_alert_id, 3)
    updated = ui.get_alert_full_state(hwnd, g_alert_id)
    print("[更新状态]", updated)
    if updated["alert_type"] != 3 or updated["last_action"] != 1:
        raise RuntimeError("警告提示类型更新失败")

    ui.trigger_alert_close(hwnd, g_alert_id)
    closed = ui.get_alert_full_state(hwnd, g_alert_id)
    print("[程序关闭]", closed)
    if closed["closed"] != 1 or closed["close_count"] != 1 or closed["last_action"] != 4:
        raise RuntimeError("警告提示程序关闭失败")
    if not g_events or g_events[-1][2] != 4:
        raise RuntimeError("警告提示关闭回调失败")

    ui.set_alert_closed(hwnd, g_alert_id, False)
    reopened = ui.get_alert_full_state(hwnd, g_alert_id)
    if reopened["closed"] != 0:
        raise RuntimeError("警告提示重新显示失败")

    ui.dll.EU_SetElementFocus(hwnd, g_alert_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)
    pump_messages(user32, msg, 0.25)
    key_closed = ui.get_alert_full_state(hwnd, g_alert_id)
    print("[键盘关闭]", key_closed)
    if key_closed["closed"] != 1 or key_closed["last_action"] != 3:
        raise RuntimeError("警告提示键盘关闭失败")
    ui.set_alert_closed(hwnd, g_alert_id, False)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("警告提示完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    auto_clicked = False
    while running and time.time() - start < 60:
        if not auto_clicked and time.time() - start > 1.0:
            on_click(g_reopen_button_id)
            auto_clicked = True
        running = pump_messages(user32, msg, 0.05)

    print("警告提示完整组件示例结束。")


if __name__ == "__main__":
    main()
