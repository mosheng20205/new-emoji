import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_affix_id = 0
g_container_id = 0
g_fix_id = 0
g_release_id = 0
g_options_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 固钉完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_fix_id:
        ui.set_affix_options(
            g_hwnd, g_affix_id,
            scroll_position=420,
            offset=180,
            container_id=g_container_id,
            placeholder_height=92,
            z_index=30,
        )
        print(f"[模拟固定] 状态：{ui.get_affix_options(g_hwnd, g_affix_id)}")
    elif element_id == g_release_id:
        ui.set_affix_options(
            g_hwnd, g_affix_id,
            scroll_position=80,
            offset=180,
            container_id=g_container_id,
            placeholder_height=92,
            z_index=30,
        )
        print(f"[回到原位] 状态：{ui.get_affix_options(g_hwnd, g_affix_id)}")
    elif element_id == g_options_id:
        print(f"[读取完整选项] 状态：{ui.get_affix_options(g_hwnd, g_affix_id)}")


def main():
    global g_hwnd, g_affix_id, g_container_id, g_fix_id, g_release_id, g_options_id

    hwnd = ui.create_window("📌 固钉完整组件验证", 220, 80, 940, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    g_container_id = ui.create_container(hwnd, 0, 0, 0, 900, 560)

    ui.create_text(hwnd, g_container_id, "📌 固钉 Affix 完整封装", 28, 24, 420, 38)
    intro_id = ui.create_text(
        hwnd,
        g_container_id,
        "本示例验证滚动容器绑定、固定阈值、占位高度、固定层级、固定顶部读回、Set/Get 状态和中文 emoji 展示。",
        28, 70, 790, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_affix_id = ui.create_affix(
        hwnd,
        g_container_id,
        title="📌 订单筛选栏",
        body="滚动超过阈值后保持在顶部，保留占位高度避免内容跳动。",
        offset=180,
        x=48,
        y=150,
        w=620,
        h=92,
    )
    ui.set_affix_options(
        hwnd,
        g_affix_id,
        scroll_position=60,
        offset=180,
        container_id=g_container_id,
        placeholder_height=92,
        z_index=30,
    )

    ui.create_infobox(
        hwnd,
        g_container_id,
        "🧭 验证提示",
        "1 秒后模拟滚动超过阈值进入固定；2 秒后读取完整选项；3 秒后滚回阈值以下。窗口会保持 60 秒可见。",
        48,
        282,
        720,
        86,
    )

    g_fix_id = ui.create_button(hwnd, g_container_id, "📌", "模拟固定", 48, 410, 140, 42)
    g_options_id = ui.create_button(hwnd, g_container_id, "🧾", "读取状态", 210, 410, 140, 42)
    g_release_id = ui.create_button(hwnd, g_container_id, "↩️", "回到原位", 372, 410, 140, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_fix_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_options_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_release_id, on_click)

    initial = ui.get_affix_options(hwnd, g_affix_id)
    print(f"[初始] 状态：{initial}")
    if (
        not initial
        or initial["fixed"]
        or initial["container_id"] != g_container_id
        or initial["placeholder_height"] != 92
        or initial["z_index"] != 30
    ):
        raise RuntimeError("固钉初始完整状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("固钉完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_fix = False
    auto_read = False
    auto_release = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_fix and elapsed > 1.0:
            on_click(g_fix_id)
            fixed_state = ui.get_affix_options(hwnd, g_affix_id)
            if not fixed_state or not fixed_state["fixed"] or fixed_state["fixed_top"] != 180:
                raise RuntimeError("固钉固定状态读回失败")
            auto_fix = True
        if not auto_read and elapsed > 2.0:
            on_click(g_options_id)
            auto_read = True
        if not auto_release and elapsed > 3.0:
            on_click(g_release_id)
            release_state = ui.get_affix_options(hwnd, g_affix_id)
            if not release_state or release_state["fixed"]:
                raise RuntimeError("固钉回到原位状态读回失败")
            auto_release = True

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

    print("固钉完整组件示例结束。")


if __name__ == "__main__":
    main()
