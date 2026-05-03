import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dialog_id = 0
g_drawer_id = 0
g_open_dialog_id = 0
g_open_drawer_id = 0
g_popconfirm_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 覆盖层组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[Resize] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_open_dialog_id:
        ui.dll.EU_SetDialogOpen(g_hwnd, g_dialog_id, 1)
        print("[对话框] 打开")
    elif element_id == g_open_drawer_id:
        ui.dll.EU_SetDrawerOpen(g_hwnd, g_drawer_id, 1)
        print("[抽屉] 打开")
    elif element_id == g_popconfirm_id:
        result = ui.dll.EU_GetPopconfirmResult(g_hwnd, g_popconfirm_id)
        label = {1: "确认", 0: "取消", -1: "未选择"}.get(result, str(result))
        print(f"[气泡确认框] 结果={label}")


def main():
    global g_hwnd, g_dialog_id, g_drawer_id
    global g_open_dialog_id, g_open_drawer_id, g_popconfirm_id

    hwnd = ui.create_window("覆盖层组件示例", 260, 100, 980, 580)
    if not hwnd:
        print("错误：创建窗口失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 530)

    ui.create_text(hwnd, content_id, "覆盖层组件", 28, 24, 360, 28)

    ui.create_text(hwnd, content_id, "悬停或点击触发器", 28, 68, 260, 24)
    tooltip_id = ui.create_tooltip(
        hwnd, content_id,
        "上方提示",
        "提示内容",
        2,
        28, 108, 160, 38
    )
    tooltip_right_id = ui.create_tooltip(
        hwnd, content_id,
        "右侧提示",
        "右侧提示内容",
        1,
        220, 108, 160, 38
    )
    popover_id = ui.create_popover(
        hwnd, content_id,
        "打开气泡卡片",
        "气泡卡片标题",
        "气泡卡片支持标题、正文、关闭按钮，以及点击外部关闭。",
        3,
        28, 178, 170, 38
    )
    g_popconfirm_id = ui.create_popconfirm(
        hwnd, content_id,
        "删除一行",
        "确认操作",
        "点击确认或取消后会自动关闭。",
        "确认",
        "取消",
        3,
        220, 178, 160, 38
    )
    ui.dll.EU_SetElementClickCallback(hwnd, g_popconfirm_id, on_click)

    ui.create_text(hwnd, content_id, "模态层", 430, 68, 220, 24)
    g_open_dialog_id = ui.create_button(
        hwnd, content_id,
        "",
        "打开对话框",
        430, 108, 180, 42
    )
    g_open_drawer_id = ui.create_button(
        hwnd, content_id,
        "",
        "打开抽屉",
        430, 166, 180, 42
    )
    ui.dll.EU_SetElementClickCallback(hwnd, g_open_dialog_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_open_drawer_id, on_click)

    ui.create_alert(
        hwnd, content_id,
        "覆盖层行为",
        "对话框和抽屉挂载为顶层覆盖层。提示、气泡卡片和气泡确认框会在覆盖层阶段绘制弹出内容。",
        0, 0, False,
        28, 280, 620, 62
    )

    g_dialog_id = ui.create_dialog(
        hwnd,
        "Element 对话框",
        "这个对话框是顶层覆盖层，会适配当前客户区。按 Esc 或点击 x 可以关闭。",
        True,
        True,
        460,
        250
    )
    ui.dll.EU_SetDialogOpen(hwnd, g_dialog_id, 0)

    g_drawer_id = ui.create_drawer(
        hwnd,
        "Element 抽屉",
        "抽屉可以从 Python 打开，也可以点击 x 关闭。位置可通过 EU_SetDrawerPlacement 调整。",
        1,
        True,
        True,
        310
    )
    ui.dll.EU_SetDrawerOpen(hwnd, g_drawer_id, 0)

    # 保持回调注册，便于测试点击和悬停路径。
    for eid in (tooltip_id, tooltip_right_id, popover_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("覆盖层组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("覆盖层组件示例结束。")


if __name__ == "__main__":
    main()
