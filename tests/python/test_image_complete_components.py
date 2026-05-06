import ctypes
from ctypes import wintypes
import functools
import http.server
import os
import socketserver
import struct
import tempfile
import threading
import time

import test_new_emoji as ui


g_hwnd = None
g_image_id = 0
g_zoom_id = 0
g_close_id = 0
g_fit_ids = []
g_remote_id = 0
g_placeholder_id = 0
g_error_id = 0
g_lazy_id = 0


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


def create_sample_image_alt():
    path = os.path.join(tempfile.gettempdir(), "new_emoji_image_sample_alt.bmp")
    width, height = 44, 72
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            pixels.extend([80 + y * 2, 120, 220 - x * 2, 255])
    file_size = 54 + len(pixels)
    with open(path, "wb") as f:
        f.write(struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54))
        f.write(struct.pack("<IiiHHIIiiII", 40, width, height, 1, 32, 0, len(pixels), 2835, 2835, 0, 0))
        f.write(pixels)
    return path


class QuietHttpHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_http_server(directory):
    handler = functools.partial(QuietHttpHandler, directory=directory)
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/new_emoji_image_sample.bmp"


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 图片完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_zoom_id:
        ui.set_image_preview(g_hwnd, g_image_id, True)
        ui.set_image_preview_transform(g_hwnd, g_image_id, 150, 24, -12)
        ui.set_image_preview_index(g_hwnd, g_image_id, 2)
        print(f"[预览缩放] 状态：{ui.get_image_full_options(g_hwnd, g_image_id)}")
    elif element_id == g_close_id:
        ui.set_image_preview(g_hwnd, g_image_id, False)
        print(f"[关闭预览] 状态：{ui.get_image_full_options(g_hwnd, g_image_id)}")


