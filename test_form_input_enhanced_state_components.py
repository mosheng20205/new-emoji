import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_slider_id = 0
g_number_id = 0
g_input_id = 0
g_tag_id = 0
g_update_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 表单输入增强验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id != g_update_id:
        return
    ui.dll.EU_SetSliderValue(g_hwnd, g_slider_id, 85)
    ui.dll.EU_SetInputNumberValue(g_hwnd, g_number_id, 12)
    ui.set_input_value(g_hwnd, g_input_id, "已校验通过 ✅")
    ui.set_input_options(g_hwnd, g_input_id, readonly=False, password=False, multiline=False, validate_state=1)
    tags = ui.make_utf8("产品|设计|研发|产品")
    ui.dll.EU_SetInputTagTags(g_hwnd, g_tag_id, ui.bytes_arg(tags), len(tags))
    ui.set_input_tag_options(g_hwnd, g_tag_id, max_count=3, allow_duplicates=False)
    print("[读取] Slider:", ui.dll.EU_GetSliderValue(g_hwnd, g_slider_id), ui.get_slider_options(g_hwnd, g_slider_id))
    print("[读取] InputNumber:", ui.dll.EU_GetInputNumberValue(g_hwnd, g_number_id),
          ui.get_input_number_options(g_hwnd, g_number_id),
          "可加:", ui.dll.EU_GetInputNumberCanStep(g_hwnd, g_number_id, 5))
    print("[读取] Input:", ui.get_input_value(g_hwnd, g_input_id), ui.get_input_state(g_hwnd, g_input_id))
    print("[读取] InputTag:", ui.get_input_tag_count(g_hwnd, g_tag_id), ui.get_input_tag_options(g_hwnd, g_tag_id))


def main():
    global g_hwnd, g_slider_id, g_number_id, g_input_id, g_tag_id, g_update_id

    hwnd = ui.create_window("🧮 表单输入增强验证", 220, 90, 980, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 630)

    ui.create_text(hwnd, content_id, "🧮 Slider / InputNumber / Input / InputTag", 28, 24, 760, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "这一批补齐输入类控件的状态读回和约束选项：滑块范围/步长/提示、数字输入范围/步长、"
        "输入框值与校验状态、标签输入最大数量和重复校验。",
        28, 70, 820, 64,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_slider_id = ui.create_slider(
        hwnd, content_id, "🎚️ 完成度", 0, 100, 40,
        40, 160, 420, 62, step=5, show_tooltip=True,
    )

    g_number_id = ui.create_input_number(
        hwnd, content_id, "🔢 数量", value=6, min_value=0, max_value=20, step=2,
        x=40, y=248, w=320, h=40,
    )

    g_input_id = ui.create_input(
        hwnd, content_id, value="待校验", placeholder="请输入名称 ✨",
        prefix="📝", suffix="状态", clearable=True,
        x=40, y=328, w=420, h=42,
    )
    ui.set_input_options(hwnd, g_input_id, readonly=False, password=False, multiline=False, validate_state=2)

    g_tag_id = ui.create_input_tag(
        hwnd, content_id, tags=["产品", "设计"], placeholder="输入标签，回车提交 🏷️",
        x=40, y=408, w=520, h=96,
    )
    ui.set_input_tag_options(hwnd, g_tag_id, max_count=4, allow_duplicates=False)

    panel_id = ui.create_panel(hwnd, content_id, 610, 170, 280, 250)
    ui.set_panel_style(hwnd, panel_id, 0x102563EB, 0x552563EB, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "🔎 状态读回", 0, 0, 180, 30)
    note = ui.create_text(
        hwnd, panel_id,
        "窗口显示后会输出初始状态；点击按钮或等待自动触发后，会写入新值并再次读取所有新增 API。",
        0, 46, 230, 108,
    )
    ui.set_text_options(hwnd, note, align=0, valign=0, wrap=True, ellipsis=False)

    g_update_id = ui.create_button(hwnd, content_id, "🔁", "写入状态并读取", 610, 462, 170, 42)
    ui.set_button_variant(hwnd, g_update_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("表单输入增强验证已显示。窗口会保持 60 秒。")
    print("[初始读取] Slider:", ui.dll.EU_GetSliderValue(hwnd, g_slider_id), ui.get_slider_options(hwnd, g_slider_id))
    print("[初始读取] InputNumber:", ui.dll.EU_GetInputNumberValue(hwnd, g_number_id),
          ui.get_input_number_options(hwnd, g_number_id))
    print("[初始读取] Input:", ui.get_input_value(hwnd, g_input_id), ui.get_input_state(hwnd, g_input_id))
    print("[初始读取] InputTag:", ui.get_input_tag_count(hwnd, g_tag_id), ui.get_input_tag_options(hwnd, g_tag_id))

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_done = False
    while running and time.time() - start < 60:
        if not auto_done and time.time() - start > 1.0:
            on_click(g_update_id)
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

    print("表单输入增强验证结束。")


if __name__ == "__main__":
    main()
