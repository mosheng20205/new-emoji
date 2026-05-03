import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_checkbox_id = 0
g_radio_a_id = 0
g_radio_b_id = 0
g_switch_id = 0
g_disabled_switch_id = 0
g_toggle_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 表单选择组件验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id != g_toggle_id:
        return
    ui.dll.EU_SetCheckboxIndeterminate(g_hwnd, g_checkbox_id, 0)
    ui.dll.EU_SetCheckboxChecked(g_hwnd, g_checkbox_id, 1)
    ui.dll.EU_SetRadioChecked(g_hwnd, g_radio_b_id, 1)
    ui.dll.EU_SetSwitchChecked(g_hwnd, g_switch_id, 1)
    ui.dll.EU_SetSwitchLoading(g_hwnd, g_disabled_switch_id, 1)
    ui.dll.EU_SetElementEnabled(g_hwnd, g_disabled_switch_id, 0)
    print("[读取] 复选框:", ui.dll.EU_GetCheckboxChecked(g_hwnd, g_checkbox_id),
          "半选:", ui.dll.EU_GetCheckboxIndeterminate(g_hwnd, g_checkbox_id),
          "启用:", ui.get_element_enabled(g_hwnd, g_checkbox_id))
    print("[读取] 单选:", ui.dll.EU_GetRadioChecked(g_hwnd, g_radio_a_id),
          ui.dll.EU_GetRadioChecked(g_hwnd, g_radio_b_id))
    print("[读取] 开关:", ui.dll.EU_GetSwitchChecked(g_hwnd, g_switch_id),
          "禁用开关启用:", ui.get_element_enabled(g_hwnd, g_disabled_switch_id),
          "加载:", ui.dll.EU_GetSwitchLoading(g_hwnd, g_disabled_switch_id))


def main():
    global g_hwnd, g_checkbox_id, g_radio_a_id, g_radio_b_id, g_switch_id, g_disabled_switch_id, g_toggle_id

    hwnd = ui.create_window("✅ 表单选择组件验证", 220, 90, 900, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 570)

    ui.create_text(hwnd, content_id, "✅ Checkbox / Radio / Switch 键盘与禁用态", 28, 24, 720, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "这一批补齐复选框、单选框和开关的 Space/Enter 键盘触发、焦点描边、禁用态视觉和禁用交互拦截，"
        "并用通用元素状态 Get API 读取启用/可见状态。",
        28, 70, 760, 64,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_checkbox_id = ui.create_checkbox(hwnd, content_id, "☑️ 接收更新通知", False, 40, 160, 260, 34)
    ui.dll.EU_SetCheckboxIndeterminate(hwnd, g_checkbox_id, 1)

    g_radio_a_id = ui.create_radio(hwnd, content_id, "🌤️ 白天模式", True, 40, 220, 180, 34)
    g_radio_b_id = ui.create_radio(hwnd, content_id, "🌙 夜间模式", False, 240, 220, 180, 34)
    ui.set_radio_group(hwnd, g_radio_a_id, "theme")
    ui.set_radio_group(hwnd, g_radio_b_id, "theme")

    g_switch_id = ui.create_switch(hwnd, content_id, "🚀 自动同步", False, 40, 284, 260, 36)
    ui.set_switch_texts(hwnd, g_switch_id, "已开启 ✅", "已关闭 ⏸")

    g_disabled_switch_id = ui.create_switch(hwnd, content_id, "🔒 禁用加载态", True, 40, 348, 280, 36)
    ui.set_switch_texts(hwnd, g_disabled_switch_id, "锁定中", "未锁定")
    ui.dll.EU_SetSwitchLoading(hwnd, g_disabled_switch_id, 1)
    ui.dll.EU_SetElementEnabled(hwnd, g_disabled_switch_id, 0)

    panel_id = ui.create_panel(hwnd, content_id, 500, 160, 300, 210)
    ui.set_panel_style(hwnd, panel_id, 0x102563EB, 0x552563EB, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "⌨️ 键盘验证", 0, 0, 180, 30)
    note = ui.create_text(
        hwnd, panel_id,
        "可点击控件后用 Space 或 Enter 切换状态；禁用开关会保持加载样式但不响应交互。",
        0, 46, 240, 92,
    )
    ui.set_text_options(hwnd, note, align=0, valign=0, wrap=True, ellipsis=False)

    g_toggle_id = ui.create_button(hwnd, content_id, "🔁", "写入状态并读取", 40, 430, 170, 42)
    ui.set_button_variant(hwnd, g_toggle_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("表单选择组件验证已显示。窗口会保持 60 秒。")
    print("[初始读取] 可见:", ui.get_element_visible(hwnd, g_checkbox_id),
          "启用:", ui.get_element_enabled(hwnd, g_disabled_switch_id))
    print("[初始读取] 复选框:", ui.dll.EU_GetCheckboxChecked(hwnd, g_checkbox_id),
          "半选:", ui.dll.EU_GetCheckboxIndeterminate(hwnd, g_checkbox_id))
    print("[初始读取] 单选:", ui.dll.EU_GetRadioChecked(hwnd, g_radio_a_id),
          ui.dll.EU_GetRadioChecked(hwnd, g_radio_b_id))
    print("[初始读取] 开关:", ui.dll.EU_GetSwitchChecked(hwnd, g_switch_id),
          "加载:", ui.dll.EU_GetSwitchLoading(hwnd, g_disabled_switch_id))

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

    print("表单选择组件验证结束。")


if __name__ == "__main__":
    main()
