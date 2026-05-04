import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dialog_id = 0
g_events = []
g_before_close_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 对话框完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_dialog_button(element_id, button_index, button_count, action):
    g_events.append((button_index, button_count, action))
    print(f"[对话框按钮回调] 元素={element_id} 按钮={button_index} 总数={button_count} 动作={action}")


@ui.BeforeCloseCallback
def on_before_close(element_id, action):
    g_before_close_events.append((element_id, action))
    print(f"[Dialog before-close] 元素={element_id} 动作={action}，先拦截等待确认")
    return 0


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


def make_lparam(x, y):
    return ((y & 0xFFFF) << 16) | (x & 0xFFFF)


def click_at(user32, hwnd, x, y):
    user32.SendMessageW(hwnd, 0x0201, 0x0001, make_lparam(x, y))  # WM_LBUTTONDOWN
    user32.SendMessageW(hwnd, 0x0202, 0, make_lparam(x, y))       # WM_LBUTTONUP


def click_centered_dialog_button(user32, hwnd, dialog_w, dialog_h, button_count, button_index):
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    dpi = user32.GetDpiForWindow(hwnd) if hasattr(user32, "GetDpiForWindow") else 96
    dpi_scale = dpi / 96.0 if dpi else 1.0
    client_w = rect.right - rect.left
    client_h = rect.bottom - rect.top
    dw = round(dialog_w)
    dh = round(dialog_h)
    bw = round(92)
    bh = round(34)
    gap = round(10)
    pad = round(18)
    total_w = button_count * bw + (button_count - 1) * gap
    dialog_x = max(0, (client_w - dw) // 2)
    dialog_y = max(0, (client_h - dh) // 2)
    x = round((dialog_x + (dw - total_w) // 2 + button_index * (bw + gap) + bw // 2) * dpi_scale)
    y = round((dialog_y + dh - pad - bh + bh // 2) * dpi_scale)
    click_at(user32, hwnd, x, y)


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

    content_parent = ui.get_dialog_content_parent(hwnd, g_dialog_id)
    footer_parent = ui.get_dialog_footer_parent(hwnd, g_dialog_id)
    if content_parent <= 0 or footer_parent <= 0:
        raise RuntimeError("Dialog slot 容器 ID 读取失败")
    ui.set_dialog_advanced_options(
        hwnd,
        g_dialog_id,
        width_mode=1,
        width_value=55,
        center=True,
        footer_center=True,
        content_padding=22,
        footer_height=62,
    )
    ui.create_table(
        hwnd,
        content_parent,
        ["日期", "姓名", "地址"],
        [
            ["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"],
            ["2016-05-04", "王小虎", "上海市普陀区金沙江路 1518 弄"],
        ],
        True,
        True,
        0,
        0,
        500,
        116,
    )
    ui.create_button(hwnd, footer_parent, "✅", "slot 确定", 316, 12, 118, 36)
    advanced = ui.get_dialog_advanced_options(hwnd, g_dialog_id)
    if (
        not advanced
        or advanced["width_mode"] != 1
        or advanced["width_value"] != 55
        or not advanced["center"]
        or not advanced["footer_center"]
        or advanced["content_parent_id"] != content_parent
        or advanced["footer_parent_id"] != footer_parent
    ):
        raise RuntimeError("Dialog 高级布局或 slot 状态读回失败")

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

    mouse_dialog_id = ui.create_dialog(
        hwnd,
        title="🖱️ 居中页脚点击",
        body="页脚按钮居中时，鼠标命中区域必须和绘制区域一致。",
        modal=True,
        closable=True,
        w=460,
        h=250,
    )
    ui.set_dialog_buttons(hwnd, mouse_dialog_id, ["确认 ✅", "取消 ❌"])
    ui.set_dialog_button_callback(hwnd, mouse_dialog_id, on_dialog_button)
    ui.set_dialog_advanced_options(
        hwnd,
        mouse_dialog_id,
        width_mode=0,
        width_value=460,
        center=True,
        footer_center=True,
        content_padding=22,
        footer_height=62,
    )
    ui.set_dialog_options(hwnd, mouse_dialog_id, open=True, modal=True, closable=True,
                          close_on_mask=True, draggable=True, w=460, h=250)
    click_centered_dialog_button(user32, hwnd, 460, 250, 2, 0)
    pump_messages(user32, msg, 0.12)
    mouse_state = ui.get_dialog_full_state(hwnd, mouse_dialog_id)
    print("[鼠标点击居中页脚按钮]", mouse_state)
    if mouse_state["open"] != 0 or mouse_state["last_button"] != 0 or mouse_state["last_action"] != 2:
        raise RuntimeError("Dialog 居中页脚按钮鼠标命中失败")
    if not g_events or g_events[-1] != (0, 2, 2):
        raise RuntimeError("Dialog 居中页脚按钮鼠标回调失败")

    ui.set_dialog_options(hwnd, g_dialog_id, open=True, modal=True, closable=True,
                          close_on_mask=True, draggable=True, w=580, h=320)
    reopened = ui.get_dialog_full_state(hwnd, g_dialog_id)
    if reopened["open"] != 1 or reopened["width"] != 580 or reopened["height"] != 320:
        raise RuntimeError("对话框重新打开或尺寸读回失败")

    ui.set_dialog_before_close_callback(hwnd, g_dialog_id, on_before_close)
    ui.trigger_dialog_button(hwnd, g_dialog_id, 0)
    blocked = ui.get_dialog_advanced_options(hwnd, g_dialog_id)
    blocked_full = ui.get_dialog_full_state(hwnd, g_dialog_id)
    print("[before-close 拦截状态]", blocked, blocked_full)
    if not blocked or not blocked["close_pending"] or not blocked_full["open"]:
        raise RuntimeError("Dialog before-close 拦截失败")
    if not g_before_close_events:
        raise RuntimeError("Dialog before-close 回调未触发")
    ui.confirm_dialog_close(hwnd, g_dialog_id, True)
    confirmed_close = ui.get_dialog_full_state(hwnd, g_dialog_id)
    if confirmed_close["open"] != 0:
        raise RuntimeError("Dialog before-close 确认关闭失败")
    ui.set_dialog_options(hwnd, g_dialog_id, open=True, modal=True, closable=True,
                          close_on_mask=True, draggable=True, w=580, h=320)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、按钮区、焦点循环与首屏尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
