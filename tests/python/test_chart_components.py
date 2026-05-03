import ctypes
from ctypes import wintypes
import sys
import time

import test_new_emoji as ui

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WINDOW_W = 980
WINDOW_H = 760
CONTENT_W = 960
CONTENT_H = 710

g_hwnd = None
g_line_id = 0
g_bar_id = 0
g_donut_id = 0
g_update_id = 0
g_dark_id = 0
g_light_id = 0
g_flip = False


def chart_arg(values):
    data = ui._chart_data(values)
    return ui.bytes_arg(data), len(data)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 📈 图表组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] 宽 {width}，高 {height}")


@ui.ClickCallback
def on_click(element_id):
    global g_flip
    if element_id == g_update_id:
        g_flip = not g_flip
        if g_flip:
            line = [("周一", 28), ("周二", 42), ("周三", 58), ("周四", 73), ("周五", 96), ("周六", 88)]
            bars = [("华东", 96), ("华南", 78), ("华北", 63), ("西南", 49), ("海外", 35)]
            donut = [("移动端", 56), ("桌面端", 28), ("小程序", 11), ("其他", 5)]
            active = 0
            print("[图表] 🔄 已切换到增长数据")
        else:
            line = [("周一", 66), ("周二", 54), ("周三", 46), ("周四", 52), ("周五", 38), ("周六", 44)]
            bars = [("会员", 82), ("自然", 61), ("活动", 55), ("推荐", 38), ("其他", 24)]
            donut = [("新客户", 42), ("老客户", 39), ("沉睡唤醒", 13), ("试用", 6)]
            active = 1
            print("[图表] 🔄 已切换到复盘数据")

        data, length = chart_arg(line)
        ui.dll.EU_SetLineChartData(g_hwnd, g_line_id, data, length)
        data, length = chart_arg(bars)
        ui.dll.EU_SetBarChartData(g_hwnd, g_bar_id, data, length)
        data, length = chart_arg(donut)
        ui.dll.EU_SetDonutChartData(g_hwnd, g_donut_id, data, length, active)
    elif element_id == g_dark_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 1)
        print("[主题] 🌙 已切换深色")
    elif element_id == g_light_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 0)
        print("[主题] ☀️ 已切换浅色")
    elif element_id in (g_line_id, g_bar_id, g_donut_id):
        print(f"[点击] 👆 图表元素 {element_id}")


def main():
    global g_hwnd, g_line_id, g_bar_id, g_donut_id
    global g_update_id, g_dark_id, g_light_id

    hwnd = ui.create_window("📈 图表展示组件示例", 220, 70, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "📈 图表展示组件", 28, 24, 360, 28)
    ui.create_divider(
        hwnd, content_id,
        "📉 折线趋势 / 📊 柱状排行 / 🍩 环形占比",
        0, 1, 28, 62, 880, 34
    )

    g_line_id = ui.create_line_chart(
        hwnd, content_id,
        "📉 本周活跃趋势",
        [("周一", 66), ("周二", 54), ("周三", 46), ("周四", 52), ("周五", 38), ("周六", 44)],
        1,
        28, 114, 560, 250
    )
    g_donut_id = ui.create_donut_chart(
        hwnd, content_id,
        "🍩 客户来源占比",
        [("新客户", 42), ("老客户", 39), ("沉睡唤醒", 13), ("试用", 6)],
        1,
        608, 114, 300, 250
    )
    g_bar_id = ui.create_bar_chart(
        hwnd, content_id,
        "📊 渠道贡献排行",
        [("会员", 82), ("自然", 61), ("活动", 55), ("推荐", 38), ("其他", 24)],
        0,
        28, 394, 560, 250
    )

    ui.create_infobox(
        hwnd, content_id,
        "🧪 批次说明",
        "本批新增三个纯 D2D 图表控件，数据从 UTF-8 字节数组解析，文本和标签支持中文与 emoji。",
        608, 394, 300, 92
    )

    g_update_id = ui.create_button(hwnd, content_id, "🔄", "切换图表数据", 608, 514, 142, 42)
    g_dark_id = ui.create_button(hwnd, content_id, "🌙", "深色主题", 766, 514, 118, 42)
    g_light_id = ui.create_button(hwnd, content_id, "☀️", "浅色主题", 766, 570, 118, 42)

    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        "🖥️ 首屏已适配：右 908，底 668。",
        0, 0, False,
        608, 626, 300, 56
    )

    for eid in (g_line_id, g_bar_id, g_donut_id, g_update_id, g_dark_id, g_light_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📈 图表展示组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("📈 图表展示组件示例结束。")


if __name__ == "__main__":
    main()
