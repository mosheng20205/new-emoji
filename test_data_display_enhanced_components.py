import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_table_id = 0
g_collapse_id = 0
g_stat_id = 0
g_update_id = 0
g_empty_table_id = 0
g_counter = 2468


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 增强数据展示组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_counter

    if element_id == g_update_id:
        g_counter += 128
        value_data = ui.make_utf8(str(g_counter))
        ui.dll.EU_SetStatisticValue(
            g_hwnd, g_stat_id, ui.bytes_arg(value_data), len(value_data)
        )
        next_row = (ui.get_table_selected_row(g_hwnd, g_table_id) + 1) % max(
            1, ui.get_table_row_count(g_hwnd, g_table_id)
        )
        ui.set_table_selected_row(g_hwnd, g_table_id, next_row)
        print(f"[更新] 统计={g_counter}，表格选中行={next_row}")
    elif element_id == g_collapse_id:
        active = ui.dll.EU_GetCollapseActive(g_hwnd, g_collapse_id)
        print(f"[折叠面板] 当前展开项={active}")
    else:
        print(f"[点击] 元素 #{element_id}")


def main():
    global g_hwnd, g_table_id, g_collapse_id, g_stat_id, g_update_id, g_empty_table_id

    hwnd = ui.create_window("📚 增强数据展示组件", 220, 70, 1080, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 1040, 700)
    ui.create_text(hwnd, content_id, "📚 数据展示增强批次", 28, 22, 340, 34)

    desc_id = ui.create_descriptions(
        hwnd, content_id,
        "📋 项目概览",
        [
            ("项目", "new_emoji 纯 D2D 界面库"),
            ("亮点", "🎨 中文与彩色 emoji 原生渲染"),
            ("状态", "✅ 数据展示组件增强中"),
            ("说明", "描述列表支持更宽标签、最小行高和长文本换行。"),
        ],
        2,
        True,
        28, 70, 470, 170,
    )
    ui.set_descriptions_options(
        hwnd, desc_id, columns=2, bordered=True,
        label_width=118, min_row_height=42, wrap_values=True,
    )

    card_id = ui.create_card(
        hwnd, content_id,
        "🧩 发布卡片",
        "卡片现在支持页脚区域，可用于放置状态、更新时间或轻量操作提示。",
        2,
        530, 70, 420, 170,
    )
    ui.set_card_footer(hwnd, card_id, "✅ 已同步到 Python / 易语言导出文档")
    ui.set_card_options(hwnd, card_id, shadow=2, hoverable=True)

    g_table_id = ui.create_table(
        hwnd, content_id,
        ["组件", "能力", "进度"],
        [
            ["📋 描述列表", "列数/标签宽/换行", "✅ 已接入"],
            ["📊 表格", "行选择/空态/行高", "✅ 已接入"],
            ["🧩 卡片", "页脚/悬停阴影", "✅ 已接入"],
            ["🪗 折叠面板", "禁用项/键盘切换", "✅ 已接入"],
        ],
        True,
        True,
        28, 270, 600, 210,
    )
    ui.set_table_options(
        hwnd, g_table_id, striped=True, bordered=True,
        row_height=38, header_height=42, selectable=True,
    )
    ui.set_table_selected_row(hwnd, g_table_id, 1)

    g_empty_table_id = ui.create_table(
        hwnd, content_id,
        ["📭 空表头", "状态"],
        [],
        False,
        True,
        660, 270, 290, 112,
    )
    ui.set_table_empty_text(hwnd, g_empty_table_id, "📭 暂无待处理数据")

    g_stat_id = ui.create_statistic(
        hwnd, content_id,
        "📈 今日访问",
        str(g_counter),
        "",
        " 次",
        660, 402, 170, 110,
    )
    ui.set_statistic_format(hwnd, g_stat_id, "📈 今日访问", "🔥 ", " 次")
    g_update_id = ui.create_button(hwnd, content_id, "🔄", "刷新数据", 850, 438, 120, 42)

    g_collapse_id = ui.create_collapse(
        hwnd, content_id,
        [
            ("🎯 可展开项目", "当前项目允许点击与键盘切换。"),
            ("🔒 禁用项目", "这个标题会以弱化样式显示，并跳过点击命中。"),
            ("💡 说明项目", "allow_collapse=False 时，已展开项不会被再次点击折叠。"),
        ],
        0,
        True,
        28, 510, 430, 158,
    )
    ui.set_collapse_options(
        hwnd, g_collapse_id,
        accordion=True,
        allow_collapse=False,
        disabled_indices=[1],
    )

    timeline_id = ui.create_timeline(
        hwnd, content_id,
        [
            ("09:00", "🚀 创建增强批次窗口", 0),
            ("10:20", "✅ 接入表格选中与空态", 1),
            ("11:10", "⚠️ 保留禁用折叠项用于状态验证", 2),
            ("12:00", "🎉 完成导出与示例", 3),
        ],
        500, 520, 450, 150,
    )
    ui.set_timeline_options(hwnd, timeline_id, position=2, show_time=True)

    for eid in (card_id, g_table_id, g_collapse_id, g_stat_id, g_update_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    print(
        "[检查] 描述项={desc} 表格={rows}x{cols} 空表={empty_rows} 折叠项={collapse} 时间线={timeline}".format(
            desc=ui.get_descriptions_item_count(hwnd, desc_id),
            rows=ui.get_table_row_count(hwnd, g_table_id),
            cols=ui.get_table_column_count(hwnd, g_table_id),
            empty_rows=ui.get_table_row_count(hwnd, g_empty_table_id),
            collapse=ui.get_collapse_item_count(hwnd, g_collapse_id),
            timeline=ui.get_timeline_item_count(hwnd, timeline_id),
        )
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("增强数据展示组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("增强数据展示组件示例结束。")


if __name__ == "__main__":
    main()
