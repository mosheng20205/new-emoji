import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 日历完成验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def main():
    hwnd = ui.create_window("📅 日历组件完成验证", 220, 80, 760, 520)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 720, 460)
    ui.create_text(hwnd, content, "📅 日历组件完成验证", 30, 22, 320, 36)
    ui.create_text(hwnd, content, "支持范围限制、今天高亮、选择区间和键盘方向键导航。", 30, 58, 520, 28)

    cal = ui.create_calendar(hwnd, content, 2026, 5, 12, 36, 100, 360, 310)
    ui.set_calendar_range(hwnd, cal, 20260505, 20260528)
    ui.set_calendar_options(hwnd, cal, 20260503, True)
    ui.set_calendar_selection_range(hwnd, cal, 20260510, 20260518, True)

    ui.create_text(hwnd, content, "⌨️ 点击日历后可用方向键、Home/End、PageUp/PageDown 操作。", 430, 120, 260, 80)
    ui.create_text(hwnd, content, "✅ 区间选择读回：", 430, 230, 180, 28)
    print("[读回] 日历日期=", ui.get_calendar_value(hwnd, cal))
    print("[读回] 日期范围=", ui.get_calendar_range(hwnd, cal))
    print("[读回] 日历选项=", ui.get_calendar_options(hwnd, cal))
    print("[读回] 选择区间=", ui.get_calendar_selection_range(hwnd, cal))

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📅 日历完成验证示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("📅 日历完成验证示例结束。")


if __name__ == "__main__":
    main()
