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
WINDOW_H = 800
CONTENT_W = 960
CONTENT_H = 750

g_hwnd = None
g_gauge_id = 0
g_ring_quality_id = 0
g_ring_plan_id = 0
g_bullet_cpu_id = 0
g_bullet_memory_id = 0
g_bullet_delivery_id = 0
g_update_id = 0
g_dark_id = 0
g_light_id = 0
g_flip = False


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 🎛️ 进度看板组件示例正在关闭")
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
            gauge_value, gauge_caption, gauge_status = 91, "🚀 系统负载健康", 1
            quality_value, quality_label, quality_status = 96, "✅ 质量达标", 1
            plan_value, plan_label, plan_status = 78, "📦 发布完成率", 0
            cpu_value, cpu_target, cpu_desc, cpu_status = 42, 75, "🧊 CPU 余量充足", 1
            mem_value, mem_target, mem_desc, mem_status = 58, 80, "🧠 内存曲线稳定", 0
            delivery_value, delivery_target, delivery_desc, delivery_status = 88, 90, "🚚 交付接近目标", 2
            print("[进度看板] 🔄 已切换到健康数据")
        else:
            gauge_value, gauge_caption, gauge_status = 64, "⚠️ 高峰压力观察中", 2
            quality_value, quality_label, quality_status = 82, "🧪 质量复检中", 2
            plan_value, plan_label, plan_status = 51, "📦 发布推进中", 0
            cpu_value, cpu_target, cpu_desc, cpu_status = 76, 70, "🔥 CPU 超过预警线", 3
            mem_value, mem_target, mem_desc, mem_status = 69, 78, "🧠 内存仍在可控区间", 2
            delivery_value, delivery_target, delivery_desc, delivery_status = 63, 85, "🚚 交付节奏偏慢", 2
            print("[进度看板] 🔄 已切换到观察数据")

        caption_data, caption_len = utf8_arg(gauge_caption)
        ui.dll.EU_SetGaugeValue(g_hwnd, g_gauge_id, gauge_value, caption_data, caption_len, gauge_status)

        label_data, label_len = utf8_arg(quality_label)
        ui.dll.EU_SetRingProgressValue(g_hwnd, g_ring_quality_id, quality_value, label_data, label_len, quality_status)
        label_data, label_len = utf8_arg(plan_label)
        ui.dll.EU_SetRingProgressValue(g_hwnd, g_ring_plan_id, plan_value, label_data, label_len, plan_status)

        for eid, value, target, desc, status in (
            (g_bullet_cpu_id, cpu_value, cpu_target, cpu_desc, cpu_status),
            (g_bullet_memory_id, mem_value, mem_target, mem_desc, mem_status),
            (g_bullet_delivery_id, delivery_value, delivery_target, delivery_desc, delivery_status),
        ):
            desc_data, desc_len = utf8_arg(desc)
            ui.dll.EU_SetBulletProgressValue(g_hwnd, eid, value, target, desc_data, desc_len, status)
    elif element_id == g_dark_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 1)
        print("[主题] 🌙 已切换深色")
    elif element_id == g_light_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 0)
        print("[主题] ☀️ 已切换浅色")
    elif element_id in (
        g_gauge_id, g_ring_quality_id, g_ring_plan_id,
        g_bullet_cpu_id, g_bullet_memory_id, g_bullet_delivery_id,
    ):
        print(f"[点击] 👆 看板元素 {element_id}")


def main():
    global g_hwnd, g_gauge_id, g_ring_quality_id, g_ring_plan_id
    global g_bullet_cpu_id, g_bullet_memory_id, g_bullet_delivery_id
    global g_update_id, g_dark_id, g_light_id

    hwnd = ui.create_window("🎛️ 进度看板组件示例", 220, 70, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "🎛️ 进度看板组件", 28, 24, 330, 28)
    ui.create_divider(
        hwnd, content_id,
        "🎚️ 仪表盘 / ⭕ 环形进度 / 🧭 子弹进度",
        0, 1, 28, 62, 880, 34
    )

    g_gauge_id = ui.create_gauge(
        hwnd, content_id,
        "🎚️ 服务健康度", 64, "⚠️ 高峰压力观察中", 2,
        28, 114, 300, 260
    )
    g_ring_quality_id = ui.create_ring_progress(
        hwnd, content_id,
        "⭕ 质量通过率", 82, "🧪 质量复检中", 2,
        348, 114, 260, 260
    )
    g_ring_plan_id = ui.create_ring_progress(
        hwnd, content_id,
        "📦 发布完成率", 51, "📦 发布推进中", 0,
        628, 114, 280, 260
    )

    ui.create_text(hwnd, content_id, "🧭 资源与交付进度", 28, 410, 260, 26)
    g_bullet_cpu_id = ui.create_bullet_progress(
        hwnd, content_id,
        "🔥 CPU 使用率", "🔥 CPU 超过预警线", 76, 70, 3,
        28, 452, 420, 108
    )
    g_bullet_memory_id = ui.create_bullet_progress(
        hwnd, content_id,
        "🧠 内存占用", "🧠 内存仍在可控区间", 69, 78, 2,
        488, 452, 420, 108
    )
    g_bullet_delivery_id = ui.create_bullet_progress(
        hwnd, content_id,
        "🚚 交付进度", "🚚 交付节奏偏慢", 63, 85, 2,
        28, 574, 420, 108
    )

    ui.create_infobox(
        hwnd, content_id,
        "🧪 批次说明",
        "本批新增三个看板型纯 D2D 组件：仪表盘、环形进度和子弹进度条，均支持中文与 emoji。",
        488, 574, 420, 78
    )

    g_update_id = ui.create_button(hwnd, content_id, "🔄", "切换看板数据", 488, 660, 142, 42)
    g_dark_id = ui.create_button(hwnd, content_id, "🌙", "深色主题", 646, 660, 118, 42)
    g_light_id = ui.create_button(hwnd, content_id, "☀️", "浅色主题", 780, 660, 118, 42)

    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        "🖥️ 首屏已适配：右 908，底 728。",
        0, 0, False,
        28, 686, 420, 42
    )

    for eid in (
        g_gauge_id, g_ring_quality_id, g_ring_plan_id,
        g_bullet_cpu_id, g_bullet_memory_id, g_bullet_delivery_id,
        g_update_id, g_dark_id, g_light_id,
    ):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("🎛️ 进度看板组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("🎛️ 进度看板组件示例结束。")


if __name__ == "__main__":
    main()
