import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tree_select_id = 0
g_search_id = 0
g_multi_id = 0
g_clear_id = 0


TREE_ITEMS = [
    ("📦 组件库", 0, True),
    ("🧱 基础组件", 1, True),
    ("🔘 按钮", 2, True),
    ("📝 输入框", 2, True),
    ("🌲 复杂选择", 1, True),
    ("🌳 树选择器", 2, True),
    ("🔀 穿梭框", 2, True),
    ("🔎 自动补全", 2, True),
    ("📊 数据展示", 1, True),
]


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 树选择器完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_search_id:
        ui.set_tree_select_search(g_hwnd, g_tree_select_id, "树")
        ui.set_tree_select_open(g_hwnd, g_tree_select_id, True)
        print(
            "[搜索] "
            f"文本={ui.get_tree_select_search(g_hwnd, g_tree_select_id)} "
            f"匹配={ui.get_tree_select_options(g_hwnd, g_tree_select_id)['matched_count']}"
        )
    elif element_id == g_multi_id:
        ui.set_tree_select_selected_items(g_hwnd, g_tree_select_id, [2, 5, 7])
        options = ui.get_tree_select_options(g_hwnd, g_tree_select_id)
        print(
            "[多选] "
            f"已选={options['selected_count']} "
            f"第2项={ui.get_tree_select_selected_item(g_hwnd, g_tree_select_id, 1)} "
            f"单选读回={ui.get_tree_select_selected(g_hwnd, g_tree_select_id)}"
        )
    elif element_id == g_clear_id:
        ui.clear_tree_select(g_hwnd, g_tree_select_id)
        print(
            "[清空] "
            f"已选={ui.get_tree_select_selected_count(g_hwnd, g_tree_select_id)} "
            f"选中={ui.get_tree_select_selected(g_hwnd, g_tree_select_id)}"
        )


def main():
    global g_hwnd, g_tree_select_id, g_search_id, g_multi_id, g_clear_id

    hwnd = ui.create_window("🌳 树选择器完整验证", 240, 90, 760, 520)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 740, 470)

    ui.create_text(hwnd, content_id, "🌳 树选择器：搜索、多选、清空", 28, 24, 520, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证树选择器弹层搜索、多个节点勾选、清空选择、展开状态和选项读回。",
        28, 66, 650, 46,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "🌲 选择组件", 28, 132, 160, 28)
    g_tree_select_id = ui.create_tree_select(hwnd, content_id, TREE_ITEMS, 5, 28, 168, 340, 40)
    ui.set_tree_select_options(hwnd, g_tree_select_id, multiple=True, clearable=True, searchable=True)
    ui.set_tree_select_open(hwnd, g_tree_select_id, True)

    g_search_id = ui.create_button(hwnd, content_id, "🔎", "搜索“树”", 420, 164, 170, 42)
    g_multi_id = ui.create_button(hwnd, content_id, "✅", "设置多选", 420, 222, 170, 42)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空选择", 420, 280, 170, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_search_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_multi_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_clear_id, on_click)

    ui.create_text(hwnd, content_id, "⌨️ 打开弹层后可用方向键移动，空格勾选，Delete 清空。", 28, 430, 620, 32)

    ui.dll.EU_ShowWindow(hwnd, 1)
    ui.dll.EU_SetElementFocus(hwnd, g_tree_select_id)
    print(
        "[初始] "
        f"打开={ui.get_tree_select_open(hwnd, g_tree_select_id)} "
        f"配置={ui.get_tree_select_options(hwnd, g_tree_select_id)}"
    )
    print("树选择器完整验证已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    did_search = False
    did_multi = False
    did_clear = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not did_search and elapsed > 1.0:
            on_click(g_search_id)
            did_search = True
        if not did_multi and elapsed > 2.0:
            on_click(g_multi_id)
            did_multi = True
        if not did_clear and elapsed > 4.0:
            on_click(g_clear_id)
            did_clear = True

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

    final_options = ui.get_tree_select_options(hwnd, g_tree_select_id)
    print(f"[结果] {final_options}")
    print("树选择器完整验证结束。")


if __name__ == "__main__":
    main()
