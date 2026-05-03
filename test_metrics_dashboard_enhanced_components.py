import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_kpi_id = 0
g_trend_id = 0
g_status_id = 0
g_gauge_id = 0
g_ring_id = 0
g_bullet_id = 0
g_update_id = 0
g_loading_id = 0
g_flip = False
g_loading = False


def utf8_arg(text):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 指标看板增强组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_flip, g_loading

    if element_id == g_loading_id:
        g_loading = not g_loading
        ui.set_kpi_card_options(
            g_hwnd, g_kpi_id,
            loading=g_loading,
            helper="⏳ 正在刷新关键指标" if g_loading else "🧾 样本 12,480 条",
        )
        print(f"[KPI] loading={g_loading}")
        return

    if element_id != g_update_id:
        print(f"[点击] 元素 #{element_id}")
        return

    g_flip = not g_flip
    if g_flip:
        kpi_value, kpi_sub, kpi_trend, kpi_type = "386.2万", "🚀 新增客户 68 个", "上升 13.2%", 1
        trend_value, trend_pct, trend_detail, direction = "118 毫秒", "下降 22 毫秒", "✅ 延迟降低是好事", -1
        status_label, status_desc, status = "🟢 服务健康", "✅ 所有节点通过巡检", 1
        gauge_value, gauge_caption, gauge_status = 82, "⚠️ 接近容量阈值", 0
        ring_value, ring_label, ring_status = 94, "✅ 质量通过率", 1
        bullet_value, bullet_target, bullet_desc, bullet_status = 88, 90, "🚚 距离目标还差 2%", 0
    else:
        kpi_value, kpi_sub, kpi_trend, kpi_type = "241.7万", "📉 老客回访下降", "下降 5.8%", -1
        trend_value, trend_pct, trend_detail, direction = "156 毫秒", "上升 36 毫秒", "⚠️ 延迟上升需要关注", 1
        status_label, status_desc, status = "🔴 服务告警", "🛡️ 备用链路已接管", 3
        gauge_value, gauge_caption, gauge_status = 96, "🔥 超过危险阈值", 0
        ring_value, ring_label, ring_status = 67, "🧪 质量复检中", 2
        bullet_value, bullet_target, bullet_desc, bullet_status = 52, 85, "⏱️ 交付节奏偏慢", 0

    value_data, value_len = utf8_arg(kpi_value)
    sub_data, sub_len = utf8_arg(kpi_sub)
    trend_data, trend_len = utf8_arg(kpi_trend)
    ui.dll.EU_SetKpiCardData(g_hwnd, g_kpi_id, value_data, value_len, sub_data, sub_len,
                             trend_data, trend_len, kpi_type)

    value_data, value_len = utf8_arg(trend_value)
    pct_data, pct_len = utf8_arg(trend_pct)
    detail_data, detail_len = utf8_arg(trend_detail)
    ui.dll.EU_SetTrendData(g_hwnd, g_trend_id, value_data, value_len, pct_data, pct_len,
                           detail_data, detail_len, direction)

    label_data, label_len = utf8_arg(status_label)
    desc_data, desc_len = utf8_arg(status_desc)
    ui.dll.EU_SetStatusDot(g_hwnd, g_status_id, label_data, label_len, desc_data, desc_len, status)

    caption_data, caption_len = utf8_arg(gauge_caption)
    ui.dll.EU_SetGaugeValue(g_hwnd, g_gauge_id, gauge_value, caption_data, caption_len, gauge_status)

    ring_data, ring_len = utf8_arg(ring_label)
    ui.dll.EU_SetRingProgressValue(g_hwnd, g_ring_id, ring_value, ring_data, ring_len, ring_status)

    bullet_data, bullet_len = utf8_arg(bullet_desc)
    ui.dll.EU_SetBulletProgressValue(
        g_hwnd, g_bullet_id, bullet_value, bullet_target, bullet_data, bullet_len, bullet_status
    )

    print(
        "[读回] kpi={kpi_opts} trend={trend}/{trend_opts} status={status}/{status_opts} "
        "gauge={gauge}/{gauge_status}/{gauge_opts} ring={ring}/{ring_status}/{ring_opts} "
        "bullet={bullet}/{target}/{bullet_status}/{bullet_opts}".format(
            kpi_opts=ui.get_kpi_card_options(g_hwnd, g_kpi_id),
            trend=ui.get_trend_direction(g_hwnd, g_trend_id),
            trend_opts=ui.get_trend_options(g_hwnd, g_trend_id),
            status=ui.get_status_dot_status(g_hwnd, g_status_id),
            status_opts=ui.get_status_dot_options(g_hwnd, g_status_id),
            gauge=ui.get_gauge_value(g_hwnd, g_gauge_id),
            gauge_status=ui.get_gauge_status(g_hwnd, g_gauge_id),
            gauge_opts=ui.get_gauge_options(g_hwnd, g_gauge_id),
            ring=ui.get_ring_progress_value(g_hwnd, g_ring_id),
            ring_status=ui.get_ring_progress_status(g_hwnd, g_ring_id),
            ring_opts=ui.get_ring_progress_options(g_hwnd, g_ring_id),
            bullet=ui.get_bullet_progress_value(g_hwnd, g_bullet_id),
            target=ui.get_bullet_progress_target(g_hwnd, g_bullet_id),
            bullet_status=ui.get_bullet_progress_status(g_hwnd, g_bullet_id),
            bullet_opts=ui.get_bullet_progress_options(g_hwnd, g_bullet_id),
        )
    )


