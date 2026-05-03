import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_result_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 结果页完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_result_action(element_id, action_index, action_count, source):
    g_events.append((action_index, action_count, source))
    print(f"[结果操作回调] 元素={element_id} 操作={action_index} 总数={action_count} 来源={source}")


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
    global g_hwnd, g_result_id

    hwnd = ui.create_window("🎉 结果页完整组件验证", 220, 80, 960, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 600)

    ui.create_text(hwnd, content_id, "🎉 Result 结果页完整封装", 30, 24, 620, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证类型图标、自定义内容、操作区鼠标/键盘/程序触发、操作回调、文本读回和完整状态读回。",
        30, 70, 840, 52,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_result_id = ui.create_result(
        hwnd,
        content_id,
        title="✅ 提交成功",
        subtitle="订单已进入处理队列，稍后会同步到工作台。",
        result_type=1,
        x=70,
        y=132,
        w=760,
        h=320,
    )
    ui.set_result_actions(hwnd, g_result_id, ["查看详情 👀", "继续提交 🚀", "返回首页 🏠"])
    ui.set_result_extra_content(
        hwnd,
        g_result_id,
        "📌 自定义内容：编号 A-2026-0503，负责人 小易，当前状态 已归档。",
    )
    ui.set_result_action_callback(hwnd, g_result_id, on_result_action)

    ui.create_text(hwnd, content_id, "⌨️ 键盘：方向键切换操作，Enter/Space 触发；下方测试会自动演示一次。", 84, 472, 700, 32)
    ui.create_button(hwnd, content_id, "🔁", "程序触发第二项", 84, 520, 170, 42)
    ui.create_button(hwnd, content_id, "🎨", "主题与 DPI 自适应", 278, 520, 190, 42)

    title = ui.get_result_text(hwnd, g_result_id, 0)
    subtitle = ui.get_result_text(hwnd, g_result_id, 1)
    extra = ui.get_result_text(hwnd, g_result_id, 2)
    action0 = ui.get_result_action_text(hwnd, g_result_id, 0)
    print("[文本读回]", title, subtitle, extra, action0)
    if "提交成功" not in title or "工作台" not in subtitle or "自定义内容" not in extra:
        raise RuntimeError("结果页文本读回失败")
    if "查看详情" not in action0:
        raise RuntimeError("结果页操作文本读回失败")

    state = ui.get_result_full_state(hwnd, g_result_id)
    print("[初始完整状态]", state)
    if not state or state["result_type"] != 1 or state["action_count"] != 3 or state["has_extra_content"] != 1:
        raise RuntimeError("结果页初始完整状态读回失败")

    ui.set_result_type(hwnd, g_result_id, 2)
    ui.set_result_subtitle(hwnd, g_result_id, "⚠️ 类型已切换为提醒状态，完整状态仍可读回。")
    updated = ui.get_result_full_state(hwnd, g_result_id)
    print("[设置后状态]", updated)
    if updated["result_type"] != 2 or updated["last_action_source"] != 1:
        raise RuntimeError("结果页类型/设置动作状态失败")

    ui.trigger_result_action(hwnd, g_result_id, 1)
    triggered = ui.get_result_full_state(hwnd, g_result_id)
    print("[程序触发]", triggered)
    if triggered["last_action"] != 1 or triggered["action_click_count"] != 1 or triggered["last_action_source"] != 4:
        raise RuntimeError("结果页程序触发失败")
    if not g_events or g_events[-1] != (1, 3, 4):
        raise RuntimeError("结果页程序触发回调失败")

    ui.dll.EU_SetElementFocus(hwnd, g_result_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)  # VK_RIGHT
    user32.PostMessageW(hwnd, 0x0100, 0x0D, 0)  # VK_RETURN
    pump_messages(user32, msg, 0.35)
    keyed = ui.get_result_full_state(hwnd, g_result_id)
    print("[键盘触发]", keyed)
    if keyed["action_click_count"] < 2 or keyed["last_action_source"] != 3:
        raise RuntimeError("结果页键盘触发失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、操作区与首次尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
