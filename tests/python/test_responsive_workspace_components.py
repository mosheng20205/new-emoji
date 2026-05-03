import ctypes
from ctypes import wintypes
import sys
import time

import test_new_emoji as ui

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WINDOW_W = 1120
WINDOW_H = 820
CONTENT_W = 1090
CONTENT_H = 770
MIN_CONTENT_W = 860

g_hwnd = None
g_content_id = 0
g_title_id = 0
g_notice_id = 0
g_sales_id = 0
g_orders_id = 0
g_quality_id = 0
g_chart_id = 0
g_table_id = 0
g_progress_id = 0
g_status_api_id = 0
g_status_queue_id = 0
g_status_release_id = 0
g_refresh_id = 0
g_compact_id = 0
g_wide_id = 0
g_dark_id = 0
g_light_id = 0
g_flip = False


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


def set_text(element_id: int, text: str):
    data, length = utf8_arg(text)
    ui.dll.EU_SetElementText(g_hwnd, element_id, data, length)


def set_table(columns, rows):
    col_data, col_len = utf8_arg("|".join(columns))
    row_data, row_len = utf8_arg("|".join(",".join(row) for row in rows))
    ui.dll.EU_SetTableData(g_hwnd, g_table_id, col_data, col_len, row_data, row_len)


def set_line(points):
    data, length = utf8_arg("|".join(f"{label}\t{value}" for label, value in points))
    ui.dll.EU_SetLineChartData(g_hwnd, g_chart_id, data, length)


def set_kpi(element_id: int, value: str, subtitle: str, trend: str, trend_type: int):
    value_data, value_len = utf8_arg(value)
    subtitle_data, subtitle_len = utf8_arg(subtitle)
    trend_data, trend_len = utf8_arg(trend)
    ui.dll.EU_SetKpiCardData(
        g_hwnd, element_id,
        value_data, value_len,
        subtitle_data, subtitle_len,
        trend_data, trend_len,
        trend_type
    )


def set_status(element_id: int, label: str, desc: str, status: int):
    label_data, label_len = utf8_arg(label)
    desc_data, desc_len = utf8_arg(desc)
    ui.dll.EU_SetStatusDot(g_hwnd, element_id, label_data, label_len, desc_data, desc_len, status)


