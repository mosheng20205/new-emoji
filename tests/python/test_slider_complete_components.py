import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_single_slider_id = 0
g_range_slider_id = 0
g_status_id = 0
g_apply_id = 0
g_toggle_id = 0
g_slider_callback = None


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Slider 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.ValueCallback
def on_slider_value(element_id, value, range_start, range_end):
    if element_id == g_range_slider_id:
        print(f"[滑块回调] 范围={range_start}-{range_end} 当前={value}")
        update_status(f"🎚️ 范围滑块回调：{range_start} - {range_end}，当前终点 {value}")
    else:
        print(f"[滑块回调] 单值={value}")
        update_status(f"🎚️ 单值滑块回调：当前 {value}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.dll.EU_SetSliderValue(g_hwnd, g_single_slider_id, 75)
        ui.set_slider_range_value(g_hwnd, g_range_slider_id, 25, 85)
        single = ui.dll.EU_GetSliderValue(g_hwnd, g_single_slider_id)
        range_value = ui.get_slider_range_value(g_hwnd, g_range_slider_id)
        range_mode = ui.get_slider_range_mode(g_hwnd, g_range_slider_id)
        print("[读取] 单值:", single, "范围值:", range_value, "范围模式:", range_mode)
        update_status(f"✅ 已写入并读回：单值 {single}，范围 {range_value[0]} - {range_value[1]}")
    elif element_id == g_toggle_id:
        enabled, start_value, end_value = ui.get_slider_range_mode(g_hwnd, g_range_slider_id)
        ui.set_slider_range_mode(g_hwnd, g_range_slider_id, not enabled, start_value, end_value)
        print("[切换] 范围模式:", ui.get_slider_range_mode(g_hwnd, g_range_slider_id))
        update_status("🔁 已切换范围模式，可用键盘方向键继续验证焦点滑块")


def main():
    global g_hwnd, g_single_slider_id, g_range_slider_id, g_status_id
    global g_apply_id, g_toggle_id, g_slider_callback

    hwnd = ui.create_window("🎚️ Slider 完整封装验证", 220, 110, 920, 600)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_slider_callback = on_slider_value
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 550)
    ui.create_text(hwnd, content_id, "🎚️ 滑块组件完整能力", 28, 24, 420, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "本窗口验证单值滑块、双滑块范围选择、步进吸附、浮动提示、键盘操作、状态读回和数值变化回调。",
        28, 72, 760, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "📍 单值进度", 36, 150, 180, 26)
    g_single_slider_id = ui.create_slider(
        hwnd, content_id, "完成度 🎯", 0, 100, 40,
        36, 184, 520, 72, step=5, show_tooltip=True,
    )
    ui.dll.EU_SetSliderValueCallback(hwnd, g_single_slider_id, g_slider_callback)

    ui.create_text(hwnd, content_id, "📏 范围选择", 36, 280, 180, 26)
    g_range_slider_id = ui.create_slider(
        hwnd, content_id, "预算范围 💰", 0, 100, 70,
        36, 314, 520, 72, step=5, show_tooltip=True,
    )
    ui.set_slider_range_mode(hwnd, g_range_slider_id, True, 20, 70)
    ui.dll.EU_SetSliderValueCallback(hwnd, g_range_slider_id, g_slider_callback)

    panel_id = ui.create_panel(hwnd, content_id, 610, 150, 250, 236)
    ui.set_panel_style(hwnd, panel_id, 0x10E6A23C, 0x66E6A23C, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "🧪 验证状态", 0, 0, 180, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待操作，窗口会自动写入一次状态。", 0, 48, 210, 120)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "写入并读取", 610, 420, 140, 42)
    g_toggle_id = ui.create_button(hwnd, content_id, "🔁", "切换范围模式", 36, 420, 170, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("Slider 完整封装验证已显示。窗口会保持 60 秒。")
    print("[初始] 单值:", ui.dll.EU_GetSliderValue(hwnd, g_single_slider_id))
    print("[初始] 范围:", ui.get_slider_range_mode(hwnd, g_range_slider_id), ui.get_slider_options(hwnd, g_range_slider_id))

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_done = False
    while running and time.time() - start < 60:
        if not auto_done and time.time() - start > 1.0:
            on_click(g_apply_id)
            auto_done = True
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

    print("Slider 完整封装验证结束。")


if __name__ == "__main__":
    main()
