import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_MOUSEMOVE = 0x0200
VK_CONTROL = 0x11


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Input 完整组件验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


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


def get_bounds(hwnd, element_id):
    x = ctypes.c_int()
    y = ctypes.c_int()
    w = ctypes.c_int()
    h = ctypes.c_int()
    ok = ui.dll.EU_GetElementBounds(
        hwnd, element_id,
        ctypes.byref(x), ctypes.byref(y), ctypes.byref(w), ctypes.byref(h),
    )
    if not ok:
        raise RuntimeError(f"元素 {element_id} 读取 bounds 失败")
    return (x.value, y.value, w.value, h.value)


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


def click_input_right_affix(user32, hwnd, x, y, w, h, offset=18):
    click_logical_point(user32, hwnd, x + w - offset, y + h / 2.0)


def drag_logical(user32, hwnd, x1, y1, x2, y2):
    px1, py1 = logical_point(hwnd, x1, y1)
    px2, py2 = logical_point(hwnd, x2, y2)
    user32.SendMessageW(hwnd, 0x0201, 0x0001, make_lparam(px1, py1))
    user32.SendMessageW(hwnd, WM_MOUSEMOVE, 0x0001, make_lparam(px2, py2))
    user32.SendMessageW(hwnd, 0x0202, 0, make_lparam(px2, py2))


