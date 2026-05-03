import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_calendar_id = 0
g_tree_id = 0
g_transfer_id = 0
g_calendar_btn_id = 0
g_tree_btn_id = 0
g_transfer_btn_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 高级组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_calendar_btn_id:
        ui.dll.EU_SetCalendarDate(g_hwnd, g_calendar_id, 2026, 6, 18)
        print("[日历] 已切换到 2026-06-18")
    elif element_id == g_tree_btn_id:
        ui.dll.EU_SetTreeSelected(g_hwnd, g_tree_id, 4)
        current = ui.dll.EU_GetTreeSelected(g_hwnd, g_tree_id)
        print(f"[树形控件] 当前选中节点索引：{current}")
    elif element_id == g_transfer_btn_id:
        left = ui.make_utf8("上海|杭州|广州|深圳")
        right = ui.make_utf8("北京|成都")
        ui.dll.EU_SetTransferItems(
            g_hwnd, g_transfer_id,
            ui.bytes_arg(left), len(left),
            ui.bytes_arg(right), len(right)
        )
        print("[穿梭框] 已重置左右列表")
    else:
        print(f"[高级组件] 点击元素 #{element_id}")


def main():
    global g_hwnd, g_calendar_id, g_tree_id, g_transfer_id
    global g_calendar_btn_id, g_tree_btn_id, g_transfer_btn_id

    hwnd = ui.create_window("高级组件示例", 240, 90, 920, 700)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 650)

    ui.create_text(hwnd, content_id, "高级组件", 28, 24, 220, 28)
    ui.create_divider(hwnd, content_id, "分割线 Divider ✨", 0, 1, 28, 62, 820, 36)

    g_calendar_id = ui.create_calendar(
        hwnd, content_id,
        2026, 5, 2,
        28, 116, 360, 300
    )

    tree_items = [
        ("Element Plus 组件", 0, True),
        ("基础组件", 1, True),
        ("按钮 Button", 2, True),
        ("图标 Icon", 2, True),
        ("数据组件", 1, True),
        ("日历 Calendar", 2, True),
        ("树形控件 Tree", 2, True),
        ("穿梭框 Transfer", 2, True),
    ]
    g_tree_id = ui.create_tree(
        hwnd, content_id,
        tree_items,
        5,
        420, 116, 420, 230
    )

    g_calendar_btn_id = ui.create_button(
        hwnd, content_id,
        "",
        "切换日历",
        420, 364, 126, 38
    )
    g_tree_btn_id = ui.create_button(
        hwnd, content_id,
        "",
        "选中节点",
        562, 364, 126, 38
    )
    g_transfer_btn_id = ui.create_button(
        hwnd, content_id,
        "",
        "重置列表",
        704, 364, 126, 38
    )

    ui.create_divider(hwnd, content_id, "穿梭框 Transfer", 0, 0, 28, 424, 812, 32)
    g_transfer_id = ui.create_transfer(
        hwnd, content_id,
        ["上海", "杭州", "广州", "深圳", "南京"],
        ["北京", "成都"],
        28, 468, 812, 156
    )

    for eid in (g_calendar_btn_id, g_tree_btn_id, g_transfer_btn_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("高级组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < 60:
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

    print("高级组件示例结束。")


if __name__ == "__main__":
    main()
