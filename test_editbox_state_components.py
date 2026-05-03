import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_edit_id = 0
g_password_id = 0
g_multiline_id = 0
g_update_id = 0
g_readonly = False


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 编辑框状态验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_readonly
    if element_id != g_update_id:
        return
    g_readonly = not g_readonly
    ui.set_editbox_text(g_hwnd, g_edit_id, "已通过 API 写入：中文 + emoji 🎯")
    ui.set_editbox_options(
        g_hwnd, g_edit_id,
        readonly=g_readonly,
        password=False,
        multiline=False,
        focus_border=0xFF16A34A if g_readonly else 0xFF2563EB,
        placeholder="请输入中文或 emoji ✨",
    )
    print("[读取] 主编辑框文本:", ui.get_editbox_text(g_hwnd, g_edit_id))
    print("[读取] 主编辑框选项:", ui.get_editbox_options(g_hwnd, g_edit_id))
    print("[读取] 主编辑框状态:", ui.get_editbox_state(g_hwnd, g_edit_id))


def main():
    global g_hwnd, g_edit_id, g_password_id, g_multiline_id, g_update_id

    hwnd = ui.create_window("⌨️ 编辑框状态验证", 220, 90, 900, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 570)

    ui.create_text(hwnd, content_id, "⌨️ EditBox 文本、占位、密码、多行与状态读回", 28, 24, 720, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "这一批补齐 EditBox 专用 Set/Get：可以设置文本、只读/密码/多行/焦点色/占位文本，"
        "并读取光标、选区和文本长度状态。",
        28, 70, 720, 60,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "📝 普通编辑框", 28, 154, 180, 28)
    g_edit_id = ui.create_editbox(hwnd, content_id, 28, 188, 500, 40)
    ui.set_editbox_options(hwnd, g_edit_id, False, False, False, 0xFF2563EB, "请输入中文或 emoji ✨")

    ui.create_text(hwnd, content_id, "🔒 密码编辑框", 28, 252, 180, 28)
    g_password_id = ui.create_editbox(hwnd, content_id, 28, 286, 500, 40)
    ui.set_editbox_text(hwnd, g_password_id, "安全口令🔑")
    ui.set_editbox_options(hwnd, g_password_id, False, True, False, 0xFF7C3AED, "请输入密码")

    ui.create_text(hwnd, content_id, "📚 多行编辑框", 28, 350, 180, 28)
    g_multiline_id = ui.create_editbox(hwnd, content_id, 28, 384, 500, 86)
    ui.set_editbox_text(hwnd, g_multiline_id, "第一行：中文\n第二行：emoji 🌈")
    ui.set_editbox_options(hwnd, g_multiline_id, False, False, True, 0xFF16A34A, "请输入多行内容")

    status_panel = ui.create_panel(hwnd, content_id, 574, 170, 260, 230)
    ui.set_panel_style(hwnd, status_panel, 0x102563EB, 0x552563EB, 1.0, 12.0, 16)
    ui.create_text(hwnd, status_panel, "🔎 状态读取", 0, 0, 180, 30)
    status_text = ui.create_text(
        hwnd, status_panel,
        "窗口显示后会在控制台输出三个编辑框的选项与状态；点击按钮会写入新文本并切换只读状态。",
        0, 42, 210, 110,
    )
    ui.set_text_options(hwnd, status_text, align=0, valign=0, wrap=True, ellipsis=False)

    g_update_id = ui.create_button(hwnd, content_id, "🔁", "写入并切换只读", 574, 430, 180, 42)
    ui.set_button_variant(hwnd, g_update_id, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("编辑框状态验证已显示。窗口会保持 60 秒。")
    for name, eid in [("普通", g_edit_id), ("密码", g_password_id), ("多行", g_multiline_id)]:
        print(f"[初始读取] {name}选项:", ui.get_editbox_options(hwnd, eid))
        print(f"[初始读取] {name}状态:", ui.get_editbox_state(hwnd, eid))
        print(f"[初始读取] {name}文本:", ui.get_editbox_text(hwnd, eid))

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

    print("编辑框状态验证结束。")


if __name__ == "__main__":
    main()
