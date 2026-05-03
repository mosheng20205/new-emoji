import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_cascader_id = 0
g_search_id = 0
g_lazy_id = 0


OPTIONS = [
    ("浙江", "杭州", "西湖区"),
    ("浙江", "杭州", "滨江区"),
    ("浙江", "宁波", "海曙区"),
    ("江苏", "南京", "玄武区"),
    ("江苏", "苏州", "姑苏区"),
]


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 级联选择器完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_search_id:
        ui.set_cascader_search(g_hwnd, g_cascader_id, "杭州")
        ui.set_cascader_open(g_hwnd, g_cascader_id, True)
        print(f"[搜索] {ui.get_cascader_advanced_options(g_hwnd, g_cascader_id)}")
    elif element_id == g_lazy_id:
        ui.set_cascader_search(g_hwnd, g_cascader_id, "")
        ui.set_cascader_value(g_hwnd, g_cascader_id, ["浙江"])
        ui.set_cascader_open(g_hwnd, g_cascader_id, True)
        print(f"[懒加载] {ui.get_cascader_advanced_options(g_hwnd, g_cascader_id)}")


def main():
    global g_hwnd, g_cascader_id, g_search_id, g_lazy_id

    hwnd = ui.create_window("🧭 级联选择器完整验证", 240, 90, 760, 500)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 740, 450)

    ui.create_text(hwnd, content_id, "🧭 级联选择器：搜索与懒加载状态", 28, 24, 560, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证完整路径搜索、匹配数量、懒加载模式和弹层列数读回。",
        28, 66, 650, 46,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_cascader_id = ui.create_cascader(hwnd, content_id, OPTIONS, ["浙江", "杭州", "西湖区"], 28, 150, 300, 42)
    ui.set_cascader_advanced_options(hwnd, g_cascader_id, searchable=True, lazy_mode=True)
    ui.set_cascader_open(hwnd, g_cascader_id, True)

    g_search_id = ui.create_button(hwnd, content_id, "🔎", "搜索杭州", 380, 146, 160, 42)
    g_lazy_id = ui.create_button(hwnd, content_id, "⏳", "查看懒加载", 380, 204, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_search_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_lazy_id, on_click)

    ui.create_text(hwnd, content_id, "🌸 搜索模式显示完整路径；普通模式继续按省/市/区逐列展开。", 28, 388, 660, 32)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[初始] "
        f"打开={ui.get_cascader_open(hwnd, g_cascader_id)} "
        f"选中深度={ui.get_cascader_selected_depth(hwnd, g_cascader_id)} "
        f"层数={ui.get_cascader_level_count(hwnd, g_cascader_id)}"
    )
    print("级联选择器完整验证已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    did_search = False
    did_lazy = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not did_search and elapsed > 1.0:
            on_click(g_search_id)
            did_search = True
        if not did_lazy and elapsed > 3.0:
            on_click(g_lazy_id)
            did_lazy = True

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

    print(f"[结果] {ui.get_cascader_advanced_options(hwnd, g_cascader_id)}")
    print("级联选择器完整验证结束。")


if __name__ == "__main__":
    main()
