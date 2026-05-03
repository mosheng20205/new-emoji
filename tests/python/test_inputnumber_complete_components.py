import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_amount_id = 0
g_stock_id = 0
g_status_id = 0
g_apply_id = 0
g_invalid_id = 0
g_value_callback = None


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] InputNumber 完整封装验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def update_status(text):
    if g_hwnd and g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


@ui.ValueCallback
def on_value_change(element_id, value, min_value, max_value):
    name = "金额" if element_id == g_amount_id else "库存"
    print(f"[数字回调] {name}: value={value}, range={min_value}-{max_value}")
    update_status(f"🔢 {name} 已变化：内部值 {value}，范围 {min_value} - {max_value}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_input_number_precision(g_hwnd, g_amount_id, 2)
        ok = ui.set_input_number_text(g_hwnd, g_amount_id, "128.50")
        ui.dll.EU_SetInputNumberValue(g_hwnd, g_stock_id, 18)
        amount_text = ui.get_input_number_text(g_hwnd, g_amount_id)
        amount_state = ui.get_input_number_state(g_hwnd, g_amount_id)
        stock_state = ui.get_input_number_state(g_hwnd, g_stock_id)
        print("[读取] 金额:", amount_text, ok, amount_state)
        print("[读取] 库存:", ui.dll.EU_GetInputNumberValue(g_hwnd, g_stock_id), stock_state)
        update_status(f"✅ 文本校验通过：金额 {amount_text}，库存 {ui.dll.EU_GetInputNumberValue(g_hwnd, g_stock_id)}")
    elif element_id == g_invalid_id:
        ok = ui.set_input_number_text(g_hwnd, g_amount_id, "12.345")
        state = ui.get_input_number_state(g_hwnd, g_amount_id)
        print("[无效输入] 返回:", ok, "状态:", state, "显示:", ui.get_input_number_text(g_hwnd, g_amount_id))
        update_status(f"⚠️ 无效小数被拦截：校验结果 {ok}，状态 {state}")


def main():
    global g_hwnd, g_amount_id, g_stock_id, g_status_id
    global g_apply_id, g_invalid_id, g_value_callback

    hwnd = ui.create_window("🔢 InputNumber 完整封装验证", 220, 120, 920, 600)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    g_value_callback = on_value_change
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 550)
    ui.create_text(hwnd, content_id, "🔢 数字输入框完整能力", 28, 24, 420, 36)
    intro_id = ui.create_text(
        hwnd, content_id,
        "本窗口验证长按步进、边界夹紧、固定小数精度、文本输入校验、状态读回和值变化回调。",
        28, 72, 760, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "💰 金额输入（两位小数）", 36, 150, 260, 26)
    g_amount_id = ui.create_input_number(
        hwnd, content_id, "金额 💰", value=9900, min_value=0, max_value=20000, step=25,
        x=36, y=184, w=360, h=44,
    )
    ui.set_input_number_precision(hwnd, g_amount_id, 2)
    ui.dll.EU_SetInputNumberValueCallback(hwnd, g_amount_id, g_value_callback)

    ui.create_text(hwnd, content_id, "📦 库存输入（整数边界）", 36, 270, 260, 26)
    g_stock_id = ui.create_input_number(
        hwnd, content_id, "库存 📦", value=6, min_value=0, max_value=20, step=2,
        x=36, y=304, w=320, h=44,
    )
    ui.dll.EU_SetInputNumberValueCallback(hwnd, g_stock_id, g_value_callback)

    panel_id = ui.create_panel(hwnd, content_id, 560, 150, 300, 220)
    ui.set_panel_style(hwnd, panel_id, 0x1043A047, 0x6643A047, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel_id, "🧪 验证状态", 0, 0, 180, 30)
    g_status_id = ui.create_text(hwnd, panel_id, "等待自动写入与无效输入校验。", 0, 48, 250, 110)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "写入有效小数", 560, 414, 150, 42)
    g_invalid_id = ui.create_button(hwnd, content_id, "⚠️", "尝试无效小数", 728, 414, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_invalid_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("InputNumber 完整封装验证已显示。窗口会保持 60 秒。")
    print("[初始] 金额:", ui.get_input_number_text(hwnd, g_amount_id), ui.get_input_number_state(hwnd, g_amount_id))
    print("[初始] 库存:", ui.dll.EU_GetInputNumberValue(hwnd, g_stock_id), ui.get_input_number_options(hwnd, g_stock_id))

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
            on_click(g_invalid_id)
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

    print("InputNumber 完整封装验证结束。")


if __name__ == "__main__":
    main()
