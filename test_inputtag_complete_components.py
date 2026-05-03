import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tags_id = 0
g_status_id = 0
g_apply_id = 0
g_remove_id = 0
g_change_callback = None


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] InputTag 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.TextCallback
def on_tags_change(element_id, utf8_ptr, length):
    raw = bytes(utf8_ptr[:length]) if utf8_ptr and length > 0 else b""
    value = raw.decode("utf-8", errors="replace")
    print(f"[标签回调] {value}")
    update_status(f"🏷️ 标签变化：{value}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.add_input_tag_item(g_hwnd, g_tags_id, "测试 ✅")
        duplicate_ok = ui.add_input_tag_item(g_hwnd, g_tags_id, "产品")
        ui.set_input_tag_input_value(g_hwnd, g_tags_id, "待提交 ✨")
        count = ui.get_input_tag_count(g_hwnd, g_tags_id)
        first = ui.get_input_tag_item(g_hwnd, g_tags_id, 0)
        last = ui.get_input_tag_item(g_hwnd, g_tags_id, count - 1)
        print("[读取] 数量:", count, "首项:", first, "末项:", last, "重复添加:", duplicate_ok)
        print("[读取] 输入缓冲:", ui.get_input_tag_input_value(g_hwnd, g_tags_id), ui.get_input_tag_options(g_hwnd, g_tags_id))
        update_status(f"✅ 已添加标签，数量 {count}，重复项被拦截：{not duplicate_ok}")
    elif element_id == g_remove_id:
        removed = ui.remove_input_tag_item(g_hwnd, g_tags_id, 1)
        print("[删除] index=1:", removed, "数量:", ui.get_input_tag_count(g_hwnd, g_tags_id))
        update_status(f"🧹 删除第 2 个标签：{removed}")


def main():
    global g_hwnd, g_tags_id, g_status_id, g_apply_id, g_remove_id, g_change_callback

    hwnd = ui.create_window("🏷️ InputTag 完整封装验证", 220, 120, 920, 600)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_change_callback = on_tags_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 550)
    ui.create_text(hwnd, content_id, "🏷️ 标签输入框完整能力", 28, 24, 420, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "本窗口验证标签增删、最大数量、重复校验、单项读回、输入缓冲读写、键盘编辑基础和标签变化回调。",
        28, 72, 800, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_tags_id = ui.create_input_tag(
        hwnd, content_id, tags=["产品", "设计"], placeholder="输入标签，回车提交 🏷️",
        x=36, y=154, w=520, h=150,
    )
    ui.set_input_tag_options(hwnd, g_tags_id, max_count=4, allow_duplicates=False)
    ui.dll.EU_SetInputTagChangeCallback(hwnd, g_tags_id, g_change_callback)

    panel_id = ui.create_panel(hwnd, content_id, 610, 154, 260, 220)
    ui.set_panel_style(hwnd, panel_id, 0x108E24AA, 0x668E24AA, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "🔎 状态读回", 0, 0, 180, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待自动添加标签。", 0, 48, 210, 112)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "添加并读取", 36, 382, 150, 42)
    g_remove_id = ui.create_button(hwnd, content_id, "🧹", "删除第 2 项", 208, 382, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_remove_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("InputTag 完整封装验证已显示。窗口会保持 60 秒。")
    print("[初始] 数量:", ui.get_input_tag_count(hwnd, g_tags_id), ui.get_input_tag_options(hwnd, g_tags_id))
    print("[初始] 第 1 项:", ui.get_input_tag_item(hwnd, g_tags_id, 0))

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_stage = 0
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if auto_stage == 0 and elapsed > 1.0:
            on_click(g_apply_id)
            auto_stage = 1
        elif auto_stage == 1 and elapsed > 2.0:
            on_click(g_remove_id)
            auto_stage = 2
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

    print("InputTag 完整封装验证结束。")


if __name__ == "__main__":
    main()
