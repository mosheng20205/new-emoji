import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


ui.dll.EU_GetElementBounds.argtypes = [
    wintypes.HWND,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
ui.dll.EU_GetElementBounds.restype = ctypes.c_int


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 文字提示完整验证窗口正在关闭")
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


def open_tooltip_and_get_state(hwnd, tip_id, user32, msg, duration=0.16):
    ui.trigger_tooltip(hwnd, tip_id, True)
    pump_messages(user32, msg, duration)
    return ui.get_tooltip_full_state(hwnd, tip_id)


def get_element_bounds(hwnd, element_id):
    x = ctypes.c_int()
    y = ctypes.c_int()
    w = ctypes.c_int()
    h = ctypes.c_int()
    ok = ui.dll.EU_GetElementBounds(
        hwnd,
        element_id,
        ctypes.byref(x),
        ctypes.byref(y),
        ctypes.byref(w),
        ctypes.byref(h),
    )
    if not ok:
        raise RuntimeError(f"元素 {element_id} 读取 bounds 失败")
    return x.value, y.value, w.value, h.value


def assert_near(actual, expected, label, tolerance=1):
    if abs(actual - expected) > tolerance:
        raise RuntimeError(f"{label} 坐标错误：实际 {actual}，期望 {expected}")


def main():
    hwnd = ui.create_window("💡 文字提示完整组件验证", 220, 80, 920, 620)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 560)
    ui.create_text(hwnd, content_id, "💡 Tooltip 文字提示完整封装", 30, 24, 640, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证箭头绘制、显示/隐藏延迟、焦点触发、键盘关闭、手动触发、文本读回和完整状态读回。",
        30,
        72,
        820,
        56,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    tip_id = ui.create_tooltip(
        hwnd,
        content_id,
        label="聚焦查看提示 ✨",
        content="💡 焦点触发后延迟显示，支持中文和 emoji。",
        placement=2,
        x=84,
        y=176,
        w=190,
        h=42,
    )
    ui.set_tooltip_behavior(hwnd, tip_id, show_delay=120, hide_delay=80,
                            trigger_mode=2, show_arrow=True)
    ui.set_tooltip_options(hwnd, tip_id, placement=2, open=False, max_width=300)
    ui.set_tooltip_advanced_options(
        hwnd,
        tip_id,
        placement="top-start",
        effect="light",
        disabled=False,
        show_arrow=True,
        offset=10,
        max_width=300,
    )
    advanced = ui.get_tooltip_advanced_options(hwnd, tip_id)
    if (
        not advanced
        or advanced["placement"] != ui.EXTENDED_PLACEMENTS["top-start"]
        or advanced["effect"] != 1
        or advanced["disabled"]
        or not advanced["show_arrow"]
        or advanced["offset"] != 10
    ):
        raise RuntimeError("Tooltip 高级选项读回失败")

    geometry_id = ui.create_tooltip(
        hwnd,
        content_id,
        label="方位几何 ✅",
        content="提示",
        placement=2,
        x=320,
        y=250,
        w=220,
        h=100,
    )

    placements = [
        ("top-start", "上左"), ("top", "上边"), ("top-end", "上右"),
        ("left-start", "左上"), ("left", "左边"), ("left-end", "左下"),
        ("right-start", "右上"), ("right", "右边"), ("right-end", "右下"),
        ("bottom-start", "下左"), ("bottom", "下边"), ("bottom-end", "下右"),
    ]
    for index, (placement_name, label) in enumerate(placements):
        col = index % 3
        row = index // 3
        item_id = ui.create_tooltip(
            hwnd,
            content_id,
            label=f"{label} 📍",
            content=f"📍 {placement_name} 方位提示\n第二行中文信息",
            placement=2,
            x=40 + col * 150,
            y=300 + row * 48,
            w=128,
            h=34,
        )
        ui.set_tooltip_advanced_options(
            hwnd,
            item_id,
            placement=placement_name,
            effect="dark" if index % 2 == 0 else "light",
            disabled=False,
            show_arrow=True,
            offset=8,
            max_width=220,
        )

    disabled_id = ui.create_tooltip(
        hwnd,
        content_id,
        label="点击开启提示 🚫",
        content="🚫 disabled 状态不弹出",
        placement=3,
        x=548,
        y=300,
        w=178,
        h=38,
    )
    ui.set_tooltip_advanced_options(
        hwnd,
        disabled_id,
        placement="bottom",
        effect="light",
        disabled=True,
        show_arrow=True,
        offset=8,
        max_width=220,
    )
    ui.trigger_tooltip(hwnd, disabled_id, True)
    disabled_state = ui.get_tooltip_advanced_options(hwnd, disabled_id)
    disabled_full = ui.get_tooltip_full_state(hwnd, disabled_id)
    if not disabled_state or not disabled_state["disabled"] or disabled_full["open"]:
        raise RuntimeError("Tooltip disabled 状态失败")

    if "聚焦查看" not in ui.get_tooltip_text(hwnd, tip_id, 0):
        raise RuntimeError("文字提示标签读回失败")
    if "焦点触发" not in ui.get_tooltip_text(hwnd, tip_id, 1):
        raise RuntimeError("文字提示内容读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()

    geometry_states = {}
    for placement_name in [item[0] for item in placements]:
        ui.set_tooltip_advanced_options(
            hwnd,
            geometry_id,
            placement=placement_name,
            effect="light",
            disabled=False,
            show_arrow=True,
            offset=8,
            max_width=180,
        )
        state = open_tooltip_and_get_state(hwnd, geometry_id, user32, msg, 0.14)
        print("[方位几何]", placement_name, state)
        if not state or not state["open"] or state["popup_w"] <= 0 or state["popup_h"] <= 0:
            raise RuntimeError(f"Tooltip 方位几何打开失败: {placement_name}")
        geometry_states[placement_name] = state
        ui.trigger_tooltip(hwnd, geometry_id, False)
        pump_messages(user32, msg, 0.06)

    top_states = [geometry_states[name] for name in ("top-start", "top", "top-end")]
    bottom_states = [geometry_states[name] for name in ("bottom-start", "bottom", "bottom-end")]
    left_states = [geometry_states[name] for name in ("left-start", "left", "left-end")]
    right_states = [geometry_states[name] for name in ("right-start", "right", "right-end")]

    if not all(st["popup_y"] < 0 for st in top_states):
        raise RuntimeError("Tooltip 顶部方位应当显示在触发器上方")
    if not all(st["popup_y"] > 0 for st in bottom_states):
        raise RuntimeError("Tooltip 底部方位应当显示在触发器下方")
    if not all(st["popup_x"] < 0 for st in left_states):
        raise RuntimeError("Tooltip 左侧方位应当显示在触发器左侧")
    if not all(st["popup_x"] > 0 for st in right_states):
        raise RuntimeError("Tooltip 右侧方位应当显示在触发器右侧")

    if not (top_states[0]["popup_x"] < top_states[1]["popup_x"] < top_states[2]["popup_x"]):
        raise RuntimeError("Tooltip 顶部 start/center/end 水平顺序错误")
    if not (bottom_states[0]["popup_x"] < bottom_states[1]["popup_x"] < bottom_states[2]["popup_x"]):
        raise RuntimeError("Tooltip 底部 start/center/end 水平顺序错误")
    if not (left_states[0]["popup_y"] < left_states[1]["popup_y"] < left_states[2]["popup_y"]):
        raise RuntimeError("Tooltip 左侧 start/center/end 垂直顺序错误")
    if not (right_states[0]["popup_y"] < right_states[1]["popup_y"] < right_states[2]["popup_y"]):
        raise RuntimeError("Tooltip 右侧 start/center/end 垂直顺序错误")

    _, _, logical_trigger_w, logical_trigger_h = get_element_bounds(hwnd, geometry_id)
    if logical_trigger_w != 220 or logical_trigger_h != 100:
        raise RuntimeError("Tooltip 几何触发器逻辑尺寸读回错误")

    trigger_w = top_states[1]["popup_x"] * 2 + top_states[1]["popup_w"]
    trigger_h = left_states[1]["popup_y"] * 2 + left_states[1]["popup_h"]
    expected_gap = -top_states[1]["popup_y"] - top_states[1]["popup_h"]
    if expected_gap <= 0:
        raise RuntimeError("Tooltip 顶部 offset 坐标错误")

    def expected_popup_xy(placement_name, state):
        popup_w = state["popup_w"]
        popup_h = state["popup_h"]
        align = "center"
        if placement_name.endswith("-start"):
            align = "start"
        elif placement_name.endswith("-end"):
            align = "end"

        if placement_name.startswith("top"):
            x = 0 if align == "start" else trigger_w - popup_w if align == "end" else (trigger_w - popup_w) // 2
            y = -popup_h - expected_gap
        elif placement_name.startswith("bottom"):
            x = 0 if align == "start" else trigger_w - popup_w if align == "end" else (trigger_w - popup_w) // 2
            y = trigger_h + expected_gap
        elif placement_name.startswith("left"):
            x = -popup_w - expected_gap
            y = 0 if align == "start" else trigger_h - popup_h if align == "end" else (trigger_h - popup_h) // 2
        else:
            x = trigger_w + expected_gap
            y = 0 if align == "start" else trigger_h - popup_h if align == "end" else (trigger_h - popup_h) // 2
        return x, y

    for placement_name, state in geometry_states.items():
        expected_x, expected_y = expected_popup_xy(placement_name, state)
        assert_near(state["popup_x"], expected_x, f"Tooltip {placement_name} popup_x")
        assert_near(state["popup_y"], expected_y, f"Tooltip {placement_name} popup_y")

    ui.dll.EU_SetElementFocus(hwnd, tip_id)
    pending = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[焦点等待状态]", pending)
    if not pending or not pending["timer_running"] or pending["timer_phase"] != 1:
        raise RuntimeError("文字提示焦点延迟计时器未启动")

    pump_messages(user32, msg, 0.22)
    opened = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[焦点打开状态]", opened)
    if not opened["open"] or opened["open_count"] < 1 or not opened["show_arrow"]:
        raise RuntimeError("文字提示焦点延迟打开失败")
    if opened["placement"] != 2 or opened["max_width"] != 300 or opened["show_delay"] != 120:
        raise RuntimeError("文字提示完整状态读回失败")

    user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)  # VK_ESCAPE
    pump_messages(user32, msg, 0.12)
    key_closed = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[键盘关闭状态]", key_closed)
    if key_closed["open"] or key_closed["close_count"] < 1 or key_closed["last_action"] != 4:
        raise RuntimeError("文字提示键盘关闭失败")

    ui.trigger_tooltip(hwnd, tip_id, True)
    manual_opened = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[手动打开状态]", manual_opened)
    if not manual_opened["open"] or manual_opened["last_action"] != 5:
        raise RuntimeError("文字提示手动打开失败")

    ui.trigger_tooltip(hwnd, tip_id, False)
    manual_closed = ui.get_tooltip_full_state(hwnd, tip_id)
    print("[手动关闭状态]", manual_closed)
    if manual_closed["open"] or manual_closed["last_action"] != 5:
        raise RuntimeError("文字提示手动关闭失败")

    ui.set_tooltip_options(hwnd, tip_id, placement=3, open=True, max_width=260)
    ui.create_tooltip(
        hwnd,
        content_id,
        label="悬停提示 🌟",
        content="🌟 悬停模式也可使用，弹层保持中文。",
        placement=3,
        x=330,
        y=176,
        w=170,
        h=42,
    )
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、箭头、焦点触发和首屏尺寸余量。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
