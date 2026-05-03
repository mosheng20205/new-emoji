import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 分割线完成验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def main():
    hwnd = ui.create_window("➗ 分割线组件完成验证", 240, 90, 760, 420)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 720, 360)
    ui.create_text(hwnd, content, "➗ 分割线组件完成验证", 30, 24, 320, 34)

    d1 = ui.create_divider(hwnd, content, "✨ 居中标题", 0, 1, 40, 88, 600, 36)
    ui.set_divider_options(hwnd, d1, 0, 1, 0xFF409EFF, 2.0, False, "✨ 居中标题")
    ui.set_divider_spacing(hwnd, d1, margin=28, gap=14)

    d2 = ui.create_divider(hwnd, content, "📌 左侧标题", 0, 0, 40, 150, 600, 36)
    ui.set_divider_options(hwnd, d2, 0, 0, 0xFFE6A23C, 1.5, True, "📌 左侧标题")
    ui.set_divider_spacing(hwnd, d2, margin=8, gap=18)

    d3 = ui.create_divider(hwnd, content, "", 1, 1, 660, 82, 32, 190)
    ui.set_divider_options(hwnd, d3, 1, 1, 0xFF67C23A, 2.0, True, "")
    ui.set_divider_spacing(hwnd, d3, margin=16, gap=8)

    ui.create_text(hwnd, content, "✅ 间距、虚线、颜色、方向和文本位置均可读写。", 40, 236, 520, 32)

    print("[读回] 分割线选项=", ui.get_divider_options(hwnd, d1))
    print("[读回] 分割线间距=", ui.get_divider_spacing(hwnd, d1))

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("➗ 分割线完成验证示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("➗ 分割线完成验证示例结束。")


if __name__ == "__main__":
    main()
