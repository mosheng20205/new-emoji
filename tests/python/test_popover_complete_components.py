import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 弹出框完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_popover_action(element_id, open_value, close_count, action):
    g_events.append((open_value, close_count, action))
    print(f"[弹出框动作回调] 元素={element_id} 打开={open_value} 关闭次数={close_count} 动作={action}")


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
    hwnd = ui.create_window("🪟 弹出框完整组件验证", 220, 80, 960, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 600)
    ui.create_text(hwnd, content_id, "🪟 Popover 弹出框完整封装", 30, 24, 640, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证标题/正文、定位尺寸、焦点管理、Tab 切换关闭按钮、Enter 触发、动作回调和完整状态读回。",
        30,
        72,
        840,
        56,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    popover_id = ui.create_popover(
        hwnd,
        content_id,
        label="查看详情 📝",
        title="📝 审核信息",
        content="这里是弹出框正文，包含中文说明、emoji 和可关闭按钮。",
        placement=3,
        x=86,
        y=180,
        w=160,
        h=42,
    )
    ui.set_popover_options(hwnd, popover_id, placement=3, open=False,
                           popup_width=320, popup_height=158, closable=True)
    ui.set_popover_advanced_options(
        hwnd,
        popover_id,
        placement="bottom-start",
        open=False,
        popup_width=320,
        popup_height=158,
        closable=True,
    )
    ui.set_popover_behavior(
        hwnd,
        popover_id,
        trigger_mode="click",
        close_on_outside=True,
        show_arrow=True,
        offset=10,
    )
    ui.set_popover_action_callback(hwnd, popover_id, on_popover_action)

    slot_parent = ui.get_popover_content_parent(hwnd, popover_id)
    if slot_parent <= 0:
        raise RuntimeError("Popover slot 容器 ID 读取失败")
    ui.create_table(
        hwnd,
        slot_parent,
        ["日期", "姓名", "地址"],
        [
            ["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"],
            ["2016-05-04", "王小虎", "上海市普陀区金沙江路 1518 弄"],
        ],
        True,
        True,
        0,
        0,
        292,
        92,
    )
    behavior = ui.get_popover_behavior(hwnd, popover_id)
    if (
        not behavior
        or behavior["trigger_mode"] != ui.TRIGGER_MODES["click"]
        or not behavior["close_on_outside"]
        or not behavior["show_arrow"]
        or behavior["offset"] != 10
    ):
        raise RuntimeError("Popover 行为选项读回失败")

    if "查看详情" not in ui.get_popover_text(hwnd, popover_id, 0):
        raise RuntimeError("弹出框触发标签读回失败")
    if "审核信息" not in ui.get_popover_text(hwnd, popover_id, 1):
        raise RuntimeError("弹出框标题读回失败")
    if "弹出框正文" not in ui.get_popover_text(hwnd, popover_id, 2):
        raise RuntimeError("弹出框正文读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()

    ui.trigger_popover(hwnd, popover_id, True)
    pump_messages(user32, msg, 0.15)
    opened = ui.get_popover_full_state(hwnd, popover_id)
    print("[手动打开状态]", opened)
    if not opened or not opened["open"] or opened["last_action"] != 5:
        raise RuntimeError("弹出框手动打开失败")
    if opened["popup_width"] != 320 or opened["popup_height"] != 158 or not opened["closable"]:
        raise RuntimeError("弹出框尺寸/可关闭状态读回失败")
    if not g_events or g_events[-1] != (1, 0, 5):
        raise RuntimeError("弹出框打开回调失败")

    ui.dll.EU_SetElementFocus(hwnd, popover_id)
    user32.PostMessageW(hwnd, 0x0100, 0x09, 0)  # VK_TAB，焦点到关闭按钮
    pump_messages(user32, msg, 0.12)
    focused = ui.get_popover_full_state(hwnd, popover_id)
    print("[焦点切换状态]", focused)
    if focused["focus_part"] != 2:
        raise RuntimeError("弹出框 Tab 焦点切换失败")

    user32.PostMessageW(hwnd, 0x0100, 0x0D, 0)  # VK_RETURN，关闭按钮
    pump_messages(user32, msg, 0.12)
    key_closed = ui.get_popover_full_state(hwnd, popover_id)
    print("[键盘关闭状态]", key_closed)
    if key_closed["open"] or key_closed["close_count"] < 1 or key_closed["last_action"] != 3:
        raise RuntimeError("弹出框键盘关闭失败")

    ui.set_popover_options(hwnd, popover_id, placement=1, open=True,
                           popup_width=300, popup_height=150, closable=True)
    updated = ui.get_popover_full_state(hwnd, popover_id)
    print("[重新打开状态]", updated)
    if updated["placement"] != 1 or not updated["open"]:
        raise RuntimeError("弹出框重新打开或位置读回失败")

    hover_id = ui.create_popover(
        hwnd,
        content_id,
        label="悬停激活 🖱",
        title="🖱 悬停提示",
        content="悬停触发弹出框，带箭头。",
        placement=2,
        x=330,
        y=180,
        w=160,
        h=42,
    )
    ui.set_popover_advanced_options(hwnd, hover_id, placement="top", popup_width=260, popup_height=132)
    ui.set_popover_behavior(hwnd, hover_id, trigger_mode="hover", close_on_outside=True, show_arrow=True)

    focus_id = ui.create_popover(
        hwnd,
        content_id,
        label="聚焦激活 ⌨",
        title="⌨ 聚焦说明",
        content="焦点进入时打开，失焦时关闭。",
        placement=2,
        x=514,
        y=180,
        w=160,
        h=42,
    )
    ui.set_popover_advanced_options(hwnd, focus_id, placement="right", popup_width=260, popup_height=132)
    ui.set_popover_behavior(hwnd, focus_id, trigger_mode="focus", close_on_outside=True, show_arrow=True)

    manual_id = ui.create_popover(
        hwnd,
        content_id,
        label="手动激活 🧭",
        title="🧭 手动说明",
        content="程序触发打开和关闭。",
        placement=3,
        x=698,
        y=180,
        w=160,
        h=42,
    )
    ui.set_popover_advanced_options(hwnd, manual_id, placement="bottom-end", popup_width=260, popup_height=132)
    ui.set_popover_behavior(hwnd, manual_id, trigger_mode="manual", close_on_outside=False, show_arrow=True)
    manual_behavior = ui.get_popover_behavior(hwnd, manual_id)
    if (
        not manual_behavior
        or manual_behavior["trigger_mode"] != ui.TRIGGER_MODES["manual"]
        or manual_behavior["close_on_outside"]
    ):
        raise RuntimeError("Popover manual 行为读回失败")
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、焦点轮换和首屏尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
