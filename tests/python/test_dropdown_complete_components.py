import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202


g_hwnd = None
g_controls = {}
g_labels = {}
g_state = {
    "commands": [],
    "main_clicks": 0,
}


def lp_from_xy(x, y):
    return (y << 16) | (x & 0xFFFF)


def click_point(x, y):
    user32 = ctypes.windll.user32
    lp = lp_from_xy(x, y)
    user32.SendMessageW(g_hwnd, WM_MOUSEMOVE, 0, lp)
    user32.SendMessageW(g_hwnd, WM_LBUTTONDOWN, 1, lp)
    user32.SendMessageW(g_hwnd, WM_LBUTTONUP, 0, lp)


def click_dropdown_item(rect, index, row_height):
    x, y, w, h = rect
    item_x = x + 18
    item_y = y + h + 4 + index * row_height + row_height // 2
    click_point(item_x, item_y)


def refresh_summary():
    if not g_labels:
        return
    hide_opts = ui.get_dropdown_options(g_hwnd, g_controls["hide_keep"])
    hide_state = ui.get_dropdown_state(g_hwnd, g_controls["hide_keep"])
    meta_state = ui.get_dropdown_state(g_hwnd, g_controls["meta"])
    meta_2 = ui.get_dropdown_item_meta(g_hwnd, g_controls["meta"], 2)
    meta_5 = ui.get_dropdown_item_meta(g_hwnd, g_controls["meta"], 5)
    scroll_4 = ui.get_dropdown_item_meta(g_hwnd, g_controls["scroll"], 4)
    ui.set_element_text(
        g_hwnd, g_labels["summary"],
        "📘 Dropdown 读回："
        f"hide_on_click={hide_opts['hide_on_click']} split={hide_opts['split_button']} "
        f"variant={hide_opts['button_variant']} size={hide_opts['size']} style={hide_opts['trigger_style']}\n"
        f"状态：selected={hide_state['selected']} count={hide_state['count']} disabled={hide_state['disabled']} "
        f"level={hide_state['level']} hover={hide_state['hover']}\n"
        f"第3项：icon={meta_2['icon']} command={meta_2['command']} divided={meta_2['divided']} "
        f"disabled={meta_2['disabled']} level={meta_2['level']}\n"
        f"第6项：icon={meta_5['icon']} command={meta_5['command']} divided={meta_5['divided']} "
        f"disabled={meta_5['disabled']} level={meta_5['level']}\n"
        f"长列表第5项：icon={scroll_4['icon']} command={scroll_4['command']} disabled={scroll_4['disabled']}"
    )
    ui.set_element_text(
        g_hwnd, g_labels["last"],
        f"📨 最近命令：{g_state['commands'][-1][2] if g_state['commands'] else '等待选择'}"
    )
    ui.set_element_text(
        g_hwnd, g_labels["main"],
        f"🧭 主按钮点击：{g_state['main_clicks']} 次"
    )


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


@ui.DropdownCommandCallback
def on_dropdown_command(element_id, item_index, command_ptr, command_len):
    command = ""
    if command_ptr and command_len > 0:
        command = ctypes.string_at(command_ptr, command_len).decode("utf-8", errors="replace")
    g_state["commands"].append((element_id, item_index, command))
    refresh_summary()


@ui.ClickCallback
def on_split_main(element_id):
    g_state["main_clicks"] += 1
    refresh_summary()


def assert_true(value, message):
    if not value:
        raise RuntimeError(message)


