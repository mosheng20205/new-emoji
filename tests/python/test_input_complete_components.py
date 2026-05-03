import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_name_id = 0
g_note_id = 0
g_status_id = 0
g_apply_id = 0
g_clear_id = 0
g_text_callback = None


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Input 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.TextCallback
def on_text_change(element_id, utf8_ptr, length):
    raw = bytes(utf8_ptr[:length]) if utf8_ptr and length > 0 else b""
    value = raw.decode("utf-8", errors="replace")
    name = "备注" if element_id == g_note_id else "名称"
    print(f"[输入回调] {name}: {value!r}")
    update_status(f"📝 {name} 已变化，UTF-8 长度 {length}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_input_value(g_hwnd, g_name_id, "小林同学 ✅")
        ui.set_input_value(
            g_hwnd,
            g_note_id,
            "第一行：支持中文与 emoji ✨\n第二行：自动换行显示，回车可继续输入。\n第三行：文本变化会回调。",
        )
        ui.set_input_options(g_hwnd, g_note_id, readonly=False, password=False, multiline=True, validate_state=1)
        print("[读取] 名称:", ui.get_input_value(g_hwnd, g_name_id), ui.get_input_state(g_hwnd, g_name_id))
        print("[读取] 备注:", ui.get_input_value(g_hwnd, g_note_id), ui.get_input_state(g_hwnd, g_note_id))
        print("[读取] 最大长度:", ui.get_input_max_length(g_hwnd, g_note_id))
        update_status("✅ 已写入多行文本并触发输入变化回调")
    elif element_id == g_clear_id:
        ui.set_input_value(g_hwnd, g_note_id, "")
        update_status("🧹 已清空多行备注")


def main():
    global g_hwnd, g_name_id, g_note_id, g_status_id
    global g_apply_id, g_clear_id, g_text_callback

    hwnd = ui.create_window("📝 Input 完整封装验证", 220, 120, 960, 660)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_text_callback = on_text_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 610)
    ui.create_text(hwnd, content_id, "📝 输入框完整能力", 28, 24, 380, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "本窗口验证 clear、prefix/suffix、校验态、密码/只读状态、多行换行绘制、最大长度和 UTF-8 文本变化回调。",
        28, 72, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "👤 单行名称", 36, 150, 180, 26)
    g_name_id = ui.create_input(
        hwnd, content_id, value="访客", placeholder="请输入姓名 ✨",
        prefix="👤", suffix="名称", clearable=True,
        x=36, y=184, w=380, h=44,
    )
    ui.set_input_max_length(hwnd, g_name_id, 20)
    ui.dll.EU_SetInputTextCallback(hwnd, g_name_id, g_text_callback)

    ui.create_text(hwnd, content_id, "📒 多行备注", 36, 268, 180, 26)
    g_note_id = ui.create_input(
        hwnd, content_id, value="", placeholder="请输入多行备注，支持 emoji 🎯",
        prefix="🧾", suffix="", clearable=True,
        x=36, y=302, w=520, h=150,
    )
    ui.set_input_options(hwnd, g_note_id, readonly=False, password=False, multiline=True, validate_state=0)
    ui.set_input_max_length(hwnd, g_note_id, 160)
    ui.dll.EU_SetInputTextCallback(hwnd, g_note_id, g_text_callback)

    panel_id = ui.create_panel(hwnd, content_id, 610, 164, 290, 238)
    ui.set_panel_style(hwnd, panel_id, 0x101E66F5, 0x661E66F5, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "🔎 状态读回", 0, 0, 180, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待自动写入多行内容。", 0, 48, 240, 110)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "写入多行文本", 610, 454, 150, 42)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空备注", 778, 454, 120, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_clear_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("Input 完整封装验证已显示。窗口会保持 60 秒。")
    print("[初始] 名称:", ui.get_input_value(hwnd, g_name_id), ui.get_input_state(hwnd, g_name_id))
    print("[初始] 备注:", ui.get_input_state(hwnd, g_note_id), "最大长度:", ui.get_input_max_length(hwnd, g_note_id))

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_done = False
    while running and time.time() - start < 60:
        if not auto_done and time.time() - start > 1.0:
            on_click(g_apply_id)
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

    print("Input 完整封装验证结束。")


if __name__ == "__main__":
    main()
