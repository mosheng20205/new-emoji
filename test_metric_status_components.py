import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 960
WINDOW_H = 720
CONTENT_W = 940
CONTENT_H = 670

g_hwnd = None
g_kpi_sales_id = 0
g_kpi_order_id = 0
g_trend_visit_id = 0
g_trend_latency_id = 0
g_status_service_id = 0
g_status_queue_id = 0
g_status_pay_id = 0
g_update_id = 0
g_dark_id = 0
g_light_id = 0
g_flip = False


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 📊 指标状态组件示例正在关闭")
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
            value, subtitle, trend = "328.6万", "🚀 较昨日多 42 个活跃客户", "📈 上升 12.8%"
            order_value, order_subtitle, order_trend = "18,420", "🕑 高峰时段集中在 14:00", "📈 上升 6.4%"
            visit_value, visit_pct, visit_detail, visit_dir = "72,910", "📈 上升 9.6%", "📱 移动端访问占比继续提高", 1
            latency_value, latency_pct, latency_detail, latency_dir = "86 毫秒", "⚡ 下降 18 毫秒", "✅ 接口响应速度改善", 1
            service_label, service_desc, service_status = "🟢 主服务运行中", "✅ 所有实例均已通过健康检查", 1
            queue_label, queue_desc, queue_status = "🟢 消息队列正常", "📬 待处理任务 128 条", 1
            pay_label, pay_desc, pay_status = "🟡 支付通道观察中", "⏱️ 第三方回调存在轻微延迟", 2
        else:
            value, subtitle, trend = "291.4万", "📉 较昨日少 17 个活跃客户", "📉 下降 4.2%"
            order_value, order_subtitle, order_trend = "15,806", "🛒 复购订单占比 31%", "📉 下降 2.1%"
            visit_value, visit_pct, visit_detail, visit_dir = "66,240", "📉 下降 3.7%", "🎯 活动页访问回落到常规水平", -1
            latency_value, latency_pct, latency_detail, latency_dir = "124 毫秒", "⏱️ 上升 22 毫秒", "🛰️ 华东节点需要继续观察", -1
            service_label, service_desc, service_status = "🟢 主服务运行中", "✅ 核心接口可用，错误率 0.03%", 1
            queue_label, queue_desc, queue_status = "🟡 消息队列积压", "📬 消费速度低于写入速度", 2
            pay_label, pay_desc, pay_status = "🔴 支付通道异常", "🛡️ 备用通道已经自动接管", 3

        value_data, value_len = utf8_arg(value)
        subtitle_data, subtitle_len = utf8_arg(subtitle)
        trend_data, trend_len = utf8_arg(trend)
        ui.dll.EU_SetKpiCardData(
            g_hwnd, g_kpi_sales_id,
            value_data, value_len,
            subtitle_data, subtitle_len,
            trend_data, trend_len,
            1 if g_flip else -1
        )

        value_data, value_len = utf8_arg(order_value)
        subtitle_data, subtitle_len = utf8_arg(order_subtitle)
        trend_data, trend_len = utf8_arg(order_trend)
        ui.dll.EU_SetKpiCardData(
            g_hwnd, g_kpi_order_id,
            value_data, value_len,
            subtitle_data, subtitle_len,
            trend_data, trend_len,
            1 if g_flip else -1
        )

        value_data, value_len = utf8_arg(visit_value)
        percent_data, percent_len = utf8_arg(visit_pct)
        detail_data, detail_len = utf8_arg(visit_detail)
        ui.dll.EU_SetTrendData(
            g_hwnd, g_trend_visit_id,
            value_data, value_len,
            percent_data, percent_len,
            detail_data, detail_len,
            visit_dir
        )

        value_data, value_len = utf8_arg(latency_value)
        percent_data, percent_len = utf8_arg(latency_pct)
        detail_data, detail_len = utf8_arg(latency_detail)
        ui.dll.EU_SetTrendData(
            g_hwnd, g_trend_latency_id,
            value_data, value_len,
            percent_data, percent_len,
            detail_data, detail_len,
            latency_dir
        )

        for eid, label, desc, status in (
            (g_status_service_id, service_label, service_desc, service_status),
            (g_status_queue_id, queue_label, queue_desc, queue_status),
            (g_status_pay_id, pay_label, pay_desc, pay_status),
        ):
            label_data, label_len = utf8_arg(label)
            desc_data, desc_len = utf8_arg(desc)
            ui.dll.EU_SetStatusDot(g_hwnd, eid, label_data, label_len, desc_data, desc_len, status)

        print("[指标状态] 🔄 已切换演示数据")
    elif element_id == g_dark_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 1)
        print("[主题] 🌙 已切换深色")
    elif element_id == g_light_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 0)
        print("[主题] ☀️ 已切换浅色")
    elif element_id in (
        g_kpi_sales_id, g_kpi_order_id, g_trend_visit_id, g_trend_latency_id,
        g_status_service_id, g_status_queue_id, g_status_pay_id,
    ):
        print(f"[点击] 👆 元素 {element_id}")


