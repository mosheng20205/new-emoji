import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_mentions_id = 0
g_filter_id = 0
g_insert_id = 0
g_trigger_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 提及输入完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_filter_id:
        ui.set_mentions_value(g_hwnd, g_mentions_id, "请 @设")
        ui.set_mentions_filter(g_hwnd, g_mentions_id, "设")
        ui.set_mentions_open(g_hwnd, g_mentions_id, True)
        print(f"[过滤] {ui.get_mentions_options(g_hwnd, g_mentions_id)}")
    elif element_id == g_insert_id:
        ui.set_mentions_selected(g_hwnd, g_mentions_id, 0)
        ui.insert_mentions_selected(g_hwnd, g_mentions_id)
        print(f"[插入] 值={ui.get_mentions_value(g_hwnd, g_mentions_id)}")
    elif element_id == g_trigger_id:
        ui.set_mentions_options(g_hwnd, g_mentions_id, "#", True, True)
        ui.set_mentions_value(g_hwnd, g_mentions_id, "话题 #组")
        ui.set_mentions_filter(g_hwnd, g_mentions_id, "组")
        ui.set_mentions_open(g_hwnd, g_mentions_id, True)
        print(f"[触发符] {ui.get_mentions_options(g_hwnd, g_mentions_id)}")


def main():
    global g_hwnd, g_mentions_id, g_filter_id, g_insert_id, g_trigger_id

    hwnd = ui.create_window("💬 提及输入完整验证", 240, 90, 760, 500)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 740, 450)

    ui.create_text(hwnd, content_id, "💬 提及输入：触发、过滤、插入", 28, 24, 520, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证 @ 或 # 触发建议、过滤匹配、选择插入和 UTF-8 文本读回。",
        28, 66, 660, 46,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_mentions_id = ui.create_mentions(
        hwnd,
        content_id,
        "请 @",
        ["👩‍💻 设计师", "🧑‍🔧 开发者", "🧪 测试员", "👥 组件组"],
        28, 150, 380, 42,
    )
    ui.set_mentions_options(hwnd, g_mentions_id, "@", True, True)
    ui.set_mentions_open(hwnd, g_mentions_id, True)

    g_filter_id = ui.create_button(hwnd, content_id, "🔎", "过滤“设”", 450, 146, 170, 42)
    g_insert_id = ui.create_button(hwnd, content_id, "✅", "插入选中", 450, 204, 170, 42)
    g_trigger_id = ui.create_button(hwnd, content_id, "#️⃣", "切换#触发", 450, 262, 170, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_filter_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_insert_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_trigger_id, on_click)

    ui.create_text(hwnd, content_id, "⌨️ 输入触发字符后弹出建议，回车会插入当前选中项。", 28, 388, 620, 32)

    ui.dll.EU_ShowWindow(hwnd, 1)
    ui.dll.EU_SetElementFocus(hwnd, g_mentions_id)
    print(f"[初始] {ui.get_mentions_options(hwnd, g_mentions_id)}")
    print("提及输入完整验证已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    did_filter = False
    did_insert = False
    did_trigger = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not did_filter and elapsed > 1.0:
            on_click(g_filter_id)
            did_filter = True
        if not did_insert and elapsed > 2.0:
            on_click(g_insert_id)
            did_insert = True
        if not did_trigger and elapsed > 4.0:
            on_click(g_trigger_id)
            did_trigger = True

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

    print(f"[结果] 值={ui.get_mentions_value(hwnd, g_mentions_id)} 状态={ui.get_mentions_options(hwnd, g_mentions_id)}")
    print("提及输入完整验证结束。")


if __name__ == "__main__":
    main()
