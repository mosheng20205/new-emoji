import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tree_id = 0
g_tree_select_id = 0
g_transfer_id = 0
g_update_id = 0
g_toggle_id = 0


TREE_ITEMS = [
    ("📦 组件库", 0, True),
    ("基础组件", 1, True),
    ("按钮 Button", 2, True),
    ("图标 Icon", 2, True),
    ("选择组件", 1, True),
    ("树 Tree", 2, True),
    ("树选择 TreeSelect", 2, True),
    ("穿梭框 Transfer", 2, True),
]


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 选择状态组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_toggle_id:
        ui.toggle_tree_item_expanded(g_hwnd, g_tree_id, 1)
        ui.toggle_tree_select_item_expanded(g_hwnd, g_tree_select_id, 4)
        ui.set_tree_select_open(g_hwnd, g_tree_select_id, True)
        print(
            "[展开] "
            f"树可见={ui.get_tree_visible_count(g_hwnd, g_tree_id)} "
            f"树选择打开={ui.get_tree_select_open(g_hwnd, g_tree_select_id)} "
            f"选择分组展开={ui.get_tree_select_item_expanded(g_hwnd, g_tree_select_id, 4)}"
        )
    elif element_id == g_update_id:
        ui.set_tree_selected(g_hwnd, g_tree_id, 6)
        ui.set_tree_select_selected(g_hwnd, g_tree_select_id, 7)
        ui.set_transfer_selected(g_hwnd, g_transfer_id, 0, 2)
        ui.transfer_move_right(g_hwnd, g_transfer_id)
        ui.set_transfer_selected(g_hwnd, g_transfer_id, 1, 0)
        ui.transfer_move_left(g_hwnd, g_transfer_id)
        print(
            "[选择] "
            f"树={ui.get_tree_selected(g_hwnd, g_tree_id)} "
            f"树选择={ui.get_tree_select_selected(g_hwnd, g_tree_select_id)} "
            f"左侧={ui.get_transfer_count(g_hwnd, g_transfer_id, 0)} "
            f"右侧={ui.get_transfer_count(g_hwnd, g_transfer_id, 1)} "
            f"左选中={ui.get_transfer_selected(g_hwnd, g_transfer_id, 0)} "
            f"右选中={ui.get_transfer_selected(g_hwnd, g_transfer_id, 1)}"
        )


def main():
    global g_hwnd, g_tree_id, g_tree_select_id, g_transfer_id, g_update_id, g_toggle_id

    hwnd = ui.create_window("🌲 复杂选择状态示例", 220, 80, 980, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 960, 630)

    ui.create_text(hwnd, content_id, "🌲 Tree / TreeSelect / Transfer", 28, 24, 520, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐复杂选择类的状态 API：树节点展开、可见数量、树选择弹层开关，以及穿梭框选中项和左右数量读取。",
        28, 68, 800, 48,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_tree_id = ui.create_tree(hwnd, content_id, TREE_ITEMS, 5, 28, 134, 360, 280)
    ui.create_text(hwnd, content_id, "🌳 树选择", 430, 134, 160, 28)
    g_tree_select_id = ui.create_tree_select(hwnd, content_id, TREE_ITEMS, 5, 430, 172, 280, 38)

    g_toggle_id = ui.create_button(hwnd, content_id, "🔁", "切换展开", 740, 168, 150, 42)
    g_update_id = ui.create_button(hwnd, content_id, "🚀", "移动并读取", 740, 226, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_toggle_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.create_divider(hwnd, content_id, "🔀 穿梭框", 0, 0, 28, 432, 862, 32)
    g_transfer_id = ui.create_transfer(
        hwnd,
        content_id,
        ["北京", "上海", "杭州", "广州", "深圳"],
        ["成都", "南京"],
        28, 478, 862, 130,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("选择状态组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_toggle = False
    auto_update = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_toggle and elapsed > 1.0:
            on_click(g_toggle_id)
            auto_toggle = True
        if not auto_update and elapsed > 2.0:
            on_click(g_update_id)
            auto_update = True
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

    print("选择状态组件示例结束。")


if __name__ == "__main__":
    main()
