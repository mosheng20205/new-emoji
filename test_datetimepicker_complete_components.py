import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dt_id = 0
g_precise_id = 0
g_now_id = 0
g_clear_id = 0
g_scroll_id = 0
g_clamp_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 日期时间选择器完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_now_id:
        ui.datetimepicker_select_today(g_hwnd, g_dt_id)
        ui.datetimepicker_select_now(g_hwnd, g_precise_id)
        print(
            "[快捷] "
            f"今天={ui.get_datetimepicker_date_value(g_hwnd, g_dt_id)} "
            f"当前={ui.get_datetimepicker_date_value(g_hwnd, g_precise_id)} "
            f"{ui.get_datetimepicker_time_value(g_hwnd, g_precise_id):04d}"
        )
    elif element_id == g_clear_id:
        ui.clear_datetimepicker(g_hwnd, g_dt_id)
        ui.clear_datetimepicker(g_hwnd, g_precise_id)
        print(
            "[清空] "
            f"日期={ui.get_datetimepicker_date_value(g_hwnd, g_dt_id)} "
            f"时间={ui.get_datetimepicker_time_value(g_hwnd, g_dt_id)}"
        )
    elif element_id == g_scroll_id:
        ui.set_datetimepicker_scroll(g_hwnd, g_precise_id, 13, 42)
        ui.set_datetimepicker_open(g_hwnd, g_precise_id, True)
        print(f"[滚动] 精确选择器滚动={ui.get_datetimepicker_scroll(g_hwnd, g_precise_id)}")
    elif element_id == g_clamp_id:
        ui.set_datetimepicker_datetime(g_hwnd, g_dt_id, 2026, 4, 1, 6, 10)
        ui.set_datetimepicker_datetime(g_hwnd, g_precise_id, 2026, 9, 20, 23, 58)
        print(
            "[范围夹取] "
            f"中文={ui.get_datetimepicker_date_value(g_hwnd, g_dt_id)} "
            f"{ui.get_datetimepicker_time_value(g_hwnd, g_dt_id):04d} "
            f"精确={ui.get_datetimepicker_date_value(g_hwnd, g_precise_id)} "
            f"{ui.get_datetimepicker_time_value(g_hwnd, g_precise_id):04d}"
        )


def main():
    global g_hwnd, g_dt_id, g_precise_id
    global g_now_id, g_clear_id, g_scroll_id, g_clamp_id

    hwnd = ui.create_window("🗓 日期时间选择器完整组件", 220, 80, 980, 650)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 600)

    ui.create_text(hwnd, content_id, "🗓 日期时间选择器完整验证", 28, 24, 420, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证固定高度弹层、小时 0-23 全量列表、分钟长列表滚动、快捷今天、当前时间、清空、范围夹取和滚动状态读回。",
        28, 68, 860, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "📅 中文日期时间，15 分钟步进", 48, 148, 280, 28)
    g_dt_id = ui.create_datetimepicker(hwnd, content_id, 2026, 5, 18, 10, 30, 48, 184, 360, 40)
    ui.set_datetimepicker_range(hwnd, g_dt_id, 20260501, 20260731, 830, 1830)
    ui.set_datetimepicker_options(hwnd, g_dt_id, 20260503, True, 15, 1)
    ui.set_datetimepicker_open(hwnd, g_dt_id, True)

    ui.create_text(hwnd, content_id, "⏱ 精确分钟，长列表滚动", 500, 148, 280, 28)
    g_precise_id = ui.create_datetimepicker(hwnd, content_id, 2026, 6, 12, 14, 37, 500, 184, 360, 40)
    ui.set_datetimepicker_range(hwnd, g_precise_id, 20260501, 20260831, 0, 2359)
    ui.set_datetimepicker_options(hwnd, g_precise_id, 20260503, True, 1, 0)
    ui.set_datetimepicker_datetime(hwnd, g_precise_id, 2026, 6, 12, 14, 37)
    ui.set_datetimepicker_scroll(hwnd, g_precise_id, 10, 32)
    ui.set_datetimepicker_open(hwnd, g_precise_id, True)

    g_now_id = ui.create_button(hwnd, content_id, "📍", "今天/当前", 48, 540, 140, 40)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空", 210, 540, 110, 40)
    g_scroll_id = ui.create_button(hwnd, content_id, "🧭", "滚动列表", 342, 540, 130, 40)
    g_clamp_id = ui.create_button(hwnd, content_id, "📌", "范围夹取", 494, 540, 130, 40)
    for btn in (g_now_id, g_clear_id, g_scroll_id, g_clamp_id):
        ui.dll.EU_SetElementClickCallback(hwnd, btn, on_click)

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "1 秒后快捷选择，2 秒后滚动列表，3 秒后设置越界值，4 秒后清空。窗口保持 60 秒。",
        650, 520, 270, 72,
    )

    print(
        "[初始] "
        f"中文={ui.get_datetimepicker_date_value(hwnd, g_dt_id)} "
        f"{ui.get_datetimepicker_time_value(hwnd, g_dt_id):04d} "
        f"范围={ui.get_datetimepicker_range(hwnd, g_dt_id)} "
        f"选项={ui.get_datetimepicker_options(hwnd, g_dt_id)} "
        f"精确={ui.get_datetimepicker_date_value(hwnd, g_precise_id)} "
        f"{ui.get_datetimepicker_time_value(hwnd, g_precise_id):04d} "
        f"滚动={ui.get_datetimepicker_scroll(hwnd, g_precise_id)}"
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("日期时间选择器完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_now = False
    auto_scroll = False
    auto_clamp = False
    auto_clear = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_now and elapsed > 1.0:
            on_click(g_now_id)
            auto_now = True
        if not auto_scroll and elapsed > 2.0:
            on_click(g_scroll_id)
            auto_scroll = True
        if not auto_clamp and elapsed > 3.0:
            on_click(g_clamp_id)
            auto_clamp = True
        if not auto_clear and elapsed > 4.0:
            on_click(g_clear_id)
            auto_clear = True
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

    print("日期时间选择器完整组件示例结束。")


if __name__ == "__main__":
    main()
