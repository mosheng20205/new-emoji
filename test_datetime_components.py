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
g_update_id = 0
g_toggle_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 日期时间组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        ui.calendar_move_month(g_hwnd, g_calendar_id, 1)
        ui.set_datepicker_date(g_hwnd, g_date_id, 2026, 6, 18)
        ui.datepicker_move_month(g_hwnd, g_date_id, 1)
        ui.set_timepicker_time(g_hwnd, g_time_id, 14, 40)
        ui.set_datetimepicker_datetime(g_hwnd, g_datetime_id, 2026, 7, 8, 16, 50)
        ui.datetimepicker_move_month(g_hwnd, g_datetime_id, -1)
        ui.set_time_select_time(g_hwnd, g_time_select_id, 20, 10)
        print(
            "[更新] "
            f"日历={ui.get_calendar_value(g_hwnd, g_calendar_id)} "
            f"日期={ui.get_datepicker_value(g_hwnd, g_date_id)} "
            f"时间={ui.get_timepicker_value(g_hwnd, g_time_id):04d} "
            f"日期时间={ui.get_datetimepicker_date_value(g_hwnd, g_datetime_id)} "
            f"{ui.get_datetimepicker_time_value(g_hwnd, g_datetime_id):04d} "
            f"时间选择={ui.get_time_select_value(g_hwnd, g_time_select_id):04d}"
        )
    elif element_id == g_toggle_id:
        next_open = not bool(ui.get_datepicker_open(g_hwnd, g_date_id))
        ui.set_datepicker_open(g_hwnd, g_date_id, next_open)
        ui.set_timepicker_open(g_hwnd, g_time_id, next_open)
        ui.set_datetimepicker_open(g_hwnd, g_datetime_id, next_open)
        ui.set_time_select_open(g_hwnd, g_time_select_id, next_open)
        print(
            "[弹层] "
            f"日期={ui.get_datepicker_open(g_hwnd, g_date_id)} "
            f"时间={ui.get_timepicker_open(g_hwnd, g_time_id)} "
            f"日期时间={ui.get_datetimepicker_open(g_hwnd, g_datetime_id)} "
            f"时间选择={ui.get_time_select_open(g_hwnd, g_time_select_id)}"
        )


def main():
    global g_hwnd, g_calendar_id, g_date_id, g_time_id
    global g_datetime_id, g_time_select_id, g_update_id, g_toggle_id

    hwnd = ui.create_window("📅 日期时间组件示例", 220, 80, 980, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 630)

    ui.create_text(hwnd, content_id, "📅 日期时间组件", 28, 24, 340, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐日历、日期选择器、时间选择器、日期时间选择器和时间选择的运行时开关、状态读取与月份切换。",
        28, 68, 760, 48,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_calendar_id = ui.create_calendar(hwnd, content_id, 2026, 5, 2, 28, 136, 360, 310)
    ui.create_text(hwnd, content_id, "📌 可点标题两侧切换月份", 44, 456, 300, 28)

    ui.create_text(hwnd, content_id, "📆 日期选择器", 430, 136, 180, 28)
    g_date_id = ui.create_datepicker(hwnd, content_id, 2026, 5, 2, 430, 172, 240, 38)

    ui.create_text(hwnd, content_id, "⏱ 时间选择器", 700, 136, 180, 28)
    g_time_id = ui.create_timepicker(hwnd, content_id, 9, 30, 700, 172, 190, 38)

    ui.create_text(hwnd, content_id, "🗓 日期时间选择器", 430, 250, 220, 28)
    g_datetime_id = ui.create_datetimepicker(
        hwnd, content_id, 2026, 5, 2, 10, 20, 430, 286, 300, 38
    )

    ui.create_text(hwnd, content_id, "🕘 时间选择", 760, 250, 180, 28)
    g_time_select_id = ui.create_time_select(hwnd, content_id, 18, 0, 760, 286, 170, 38)

    g_toggle_id = ui.create_button(hwnd, content_id, "🔎", "打开/关闭弹层", 430, 384, 170, 42)
    g_update_id = ui.create_button(hwnd, content_id, "🚀", "切换并读取", 626, 384, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "验证提示",
        "示例会在 1 秒后自动打开弹层，2 秒后切换日期时间并打印读取值。所有尺寸按首次打开窗口适配。",
        430, 468, 500, 86,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("日期时间组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_open = False
    auto_update = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_open and elapsed > 1.0:
            on_click(g_toggle_id)
            auto_open = True
        if not auto_update and elapsed > 2.0:
            on_click(g_update_id)
            auto_update = True
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

    print("日期时间组件示例结束。")


if __name__ == "__main__":
    main()
