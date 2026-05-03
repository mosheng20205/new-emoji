import ctypes
from ctypes import wintypes
import sys
import time

import test_new_emoji as ui

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WINDOW_W = 1040
WINDOW_H = 760
CONTENT_W = 1010
CONTENT_H = 710

g_hwnd = None
g_title_id = 0
g_status_id = 0
g_detail_id = 0
g_edit_id = 0
g_badge_id = 0
g_move_card_id = 0
g_hidden_tip_id = 0
g_disabled_button_id = 0
g_update_id = 0
g_toggle_visible_id = 0
g_toggle_enabled_id = 0
g_move_id = 0
g_message_id = 0
g_confirm_id = 0
g_bounds_id = 0
g_dark_id = 0
g_light_id = 0
g_system_id = 0
g_flip = False
g_hidden_visible = False
g_button_enabled = True
g_card_moved = False


ui.dll.EU_SetWindowTitle.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
ui.dll.EU_SetWindowTitle.restype = None
ui.dll.EU_SetWindowBounds.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
ui.dll.EU_SetWindowBounds.restype = None
ui.dll.EU_GetWindowBounds.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
ui.dll.EU_GetWindowBounds.restype = ctypes.c_int
ui.dll.EU_GetElementText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
ui.dll.EU_GetElementText.restype = ctypes.c_int
ui.dll.EU_GetEditBoxText.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
ui.dll.EU_GetEditBoxText.restype = ctypes.c_int
ui.dll.EU_GetElementBounds.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]
ui.dll.EU_GetElementBounds.restype = ctypes.c_int
ui.dll.EU_SetElementVisible.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
ui.dll.EU_SetElementVisible.restype = None
ui.dll.EU_SetElementEnabled.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_int]
ui.dll.EU_SetElementEnabled.restype = None
ui.dll.EU_SetElementFont.argtypes = [
    wintypes.HWND, ctypes.c_int,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
    ctypes.c_float,
]
ui.dll.EU_SetElementFont.restype = None


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


def set_text(element_id: int, text: str):
    data, length = utf8_arg(text)
    ui.dll.EU_SetElementText(g_hwnd, element_id, data, length)


def set_window_title(text: str):
    data, length = utf8_arg(text)
    ui.dll.EU_SetWindowTitle(g_hwnd, data, length)


def set_font(element_id: int, font_name: str, size: float):
    data, length = utf8_arg(font_name)
    ui.dll.EU_SetElementFont(g_hwnd, element_id, data, length, ctypes.c_float(size))


def get_element_text(element_id: int, editbox=False) -> str:
    buf = (ctypes.c_ubyte * 512)()
    if editbox:
        needed = ui.dll.EU_GetEditBoxText(g_hwnd, element_id, buf, len(buf))
    else:
        needed = ui.dll.EU_GetElementText(g_hwnd, element_id, buf, len(buf))
    if needed <= 0:
        return ""
    raw = bytes(buf[: min(needed, len(buf) - 1)])
    return raw.decode("utf-8", errors="replace")


def get_element_bounds(element_id: int):
    x = ctypes.c_int()
    y = ctypes.c_int()
    w = ctypes.c_int()
    h = ctypes.c_int()
    ok = ui.dll.EU_GetElementBounds(g_hwnd, element_id, ctypes.byref(x), ctypes.byref(y), ctypes.byref(w), ctypes.byref(h))
    return ok, x.value, y.value, w.value, h.value


def get_window_bounds():
    x = ctypes.c_int()
    y = ctypes.c_int()
    w = ctypes.c_int()
    h = ctypes.c_int()
    ok = ui.dll.EU_GetWindowBounds(g_hwnd, ctypes.byref(x), ctypes.byref(y), ctypes.byref(w), ctypes.byref(h))
    return ok, x.value, y.value, w.value, h.value


def show_message(title: str, text: str, confirm="知道了 ✅"):
    title_data, title_len = utf8_arg(title)
    text_data, text_len = utf8_arg(text)
    confirm_data, confirm_len = utf8_arg(confirm)
    return ui.dll.EU_ShowMessageBox(
        g_hwnd,
        title_data, title_len,
        text_data, text_len,
        confirm_data, confirm_len,
        on_messagebox_result
    )


def show_confirm(title: str, text: str, confirm="确认 ✅", cancel="取消 ❌"):
    title_data, title_len = utf8_arg(title)
    text_data, text_len = utf8_arg(text)
    confirm_data, confirm_len = utf8_arg(confirm)
    cancel_data, cancel_len = utf8_arg(cancel)
    return ui.dll.EU_ShowConfirmBox(
        g_hwnd,
        title_data, title_len,
        text_data, text_len,
        confirm_data, confirm_len,
        cancel_data, cancel_len,
        on_messagebox_result
    )


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 🧩 交互 API 示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] 🪟 宽 {width}，高 {height}")


