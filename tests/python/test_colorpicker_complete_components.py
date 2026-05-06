import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 960
WINDOW_H = 660
CONTENT_W = 920
CONTENT_H = 600

PREDEFINE_COLORS = [
    0xFFFF4500,
    0xFFFF8C00,
    0xFFFFD700,
    0xFF90EE90,
    0xFF00CED1,
    0xFF1E90FF,
    0xFFC71585,
    0xADFF4500,
    0xFFFF7800,
    0xFFFAE900,
    0x8FFFE699,
    0xFF00BBC0,
    0xBA1F8EFF,
    0x77C71585,
]

g_hwnd = None
g_color_id = 0
g_empty_id = 0
g_alpha_id = 0
g_status_id = 0
g_apply_id = 0
g_clear_id = 0
g_invalid_id = 0
g_change_callback = None
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] ColorPicker 全样式验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.ValueCallback
def on_color_change(element_id, argb_value, alpha, palette_count):
    argb = argb_value & 0xFFFFFFFF
    g_events.append((element_id, argb, alpha, palette_count))
    update_status(f"🎨 回调：元素 {element_id}，颜色 0x{argb:08X}，透明度 {alpha}，预设色 {palette_count} 个")


def assert_colorpicker_state():
    assert ui.get_colorpicker_has_value(g_hwnd, g_color_id) is True
    assert ui.get_colorpicker_color(g_hwnd, g_color_id) == 0xFF409EFF
    assert ui.get_colorpicker_hex(g_hwnd, g_color_id) == "#409EFF"

    assert ui.get_colorpicker_has_value(g_hwnd, g_empty_id) is False
    assert ui.get_colorpicker_color(g_hwnd, g_empty_id) == 0
    assert ui.get_colorpicker_hex(g_hwnd, g_empty_id) == ""

    alpha_options = ui.get_colorpicker_options(g_hwnd, g_alpha_id)
    assert alpha_options == {"show_alpha": True, "size": 0, "clearable": True}
    assert ui.get_colorpicker_alpha(g_hwnd, g_alpha_id) == 173
    assert ui.get_colorpicker_hex(g_hwnd, g_alpha_id) == "#ADFF4500"
    assert ui.get_colorpicker_palette_count(g_hwnd, g_alpha_id) == len(PREDEFINE_COLORS)

    assert ui.set_colorpicker_hex(g_hwnd, g_color_id, "#12ABEF") is True
    assert ui.get_colorpicker_color(g_hwnd, g_color_id) == 0xFF12ABEF
    assert ui.get_colorpicker_hex(g_hwnd, g_color_id) == "#12ABEF"
    ui.set_colorpicker_color(g_hwnd, g_color_id, 0xFF409EFF)

    for size, picker_id in enumerate(g_size_ids):
        options = ui.get_colorpicker_options(g_hwnd, picker_id)
        assert options["size"] == size
        assert options["show_alpha"] is False
        assert options["clearable"] is True


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_colorpicker_hex(g_hwnd, g_empty_id, "#8843A047")
        assert ui.get_colorpicker_has_value(g_hwnd, g_empty_id) is True
        assert ui.get_colorpicker_hex(g_hwnd, g_empty_id) == "#43A047"
        assert ui.get_colorpicker_alpha(g_hwnd, g_empty_id) == 136
        update_status("✅ 空值选择器已设置为半透明绿色，并自动恢复为有值态。")
    elif element_id == g_clear_id:
        ui.clear_colorpicker(g_hwnd, g_alpha_id)
        assert ui.get_colorpicker_has_value(g_hwnd, g_alpha_id) is False
        assert ui.get_colorpicker_color(g_hwnd, g_alpha_id) == 0
        update_status("🧹 已清空透明度选择器，颜色与文本读回均为空。")
    elif element_id == g_invalid_id:
        before = ui.get_colorpicker_color(g_hwnd, g_color_id)
        ok = ui.set_colorpicker_hex(g_hwnd, g_color_id, "#GGGGGG")
        after = ui.get_colorpicker_color(g_hwnd, g_color_id)
        assert ok is False
        assert before == after
        update_status("🛡️ 非法十六进制输入已被拒绝，原颜色保持不变。")


