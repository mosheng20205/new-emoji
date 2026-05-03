import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_work_id = 0
g_full_id = 0
g_scroll_id = 0
g_clamp_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 时间选择完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_scroll_id:
        ui.set_time_select_open(g_hwnd, g_full_id, True)
        ui.set_time_select_scroll(g_hwnd, g_full_id, 22)
        print(
            "[滚动] "
            f"全天状态={ui.get_time_select_state(g_hwnd, g_full_id)} "
            f"当前={ui.get_time_select_value(g_hwnd, g_full_id):04d}"
        )
    elif element_id == g_clamp_id:
        ui.set_time_select_time(g_hwnd, g_work_id, 7, 10)
        ui.set_time_select_time(g_hwnd, g_full_id, 23, 59)
        print(
            "[范围夹取] "
            f"工作时间={ui.get_time_select_value(g_hwnd, g_work_id):04d} "
            f"全天={ui.get_time_select_value(g_hwnd, g_full_id):04d}"
        )


def main():
    global g_hwnd, g_work_id, g_full_id, g_scroll_id, g_clamp_id

    hwnd = ui.create_window("🕒 时间选择完整组件", 220, 80, 880, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 860, 570)

    ui.create_text(hwnd, content_id, "🕒 时间选择完整验证", 28, 24, 360, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证固定高度候选列表、凌晨/上午/下午/晚上分组、滚轮滚动、键盘选择、状态读回和范围夹取。",
        28, 68, 760, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "💼 工作时间，15 分钟候选", 48, 148, 260, 28)
    g_work_id = ui.create_time_select(hwnd, content_id, 9, 30, 48, 184, 260, 40)
    ui.set_time_select_range(hwnd, g_work_id, 830, 1830)
    ui.set_time_select_options(hwnd, g_work_id, 15, 1)
    ui.set_time_select_open(hwnd, g_work_id, True)

    ui.create_text(hwnd, content_id, "🌙 全天候选，5 分钟步进", 410, 148, 260, 28)
    g_full_id = ui.create_time_select(hwnd, content_id, 14, 35, 410, 184, 260, 40)
    ui.set_time_select_range(hwnd, g_full_id, 0, 2355)
    ui.set_time_select_options(hwnd, g_full_id, 5, 0)
    ui.set_time_select_time(hwnd, g_full_id, 14, 35)
    ui.set_time_select_open(hwnd, g_full_id, True)
    ui.set_time_select_scroll(hwnd, g_full_id, 18)

    g_scroll_id = ui.create_button(hwnd, content_id, "🧭", "滚动候选", 48, 514, 150, 40)
    g_clamp_id = ui.create_button(hwnd, content_id, "📌", "测试范围夹取", 220, 514, 170, 40)
    ui.dll.EU_SetElementClickCallback(hwnd, g_scroll_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_clamp_id, on_click)

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "1 秒后自动滚动全天候选，2 秒后设置越界时间并打印夹取结果。窗口保持 60 秒。",
        430, 494, 360, 72,
    )

    print(
        "[初始] "
        f"工作={ui.get_time_select_value(hwnd, g_work_id):04d} "
        f"范围={ui.get_time_select_range(hwnd, g_work_id)} "
        f"选项={ui.get_time_select_options(hwnd, g_work_id)} "
        f"状态={ui.get_time_select_state(hwnd, g_work_id)} "
        f"全天={ui.get_time_select_value(hwnd, g_full_id):04d} "
        f"状态={ui.get_time_select_state(hwnd, g_full_id)}"
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("时间选择完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_scroll = False
    auto_clamp = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_scroll and elapsed > 1.0:
            on_click(g_scroll_id)
            auto_scroll = True
        if not auto_clamp and elapsed > 2.0:
            on_click(g_clamp_id)
            auto_clamp = True
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

    print("时间选择完整组件示例结束。")


if __name__ == "__main__":
    main()
