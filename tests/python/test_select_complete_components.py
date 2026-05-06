import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 920
WINDOW_H = 640
CONTENT_W = 900
CONTENT_H = 590

g_hwnd = None
g_select_id = 0
g_multi_id = 0
g_status_id = 0
g_apply_id = 0
g_reset_id = 0
g_change_callback = None
g_callback_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Select 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.ValueCallback
def on_select_change(element_id, current_index, selected_count, open_state):
    g_callback_events.append((element_id, current_index, selected_count, open_state))
    print(
        f"[选择器回调] 元素={element_id} 当前={current_index} "
        f"数量={selected_count} 打开={open_state}"
    )


def print_state(prefix):
    single = ui.get_select_index(g_hwnd, g_select_id)
    multi = ui.get_select_selected_indices(g_hwnd, g_multi_id)
    print(
        f"{prefix} 单选={single} 打开={ui.get_select_open(g_hwnd, g_select_id)} "
        f"匹配={ui.get_select_matched_count(g_hwnd, g_select_id)} "
        f"禁用项1={ui.get_select_option_disabled(g_hwnd, g_select_id, 1)} "
        f"多选模式={ui.get_select_multiple(g_hwnd, g_multi_id)} "
        f"多选={multi} 数量={ui.get_select_selected_count(g_hwnd, g_multi_id)} "
        f"回调次数={len(g_callback_events)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_select_open(g_hwnd, g_select_id, True)
        ui.set_select_search(g_hwnd, g_select_id, "🍊")
        ui.set_select_option_disabled(g_hwnd, g_select_id, 1, True)
        ui.set_select_option_alignment(g_hwnd, g_select_id, 2)
        ui.set_select_value_alignment(g_hwnd, g_select_id, 2)
        before = ui.get_select_index(g_hwnd, g_select_id)
        ui.set_select_index(g_hwnd, g_select_id, 1)
        after_disabled_try = ui.get_select_index(g_hwnd, g_select_id)
        ui.set_select_index(g_hwnd, g_select_id, 2)

        ui.set_select_multiple(g_hwnd, g_multi_id, True)
        ui.set_select_option_disabled(g_hwnd, g_multi_id, 3, True)
        ui.set_select_option_alignment(g_hwnd, g_multi_id, 1)
        ui.set_select_value_alignment(g_hwnd, g_multi_id, 1)
        ui.set_select_selected_indices(g_hwnd, g_multi_id, [0, 2, 3, 4])
        selected = ui.get_select_selected_indices(g_hwnd, g_multi_id)
        single_align = ui.get_select_option_alignment(g_hwnd, g_select_id)
        multi_align = ui.get_select_option_alignment(g_hwnd, g_multi_id)
        single_value_align = ui.get_select_value_alignment(g_hwnd, g_select_id)
        multi_value_align = ui.get_select_value_alignment(g_hwnd, g_multi_id)
        if single_align != 2 or multi_align != 1 or single_value_align != 2 or multi_value_align != 1:
            raise RuntimeError(
                f"Select 对齐读回异常：option=({single_align},{multi_align}), value=({single_value_align},{multi_value_align})"
            )
        print(
            "[应用] 禁用选择前后:",
            before,
            after_disabled_try,
            "多选读回:",
            selected,
            "对齐:",
            single_align,
            multi_align,
            single_value_align,
            multi_value_align,
        )
        update_status(f"✅ 单选匹配 {ui.get_select_matched_count(g_hwnd, g_select_id)} 项，多选读回 {selected}，表项对齐已读回。")
        print_state("[应用状态]")
    elif element_id == g_reset_id:
        ui.set_select_search(g_hwnd, g_select_id, "")
        ui.set_select_open(g_hwnd, g_select_id, False)
        ui.set_select_option_disabled(g_hwnd, g_select_id, 1, False)
        ui.set_select_option_alignment(g_hwnd, g_select_id, 0)
        ui.set_select_value_alignment(g_hwnd, g_select_id, 0)
        ui.set_select_index(g_hwnd, g_select_id, 0)
        ui.set_select_multiple(g_hwnd, g_multi_id, False)
        ui.set_select_option_disabled(g_hwnd, g_multi_id, 3, False)
        ui.set_select_option_alignment(g_hwnd, g_multi_id, 0)
        ui.set_select_value_alignment(g_hwnd, g_multi_id, 0)
        ui.set_select_index(g_hwnd, g_multi_id, 1)
        update_status("↩ 已恢复单选与多选默认状态。")
        print_state("[恢复状态]")


def main():
    global g_hwnd, g_select_id, g_multi_id, g_status_id, g_apply_id, g_reset_id
    global g_change_callback

    hwnd = ui.create_window("🎛️ Select 完整封装验证", 220, 120, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_change_callback = on_select_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    ui.create_text(hwnd, content_id, "🎛️ 选择器完整能力", 28, 24, 360, 34)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证单选弹层、搜索、禁用项、表项/已选值对齐、空状态、多选读写、选中数量读取和变化回调；窗口首屏预留足够逻辑边距。",
        28,
        68,
        820,
        52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "🍱 单选午餐", 36, 138, 180, 28)
    g_select_id = ui.create_select(
        hwnd,
        content_id,
        "午餐",
        ["米饭 🍚", "面条 🍜", "橙汁 🍊", "沙拉 🥗", "汤品 🍲"],
        0,
        36,
        176,
        360,
        42,
    )
    ui.set_select_option_disabled(hwnd, g_select_id, 1, True)
    ui.dll.EU_SetSelectChangeCallback(hwnd, g_select_id, g_change_callback)

    ui.create_text(hwnd, content_id, "🧩 多选能力", 36, 282, 180, 28)
    g_multi_id = ui.create_select(
        hwnd,
        content_id,
        "配料",
        ["香菜 🌿", "辣椒 🌶️", "鸡蛋 🥚", "海鲜 🦐", "芝士 🧀"],
        0,
        36,
        320,
        360,
        42,
    )
    ui.set_select_multiple(hwnd, g_multi_id, True)
    ui.set_select_selected_indices(hwnd, g_multi_id, [0, 2])
    ui.set_select_open(hwnd, g_multi_id, True)
    ui.dll.EU_SetSelectChangeCallback(hwnd, g_multi_id, g_change_callback)

    panel_id = ui.create_panel(hwnd, content_id, 450, 138, 390, 224)
    ui.set_panel_style(hwnd, panel_id, 0x108E24AA, 0x668E24AA, 1.0, 12.0, 18)
    ui.create_text(hwnd, panel_id, "🔎 状态读回", 0, 0, 220, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待自动应用选择器状态。", 0, 48, 320, 104)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "应用并读取", 450, 392, 150, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "↩", "恢复默认", 620, 392, 140, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_alert(
        hwnd,
        content_id,
        "📐 首屏尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 840，最下内容约 434，保留 20px 以上逻辑余量。",
        0,
        0,
        False,
        36,
        472,
        780,
        60,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("Select 完整封装验证已显示。窗口会保持 60 秒。")
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
            on_click(g_reset_id)
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

    print("Select 完整封装验证结束。")


if __name__ == "__main__":
    main()