def main():
    global g_hwnd
    global g_kpi_sales_id, g_kpi_order_id, g_trend_visit_id, g_trend_latency_id
    global g_status_service_id, g_status_queue_id, g_status_pay_id
    global g_update_id, g_dark_id, g_light_id

    hwnd = ui.create_window("📊 指标与状态展示组件示例", 230, 80, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "📊 指标与状态展示组件", 28, 24, 360, 28)
    ui.create_divider(
        hwnd, content_id,
        "💼 关键指标卡片 / 📈 趋势指标 / 🚦 状态点",
        0, 1, 28, 62, 850, 34
    )

    g_kpi_sales_id = ui.create_kpi_card(
        hwnd, content_id,
        "💰 今日成交额", "291.4万", "📉 较昨日少 17 个活跃客户", "📉 下降 4.2%",
        -1, 28, 112, 260, 132
    )
    g_kpi_order_id = ui.create_kpi_card(
        hwnd, content_id,
        "🧾 订单数量", "15,806", "🛒 复购订单占比 31%", "📉 下降 2.1%",
        -1, 308, 112, 260, 132
    )
    ui.create_kpi_card(
        hwnd, content_id,
        "😊 客服满意度", "96.8%", "💬 抽样 1,248 条会话", "🟦 稳定",
        0, 588, 112, 260, 132
    )

    ui.create_text(hwnd, content_id, "📈 趋势指标", 28, 276, 180, 26)
    g_trend_visit_id = ui.create_trend(
        hwnd, content_id,
        "👥 访问人数", "66,240", "📉 下降 3.7%", "🎯 活动页访问回落到常规水平",
        -1, 28, 314, 400, 104
    )
    g_trend_latency_id = ui.create_trend(
        hwnd, content_id,
        "⚡ 平均响应", "124 毫秒", "⏱️ 上升 22 毫秒", "🛰️ 华东节点需要继续观察",
        -1, 448, 314, 400, 104
    )

    ui.create_text(hwnd, content_id, "🚦 服务状态", 28, 450, 180, 26)
    g_status_service_id = ui.create_status_dot(
        hwnd, content_id,
        "🟢 主服务运行中", "✅ 核心接口可用，错误率 0.03%",
        1, 28, 488, 250, 56
    )
    g_status_queue_id = ui.create_status_dot(
        hwnd, content_id,
        "🟡 消息队列积压", "📬 消费速度低于写入速度",
        2, 308, 488, 250, 56
    )
    g_status_pay_id = ui.create_status_dot(
        hwnd, content_id,
        "🔴 支付通道异常", "🛡️ 备用通道已经自动接管",
        3, 588, 488, 260, 56
    )
    ui.create_status_dot(
        hwnd, content_id,
        "⚪ 灰度发布暂停", "📝 等待下一轮审批",
        4, 28, 558, 250, 56
    )
    ui.create_status_dot(
        hwnd, content_id,
        "🔵 缓存命中稳定", "⚙️ 近十分钟命中率 91%",
        0, 308, 558, 250, 56
    )

    g_update_id = ui.create_button(hwnd, content_id, "🔄", "切换指标数据", 588, 562, 140, 42)
    g_dark_id = ui.create_button(hwnd, content_id, "🌙", "深色主题", 742, 562, 106, 42)
    g_light_id = ui.create_button(hwnd, content_id, "☀️", "浅色主题", 742, 612, 106, 42)

    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        f"🖥️ 窗口宽 {WINDOW_W}、高 {WINDOW_H}，容器宽 {CONTENT_W}、高 {CONTENT_H}；内容右边界 848，底边界 668。",
        0, 0, False,
        28, 626, 530, 42
    )

    for eid in (
        g_kpi_sales_id, g_kpi_order_id, g_trend_visit_id, g_trend_latency_id,
        g_status_service_id, g_status_queue_id, g_status_pay_id,
        g_update_id, g_dark_id, g_light_id,
    ):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📊 指标与状态展示组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("📊 指标与状态展示组件示例结束。")


if __name__ == "__main__":
    main()
