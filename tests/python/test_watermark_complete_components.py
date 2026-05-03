import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_watermark_id = 0
g_container_id = 0
g_click_id = 0
g_toggle_id = 0
g_clicks = 0


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 水印完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_clicks
    if element_id == g_click_id:
        g_clicks += 1
        print(f"[穿透点击] 底层按钮已收到点击：{g_clicks}")
    elif element_id == g_toggle_id:
        ui.set_watermark_layer(g_hwnd, g_watermark_id, g_container_id, True, True, 20)
        print(f"[覆盖层] 状态：{ui.get_watermark_full_options(g_hwnd, g_watermark_id)}")


def main():
    global g_hwnd, g_watermark_id, g_container_id, g_click_id, g_toggle_id

    hwnd = ui.create_window("💧 水印完整组件验证", 220, 80, 940, 640)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    g_container_id = ui.create_container(hwnd, 0, 0, 0, 900, 580)

    ui.create_text(hwnd, g_container_id, "💧 水印 Watermark 完整封装", 28, 24, 500, 38)
    intro_id = ui.create_text(
        hwnd,
        g_container_id,
        "本示例验证重复平铺、旋转、透明度、覆盖层绑定、鼠标穿透、层级与平铺数量读回。",
        28, 72, 780, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_infobox(
        hwnd,
        g_container_id,
        "🔎 验证提示",
        "水印覆盖在内容上方，但设置为鼠标穿透；1 秒后会向底层按钮位置发送点击，按钮应能收到事件。",
        48,
        150,
        740,
        86,
    )

    g_click_id = ui.create_button(hwnd, g_container_id, "✅", "底层可点击", 80, 300, 170, 46)
    g_toggle_id = ui.create_button(hwnd, g_container_id, "🧾", "读取覆盖层", 276, 300, 170, 46)
    ui.dll.EU_SetElementClickCallback(hwnd, g_click_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    g_watermark_id = ui.create_watermark(
        hwnd,
        g_container_id,
        content="💧 内部资料",
        gap_x=130,
        gap_y=82,
        x=0,
        y=0,
        w=900,
        h=580,
    )
    ui.set_watermark_options(hwnd, g_watermark_id, gap_x=130, gap_y=82, rotation=-24, alpha=64)
    ui.set_watermark_layer(hwnd, g_watermark_id, g_container_id, True, True, 20)

    initial = ui.get_watermark_full_options(hwnd, g_watermark_id)
    print(f"[初始] 状态：{initial}")
    if (
        not initial
        or initial["gap_x"] != 130
        or initial["gap_y"] != 82
        or initial["rotation"] != -24
        or initial["alpha"] != 64
        or initial["container_id"] != g_container_id
        or not initial["overlay"]
        or not initial["pass_through"]
        or initial["z_index"] != 20
    ):
        raise RuntimeError("水印完整选项初始读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("水印完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    dpi = user32.GetDpiForWindow(hwnd) if hasattr(user32, "GetDpiForWindow") else 96
    scale = dpi / 96.0
    click_points = []
    for probe_scale in (scale, 1.0, 1.25, 1.5, 2.0):
        click_points.append((int((80 + 85) * probe_scale), int((30 + 300 + 23) * probe_scale)))
        click_points.append((int((80 + 85) * probe_scale), int((300 + 23) * probe_scale)))
    start = time.time()
    running = True
    auto_click = False
    auto_read = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_click and elapsed > 1.0:
            for click_x, click_y in click_points:
                user32.PostMessageW(hwnd, 0x0201, 0x0001, make_lparam(click_x, click_y))
                user32.PostMessageW(hwnd, 0x0202, 0x0000, make_lparam(click_x, click_y))
            auto_click = True
        if not auto_read and elapsed > 2.0:
            on_click(g_toggle_id)
            state = ui.get_watermark_full_options(hwnd, g_watermark_id)
            if not state or state["tile_count_x"] <= 0 or state["tile_count_y"] <= 0:
                raise RuntimeError("水印平铺数量读回失败")
            auto_read = True
        if auto_click and elapsed > 2.5 and g_clicks < 1:
            raise RuntimeError("水印鼠标穿透验证失败，底层按钮没有收到点击")

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

    print("水印完整组件示例结束。")


if __name__ == "__main__":
    main()
