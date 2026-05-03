import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_input_id = 0
g_input_tag_id = 0
g_mentions_id = 0
g_time_select_id = 0
g_apply_id = 0
g_reset_id = 0


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    if not data:
        return None, 0
    return ui.bytes_arg(data), len(data)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 表单组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[Resize] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.dll.EU_SetInputValue(g_hwnd, g_input_id, *utf8_arg("张三😀"))
        ui.dll.EU_SetInputPlaceholder(g_hwnd, g_input_id, *utf8_arg("请输入姓名"))
        ui.dll.EU_SetInputAffixes(g_hwnd, g_input_id, *utf8_arg("用户："), *utf8_arg("kg"))
        ui.dll.EU_SetInputClearable(g_hwnd, g_input_id, 1)

        ui.dll.EU_SetInputTagTags(
            g_hwnd, g_input_tag_id, *utf8_arg("前端|后端|UI|Emoji")
        )
        ui.dll.EU_SetInputTagPlaceholder(
            g_hwnd, g_input_tag_id, *utf8_arg("输入标签后回车提交")
        )

        ui.dll.EU_SetMentionsValue(
            g_hwnd, g_mentions_id, *utf8_arg("请在 @ 后选择成员")
        )
        ui.dll.EU_SetMentionsSuggestions(
            g_hwnd, g_mentions_id, *utf8_arg("Alice|Bob|Charlie|Dora")
        )

        ui.dll.EU_SetTimeSelectTime(g_hwnd, g_time_select_id, 14, 45)
        print("[表单] 已填充示例数据")
    elif element_id == g_reset_id:
        ui.dll.EU_SetInputValue(g_hwnd, g_input_id, *utf8_arg(""))
        ui.dll.EU_SetInputPlaceholder(g_hwnd, g_input_id, *utf8_arg("请输入内容"))
        ui.dll.EU_SetInputAffixes(g_hwnd, g_input_id, *utf8_arg(""), *utf8_arg(""))
        ui.dll.EU_SetInputClearable(g_hwnd, g_input_id, 0)

        ui.dll.EU_SetInputTagTags(g_hwnd, g_input_tag_id, *utf8_arg("前端|设计"))
        ui.dll.EU_SetInputTagPlaceholder(
            g_hwnd, g_input_tag_id, *utf8_arg("输入标签，回车提交")
        )

        ui.dll.EU_SetMentionsValue(g_hwnd, g_mentions_id, *utf8_arg("请在 @ 后选择"))
        ui.dll.EU_SetMentionsSuggestions(
            g_hwnd, g_mentions_id, *utf8_arg("Alice|Bob|Charlie")
        )

        ui.dll.EU_SetTimeSelectTime(g_hwnd, g_time_select_id, 9, 30)
        print("[表单] 已恢复默认状态")


def main():
    global g_hwnd, g_input_id, g_input_tag_id, g_mentions_id, g_time_select_id
    global g_apply_id, g_reset_id

    hwnd = ui.create_window("表单组件示例", 220, 120, 920, 650)
    if not hwnd:
        print("ERROR: failed to create window")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 600)

    ui.create_text(hwnd, content_id, "表单组件批次", 20, 18, 260, 28)
    ui.create_divider(hwnd, content_id, "Input / InputTag / Mentions / TimeSelect", 0, 1, 20, 52, 860, 26)

    ui.create_text(hwnd, content_id, "输入框", 20, 82, 120, 24)
    g_input_id = ui.create_input(
        hwnd, content_id,
        "张三😀", "请输入姓名", "用户：", "kg", True,
        20, 110, 380, 40
    )

    ui.create_text(hwnd, content_id, "标签输入", 20, 170, 120, 24)
    g_input_tag_id = ui.create_input_tag(
        hwnd, content_id,
        ["前端", "设计"], "输入标签后回车提交",
        20, 198, 380, 112
    )

    ui.create_text(hwnd, content_id, "Mentions", 20, 330, 120, 24)
    g_mentions_id = ui.create_mentions(
        hwnd, content_id,
        "请在 @ 后选择成员", ["Alice", "Bob", "Charlie", "Dora"],
        20, 358, 380, 46
    )

    ui.create_text(hwnd, content_id, "时间选择", 430, 82, 120, 24)
    g_time_select_id = ui.create_time_select(hwnd, content_id, 9, 30, 430, 110, 220, 40)

    ui.create_text(hwnd, content_id, "操作", 430, 170, 120, 24)
    g_apply_id = ui.create_button(hwnd, content_id, "", "填充示例", 430, 198, 160, 40)
    g_reset_id = ui.create_button(hwnd, content_id, "", "恢复默认", 600, 198, 160, 40)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "说明",
        "这个批次补齐了表单类控件的运行时更新接口，并演示 Input、InputTag、Mentions 和 TimeSelect 的基础用法。",
        430, 260, 390, 104
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("Form demo visible. Close the window or wait 60 seconds.")

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

    print("Form demo complete.")


if __name__ == "__main__":
    main()
