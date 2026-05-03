import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_clicks = []
g_changes = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Checkbox 完整组件验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    g_clicks.append(element_id)
    print(f"[复选点击回调] 元素={element_id}")


@ui.ValueCallback
def on_group_change(element_id, value, count, action):
    g_changes.append((element_id, value, count, action))
    print(f"[复选组变更] 元素={element_id} 索引={value} 已选={count} 动作={action}")


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


def require_equal(name, actual, expected):
    if actual != expected:
        raise RuntimeError(f"{name} 预期 {expected!r}，实际 {actual!r}")


def require_list(name, actual, expected):
    if actual != expected:
        raise RuntimeError(f"{name} 预期 {expected!r}，实际 {actual!r}")


def require_dict(name, actual, expected):
    if actual is None:
        raise RuntimeError(f"{name} 读回失败")
    for key, value in expected.items():
        if actual[key] != value:
            raise RuntimeError(f"{name}.{key} 预期 {value!r}，实际 {actual[key]!r}")


def main():
    hwnd = ui.create_window("☑️ Checkbox 复选完整组件验证", 220, 80, 1200, 780)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1160, 720)

    ui.create_text(hwnd, content, "☑️ Checkbox 复选完整封装", 34, 26, 560, 40)
    intro = ui.create_text(
        hwnd, content,
        "验证普通复选、禁用、半选、边框、尺寸、CheckboxGroup、CheckboxButton、min/max、鼠标和键盘交互。",
        34, 76, 1020, 54,
    )
    ui.set_text_options(hwnd, intro, align=0, valign=0, wrap=True, ellipsis=False)

    base = ui.create_checkbox(hwnd, content, "普通复选 ✅", True, 50, 150, 160, 34)
    border = ui.create_checkbox(hwnd, content, "边框中等 📦", False, 230, 146, 170, 40,
                                border=True, size=1)
    partial = ui.create_checkbox(hwnd, content, "半选状态 🌗", False, 430, 150, 170, 34)
    disabled = ui.create_checkbox(hwnd, content, "禁用复选 🔒", True, 620, 150, 170, 34)
    ui.dll.EU_SetCheckboxIndeterminate(hwnd, partial, 1)
    ui.set_element_enabled(hwnd, disabled, False)
    ui.dll.EU_SetElementClickCallback(hwnd, base, on_click)

    require_equal("Base checked", ui.dll.EU_GetCheckboxChecked(hwnd, base), 1)
    require_equal("Partial indeterminate", ui.dll.EU_GetCheckboxIndeterminate(hwnd, partial), 1)
    require_dict("Checkbox options", ui.get_checkbox_options(hwnd, border), {"border": True, "size": 1})

    items = [
        ("上海 🏙️", "上海", False),
        ("北京 🔒", "北京", True),
        ("广州 🌿", "广州", False),
        ("深圳 🚀", "深圳", False),
    ]
    normal_group = ui.create_checkbox_group(
        hwnd, content, items, ["上海", "广州"], style=0, size=0,
        x=50, y=230, w=640, h=44,
    )
    limited_group = ui.create_checkbox_group(
        hwnd, content, items, ["上海", "广州"], style=0, size=0,
        min_checked=1, max_checked=2, x=50, y=312, w=640, h=44,
    )
    button_group = ui.create_checkbox_group(
        hwnd, content, items, ["上海"], style=1, size=2,
        x=50, y=394, w=560, h=36,
    )
    border_group = ui.create_checkbox_group(
        hwnd, content, items, ["深圳"], style=2, size=1,
        x=50, y=476, w=640, h=42,
    )
    disabled_group = ui.create_checkbox_group(
        hwnd, content, items, ["上海"], style=1, size=3, disabled=True,
        x=50, y=558, w=460, h=32,
    )

    for group in (normal_group, limited_group, button_group, border_group, disabled_group):
        ui.dll.EU_SetElementClickCallback(hwnd, group, on_click)
        ui.dll.EU_SetCheckboxGroupChangeCallback(hwnd, group, on_group_change)

    require_list("Normal group value", ui.get_checkbox_group_value(hwnd, normal_group), ["上海", "广州"])
    ui.set_checkbox_group_value(hwnd, normal_group, ["北京"])
    require_list("Programmatic disabled value", ui.get_checkbox_group_value(hwnd, normal_group), ["北京"])
    require_dict("Button group options", ui.get_checkbox_group_options(hwnd, button_group),
                 {"disabled": False, "style": 1, "size": 2, "min_checked": 0, "max_checked": 0})
    require_dict("Limited group options", ui.get_checkbox_group_options(hwnd, limited_group),
                 {"disabled": False, "style": 0, "size": 0, "min_checked": 1, "max_checked": 2})
    require_dict("Border group state", ui.get_checkbox_group_state(hwnd, border_group),
                 {"checked_count": 1, "item_count": 4, "disabled_count": 1, "style": 2, "size": 1})
    require_dict("Disabled group options", ui.get_checkbox_group_options(hwnd, disabled_group),
                 {"disabled": True, "style": 1, "size": 3})

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.25)

    click_logical_rect(user32, hwnd, 50 + 480, 312, 160, 44)
    pump_messages(user32, msg, 0.2)
    require_list("Max limit ignores third check", ui.get_checkbox_group_value(hwnd, limited_group),
                 ["上海", "广州"])
    click_logical_rect(user32, hwnd, 50, 312, 160, 44)
    pump_messages(user32, msg, 0.2)
    require_list("Uncheck to min count", ui.get_checkbox_group_value(hwnd, limited_group), ["广州"])
    click_logical_rect(user32, hwnd, 50 + 320, 312, 160, 44)
    pump_messages(user32, msg, 0.2)
    require_list("Min limit keeps one checked", ui.get_checkbox_group_value(hwnd, limited_group), ["广州"])

    click_logical_rect(user32, hwnd, 50 + 140, 394, 140, 36)
    pump_messages(user32, msg, 0.2)
    require_list("Disabled button item ignored", ui.get_checkbox_group_value(hwnd, button_group), ["上海"])
    click_logical_rect(user32, hwnd, 50 + 420, 394, 140, 36)
    pump_messages(user32, msg, 0.2)
    require_list("Button group mouse value", ui.get_checkbox_group_value(hwnd, button_group), ["上海", "深圳"])
    if not any(change[0] == button_group and change[1] == 3 for change in g_changes):
        raise RuntimeError("CheckboxGroup 变更回调未触发")

    before_disabled = ui.get_checkbox_group_value(hwnd, disabled_group)
    click_logical_rect(user32, hwnd, 50 + 115, 558, 115, 32)
    pump_messages(user32, msg, 0.2)
    require_list("Group disabled click ignored", ui.get_checkbox_group_value(hwnd, disabled_group), before_disabled)

    ui.dll.EU_SetElementFocus(hwnd, normal_group)
    user32.SendMessageW(hwnd, 0x0100, 0x27, 0)  # VK_RIGHT
    user32.SendMessageW(hwnd, 0x0101, 0x27, 0)
    user32.SendMessageW(hwnd, 0x0100, 0x20, 0)  # VK_SPACE
    user32.SendMessageW(hwnd, 0x0101, 0x20, 0)
    pump_messages(user32, msg, 0.25)
    require_list("Keyboard toggles focused item", ui.get_checkbox_group_value(hwnd, normal_group), ["北京", "广州"])

    ui.set_checkbox_group_items(hwnd, border_group, [
        ("权限 A 🧩", "A", False),
        ("权限 B 🔒", "B", True),
        ("权限 C ✅", "C", False),
    ])
    ui.set_checkbox_group_value(hwnd, border_group, ["A", "C"])
    require_list("Updated border group value", ui.get_checkbox_group_value(hwnd, border_group), ["A", "C"])

    print("[提示] 窗口将保持 8 秒，可检查中文、emoji、普通/按钮/边框/禁用/尺寸 Checkbox 样式。")
    pump_messages(user32, msg, 8.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
