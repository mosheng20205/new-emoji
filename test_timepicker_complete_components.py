import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_time_id = 0
g_precise_id = 0
g_scroll_id = 0
g_range_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 时间选择器完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_scroll_id:
        ui.set_timepicker_scroll(g_hwnd, g_precise_id, 12, 36)
        ui.set_timepicker_open(g_hwnd, g_precise_id, True)
        print(
            "[滚动] "
            f"精确时间={ui.get_timepicker_value(g_hwnd, g_precise_id):04d} "
            f"滚动={ui.get_timepicker_scroll(g_hwnd, g_precise_id)}"
        )
    elif element_id == g_range_id:
        ui.set_timepicker_time(g_hwnd, g_time_id, 7, 10)
        ui.set_timepicker_time(g_hwnd, g_precise_id, 23, 58)
        print(
            "[范围夹取] "
            f"中文时间={ui.get_timepicker_value(g_hwnd, g_time_id):04d} "
            f"精确时间={ui.get_timepicker_value(g_hwnd, g_precise_id):04d}"
        )


def main():
    global g_hwnd, g_time_id, g_precise_id, g_scroll_id, g_range_id

    hwnd = ui.create_window("⏰ 时间选择器完整组件", 220, 80, 880, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 860, 570)

    ui.create_text(hwnd, content_id, "⏰ 时间选择器完整验证", 28, 24, 360, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证小时 0-23 全量列表、分钟长列表滚动、范围夹取、中文格式、滚动位置读回和首次窗口尺寸适配。",
        28, 68, 760, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "🕘 中文格式，15 分钟步进", 48, 148, 260, 28)
    g_time_id = ui.create_timepicker(hwnd, content_id, 9, 30, 48, 184, 260, 40)
    ui.set_timepicker_range(hwnd, g_time_id, 830, 1830)
    ui.set_timepicker_options(hwnd, g_time_id, 15, 1)
    ui.set_timepicker_open(hwnd, g_time_id, True)

    ui.create_text(hwnd, content_id, "🧭 精确分钟，长列表滚动", 410, 148, 280, 28)
    g_precise_id = ui.create_timepicker(hwnd, content_id, 14, 37, 410, 184, 260, 40)
    ui.set_timepicker_range(hwnd, g_precise_id, 0, 2359)
    ui.set_timepicker_options(hwnd, g_precise_id, 1, 0)
    ui.set_timepicker_time(hwnd, g_precise_id, 14, 37)
    ui.set_timepicker_open(hwnd, g_precise_id, True)
    ui.set_timepicker_scroll(hwnd, g_precise_id, 10, 32)

    g_scroll_id = ui.create_button(hwnd, content_id, "🧭", "滚动到下午", 48, 514, 150, 40)
    g_range_id = ui.create_button(hwnd, content_id, "📌", "测试范围夹取", 220, 514, 170, 40)
    ui.dll.EU_SetElementClickCallback(hwnd, g_scroll_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_range_id, on_click)

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "1 秒后自动滚动精确分钟列表，2 秒后设置越界时间并读取夹取结果。窗口保持 60 秒。",
        430, 494, 360, 72,
    )

    print(
        "[初始] "
        f"中文时间={ui.get_timepicker_value(hwnd, g_time_id):04d} "
        f"范围={ui.get_timepicker_range(hwnd, g_time_id)} "
        f"选项={ui.get_timepicker_options(hwnd, g_time_id)} "
        f"精确时间={ui.get_timepicker_value(hwnd, g_precise_id):04d} "
        f"滚动={ui.get_timepicker_scroll(hwnd, g_precise_id)}"
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("时间选择器完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_scroll = False
    auto_range = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_scroll and elapsed > 1.0:
            on_click(g_scroll_id)
            auto_scroll = True
        if not auto_range and elapsed > 2.0:
            on_click(g_range_id)
            auto_range = True
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

    print("时间选择器完整组件示例结束。")


if __name__ == "__main__":
    main()
