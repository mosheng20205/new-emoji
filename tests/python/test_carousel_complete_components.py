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
    print("[关闭] 🎠 走马灯完整样式验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_prev_id:
        ui.carousel_advance(g_hwnd, g_carousel_id, -1)
        print("[上一项] 状态：", ui.get_carousel_full_state(g_hwnd, g_carousel_id))
    elif element_id == g_next_id:
        ui.carousel_advance(g_hwnd, g_carousel_id, 1)
        print("[下一项] 状态：", ui.get_carousel_full_state(g_hwnd, g_carousel_id))
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


def assert_equal(label, actual, expected):
    if actual != expected:
        raise RuntimeError(f"{label} 读回失败：实际={actual!r} 预期={expected!r}")


def main():
    global g_hwnd, g_carousel_id, g_prev_id, g_next_id, g_pause_id

    hwnd = ui.create_window("🎠 走马灯全样式组件验证", 220, 80, 1080, 720)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1040, 660)

    ui.create_text(hwnd, content_id, "🎠 Carousel 走马灯全样式封装", 28, 24, 520, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证指示器触发方式、箭头模式、横向/纵向、普通/卡片、交替背景、文字样式、自动播放、边界和动画状态。",
        28, 72, 930, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    items = [
        "🚀 第一屏：默认横向轮播",
        "🎨 第二屏：Element Plus 交替背景",
        "🧭 第三屏：指示器与箭头交互",
        "✅ 第四屏：状态读回与动画",
    ]
    g_carousel_id = ui.create_carousel(hwnd, content_id, items, 0, 0, 46, 150, 860, 280)
    ui.set_carousel_options(hwnd, g_carousel_id, loop=True, indicator_position=0, show_arrows=True, show_indicators=True)
    ui.set_carousel_behavior(hwnd, g_carousel_id, trigger_mode="hover", arrow_mode="hover",
                             direction="horizontal", carousel_type="normal", pause_on_hover=True)
    ui.set_carousel_visual(
        hwnd, g_carousel_id,
        text_color=0xFF475669,
        text_alpha=191,
        text_font_size=18,
        odd_bg=0xFFD3DCE6,
        even_bg=0xFF99A9BF,
        panel_bg=0xFFF5F7FA,
        active_indicator=0xFF409EFF,
        inactive_indicator=0x6678909C,
        card_scale_percent=78,
    )
    ui.set_carousel_animation(hwnd, g_carousel_id, 260)
    ui.set_carousel_autoplay(hwnd, g_carousel_id, True, 700)

    g_prev_id = ui.create_button(hwnd, content_id, "⬅️", "上一项", 46, 470, 116, 40)
    g_next_id = ui.create_button(hwnd, content_id, "➡️", "下一项", 178, 470, 116, 40)
    g_pause_id = ui.create_button(hwnd, content_id, "⏯️", "切换自动播放", 310, 470, 166, 40)
    for eid in (g_prev_id, g_next_id, g_pause_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    status_id = ui.create_text(hwnd, content_id, "📊 状态会输出到控制台，窗口保持可见用于人工确认。", 46, 535, 820, 34)
    ui.set_text_options(hwnd, status_id, align=0, valign=0, wrap=False, ellipsis=False)

    behavior = ui.get_carousel_behavior(hwnd, g_carousel_id)
    print("[行为读回]", behavior)
    assert_equal("trigger_mode", behavior["trigger_mode"], 0)
    assert_equal("arrow_mode", behavior["arrow_mode"], 0)
    assert_equal("direction", behavior["direction"], 0)
    assert_equal("carousel_type", behavior["carousel_type"], 0)
    assert_equal("pause_on_hover", behavior["pause_on_hover"], True)

    visual = ui.get_carousel_visual(hwnd, g_carousel_id)
    print("[视觉读回]", visual)
    assert_equal("text_color", visual["text_color"], 0xFF475669)
    assert_equal("text_alpha", visual["text_alpha"], 191)
    assert_equal("text_font_size", visual["text_font_size"], 18)
    assert_equal("odd_bg", visual["odd_bg"], 0xFFD3DCE6)
    assert_equal("even_bg", visual["even_bg"], 0xFF99A9BF)
    assert_equal("panel_bg", visual["panel_bg"], 0xFFF5F7FA)
    assert_equal("active_indicator", visual["active_indicator"], 0xFF409EFF)
    assert_equal("inactive_indicator", visual["inactive_indicator"], 0x6678909C)
    assert_equal("card_scale_percent", visual["card_scale_percent"], 78)

    initial = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[初始状态]", initial)
    if not initial or initial["item_count"] != 4 or initial["active_index"] != 0:
        raise RuntimeError("走马灯初始状态读回失败")
    if not (initial["loop"] and initial["show_arrows"] and initial["show_indicators"]):
        raise RuntimeError("走马灯循环 / 箭头 / 指示器选项读回失败")
    if not initial["autoplay"] or initial["interval_ms"] != 700 or initial["transition_ms"] != 260:
        raise RuntimeError("走马灯自动播放或动画选项读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("🎠 走马灯完整样式示例已显示。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32

    running = pump_messages(user32, msg, 1.15)
    state = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[内部定时器自动播放]", state)
    if not state or state["autoplay_tick"] < 1 or state["active_index"] == 0:
        raise RuntimeError("走马灯内部自动播放定时器未推进")

    ui.set_carousel_behavior(hwnd, g_carousel_id, trigger_mode="click", arrow_mode="always",
                             direction="vertical", carousel_type="card", pause_on_hover=False)
    behavior = ui.get_carousel_behavior(hwnd, g_carousel_id)
    print("[卡片纵向行为读回]", behavior)
    assert_equal("trigger_mode click", behavior["trigger_mode"], 1)
    assert_equal("arrow_mode always", behavior["arrow_mode"], 1)
    assert_equal("direction vertical", behavior["direction"], 1)
    assert_equal("carousel_type card", behavior["carousel_type"], 1)
    assert_equal("pause_on_hover off", behavior["pause_on_hover"], False)

    ui.set_carousel_options(hwnd, g_carousel_id, loop=False, indicator_position=1, show_arrows=False, show_indicators=True)
    options = ui.get_carousel_options(hwnd, g_carousel_id)
    behavior = ui.get_carousel_behavior(hwnd, g_carousel_id)
    print("[旧选项兼容读回]", options, behavior)
    if options[0] or options[2] or behavior["arrow_mode"] != 2:
        raise RuntimeError("旧 EU_SetCarouselOptions 未正确映射箭头显示状态")

    ui.set_carousel_active(hwnd, g_carousel_id, 3)
    before_boundary = ui.get_carousel_full_state(hwnd, g_carousel_id)
    ui.carousel_advance(hwnd, g_carousel_id, 1)
    after_boundary = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[非循环边界]", before_boundary, after_boundary)
    if after_boundary["active_index"] != 3 or after_boundary["change_count"] != before_boundary["change_count"]:
        raise RuntimeError("走马灯非循环边界夹取失败")

    ui.set_carousel_options(hwnd, g_carousel_id, loop=True, indicator_position=0, show_arrows=True, show_indicators=True)
    ui.set_carousel_behavior(hwnd, g_carousel_id, trigger_mode="click", arrow_mode="always",
                             direction="vertical", carousel_type="normal", pause_on_hover=False)
    ui.carousel_advance(hwnd, g_carousel_id, -1)
    anim_start = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[纵向切换动画开始]", anim_start)
    if anim_start["active_index"] != 2 or anim_start["previous_index"] != 3:
        raise RuntimeError("走马灯上一项切换状态失败")
    if anim_start["transition_progress"] >= 100 or anim_start["last_action"] != 2:
        raise RuntimeError("走马灯动画起始状态读回失败")

    running = running and pump_messages(user32, msg, 0.45)
    anim_done = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[切换动画结束]", anim_done)
    if anim_done["transition_progress"] != 100:
        raise RuntimeError("走马灯动画进度未完成")

    ui.set_carousel_active(hwnd, g_carousel_id, 0)
    ui.set_carousel_autoplay(hwnd, g_carousel_id, True, 600)
    tick_before = ui.get_carousel_full_state(hwnd, g_carousel_id)
    ui.carousel_tick(hwnd, g_carousel_id, 600)
    tick_after = ui.get_carousel_full_state(hwnd, g_carousel_id)
    print("[主动 tick 推进]", tick_before, tick_after)
    if tick_after["active_index"] != 1 or tick_after["autoplay_tick"] <= tick_before["autoplay_tick"]:
        raise RuntimeError("走马灯主动 tick 推进失败")

    start = time.time()
    while running and time.time() - start < 6:
        running = pump_messages(user32, msg, 0.05)

    print("✅ 走马灯全样式组件验证完成")


if __name__ == "__main__":
    main()