def apply_layout(width: int, height: int):
    content_w = max(MIN_CONTENT_W, min(width - 30, CONTENT_W))
    content_h = max(650, min(height - 50, CONTENT_H))
    right_x = 28 + (content_w - 56) // 2 + 16
    left_w = right_x - 44
    right_w = content_w - right_x - 28
    card_w = (content_w - 56 - 32) // 3

    ui.dll.EU_SetElementBounds(g_hwnd, g_content_id, 0, 0, content_w, content_h)
    ui.dll.EU_SetElementBounds(g_hwnd, g_title_id, 28, 24, min(520, content_w - 56), 32)
    ui.dll.EU_SetElementBounds(g_hwnd, g_notice_id, 28, 66, content_w - 56, 42)

    ui.dll.EU_SetElementBounds(g_hwnd, g_sales_id, 28, 132, card_w, 126)
    ui.dll.EU_SetElementBounds(g_hwnd, g_orders_id, 28 + card_w + 16, 132, card_w, 126)
    ui.dll.EU_SetElementBounds(g_hwnd, g_quality_id, 28 + (card_w + 16) * 2, 132, card_w, 126)

    ui.dll.EU_SetElementBounds(g_hwnd, g_chart_id, 28, 290, left_w, 250)
    ui.dll.EU_SetElementBounds(g_hwnd, g_table_id, right_x, 290, right_w, 250)
    ui.dll.EU_SetElementBounds(g_hwnd, g_progress_id, 28, 564, left_w, 46)

    status_w = max(180, (right_w - 24) // 3)
    ui.dll.EU_SetElementBounds(g_hwnd, g_status_api_id, right_x, 560, status_w, 56)
    ui.dll.EU_SetElementBounds(g_hwnd, g_status_queue_id, right_x + status_w + 12, 560, status_w, 56)
    ui.dll.EU_SetElementBounds(g_hwnd, g_status_release_id, right_x + (status_w + 12) * 2, 560, status_w, 56)

    button_y = 650
    ui.dll.EU_SetElementBounds(g_hwnd, g_refresh_id, 28, button_y, 138, 42)
    ui.dll.EU_SetElementBounds(g_hwnd, g_compact_id, 184, button_y, 124, 42)
    ui.dll.EU_SetElementBounds(g_hwnd, g_wide_id, 326, button_y, 124, 42)
    ui.dll.EU_SetElementBounds(g_hwnd, g_dark_id, right_x, button_y, 118, 42)
    ui.dll.EU_SetElementBounds(g_hwnd, g_light_id, right_x + 136, button_y, 118, 42)

    set_text(g_notice_id, f"📐 已按当前窗口重排：内容区 {content_w}x{content_h}，右侧起点 {right_x}。")
    ui.dll.EU_InvalidateElement(g_hwnd, g_content_id)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 📐 自适应工作台示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[重排] 📐 窗口 {width}x{height}")
    apply_layout(width, height)


@ui.ClickCallback
def on_click(element_id):
    global g_flip

    if element_id == g_refresh_id:
        g_flip = not g_flip
        if g_flip:
            set_kpi(g_sales_id, "386.2万", "🚀 大客户成交提升", "📈 上升 18.4%", 1)
            set_kpi(g_orders_id, "22,908", "🛒 小程序订单增长", "📈 上升 9.7%", 1)
            set_kpi(g_quality_id, "98.1%", "✅ 抽检全部通过", "📈 上升 1.3%", 1)
            set_line([("周一", 42), ("周二", 56), ("周三", 63), ("周四", 78), ("周五", 92), ("周六", 86)])
            set_table(
                ["模块", "负责人", "状态"],
                [
                    ["📊 数据看板", "阿青", "✅ 已发布"],
                    ["🎨 主题系统", "小南", "🚀 灰度中"],
                    ["🔔 通知中心", "小周", "🟢 正常"],
                ],
            )
            ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_id, 92)
            set_status(g_status_api_id, "🟢 API 正常", "平均 82ms", 1)
            set_status(g_status_queue_id, "🟢 队列顺畅", "积压 42 条", 1)
            set_status(g_status_release_id, "🚀 发布推进", "进度 92%", 1)
            print("[数据] 🔄 已切换到增长视图")
        else:
            set_kpi(g_sales_id, "318.9万", "📉 活动流量回落", "📉 下降 4.8%", -1)
            set_kpi(g_orders_id, "18,204", "🧾 复购订单稳定", "📈 上升 2.1%", 1)
            set_kpi(g_quality_id, "94.6%", "🧪 仍有样本复检", "📉 下降 0.8%", -1)
            set_line([("周一", 68), ("周二", 61), ("周三", 59), ("周四", 64), ("周五", 58), ("周六", 71)])
            set_table(
                ["模块", "负责人", "状态"],
                [
                    ["📊 数据看板", "阿青", "🟡 观察"],
                    ["🎨 主题系统", "小南", "✅ 完成"],
                    ["🔔 通知中心", "小周", "🟠 排队"],
                ],
            )
            ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_id, 68)
            set_status(g_status_api_id, "🟢 API 正常", "平均 108ms", 1)
            set_status(g_status_queue_id, "🟡 队列积压", "积压 318 条", 2)
            set_status(g_status_release_id, "🟠 发布观察", "进度 68%", 2)
            print("[数据] 🔄 已切换到观察视图")

    elif element_id == g_compact_id:
        ui.dll.EU_SetWindowBounds(g_hwnd, 220, 90, 940, 720)
        apply_layout(940, 720)
        print("[布局] 📱 紧凑窗口")

    elif element_id == g_wide_id:
        ui.dll.EU_SetWindowBounds(g_hwnd, 160, 70, WINDOW_W, WINDOW_H)
        apply_layout(WINDOW_W, WINDOW_H)
        print("[布局] 🖥️ 宽屏窗口")

    elif element_id == g_dark_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 1)
        print("[主题] 🌙 深色")

    elif element_id == g_light_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 0)
        print("[主题] ☀️ 浅色")


