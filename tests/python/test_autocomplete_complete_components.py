import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_auto_id = 0
g_loading_id = 0
g_result_id = 0
g_empty_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 自动补全完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_loading_id:
        ui.set_autocomplete_value(g_hwnd, g_auto_id, "杭")
        ui.set_autocomplete_async_state(g_hwnd, g_auto_id, True, 20260503)
        print(f"[异步请求] {ui.get_autocomplete_options(g_hwnd, g_auto_id)}")
    elif element_id == g_result_id:
        ui.set_autocomplete_suggestions(g_hwnd, g_auto_id, ["🌸 杭州", "🏞️ 杭州西湖", "🚄 杭州东站"])
        ui.set_autocomplete_open(g_hwnd, g_auto_id, True)
        ui.set_autocomplete_selected(g_hwnd, g_auto_id, 1)
        print(
            "[建议返回] "
            f"值={ui.get_autocomplete_value(g_hwnd, g_auto_id)} "
            f"状态={ui.get_autocomplete_options(g_hwnd, g_auto_id)}"
        )
    elif element_id == g_empty_id:
        ui.set_autocomplete_empty_text(g_hwnd, g_auto_id, "🫥 没找到城市建议")
        ui.set_autocomplete_suggestions(g_hwnd, g_auto_id, [])
        ui.set_autocomplete_open(g_hwnd, g_auto_id, True)
        print(f"[空状态] {ui.get_autocomplete_options(g_hwnd, g_auto_id)}")


def main():
    global g_hwnd, g_auto_id, g_loading_id, g_result_id, g_empty_id

    hwnd = ui.create_window("🔎 自动补全完整验证", 240, 90, 760, 500)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 740, 450)

    ui.create_text(hwnd, content_id, "🔎 自动补全：异步建议与空状态", 28, 24, 520, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证加载中状态、请求ID、建议返回、选中读回和没有匹配建议时的中文 emoji 空状态。",
        28, 66, 660, 48,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "🏙️ 城市", 28, 138, 120, 28)
    g_auto_id = ui.create_autocomplete(
        hwnd,
        content_id,
        "北",
        ["🏙️ 北京", "🌊 上海", "🌸 杭州", "🚀 深圳"],
        28, 174, 360, 42,
    )
    ui.set_autocomplete_open(hwnd, g_auto_id, True)

    g_loading_id = ui.create_button(hwnd, content_id, "⏳", "模拟异步请求", 430, 170, 180, 42)
    g_result_id = ui.create_button(hwnd, content_id, "✅", "写入建议结果", 430, 228, 180, 42)
    g_empty_id = ui.create_button(hwnd, content_id, "🫥", "显示空状态", 430, 286, 180, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_loading_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_result_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_empty_id, on_click)

    ui.create_text(hwnd, content_id, "⌨️ 聚焦输入框后可键入中文，方向键切换建议，回车/空格打开弹层。", 28, 388, 660, 32)

    ui.dll.EU_ShowWindow(hwnd, 1)
    ui.dll.EU_SetElementFocus(hwnd, g_auto_id)
    print(f"[初始] {ui.get_autocomplete_options(hwnd, g_auto_id)}")
    print("自动补全完整验证已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    did_loading = False
    did_result = False
    did_empty = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not did_loading and elapsed > 1.0:
            on_click(g_loading_id)
            did_loading = True
        if not did_result and elapsed > 2.0:
            on_click(g_result_id)
            did_result = True
        if not did_empty and elapsed > 4.0:
            on_click(g_empty_id)
            did_empty = True

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

    print(f"[结果] {ui.get_autocomplete_options(hwnd, g_auto_id)}")
    print("自动补全完整验证结束。")


if __name__ == "__main__":
    main()
