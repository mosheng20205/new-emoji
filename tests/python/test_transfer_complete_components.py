import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_transfer_id = 0
g_filter_id = 0
g_bulk_id = 0
g_restore_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 穿梭框完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_filter_id:
        ui.set_transfer_filters(g_hwnd, g_transfer_id, "北", "")
        ui.set_transfer_item_disabled(g_hwnd, g_transfer_id, 0, 0, True)
        print(
            "[过滤禁用] "
            f"左匹配={ui.get_transfer_matched_count(g_hwnd, g_transfer_id, 0)} "
            f"左禁用={ui.get_transfer_disabled_count(g_hwnd, g_transfer_id, 0)} "
            f"北京禁用={ui.get_transfer_item_disabled(g_hwnd, g_transfer_id, 0, 0)}"
        )
    elif element_id == g_bulk_id:
        ui.transfer_move_all_right(g_hwnd, g_transfer_id)
        print(
            "[批量右移] "
            f"左侧={ui.get_transfer_count(g_hwnd, g_transfer_id, 0)} "
            f"右侧={ui.get_transfer_count(g_hwnd, g_transfer_id, 1)} "
            f"左匹配={ui.get_transfer_matched_count(g_hwnd, g_transfer_id, 0)}"
        )
    elif element_id == g_restore_id:
        ui.set_transfer_filters(g_hwnd, g_transfer_id, "", "")
        ui.transfer_move_all_left(g_hwnd, g_transfer_id)
        print(
            "[全部左移] "
            f"左侧={ui.get_transfer_count(g_hwnd, g_transfer_id, 0)} "
            f"右侧={ui.get_transfer_count(g_hwnd, g_transfer_id, 1)} "
            f"右禁用={ui.get_transfer_disabled_count(g_hwnd, g_transfer_id, 1)}"
        )


def main():
    global g_hwnd, g_transfer_id, g_filter_id, g_bulk_id, g_restore_id

    hwnd = ui.create_window("🔀 穿梭框完整验证", 230, 90, 900, 560)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 510)

    ui.create_text(hwnd, content_id, "🔀 穿梭框：过滤、禁用、批量移动", 28, 24, 560, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证穿梭框过滤后的匹配数量、禁用项不可移动、单项移动和批量移动能力。",
        28, 66, 760, 46,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_transfer_id = ui.create_transfer(
        hwnd,
        content_id,
        ["🏙️ 北京", "🌊 上海", "🌸 杭州", "🌴 广州", "🚀 深圳"],
        ["🐼 成都", "🌉 南京"],
        28, 130, 820, 210,
    )
    ui.set_transfer_item_disabled(hwnd, g_transfer_id, 0, 3, True)

    g_filter_id = ui.create_button(hwnd, content_id, "🔎", "过滤并禁用", 84, 374, 170, 42)
    g_bulk_id = ui.create_button(hwnd, content_id, "➡️", "批量右移", 280, 374, 150, 42)
    g_restore_id = ui.create_button(hwnd, content_id, "⬅️", "全部左移", 456, 374, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_filter_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_bulk_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_restore_id, on_click)

    ui.create_text(hwnd, content_id, "🚫 禁用项保留在原列表；批量移动只移动当前过滤范围内的可用项。", 28, 444, 740, 32)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[初始] "
        f"左侧={ui.get_transfer_count(hwnd, g_transfer_id, 0)} "
        f"右侧={ui.get_transfer_count(hwnd, g_transfer_id, 1)} "
        f"左禁用={ui.get_transfer_disabled_count(hwnd, g_transfer_id, 0)}"
    )
    print("穿梭框完整验证已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    did_filter = False
    did_bulk = False
    did_restore = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not did_filter and elapsed > 1.0:
            on_click(g_filter_id)
            did_filter = True
        if not did_bulk and elapsed > 2.0:
            on_click(g_bulk_id)
            did_bulk = True
        if not did_restore and elapsed > 4.0:
            on_click(g_restore_id)
            did_restore = True

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

    print(
        "[结果] "
        f"左侧={ui.get_transfer_count(hwnd, g_transfer_id, 0)} "
        f"右侧={ui.get_transfer_count(hwnd, g_transfer_id, 1)} "
        f"左匹配={ui.get_transfer_matched_count(hwnd, g_transfer_id, 0)}"
    )
    print("穿梭框完整验证结束。")


if __name__ == "__main__":
    main()
