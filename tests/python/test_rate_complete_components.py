import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 900
WINDOW_H = 600
CONTENT_W = 880
CONTENT_H = 550

g_hwnd = None
g_rate_id = 0
g_readonly_id = 0
g_status_id = 0
g_apply_id = 0
g_clear_id = 0
g_change_callback = None
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Rate 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.ValueCallback
def on_rate_change(element_id, value_x2, value, max_value):
    g_events.append((element_id, value_x2, value, max_value))
    print(f"[评分回调] 元素={element_id} 半星值={value_x2} 整数={value} 最大={max_value}")
    update_status(f"⭐ 回调：半星值 {value_x2}，整数星 {value}/{max_value}")


def print_state(prefix):
    print(
        f"{prefix} 半星={ui.get_rate_value_x2(g_hwnd, g_rate_id)} "
        f"整数={ui.get_rate_value(g_hwnd, g_rate_id)} "
        f"最大={ui.get_rate_max(g_hwnd, g_rate_id)} "
        f"选项={ui.get_rate_options(g_hwnd, g_rate_id)} "
        f"只读半星={ui.get_rate_value_x2(g_hwnd, g_readonly_id)} "
        f"回调次数={len(g_events)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_rate_options(g_hwnd, g_rate_id, allow_clear=True, allow_half=True, readonly=False)
        ui.set_rate_texts(g_hwnd, g_rate_id, "待体验 💤", "很满意 🎉", True)
        ui.set_rate_value_x2(g_hwnd, g_rate_id, 7)
        ui.set_rate_max(g_hwnd, g_rate_id, 6)
        ui.set_rate_value_x2(g_hwnd, g_rate_id, 11)
        update_status("✅ 已设置为 5.5/6 星，并触发变化回调。")
        print_state("[应用状态]")
    elif element_id == g_clear_id:
        ui.set_rate_value_x2(g_hwnd, g_rate_id, 0)
        update_status("🧹 已清空评分，验证 allow_clear 与低分文案。")
        print_state("[清空状态]")


def main():
    global g_hwnd, g_rate_id, g_readonly_id, g_status_id, g_apply_id, g_clear_id
    global g_change_callback

    hwnd = ui.create_window("⭐ Rate 完整封装验证", 240, 120, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_change_callback = on_rate_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    ui.create_text(hwnd, content_id, "⭐ 评分组件完整能力", 28, 24, 380, 34)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证半星、清除、最大值夹取、只读拦截、评分文案、Set/Get 和评分变化回调。",
        28,
        68,
        780,
        52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_rate_id = ui.create_rate(
        hwnd, content_id, "体验", 3, 5, 36, 150, 520, 44,
        allow_clear=True, allow_half=True, readonly=False, value_x2=6,
    )
    ui.set_rate_texts(hwnd, g_rate_id, "待评分 😴", "已评分 🌟", True)
    ui.set_rate_change_callback(hwnd, g_rate_id, g_change_callback)

    g_readonly_id = ui.create_rate(
        hwnd, content_id, "只读", 4, 5, 36, 226, 520, 44,
        allow_clear=False, allow_half=False, readonly=True, value_x2=8,
    )
    ui.set_rate_texts(hwnd, g_readonly_id, "不可编辑 🔒", "展示评分 🔒", True)

    panel_id = ui.create_panel(hwnd, content_id, 590, 142, 250, 180)
    ui.set_panel_style(hwnd, panel_id, 0x10FFB300, 0x66FFB300, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "🔎 状态读回", 0, 0, 180, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待自动设置评分。", 0, 48, 190, 90)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "设置 5.5 星", 590, 352, 150, 42)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空评分", 36, 352, 130, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_clear_id, on_click)

    ui.create_alert(
        hwnd,
        content_id,
        "📐 首屏尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 840，最下内容约 394，保留足够逻辑余量。",
        0,
        0,
        False,
        36,
        438,
        780,
        60,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("Rate 完整封装验证已显示。窗口会保持 60 秒。")
    print_state("[初始状态]")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_stage = 0
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if auto_stage == 0 and elapsed > 1.0:
            on_click(g_apply_id)
            auto_stage = 1
        elif auto_stage == 1 and elapsed > 3.0:
            on_click(g_clear_id)
            auto_stage = 2
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

    print("Rate 完整封装验证结束。")


if __name__ == "__main__":
    main()