def main():
    hwnd = ui.create_window("📝 Input 全套能力验证", 220, 70, 1260, 860)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1220, 800)

    ui.create_text(hwnd, content, "📝 Input 全套 Element 风格验证", 34, 24, 560, 40)
    intro = ui.create_text(
        hwnd, content,
        "覆盖基础/禁用/clearable/密码显隐/图标/textarea/autosize/字数统计/四尺寸，"
        "同时保留旧 create_input 调用方式作为兼容验证。",
        34, 74, 1080, 56,
    )
    ui.set_text_options(hwnd, intro, align=0, valign=0, wrap=True, ellipsis=False)

    legacy_input = ui.create_input(
        hwnd, content,
        "旧 helper 兼容", "请输入昵称", "👤", "旧版", True,
        44, 152, 320, 42,
    )
    disabled_input = ui.create_input(
        hwnd, content,
        value="禁用状态", placeholder="不可编辑",
        prefix="🔒", suffix="禁用", clearable=False,
        x=392, y=152, w=300, h=42,
    )
    ui.set_element_enabled(hwnd, disabled_input, False)

    clearable_input = ui.create_input(
        hwnd, content,
        value="可清空内容", placeholder="点击右侧清空",
        prefix="🧹", suffix="清空", clearable=True,
        x=720, y=152, w=380, h=42,
    )

    icons_input = ui.create_input(
        hwnd, content,
        value="", placeholder="前后图标输入框",
        size=1, prefix_icon="📅", suffix_icon="🔎",
        x=44, y=244, w=320, h=40,
    )
    password_input = ui.create_input(
        hwnd, content,
        value="abc123", placeholder="请输入密码",
        prefix_icon="🔐",
        password=True, show_password=True, clearable=True,
        x=392, y=244, w=320, h=40,
    )
    multiline_input = ui.create_input(
        hwnd, content,
        value="第 1 行", placeholder="请输入多行内容 ✨",
        prefix="📝", suffix="备注",
        clearable=True, multiline=True,
        show_word_limit=True, autosize=True,
        min_rows=2, max_rows=4, max_length=30,
        x=44, y=336, w=668, h=64,
    )

    ui.create_text(hwnd, content, "📏 四尺寸", 44, 448, 180, 28)
    size_default = ui.create_input(
        hwnd, content, placeholder="default", suffix_icon="📎",
        size=0, x=44, y=486, w=240, h=42,
    )
    size_medium = ui.create_input(
        hwnd, content, placeholder="medium", suffix_icon="📎",
        size=1, x=304, y=486, w=240, h=40,
    )
    size_small = ui.create_input(
        hwnd, content, placeholder="small", suffix_icon="📎",
        size=2, x=564, y=486, w=240, h=36,
    )
    size_mini = ui.create_input(
        hwnd, content, placeholder="mini", suffix_icon="📎",
        size=3, x=824, y=486, w=240, h=32,
    )

    panel = ui.create_panel(hwnd, content, 748, 252, 364, 234)
    ui.set_panel_style(hwnd, panel, 0x102563EB, 0x552563EB, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel, "📊 读回检查", 0, 0, 180, 30)
    note = ui.create_text(
        hwnd, panel,
        "窗口显示后会自动检查 clearable、密码显隐、图标、字数统计与 autosize 高度变化。",
        0, 46, 286, 106,
    )
    ui.set_text_options(hwnd, note, align=0, valign=0, wrap=True, ellipsis=False)

    require_equal("旧 helper 值", ui.get_input_value(hwnd, legacy_input), "旧 helper 兼容")
    require_equal("旧 helper clearable", ui.get_input_state(hwnd, legacy_input)[2], True)
    require_true("禁用输入框", not ui.get_element_enabled(hwnd, disabled_input))
    require_dict("图标输入框视觉", ui.get_input_visual_options(hwnd, icons_input), {"size": 1})
    require_equal("图标输入框图标", ui.get_input_icons(hwnd, icons_input), ("📅", "🔎"))
    require_equal("密码输入框密码态", ui.get_input_state(hwnd, password_input)[4], True)
    require_dict(
        "密码输入框视觉",
        ui.get_input_visual_options(hwnd, password_input),
        {"show_password_toggle": True},
    )
    require_equal("密码输入框图标", ui.get_input_icons(hwnd, password_input), ("🔐", ""))
    require_equal("多行输入框 multiline", ui.get_input_state(hwnd, multiline_input)[5], True)
    require_equal("多行输入框 maxlength", ui.get_input_max_length(hwnd, multiline_input), 30)
    require_dict(
        "多行输入框视觉",
        ui.get_input_visual_options(hwnd, multiline_input),
        {"show_word_limit": True, "autosize": True, "min_rows": 2, "max_rows": 4},
    )
    require_dict("default 尺寸", ui.get_input_visual_options(hwnd, size_default), {"size": 0})
    require_dict("medium 尺寸", ui.get_input_visual_options(hwnd, size_medium), {"size": 1})
    require_dict("small 尺寸", ui.get_input_visual_options(hwnd, size_small), {"size": 2})
    require_dict("mini 尺寸", ui.get_input_visual_options(hwnd, size_mini), {"size": 3})

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.35)

    require_equal("context menu default", ui.get_input_context_menu_enabled(hwnd, legacy_input), True)
    ui.set_input_context_menu_enabled(hwnd, legacy_input, False)
    require_equal("context menu disabled", ui.get_input_context_menu_enabled(hwnd, legacy_input), False)
    ui.set_input_context_menu_enabled(hwnd, legacy_input, True)

    ui.dll.EU_SetElementFocus(hwnd, legacy_input)
    pump_messages(user32, msg, 0.15)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    pump_messages(user32, msg, 0.05)
    user32.PostMessageW(hwnd, WM_KEYDOWN, ord("A"), 0)
    user32.PostMessageW(hwnd, WM_KEYUP, ord("A"), 0)
    pump_messages(user32, msg, 0.05)
    user32.keybd_event(VK_CONTROL, 0, 2, 0)
    pump_messages(user32, msg, 0.2)
    require_equal("Ctrl+A selection", ui.get_input_selection(hwnd, legacy_input),
                  (0, len(ui.get_input_value(hwnd, legacy_input))))

    ui.set_input_selection(hwnd, legacy_input, 0, 0)
    drag_logical(user32, hwnd, 52, 173, 180, 173)
    pump_messages(user32, msg, 0.2)
    drag_start, drag_end = ui.get_input_selection(hwnd, legacy_input)
    require_true("mouse drag selection", drag_end > drag_start)

    before_height = get_bounds(hwnd, multiline_input)[3]
    ui.set_input_value(hwnd, multiline_input, "第 1 行\n第 2 行\n第 3 行\n第 4 行")
    pump_messages(user32, msg, 0.35)
    after_height = get_bounds(hwnd, multiline_input)[3]
    require_true("autosize 高度增长", after_height >= before_height)

    click_input_right_affix(user32, hwnd, 720, 152, 380, 42, offset=18)
    pump_messages(user32, msg, 0.25)
    require_equal("clearable 清空结果", ui.get_input_value(hwnd, clearable_input), "")

    ui.dll.EU_SetElementFocus(hwnd, legacy_input)
    pump_messages(user32, msg, 0.15)
    user32.SendMessageW(hwnd, WM_KEYDOWN, 0x09, 0)
    user32.SendMessageW(hwnd, WM_KEYUP, 0x09, 0)
    pump_messages(user32, msg, 0.2)

    print("[读取] 旧 helper:", ui.get_input_value(hwnd, legacy_input), ui.get_input_state(hwnd, legacy_input))
    print("[读取] 图标:", ui.get_input_icons(hwnd, icons_input), ui.get_input_visual_options(hwnd, icons_input))
    print("[读取] 密码:", ui.get_input_state(hwnd, password_input), ui.get_input_visual_options(hwnd, password_input))
    print("[读取] 多行:", ui.get_input_state(hwnd, multiline_input), ui.get_input_visual_options(hwnd, multiline_input))
    print("[提示] 窗口将保持 8 秒，可检查中文、emoji、clearable、密码显隐、字数统计与四尺寸外观。")

    pump_messages(user32, msg, 8.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
