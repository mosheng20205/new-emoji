import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_clicks = []
g_changes = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Radio 完整组件验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    g_clicks.append(element_id)
    print(f"[单选点击回调] 元素={element_id}")


@ui.ValueCallback
def on_group_change(element_id, value, count, action):
    g_changes.append((element_id, value, count, action))
    print(f"[单选组变更] 元素={element_id} 选中索引={value} 数量={count} 动作={action}")


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


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


def logical_point(hwnd, x, y):
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    scale = dpi / 96.0 if dpi else 1.0
    titlebar_h = int(round(30 * scale))
    return int(round(x * scale)), titlebar_h + int(round(y * scale))


def click_logical_rect(user32, hwnd, x, y, w, h):
    px, py = logical_point(hwnd, x + w / 2.0, y + h / 2.0)
    user32.SendMessageW(hwnd, 0x0201, 0x0001, make_lparam(px, py))
    user32.SendMessageW(hwnd, 0x0202, 0, make_lparam(px, py))


def move_logical(user32, hwnd, x, y):
    px, py = logical_point(hwnd, x, y)
    user32.SendMessageW(hwnd, 0x0200, 0, make_lparam(px, py))


def require_equal(name, actual, expected):
    if actual != expected:
        raise RuntimeError(f"{name} 预期 {expected!r}，实际 {actual!r}")


def require_dict(name, actual, expected):
    if actual is None:
        raise RuntimeError(f"{name} 读回失败")
    for key, value in expected.items():
        if actual[key] != value:
            raise RuntimeError(f"{name}.{key} 预期 {value!r}，实际 {actual[key]!r}")