def main():
    global g_hwnd, g_content_id, g_title_id, g_notice_id
    global g_sales_id, g_orders_id, g_quality_id, g_chart_id, g_table_id, g_progress_id
    global g_status_api_id, g_status_queue_id, g_status_release_id
    global g_refresh_id, g_compact_id, g_wide_id, g_dark_id, g_light_id

    hwnd = ui.create_window("📐 自适应工作台组件示例", 180, 70, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    g_content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    g_title_id = ui.create_text(hwnd, g_content_id, "📐 自适应工作台组件", 28, 24, 520, 32)
    g_notice_id = ui.create_alert(
        hwnd, g_content_id,
        "📏 布局状态",
        "🖥️ 首屏已适配，拖动窗口或点击紧凑/宽屏按钮会重新排布。",
        0, 0, False,
        28, 66, 1034, 42
    )

    g_sales_id = ui.create_kpi_card(
        hwnd, g_content_id,
        "💰 今日成交额", "318.9万", "📉 活动流量回落", "📉 下降 4.8%",
        -1, 28, 132, 330, 126
    )
    g_orders_id = ui.create_kpi_card(
        hwnd, g_content_id,
        "🧾 订单数量", "18,204", "🧾 复购订单稳定", "📈 上升 2.1%",
        1, 374, 132, 330, 126
    )
    g_quality_id = ui.create_kpi_card(
        hwnd, g_content_id,
        "🧪 质检通过率", "94.6%", "🧪 仍有样本复检", "📉 下降 0.8%",
        -1, 720, 132, 330, 126
    )

    g_chart_id = ui.create_line_chart(
        hwnd, g_content_id,
        "📈 访问趋势",
        [("周一", 68), ("周二", 61), ("周三", 59), ("周四", 64), ("周五", 58), ("周六", 71)],
        0, 28, 290, 520, 250
    )
    g_table_id = ui.create_table(
        hwnd, g_content_id,
        ["模块", "负责人", "状态"],
        [
            ["📊 数据看板", "阿青", "🟡 观察"],
            ["🎨 主题系统", "小南", "✅ 完成"],
            ["🔔 通知中心", "小周", "🟠 排队"],
        ],
        True, True, 580, 290, 482, 250
    )
    g_progress_id = ui.create_progress(
        hwnd, g_content_id,
        "🚚 发布进度", 68, 2, 28, 564, 520, 46
    )
    g_status_api_id = ui.create_status_dot(
        hwnd, g_content_id,
        "🟢 API 正常", "平均 108ms", 1, 580, 560, 146, 56
    )
    g_status_queue_id = ui.create_status_dot(
        hwnd, g_content_id,
        "🟡 队列积压", "积压 318 条", 2, 742, 560, 146, 56
    )
    g_status_release_id = ui.create_status_dot(
        hwnd, g_content_id,
        "🟠 发布观察", "进度 68%", 2, 904, 560, 146, 56
    )

    g_refresh_id = ui.create_button(hwnd, g_content_id, "🔄", "切换数据", 28, 650, 138, 42)
    g_compact_id = ui.create_button(hwnd, g_content_id, "📱", "紧凑布局", 184, 650, 124, 42)
    g_wide_id = ui.create_button(hwnd, g_content_id, "🖥️", "宽屏布局", 326, 650, 124, 42)
    g_dark_id = ui.create_button(hwnd, g_content_id, "🌙", "深色主题", 580, 650, 118, 42)
    g_light_id = ui.create_button(hwnd, g_content_id, "☀️", "浅色主题", 716, 650, 118, 42)

    apply_layout(WINDOW_W, WINDOW_H)

    for eid in (g_refresh_id, g_compact_id, g_wide_id, g_dark_id, g_light_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📐 自适应工作台组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("📐 自适应工作台组件示例结束。")


if __name__ == "__main__":
    main()
