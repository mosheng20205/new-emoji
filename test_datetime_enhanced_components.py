import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_calendar_id = 0
g_date_id = 0
g_time_id = 0
g_datetime_id = 0
g_time_select_id = 0
g_clamp_id = 0
g_toggle_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 日期时间增强组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_toggle_id:
        next_open = not bool(ui.get_datepicker_open(g_hwnd, g_date_id))
        ui.set_datepicker_open(g_hwnd, g_date_id, next_open)
        ui.set_timepicker_open(g_hwnd, g_time_id, next_open)
        ui.set_datetimepicker_open(g_hwnd, g_datetime_id, next_open)
        ui.set_time_select_open(g_hwnd, g_time_select_id, next_open)
        print(f"[弹层] 打开状态={int(next_open)}")
    elif element_id == g_clamp_id:
        ui.set_calendar_date(g_hwnd, g_calendar_id, 2026, 4, 3)
        ui.set_datepicker_date(g_hwnd, g_date_id, 2026, 8, 26)
        ui.set_timepicker_time(g_hwnd, g_time_id, 22, 58)
        ui.set_datetimepicker_datetime(g_hwnd, g_datetime_id, 2026, 3, 1, 6, 2)
        ui.set_time_select_time(g_hwnd, g_time_select_id, 23, 55)
        print(
            "[范围夹取] "
            f"日历={ui.get_calendar_value(g_hwnd, g_calendar_id)} "
            f"日期={ui.get_datepicker_value(g_hwnd, g_date_id)} "
            f"时间={ui.get_timepicker_value(g_hwnd, g_time_id):04d} "
            f"日期时间={ui.get_datetimepicker_date_value(g_hwnd, g_datetime_id)} "
            f"{ui.get_datetimepicker_time_value(g_hwnd, g_datetime_id):04d} "
            f"时间选择={ui.get_time_select_value(g_hwnd, g_time_select_id):04d}"
        )
        print(
            "[日期时间读回] "
            f"日历范围={ui.get_calendar_range(g_hwnd, g_calendar_id)} 选项={ui.get_calendar_options(g_hwnd, g_calendar_id)} "
            f"日期范围={ui.get_datepicker_range(g_hwnd, g_date_id)} 选项={ui.get_datepicker_options(g_hwnd, g_date_id)} "
            f"时间范围={ui.get_timepicker_range(g_hwnd, g_time_id)} 选项={ui.get_timepicker_options(g_hwnd, g_time_id)} "
            f"日期时间范围={ui.get_datetimepicker_range(g_hwnd, g_datetime_id)} 选项={ui.get_datetimepicker_options(g_hwnd, g_datetime_id)} "
            f"时间选择范围={ui.get_time_select_range(g_hwnd, g_time_select_id)} 选项={ui.get_time_select_options(g_hwnd, g_time_select_id)}"
        )


def main():
    global g_hwnd, g_calendar_id, g_date_id, g_time_id
    global g_datetime_id, g_time_select_id, g_clamp_id, g_toggle_id

    hwnd = ui.create_window("📅 日期时间增强组件", 220, 80, 1040, 700)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1020, 650)

    ui.create_text(hwnd, content_id, "📅 日期时间增强组件", 28, 24, 360, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐范围限制、今天高亮、中文日期格式、分钟步进和禁用项显示。弹层内灰色项不可选择，超界设置会自动夹取到有效范围。",
        28, 68, 900, 52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_calendar_id = ui.create_calendar(hwnd, content_id, 2026, 5, 12, 28, 140, 350, 310)
    ui.set_calendar_range(hwnd, g_calendar_id, 20260506, 20260622)
    ui.set_calendar_options(hwnd, g_calendar_id, 20260503, True)
    ui.create_text(hwnd, content_id, "🟦 日历：2026-05-06 至 2026-06-22 可选", 42, 460, 350, 30)

    ui.create_text(hwnd, content_id, "📆 日期选择器", 420, 140, 180, 28)
    g_date_id = ui.create_datepicker(hwnd, content_id, 2026, 5, 18, 420, 176, 260, 38)
    ui.set_datepicker_range(hwnd, g_date_id, 20260510, 20260720)
    ui.set_datepicker_options(hwnd, g_date_id, 20260503, True, 1)

    ui.create_text(hwnd, content_id, "⏰ 时间选择器", 720, 140, 180, 28)
    g_time_id = ui.create_timepicker(hwnd, content_id, 9, 25, 720, 176, 200, 38)
    ui.set_timepicker_range(hwnd, g_time_id, 830, 1830)
    ui.set_timepicker_options(hwnd, g_time_id, 5, 1)

    ui.create_text(hwnd, content_id, "🗓️ 日期时间选择器", 420, 260, 220, 28)
    g_datetime_id = ui.create_datetimepicker(
        hwnd, content_id, 2026, 5, 22, 10, 40, 420, 296, 320, 38
    )
    ui.set_datetimepicker_range(hwnd, g_datetime_id, 20260501, 20260731, 900, 1800)
    ui.set_datetimepicker_options(hwnd, g_datetime_id, 20260503, True, 15, 1)

    ui.create_text(hwnd, content_id, "🕒 时间选择", 780, 260, 180, 28)
    g_time_select_id = ui.create_time_select(hwnd, content_id, 14, 0, 780, 296, 190, 38)
    ui.set_time_select_range(hwnd, g_time_select_id, 1000, 2100)
    ui.set_time_select_options(hwnd, g_time_select_id, 15, 1)

    g_toggle_id = ui.create_button(hwnd, content_id, "🔎", "打开/关闭弹层", 420, 398, 170, 42)
    g_clamp_id = ui.create_button(hwnd, content_id, "📌", "设置越界值", 618, 398, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_clamp_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "验证提示",
        "示例会在 1 秒后自动打开弹层，2 秒后设置一组越界值并打印夹取结果。窗口保持 60 秒，方便观察中文和 emoji 渲染。",
        420, 480, 540, 86,
    )

    print(
        "[初始读回] "
        f"日历={ui.get_calendar_value(hwnd, g_calendar_id)} 范围={ui.get_calendar_range(hwnd, g_calendar_id)} 选项={ui.get_calendar_options(hwnd, g_calendar_id)} "
        f"日期={ui.get_datepicker_value(hwnd, g_date_id)} 范围={ui.get_datepicker_range(hwnd, g_date_id)} 选项={ui.get_datepicker_options(hwnd, g_date_id)} "
        f"时间={ui.get_timepicker_value(hwnd, g_time_id):04d} 范围={ui.get_timepicker_range(hwnd, g_time_id)} 选项={ui.get_timepicker_options(hwnd, g_time_id)} "
        f"日期时间={ui.get_datetimepicker_date_value(hwnd, g_datetime_id)} {ui.get_datetimepicker_time_value(hwnd, g_datetime_id):04d} "
        f"范围={ui.get_datetimepicker_range(hwnd, g_datetime_id)} 选项={ui.get_datetimepicker_options(hwnd, g_datetime_id)} "
        f"时间选择={ui.get_time_select_value(hwnd, g_time_select_id):04d} 范围={ui.get_time_select_range(hwnd, g_time_select_id)} 选项={ui.get_time_select_options(hwnd, g_time_select_id)}"
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("日期时间增强组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_open = False
    auto_clamp = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_open and elapsed > 1.0:
            on_click(g_toggle_id)
            auto_open = True
        if not auto_clamp and elapsed > 2.0:
            on_click(g_clamp_id)
            auto_clamp = True
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

    print("日期时间增强组件示例结束。")


if __name__ == "__main__":
    main()
