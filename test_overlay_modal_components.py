import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dialog_id = 0
g_drawer_id = 0
g_toggle_id = 0
g_alt = False


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 模态浮层示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_alt
    if element_id == g_toggle_id:
        g_alt = not g_alt
        ui.set_dialog_title(g_hwnd, g_dialog_id, "🧩 可拖拽对话框" if g_alt else "💬 运行时对话框")
        ui.set_dialog_body(
            g_hwnd,
            g_dialog_id,
            "标题栏可以拖拽，点击遮罩可以关闭。尺寸、模态、关闭按钮都由 options API 控制。"
        )
        ui.set_dialog_options(
            g_hwnd, g_dialog_id,
            open=True, modal=True, closable=True,
            close_on_mask=True, draggable=True,
            w=520 if g_alt else 460,
            h=280 if g_alt else 240,
        )
        expected_dialog = (
            True, True, True, True, True,
            520 if g_alt else 460,
            280 if g_alt else 240,
        )
        assert ui.get_dialog_options(g_hwnd, g_dialog_id) == expected_dialog

        ui.set_drawer_title(g_hwnd, g_drawer_id, "📚 底部抽屉" if g_alt else "📂 右侧抽屉")
        ui.set_drawer_body(
            g_hwnd,
            g_drawer_id,
            "Drawer 支持运行时切换位置、尺寸和遮罩关闭。当前示例会在右侧和底部之间切换。"
        )
        ui.set_drawer_options(
            g_hwnd, g_drawer_id,
            placement=3 if g_alt else 1,
            open=True, modal=True, closable=True,
            close_on_mask=True,
            size=230 if g_alt else 320,
        )
        expected_drawer = (3 if g_alt else 1, True, True, True, True, 230 if g_alt else 320)
        assert ui.get_drawer_options(g_hwnd, g_drawer_id) == expected_drawer

        print(
            f"[更新] dialog={ui.get_dialog_options(g_hwnd, g_dialog_id)}, "
            f"drawer={ui.get_drawer_options(g_hwnd, g_drawer_id)}"
        )


def main():
    global g_hwnd, g_dialog_id, g_drawer_id, g_toggle_id

    hwnd = ui.create_window("🧱 模态浮层组件示例", 220, 80, 920, 640)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 590)

    ui.create_text(hwnd, content_id, "🧱 Dialog / Drawer", 28, 24, 420, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐对话框和抽屉的运行时控制：打开状态、尺寸、遮罩关闭、关闭按钮、抽屉方向，以及对话框标题栏拖拽。",
        28, 68, 720, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_toggle_id = ui.create_button(hwnd, content_id, "🚀", "打开并切换浮层", 28, 154, 190, 44)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "操作提示",
        "示例会在 1 秒后自动打开 Dialog 和 Drawer。你可以拖拽 Dialog 标题栏，也可以点击遮罩关闭。",
        28, 230, 620, 90,
    )

    g_dialog_id = ui.create_dialog(
        hwnd,
        "💬 运行时对话框",
        "初始内容会被自动更新。",
        modal=True,
        closable=True,
        w=460,
        h=240,
    )
    ui.set_dialog_options(
        hwnd, g_dialog_id,
        open=False, modal=True, closable=True,
        close_on_mask=True, draggable=True,
        w=460, h=240,
    )
    assert ui.get_dialog_options(hwnd, g_dialog_id) == (False, True, True, True, True, 460, 240)

    g_drawer_id = ui.create_drawer(
        hwnd,
        "📂 右侧抽屉",
        "初始内容会被自动更新。",
        placement=1,
        modal=True,
        closable=True,
        size=320,
    )
    ui.set_drawer_options(
        hwnd, g_drawer_id,
        placement=1, open=False,
        modal=True, closable=True,
        close_on_mask=True,
        size=320,
    )
    assert ui.get_drawer_options(hwnd, g_drawer_id) == (1, False, True, True, True, 320)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[模态浮层读回] "
        f"Dialog={ui.get_dialog_options(hwnd, g_dialog_id)} "
        f"Drawer={ui.get_drawer_options(hwnd, g_drawer_id)}"
    )
    print("模态浮层示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_done = False
    while running and time.time() - start < 60:
        if not auto_done and time.time() - start > 1.0:
            on_click(g_toggle_id)
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

    print("模态浮层示例结束。")


if __name__ == "__main__":
    main()
