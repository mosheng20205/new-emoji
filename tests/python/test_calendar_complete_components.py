import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 日历完成验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_calendar_change(element_id, value, range_start, range_end):
    print(f"[回调] 日历={element_id} 选中={value} 区间={range_start}-{range_end}")


def main():
    hwnd = ui.create_window("📅 日历组件全样式完成验证", 220, 80, 1240, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1200, 700)
    ui.create_text(hwnd, content, "📅 日历组件全样式完成验证", 30, 22, 420, 36)
    ui.create_text(hwnd, content, "覆盖基础绑定、dateCell 自定义、显示范围、状态颜色、选中标记、清空单元格和变化回调。", 30, 58, 860, 28)

    ui.create_text(hwnd, content, "基础日历", 36, 100, 160, 28)
    ui.create_text(hwnd, content, "dateCell 自定义", 430, 100, 180, 28)
    ui.create_text(hwnd, content, "显示范围", 824, 100, 160, 28)

    cal = ui.create_calendar(hwnd, content, 2026, 5, 12, 36, 132, 360, 330)
    custom = ui.create_calendar(hwnd, content, 2026, 5, 12, 430, 132, 360, 330)
    ranged = ui.create_calendar(hwnd, content, 2026, 5, 12, 824, 132, 350, 330)

    for item in (cal, custom, ranged):
        ui.set_calendar_range(hwnd, item, 20260505, 20260528)
        ui.set_calendar_options(hwnd, item, 20260505, True)
        ui.set_calendar_selection_range(hwnd, item, 20260510, 20260518, True)
        ui.set_calendar_selected_marker(hwnd, item, "✔️")
        ui.set_calendar_state_colors(
            hwnd, item,
            selected_bg=0xFF1989FA, selected_fg=0xFFFFFFFF,
            range_bg=0x332F80ED, today_border=0xFFE6A23C,
            hover_bg=0xFFEAF2FF, disabled_fg=0xFF9AA6BA,
            adjacent_fg=0xFF909399,
        )
        ui.set_calendar_change_callback(hwnd, item, on_calendar_change)

    cell_items = [
        {"date": 20260512, "label": "05-12", "extra": "会议", "emoji": "✔️", "badge": "会", "bg": "0xFFEAF2FF", "fg": "0xFF1989FA", "border": "0xFF1989FA", "badge_bg": "0xFF1989FA", "badge_fg": "0xFFFFFFFF", "font_flags": 1},
        {"date": 20260518, "label": "05-18", "extra": "不可选", "emoji": "⛔", "badge": "禁", "disabled": 1, "fg": "0xFF909399"},
        {"date": 20260522, "label": "05-22", "extra": "发布", "emoji": "🚀", "badge": "发", "bg": "0xFFEAF8EF", "fg": "0xFF2F855A", "border": "0xFF67C23A", "badge_bg": "0xFF67C23A", "badge_fg": "0xFFFFFFFF"},
    ]
    ui.set_calendar_visual_options(hwnd, custom, True, True, 3, True, 8.0)
    ui.set_calendar_cell_items(hwnd, custom, cell_items)
    ui.set_calendar_display_range(hwnd, ranged, 20260504, 20260524)
    ui.set_calendar_visual_options(hwnd, ranged, True, True, 1, True, 8.0)

    ui.set_calendar_cell_items(hwnd, cal, [{"date": 20260506, "label": "06", "extra": "临时"}])
    ui.clear_calendar_cell_items(hwnd, cal)

    ui.create_text(hwnd, content, "⌨️ 点击任一日历后可用方向键、Home/End、PageUp/PageDown 操作；自定义禁用日期不可点击。", 36, 492, 900, 32)
    summary = (
        f"✅ 日期={ui.get_calendar_value(hwnd, cal)}  可选范围={ui.get_calendar_range(hwnd, cal)}  "
        f"显示范围={ui.get_calendar_display_range(hwnd, ranged)}\n"
        f"视觉={ui.get_calendar_visual_options(hwnd, custom)}  颜色={ui.get_calendar_state_colors(hwnd, custom)}\n"
        f"自定义单元格行数={len(ui.get_calendar_cell_items(hwnd, custom).splitlines())}  "
        f"区间={ui.get_calendar_selection_range(hwnd, custom)}"
    )
    readback = ui.create_text(hwnd, content, summary, 36, 540, 1080, 86)
    ui.set_text_options(hwnd, readback, wrap=True, ellipsis=False)

    print("[读回] 日历日期=", ui.get_calendar_value(hwnd, cal))
    print("[读回] 日期范围=", ui.get_calendar_range(hwnd, cal))
    print("[读回] 日历选项=", ui.get_calendar_options(hwnd, cal))
    print("[读回] 显示范围=", ui.get_calendar_display_range(hwnd, ranged))
    print("[读回] 视觉选项=", ui.get_calendar_visual_options(hwnd, custom))
    print("[读回] 状态颜色=", ui.get_calendar_state_colors(hwnd, custom))
    print("[读回] 单元格数据=", ui.get_calendar_cell_items(hwnd, custom))
    print("[读回] 选择区间=", ui.get_calendar_selection_range(hwnd, custom))

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("📅 日历全样式完成验证示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("📅 日历全样式完成验证示例结束。")


if __name__ == "__main__":
    main()
