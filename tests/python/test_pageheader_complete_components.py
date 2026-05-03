import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_header_id = 0
g_back_id = 0
g_crumb_id = 0
g_action_id = 0
g_reset_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 页头完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_back_id:
        ui.trigger_pageheader_back(g_hwnd, g_header_id)
        print(f"[返回] 状态={ui.get_pageheader_state(g_hwnd, g_header_id)}")
    elif element_id == g_crumb_id:
        ui.set_pageheader_breadcrumb_active(g_hwnd, g_header_id, 2)
        print(f"[面包屑] 状态={ui.get_pageheader_state(g_hwnd, g_header_id)}")
    elif element_id == g_action_id:
        ui.set_pageheader_active_action(g_hwnd, g_header_id, 1)
        print(f"[操作项] 状态={ui.get_pageheader_state(g_hwnd, g_header_id)}")
    elif element_id == g_reset_id:
        ui.reset_pageheader_result(g_hwnd, g_header_id)
        print(f"[重置] 状态={ui.get_pageheader_state(g_hwnd, g_header_id)}")


def main():
    global g_hwnd, g_header_id, g_back_id, g_crumb_id, g_action_id, g_reset_id

    hwnd = ui.create_window("📄 页头完整组件", 220, 80, 980, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 560)

    g_header_id = ui.create_pageheader(
        hwnd,
        content_id,
        title="📄 组件封装详情",
        subtitle="验证返回事件、面包屑和右侧操作区",
        back_text="返回列表",
        x=24,
        y=24,
        w=890,
        h=92,
    )
    ui.set_pageheader_breadcrumbs(hwnd, g_header_id, ["🏠 首页", "🧩 组件", "📄 页头"])
    ui.set_pageheader_actions(hwnd, g_header_id, ["🔄 刷新", "💾 保存", "🚀 发布"])
    ui.set_pageheader_back_text(hwnd, g_header_id, "⬅️ 返回列表")

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "1 秒后触发返回，2 秒后激活面包屑，3 秒后激活操作项，4 秒后重置状态。窗口保持 60 秒。",
        48,
        152,
        760,
        86,
    )

    g_back_id = ui.create_button(hwnd, content_id, "⬅️", "触发返回", 48, 304, 150, 42)
    g_crumb_id = ui.create_button(hwnd, content_id, "🧭", "激活面包屑", 220, 304, 170, 42)
    g_action_id = ui.create_button(hwnd, content_id, "💾", "激活保存", 412, 304, 150, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "♻️", "重置状态", 584, 304, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_back_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_crumb_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_action_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    initial = ui.get_pageheader_state(hwnd, g_header_id)
    print(f"[初始] 状态={initial}")
    if not initial or initial["action_count"] != 3 or initial["breadcrumb_count"] != 3:
        raise RuntimeError("页头初始状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("页头完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_back = False
    auto_crumb = False
    auto_action = False
    auto_reset = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_back and elapsed > 1.0:
            on_click(g_back_id)
            auto_back = True
        if not auto_crumb and elapsed > 2.0:
            on_click(g_crumb_id)
            auto_crumb = True
        if not auto_action and elapsed > 3.0:
            on_click(g_action_id)
            auto_action = True
        if not auto_reset and elapsed > 4.0:
            on_click(g_reset_id)
            auto_reset = True
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

    print("页头完整组件示例结束。")


if __name__ == "__main__":
    main()
