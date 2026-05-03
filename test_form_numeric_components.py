import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_slider_id = 0
g_input_number_id = 0
g_rate_id = 0
g_color_id = 0
g_apply_id = 0
g_reset_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 数值表单组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.dll.EU_SetSliderOptions(g_hwnd, g_slider_id, 5, 1)
        ui.dll.EU_SetSliderValue(g_hwnd, g_slider_id, 65)

        ui.dll.EU_SetInputNumberRange(g_hwnd, g_input_number_id, -20, 80)
        ui.dll.EU_SetInputNumberStep(g_hwnd, g_input_number_id, 5)
        ui.dll.EU_SetInputNumberValue(g_hwnd, g_input_number_id, 40)

        ui.dll.EU_SetRateOptions(g_hwnd, g_rate_id, 1, 1, 0)
        ui.dll.EU_SetRateValueX2(g_hwnd, g_rate_id, 7)

        palette = (ctypes.c_uint32 * 8)(
            0xFF1E66F5, 0xFF43A047, 0xFFFFB300, 0xFFE53935,
            0xFF8E24AA, 0xFF00ACC1, 0xFF303133, 0xFFFFFFFF
        )
        ui.dll.EU_SetColorPickerPalette(g_hwnd, g_color_id, palette, 8)
        ui.dll.EU_SetColorPickerColor(g_hwnd, g_color_id, 0xFF43A047)
        ui.dll.EU_SetColorPickerAlpha(g_hwnd, g_color_id, 168)
        ui.dll.EU_SetColorPickerOpen(g_hwnd, g_color_id, 1)

        print(
            "[应用] "
            f"滑块={ui.dll.EU_GetSliderValue(g_hwnd, g_slider_id)} "
            f"步进={ui.dll.EU_GetSliderStep(g_hwnd, g_slider_id)} "
            f"数字={ui.dll.EU_GetInputNumberValue(g_hwnd, g_input_number_id)} "
            f"半星={ui.dll.EU_GetRateValueX2(g_hwnd, g_rate_id)}/2 "
            f"透明度={ui.dll.EU_GetColorPickerAlpha(g_hwnd, g_color_id)}"
        )
    elif element_id == g_reset_id:
        ui.dll.EU_SetSliderOptions(g_hwnd, g_slider_id, 10, 1)
        ui.dll.EU_SetSliderValue(g_hwnd, g_slider_id, 30)
        ui.dll.EU_SetInputNumberRange(g_hwnd, g_input_number_id, 0, 100)
        ui.dll.EU_SetInputNumberStep(g_hwnd, g_input_number_id, 10)
        ui.dll.EU_SetInputNumberValue(g_hwnd, g_input_number_id, 20)
        ui.dll.EU_SetRateOptions(g_hwnd, g_rate_id, 1, 1, 0)
        ui.dll.EU_SetRateValueX2(g_hwnd, g_rate_id, 9)
        ui.dll.EU_SetColorPickerColor(g_hwnd, g_color_id, 0xFF1E66F5)
        ui.dll.EU_SetColorPickerAlpha(g_hwnd, g_color_id, 255)
        ui.dll.EU_SetColorPickerOpen(g_hwnd, g_color_id, 0)
        print("[重置] 已恢复默认数值状态")


def main():
    global g_hwnd, g_slider_id, g_input_number_id, g_rate_id, g_color_id
    global g_apply_id, g_reset_id

    hwnd = ui.create_window("🎚️ 数值表单组件测试", 220, 120, 900, 620)
    if not hwnd:
        print("ERROR: failed to create window")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 570)

    ui.create_text(hwnd, content_id, "🎛️ 数值输入与选择", 24, 18, 280, 30)
    ui.create_divider(hwnd, content_id, "滑块 / 数字输入 / 评分 / 颜色", 0, 1, 24, 56, 820, 26)

    ui.create_text(hwnd, content_id, "📏 滑块步进与提示", 24, 94, 220, 26)
    g_slider_id = ui.create_slider(
        hwnd, content_id, "进度值 🎚️", 0, 100, 30,
        24, 126, 420, 72, step=10, show_tooltip=True
    )

    ui.create_text(hwnd, content_id, "🔢 数字输入边界", 24, 220, 220, 26)
    g_input_number_id = ui.create_input_number(
        hwnd, content_id, "数量 🧮", 20, 0, 100, 10,
        24, 254, 320, 42
    )
    ui.create_text(hwnd, content_id, "按住右侧上下按钮会连续调整，边界值会自动夹紧。", 24, 306, 520, 28)

    ui.create_text(hwnd, content_id, "⭐ 半星评分", 470, 94, 180, 26)
    g_rate_id = ui.create_rate(
        hwnd, content_id, "满意度 ✨", 4, 5,
        470, 126, 340, 42, allow_clear=True, allow_half=True, value_x2=9
    )

    ui.create_text(hwnd, content_id, "🎨 颜色与透明度", 470, 220, 220, 26)
    g_color_id = ui.create_colorpicker(
        hwnd, content_id, "主题色 🌈", 0xFF1E66F5,
        470, 254, 320, 42, alpha=255, open_panel=True,
        palette=[0xFF1E66F5, 0xFF43A047, 0xFFFFB300, 0xFFE53935,
                 0xFF8E24AA, 0xFF00ACC1, 0xFF303133, 0xFFFFFFFF]
    )

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "应用演示状态", 470, 414, 160, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "🔄", "恢复默认状态", 646, 414, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "🧪 验证重点",
        "本窗口覆盖 Slider 步进与浮动提示、InputNumber 连续步进、Rate 半星只读选项、ColorPicker 预设色和透明度状态。",
        24, 384, 420, 96
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("数值表单组件测试窗口已显示，60 秒后自动结束。")

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

    print("数值表单组件测试结束。")


if __name__ == "__main__":
    main()