@ui.MessageBoxCallback
def on_messagebox_result(messagebox_id, result):
    label = {1: "确认", 0: "取消", -1: "关闭"}.get(result, str(result))
    print(f"[弹窗回调] 💬 弹窗 {messagebox_id} 返回：{label}")
    set_text(g_status_id, f"💬 弹窗 {messagebox_id} 返回：{label}")


@ui.ClickCallback
def on_click(element_id):
    global g_flip, g_hidden_visible, g_button_enabled, g_card_moved

    if element_id == g_update_id:
        g_flip = not g_flip
        if g_flip:
            set_window_title("🧩 交互 API 示例 - 已切换数据")
            set_text(g_title_id, "🧩 通用命令已更新")
            set_text(g_status_id, "✅ 文本、颜色、字体和标题已经更新")
            set_text(g_detail_id, "🎨 当前状态：强调色 + 更大的中文字体 + emoji 文本")
            ui.dll.EU_SetElementColor(g_hwnd, g_title_id, 0x00000000, 0xFF2563EB)
            ui.dll.EU_SetElementColor(g_hwnd, g_badge_id, 0xFFDBEAFE, 0xFF1D4ED8)
            set_font(g_title_id, "Microsoft YaHei UI", 25.0)
        else:
            set_window_title("🧩 交互 API 与回调组件示例")
            set_text(g_title_id, "🧩 交互 API 与回调组件")
            set_text(g_status_id, "🟢 等待操作：点击按钮测试通用 DLL 命令")
            set_text(g_detail_id, "📌 本批覆盖窗口、元素、弹窗、回调与主题相关命令")
            ui.dll.EU_SetElementColor(g_hwnd, g_title_id, 0x00000000, 0xFF111827)
            ui.dll.EU_SetElementColor(g_hwnd, g_badge_id, 0xFFE0F2FE, 0xFF0369A1)
            set_font(g_title_id, "Microsoft YaHei UI", 22.0)

        current = get_element_text(g_title_id)
        print(f"[文本] 📝 当前标题文本：{current}")

    elif element_id == g_toggle_visible_id:
        g_hidden_visible = not g_hidden_visible
        ui.dll.EU_SetElementVisible(g_hwnd, g_hidden_tip_id, 1 if g_hidden_visible else 0)
        set_text(g_status_id, "👀 隐藏提示已显示" if g_hidden_visible else "🙈 隐藏提示已收起")
        print(f"[可见性] 👀 隐藏提示 visible={g_hidden_visible}")

    elif element_id == g_toggle_enabled_id:
        g_button_enabled = not g_button_enabled
        ui.dll.EU_SetElementEnabled(g_hwnd, g_disabled_button_id, 1 if g_button_enabled else 0)
        set_text(g_status_id, "🔓 禁用按钮已启用" if g_button_enabled else "🔒 禁用按钮已禁用")
        print(f"[启用状态] 🔐 演示按钮 enabled={g_button_enabled}")

    elif element_id == g_move_id:
        g_card_moved = not g_card_moved
        if g_card_moved:
            ui.dll.EU_SetElementBounds(g_hwnd, g_move_card_id, 560, 326, 400, 130)
        else:
            ui.dll.EU_SetElementBounds(g_hwnd, g_move_card_id, 520, 304, 400, 130)
        ok, x, y, w, h = get_element_bounds(g_move_card_id)
        set_text(g_status_id, f"📐 卡片位置：{x}, {y}, {w}, {h}")
        print(f"[元素尺寸] 📐 ok={ok}, x={x}, y={y}, w={w}, h={h}")

    elif element_id == g_message_id:
        edit_text = get_element_text(g_edit_id, editbox=True)
        mid = show_message("💬 消息框", f"编辑框当前内容：{edit_text or '空'}\n支持中文、emoji 和回调。")
        print(f"[消息框] 💬 已显示 #{mid}")

    elif element_id == g_confirm_id:
        mid = show_confirm("❓ 确认框", "是否确认执行这次交互 API 演示？\n按钮文字同样支持 emoji。")
        print(f"[确认框] ❓ 已显示 #{mid}")

    elif element_id == g_bounds_id:
        ok, x, y, w, h = get_window_bounds()
        set_text(g_status_id, f"🪟 窗口：{x}, {y}, {w}, {h}")
        print(f"[窗口尺寸] 🪟 ok={ok}, x={x}, y={y}, w={w}, h={h}")
        ui.dll.EU_SetWindowBounds(g_hwnd, x, y, WINDOW_W, WINDOW_H)

    elif element_id == g_dark_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 1)
        set_text(g_status_id, "🌙 已切换深色主题")
        print("[主题] 🌙 深色")

    elif element_id == g_light_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 0)
        set_text(g_status_id, "☀️ 已切换浅色主题")
        print("[主题] ☀️ 浅色")

    elif element_id == g_system_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 2)
        set_text(g_status_id, f"🖥️ 已切换系统主题，当前模式 {ui.dll.EU_GetThemeMode(g_hwnd)}")
        print("[主题] 🖥️ 系统")

    elif element_id == g_disabled_button_id:
        set_text(g_status_id, "🧪 禁用演示按钮被点击")
        print("[点击] 🧪 禁用演示按钮")


