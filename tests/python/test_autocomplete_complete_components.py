import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_DOWN = 0x28
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B

g_icon_clicks = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Autocomplete 完整组件验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_icon_clicks
    g_icon_clicks += 1
    print(f"[点击] 自动补全尾部图标回调 element={element_id}")


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


def require_equal(name, actual, expected):
    if actual != expected:
        raise RuntimeError(f"{name} 预期 {expected!r}，实际 {actual!r}")


def require_true(name, value):
    if not value:
        raise RuntimeError(f"{name} 预期为真，实际为 {value!r}")


def require_dict(name, actual, expected):
    if actual is None:
        raise RuntimeError(f"{name} 读取失败")
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            raise RuntimeError(f"{name}.{key} 预期 {expected_value!r}，实际 {actual_value!r}")


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


def logical_point(hwnd, x, y):
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    scale = dpi / 96.0 if dpi else 1.0
    titlebar_h = int(round(30 * scale))
    return int(round(x * scale)), titlebar_h + int(round(y * scale))


def click_logical_point(user32, hwnd, x, y):
    px, py = logical_point(hwnd, x, y)
    user32.SendMessageW(hwnd, 0x0201, 0x0001, make_lparam(px, py))
    user32.SendMessageW(hwnd, 0x0202, 0, make_lparam(px, py))


def send_key(user32, hwnd, vk):
    user32.SendMessageW(hwnd, WM_KEYDOWN, vk, 0)
    user32.SendMessageW(hwnd, WM_KEYUP, vk, 0)


