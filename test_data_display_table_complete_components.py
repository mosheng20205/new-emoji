import ctypes
from ctypes import wintypes
import os
import time

import test_new_emoji as ui


WINDOW_W = 980
WINDOW_H = 650
CONTENT_W = 950
CONTENT_H = 600

g_hwnd = None
g_desc_id = 0
g_table_id = 0
g_apply_id = 0
g_reset_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 描述列表与表格完成验证正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def dump_state(prefix):
    print(
        f"{prefix} "
        f"描述选项={ui.get_descriptions_options(g_hwnd, g_desc_id)} "
        f"表格选项={ui.get_table_options(g_hwnd, g_table_id)} "
        f"表格行列=({ui.dll.EU_GetTableRowCount(g_hwnd, g_table_id)}, {ui.dll.EU_GetTableColumnCount(g_hwnd, g_table_id)}) "
        f"选中行={ui.dll.EU_GetTableSelectedRow(g_hwnd, g_table_id)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_descriptions_options(
            g_hwnd, g_desc_id, columns=3, bordered=True,
            label_width=112, min_row_height=42, wrap_values=True
        )
        ui.set_descriptions_advanced_options(g_hwnd, g_desc_id, responsive=True, last_item_span=True)
        ui.set_table_sort(g_hwnd, g_table_id, 2, desc=True)
        ui.set_table_scroll_row(g_hwnd, g_table_id, 2)
        ui.set_table_column_width(g_hwnd, g_table_id, 130)
        dump_state("[应用数据展示状态]")
    elif element_id == g_reset_id:
        ui.set_descriptions_options(
            g_hwnd, g_desc_id, columns=2, bordered=True,
            label_width=92, min_row_height=34, wrap_values=False
        )
        ui.set_descriptions_advanced_options(g_hwnd, g_desc_id, responsive=False, last_item_span=False)
        ui.set_table_sort(g_hwnd, g_table_id, -1, desc=False)
        ui.set_table_scroll_row(g_hwnd, g_table_id, 0)
        ui.set_table_column_width(g_hwnd, g_table_id, 0)
        dump_state("[恢复数据展示状态]")


def main():
    global g_hwnd, g_desc_id, g_table_id, g_apply_id, g_reset_id

    hwnd = ui.create_window("📋 数据展示组件完成验证", 180, 90, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "📋 描述列表与表格完成验证", 28, 20, 420, 34)
    ui.create_divider(hwnd, content_id, "Descriptions 跨列/响应式，Table 排序/滚动/列宽", 0, 1, 28, 62, 880, 30)

    g_desc_id = ui.create_descriptions(
        hwnd, content_id,
        "🧾 项目概览",
        [
            ("名称", "new_emoji 纯 D2D 界面库 ✨"),
            ("状态", "✅ 组件封装推进中"),
            ("平台", "Win32 / x64"),
            ("说明", "最后一项可跨列显示较长中文内容，并在窄宽度下自动减少列数。"),
        ],
        columns=2,
        bordered=True,
        x=28,
        y=112,
        w=880,
        h=170,
        label_width=92,
        min_row_height=34,
        wrap_values=False,
        responsive=False,
        last_item_span=False,
    )

    rows = [
        ["Tag 🏷️", "已完成", "28"],
        ["Badge 🔔", "已完成", "31"],
        ["Progress 📈", "已完成", "76"],
        ["Avatar 👤", "已完成", "53"],
        ["Empty 📭", "已完成", "19"],
        ["Skeleton 💤", "已完成", "45"],
        ["Descriptions 🧾", "完成验证", "64"],
        ["Table 📊", "完成验证", "88"],
    ]
    g_table_id = ui.create_table(
        hwnd,
        content_id,
        ["组件", "状态", "优先级"],
        rows,
        striped=True,
        bordered=True,
        x=28,
        y=318,
        w=880,
        h=190,
        row_height=30,
        header_height=34,
        selectable=True,
    )

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "应用排序与跨列", 510, 532, 180, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "🔄", "恢复默认布局", 710, 532, 170, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_infobox(
        hwnd,
        content_id,
        "📐 首屏尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 908，最下内容约 574，保留 20px 以上余量。",
        28,
        526,
        440,
        62,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    dump_state("[初始数据展示状态]")
    duration = int(os.environ.get("EU_TEST_SECONDS", "30"))
    print(f"数据展示完成验证窗口已显示，请观察 {duration} 秒或手动关闭。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
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

    ui.dll.EU_DestroyWindow(hwnd)
    print("数据展示完成验证结束。")


if __name__ == "__main__":
    main()