def main():
    hwnd = ui.create_window("🔘 Radio 单选完整组件验证", 220, 80, 1180, 780)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1140, 720)

    ui.create_text(hwnd, content, "🔘 Radio 单选完整封装", 34, 26, 520, 40)
    intro = ui.create_text(
        hwnd, content,
        "验证普通单选、value/label、border、size、原生 RadioGroup、按钮样式、整组禁用、单项禁用、鼠标与键盘交互。",
        34, 76, 980, 54,
    )
    ui.set_text_options(hwnd, intro, align=0, valign=0, wrap=True, ellipsis=False)

    radio_a = ui.create_radio(hwnd, content, "方案 A 🚀", True, 50, 150, 150, 34, value="A")
    radio_b = ui.create_radio(hwnd, content, "方案 B ✨", False, 220, 150, 150, 34, value="B")
    ui.set_radio_group(hwnd, radio_a, "方案")
    ui.set_radio_group(hwnd, radio_b, "方案")
    ui.dll.EU_SetElementClickCallback(hwnd, radio_a, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, radio_b, on_click)
    ui.set_radio_options(hwnd, radio_b, border=True, size=1)

    require_equal("Radio value A", ui.get_radio_value(hwnd, radio_a), "A")
    require_equal("Radio value B", ui.get_radio_value(hwnd, radio_b), "B")
    require_equal("Radio group", ui.get_radio_group(hwnd, radio_a), "方案")
    require_dict("Radio options", ui.get_radio_options(hwnd, radio_b), {"border": True, "size": 1})
    require_equal("Radio checked A", ui.dll.EU_GetRadioChecked(hwnd, radio_a), 1)

    border_radio = ui.create_radio(hwnd, content, "边框小尺寸 📦", True, 410, 146, 170, 40,
                                   value="border", border=True, size=2)
    require_dict("Border radio options", ui.get_radio_options(hwnd, border_radio), {"border": True, "size": 2})

    normal_group = ui.create_radio_group(
        hwnd, content,
        [("上海 🏙️", "上海", False), ("北京 🏛️", "北京", False), ("广州 🌆", "广州", False)],
        value="北京", style=0, size=0, x=50, y=230, w=560, h=44,
    )
    button_group = ui.create_radio_group(
        hwnd, content,
        [("上海", "上海", False), ("北京", "北京", True), ("广州", "广州", False), ("深圳", "深圳", False)],
        value="上海", style=1, size=2, x=50, y=318, w=520, h=36,
    )
    border_group = ui.create_radio_group(
        hwnd, content,
        [("备选 1 📌", "1", False), ("备选 2 📎", "2", True), ("备选 3 ✅", "3", False)],
        value="1", style=2, size=1, x=50, y=410, w=560, h=42,
    )
    disabled_group = ui.create_radio_group(
        hwnd, content,
        [("上海", "上海", False), ("北京", "北京", False), ("广州", "广州", False)],
        value="上海", style=1, size=3, disabled=True, x=50, y=502, w=420, h=32,
    )
    for group in (normal_group, button_group, border_group, disabled_group):
        ui.dll.EU_SetElementClickCallback(hwnd, group, on_click)
        ui.dll.EU_SetRadioGroupChangeCallback(hwnd, group, on_group_change)

    require_equal("Normal group value", ui.get_radio_group_value(hwnd, normal_group), "北京")
    require_equal("Normal group index", ui.get_radio_group_selected_index(hwnd, normal_group), 1)
    require_dict("Button group options", ui.get_radio_group_options(hwnd, button_group),
                 {"disabled": False, "style": 1, "size": 2})
    require_dict("Border group options", ui.get_radio_group_options(hwnd, border_group),
                 {"disabled": False, "style": 2, "size": 1})
    require_dict("Disabled group options", ui.get_radio_group_options(hwnd, disabled_group),
                 {"disabled": True, "style": 1, "size": 3})
    require_dict("Button group state", ui.get_radio_group_state(hwnd, button_group),
                 {"selected_index": 0, "item_count": 4, "disabled_count": 1, "style": 1, "size": 2})

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.25)

    click_logical_rect(user32, hwnd, 220, 150, 150, 34)
    pump_messages(user32, msg, 0.25)
    require_equal("Radio checked B after mouse", ui.dll.EU_GetRadioChecked(hwnd, radio_b), 1)
    require_equal("Radio checked A after mouse", ui.dll.EU_GetRadioChecked(hwnd, radio_a), 0)
    if radio_b not in g_clicks:
        raise RuntimeError("普通 Radio 鼠标点击回调未触发")

    move_logical(user32, hwnd, 50 + 520 * 0.625, 336)
    pump_messages(user32, msg, 0.1)
    click_logical_rect(user32, hwnd, 50 + 130, 318, 130, 36)
    pump_messages(user32, msg, 0.2)
    require_equal("Disabled button group click ignored", ui.get_radio_group_value(hwnd, button_group), "上海")

    click_logical_rect(user32, hwnd, 50 + 390, 318, 130, 36)
    pump_messages(user32, msg, 0.25)
    require_equal("Button group mouse value", ui.get_radio_group_value(hwnd, button_group), "深圳")
    if not any(change[0] == button_group and change[1] == 3 for change in g_changes):
        raise RuntimeError("RadioGroup 变更回调未触发")

    before_disabled = ui.get_radio_group_value(hwnd, disabled_group)
    click_logical_rect(user32, hwnd, 50 + 140, 502, 140, 32)
    pump_messages(user32, msg, 0.2)
    require_equal("Group disabled click ignored", ui.get_radio_group_value(hwnd, disabled_group), before_disabled)

    ui.dll.EU_SetElementFocus(hwnd, normal_group)
    user32.SendMessageW(hwnd, 0x0100, 0x27, 0)  # VK_RIGHT
    user32.SendMessageW(hwnd, 0x0101, 0x27, 0)
    pump_messages(user32, msg, 0.25)
    require_equal("Normal group keyboard value", ui.get_radio_group_value(hwnd, normal_group), "广州")
    user32.SendMessageW(hwnd, 0x0100, 0x24, 0)  # VK_HOME
    user32.SendMessageW(hwnd, 0x0101, 0x24, 0)
    pump_messages(user32, msg, 0.25)
    require_equal("Normal group Home value", ui.get_radio_group_value(hwnd, normal_group), "上海")

    ui.set_radio_group_value(hwnd, border_group, "3")
    require_equal("Border group set value", ui.get_radio_group_value(hwnd, border_group), "3")
    state = ui.get_radio_group_state(hwnd, border_group)
    require_equal("Border group selected index", state["selected_index"], 2)

    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、普通/按钮/边框/禁用/尺寸 Radio 样式。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
