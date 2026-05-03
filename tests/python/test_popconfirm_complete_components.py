import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 气泡确认框完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_result(element_id, result, result_count, action):
    g_events.append((result, result_count, action))
    print(f"[气泡确认结果回调] 元素={element_id} 结果={result} 次数={result_count} 动作={action}")


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
    hwnd = ui.create_window("🛡️ 气泡确认框完整组件验证", 220, 80, 980, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 620)
    ui.create_text(hwnd, content_id, "🛡️ Popconfirm 气泡确认框完整封装", 30, 24, 720, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证确认/取消按钮、结果读回/重置、键盘确认取消、程序触发、结果回调和完整状态读回。",
        30,
        72,
        860,
        56,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    confirm_id = ui.create_popconfirm(
        hwnd,
        content_id,
        label="删除任务 🗑️",
        title="🛡️ 删除确认",
        content="确认删除这条中文 emoji 任务吗？操作会记录结果状态。",
        confirm="确认删除 ✅",
        cancel="先保留 ❌",
        placement=3,
        x=86,
        y=184,
        w=170,
        h=42,
    )
    ui.set_popconfirm_options(hwnd, confirm_id, placement=3, open=True,
                              popup_width=330, popup_height=170)
    ui.set_popconfirm_result_callback(hwnd, confirm_id, on_result)

    if "删除任务" not in ui.get_popconfirm_text(hwnd, confirm_id, 0):
        raise RuntimeError("气泡确认框触发标签读回失败")
    if "删除确认" not in ui.get_popconfirm_text(hwnd, confirm_id, 1):
        raise RuntimeError("气泡确认框标题读回失败")
    if "确认删除" not in ui.get_popconfirm_text(hwnd, confirm_id, 3):
        raise RuntimeError("气泡确认框按钮读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.15)
    initial = ui.get_popconfirm_full_state(hwnd, confirm_id)
    print("[初始状态]", initial)
    if not initial or not initial["open"] or initial["popup_width"] != 330 or initial["result"] != -1:
        raise RuntimeError("气泡确认框初始完整状态失败")

    ui.dll.EU_SetElementFocus(hwnd, confirm_id)
    user32.PostMessageW(hwnd, 0x0100, 0x09, 0)  # VK_TAB -> 取消
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)  # VK_RIGHT -> 确认
    user32.PostMessageW(hwnd, 0x0100, 0x0D, 0)  # VK_RETURN
    pump_messages(user32, msg, 0.25)
    key_confirmed = ui.get_popconfirm_full_state(hwnd, confirm_id)
    print("[键盘确认状态]", key_confirmed)
    if key_confirmed["open"] or key_confirmed["result"] != 1:
        raise RuntimeError("气泡确认框键盘确认失败")
    if key_confirmed["confirm_count"] < 1 or key_confirmed["result_action"] != 3:
        raise RuntimeError("气泡确认框键盘确认状态失败")
    if not g_events or g_events[-1] != (1, 1, 3):
        raise RuntimeError("气泡确认框键盘确认回调失败")

    ui.dll.EU_ResetPopconfirmResult(hwnd, confirm_id)
    ui.set_popconfirm_open(hwnd, confirm_id, True)
    ui.trigger_popconfirm_result(hwnd, confirm_id, False)
    program_cancel = ui.get_popconfirm_full_state(hwnd, confirm_id)
    print("[程序取消状态]", program_cancel)
    if program_cancel["open"] or program_cancel["result"] != 0:
        raise RuntimeError("气泡确认框程序取消失败")
    if program_cancel["cancel_count"] < 1 or program_cancel["result_action"] != 4:
        raise RuntimeError("气泡确认框程序取消状态失败")

    ui.set_popconfirm_content(hwnd, confirm_id, "🛡️ 再次确认", "按 Esc 可走取消语义，按钮和状态保持中文。")
    ui.set_popconfirm_buttons(hwnd, confirm_id, "继续 ✅", "取消 ❌")
    ui.set_popconfirm_options(hwnd, confirm_id, placement=1, open=True,
                              popup_width=310, popup_height=160)
    reopened = ui.get_popconfirm_full_state(hwnd, confirm_id)
    print("[重新打开状态]", reopened)
    if reopened["placement"] != 1 or not reopened["open"]:
        raise RuntimeError("气泡确认框重新打开或位置读回失败")

    user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)  # VK_ESCAPE -> 取消
    pump_messages(user32, msg, 0.18)
    esc_cancel = ui.get_popconfirm_full_state(hwnd, confirm_id)
    print("[键盘取消状态]", esc_cancel)
    if esc_cancel["open"] or esc_cancel["result"] != 0 or esc_cancel["result_action"] != 3:
        raise RuntimeError("气泡确认框键盘取消失败")

    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、确认/取消按钮、键盘焦点和首屏尺寸余量。")
    ui.set_popconfirm_open(hwnd, confirm_id, True)
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