def main():
    hwnd = ui.create_window("🔎 Autocomplete 全套能力验证", 240, 80, 1120, 760)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1080, 700)

    ui.create_text(hwnd, content, "🔎 Autocomplete 全套 Element 风格验证", 34, 24, 620, 40)
    intro = ui.create_text(
        hwnd, content,
        "覆盖激活即列出、输入后匹配、双行建议项、尾部图标点击、异步 loading / request_id、空状态和旧 helper 兼容。",
        34, 74, 980, 56,
    )
    ui.set_text_options(hwnd, intro, align=0, valign=0, wrap=True, ellipsis=False)

    focus_auto = ui.create_autocomplete(
        hwnd, content,
        value="",
        suggestions=[
            ("三全鲜食（北新泾店）", "长宁区新渔路144号", "三全鲜食（北新泾店）"),
            ("Hot honey 首尔炸鸡（仙霞路）", "上海市长宁区淞虹路661号", "Hot honey 首尔炸鸡（仙霞路）"),
            ("新旺角茶餐厅", "上海市普陀区真北路988号", "新旺角茶餐厅"),
        ],
        placeholder="请输入餐厅名称",
        trigger_on_focus=True,
        prefix_icon="📍",
        suffix_icon="✏️",
        x=44, y=156, w=460, h=42,
    )
    ui.dll.EU_SetElementClickCallback(hwnd, focus_auto, on_click)

    delayed_auto = ui.create_autocomplete(
        hwnd, content,
        value="",
        suggestions=["北京", "上海", "广州", "深圳"],
        placeholder="输入后再匹配",
        trigger_on_focus=False,
        prefix_icon="🔍",
        x=44, y=252, w=460, h=42,
    )

    async_auto = ui.create_autocomplete(
        hwnd, content,
        value="",
        suggestions=[],
        placeholder="异步建议列表",
        trigger_on_focus=False,
        suffix_icon="🛰️",
        x=44, y=348, w=460, h=42,
    )

    legacy_auto = ui.create_autocomplete(
        hwnd, content,
        "北",
        ["北京", "北海", "北戴河"],
        44, 444, 320, 42,
    )

    panel = ui.create_panel(hwnd, content, 560, 150, 430, 288)
    ui.set_panel_style(hwnd, panel, 0x102563EB, 0x552563EB, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel, "📊 读回检查", 0, 0, 180, 30)
    note = ui.create_text(
        hwnd, panel,
        "窗口显示后会自动走一遍键盘上下选择、回车写回、ESC 关闭、异步 loading 和空状态流程。",
        0, 46, 346, 118,
    )
    ui.set_text_options(hwnd, note, align=0, valign=0, wrap=True, ellipsis=False)

    require_equal("聚焦输入框 placeholder", ui.get_autocomplete_placeholder(hwnd, focus_auto), "请输入餐厅名称")
    require_equal("聚焦输入框 icons", ui.get_autocomplete_icons(hwnd, focus_auto), ("📍", "✏️"))
    require_dict("trigger_on_focus 默认开启", ui.get_autocomplete_behavior_options(hwnd, focus_auto), {"trigger_on_focus": True})
    require_dict("trigger_on_focus 关闭", ui.get_autocomplete_behavior_options(hwnd, delayed_auto), {"trigger_on_focus": False})
    require_equal("旧 helper 建议数量", ui.get_autocomplete_suggestion_count(hwnd, legacy_auto), 3)

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.35)

    ui.dll.EU_SetElementFocus(hwnd, focus_auto)
    pump_messages(user32, msg, 0.35)
    require_equal("激活即列出 open", ui.get_autocomplete_options(hwnd, focus_auto)["open"], 1)
    require_equal("激活即列出 count", ui.get_autocomplete_options(hwnd, focus_auto)["count"], 3)

    send_key(user32, hwnd, VK_DOWN)
    send_key(user32, hwnd, VK_DOWN)
    pump_messages(user32, msg, 0.2)
    require_equal("键盘选中索引", ui.get_autocomplete_selected(hwnd, focus_auto), 2)
    send_key(user32, hwnd, VK_RETURN)
    pump_messages(user32, msg, 0.25)
    require_equal("回车写回值", ui.get_autocomplete_value(hwnd, focus_auto), "新旺角茶餐厅")

    ui.set_autocomplete_open(hwnd, focus_auto, True)
    pump_messages(user32, msg, 0.15)
    send_key(user32, hwnd, VK_ESCAPE)
    pump_messages(user32, msg, 0.2)
    require_equal("ESC 关闭下拉", ui.get_autocomplete_open(hwnd, focus_auto), 0)

    ui.dll.EU_SetElementFocus(hwnd, delayed_auto)
    pump_messages(user32, msg, 0.3)
    require_equal("关闭焦点触发后不自动展开", ui.get_autocomplete_open(hwnd, delayed_auto), 0)

    ui.set_autocomplete_async_state(hwnd, async_auto, True, 20260504)
    require_dict(
        "异步 loading 状态",
        ui.get_autocomplete_options(hwnd, async_auto),
        {"loading": 1, "request_id": 20260504},
    )
    ui.set_autocomplete_empty_text(hwnd, async_auto, "🫥 没有找到匹配餐厅")
    ui.set_autocomplete_open(hwnd, async_auto, True)
    pump_messages(user32, msg, 0.2)
    require_equal("空状态建议数", ui.get_autocomplete_options(hwnd, async_auto)["count"], 0)

    ui.set_autocomplete_suggestions(
        hwnd, async_auto,
        [
            ("Merci Paul cafe", "上海市普陀区光复西路丹巴路28弄", "Merci Paul cafe"),
            ("猫山王（西郊百联店）", "上海市长宁区仙霞西路88号", "猫山王（西郊百联店）"),
        ],
    )
    ui.set_autocomplete_async_state(hwnd, async_auto, False, 20260505)
    ui.set_autocomplete_open(hwnd, async_auto, True)
    ui.set_autocomplete_selected(hwnd, async_auto, 0)
    pump_messages(user32, msg, 0.2)
    require_dict(
        "异步结果状态",
        ui.get_autocomplete_options(hwnd, async_auto),
        {"count": 2, "loading": 0, "request_id": 20260505, "selected": 0},
    )

    click_logical_point(user32, hwnd, 44 + 460 - 18, 156 + 21)
    pump_messages(user32, msg, 0.2)
    require_true("尾部图标点击回调", g_icon_clicks >= 1)

    print("[读取] focus:", ui.get_autocomplete_options(hwnd, focus_auto), ui.get_autocomplete_icons(hwnd, focus_auto))
    print("[读取] delayed:", ui.get_autocomplete_options(hwnd, delayed_auto), ui.get_autocomplete_behavior_options(hwnd, delayed_auto))
    print("[读取] async:", ui.get_autocomplete_options(hwnd, async_auto))
    print("[提示] 窗口将保持 8 秒，可检查中文、emoji、双行建议项、异步 loading 和空状态外观。")

    pump_messages(user32, msg, 8.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
