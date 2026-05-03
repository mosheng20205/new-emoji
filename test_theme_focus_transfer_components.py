import ctypes
from ctypes import wintypes
import sys
import time

import test_new_emoji as ui

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WINDOW_W = 1060
WINDOW_H = 760
CONTENT_W = 1030
CONTENT_H = 710

KeyCallback = ctypes.WINFUNCTYPE(
    None,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
)

ui.dll.EU_CreateWindowDark.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint32,
]
ui.dll.EU_CreateWindowDark.restype = wintypes.HWND
ui.dll.EU_SetButtonEmoji.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]
ui.dll.EU_SetButtonEmoji.restype = None
ui.dll.EU_SetElementFocus.argtypes = [wintypes.HWND, ctypes.c_int]
ui.dll.EU_SetElementFocus.restype = None
ui.dll.EU_InvalidateElement.argtypes = [wintypes.HWND, ctypes.c_int]
ui.dll.EU_InvalidateElement.restype = None
ui.dll.EU_SetDarkMode.argtypes = [wintypes.HWND, ctypes.c_int]
ui.dll.EU_SetDarkMode.restype = None
ui.dll.EU_SetThemeColor.argtypes = [wintypes.HWND, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_uint32]
ui.dll.EU_SetThemeColor.restype = ctypes.c_int
ui.dll.EU_ResetTheme.argtypes = [wintypes.HWND]
ui.dll.EU_ResetTheme.restype = None
ui.dll.EU_SetElementKeyCallback.argtypes = [wintypes.HWND, ctypes.c_int, KeyCallback]
ui.dll.EU_SetElementKeyCallback.restype = None
ui.dll.EU_TransferMoveRight.argtypes = [wintypes.HWND, ctypes.c_int]
ui.dll.EU_TransferMoveRight.restype = None
ui.dll.EU_TransferMoveLeft.argtypes = [wintypes.HWND, ctypes.c_int]
ui.dll.EU_TransferMoveLeft.restype = None


g_hwnd = None
g_title_id = 0
g_status_id = 0
g_edit_id = 0
g_transfer_id = 0
g_emoji_button_id = 0
g_focus_id = 0
g_refresh_id = 0
g_accent_id = 0
g_reset_theme_id = 0
g_dark_mode_id = 0
g_light_mode_id = 0
g_move_right_id = 0
g_move_left_id = 0
g_emoji_index = 0
g_accent_flip = False

EMOJIS = ["🚀", "🎯", "✨", "🧠", "🌈"]


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


def create_dark_window(title: str, x: int, y: int, w: int, h: int):
    data, length = utf8_arg(title)
    return ui.dll.EU_CreateWindowDark(data, length, x, y, w, h, 0xFF181825)


def set_text(element_id: int, text: str):
    data, length = utf8_arg(text)
    ui.dll.EU_SetElementText(g_hwnd, element_id, data, length)


def set_button_emoji(element_id: int, emoji: str):
    data, length = utf8_arg(emoji)
    ui.dll.EU_SetButtonEmoji(g_hwnd, element_id, data, length)


def set_theme_color(token: str, value: int):
    data, length = utf8_arg(token)
    return ui.dll.EU_SetThemeColor(g_hwnd, data, length, value)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 🌗 主题焦点穿梭组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] 🪟 宽 {width}，高 {height}")


@KeyCallback
def on_key(element_id, vk_code, key_down, shift, ctrl, alt):
    action = "按下" if key_down else "松开"
    mods = []
    if shift:
        mods.append("Shift")
    if ctrl:
        mods.append("Ctrl")
    if alt:
        mods.append("Alt")
    mod_text = "+".join(mods) if mods else "无组合键"
    set_text(g_status_id, f"⌨️ 元素 {element_id}：{action} VK={vk_code}，{mod_text}")
    print(f"[键盘] ⌨️ element={element_id}, vk={vk_code}, down={key_down}, mods={mod_text}")


@ui.ClickCallback
def on_click(element_id):
    global g_emoji_index, g_accent_flip

    if element_id == g_emoji_button_id:
        g_emoji_index = (g_emoji_index + 1) % len(EMOJIS)
        emoji = EMOJIS[g_emoji_index]
        set_button_emoji(g_emoji_button_id, emoji)
        set_text(g_status_id, f"{emoji} 已通过 EU_SetButtonEmoji 替换按钮表情")
        print(f"[按钮表情] {emoji}")

    elif element_id == g_focus_id:
        ui.dll.EU_SetElementFocus(g_hwnd, g_edit_id)
        set_text(g_status_id, "🎯 已把焦点设置到编辑框，请直接按键测试键盘回调")
        print("[焦点] 🎯 已设置到编辑框")

    elif element_id == g_refresh_id:
        ui.dll.EU_InvalidateElement(g_hwnd, g_title_id)
        ui.dll.EU_InvalidateElement(g_hwnd, g_transfer_id)
        set_text(g_status_id, "🔄 已手动刷新标题和穿梭框")
        print("[刷新] 🔄 已调用 EU_InvalidateElement")

    elif element_id == g_accent_id:
        g_accent_flip = not g_accent_flip
        accent = 0xFFFF6B6B if g_accent_flip else 0xFF22C55E
        button_bg = 0xFF7F1D1D if g_accent_flip else 0xFF14532D
        ok1 = set_theme_color("accent", accent)
        ok2 = set_theme_color("button_bg", button_bg)
        set_text(g_status_id, f"🎨 已设置主题颜色：accent={ok1}，button_bg={ok2}")
        print(f"[主题颜色] 🎨 accent_ok={ok1}, button_ok={ok2}")

    elif element_id == g_reset_theme_id:
        ui.dll.EU_ResetTheme(g_hwnd)
        set_text(g_status_id, "♻️ 已重置自定义主题颜色")
        print("[主题] ♻️ 已重置")

    elif element_id == g_dark_mode_id:
        ui.dll.EU_SetDarkMode(g_hwnd, 1)
        set_text(g_status_id, "🌙 已通过 EU_SetDarkMode 切换深色")
        print("[主题] 🌙 深色")

    elif element_id == g_light_mode_id:
        ui.dll.EU_SetDarkMode(g_hwnd, 0)
        set_text(g_status_id, "☀️ 已通过 EU_SetDarkMode 切换浅色")
        print("[主题] ☀️ 浅色")

    elif element_id == g_move_right_id:
        ui.dll.EU_TransferMoveRight(g_hwnd, g_transfer_id)
        set_text(g_status_id, "➡️ 已调用 EU_TransferMoveRight")
        print("[穿梭框] ➡️ 右移")

    elif element_id == g_move_left_id:
        ui.dll.EU_TransferMoveLeft(g_hwnd, g_transfer_id)
        set_text(g_status_id, "⬅️ 已调用 EU_TransferMoveLeft")
        print("[穿梭框] ⬅️ 左移")


