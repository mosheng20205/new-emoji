import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 920
WINDOW_H = 630
CONTENT_W = 900
CONTENT_H = 580

g_hwnd = None
g_color_id = 0
g_status_id = 0
g_apply_id = 0
g_invalid_id = 0
g_change_callback = None
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] ColorPicker 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.ValueCallback
def on_color_change(element_id, argb_value, alpha, palette_count):
    argb = argb_value & 0xFFFFFFFF
    g_events.append((element_id, argb, alpha, palette_count))
    print(f"[颜色回调] 元素={element_id} 颜色=0x{argb:08X} 透明度={alpha} 预设={palette_count}")
    update_status(f"🎨 回调：0x{argb:08X}，透明度 {alpha}，预设色 {palette_count} 个")


def print_state(prefix):
    color = ui.get_colorpicker_color(g_hwnd, g_color_id) & 0xFFFFFFFF
    print(
        f"{prefix} 颜色=0x{color:08X} 文本={ui.get_colorpicker_hex(g_hwnd, g_color_id)} "
        f"透明度={ui.get_colorpicker_alpha(g_hwnd, g_color_id)} "
        f"打开={ui.get_colorpicker_open(g_hwnd, g_color_id)} "
        f"预设={ui.get_colorpicker_palette_count(g_hwnd, g_color_id)} "
        f"回调次数={len(g_events)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_colorpicker_palette(
            g_hwnd,
            g_color_id,
            [0xFF1E66F5, 0xFF43A047, 0xFFFFB300, 0xFFE53935, 0xFF8E24AA, 0xFF00ACC1],
        )
        ok_hex = ui.set_colorpicker_hex(g_hwnd, g_color_id, "#8843A047")
        ui.set_colorpicker_open(g_hwnd, g_color_id, True)
        update_status(f"✅ 十六进制设置成功：{ok_hex}，当前 {ui.get_colorpicker_hex(g_hwnd, g_color_id)}")
        print_state("[应用状态]")
    elif element_id == g_invalid_id:
        before = ui.get_colorpicker_color(g_hwnd, g_color_id) & 0xFFFFFFFF
        ok_hex = ui.set_colorpicker_hex(g_hwnd, g_color_id, "#GGGGGG")
        after = ui.get_colorpicker_color(g_hwnd, g_color_id) & 0xFFFFFFFF
        update_status(f"🛡️ 非法颜色被拒绝：{not ok_hex}，颜色保持：{before == after}")
        print("[非法输入]", ok_hex, f"before=0x{before:08X}", f"after=0x{after:08X}")
        print_state("[非法状态]")


def main():
    global g_hwnd, g_color_id, g_status_id, g_apply_id, g_invalid_id, g_change_callback

    hwnd = ui.create_window("🎨 ColorPicker 完整封装验证", 220, 110, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_change_callback = on_color_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    ui.create_text(hwnd, content_id, "🎨 颜色选择器完整能力", 28, 24, 420, 34)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证预设色面板、透明度、十六进制文本输入校验、读回、变化回调和首次窗口尺寸适配。",
        28,
        68,
        800,
        52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_color_id = ui.create_colorpicker(
        hwnd,
        content_id,
        "主题色",
        0xFF1E66F5,
        36,
        150,
        360,
        42,
        alpha=255,
        open_panel=True,
    )
    ui.set_colorpicker_change_callback(hwnd, g_color_id, g_change_callback)

    panel_id = ui.create_panel(hwnd, content_id, 470, 150, 360, 210)
    ui.set_panel_style(hwnd, panel_id, 0x1000ACC1, 0x6600ACC1, 1.0, 12.0, 18)
    ui.create_text(hwnd, panel_id, "🔎 状态读回", 0, 0, 220, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待自动设置颜色。", 0, 48, 290, 108)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "设置半透明绿", 470, 392, 160, 42)
    g_invalid_id = ui.create_button(hwnd, content_id, "🛡️", "验证非法输入", 650, 392, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_invalid_id, on_click)

    ui.create_alert(
        hwnd,
        content_id,
        "📐 首屏尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 830，最下内容约 434，保留足够逻辑余量。",
        0,
        0,
        False,
        36,
        480,
        790,
        60,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("ColorPicker 完整封装验证已显示。窗口会保持 60 秒。")
    print_state("[初始状态]")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_stage = 0
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if auto_stage == 0 and elapsed > 1.0:
            on_click(g_apply_id)
            auto_stage = 1
        elif auto_stage == 1 and elapsed > 3.0:
            on_click(g_invalid_id)
            auto_stage = 2
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

    print("ColorPicker 完整封装验证结束。")


if __name__ == "__main__":
    main()
