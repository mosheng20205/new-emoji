import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_carousel_id = 0
g_prev_id = 0
g_next_id = 0
g_pause_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 走马灯完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_prev_id:
        ui.carousel_advance(g_hwnd, g_carousel_id, -1)
        print("[上一页] 状态：", ui.get_carousel_full_state(g_hwnd, g_carousel_id))
    elif element_id == g_next_id:
        ui.carousel_advance(g_hwnd, g_carousel_id, 1)
        print("[下一页] 状态：", ui.get_carousel_full_state(g_hwnd, g_carousel_id))
    elif element_id == g_pause_id:
        state = ui.get_carousel_full_state(g_hwnd, g_carousel_id)
        enabled = not bool(state["autoplay"])
        ui.set_carousel_autoplay(g_hwnd, g_carousel_id, enabled, 700)
        print("[自动播放切换] 状态：", ui.get_carousel_full_state(g_hwnd, g_carousel_id))


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
    global g_hwnd, g_carousel_id, g_prev_id, g_next_id, g_pause_id

    hwnd = ui.create_window("🎠 走马灯完整组件验证", 220, 80, 1000, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 620)

    ui.create_text(hwnd, content_id, "🎠 Carousel 走马灯完整封装", 28, 24, 440, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证真实内部定时器、自动播放推进、切换动画、循环边界、箭头/指示器交互和完整状态读回。",
        28, 72, 860, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    items = [
        "🚀 今日发布：新版组件全部走纯 D2D 渲染",
        "🎨 主题适配：浅色/深色下都保持清晰",
        "🧭 交互验证：箭头、指示器、键盘和自动播放",
        "✅ 状态读回：动画、边界、次数都可检查",
    ]
    g_carousel_id = ui.create_carousel(hwnd, content_id, items, 0, 0, 46, 150, 820, 280)
    ui.set_carousel_options(hwnd, g_carousel_id, loop=True, indicator_position=0, show_arrows=True, show_indicators=True)
    ui.set_carousel_animation(hwnd, g_carousel_id, 260)
    ui.set_carousel_autoplay(hwnd, g_carousel_id, True, 700)

    g_prev_id = ui.create_button(hwnd, content_id, "⬅️", "上一页", 46, 470, 116, 40)
    g_next_id = ui.create_button(hwnd, content_id, "➡️", "下一页", 178, 470, 116, 40)
    g_pause_id = ui.create_button(hwnd, content_id, "⏯️", "切换自动播放", 310, 470, 166, 40)
    for eid in (g_prev_id, g_next_id, g_pause_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    status_id = ui.create_text(hwnd, content_id, "📌 状态会输出到控制台，窗口保持可见 60 秒。", 46, 535, 760, 34)
    ui.set_text_options(hwnd, status_id, align=0, valign=0, wrap=False, ellipsis=False)

    initial = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[初始状态] ", initial)
    if not initial or initial["item_count"] != 4 or initial["active_index"] != 0:
        raise RuntimeError("走马灯初始状态读回失败")
    if not (initial["loop"] and initial["show_arrows"] and initial["show_indicators"]):
        raise RuntimeError("走马灯循环/箭头/指示器选项读回失败")
    if not initial["autoplay"] or initial["interval_ms"] != 700 or initial["transition_ms"] != 260:
        raise RuntimeError("走马灯自动播放或动画选项读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("走马灯完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32

    running = pump_messages(user32, msg, 1.15)
    state = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[内部定时器自动播放] ", state)
    if not state or state["autoplay_tick"] < 1 or state["active_index"] == 0:
        raise RuntimeError("走马灯内部自动播放定时器未推进")

    ui.set_carousel_autoplay(hwnd, g_carousel_id, False, 700)
    ui.set_carousel_options(hwnd, g_carousel_id, loop=False, indicator_position=0, show_arrows=True, show_indicators=True)
    ui.set_carousel_active(hwnd, g_carousel_id, 3)
    before_boundary = ui.get_carousel_full_state(hwnd, g_carousel_id)
    ui.carousel_advance(hwnd, g_carousel_id, 1)
    after_boundary = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[非循环边界] ", before_boundary, after_boundary)
    if after_boundary["active_index"] != 3 or after_boundary["change_count"] != before_boundary["change_count"]:
        raise RuntimeError("走马灯非循环边界夹取失败")

    ui.carousel_advance(hwnd, g_carousel_id, -1)
    anim_start = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[切换动画开始] ", anim_start)
    if anim_start["active_index"] != 2 or anim_start["previous_index"] != 3:
        raise RuntimeError("走马灯上一页切换状态失败")
    if anim_start["transition_progress"] >= 100 or anim_start["last_action"] != 2:
        raise RuntimeError("走马灯动画起始状态读回失败")

    running = running and pump_messages(user32, msg, 0.45)
    anim_done = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[切换动画结束] ", anim_done)
    if anim_done["transition_progress"] != 100:
        raise RuntimeError("走马灯动画进度未完成")

    ui.set_carousel_options(hwnd, g_carousel_id, loop=True, indicator_position=0, show_arrows=True, show_indicators=True)
    ui.set_carousel_active(hwnd, g_carousel_id, 0)
    ui.set_carousel_autoplay(hwnd, g_carousel_id, True, 600)
    tick_before = ui.get_carousel_full_state(hwnd, g_carousel_id)
    ui.carousel_tick(hwnd, g_carousel_id, 600)
    tick_after = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[主动 tick 推进] ", tick_before, tick_after)
    if tick_after["active_index"] != 1 or tick_after["autoplay_tick"] <= tick_before["autoplay_tick"]:
        raise RuntimeError("走马灯主动 tick 推进失败")

    start = time.time()
    while running and time.time() - start < 56:
        running = pump_messages(user32, msg, 0.05)

    print("走马灯完整组件示例结束。")


if __name__ == "__main__":
    main()