def main():
    global g_hwnd, g_title_id, g_status_id, g_edit_id, g_transfer_id
    global g_emoji_button_id, g_focus_id, g_refresh_id, g_accent_id, g_reset_theme_id
    global g_dark_mode_id, g_light_mode_id, g_move_right_id, g_move_left_id

    hwnd = create_dark_window("🌗 主题焦点穿梭组件示例", 200, 70, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    g_title_id = ui.create_text(hwnd, content_id, "🌗 主题焦点与穿梭操作", 28, 24, 420, 32)
    ui.create_divider(
        hwnd, content_id,
        "🎨 主题 token / 🎯 焦点 / ⌨️ 键盘回调 / 🔄 手动刷新 / 🔀 穿梭框移动",
        0, 1, 28, 66, 930, 34
    )

    g_status_id = ui.create_infobox(
        hwnd, content_id,
        "📡 当前状态",
        "🌙 深色窗口已创建，请点击按钮测试剩余通用命令。",
        28, 116, 440, 90
    )
    ui.create_infobox(
        hwnd, content_id,
        "🧪 本批覆盖",
        "CreateWindowDark、SetButtonEmoji、SetElementFocus、SetDarkMode、SetThemeColor、ResetTheme、InvalidateElement、TransferMove。",
        500, 116, 460, 90
    )

    ui.create_text(hwnd, content_id, "⌨️ 焦点与键盘回调", 28, 238, 220, 26)
    g_edit_id = ui.create_editbox(hwnd, content_id, 28, 276, 440, 42)
    set_text(g_edit_id, "🎯 点击“设置焦点”后在这里输入")
    ui.dll.EU_SetElementKeyCallback(hwnd, g_edit_id, on_key)

    g_emoji_button_id = ui.create_button(hwnd, content_id, "🚀", "替换按钮表情", 28, 348, 150, 42)
    g_focus_id = ui.create_button(hwnd, content_id, "🎯", "设置焦点", 194, 348, 128, 42)
    g_refresh_id = ui.create_button(hwnd, content_id, "🔄", "手动刷新", 338, 348, 130, 42)

    ui.create_text(hwnd, content_id, "🎨 主题命令", 28, 424, 180, 26)
    g_accent_id = ui.create_button(hwnd, content_id, "🌈", "切换主题色", 28, 462, 140, 42)
    g_reset_theme_id = ui.create_button(hwnd, content_id, "♻️", "重置主题", 184, 462, 130, 42)
    g_dark_mode_id = ui.create_button(hwnd, content_id, "🌙", "深色模式", 330, 462, 138, 42)
    g_light_mode_id = ui.create_button(hwnd, content_id, "☀️", "浅色模式", 28, 522, 140, 42)

    ui.create_text(hwnd, content_id, "🔀 穿梭框命令", 500, 238, 200, 26)
    g_transfer_id = ui.create_transfer(
        hwnd, content_id,
        ["🧩 待办组件", "🎨 主题令牌", "⌨️ 键盘事件", "🔄 重绘请求"],
        ["✅ 已完成示例"],
        500, 276, 460, 206
    )
    g_move_right_id = ui.create_button(hwnd, content_id, "➡️", "移到右侧", 500, 512, 132, 42)
    g_move_left_id = ui.create_button(hwnd, content_id, "⬅️", "移回左侧", 648, 512, 132, 42)

    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        f"🖥️ 窗口 {WINDOW_W}x{WINDOW_H}，容器 {CONTENT_W}x{CONTENT_H}；内容右边界 960，底边界 674。",
        0, 0, False,
        28, 618, 932, 56
    )

    for eid in (
        g_emoji_button_id, g_focus_id, g_refresh_id, g_accent_id, g_reset_theme_id,
        g_dark_mode_id, g_light_mode_id, g_move_right_id, g_move_left_id,
    ):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("🌗 主题焦点穿梭组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("🌗 主题焦点穿梭组件示例结束。")


if __name__ == "__main__":
    main()
