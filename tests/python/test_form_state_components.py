import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_checkbox_id = 0
g_radio_a_id = 0
g_radio_b_id = 0
g_switch_id = 0
g_update_id = 0
g_loading_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 表单状态组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        ui.dll.EU_SetCheckboxIndeterminate(g_hwnd, g_checkbox_id, 1)
        ui.dll.EU_SetRadioChecked(g_hwnd, g_radio_b_id, 1)
        ui.dll.EU_SetSwitchChecked(g_hwnd, g_switch_id, 1)
        ui.set_switch_texts(g_hwnd, g_switch_id, "已启用 ✅", "已关闭")
        print(
            "[更新] 复选半选=",
            ui.dll.EU_GetCheckboxIndeterminate(g_hwnd, g_checkbox_id),
            "单选A=",
            ui.dll.EU_GetRadioChecked(g_hwnd, g_radio_a_id),
            "单选B=",
            ui.dll.EU_GetRadioChecked(g_hwnd, g_radio_b_id),
        )
    elif element_id == g_loading_id:
        loading = 0 if ui.dll.EU_GetSwitchLoading(g_hwnd, g_switch_id) else 1
        ui.dll.EU_SetSwitchLoading(g_hwnd, g_switch_id, loading)
        print("[开关] 加载状态=", ui.dll.EU_GetSwitchLoading(g_hwnd, g_switch_id))
    else:
        print(
            "[表单状态] checked=",
            ui.dll.EU_GetCheckboxChecked(g_hwnd, g_checkbox_id),
            "indeterminate=",
            ui.dll.EU_GetCheckboxIndeterminate(g_hwnd, g_checkbox_id),
            "switch=",
            ui.dll.EU_GetSwitchChecked(g_hwnd, g_switch_id),
        )


def main():
    global g_hwnd, g_checkbox_id, g_radio_a_id, g_radio_b_id, g_switch_id
    global g_update_id, g_loading_id

    hwnd = ui.create_window("☑️ 表单状态组件示例", 240, 100, 720, 460)
    if not hwnd:
        print("错误：窗口创建失败")
        return
    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 700, 410)
    ui.create_text(hwnd, content_id, "☑️ 表单状态组件", 28, 24, 260, 30)
    ui.create_divider(hwnd, content_id, "复选框 / 单选框 / 开关", 0, 1, 28, 60, 620, 28)

    g_checkbox_id = ui.create_checkbox(hwnd, content_id, "📌 部分权限已选择", False, 28, 108, 260, 34,
                                       border=True, size=1)
    ui.dll.EU_SetCheckboxIndeterminate(hwnd, g_checkbox_id, 1)
    print("[读取] 复选框样式=", ui.get_checkbox_options(hwnd, g_checkbox_id))

    g_radio_a_id = ui.create_radio(hwnd, content_id, "🟢 普通模式", True, 28, 156, 180, 34)
    g_radio_b_id = ui.create_radio(hwnd, content_id, "🔵 专家模式", False, 220, 156, 180, 34)
    ui.set_radio_group(hwnd, g_radio_a_id, "mode")
    ui.set_radio_group(hwnd, g_radio_b_id, "mode")

    g_switch_id = ui.create_switch(hwnd, content_id, "🚀 自动同步", False, 28, 208, 300, 36)
    ui.set_switch_texts(hwnd, g_switch_id, "已启用 ✅", "已关闭")

    g_update_id = ui.create_button(hwnd, content_id, "🔄", "应用状态", 28, 278, 140, 40)
    g_loading_id = ui.create_button(hwnd, content_id, "⏳", "切换加载", 184, 278, 140, 40)

    ui.create_infobox(
        hwnd, content_id,
        "✅ 本批完善",
        "复选框半选、单选框分组互斥、开关加载态和开关文案均已开放 API。",
        360, 108, 300, 108,
    )

    for eid in (g_checkbox_id, g_radio_a_id, g_radio_b_id, g_switch_id, g_update_id, g_loading_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("表单状态组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("表单状态组件示例结束。")


if __name__ == "__main__":
    main()
