import ctypes
from ctypes import wintypes
import os
import struct
import tempfile
import time

import test_new_emoji as ui


WINDOW_W = 760
WINDOW_H = 520
CONTENT_W = 720
CONTENT_H = 460


def write_demo_bmp(path, width=72, height=48):
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            r = 90 + x * 120 // max(1, width - 1)
            g = 150 + y * 80 // max(1, height - 1)
            b = 230 - x * 90 // max(1, width - 1)
            pixels.extend([b & 0xFF, g & 0xFF, r & 0xFF, 255])
    with open(path, "wb") as f:
        f.write(struct.pack("<2sIHHI", b"BM", 54 + len(pixels), 0, 0, 54))
        f.write(struct.pack("<IiiHHIIiiII", 40, width, height, 1, 32, 0, len(pixels), 2835, 2835, 0, 0))
        f.write(pixels)


def pump_messages(seconds):
    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    while time.time() - start < seconds:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                return
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    folder = tempfile.mkdtemp(prefix="new_emoji_avatar_test_")
    local_image = os.path.join(folder, "头像本地图.bmp")
    fallback_image = os.path.join(folder, "头像备用图.bmp")
    missing_image = os.path.join(folder, "不存在头像.bmp")
    write_demo_bmp(local_image, 96, 56)
    write_demo_bmp(fallback_image, 42, 42)

    hwnd = ui.create_window("😀 Avatar 头像完整样式测试", 220, 120, WINDOW_W, WINDOW_H)
    require(hwnd, "窗口创建失败")
    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "😀 Avatar：形状、图片、图标、回退与五种适配", 24, 20, 620, 30)
    round_id = ui.create_avatar(hwnd, content_id, "圆", 0, 30, 76, 64, 64)
    square_id = ui.create_avatar(hwnd, content_id, "方", 1, 118, 76, 64, 64)
    local_id = ui.create_avatar(hwnd, content_id, "", 0, 206, 76, 72, 72, source=local_image, fit="cover")
    fallback_id = ui.create_avatar(
        hwnd, content_id, "", 0, 306, 76, 72, 72,
        source=missing_image, fallback_source=fallback_image, fit="scale-down", icon="🛟"
    )
    failed_id = ui.create_avatar(
        hwnd, content_id, "", 1, 406, 76, 72, 72,
        source=missing_image, error_text="错"
    )
    icon_id = ui.create_avatar(hwnd, content_id, "", 0, 506, 76, 72, 72, icon="👤")

    ui.create_text(hwnd, content_id, "🖼️ 五种图片适配", 24, 184, 260, 28)
    fit_names = ["contain", "cover", "fill", "none", "scale-down"]
    fit_ids = []
    for index, fit in enumerate(fit_names):
        fit_ids.append(ui.create_avatar(hwnd, content_id, "", 1, 30 + index * 104, 226, 76, 76, source=local_image, fit=fit))
        ui.create_text(hwnd, content_id, fit, 30 + index * 104, 312, 92, 24)

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(1.2)

    require(ui.get_avatar_options(hwnd, round_id) == (0, 0), "圆形头像选项读回错误")
    require(ui.get_avatar_options(hwnd, square_id) == (1, 0), "方形头像选项读回错误")
    for expected, element_id in enumerate(fit_ids):
        require(ui.get_avatar_options(hwnd, element_id) == (1, expected), f"适配方式 {expected} 读回错误")

    require(ui.get_avatar_image_status(hwnd, local_id) == 1, "本地图片头像应加载成功")
    require(ui.get_avatar_image_status(hwnd, fallback_id) == 1, "备用图片头像应加载成功")
    require(ui.get_avatar_image_status(hwnd, failed_id) == 2, "缺失图片头像应返回失败状态")
    require(ui.get_avatar_image_status(hwnd, icon_id) == 0, "纯图标头像应保持空图片状态")

    ui.set_avatar_shape(hwnd, icon_id, 1)
    ui.set_avatar_fit(hwnd, icon_id, "none")
    ui.set_avatar_icon(hwnd, icon_id, "🧑‍💼")
    ui.set_avatar_error_text(hwnd, failed_id, "离线")
    require(ui.get_avatar_options(hwnd, icon_id) == (1, 3), "图标头像 Set/Get 读回错误")

    print("Avatar 完整样式测试通过：圆形/方形、本地图片、失败回退、图标、错误文本和五种 fit 均已验证。")
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