def main():
    global g_hwnd

    hwnd = ui.create_window("📂 Dropdown 完整组件测试", 220, 80, 1180, 1080)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 1120, 1000)
    ui.create_text(hwnd, content_id, "📂 Dropdown 完整组件测试", 28, 24, 420, 34)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本页覆盖 options 读回、item meta 读回、禁用项拦截、hide-on-click、split-button、manual 和四种尺寸。",
        28, 66, 980, 42,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    trigger_panel = ui.create_panel(hwnd, content_id, 28, 120, 520, 200)
    behavior_panel = ui.create_panel(hwnd, content_id, 572, 120, 520, 260)
    menu_panel = ui.create_panel(hwnd, content_id, 28, 340, 1064, 240)
    size_panel = ui.create_panel(hwnd, content_id, 28, 600, 1064, 180)
    readback_panel = ui.create_panel(hwnd, content_id, 28, 800, 1064, 220)

    for panel in (trigger_panel, behavior_panel, menu_panel, size_panel, readback_panel):
        ui.set_panel_style(hwnd, panel, 0xFF252A42, 0xFF3D4668, 1.0, 8.0, 10)

    action_items = ["📄 复制", "✏️ 编辑", "🗑️ 删除"]
    meta_items = [
        "📄 复制",
        "✏️ 编辑",
        "> !🗑️ 删除",
        "📤 导出",
        "> 归档",
        "> > 归档到项目",
    ]
    scroll_items = [f"📁 最近文件 {i:02d}" for i in range(1, 13)]

    link_hover = ui.create_dropdown(hwnd, trigger_panel, "文字链接", action_items, 0, 28, 72, 160, 34)
    ui.set_dropdown_options(hwnd, link_hover, trigger_mode=1, hide_on_click=True, split_button=False, button_variant=0, size=0, trigger_style=1)
    link_click = ui.create_dropdown(hwnd, trigger_panel, "文字链接", action_items, 0, 204, 72, 160, 34)
    ui.set_dropdown_options(hwnd, link_click, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=0, size=0, trigger_style=1)

    manual_status = ui.create_text(hwnd, trigger_panel, "🧭 手动菜单：已关闭", 28, 124, 300, 24)
    ui.set_text_options(hwnd, manual_status, align=0, valign=0, wrap=True, ellipsis=False)
    manual_menu = ui.create_dropdown(hwnd, trigger_panel, "手动控制", ["开始", "暂停", "结束"], 0, 28, 150, 220, 34)
    ui.set_dropdown_options(hwnd, manual_menu, trigger_mode=2, hide_on_click=True, split_button=False, button_variant=6, size=0, trigger_style=0)
    toggle_manual = ui.create_button(hwnd, trigger_panel, "🧭", "切换手动菜单", 268, 150, 148, 36)

    hide_keep = ui.create_dropdown(hwnd, behavior_panel, "保持展开", meta_items, 0, 28, 72, 220, 36)
    ui.set_dropdown_options(hwnd, hide_keep, trigger_mode=0, hide_on_click=False, split_button=False, button_variant=2, size=1, trigger_style=0)
    ui.set_dropdown_item_meta(
        hwnd, hide_keep,
        ["📄", "✏️", "🗑️", "📤", "🗂️", "🏷️"],
        ["copy", "", "delete", "export", "archive", "archive_project"],
        [3],
    )
    ui.set_dropdown_disabled(hwnd, hide_keep, [4])

    split_menu = ui.create_dropdown(hwnd, behavior_panel, "分裂按钮", action_items, 0, 268, 72, 220, 36)
    ui.set_dropdown_options(hwnd, split_menu, trigger_mode=0, hide_on_click=True, split_button=True, button_variant=1, size=0, trigger_style=0)
    ui.set_dropdown_command_callback(hwnd, split_menu, on_dropdown_command)

    meta_dropdown = ui.create_dropdown(hwnd, menu_panel, "项目样式", meta_items, 0, 28, 72, 300, 36)
    ui.set_dropdown_options(hwnd, meta_dropdown, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=0, size=0, trigger_style=0)
    ui.set_dropdown_item_meta(
        hwnd, meta_dropdown,
        ["📄", "✏️", "🗑️", "📤", "🗂️", "🏷️"],
        ["copy", "", "delete", "export", "archive", "archive_project"],
        [3],
    )
    ui.set_dropdown_disabled(hwnd, meta_dropdown, [2, 4])

    scroll_dropdown = ui.create_dropdown(hwnd, menu_panel, "长列表滚动", scroll_items, 0, 348, 72, 470, 36)
    ui.set_dropdown_options(hwnd, scroll_dropdown, trigger_mode=0, hide_on_click=True, split_button=False, button_variant=0, size=2, trigger_style=0)
    ui.set_dropdown_disabled(hwnd, scroll_dropdown, [4])

    size_dropdowns = {}
    size_positions = [(0, "默认", 28), (1, "medium", 300), (2, "small", 572), (3, "mini", 844)]
    for size_value, label, x in size_positions:
        ui.create_text(hwnd, size_panel, f"{label} 尺寸", x, 36, 120, 22)
        dd = ui.create_dropdown(hwnd, size_panel, label, action_items, 0, x, 68, 220, 36)
        ui.set_dropdown_options(hwnd, dd, trigger_mode=0, hide_on_click=True, split_button=True, button_variant=1, size=size_value, trigger_style=0)
        size_dropdowns[size_value] = dd

    g_controls.update({
        "link_hover": link_hover,
        "link_click": link_click,
        "manual_menu": manual_menu,
        "hide_keep": hide_keep,
        "split_menu": split_menu,
        "meta": meta_dropdown,
        "scroll": scroll_dropdown,
        "size0": size_dropdowns[0],
        "size1": size_dropdowns[1],
        "size2": size_dropdowns[2],
        "size3": size_dropdowns[3],
    })

    g_labels.update({
        "last": ui.create_text(hwnd, readback_panel, "📨 最近命令：等待选择", 28, 72, 420, 28),
        "main": ui.create_text(hwnd, readback_panel, "🧭 主按钮点击：0 次", 28, 102, 420, 28),
        "summary": ui.create_text(hwnd, readback_panel, "📘 Dropdown 读回：等待刷新", 28, 132, 1040, 64),
    })
    for key in ("last", "main", "summary"):
        ui.set_text_options(hwnd, g_labels[key], align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_infobox(
        hwnd, readback_panel,
        "📚 枚举",
        "触发模式：0 点击 / 1 悬停 / 2 手动；触发器样式：0 按钮 / 1 文字链接；尺寸：0 默认 / 1 medium / 2 small / 3 mini。",
        480, 68, 560, 64,
    )

    ui.set_dropdown_command_callback(hwnd, hide_keep, on_dropdown_command)
    ui.set_dropdown_command_callback(hwnd, manual_menu, on_dropdown_command)
    ui.set_dropdown_command_callback(hwnd, meta_dropdown, on_dropdown_command)
    ui.set_dropdown_command_callback(hwnd, scroll_dropdown, on_dropdown_command)
    ui.set_dropdown_main_click_callback(hwnd, split_menu, on_split_main)

    ui.dll.EU_SetElementClickCallback(hwnd, toggle_manual, keep_callback(ui.ClickCallback(lambda _eid: None)))

    @ui.ClickCallback
    def on_toggle_manual(_eid):
        now_open = not ui.get_dropdown_open(hwnd, manual_menu)
        ui.set_dropdown_open(hwnd, manual_menu, now_open)
        ui.set_element_text(hwnd, manual_status, f"🧭 手动菜单：{'已打开' if now_open else '已关闭'}")
        refresh_summary()

    @ui.ClickCallback
    def on_refresh(_eid):
        refresh_summary()

    g_controls["toggle_manual"] = toggle_manual
    g_controls["manual_status"] = manual_status
    g_controls["refresh"] = ui.create_button(hwnd, readback_panel, "🔄", "刷新读回", 860, 72, 128, 36)
    ui.dll.EU_SetElementClickCallback(hwnd, toggle_manual, on_toggle_manual)
    ui.dll.EU_SetElementClickCallback(hwnd, g_controls["refresh"], on_refresh)

    refresh_summary()
    ui.dll.EU_ShowWindow(hwnd, 1)

    assert_true(ui.get_dropdown_options(hwnd, link_hover)["trigger_mode"] == 1, "link_hover 触发模式读回失败")
    assert_true(ui.get_dropdown_options(hwnd, link_click)["trigger_style"] == 1, "link_click 触发器样式读回失败")
    assert_true(ui.get_dropdown_options(hwnd, hide_keep)["hide_on_click"] is False, "hide_keep hide_on_click 读回失败")
    assert_true(ui.get_dropdown_options(hwnd, manual_menu)["trigger_mode"] == 2, "manual_menu 手动模式读回失败")
    assert_true(ui.get_dropdown_options(hwnd, split_menu)["split_button"] is True, "split_menu split-button 读回失败")
    assert_true(ui.get_dropdown_options(hwnd, size_dropdowns[3])["size"] == 3, "mini 尺寸读回失败")

    meta_info = ui.get_dropdown_item_meta(hwnd, meta_dropdown, 2)
    assert_true(meta_info["disabled"] is True, "禁用项元数据读回失败")
    assert_true(meta_info["level"] == 1, "禁用项层级读回失败")
    assert_true(meta_info["command"] == "delete", "禁用项 command 读回失败")
    meta_child = ui.get_dropdown_item_meta(hwnd, meta_dropdown, 5)
    assert_true(meta_child["level"] == 2, "二级菜单层级读回失败")

    ui.set_dropdown_selected(hwnd, meta_dropdown, 2)
    meta_state = ui.get_dropdown_state(hwnd, meta_dropdown)
    assert_true(meta_state["selected"] != 2, "禁用项不应被选中")

    before_commands = len(g_state["commands"])
    ui.set_dropdown_open(hwnd, meta_dropdown, True)
    click_dropdown_item((28, 72, 300, 36), 2, 34)
    assert_true(len(g_state["commands"]) == before_commands, "禁用项不应触发 command")

    ui.set_dropdown_open(hwnd, meta_dropdown, True)
    click_dropdown_item((28, 72, 300, 36), 1, 34)
    assert_true(g_state["commands"][-1][2] == "编辑", "空 command 应回传显示文本")
    assert_true(ui.get_dropdown_open(hwnd, meta_dropdown) is False, "hide_on_click=True 点击后应关闭")

    ui.set_dropdown_open(hwnd, hide_keep, True)
    before_commands = len(g_state["commands"])
    click_dropdown_item((28, 72, 220, 36), 1, 32)
    assert_true(len(g_state["commands"]) == before_commands + 1, "保持展开菜单应触发 command")
    assert_true(ui.get_dropdown_open(hwnd, hide_keep) is True, "hide_on_click=False 点击后应保持打开")

    split_rect = (268, 72, 220, 36)
    click_point(split_rect[0] + split_rect[2] - 8, split_rect[1] + split_rect[3] // 2)
    assert_true(ui.get_dropdown_open(hwnd, split_menu) is True, "split-button 箭头应打开菜单")
    main_before = g_state["main_clicks"]
    click_point(split_rect[0] + 18, split_rect[1] + split_rect[3] // 2)
    assert_true(g_state["main_clicks"] == main_before + 1, "split-button 主按钮回调未触发")
    assert_true(ui.get_dropdown_open(hwnd, split_menu) is True, "split-button 主按钮不应关闭菜单")

    click_point(268 + 12, 150 + 18)
    assert_true(ui.get_dropdown_open(hwnd, manual_menu) is True, "手动菜单应由程序按钮打开")
    click_dropdown_item((28, 150, 220, 36), 0, 34)
    assert_true(g_state["commands"][-1][2] == "开始", "手动菜单 command 读回失败")

    ui.set_dropdown_open(hwnd, scroll_dropdown, True)
    before_commands = len(g_state["commands"])
    click_dropdown_item((348, 72, 470, 36), 4, 30)
    assert_true(len(g_state["commands"]) == before_commands, "运行时禁用项不应触发 command")
    scroll_meta = ui.get_dropdown_item_meta(hwnd, scroll_dropdown, 4)
    assert_true(scroll_meta["disabled"] is True, "运行时禁用项读回失败")

    refresh_summary()

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    while time.time() - start < 12:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                return
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)

    print("Dropdown 完整组件测试通过。")


if __name__ == "__main__":
    main()
