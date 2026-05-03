import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tooltip_id = 0
g_popover_id = 0
g_popconfirm_id = 0
g_update_id = 0
g_opened = False


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 浮层组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_opened
    if element_id == g_update_id:
        g_opened = not g_opened
        ui.set_tooltip_content(g_hwnd, g_tooltip_id, "💡 提示内容已通过 API 更新，并限制最大宽度。")
        ui.set_tooltip_options(g_hwnd, g_tooltip_id, placement=3, open=g_opened, max_width=260)
        assert ui.get_tooltip_options(g_hwnd, g_tooltip_id) == (3, g_opened, 260)

        ui.set_popover_title(g_hwnd, g_popover_id, "📌 当前批次")
        ui.set_popover_content(g_hwnd, g_popover_id, "Popover 支持标题、正文、尺寸、位置和关闭按钮。再次点击外部区域可关闭。")
        ui.set_popover_options(
            g_hwnd, g_popover_id,
            placement=3, open=g_opened,
            popup_width=300, popup_height=150, closable=True
        )
        assert ui.get_popover_options(g_hwnd, g_popover_id) == (3, g_opened, 300, 150, True)

        ui.set_popconfirm_content(g_hwnd, g_popconfirm_id, "⚠️ 删除确认", "确认要执行这个演示操作吗？")
        ui.set_popconfirm_buttons(g_hwnd, g_popconfirm_id, "确认", "取消")
        ui.set_popconfirm_options(g_hwnd, g_popconfirm_id, placement=2, open=g_opened,
                                  popup_width=310, popup_height=150)
        ui.dll.EU_ResetPopconfirmResult(g_hwnd, g_popconfirm_id)
        assert ui.get_popconfirm_options(g_hwnd, g_popconfirm_id) == (2, g_opened, 310, 150, -1)

        print(
            f"[更新] tooltip={ui.get_tooltip_options(g_hwnd, g_tooltip_id)}, "
            f"popover={ui.get_popover_options(g_hwnd, g_popover_id)}, "
            f"popconfirm={ui.get_popconfirm_options(g_hwnd, g_popconfirm_id)}"
        )


def main():
    global g_hwnd, g_tooltip_id, g_popover_id, g_popconfirm_id, g_update_id

    hwnd = ui.create_window("🪟 浮层组件示例", 240, 90, 900, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 570)

    ui.create_text(hwnd, content_id, "🪟 Tooltip / Popover / Popconfirm", 28, 24, 560, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐浮层组件的运行时 API：位置、打开状态、内容、标题、弹层尺寸、确认按钮和结果查询。",
        28, 68, 700, 48,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_tooltip_id = ui.create_tooltip(
        hwnd, content_id,
        "悬停提示",
        "💡 初始提示",
        placement=2,
        x=40, y=156, w=150, h=40,
    )
    ui.set_tooltip_options(hwnd, g_tooltip_id, placement=2, open=False, max_width=280)
    assert ui.get_tooltip_options(hwnd, g_tooltip_id) == (2, False, 280)

    g_popover_id = ui.create_popover(
        hwnd, content_id,
        "打开弹出卡片",
        "📌 弹出卡片",
        "这里展示可关闭的弹出内容。",
        placement=3,
        x=260, y=156, w=170, h=40,
    )
    ui.set_popover_options(hwnd, g_popover_id, placement=3, open=False,
                           popup_width=250, popup_height=132, closable=True)
    assert ui.get_popover_options(hwnd, g_popover_id) == (3, False, 250, 132, True)

    g_popconfirm_id = ui.create_popconfirm(
        hwnd, content_id,
        "危险操作",
        "⚠️ 操作确认",
        "确认继续吗？",
        "确认",
        "取消",
        placement=2,
        x=500, y=156, w=160, h=40,
    )
    ui.set_popconfirm_options(hwnd, g_popconfirm_id, placement=2, open=False,
                              popup_width=286, popup_height=146)
    assert ui.get_popconfirm_options(hwnd, g_popconfirm_id) == (2, False, 286, 146, -1)

    g_update_id = ui.create_button(hwnd, content_id, "🔁", "切换浮层状态", 40, 460, 180, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "说明",
        "示例会在 1 秒后自动打开全部浮层。也可以点击按钮反复切换，Popconfirm 的确认/取消结果可通过导出 API 读取。",
        40, 340, 620, 90
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[浮层组件读回] "
        f"Tooltip={ui.get_tooltip_options(hwnd, g_tooltip_id)} "
        f"Popover={ui.get_popover_options(hwnd, g_popover_id)} "
        f"Popconfirm={ui.get_popconfirm_options(hwnd, g_popconfirm_id)}"
    )
    print("浮层组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_done = False
    while running and time.time() - start < 60:
        if not auto_done and time.time() - start > 1.0:
            on_click(g_update_id)
            auto_done = True
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

    print("浮层组件示例结束。")


if __name__ == "__main__":
    main()
