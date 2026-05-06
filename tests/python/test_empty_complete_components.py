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


def create_sample_image(name="new_emoji_empty_sample.bmp", width=96, height=64):
    path = os.path.join(tempfile.gettempdir(), name)
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            pixels.extend([90 + y * 2, 120 + x, 220 - x, 255])
    file_size = 54 + len(pixels)
    with open(path, "wb") as f:
        f.write(struct.pack("<2sIHHI", b"BM", file_size, 0, 0, 54))
        f.write(struct.pack("<IiiHHIIiiII", 40, width, height, 1, 32, 0, len(pixels), 2835, 2835, 0, 0))
        f.write(pixels)
    return path


class QuietHttpHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_http_server(directory, filename):
    handler = functools.partial(QuietHttpHandler, directory=directory)
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/{filename}"


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages(user32, msg):
    handled = False
    while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
        handled = True
        if msg.message in (0x0012, 0x0002):
            return False
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
    if not handled:
        time.sleep(0.01)
    return True


def main():
    global g_hwnd

    sample_path = create_sample_image()
    server, remote_url = start_http_server(tempfile.gettempdir(), os.path.basename(sample_path))
    hwnd = ui.create_window("📭 Empty 空状态完整组件验证", 220, 80, 1040, 720)
    if not hwnd:
        server.shutdown()
        raise RuntimeError("窗口创建失败")

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1000, 660)

    ui.create_text(hwnd, content, "📭 Empty 空状态完整组件验证", 28, 24, 520, 34)
    ui.create_text(hwnd, content, "覆盖描述文字、自定义图片、本地 HTTP 图片、图片尺寸和真实子按钮插槽。", 28, 66, 780, 28)

    basic = ui.create_empty(
        hwnd, content, "暂无数据 📭", "描述文字：当前筛选下没有结果。",
        28, 112, 290, 190, icon="📭", action="刷新"
    )
    ui.set_empty_description(hwnd, basic, "当前筛选条件下没有结果，换个关键词试试 🔎")
    ui.set_empty_options(hwnd, basic, "🔎", "清空筛选")
    ui.set_empty_action_clicked(hwnd, basic, True)
    if ui.get_empty_action_clicked(hwnd, basic) != 1:
        raise RuntimeError("空状态内置按钮点击状态读回失败")
    ui.set_empty_action_clicked(hwnd, basic, False)

    local_empty = ui.create_empty(
        hwnd, content, "本地图片 🖼️", "image-size=180，本地 BMP 图片应加载成功。",
        348, 112, 300, 260, image=sample_path, image_size=180
    )
    if ui.get_empty_image_size(hwnd, local_empty) != 180:
        raise RuntimeError("空状态图片尺寸读回失败")

    remote_empty = ui.create_empty(
        hwnd, content, "HTTP 图片 🌐", "通过本地 HTTP 服务验证远程图片加载。",
        678, 112, 300, 230, image=remote_url, image_size=128, action="重新加载"
    )

    slot_empty = ui.create_empty(
        hwnd, content, "默认插槽按钮 ➕", "Empty 内挂载真实 Button 子元素。",
        28, 398, 340, 220, icon="🧩"
    )
    slot_button = ui.create_button(hwnd, slot_empty, "➕", "创建内容", 96, 166, 148, 40)
    if not slot_button:
        raise RuntimeError("空状态子按钮创建失败")

    ui.dll.EU_ShowWindow(hwnd, 1)

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    local_loaded = False
    remote_loaded = False
    try:
        while time.time() - start < 12.0:
            if not pump_messages(user32, msg):
                break
            elapsed = time.time() - start
            local_status = ui.get_empty_image_status(hwnd, local_empty)
            remote_status = ui.get_empty_image_status(hwnd, remote_empty)
            local_loaded = local_loaded or local_status == 1
            remote_loaded = remote_loaded or remote_status == 1
            if elapsed > 3.0 and not local_loaded:
                raise RuntimeError(f"本地 Empty 图片未加载成功，状态={local_status}")
            if local_loaded and remote_loaded:
                break
        if not remote_loaded:
            raise RuntimeError(f"HTTP Empty 图片未加载成功，状态={ui.get_empty_image_status(hwnd, remote_empty)}")
    finally:
        server.shutdown()
        server.server_close()
        if hwnd:
            ui.dll.EU_DestroyWindow(hwnd)

    print("Empty 空状态完整组件测试通过。")


if __name__ == "__main__":
    main()
