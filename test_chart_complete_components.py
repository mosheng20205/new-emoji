import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 图表完成批次窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def main():
    hwnd = ui.create_window("📊 图表组件完成验证", 220, 70, 1060, 720)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1020, 660)
    ui.create_text(hwnd, content, "📊 图表组件完成验证", 28, 22, 320, 36)

    line_id = ui.create_line_chart(
        hwnd, content, "📈 多序列折线趋势",
        [("一月", 32), ("二月", 48), ("三月", 62), ("四月", 78)],
        1, 28, 76, 460, 250,
    )
    ui.set_line_chart_series(hwnd, line_id, [
        [("一月", 32), ("二月", 48), ("三月", 62), ("四月", 78)],
        [("一月", 18), ("二月", 35), ("三月", 44), ("四月", 59)],
        [("一月", 25), ("二月", 28), ("三月", 52), ("四月", 68)],
    ])
    ui.set_line_chart_options(hwnd, line_id, chart_style=1, show_axis=True, show_area=False, show_tooltip=True)

    bar_id = ui.create_bar_chart(
        hwnd, content, "📊 分组柱状排行",
        [("北京", 82), ("上海", 76), ("深圳", 69), ("成都", 58)],
        1, 530, 76, 430, 250,
    )
    ui.set_bar_chart_series(hwnd, bar_id, [
        [("北京", 82), ("上海", 76), ("深圳", 69), ("成都", 58)],
        [("北京", 62), ("上海", 55), ("深圳", 72), ("成都", 49)],
    ])
    ui.set_bar_chart_options(hwnd, bar_id, orientation=1, show_values=True, show_axis=True)

    donut_id = ui.create_donut_chart(
        hwnd, content, "🍩 外部标签环形占比",
        [("桌面端", 46), ("移动端", 34), ("平板端", 12), ("其他", 8)],
        0, 28, 370, 460, 230,
    )
    ui.set_donut_chart_advanced_options(hwnd, donut_id, show_legend=True, ring_width=24, show_labels=True)

    ui.create_text(hwnd, content, "✅ 多序列、分组柱状、外部百分比标签和状态读回均已接入。", 530, 392, 430, 34)
    print("[读回] 折线序列数=", ui.get_line_chart_series_count(hwnd, line_id))
    print("[读回] 柱状序列数=", ui.get_bar_chart_series_count(hwnd, bar_id))
    print("[读回] 环形高级选项=", ui.get_donut_chart_advanced_options(hwnd, donut_id))

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📊 图表完成批次示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < 60:
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

    print("📊 图表完成批次示例结束。")


if __name__ == "__main__":
    main()
