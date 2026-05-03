import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_info_id = 0
g_space_id = 0
g_divider_id = 0
g_update_id = 0
g_spacing_large = False


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 基础工具组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_spacing_large
    if element_id == g_update_id:
        g_spacing_large = not g_spacing_large
        ui.set_space_size(g_hwnd, g_space_id, 72 if g_spacing_large else 24, 36)
        ui.set_infobox_text(
            g_hwnd,
            g_info_id,
            "✅ 状态已更新" if g_spacing_large else "ℹ️ 信息提示",
            "Space 占位已放大，虚线分割线和可关闭信息框都通过导出 API 动态设置。",
        )
        ui.set_infobox_options(
            g_hwnd,
            g_info_id,
            type=1 if g_spacing_large else 0,
            closable=True,
            accent=0,
            icon="✅" if g_spacing_large else "💡",
        )
        ui.set_divider_options(
            g_hwnd,
            g_divider_id,
            direction=0,
            content_position=2 if g_spacing_large else 1,
            color=0xFF7C3AED if g_spacing_large else 0xFF2563EB,
            width=2.0,
            dashed=g_spacing_large,
            text="🧭 动态分割线",
        )
        print("[更新] 信息框、占位和分割线选项已切换")
    elif element_id == g_info_id:
        print("[信息框] 关闭按钮已触发")


def main():
    global g_hwnd, g_info_id, g_space_id, g_divider_id, g_update_id

    hwnd = ui.create_window("🧰 基础工具组件示例", 240, 100, 860, 560)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 840, 510)

    ui.create_text(hwnd, content_id, "🧰 InfoBox / Space / Divider", 28, 24, 520, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐了信息框类型与关闭、Space 运行时占位调整、Divider 虚线和动态文本设置。",
        28, 68, 620, 46,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_info_id = ui.create_infobox(
        hwnd,
        content_id,
        "ℹ️ 信息提示",
        "这是一个可关闭的信息框。点击右上角关闭按钮会隐藏组件，点击下方按钮会重新更新状态。",
        28,
        136,
        560,
        96,
    )
    ui.set_infobox_options(hwnd, g_info_id, type=0, closable=True, accent=0, icon="💡")

    g_divider_id = ui.create_divider(
        hwnd,
        content_id,
        "🧭 动态分割线",
        0,
        1,
        28,
        260,
        560,
        38,
    )
    ui.set_divider_options(hwnd, g_divider_id, 0, 1, 0xFF2563EB, 2.0, False, "🧭 动态分割线")

    layout_id = ui.create_layout(hwnd, content_id, 0, 8, 28, 326, 620, 54)
    ui.set_panel_style(hwnd, layout_id, 0x1016A34A, 0x4416A34A, 1.0, 10.0, 8)
    ui.set_layout_options(hwnd, layout_id, orientation=0, gap=8, stretch=False, align=1, wrap=False)
    ui.create_button(hwnd, layout_id, "", "左侧按钮", 0, 0, 100, 36)
    g_space_id = ui.create_space(hwnd, layout_id, 0, 0, 24, 36)
    ui.create_button(hwnd, layout_id, "", "右侧按钮", 0, 0, 100, 36)

    ui.create_text(hwnd, content_id, "Space 是不可见占位，但会参与 Layout 排布。", 28, 396, 420, 28)
    g_update_id = ui.create_button(hwnd, content_id, "🔁", "切换状态", 670, 438, 150, 42)

    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_info_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("基础工具组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("基础工具组件示例结束。")


if __name__ == "__main__":
    main()
