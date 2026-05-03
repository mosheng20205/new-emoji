import ctypes
from ctypes import wintypes
import os
import struct
import tempfile
import time

import test_new_emoji as ui


g_hwnd = None
g_image_id = 0
g_zoom_id = 0
g_close_id = 0


def create_sample_image():
    path = os.path.join(tempfile.gettempdir(), "new_emoji_image_sample.bmp")
    width, height = 64, 40
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            pixels.extend([210, 80 + x * 2, 80 + y * 4, 255])
    file_size = 54 + len(pixels)
    with open(path, "wb") as f:
        f.write(struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54))
        f.write(struct.pack("<IiiHHIIiiII", 40, width, height, 1, 32, 0, len(pixels), 2835, 2835, 0, 0))
        f.write(pixels)
    return path


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 图片完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_zoom_id:
        ui.set_image_preview(g_hwnd, g_image_id, True)
        ui.set_image_preview_transform(g_hwnd, g_image_id, 150, 24, -12)
        print(f"[预览缩放] 状态：{ui.get_image_full_options(g_hwnd, g_image_id)}")
    elif element_id == g_close_id:
        ui.set_image_preview(g_hwnd, g_image_id, False)
        print(f"[关闭预览] 状态：{ui.get_image_full_options(g_hwnd, g_image_id)}")


def main():
    global g_hwnd, g_image_id, g_zoom_id, g_close_id

    sample_path = create_sample_image()
    hwnd = ui.create_window("🖼️ 图片完整组件验证", 220, 80, 980, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 600)

    ui.create_text(hwnd, content_id, "🖼️ Image 图片完整封装", 28, 24, 470, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证本地图片加载、contain/cover/fill、预览打开、缩放偏移、缓存开关和完整状态读回。",
        28, 72, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_image_id = ui.create_image(
        hwnd,
        content_id,
        src=sample_path,
        alt="🖼️ 本地渐变示例图",
        fit=0,
        x=56,
        y=150,
        w=300,
        h=240,
    )
    ui.set_image_cache_enabled(hwnd, g_image_id, True)
    ui.set_image_preview_enabled(hwnd, g_image_id, True)

    g_zoom_id = ui.create_button(hwnd, content_id, "🔍", "打开缩放预览", 410, 190, 170, 42)
    g_close_id = ui.create_button(hwnd, content_id, "✅", "关闭预览", 410, 250, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_zoom_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_close_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("图片完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    checked_load = False
    auto_zoom = False
    auto_close = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not checked_load and elapsed > 1.0:
            state = ui.get_image_full_options(hwnd, g_image_id)
            print(f"[加载状态] 状态：{state}")
            if not state or state["status"] != 1 or state["bitmap_width"] <= 0 or state["bitmap_height"] <= 0:
                raise RuntimeError("图片加载状态读回失败")
            checked_load = True
        if checked_load and not auto_zoom and elapsed > 2.0:
            on_click(g_zoom_id)
            state = ui.get_image_full_options(hwnd, g_image_id)
            if not state or not state["preview_open"] or state["scale_percent"] != 150:
                raise RuntimeError("图片预览缩放状态读回失败")
            auto_zoom = True
        if auto_zoom and not auto_close and elapsed > 3.0:
            on_click(g_close_id)
            state = ui.get_image_full_options(hwnd, g_image_id)
            if not state or state["preview_open"]:
                raise RuntimeError("图片预览关闭状态读回失败")
            auto_close = True

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

    print("图片完整组件示例结束。")


if __name__ == "__main__":
    main()
