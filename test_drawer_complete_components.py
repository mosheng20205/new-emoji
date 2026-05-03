import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_drawer_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 抽屉完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_drawer_close(element_id, close_count, placement, action):
    g_events.append((close_count, placement, action))
    print(f"[抽屉关闭回调] 元素={element_id} 次数={close_count} 位置={placement} 动作={action}")


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
    global g_hwnd, g_drawer_id

    hwnd = ui.create_window("🧭 抽屉完整组件验证", 220, 80, 980, 700)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 640)
    ui.create_text(hwnd, content_id, "🧭 Drawer 抽屉完整封装", 32, 28, 620, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证方向、遮罩、动画计时器、程序关闭、键盘关闭、标题/正文读回、完整状态读回和关闭回调。",
        32,
        78,
        840,
        56,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)
    ui.create_button(hwnd, content_id, "📌", "背景操作：抽屉覆盖其上", 52, 168, 250, 44)
    ui.create_text(hwnd, content_id, "✨ 首屏保留足够余量，右侧抽屉宽度 320px。", 52, 238, 620, 34)

    g_drawer_id = ui.create_drawer(
        hwnd,
        title="🧭 任务详情",
        body="这里显示中文说明、emoji 状态和抽屉内容。打开动画、关闭动作和状态读回都应可验证。",
        placement=1,
        modal=True,
        closable=True,
        size=320,
    )
    ui.set_drawer_animation(hwnd, g_drawer_id, 360)
    ui.set_drawer_options(hwnd, g_drawer_id, placement=1, open=True,
                          modal=True, closable=True, close_on_mask=True, size=320)
    ui.set_drawer_close_callback(hwnd, g_drawer_id, on_drawer_close)

    if "任务详情" not in ui.get_drawer_text(hwnd, g_drawer_id, 0):
        raise RuntimeError("抽屉标题读回失败")
    if "中文说明" not in ui.get_drawer_text(hwnd, g_drawer_id, 1):
        raise RuntimeError("抽屉正文读回失败")

    initial = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[初始完整状态]", initial)
    if not initial or not initial["open"] or initial["placement"] != 1 or initial["size"] != 320:
        raise RuntimeError("抽屉初始完整状态失败")
    if initial["animation_ms"] != 360 or not initial["timer_running"]:
        raise RuntimeError("抽屉动画计时器未启动")

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.45)
    animated = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[动画推进状态]", animated)
    if animated["tick_count"] <= initial["tick_count"] or animated["animation_progress"] < 75:
        raise RuntimeError("抽屉动画推进失败")

    ui.trigger_drawer_close(hwnd, g_drawer_id)
    closed = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[程序关闭状态]", closed)
    if closed["open"] or closed["close_count"] != 1 or closed["last_action"] != 4:
        raise RuntimeError("抽屉程序关闭失败")
    if not g_events or g_events[-1] != (1, 1, 4):
        raise RuntimeError("抽屉关闭回调失败")

    ui.set_drawer_options(hwnd, g_drawer_id, placement=2, open=True,
                          modal=True, closable=True, close_on_mask=True, size=220)
    top_state = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[顶部抽屉状态]", top_state)
    if top_state["placement"] != 2 or top_state["size"] != 220 or not top_state["open"]:
        raise RuntimeError("抽屉顶部方向或高度读回失败")

    ui.dll.EU_SetElementFocus(hwnd, g_drawer_id)
    user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)  # VK_ESCAPE
    pump_messages(user32, msg, 0.25)
    key_closed = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[键盘关闭状态]", key_closed)
    if key_closed["open"] or key_closed["close_count"] != 2 or key_closed["last_action"] != 3:
        raise RuntimeError("抽屉键盘关闭失败")

    ui.set_drawer_options(hwnd, g_drawer_id, placement=0, open=True,
                          modal=True, closable=True, close_on_mask=True, size=300)
    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、抽屉动画、遮罩和首屏尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
