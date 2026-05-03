import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dialog_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 对话框完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_dialog_button(element_id, button_index, button_count, action):
    g_events.append((button_index, button_count, action))
    print(f"[对话框按钮回调] 元素={element_id} 按钮={button_index} 总数={button_count} 动作={action}")


def pump_messages(user32, msg, duration):
    start = time.time()
    running = True
    while running and time.time() - start < duration:
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
    return running


def main():
    global g_hwnd, g_dialog_id

    hwnd = ui.create_window("💬 对话框完整组件验证", 220, 80, 980, 700)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 640)
    ui.create_text(hwnd, content_id, "💬 Dialog 对话框完整封装", 32, 28, 680, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证按钮区、焦点循环、键盘触发、程序触发、按钮回调、文本读回和完整状态读回。",
        32,
        78,
        840,
        56,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)
    ui.create_button(hwnd, content_id, "📌", "背景按钮：对话框覆盖其上", 64, 166, 260, 44)

    g_dialog_id = ui.create_dialog(
        hwnd,
        title="🚀 发布确认",
        body="请确认是否发布当前中文 emoji 组件封装结果。按钮区支持 Tab/方向键循环，Enter/Space 触发。",
        modal=True,
        closable=True,
        w=560,
        h=310,
    )
    ui.set_dialog_options(hwnd, g_dialog_id, open=True, modal=True, closable=True,
                          close_on_mask=True, draggable=True, w=560, h=310)
    ui.set_dialog_buttons(hwnd, g_dialog_id, ["确认发布 ✅", "稍后处理 ⏳", "取消 ❌"])
    ui.set_dialog_button_callback(hwnd, g_dialog_id, on_dialog_button)

    if "发布确认" not in ui.get_dialog_text(hwnd, g_dialog_id, 0):
        raise RuntimeError("对话框标题读回失败")
    if "组件封装结果" not in ui.get_dialog_text(hwnd, g_dialog_id, 1):
        raise RuntimeError("对话框正文读回失败")
    if "确认发布" not in ui.get_dialog_button_text(hwnd, g_dialog_id, 0):
        raise RuntimeError("对话框按钮文本读回失败")

    initial = ui.get_dialog_full_state(hwnd, g_dialog_id)
    print("[初始完整状态]", initial)
    if not initial or initial["open"] != 1 or initial["button_count"] != 3 or initial["close_on_mask"] != 1:
        raise RuntimeError("对话框初始完整状态失败")

    ui.trigger_dialog_button(hwnd, g_dialog_id, 1)
    program_state = ui.get_dialog_full_state(hwnd, g_dialog_id)
    print("[程序触发按钮]", program_state)
    if program_state["open"] != 0 or program_state["last_button"] != 1 or program_state["last_action"] != 4:
        raise RuntimeError("对话框程序按钮触发失败")
    if not g_events or g_events[-1] != (1, 3, 4):
        raise RuntimeError("对话框程序按钮回调失败")

    ui.set_dialog_options(hwnd, g_dialog_id, open=True, modal=True, closable=True,
                          close_on_mask=True, draggable=True, w=560, h=310)
    ui.dll.EU_SetElementFocus(hwnd, g_dialog_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x09, 0)  # VK_TAB
    user32.PostMessageW(hwnd, 0x0100, 0x0D, 0)  # VK_RETURN
    pump_messages(user32, msg, 0.35)
    keyed = ui.get_dialog_full_state(hwnd, g_dialog_id)
    print("[键盘触发按钮]", keyed)
    if keyed["open"] != 0 or keyed["button_click_count"] < 2 or keyed["last_action"] != 3:
        raise RuntimeError("对话框键盘焦点/按钮触发失败")

    ui.set_dialog_options(hwnd, g_dialog_id, open=True, modal=True, closable=True,
                          close_on_mask=True, draggable=True, w=580, h=320)
    reopened = ui.get_dialog_full_state(hwnd, g_dialog_id)
    if reopened["open"] != 1 or reopened["width"] != 580 or reopened["height"] != 320:
        raise RuntimeError("对话框重新打开或尺寸读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、按钮区、焦点循环与首屏尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