def main():
    global g_hwnd, g_title_id, g_status_id, g_detail_id, g_edit_id, g_badge_id
    global g_move_card_id, g_hidden_tip_id, g_disabled_button_id
    global g_update_id, g_toggle_visible_id, g_toggle_enabled_id, g_move_id
    global g_message_id, g_confirm_id, g_bounds_id, g_dark_id, g_light_id, g_system_id

    hwnd = ui.create_window("🧩 交互 API 与回调组件示例", 210, 70, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    g_title_id = ui.create_text(hwnd, content_id, "🧩 交互 API 与回调组件", 28, 24, 460, 32)
    set_font(g_title_id, "Microsoft YaHei UI", 22.0)
    ui.create_divider(
        hwnd, content_id,
        "💬 弹窗 / 📝 文本 / 📐 位置尺寸 / 👀 可见启用 / 🌗 主题",
        0, 1, 28, 66, 900, 34
    )

    g_status_id = ui.create_infobox(
        hwnd, content_id,
        "📡 当前状态",
        "🟢 等待操作：点击按钮测试通用 DLL 命令",
        28, 116, 430, 92
    )
    g_detail_id = ui.create_infobox(
        hwnd, content_id,
        "🧪 本批范围",
        "📌 覆盖窗口标题、窗口尺寸、元素文本、元素颜色、字体、可见性、启用状态、弹窗和回调。",
        488, 116, 440, 92
    )

    g_edit_id = ui.create_editbox(hwnd, content_id, 28, 238, 430, 40)
    set_text(g_edit_id, "✍️ 可以在这里输入中文和 emoji")
    g_badge_id = ui.create_tag(hwnd, content_id, "🧷 通用属性命令", 0, 1, False, 488, 238, 176, 38)
    ui.dll.EU_SetElementColor(hwnd, g_badge_id, 0xFFE0F2FE, 0xFF0369A1)
    g_disabled_button_id = ui.create_button(hwnd, content_id, "🧪", "启用状态演示", 692, 238, 176, 40)

    ui.create_text(hwnd, content_id, "🎛️ 操作区", 28, 312, 160, 26)
    g_update_id = ui.create_button(hwnd, content_id, "📝", "更新文本样式", 28, 350, 146, 42)
    g_toggle_visible_id = ui.create_button(hwnd, content_id, "👀", "显示/隐藏提示", 190, 350, 154, 42)
    g_toggle_enabled_id = ui.create_button(hwnd, content_id, "🔐", "启用/禁用按钮", 360, 350, 154, 42)
    g_move_id = ui.create_button(hwnd, content_id, "📐", "移动卡片", 28, 410, 146, 42)
    g_message_id = ui.create_button(hwnd, content_id, "💬", "消息框", 190, 410, 154, 42)
    g_confirm_id = ui.create_button(hwnd, content_id, "❓", "确认框", 360, 410, 154, 42)
    g_bounds_id = ui.create_button(hwnd, content_id, "🪟", "读取窗口尺寸", 28, 470, 146, 42)
    g_dark_id = ui.create_button(hwnd, content_id, "🌙", "深色主题", 190, 470, 154, 42)
    g_light_id = ui.create_button(hwnd, content_id, "☀️", "浅色主题", 360, 470, 154, 42)
    g_system_id = ui.create_button(hwnd, content_id, "🖥️", "系统主题", 190, 530, 154, 42)

    g_move_card_id = ui.create_infobox(
        hwnd, content_id,
        "📦 可移动卡片",
        "点击“移动卡片”会调用 EU_SetElementBounds，并用 EU_GetElementBounds 读取结果。",
        520, 304, 400, 130
    )
    g_hidden_tip_id = ui.create_alert(
        hwnd, content_id,
        "👀 隐藏提示",
        "这个提示默认隐藏，通过 EU_SetElementVisible 控制显示。",
        1, 0, False,
        520, 468, 400, 56
    )
    ui.dll.EU_SetElementVisible(hwnd, g_hidden_tip_id, 0)

    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        f"🖥️ 窗口 {WINDOW_W}x{WINDOW_H}，容器 {CONTENT_W}x{CONTENT_H}；内容右边界 920，底边界 674。",
        0, 0, False,
        28, 618, 892, 56
    )

    for eid in (
        g_update_id, g_toggle_visible_id, g_toggle_enabled_id, g_move_id,
        g_message_id, g_confirm_id, g_bounds_id,
        g_dark_id, g_light_id, g_system_id, g_disabled_button_id,
    ):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("🧩 交互 API 与回调组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("🧩 交互 API 与回调组件示例结束。")


if __name__ == "__main__":
    main()