def main():
    global g_hwnd, g_image_id, g_zoom_id, g_close_id
    global g_fit_ids, g_remote_id, g_placeholder_id, g_error_id, g_lazy_id

    sample_path = create_sample_image()
    sample_alt_path = create_sample_image_alt()
    server, remote_url = start_http_server(tempfile.gettempdir())
    hwnd = ui.create_window("🖼️ 图片全样式组件验证", 220, 60, 1180, 840)
    if not hwnd:
        print("错误：窗口创建失败")
        server.shutdown()
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1140, 780)

    ui.create_text(hwnd, content_id, "🖼️ Image 图片全样式封装", 28, 24, 520, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证五种适配、本地/远程图片、自定义占位、失败状态、懒加载和预览列表。",
        28, 72, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    fits = [("contain", "包含"), ("cover", "覆盖"), ("fill", "拉伸"), ("none", "原尺寸"), ("scale-down", "缩小")]
    g_fit_ids = []
    for index, (fit, label) in enumerate(fits):
        x = 36 + index * 150
        ui.create_text(hwnd, content_id, f"🧩 {label}", x, 128, 122, 24)
        image_id = ui.create_image(
            hwnd, content_id, src=sample_path, alt=f"🖼️ {label}", fit=fit,
            x=x, y=158, w=132, h=128,
        )
        g_fit_ids.append(image_id)

    g_placeholder_id = ui.create_image(hwnd, content_id, src="", alt="🕒 自定义占位",
                                       fit="contain", x=806, y=158, w=140, h=128)
    ui.set_image_placeholder(hwnd, g_placeholder_id, "⏳", "正在准备图片", 0xFF409EFF, 0xFFEAF4FF)

    g_error_id = ui.create_image(hwnd, content_id, src=os.path.join(tempfile.gettempdir(), "missing-image-file.bmp"),
                                 alt="⚠️ 自定义失败", fit="contain", x=970, y=158, w=140, h=128)
    ui.set_image_error_content(hwnd, g_error_id, "🧯", "图片读取失败", 0xFFF56C6C, 0xFFFFF0F0)

    g_remote_id = ui.create_image(hwnd, content_id, src=remote_url, alt="🌐 本地 HTTP 远程图",
                                  fit="cover", x=56, y=340, w=220, h=170)
    ui.set_image_placeholder(hwnd, g_remote_id, "🌐", "远程图片加载中", 0xFF409EFF, 0)

    g_image_id = ui.create_image(
        hwnd,
        content_id,
        src=sample_alt_path,
        alt="🔍 预览列表示例",
        fit="contain",
        x=326,
        y=340,
        w=220,
        h=170,
    )
    ui.set_image_preview_list(hwnd, g_image_id, [sample_path, sample_alt_path, remote_url], selected_index=1)
    ui.set_image_cache_enabled(hwnd, g_image_id, True)
    ui.set_image_preview_enabled(hwnd, g_image_id, True)

    g_lazy_id = ui.create_image(hwnd, content_id, src=sample_path, alt="🛗 懒加载等待可见",
                                fit="scale-down", x=596, y=900, w=220, h=150)
    ui.set_image_lazy(hwnd, g_lazy_id, True)

    g_zoom_id = ui.create_button(hwnd, content_id, "🔍", "打开缩放预览", 596, 370, 170, 42)
    g_close_id = ui.create_button(hwnd, content_id, "✅", "关闭预览", 596, 430, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_zoom_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_close_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("图片完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    checked_load = False
    moved_lazy = False
    checked_lazy = False
    auto_zoom = False
    auto_close = False
    try:
        while running and time.time() - start < 60:
            elapsed = time.time() - start
            if not checked_load and elapsed > 1.4:
                fit_values = [ui.get_image_advanced_options(hwnd, item)["fit"] for item in g_fit_ids]
                remote_state = ui.get_image_full_options(hwnd, g_remote_id)
                error_state = ui.get_image_advanced_options(hwnd, g_error_id)
                placeholder_state = ui.get_image_advanced_options(hwnd, g_placeholder_id)
                lazy_state = ui.get_image_advanced_options(hwnd, g_lazy_id)
                preview_state = ui.get_image_advanced_options(hwnd, g_image_id)
                print(f"[全样式状态] fit={fit_values}, remote={remote_state}, lazy={lazy_state}, preview={preview_state}")
                if (not remote_state or remote_state["status"] != 1) and elapsed < 18.0:
                    pass
                elif not remote_state or remote_state["status"] != 1:
                    raise RuntimeError("本地 HTTP 远程图片加载失败")
                else:
                    if fit_values != [0, 1, 2, 3, 4]:
                        raise RuntimeError("五种 fit 状态读回失败")
                    if not error_state or error_state["status"] != 2:
                        raise RuntimeError("失败图片状态读回失败")
                    if not placeholder_state or placeholder_state["status"] != 0:
                        raise RuntimeError("空 src 占位状态读回失败")
                    if not lazy_state or lazy_state["status"] != 4 or not lazy_state["lazy"]:
                        raise RuntimeError("懒加载等待状态读回失败")
                    if not preview_state or preview_state["preview_count"] != 3 or preview_state["preview_index"] != 1:
                        raise RuntimeError("预览列表状态读回失败")
                    checked_load = True
            if checked_load and not moved_lazy and elapsed > 2.0:
                ui.dll.EU_SetElementBounds(hwnd, g_lazy_id, 820, 340, 220, 150)
                moved_lazy = True
            if moved_lazy and not checked_lazy and elapsed > 2.8:
                lazy_state = ui.get_image_full_options(hwnd, g_lazy_id)
                print(f"[懒加载进入可见区] 状态：{lazy_state}")
                if not lazy_state or lazy_state["status"] != 1:
                    raise RuntimeError("懒加载进入可见区后未加载成功")
                checked_lazy = True
            if checked_lazy and not auto_zoom and elapsed > 3.4:
                on_click(g_zoom_id)
                state = ui.get_image_advanced_options(hwnd, g_image_id)
                if not state or not state["preview_open"] or state["scale_percent"] != 150 or state["preview_index"] != 2:
                    raise RuntimeError("图片预览列表/缩放状态读回失败")
                auto_zoom = True
            if auto_zoom and not auto_close and elapsed > 4.4:
                on_click(g_close_id)
                state = ui.get_image_full_options(hwnd, g_image_id)
                if not state or state["preview_open"]:
                    raise RuntimeError("图片预览关闭状态读回失败")
                auto_close = True
                running = False

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
    finally:
        server.shutdown()
        server.server_close()

    print("图片完整组件示例结束。")


if __name__ == "__main__":
    main()
