import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 文字提示完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


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
    hwnd = ui.create_window("💡 文字提示完整组件验证", 220, 80, 920, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 560)
    ui.create_text(hwnd, content_id, "💡 Tooltip 文字提示完整封装", 30, 24, 640, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证箭头绘制、显示/隐藏延迟、焦点触发、键盘关闭、手动触发、文本读回和完整状态读回。",
        30,
        72,
        820,
        56,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    tip_id = ui.create_tooltip(
        hwnd,
        content_id,
        label="聚焦查看提示 ✨",
        content="💡 焦点触发后延迟显示，支持中文和 emoji。",
        placement=2,
        x=84,
        y=176,
        w=190,
        h=42,
    )
    ui.set_tooltip_behavior(hwnd, tip_id, show_delay=120, hide_delay=80,
                            trigger_mode=2, show_arrow=True)
    ui.set_tooltip_options(hwnd, tip_id, placement=2, open=False, max_width=300)

    if "聚焦查看" not in ui.get_tooltip_text(hwnd, tip_id, 0):
        raise RuntimeError("文字提示标签读回失败")
    if "焦点触发" not in ui.get_tooltip_text(hwnd, tip_id, 1):
        raise RuntimeError("文字提示内容读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()

    ui.dll.EU_SetElementFocus(hwnd, tip_id)
    pending = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[焦点等待状态]", pending)
    if not pending or not pending["timer_running"] or pending["timer_phase"] != 1:
        raise RuntimeError("文字提示焦点延迟计时器未启动")

    pump_messages(user32, msg, 0.22)
    opened = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[焦点打开状态]", opened)
    if not opened["open"] or opened["open_count"] < 1 or not opened["show_arrow"]:
        raise RuntimeError("文字提示焦点延迟打开失败")
    if opened["placement"] != 2 or opened["max_width"] != 300 or opened["show_delay"] != 120:
        raise RuntimeError("文字提示完整状态读回失败")

    user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)  # VK_ESCAPE
    pump_messages(user32, msg, 0.12)
    key_closed = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[键盘关闭状态]", key_closed)
    if key_closed["open"] or key_closed["close_count"] < 1 or key_closed["last_action"] != 4:
        raise RuntimeError("文字提示键盘关闭失败")

    ui.trigger_tooltip(hwnd, tip_id, True)
    manual_opened = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[手动打开状态]", manual_opened)
    if not manual_opened["open"] or manual_opened["last_action"] != 5:
        raise RuntimeError("文字提示手动打开失败")

    ui.trigger_tooltip(hwnd, tip_id, False)
    manual_closed = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[手动关闭状态]", manual_closed)
    if manual_closed["open"] or manual_closed["last_action"] != 5:
        raise RuntimeError("文字提示手动关闭失败")

    ui.set_tooltip_options(hwnd, tip_id, placement=3, open=True, max_width=260)
    ui.create_tooltip(
        hwnd,
        content_id,
        label="悬停提示 🌟",
        content="🌟 悬停模式也可使用，弹层保持中文。",
        placement=3,
        x=330,
        y=176,
        w=170,
        h=42,
    )
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、箭头、焦点触发和首屏尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
