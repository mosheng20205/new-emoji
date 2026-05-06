import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_click_count = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Loading 完整样式验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(_element_id):
    global g_click_count
    g_click_count += 1


def pump_messages(user32, msg, duration):
    start = time.time()
    running = True
    while running and time.time() - start < duration:
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


def click_client(hwnd, x, y):
    lparam = (y << 16) | (x & 0xFFFF)
    ctypes.windll.user32.SendMessageW(hwnd, 0x0201, 1, lparam)
    ctypes.windll.user32.SendMessageW(hwnd, 0x0202, 0, lparam)


def click_logical(hwnd, x, y):
    user32 = ctypes.windll.user32
    try:
        dpi = user32.GetDpiForWindow(hwnd)
    except AttributeError:
        dpi = 96
    scale = dpi / 96.0 if dpi else 1.0
    click_client(hwnd, int(x * scale), int(y * scale))


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    global g_hwnd, g_click_count

    hwnd = ui.create_window("⏳ Loading 加载完整样式验证", 220, 80, 1060, 760)
    assert_state(hwnd, "窗口创建失败")
    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1020, 700)

    ui.create_text(hwnd, content_id, "⏳ Loading 加载完整样式验证", 30, 24, 680, 38)
    intro = ui.create_text(
        hwnd,
        content_id,
        "验证局部遮罩、自定义文案、黑色背景、圆弧 spinner、脉冲 spinner、进度、全屏锁定和服务式打开/关闭。",
        30, 70, 930, 52,
    )
    ui.set_text_options(hwnd, intro, align=0, valign=0, wrap=True, ellipsis=False)

    table_id = ui.create_table(
        hwnd, content_id,
        ["日期", "姓名", "地址"],
        [
            ["2016-05-03", "王小虎", "上海市普陀区金沙江路 1518 弄"],
            ["2016-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"],
            ["2016-05-04", "王小虎", "上海市普陀区金沙江路 1518 弄"],
        ],
        True, True, 70, 142, 760, 210,
    )

    loading_id = ui.create_loading(hwnd, content_id, text="📦 正在同步数据", active=True,
                                   x=70, y=142, w=760, h=210)
    ui.set_loading_target(hwnd, loading_id, table_id, 0)
    ui.set_loading_options(hwnd, loading_id, active=True, fullscreen=False, progress=42)
    ui.set_loading_style(hwnd, loading_id, background=0xCC000000, spinner_color=0xFFFFFFFF,
                         text_color=0xFFFFFFFF, spinner="el-icon-loading", lock_input=True)

    ui.set_loading_text(hwnd, loading_id, "拼命加载中")
    assert_state("拼命加载中" in ui.get_loading_text(hwnd, loading_id), "加载文本读回失败")
    style = ui.get_loading_style(hwnd, loading_id)
    assert_state(style and style["background"] == 0xCC000000, "背景色读回失败")
    assert_state(style["spinner_color"] == 0xFFFFFFFF and style["text_color"] == 0xFFFFFFFF, "颜色读回失败")
    assert_state(style["spinner_type"] == 1 and style["lock_input"], "圆弧 spinner 或锁定状态失败")

    state = ui.get_loading_full_state(hwnd, loading_id)
    assert_state(state and state["active"] == 1 and state["progress"] == 42, "初始 Loading 状态失败")
    assert_state(state["target_element_id"] == table_id and state["timer_running"] == 1, "目标绑定或定时器失败")

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.35)
    animated = ui.get_loading_full_state(hwnd, loading_id)
    assert_state(animated["tick_count"] > state["tick_count"], "Loading 动画未推进")

    ui.set_loading_style(hwnd, loading_id, spinner="pulse", background=0xAAFFFFFF,
                         spinner_color=0xFF67C23A, text_color=0xFF303133, lock_input=False)
    pulse_style = ui.get_loading_style(hwnd, loading_id)
    assert_state(pulse_style["spinner_type"] == 2 and not pulse_style["lock_input"], "脉冲 spinner 状态失败")

    action_button = ui.create_button(hwnd, content_id, "✅", "底层按钮", 70, 410, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, action_button, on_click)
    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(user32, msg, 0.1)
    click_logical(hwnd, 100, 461)
    pump_messages(user32, msg, 0.1)
    assert_state(g_click_count == 1, "非锁定 Loading 不应拦截底层点击")

    full_id = ui.show_loading(hwnd, 0, "🔒 全屏锁定处理中", fullscreen=True, lock_input=True,
                              background=0xCC111827, spinner_color=0xFF409EFF,
                              text_color=0xFFFFFFFF, spinner="arc")
    assert_state(full_id > 0, "服务式全屏 Loading 创建失败")
    full_state = ui.get_loading_full_state(hwnd, full_id)
    full_style = ui.get_loading_style(hwnd, full_id)
    assert_state(full_state and full_state["fullscreen"] == 1 and full_state["active"] == 1, "全屏状态失败")
    assert_state(full_style and full_style["lock_input"] and full_style["spinner_type"] == 1, "全屏样式失败")

    click_logical(hwnd, 100, 461)
    pump_messages(user32, msg, 0.1)
    assert_state(g_click_count == 1, "全屏锁定 Loading 应拦截底层点击")
    assert_state(ui.close_loading(hwnd, full_id), "服务式 Loading 关闭失败")
    click_logical(hwnd, 100, 461)
    pump_messages(user32, msg, 0.1)
    assert_state(g_click_count == 2, "关闭 Loading 后底层点击未恢复")

    service_id = ui.show_loading(hwnd, table_id, "🚀 服务方式加载", fullscreen=False, lock_input=True,
                                 background=0xCC000000, spinner_color=0xFFFFD166,
                                 text_color=0xFFFFFFFF, spinner="el-icon-loading")
    assert_state(service_id > 0, "局部服务式 Loading 创建失败")
    service_state = ui.get_loading_full_state(hwnd, service_id)
    assert_state(service_state and service_state["target_element_id"] == table_id, "服务式目标绑定失败")
    assert_state(ui.close_loading(hwnd, service_id), "局部服务式 Loading 关闭失败")

    ui.set_loading_options(hwnd, loading_id, active=False, fullscreen=False, progress=100)
    stopped = ui.get_loading_full_state(hwnd, loading_id)
    assert_state(stopped["active"] == 0 and stopped["timer_running"] == 0, "停止 Loading 失败")

    print("[通过] Loading 样式、服务式 API、全屏锁定和动画状态均验证完成。")
    pump_messages(user32, msg, 0.8)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
