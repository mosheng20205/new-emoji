import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_loading_id = 0
g_toggle_id = 0
g_result_id = 0
g_alert_error_id = 0
g_notify_id = 0
g_reset_id = 0
g_loading_active = True


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 反馈组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[Resize] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    global g_loading_active

    if element_id == g_toggle_id:
        g_loading_active = not g_loading_active
        progress = 72 if g_loading_active else 100
        ui.set_loading_options(g_hwnd, g_loading_id, g_loading_active, False, progress)
        label = "🔄 正在同步" if g_loading_active else "✅ 同步完成"
        text = ui.make_utf8(label)
        ui.dll.EU_SetElementText(g_hwnd, g_loading_id, ui.bytes_arg(text), len(text))
        print(f"[加载] options={ui.get_loading_options(g_hwnd, g_loading_id)}")
    elif element_id == g_reset_id:
        ui.dll.EU_SetAlertClosed(g_hwnd, g_alert_error_id, 0)
        ui.dll.EU_SetNotificationClosed(g_hwnd, g_notify_id, 0)
        ui.dll.EU_SetNotificationOptions(g_hwnd, g_notify_id, 1, 1, 4000)
        ui.dll.EU_SetResultType(g_hwnd, g_result_id, 1)
        ui.set_result_actions(g_hwnd, g_result_id, ["查看详情", "继续操作"])
        print(
            "[重置]",
            ui.get_alert_options(g_hwnd, g_alert_error_id),
            ui.get_notification_options(g_hwnd, g_notify_id),
            ui.get_result_options(g_hwnd, g_result_id),
        )
    elif element_id == g_result_id:
        print("[结果] 操作索引:", ui.dll.EU_GetResultAction(g_hwnd, g_result_id))
    elif element_id == g_alert_error_id:
        print("[警告] 关闭状态:", ui.dll.EU_GetAlertClosed(g_hwnd, g_alert_error_id))
    elif element_id == g_notify_id:
        print("[通知] 关闭状态:", ui.dll.EU_GetNotificationClosed(g_hwnd, g_notify_id))
    else:
        print(f"[反馈] 点击元素 #{element_id}")


def main():
    global g_hwnd, g_loading_id, g_toggle_id, g_result_id, g_alert_error_id, g_notify_id, g_reset_id

    hwnd = ui.create_window("💬 反馈组件示例", 240, 80, 820, 780)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 800, 730)

    ui.create_text(hwnd, content_id, "💬 反馈组件", 28, 24, 360, 28)

    alert_info = ui.create_alert(
        hwnd, content_id,
        "ℹ️ 信息提示",
        "浅色提示可以包含辅助说明文字。",
        0, 0, True,
        28, 66, 520, 54
    )
    assert ui.get_alert_options(hwnd, alert_info) == (0, 0, True, False)
    alert_success = ui.create_alert(
        hwnd, content_id,
        "✅ 成功提示",
        "组件会按类型使用成功色。",
        1, 0, True,
        28, 130, 520, 54
    )
    assert ui.get_alert_options(hwnd, alert_success) == (1, 0, True, False)
    alert_warning = ui.create_alert(
        hwnd, content_id,
        "⚠️ 警告提示",
        "深色效果会使用类型色作为背景。",
        2, 1, False,
        28, 194, 520, 54
    )
    assert ui.get_alert_options(hwnd, alert_warning) == (2, 1, False, False)
    g_alert_error_id = ui.create_alert(
        hwnd, content_id,
        "❌ 错误提示",
        "点击右侧关闭按钮后可读取关闭状态。",
        3, 0, True,
        28, 258, 520, 54
    )
    assert ui.get_alert_options(hwnd, g_alert_error_id) == (3, 0, True, False)

    g_result_id = ui.create_result(
        hwnd, content_id,
        "🎉 操作完成",
        "结果组件现在支持操作按钮和操作索引读取。",
        1,
        28, 336, 320, 190
    )
    ui.set_result_actions(hwnd, g_result_id, ["查看详情", "继续操作"])
    assert ui.get_result_options(hwnd, g_result_id) == (1, 2, -1)

    g_notify_id = ui.create_notification(
        hwnd, content_id,
        "📣 成功通知",
        "通知组件支持关闭状态和持续时间进度条。",
        0, True,
        372, 336, 330, 108
    )
    ui.dll.EU_SetNotificationOptions(hwnd, g_notify_id, 1, 1, 4000)
    assert ui.get_notification_options(hwnd, g_notify_id) == (1, True, 4000, False)
    notify_warning_id = ui.create_notification(
        hwnd, content_id,
        "⚠️ 警告通知",
        "关闭图标和正文会保持在组件边界内。",
        2, True,
        372, 462, 330, 108
    )
    assert ui.get_notification_options(hwnd, notify_warning_id) == (2, True, 0, False)

    g_loading_id = ui.create_loading(
        hwnd, content_id,
        "🔄 正在同步",
        True,
        28, 522, 300, 120
    )
    ui.set_loading_options(hwnd, g_loading_id, True, False, 72)
    assert ui.get_loading_options(hwnd, g_loading_id) == (True, False, 72)
    g_toggle_id = ui.create_button(
        hwnd, content_id,
        "🔄",
        "切换加载",
        372, 590, 180, 42
    )
    g_reset_id = ui.create_button(
        hwnd, content_id,
        "♻",
        "重置反馈状态",
        570, 590, 150, 42
    )
    ui.create_infobox(
        hwnd, content_id,
        "✅ 本批完善",
        "Alert / Result / Notification / Loading 已补关闭状态、操作按钮、持续时间和进度 API。",
        28, 660, 675, 54
    )

    for eid in (
        alert_info, alert_success, alert_warning, g_alert_error_id,
        g_result_id, g_notify_id, notify_warning_id, g_loading_id, g_toggle_id, g_reset_id
    ):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[反馈组件读回] "
        f"Alert={ui.get_alert_options(hwnd, g_alert_error_id)} "
        f"Result={ui.get_result_options(hwnd, g_result_id)} "
        f"Notify={ui.get_notification_options(hwnd, g_notify_id)} "
        f"Loading={ui.get_loading_options(hwnd, g_loading_id)}"
    )
    print("反馈组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("反馈组件示例结束。")


if __name__ == "__main__":
    main()
