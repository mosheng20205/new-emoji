import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_date_id = 0
g_range_id = 0
g_today_id = 0
g_clear_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 日期选择器完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_today_id:
        ui.datepicker_select_today(g_hwnd, g_date_id)
        ui.datepicker_select_today(g_hwnd, g_range_id)
        print(
            "[今天] "
            f"单选={ui.get_datepicker_value(g_hwnd, g_date_id)} "
            f"区间={ui.get_datepicker_selection_range(g_hwnd, g_range_id)}"
        )
    elif element_id == g_clear_id:
        ui.clear_datepicker(g_hwnd, g_date_id)
        ui.clear_datepicker(g_hwnd, g_range_id)
        print(
            "[清空] "
            f"单选={ui.get_datepicker_value(g_hwnd, g_date_id)} "
            f"区间={ui.get_datepicker_selection_range(g_hwnd, g_range_id)}"
        )


def main():
    global g_hwnd, g_date_id, g_range_id, g_today_id, g_clear_id

    hwnd = ui.create_window("📆 日期选择器完整组件", 220, 80, 900, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 570)

    ui.create_text(hwnd, content_id, "📆 日期选择器完整验证", 28, 24, 360, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证清空、快捷今天、区间选择、范围夹取、中文格式和底部操作按钮。弹层会保持可见，方便观察 emoji、主题色和区间高亮。",
        28, 68, 780, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "📅 单选日期", 48, 148, 180, 28)
    g_date_id = ui.create_datepicker(hwnd, content_id, 2026, 5, 18, 48, 184, 290, 40)
    ui.set_datepicker_range(hwnd, g_date_id, 20260501, 20260720)
    ui.set_datepicker_options(hwnd, g_date_id, 20260503, True, 1)
    ui.set_datepicker_open(hwnd, g_date_id, True)

    ui.create_text(hwnd, content_id, "🗓 区间日期", 410, 148, 180, 28)
    g_range_id = ui.create_datepicker(hwnd, content_id, 2026, 5, 20, 410, 184, 360, 40)
    ui.set_datepicker_range(hwnd, g_range_id, 20260501, 20260831)
    ui.set_datepicker_options(hwnd, g_range_id, 20260503, True, 0)
    ui.set_datepicker_selection_range(hwnd, g_range_id, 20260512, 20260522, True)
    ui.set_datepicker_open(hwnd, g_range_id, True)

    g_today_id = ui.create_button(hwnd, content_id, "📍", "选择今天", 48, 524, 140, 40)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空日期", 210, 524, 140, 40)
    ui.dll.EU_SetElementClickCallback(hwnd, g_today_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_clear_id, on_click)

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "1 秒后自动执行“选择今天”，2 秒后自动执行“清空日期”，3 秒后恢复区间并重新打开弹层。窗口保持 60 秒。",
        410, 498, 380, 72,
    )

    initial_range = ui.get_datepicker_selection_range(hwnd, g_range_id)
    initial_options = ui.get_datepicker_options(hwnd, g_date_id)
    print(
        "[初始] "
        f"单选={ui.get_datepicker_value(hwnd, g_date_id)} "
        f"范围={ui.get_datepicker_range(hwnd, g_date_id)} "
        f"选项={initial_options} "
        f"区间={initial_range}"
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("日期选择器完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_today = False
    auto_clear = False
    auto_restore = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_today and elapsed > 1.0:
            on_click(g_today_id)
            auto_today = True
        if not auto_clear and elapsed > 2.0:
            on_click(g_clear_id)
            auto_clear = True
        if not auto_restore and elapsed > 3.0:
            ui.set_datepicker_date(hwnd, g_date_id, 2026, 6, 8)
            ui.set_datepicker_selection_range(hwnd, g_range_id, 20260603, 20260618, True)
            ui.set_datepicker_open(hwnd, g_date_id, True)
            ui.set_datepicker_open(hwnd, g_range_id, True)
            print(
                "[恢复] "
                f"单选={ui.get_datepicker_value(hwnd, g_date_id)} "
                f"区间={ui.get_datepicker_selection_range(hwnd, g_range_id)} "
                f"打开={ui.get_datepicker_open(hwnd, g_range_id)}"
            )
            auto_restore = True
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

    print("日期选择器完整组件示例结束。")


if __name__ == "__main__":
    main()