def main():
    global g_hwnd, g_kpi_id, g_trend_id, g_status_id
    global g_gauge_id, g_ring_id, g_bullet_id, g_update_id, g_loading_id

    hwnd = ui.create_window("📈 指标看板增强组件", 220, 70, 1060, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 1020, 700)
    ui.create_text(hwnd, content_id, "📈 指标与看板增强批次", 28, 22, 360, 34)

    g_kpi_id = ui.create_kpi_card(
        hwnd, content_id,
        "💰 成交额", "241.7万", "📉 老客回访下降", "下降 5.8%",
        -1, 28, 76, 300, 142,
    )
    ui.set_kpi_card_options(hwnd, g_kpi_id, loading=False, helper="🧾 样本 12,480 条")

    g_trend_id = ui.create_trend(
        hwnd, content_id,
        "⚡ 接口延迟", "156 毫秒", "上升 36 毫秒", "⚠️ 延迟上升需要关注",
        1, 360, 76, 300, 112,
    )
    ui.set_trend_options(hwnd, g_trend_id, inverse=True, show_icon=True)

    g_status_id = ui.create_status_dot(
        hwnd, content_id,
        "🔴 服务告警", "🛡️ 备用链路已接管",
        3, 700, 76, 270, 72,
    )
    ui.set_status_dot_options(hwnd, g_status_id, pulse=True, compact=False)
    compact_id = ui.create_status_dot(
        hwnd, content_id,
        "🟢 缓存稳定", "命中率 91%",
        1, 700, 160, 270, 38,
    )
    ui.set_status_dot_options(hwnd, compact_id, pulse=False, compact=True)

    g_gauge_id = ui.create_gauge(
        hwnd, content_id,
        "🎚️ 容量水位", 96, "🔥 超过危险阈值", 0,
        28, 262, 300, 260,
    )
    ui.set_gauge_options(hwnd, g_gauge_id, 0, 100, 70, 90, 16)

    g_ring_id = ui.create_ring_progress(
        hwnd, content_id,
        "⭕ 质量通过率", 67, "🧪 质量复检中", 2,
        360, 262, 280, 260,
    )
    ui.set_ring_progress_options(hwnd, g_ring_id, stroke_width=22, show_center=True)

    g_bullet_id = ui.create_bullet_progress(
        hwnd, content_id,
        "🚚 交付进度", "⏱️ 交付节奏偏慢", 52, 85, 0,
        680, 298, 300, 126,
    )
    ui.set_bullet_progress_options(hwnd, g_bullet_id, good_threshold=80, warn_threshold=60, show_target=True)
    no_target_id = ui.create_bullet_progress(
        hwnd, content_id,
        "🧪 缺陷修复", "✅ 本轮修复稳定", 86, 90, 0,
        680, 446, 300, 106,
    )
    ui.set_bullet_progress_options(hwnd, no_target_id, good_threshold=75, warn_threshold=55, show_target=False)

    g_update_id = ui.create_button(hwnd, content_id, "🔄", "切换读回数据", 28, 580, 150, 42)
    g_loading_id = ui.create_button(hwnd, content_id, "⏳", "切换加载态", 198, 580, 140, 42)
    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        "🖥️ 当前内容右边界 980，底边界 622；首次打开无需缩放即可完整查看。",
        0, 0, False,
        360, 580, 620, 42,
    )

    for eid in (g_kpi_id, g_trend_id, g_status_id, g_gauge_id, g_ring_id,
                g_bullet_id, g_update_id, g_loading_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    print(
        "[初始读回] kpi={kpi_opts} trend={trend_opts} status={status}/{status_opts} "
        "gauge={gauge}/{gauge_opts} ring={ring}/{ring_opts} bullet={bullet}/{target}/{bullet_opts}".format(
            kpi_opts=ui.get_kpi_card_options(hwnd, g_kpi_id),
            trend_opts=ui.get_trend_options(hwnd, g_trend_id),
            gauge=ui.get_gauge_value(hwnd, g_gauge_id),
            gauge_opts=ui.get_gauge_options(hwnd, g_gauge_id),
            ring=ui.get_ring_progress_value(hwnd, g_ring_id),
            ring_opts=ui.get_ring_progress_options(hwnd, g_ring_id),
            bullet=ui.get_bullet_progress_value(hwnd, g_bullet_id),
            target=ui.get_bullet_progress_target(hwnd, g_bullet_id),
            status=ui.get_status_dot_status(hwnd, g_status_id),
            status_opts=ui.get_status_dot_options(hwnd, g_status_id),
            bullet_opts=ui.get_bullet_progress_options(hwnd, g_bullet_id),
        )
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📈 指标看板增强组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("📈 指标看板增强组件示例结束。")


if __name__ == "__main__":
    main()
