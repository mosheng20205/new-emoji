import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tour_id = 0
g_target_id = 0
g_next_id = 0
g_close_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 漫游引导完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_next_id:
        ui.set_tour_active(g_hwnd, g_tour_id, 2)
        print(f"[跳到最后一步] 状态：{ui.get_tour_full_state(g_hwnd, g_tour_id)}")
    elif element_id == g_close_id:
        ui.set_tour_open(g_hwnd, g_tour_id, False)
        print(f"[关闭引导] 状态：{ui.get_tour_full_state(g_hwnd, g_tour_id)}")


def main():
    global g_hwnd, g_tour_id, g_target_id, g_next_id, g_close_id

    hwnd = ui.create_window("🧭 漫游引导完整组件验证", 220, 80, 980, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 600)

    ui.create_text(hwnd, content_id, "🧭 Tour 漫游引导完整封装", 28, 24, 520, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证目标元素绑定、遮罩策略、键盘下一步/关闭、步骤状态读回和中文 emoji 展示。",
        28, 72, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_target_id = ui.create_button(hwnd, content_id, "🎯", "被高亮目标", 80, 170, 180, 48)
    ui.create_infobox(
        hwnd,
        content_id,
        "✨ 引导说明",
        "引导卡片绑定左侧目标按钮。1 秒后发送右方向键进入下一步，2 秒后发送 Esc 关闭。",
        56,
        250,
        640,
        86,
    )

    g_next_id = ui.create_button(hwnd, content_id, "➡️", "跳到最后一步", 56, 390, 170, 42)
    g_close_id = ui.create_button(hwnd, content_id, "✅", "关闭引导", 250, 390, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_next_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_close_id, on_click)

    g_tour_id = ui.create_tour(
        hwnd,
        content_id,
        steps=[
            ("🧭 第一步：定位目标", "高亮目标按钮，验证目标元素绑定和遮罩绘制。"),
            ("⌨️ 第二步：键盘导航", "右方向键、回车或空格可以进入下一步，Esc 可以关闭。"),
            ("✅ 第三步：完成", "完整状态可读回，包括最近动作和变化次数。"),
        ],
        active=0,
        open=True,
        x=460,
        y=160,
        w=380,
        h=230,
    )
    ui.set_tour_target_element(hwnd, g_tour_id, g_target_id, padding=10)
    ui.set_tour_mask_behavior(hwnd, g_tour_id, pass_through=False, close_on_mask=True)

    initial = ui.get_tour_full_state(hwnd, g_tour_id)
    print(f"[初始] 状态：{initial}")
    if (
        not initial
        or initial["count"] != 3
        or not initial["open"]
        or initial["target_element_id"] != g_target_id
        or initial["target"][2] <= 0
        or initial["mask_passthrough"]
        or not initial["close_on_mask"]
    ):
        raise RuntimeError("漫游引导完整初始状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    ui.dll.EU_SetElementFocus(hwnd, g_tour_id)
    print("漫游引导完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_next = False
    auto_close = False
    verified_close = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_next and elapsed > 1.0:
            user32.PostMessageW(hwnd, 0x0100, 0x27, 0)
            auto_next = True
        if auto_next and not auto_close and elapsed > 2.0:
            state = ui.get_tour_full_state(hwnd, g_tour_id)
            print(f"[键盘下一步] 状态：{state}")
            if not state or state["active"] != 1 or state["last_action"] != 2:
                raise RuntimeError("漫游引导键盘下一步验证失败")
            user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)
            auto_close = True
        if auto_close and not verified_close and elapsed > 3.0:
            state = ui.get_tour_full_state(hwnd, g_tour_id)
            print(f"[键盘关闭] 状态：{state}")
            if not state or state["open"] or state["last_action"] != 3:
                raise RuntimeError("漫游引导键盘关闭验证失败")
            verified_close = True

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

    ui.set_tour_open(hwnd, g_tour_id, True)
    print("漫游引导完整组件示例结束。")


if __name__ == "__main__":
    main()
