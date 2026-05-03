import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_steps_id = 0
g_vertical_id = 0
g_next_id = 0
g_fail_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 步骤条完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_steps_change(element_id, value, count, action):
    g_events.append((value, count, action))
    print(f"[步骤条变化回调] 元素={element_id} 激活={value} 总数={count} 动作={action}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_next_id:
        state = ui.get_steps_full_state(g_hwnd, g_steps_id)
        ui.trigger_steps_click(g_hwnd, g_steps_id, state["active_index"] + 1)
        print("[按钮] 下一步：", ui.get_steps_full_state(g_hwnd, g_steps_id))
    elif element_id == g_fail_id:
        ui.set_steps_statuses(g_hwnd, g_steps_id, [2, 3, 1, 0])
        print("[按钮] 设置失败状态：", ui.get_steps_full_state(g_hwnd, g_steps_id))


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
    global g_hwnd, g_steps_id, g_vertical_id, g_next_id, g_fail_id

    hwnd = ui.create_window("🪜 步骤条完整组件验证", 220, 80, 980, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 600)

    ui.create_text(hwnd, content_id, "🪜 Steps 步骤条完整封装", 28, 24, 560, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证完成/进行中/等待/失败状态、横向/纵向方向、点击和键盘切换、程序触发、文本读回和完整状态读回。",
        28, 72, 860, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_steps_id = ui.create_steps(
        hwnd,
        content_id,
        ["📝 填写", "🔍 审核", "🚀 发布", "📊 复盘"],
        1,
        46,
        150,
        760,
        112,
    )
    ui.set_steps_detail_items(
        hwnd,
        g_steps_id,
        [
            ("📝 填写资料", "准备中文表单"),
            ("🔍 审核内容", "校验权限与状态"),
            ("🚀 发布上线", "推送到用户侧"),
            ("📊 数据复盘", "查看反馈结果"),
        ],
    )
    ui.set_steps_statuses(hwnd, g_steps_id, [2, 1, 0, 0])
    ui.set_steps_change_callback(hwnd, g_steps_id, on_steps_change)

    g_vertical_id = ui.create_steps(
        hwnd,
        content_id,
        ["📥 收集", "🧭 分派", "✅ 完成"],
        1,
        650,
        300,
        220,
        210,
    )
    ui.set_steps_detail_items(
        hwnd,
        g_vertical_id,
        [("📥 收集", "接收请求"), ("🧭 分派", "处理中"), ("✅ 完成", "返回结果")],
    )
    ui.set_steps_direction(hwnd, g_vertical_id, 1)
    ui.set_steps_statuses(hwnd, g_vertical_id, [2, 1, 0])

    g_next_id = ui.create_button(hwnd, content_id, "➡️", "触发下一步", 46, 340, 150, 42)
    g_fail_id = ui.create_button(hwnd, content_id, "⚠️", "设置失败态", 220, 340, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_next_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_fail_id, on_click)

    initial = ui.get_steps_full_state(hwnd, g_steps_id)
    print("[初始状态]", initial)
    if not initial or initial["active_index"] != 1 or initial["item_count"] != 4:
        raise RuntimeError("步骤条初始状态读回失败")
    if "审核" not in ui.get_steps_item(hwnd, g_steps_id, 1, 0):
        raise RuntimeError("步骤条标题读回失败")
    if "校验" not in ui.get_steps_item(hwnd, g_steps_id, 1, 1):
        raise RuntimeError("步骤条描述读回失败")

    ui.trigger_steps_click(hwnd, g_steps_id, 2)
    triggered = ui.get_steps_full_state(hwnd, g_steps_id)
    print("[程序触发]", triggered)
    if triggered["active_index"] != 2 or triggered["last_action"] != 4 or triggered["click_count"] < 1:
        raise RuntimeError("步骤条程序触发失败")
    if not g_events or g_events[-1][0] != 2:
        raise RuntimeError("步骤条变化回调失败")

    ui.set_steps_statuses(hwnd, g_steps_id, [2, 3, 1, 0])
    failed = ui.get_steps_full_state(hwnd, g_steps_id)
    print("[失败状态]", failed)
    if failed["failed_count"] != 1:
        raise RuntimeError("步骤条失败状态读回失败")

    ui.dll.EU_SetElementFocus(hwnd, g_steps_id)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)
    pump_messages(user32, msg, 0.25)
    key_state = ui.get_steps_full_state(hwnd, g_steps_id)
    print("[键盘右移]", key_state)
    if key_state["active_index"] != 3 or key_state["last_action"] != 3:
        raise RuntimeError("步骤条键盘导航失败")

    vertical = ui.get_steps_full_state(hwnd, g_vertical_id)
    if vertical["direction"] != 1 or vertical["item_count"] != 3:
        raise RuntimeError("步骤条纵向状态读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("步骤条完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    auto_clicked = False
    while running and time.time() - start < 60:
        if not auto_clicked and time.time() - start > 1.0:
            on_click(g_fail_id)
            auto_clicked = True
        running = pump_messages(user32, msg, 0.05)

    print("步骤条完整组件示例结束。")


if __name__ == "__main__":
    main()
