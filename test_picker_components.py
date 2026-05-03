import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_autocomplete_id = 0
g_cascader_id = 0
g_datepicker_id = 0
g_timepicker_id = 0
g_update_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 输入增强组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        tips = ui.make_utf8("北京|上海|广州|深圳|成都|杭州|武汉")
        value = ui.make_utf8("杭州")
        ui.dll.EU_SetAutocompleteSuggestions(g_hwnd, g_autocomplete_id, ui.bytes_arg(tips), len(tips))
        ui.dll.EU_SetAutocompleteValue(g_hwnd, g_autocomplete_id, ui.bytes_arg(value), len(value))

        options = ui.make_utf8("浙江/杭州/西湖区|浙江/宁波/海曙区|四川/成都/高新区|广东/深圳/南山区")
        selected = ui.make_utf8("四川/成都/高新区")
        ui.dll.EU_SetCascaderOptions(g_hwnd, g_cascader_id, ui.bytes_arg(options), len(options))
        ui.dll.EU_SetCascaderValue(g_hwnd, g_cascader_id, ui.bytes_arg(selected), len(selected))

        ui.dll.EU_SetDatePickerDate(g_hwnd, g_datepicker_id, 2026, 6, 18)
        ui.dll.EU_SetTimePickerTime(g_hwnd, g_timepicker_id, 14, 30)
        print("[更新] 已更新自动补全、级联、日期和时间")
    else:
        print(f"[输入增强组件] 点击元素 #{element_id}")


def main():
    global g_hwnd, g_autocomplete_id, g_cascader_id
    global g_datepicker_id, g_timepicker_id, g_update_id

    hwnd = ui.create_window("输入增强组件示例", 240, 90, 900, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 570)

    ui.create_text(hwnd, content_id, "输入增强组件", 28, 24, 240, 28)
    ui.create_divider(hwnd, content_id, "Autocomplete / Cascader / DatePicker / TimePicker", 0, 1, 28, 62, 804, 34)

    ui.create_text(hwnd, content_id, "自动补全", 28, 120, 120, 28)
    g_autocomplete_id = ui.create_autocomplete(
        hwnd, content_id,
        "",
        ["北京", "上海", "广州", "深圳", "成都", "杭州"],
        150, 116, 280, 38
    )

    ui.create_text(hwnd, content_id, "级联选择", 28, 184, 120, 28)
    g_cascader_id = ui.create_cascader(
        hwnd, content_id,
        [
            ("浙江", "杭州", "西湖区"),
            ("浙江", "宁波", "海曙区"),
            ("江苏", "南京", "玄武区"),
            ("广东", "深圳", "南山区"),
            ("四川", "成都", "高新区"),
        ],
        ["浙江", "杭州", "西湖区"],
        150, 180, 300, 38
    )

    ui.create_text(hwnd, content_id, "日期选择", 28, 248, 120, 28)
    g_datepicker_id = ui.create_datepicker(
        hwnd, content_id,
        2026, 5, 2,
        150, 244, 220, 38
    )

    ui.create_text(hwnd, content_id, "时间选择", 28, 312, 120, 28)
    g_timepicker_id = ui.create_timepicker(
        hwnd, content_id,
        9, 30,
        150, 308, 180, 38
    )

    ui.create_card(
        hwnd, content_id,
        "本批组件",
        "这一批封装输入选择类组件，支持点击弹层、选中值和 Python setter 更新。示例窗口按逻辑尺寸预留首屏空间，适配高 DPI 首次运行。",
        1,
        500, 116, 330, 174
    )

    g_update_id = ui.create_button(
        hwnd, content_id,
        "",
        "更新示例值",
        500, 316, 150, 40
    )
    ui.create_infobox(
        hwnd, content_id,
        "提示",
        "点击输入框展开下拉面板；点击按钮会通过导出接口批量更新四个组件。",
        500, 380, 330, 90
    )

    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("输入增强组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("输入增强组件示例结束。")


if __name__ == "__main__":
    main()
