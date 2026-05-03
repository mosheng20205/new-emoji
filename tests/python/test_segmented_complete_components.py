import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_segmented_id = 0
g_select_id = 0
g_disable_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 分段控制完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_select_id:
        ui.set_segmented_active(g_hwnd, g_segmented_id, 3)
        print(f"[选择] 状态={ui.get_segmented_state(g_hwnd, g_segmented_id)}")
    elif element_id == g_disable_id:
        ui.set_segmented_disabled(g_hwnd, g_segmented_id, [1, 3])
        ui.set_segmented_active(g_hwnd, g_segmented_id, 1)
        print(f"[禁用拦截] 状态={ui.get_segmented_state(g_hwnd, g_segmented_id)}")


def main():
    global g_hwnd, g_segmented_id, g_select_id, g_disable_id

    hwnd = ui.create_window("🎛️ 分段控制完整组件", 220, 80, 820, 560)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 780, 500)

    ui.create_text(hwnd, content_id, "🎛️ 分段控制完整验证", 28, 24, 380, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证滑块式选中视觉、禁用项绘制与交互拦截、键盘左右/Home/End 选择、状态读回和中文 emoji 分段项。",
        28, 70, 720, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_segmented_id = ui.create_segmented(
        hwnd, content_id,
        ["☀️ 今日", "📅 本周", "🗓️ 本月", "📊 全年", "⭐ 收藏"],
        2, 48, 156, 560, 48,
    )
    ui.set_segmented_disabled(hwnd, g_segmented_id, [4])

    ui.create_infobox(
        hwnd, content_id,
        "验证提示",
        "初始禁用“收藏”。1 秒后选中“全年”，2 秒后禁用“本周/全年”并尝试选中禁用项，应自动跳到可用项。",
        48, 238, 560, 90,
    )

    g_select_id = ui.create_button(hwnd, content_id, "🎯", "选择全年", 48, 384, 150, 42)
    g_disable_id = ui.create_button(hwnd, content_id, "🚫", "测试禁用", 220, 384, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_select_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_disable_id, on_click)

    initial = ui.get_segmented_state(hwnd, g_segmented_id)
    print(f"[初始] 状态={initial}")
    if not initial or initial["active"] != 2 or initial["disabled"] != 1:
        raise RuntimeError("分段控制状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("分段控制完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_select = False
    auto_disable = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_select and elapsed > 1.0:
            on_click(g_select_id)
            auto_select = True
        if not auto_disable and elapsed > 2.0:
            on_click(g_disable_id)
            auto_disable = True
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

    print("分段控制完整组件示例结束。")


if __name__ == "__main__":
    main()
