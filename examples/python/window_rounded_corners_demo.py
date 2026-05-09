import ctypes
from ctypes import wintypes

import new_emoji_ui as ui


STATE = {
    "hwnd": 0,
    "status": 0,
}


def run_message_loop():
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


def set_status(text):
    hwnd = STATE["hwnd"]
    status = STATE["status"]
    if hwnd and status:
        ui.set_element_text(hwnd, status, text)


def apply_radius(radius):
    hwnd = STATE["hwnd"]
    if radius > 0:
        ui.set_window_rounded_corners(hwnd, True, radius)
        set_status(
            f"✅ 当前窗口圆角：请求 {radius}px 逻辑半径\n"
            "Windows 11 会优先使用平滑 DWM 圆角；Win10 会使用 per-pixel alpha 分层窗口。"
        )
    else:
        ui.set_window_rounded_corners(hwnd, False, 0)
        set_status("⬜ 当前窗口圆角：已关闭\nWindows 窗口外形已恢复为矩形。")


@ui.ClickCallback
def use_small_radius(_element_id):
    apply_radius(12)


@ui.ClickCallback
def use_medium_radius(_element_id):
    apply_radius(28)


@ui.ClickCallback
def use_large_radius(_element_id):
    apply_radius(44)


@ui.ClickCallback
def disable_radius(_element_id):
    apply_radius(0)


def main():
    hwnd = ui.create_window("🪟 设置窗口圆角示例", 260, 140, 860, 540)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    STATE["hwnd"] = hwnd
    root = ui.create_container(hwnd, 0, 0, 0, 820, 480)

    ui.create_text(hwnd, root, "🪟 设置真实窗口圆角", 32, 28, 420, 42)
    ui.create_text(
        hwnd,
        root,
        "这个示例演示 EU_SetWindowRoundedCorners：Windows 11 会优先使用平滑系统圆角，"
        "Win10 会使用透明分层窗口消除圆角锯齿。",
        34,
        82,
        740,
        76,
    )

    small_btn = ui.create_button(hwnd, root, "🔹", "小圆角", 34, 178, 150, 44, variant=1)
    medium_btn = ui.create_button(hwnd, root, "🟢", "中圆角", 204, 178, 150, 44, variant=2)
    large_btn = ui.create_button(hwnd, root, "✨", "大圆角", 374, 178, 150, 44, variant=3)
    off_btn = ui.create_button(hwnd, root, "⬜", "关闭圆角", 544, 178, 150, 44, variant=5)

    ui.create_text(hwnd, root, "📐 试着拖动窗口边缘改变大小，圆角区域会跟随窗口尺寸刷新。", 34, 260, 720, 34)
    ui.create_text(hwnd, root, "🧭 把窗口移动到不同缩放比例的屏幕上，也会按当前 DPI 重新应用。", 34, 304, 720, 34)
    status = ui.create_text(hwnd, root, "⏳ 正在应用默认圆角...", 34, 366, 730, 74)
    STATE["status"] = status

    ui.dll.EU_SetElementClickCallback(hwnd, small_btn, use_small_radius)
    ui.dll.EU_SetElementClickCallback(hwnd, medium_btn, use_medium_radius)
    ui.dll.EU_SetElementClickCallback(hwnd, large_btn, use_large_radius)
    ui.dll.EU_SetElementClickCallback(hwnd, off_btn, disable_radius)

    apply_radius(28)
    ui.dll.EU_ShowWindow(hwnd, 1)
    run_message_loop()


if __name__ == "__main__":
    main()