g_size_ids = []


def main():
    global g_hwnd, g_color_id, g_empty_id, g_alpha_id, g_status_id
    global g_apply_id, g_clear_id, g_invalid_id, g_change_callback, g_size_ids

    hwnd = ui.create_window("🎨 ColorPicker 全样式验证", 220, 110, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_change_callback = on_color_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    ui.create_text(hwnd, content_id, "🎨 颜色选择器全样式", 28, 24, 420, 34)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "覆盖默认值、空值、透明度开关、预设色、四种尺寸、清空、回调和非法输入校验。",
        28,
        66,
        820,
        44,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_color_id = ui.create_colorpicker(
        hwnd, content_id, "有默认值", 0xFF409EFF, 36, 126, 320, 42
    )
    g_empty_id = ui.create_colorpicker(
        hwnd, content_id, "无默认值", None, 36, 184, 320, 42
    )
    g_alpha_id = ui.create_colorpicker(
        hwnd,
        content_id,
        "透明度",
        0xADFF4500,
        36,
        242,
        360,
        42,
        show_alpha=True,
        palette=PREDEFINE_COLORS,
        open_panel=True,
    )
    for picker_id in (g_color_id, g_empty_id, g_alpha_id):
        ui.set_colorpicker_change_callback(hwnd, picker_id, g_change_callback)

    size_panel = ui.create_panel(hwnd, content_id, 450, 126, 410, 250)
    ui.set_panel_style(hwnd, size_panel, 0x1200CED1, 0x6600CED1, 1.0, 10.0, 18)
    ui.create_text(hwnd, size_panel, "📏 尺寸矩阵", 20, 12, 220, 30)
    size_specs = [
        ("默认", 0, 42),
        ("中等", 1, 38),
        ("小型", 2, 34),
        ("超小", 3, 30),
    ]
    g_size_ids = []
    for index, (label, size, height) in enumerate(size_specs):
        y = 54 + index * 45
        picker_id = ui.create_colorpicker(
            hwnd,
            size_panel,
            f"{label}色",
            0xFF409EFF,
            24,
            y,
            300,
            height,
            size=size,
        )
        g_size_ids.append(picker_id)

    status_panel = ui.create_panel(hwnd, content_id, 36, 454, 824, 92)
    ui.set_panel_style(hwnd, status_panel, 0x1000ACC1, 0x6600ACC1, 1.0, 10.0, 18)
    g_status_id = ui.create_text(hwnd, status_panel, "等待验证。", 20, 18, 760, 54)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "设置空值", 36, 392, 140, 40)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空透明度", 194, 392, 150, 40)
    g_invalid_id = ui.create_button(hwnd, content_id, "🛡️", "非法输入", 362, 392, 140, 40)
    for button_id in (g_apply_id, g_clear_id, g_invalid_id):
        ui.dll.EU_SetElementClickCallback(hwnd, button_id, on_click)

    assert_colorpicker_state()
    ui.dll.EU_ShowWindow(hwnd, 1)
    update_status("✅ 初始状态验证通过：默认值、空值、透明度、预设色和四种尺寸均可读回。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_stage = 0
    while running and time.time() - start < 8:
        elapsed = time.time() - start
        if auto_stage == 0 and elapsed > 0.6:
            on_click(g_apply_id)
            auto_stage = 1
        elif auto_stage == 1 and elapsed > 1.2:
            on_click(g_clear_id)
            auto_stage = 2
        elif auto_stage == 2 and elapsed > 1.8:
            on_click(g_invalid_id)
            auto_stage = 3
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

    assert len(g_events) >= 2
    print("ColorPicker 全样式验证结束。")


if __name__ == "__main__":
    main()
