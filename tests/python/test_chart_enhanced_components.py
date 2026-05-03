import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_line_id = 0
g_bar_id = 0
g_donut_id = 0
g_update_id = 0
g_flip = False


def chart_arg(values):
    data = ui._chart_data(values)
    return ui.bytes_arg(data), len(data)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 图表增强组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_flip
    if element_id != g_update_id:
        print(f"[点击] 图表元素 #{element_id}")
        return

    g_flip = not g_flip
    if g_flip:
        line = [("周一", 18), ("周二", 34), ("周三", 48), ("周四", 72), ("周五", 86), ("周六", 80)]
        bars = [("搜索", 92), ("推荐", 76), ("活动", 66), ("会员", 53), ("其他", 28)]
        donut = [("移动端", 58), ("桌面端", 25), ("小程序", 12), ("其他", 5)]
        line_selected, bar_selected, donut_active = 4, 0, 0
        print("[图表] 已切换到增长数据")
    else:
        line = [("周一", 62), ("周二", 50), ("周三", 46), ("周四", 39), ("周五", 44), ("周六", 36)]
        bars = [("华东", 88), ("华南", 61), ("华北", 55), ("西南", 42), ("海外", 31)]
        donut = [("新客户", 41), ("老客户", 37), ("唤醒", 16), ("试用", 6)]
        line_selected, bar_selected, donut_active = 2, 1, 1
        print("[图表] 已切换到复盘数据")

    data, length = chart_arg(line)
    ui.dll.EU_SetLineChartData(g_hwnd, g_line_id, data, length)
    ui.set_line_chart_selected(g_hwnd, g_line_id, line_selected)

    data, length = chart_arg(bars)
    ui.dll.EU_SetBarChartData(g_hwnd, g_bar_id, data, length)
    ui.set_bar_chart_selected(g_hwnd, g_bar_id, bar_selected)

    data, length = chart_arg(donut)
    ui.dll.EU_SetDonutChartData(g_hwnd, g_donut_id, data, length, donut_active)

    print(
        "[读回] 折线点={line_count}/选中={line_sel} 柱={bar_count}/选中={bar_sel} 环形={slice_count}/激活={active}".format(
            line_count=ui.get_line_chart_point_count(g_hwnd, g_line_id),
            line_sel=ui.get_line_chart_selected(g_hwnd, g_line_id),
            bar_count=ui.get_bar_chart_bar_count(g_hwnd, g_bar_id),
            bar_sel=ui.get_bar_chart_selected(g_hwnd, g_bar_id),
            slice_count=ui.get_donut_chart_slice_count(g_hwnd, g_donut_id),
            active=ui.get_donut_chart_active(g_hwnd, g_donut_id),
        )
    )
    print(
        "[选项读回] 折线={line_opts} 柱状={bar_opts} 环形={donut_opts}".format(
            line_opts=ui.get_line_chart_options(g_hwnd, g_line_id),
            bar_opts=ui.get_bar_chart_options(g_hwnd, g_bar_id),
            donut_opts=ui.get_donut_chart_options(g_hwnd, g_donut_id),
        )
    )


def main():
    global g_hwnd, g_line_id, g_bar_id, g_donut_id, g_update_id

    hwnd = ui.create_window("📊 图表增强组件", 220, 70, 1080, 780)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 1040, 720)
    ui.create_text(hwnd, content_id, "📊 图表增强批次", 28, 22, 300, 34)

    g_line_id = ui.create_line_chart(
        hwnd, content_id,
        "📈 活跃趋势面积图",
        [("周一", 62), ("周二", 50), ("周三", 46), ("周四", 39), ("周五", 44), ("周六", 36)],
        1,
        28, 74, 610, 260,
    )
    ui.set_line_chart_options(hwnd, g_line_id, chart_style=1, show_axis=True,
                              show_area=True, show_tooltip=True)
    ui.set_line_chart_selected(hwnd, g_line_id, 2)

    g_donut_id = ui.create_donut_chart(
        hwnd, content_id,
        "🍩 客户来源",
        [("新客户", 41), ("老客户", 37), ("唤醒", 16), ("试用", 6)],
        1,
        670, 74, 320, 260,
    )
    ui.set_donut_chart_options(hwnd, g_donut_id, show_legend=True, ring_width=28)

    g_bar_id = ui.create_bar_chart(
        hwnd, content_id,
        "📊 渠道贡献纵向图",
        [("华东", 88), ("华南", 61), ("华北", 55), ("西南", 42), ("海外", 31)],
        1,
        28, 372, 610, 250,
    )
    ui.set_bar_chart_options(hwnd, g_bar_id, orientation=1, show_values=True, show_axis=True)
    ui.set_bar_chart_selected(hwnd, g_bar_id, 1)

    empty_line_id = ui.create_line_chart(
        hwnd, content_id,
        "📭 空折线图",
        [],
        0,
        670, 372, 320, 108,
    )
    ui.set_line_chart_options(hwnd, empty_line_id, chart_style=0, show_axis=False,
                              show_area=False, show_tooltip=False)

    empty_bar_id = ui.create_bar_chart(
        hwnd, content_id,
        "📭 空柱状图",
        [],
        0,
        670, 500, 320, 108,
    )
    ui.set_bar_chart_options(hwnd, empty_bar_id, orientation=0, show_values=False, show_axis=False)

    g_update_id = ui.create_button(hwnd, content_id, "🔄", "切换图表数据", 28, 652, 150, 42)
    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        "🖥️ 当前内容右边界 990，底边界 694；首次打开即可完整查看。",
        0, 0, False,
        208, 652, 590, 42,
    )

    for eid in (g_line_id, g_bar_id, g_donut_id, empty_line_id, empty_bar_id, g_update_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    print(
        "[初始读回] 折线点={line_count}/选中={line_sel}/选项={line_opts} "
        "柱={bar_count}/选中={bar_sel}/选项={bar_opts} 环形={slice_count}/激活={active}/选项={donut_opts}".format(
            line_count=ui.get_line_chart_point_count(hwnd, g_line_id),
            line_sel=ui.get_line_chart_selected(hwnd, g_line_id),
            line_opts=ui.get_line_chart_options(hwnd, g_line_id),
            bar_count=ui.get_bar_chart_bar_count(hwnd, g_bar_id),
            bar_sel=ui.get_bar_chart_selected(hwnd, g_bar_id),
            bar_opts=ui.get_bar_chart_options(hwnd, g_bar_id),
            slice_count=ui.get_donut_chart_slice_count(hwnd, g_donut_id),
            active=ui.get_donut_chart_active(hwnd, g_donut_id),
            donut_opts=ui.get_donut_chart_options(hwnd, g_donut_id),
        )
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📊 图表增强组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("📊 图表增强组件示例结束。")


if __name__ == "__main__":
    main()
