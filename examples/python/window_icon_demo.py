import ctypes
import struct
import tempfile
from pathlib import Path
from ctypes import wintypes

import new_emoji_ui as ui


STATE = {
    "hwnd": 0,
    "status": 0,
}


def _dib_image(width, height, bgra, accent_bgra):
    pixels = bytearray()
    for y in reversed(range(height)):
        for x in range(width):
            border = x < 3 or y < 3 or x >= width - 3 or y >= height - 3
            diagonal = abs(x - y) <= 2
            pixels.extend(accent_bgra if border or diagonal else bgra)

    and_mask_stride = ((width + 31) // 32) * 4
    and_mask = bytes(and_mask_stride * height)
    header = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        height * 2,
        1,
        32,
        0,
        len(pixels),
        0,
        0,
        0,
        0,
    )
    return header + bytes(pixels) + and_mask


def make_ico_bytes(bgra, accent_bgra):
    images = [
        (16, 16, _dib_image(16, 16, bgra, accent_bgra)),
        (32, 32, _dib_image(32, 32, bgra, accent_bgra)),
    ]

    header = struct.pack("<HHH", 0, 1, len(images))
    entries = bytearray()
    payload = bytearray()
    offset = len(header) + len(images) * 16

    for width, height, image in images:
        entries.extend(
            struct.pack(
                "<BBBBHHII",
                width,
                height,
                0,
                0,
                1,
                32,
                len(image),
                offset,
            )
        )
        payload.extend(image)
        offset += len(image)

    return header + bytes(entries) + bytes(payload)


PATH_ICON_BYTES = make_ico_bytes(
    bgra=(0xF5, 0xA3, 0x22, 0xFF),
    accent_bgra=(0xFF, 0xFF, 0xFF, 0xFF),
)
MEMORY_ICON_BYTES = make_ico_bytes(
    bgra=(0x8A, 0x38, 0xD6, 0xFF),
    accent_bgra=(0x38, 0xF6, 0xDA, 0xFF),
)


def write_path_icon():
    path = Path(tempfile.gettempdir()) / "new_emoji_window_icon_path_demo.ico"
    path.write_bytes(PATH_ICON_BYTES)
    return path


def set_status(text):
    hwnd = STATE["hwnd"]
    status = STATE["status"]
    if hwnd and status:
        ui.set_element_text(hwnd, status, text)


@ui.ClickCallback
def use_path_icon(_element_id):
    path = write_path_icon()
    ok = ui.set_window_icon(STATE["hwnd"], path)
    result = "成功" if ok else "失败"
    set_status(f"📁 当前图标：通过文件路径设置，结果：{result}\n{path}")


@ui.ClickCallback
def use_bytes_icon(_element_id):
    ok = ui.set_window_icon_from_bytes(STATE["hwnd"], MEMORY_ICON_BYTES)
    result = "成功" if ok else "失败"
    set_status(f"🧩 当前图标：通过 .ico 文件字节集设置，结果：{result}")


def run_message_loop():
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


def main():
    hwnd = ui.create_window("🪟 设置窗口图标示例", 260, 140, 760, 460)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    STATE["hwnd"] = hwnd
    root = ui.create_container(hwnd, 0, 0, 0, 720, 400)

    ui.create_text(hwnd, root, "🪟 设置窗口图标", 32, 28, 360, 42)
    ui.create_text(
        hwnd,
        root,
        "这个示例演示两个导出方法：从 .ico 文件路径设置窗口图标，以及直接传入 .ico 文件字节集设置窗口图标。",
        34,
        82,
        660,
        64,
    )

    path_button = ui.create_button(hwnd, root, "📁", "使用文件路径图标", 34, 172, 210, 44, variant=1)
    bytes_button = ui.create_button(hwnd, root, "🧩", "使用字节集图标", 260, 172, 210, 44, variant=2)

    ui.create_text(hwnd, root, "✅ 首次显示时会先使用文件路径设置任务栏/标题栏图标。", 34, 242, 620, 34)
    status = ui.create_text(hwnd, root, "⏳ 正在设置窗口图标...", 34, 292, 650, 70)
    STATE["status"] = status

    ui.dll.EU_SetElementClickCallback(hwnd, path_button, use_path_icon)
    ui.dll.EU_SetElementClickCallback(hwnd, bytes_button, use_bytes_icon)

    use_path_icon(path_button)
    ui.dll.EU_ShowWindow(hwnd, 1)
    run_message_loop()


if __name__ == "__main__":
    main()
