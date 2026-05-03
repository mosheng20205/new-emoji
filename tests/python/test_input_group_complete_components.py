import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_button_clicks = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] InputGroup 完整组件验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_button_clicks
    g_button_clicks += 1
    print(f"[点击] InputGroup 附加按钮回调 element={element_id}")


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


def click_logical_rect(user32, hwnd, x, y, w, h):
    px, py = logical_point(hwnd, x + w / 2.0, y + h / 2.0)
    user32.SendMessageW(hwnd, 0x0201, 0x0001, make_lparam(px, py))
    user32.SendMessageW(hwnd, 0x0202, 0, make_lparam(px, py))


def main():
    hwnd = ui.create_window("🔗 InputGroup 全套能力验证", 240, 80, 1180, 760)
    if not hwnd:
        raise RuntimeError("窗口创建失败")

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1140, 700)

    ui.create_text(hwnd, content, "🔗 InputGroup 组合输入完整验证", 34, 24, 620, 40)
    intro = ui.create_text(
        hwnd, content,
        "覆盖 prepend / append 文本、按钮、选择器，验证内部 Input / Button / Select 元素 ID 读回和值同步。",
        34, 74, 980, 56,
    )
    ui.set_text_options(hwnd, intro, align=0, valign=0, wrap=True, ellipsis=False)

    basic_group = ui.create_input_group(
        hwnd, content,
        value="openai", placeholder="请输入站点名称",
        prepend={"type": "text", "text": "https://"},
        append={"type": "text", "text": ".com"},
        size=0, clearable=True,
        x=44, y=154, w=520, h=42,
    )

    search_group = ui.create_input_group(
        hwnd, content,
        value="", placeholder="请输入查询内容",
        prepend={
            "type": "select",
            "items": [("餐厅名", "1"), ("订单号", "2"), ("用户电话", "3")],
            "selected": 0,
            "placeholder": "请选择",
        },
        append={"type": "button", "emoji": "🔎", "text": "", "variant": 1},
        size=1,
        x=44, y=252, w=640, h=42,
    )

    secure_group = ui.create_input_group(
        hwnd, content,
        value="abc123", placeholder="请输入密码",
        append={"type": "text", "text": "🔐"},
        size=2, clearable=True, password=True,
        show_word_limit=True, autosize=True,
        min_rows=2, max_rows=4,
        x=44, y=350, w=520, h=40,
    )

    panel = ui.create_panel(hwnd, content, 728, 152, 340, 272)
    ui.set_panel_style(hwnd, panel, 0x102563EB, 0x552563EB, 1.0, 12.0, 16)
    ui.create_text(hwnd, panel, "📊 读回检查", 0, 0, 180, 30)
    note = ui.create_text(
        hwnd, panel,
        "窗口显示后会自动读取内部 element id、切换 prepend Select 的选中项，并点击 append Button。",
        0, 46, 260, 124,
    )
    ui.set_text_options(hwnd, note, align=0, valign=0, wrap=True, ellipsis=False)

    require_equal("基础值", ui.get_input_group_value(hwnd, basic_group), "openai")
    require_dict("基础组选项", ui.get_input_group_options(hwnd, basic_group), {"size": 0, "clearable": True})
    require_dict(
        "安全组选项",
        ui.get_input_group_options(hwnd, secure_group),
        {
            "size": 2,
            "clearable": True,
            "password": True,
            "show_word_limit": True,
            "autosize": True,
            "min_rows": 2,
            "max_rows": 4,
        },
    )

    basic_input_id = ui.get_input_group_input_element_id(hwnd, basic_group)
    basic_prepend_id = ui.get_input_group_addon_element_id(hwnd, basic_group, 0)
    basic_append_id = ui.get_input_group_addon_element_id(hwnd, basic_group, 1)
    search_input_id = ui.get_input_group_input_element_id(hwnd, search_group)
    select_addon_id = ui.get_input_group_addon_element_id(hwnd, search_group, 0)
    button_addon_id = ui.get_input_group_addon_element_id(hwnd, search_group, 1)

    require_true("基础组 input id", basic_input_id > 0)
    require_true("基础组 prepend id", basic_prepend_id > 0)
    require_true("基础组 append id", basic_append_id > 0)
    require_true("搜索组 input id", search_input_id > 0)
    require_true("搜索组 select addon id", select_addon_id > 0)
    require_true("搜索组 button addon id", button_addon_id > 0)

    ui.set_input_value(hwnd, basic_input_id, "emoji-window")
    require_equal("内部 Input 改值回写组值", ui.get_input_group_value(hwnd, basic_group), "emoji-window")

    ui.set_input_group_value(hwnd, search_group, "凌空 SOHO")
    require_equal("组值写回内部 Input", ui.get_input_value(hwnd, search_input_id), "凌空 SOHO")
    require_equal("Select 初始选中", ui.dll.EU_GetSelectIndex(hwnd, select_addon_id), 0)
    ui.dll.EU_SetSelectIndex(hwnd, select_addon_id, 2)
    require_equal("Select 切换选中", ui.dll.EU_GetSelectIndex(hwnd, select_addon_id), 2)

    ui.clear_input_group_addon(hwnd, basic_group, 1)
    require_equal("清空右侧附加项后 id", ui.get_input_group_addon_element_id(hwnd, basic_group, 1), 0)
    ui.set_input_group_text_addon(hwnd, basic_group, 1, ".dev")
    require_true("恢复右侧附加项 id", ui.get_input_group_addon_element_id(hwnd, basic_group, 1) > 0)

    ui.dll.EU_SetElementClickCallback(hwnd, button_addon_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.35)

    click_logical_rect(user32, hwnd, 44 + 560, 252, 80, 42)
    pump_messages(user32, msg, 0.25)
    require_true("附加按钮点击回调", g_button_clicks >= 1)

    print("[读取] basic:", ui.get_input_group_value(hwnd, basic_group), ui.get_input_group_options(hwnd, basic_group))
    print("[读取] search:", ui.get_input_group_value(hwnd, search_group), "select=", ui.dll.EU_GetSelectIndex(hwnd, select_addon_id))
    print("[读取] secure:", ui.get_input_group_options(hwnd, secure_group), ui.get_input_value(hwnd, ui.get_input_group_input_element_id(hwnd, secure_group)))
    print("[提示] 窗口将保持 8 秒，可检查中文、emoji、prepend/append 文本、选择器和按钮附加项外观。")

    pump_messages(user32, msg, 8.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
