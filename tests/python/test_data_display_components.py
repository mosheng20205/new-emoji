import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_collapse_id = 0
g_stat_id = 0
g_update_id = 0
g_counter = 1280


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 数据展示组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    global g_counter

    if element_id == g_update_id:
        g_counter += 37
        value_data = ui.make_utf8(str(g_counter))
        ui.dll.EU_SetStatisticValue(
            g_hwnd, g_stat_id, ui.bytes_arg(value_data), len(value_data)
        )
        print(f"[统计数值] {g_counter}")
    elif element_id == g_collapse_id:
        active = ui.dll.EU_GetCollapseActive(g_hwnd, g_collapse_id)
        print(f"[折叠面板] 当前展开项={active}")
    else:
        print(f"[数据展示] 点击元素 #{element_id}")


def main():
    global g_hwnd, g_collapse_id, g_stat_id, g_update_id

    hwnd = ui.create_window("数据展示组件示例", 240, 90, 920, 650)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 600)

    ui.create_text(hwnd, content_id, "数据展示组件", 28, 24, 260, 28)

    card_id = ui.create_card(
        hwnd, content_id,
        "卡片 Card",
        "用于承载一组信息，支持标题、正文和阴影效果。这里可以显示 emoji：🚀✅",
        2,
        28, 70, 360, 150
    )

    ui.create_card(
        hwnd, content_id,
        "轻量卡片",
        "shadow=never 的卡片更适合密集界面。",
        0,
        410, 70, 300, 150
    )

    g_stat_id = ui.create_statistic(
        hwnd, content_id,
        "今日访问",
        "1280",
        "",
        " 次",
        28, 244, 210, 112
    )
    ui.create_statistic(
        hwnd, content_id,
        "转化率",
        "18.6",
        "",
        "%",
        258, 244, 210, 112
    )
    g_update_id = ui.create_button(
        hwnd, content_id,
        "",
        "更新统计值",
        500, 280, 150, 42
    )

    g_collapse_id = ui.create_collapse(
        hwnd, content_id,
        [
            ("一致性", "与现实生活一致：遵循用户习惯和平台约定。"),
            ("反馈", "通过界面样式和交互状态，让用户清楚当前发生了什么。"),
            ("效率", "简化操作路径，避免用户在重复任务中付出额外成本。"),
        ],
        0,
        True,
        28, 378, 390, 190
    )

    ui.create_timeline(
        hwnd, content_id,
        [
            ("09:00", "创建窗口并初始化 D2D 渲染环境", 0),
            ("10:30", "完成组件样式和交互细节", 1),
            ("14:20", "接入 Python 示例和导出接口", 2),
            ("16:00", "编译并执行烟测验证", 3),
        ],
        450, 378, 390, 210
    )

    for eid in (card_id, g_collapse_id, g_stat_id, g_update_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("数据展示组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("数据展示组件示例结束。")


if __name__ == "__main__":
    main()
