import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_SPACE = 0x20
VK_RIGHT = 0x27

g_hwnd = None
g_checkbox_id = 0
g_radio_a_id = 0
g_radio_b_id = 0
g_switch_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 表单选择完成验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    g_events.append(element_id)
    print("[回调] 元素点击:", element_id)


def pump_messages(seconds=1.0):
    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < seconds:
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


def send_key(hwnd, element_id, vk):
    user32 = ctypes.windll.user32
    ui.dll.EU_SetElementFocus(hwnd, element_id)
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 0)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, 0)
    pump_messages(0.35)


def main():
    global g_hwnd, g_checkbox_id, g_radio_a_id, g_radio_b_id, g_switch_id

    hwnd = ui.create_window("☑️ 表单选择完成验证", 210, 90, 940, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 610)
    ui.set_panel_style(hwnd, content_id, 0x00000000, 0x00000000, 0.0, 0.0, 0)
    ui.set_panel_layout(hwnd, content_id, fill_parent=True, content_layout=False)

    ui.create_text(hwnd, content_id, "☑️ Container / Border / Checkbox / Radio / Switch", 28, 24, 820, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证容器填充、虚线边框、复选半选态、单选分组方向键导航、开关加载/文本状态和键盘点击回调。",
        28, 70, 790, 58,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    border_id = ui.create_border(hwnd, content_id, 28, 150, 402, 250)
    ui.set_panel_style(hwnd, border_id, 0x102563EB, 0xFF2563EB, 2.0, 16.0, 18)
    ui.set_border_options(hwnd, border_id, sides=15, color=0xFF2563EB, width=2.0, radius=16.0, title="🧩 虚线边框")
    ui.set_border_dashed(hwnd, border_id, True)

    g_checkbox_id = ui.create_checkbox(hwnd, border_id, "☑️ 复选：键盘切换", False, 0, 40, 260, 34)
    ui.dll.EU_SetCheckboxIndeterminate(hwnd, g_checkbox_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_checkbox_id, on_click)
    group_id = ui.create_checkbox_group(
        hwnd, border_id,
        [("上海 🏙️", "上海", False), ("北京 🔒", "北京", True), ("深圳 🚀", "深圳", False)],
        ["上海"], style=1, size=2, x=0, y=82, w=300, h=34,
    )

    g_radio_a_id = ui.create_radio(hwnd, border_id, "🍵 方案甲", True, 0, 132, 180, 34)
    g_radio_b_id = ui.create_radio(hwnd, border_id, "🍰 方案乙", False, 0, 176, 180, 34)
    ui.set_radio_group(hwnd, g_radio_a_id, "demo")
    ui.set_radio_group(hwnd, g_radio_b_id, "demo")
    ui.dll.EU_SetElementClickCallback(hwnd, g_radio_a_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_radio_b_id, on_click)

    panel_id = ui.create_panel(hwnd, content_id, 486, 150, 360, 250)
    ui.set_panel_style(hwnd, panel_id, 0x1016A34A, 0x5516A34A, 1.0, 14.0, 20)
    ui.set_panel_layout(hwnd, panel_id, fill_parent=False, content_layout=True)
    ui.create_text(hwnd, panel_id, "🪄 开关完整状态", 0, 0, 240, 34)
    g_switch_id = ui.create_switch(hwnd, panel_id, "⚙️ 自动同步", False, 0, 54, 260, 40)
    ui.set_switch_texts(hwnd, g_switch_id, "已开启 ✅", "已关闭 💤")
    ui.dll.EU_SetElementClickCallback(hwnd, g_switch_id, on_click)
    ui.create_text(hwnd, panel_id, "加载态会阻止切换；测试会先读回文本状态，再键盘切换。", 0, 118, 290, 64)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("表单选择完成验证已显示。窗口会保持 60 秒。")
    print("[读取] Container:", ui.get_panel_layout(hwnd, content_id))
    print("[读取] Border:", ui.get_border_options(hwnd, border_id), "虚线:", ui.get_border_dashed(hwnd, border_id))
    print("[读取] Checkbox 半选:", bool(ui.dll.EU_GetCheckboxIndeterminate(hwnd, g_checkbox_id)))
    print("[读取] CheckboxGroup:", ui.get_checkbox_group_state(hwnd, group_id))
    print("[读取] Radio 分组:", ui.get_radio_group(hwnd, g_radio_a_id))
    print("[读取] Switch:", ui.get_switch_options(hwnd, g_switch_id))

    pump_messages(0.5)
    send_key(hwnd, g_checkbox_id, VK_SPACE)
    send_key(hwnd, g_radio_a_id, VK_RIGHT)
    send_key(hwnd, g_switch_id, VK_SPACE)
    print("[读取] Checkbox:", bool(ui.dll.EU_GetCheckboxChecked(hwnd, g_checkbox_id)),
          "半选:", bool(ui.dll.EU_GetCheckboxIndeterminate(hwnd, g_checkbox_id)))
    print("[读取] Radio:", ui.dll.EU_GetRadioChecked(hwnd, g_radio_a_id), ui.dll.EU_GetRadioChecked(hwnd, g_radio_b_id))
    print("[读取] Switch:", ui.get_switch_options(hwnd, g_switch_id))
    print("[读取] 回调次数:", len(g_events))

    start = time.time()
    while time.time() - start < 58:
        if not pump_messages(0.2):
            break

    print("表单选择完成验证结束。")


if __name__ == "__main__":
    main()
