import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 加载完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages(user32, msg, duration):
    start = time.time()
    running = True
    while running and time.time() - start < duration:
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
    return running


def main():
    global g_hwnd

    hwnd = ui.create_window("⏳ 加载完整组件验证", 220, 80, 960, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 620)

    ui.create_text(hwnd, content_id, "⏳ Loading 加载完整封装", 30, 24, 640, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证目标绑定遮罩、真实旋转动画定时器、进度状态、文本读回、完整状态读回和首次窗口尺寸余量。",
        30, 70, 840, 52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    target_id = ui.create_panel(hwnd, content_id, 70, 142, 760, 250)
    ui.set_panel_style(hwnd, target_id, bg=0xFFF5F7FB, border=0xFFBFC7D5, border_width=1.0, radius=10)
    ui.create_text(hwnd, target_id, "📦 目标内容区域", 28, 28, 260, 34)
    detail_id = ui.create_text(
        hwnd,
        target_id,
        "加载遮罩会绑定这个区域，外扩 8px，并用内部定时器持续推进旋转动画。",
        28,
        78,
        660,
        60,
    )
    ui.set_text_options(hwnd, detail_id, align=0, valign=0, wrap=True, ellipsis=False)

    loading_id = ui.create_loading(
        hwnd,
        content_id,
        text="🔄 正在同步数据",
        active=True,
        x=62,
        y=134,
        w=776,
        h=266,
    )
    ui.set_loading_target(hwnd, loading_id, target_id, 8)
    ui.set_loading_options(hwnd, loading_id, active=True, fullscreen=False, progress=42)

    ui.create_text(hwnd, content_id, "🎯 绑定目标后，Loading 会覆盖目标卡片；动画帧数会持续增长。", 86, 430, 720, 34)
    ui.create_button(hwnd, content_id, "✅", "完成加载", 86, 486, 150, 42)
    ui.create_button(hwnd, content_id, "🌕", "切换全屏遮罩", 260, 486, 170, 42)

    if "同步数据" not in ui.get_loading_text(hwnd, loading_id):
        raise RuntimeError("加载文本读回失败")

    state = ui.get_loading_full_state(hwnd, loading_id)
    print("[初始完整状态]", state)
    if not state or state["active"] != 1 or state["progress"] != 42 or state["target_element_id"] != target_id:
        raise RuntimeError("加载初始完整状态失败")
    if state["timer_running"] != 1:
        raise RuntimeError("加载动画定时器未启动")

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.35)
    animated = ui.get_loading_full_state(hwnd, loading_id)
    print("[动画推进]", animated)
    if animated["tick_count"] <= state["tick_count"] or animated["animation_angle"] == state["animation_angle"]:
        raise RuntimeError("加载旋转动画未推进")

    ui.set_loading_options(hwnd, loading_id, active=False, fullscreen=True, progress=100)
    stopped = ui.get_loading_full_state(hwnd, loading_id)
    print("[停止加载]", stopped)
    if stopped["active"] != 0 or stopped["fullscreen"] != 1 or stopped["progress"] != 100 or stopped["timer_running"] != 0:
        raise RuntimeError("加载停止/全屏/进度状态失败")

    ui.set_loading_options(hwnd, loading_id, active=True, fullscreen=True, progress=88)
    restarted = ui.get_loading_full_state(hwnd, loading_id)
    if restarted["active"] != 1 or restarted["fullscreen"] != 1 or restarted["timer_running"] != 1:
        raise RuntimeError("加载重新激活失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、目标遮罩、全屏样式和旋转动画。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
