import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 940
WINDOW_H = 700
CONTENT_W = 920
CONTENT_H = 650

g_hwnd = None
g_datetime_id = 0
g_tree_select_id = 0
g_select_v2_id = 0
g_tour_id = 0
g_update_id = 0
g_open_tour_id = 0


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


def tree_items_arg(items):
    rows = []
    for label, level, expanded in items:
        rows.append(f"{label}\t{level}\t{1 if expanded else 0}")
    return utf8_arg("|".join(rows))


def tour_steps_arg(steps):
    return utf8_arg("|".join(f"{title}\t{body}" for title, body in steps))


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 扩展选择器示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] {width}×{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        cities = [
            "北京", "上海", "杭州", "深圳", "成都",
            "武汉", "南京", "苏州", "厦门", "青岛",
            "天津", "西安", "长沙", "宁波", "广州",
        ]
        data = ui.make_utf8("|".join(cities))
        ui.dll.EU_SetSelectV2Options(g_hwnd, g_select_v2_id, ui.bytes_arg(data), len(data))
        ui.dll.EU_SetSelectV2VisibleCount(g_hwnd, g_select_v2_id, 6)
        ui.dll.EU_SetSelectV2Index(g_hwnd, g_select_v2_id, 8)

        items = [
            ("工作区", 0, True),
            ("设计", 1, True),
            ("设计令牌", 2, True),
            ("组件", 2, True),
            ("工程", 1, True),
            ("构建", 2, True),
            ("发布", 2, True),
        ]
        item_data, item_len = tree_items_arg(items)
        ui.dll.EU_SetTreeSelectItems(g_hwnd, g_tree_select_id, item_data, item_len)
        ui.dll.EU_SetTreeSelectSelected(g_hwnd, g_tree_select_id, 6)

        ui.dll.EU_SetDateTimePickerDateTime(g_hwnd, g_datetime_id, 2026, 6, 18, 14, 30)

        steps = [
            ("选择时间", "日期时间选择器把日期和时间合并到同一个弹层里。"),
            ("选择节点", "树选择器用紧凑输入框保留层级结构。"),
            ("大量选项", "虚拟选择器用固定高度窗口展示长选项列表。"),
        ]
        ui.set_tour_steps(g_hwnd, g_tour_id, steps)
        ui.dll.EU_SetTourActive(g_hwnd, g_tour_id, 1)
        ui.dll.EU_SetTourOptions(g_hwnd, g_tour_id, 1, 1, 28, 250, 300, 40)
        print(
            "[扩展选择器] "
            f"虚拟选择器={ui.dll.EU_GetSelectV2Index(g_hwnd, g_select_v2_id)}，"
            f"树选择器={ui.dll.EU_GetTreeSelectSelected(g_hwnd, g_tree_select_id)}，"
            f"引导={ui.dll.EU_GetTourActive(g_hwnd, g_tour_id)}/"
            f"{ui.dll.EU_GetTourStepCount(g_hwnd, g_tour_id)}"
        )
    elif element_id == g_open_tour_id:
        ui.dll.EU_SetTourOptions(g_hwnd, g_tour_id, 1, 1, 28, 354, 300, 40)
        print("[引导] 已打开，状态=", ui.dll.EU_GetTourOpen(g_hwnd, g_tour_id))
    elif element_id == g_select_v2_id:
        print(f"[虚拟选择器] 当前选中={ui.dll.EU_GetSelectV2Index(g_hwnd, g_select_v2_id)}")
    elif element_id == g_tree_select_id:
        print(f"[树选择器] 当前选中={ui.dll.EU_GetTreeSelectSelected(g_hwnd, g_tree_select_id)}")
    elif element_id == g_tour_id:
        print(
            f"[引导] 当前步骤={ui.dll.EU_GetTourActive(g_hwnd, g_tour_id)}，"
            f"打开={ui.dll.EU_GetTourOpen(g_hwnd, g_tour_id)}"
        )


def main():
    global g_hwnd, g_datetime_id, g_tree_select_id, g_select_v2_id
    global g_tour_id, g_update_id, g_open_tour_id

    hwnd = ui.create_window("扩展选择器组件示例", 240, 90, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "扩展选择器组件", 28, 24, 360, 28)
    ui.create_divider(
        hwnd, content_id,
        "日期时间选择器 / 树选择器 / 虚拟选择器 / 引导",
        0, 1, 28, 62, 840, 34
    )

    ui.create_text(hwnd, content_id, "日期时间选择器", 28, 116, 150, 24)
    g_datetime_id = ui.create_datetimepicker(
        hwnd, content_id,
        2026, 5, 2, 9, 30,
        28, 146, 300, 40
    )

    ui.create_text(hwnd, content_id, "树选择器", 28, 220, 150, 24)
    g_tree_select_id = ui.create_tree_select(
        hwnd, content_id,
        [
            ("组件", 0, True),
            ("表单", 1, True),
            ("输入框", 2, True),
            ("选择器", 2, True),
            ("数据", 1, True),
            ("树形控件", 2, True),
            ("表格", 2, True),
        ],
        3,
        28, 250, 300, 40
    )

    ui.create_text(hwnd, content_id, "虚拟选择器", 28, 324, 150, 24)
    g_select_v2_id = ui.create_select_v2(
        hwnd, content_id,
        "城市",
        [
            "北京", "上海", "杭州", "深圳", "成都",
            "武汉", "南京", "苏州", "厦门", "青岛",
            "天津", "西安",
        ],
        2,
        6,
        28, 354, 300, 40
    )

    g_update_id = ui.create_button(hwnd, content_id, "", "更新扩展选择器", 28, 432, 210, 42)
    g_open_tour_id = ui.create_button(hwnd, content_id, "✨", "打开引导", 252, 432, 120, 42)

    ui.create_infobox(
        hwnd, content_id,
        "批次说明",
        "本批次新增四个独立控件，并保证所有示例元素都位于首次打开的逻辑视口内，右侧和底部保留额外余量。",
        28, 502, 370, 92
    )

    ui.create_card(
        hwnd, content_id,
        "交互区域",
        "可以展开每个输入框检查弹层位置。更新按钮会通过导出设置接口批量修改四个控件状态。",
        1,
        448, 116, 390, 116
    )

    g_tour_id = ui.create_tour(
        hwnd, content_id,
        [
            ("步骤一", "引导组件是普通纯绘制元素，内部带有上一步、下一步和关闭操作。"),
            ("步骤二", "它可以通过示例代码重新打开，并批量更新引导内容。"),
            ("步骤三", "引导卡片保持在初始窗口范围内，便于高缩放首次打开检查。"),
        ],
        0,
        True,
        448, 270, 390, 210
    )
    ui.dll.EU_SetTourOptions(hwnd, g_tour_id, 1, 1, 28, 146, 300, 40)

    ui.create_alert(
        hwnd, content_id,
        "首次打开尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}；内容底边 594，右边界 838。",
        0, 0, False,
        448, 516, 390, 62
    )

    for eid in (g_update_id, g_open_tour_id, g_select_v2_id, g_tree_select_id, g_tour_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("扩展选择器示例已显示。关闭窗口或等待 60 秒。")

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

    print("扩展选择器示例结束。")


if __name__ == "__main__":
    main()
