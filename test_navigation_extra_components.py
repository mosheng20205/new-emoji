import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dropdown_id = 0
g_menu_id = 0
g_anchor_id = 0
g_backtop_id = 0
g_update_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 扩展导航组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        menu_items = ui.make_utf8("总览|组件库|资源中心|更新日志")
        anchor_items = ui.make_utf8("总览|安装|组件|主题|发布")
        drop_items = ui.make_utf8("刷新数据|复制链接|导出报表|删除记录")
        ui.dll.EU_SetMenuItems(g_hwnd, g_menu_id, ui.bytes_arg(menu_items), len(menu_items))
        ui.dll.EU_SetMenuActive(g_hwnd, g_menu_id, 2)
        ui.dll.EU_SetAnchorItems(g_hwnd, g_anchor_id, ui.bytes_arg(anchor_items), len(anchor_items))
        ui.dll.EU_SetAnchorActive(g_hwnd, g_anchor_id, 3)
        ui.dll.EU_SetDropdownItems(g_hwnd, g_dropdown_id, ui.bytes_arg(drop_items), len(drop_items))
        ui.dll.EU_SetDropdownSelected(g_hwnd, g_dropdown_id, 1)
        print("[更新] 已更新菜单、锚点和下拉菜单")
    elif element_id == g_backtop_id:
        ui.dll.EU_SetAnchorActive(g_hwnd, g_anchor_id, 0)
        print("[返回顶部] 已把锚点切回第一项")
    elif element_id == g_menu_id:
        print(f"[菜单] 当前选中：{ui.dll.EU_GetMenuActive(g_hwnd, g_menu_id)}")
    elif element_id == g_anchor_id:
        print(f"[锚点] 当前选中：{ui.dll.EU_GetAnchorActive(g_hwnd, g_anchor_id)}")
    elif element_id == g_dropdown_id:
        print(f"[下拉菜单] 当前选中：{ui.dll.EU_GetDropdownSelected(g_hwnd, g_dropdown_id)}")
    else:
        print(f"[扩展导航组件] 点击元素 #{element_id}")


def main():
    global g_hwnd, g_dropdown_id, g_menu_id, g_anchor_id, g_backtop_id, g_update_id

    hwnd = ui.create_window("扩展导航组件示例", 240, 90, 920, 650)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 600)

    ui.create_text(hwnd, content_id, "扩展导航组件", 28, 24, 240, 28)
    ui.create_divider(hwnd, content_id, "Dropdown / Menu / Anchor / Backtop", 0, 1, 28, 62, 820, 34)

    g_menu_id = ui.create_menu(
        hwnd, content_id,
        ["首页", "组件库", "设计资源", "更新日志"],
        1,
        0,
        28, 116, 820, 54
    )

    ui.create_text(hwnd, content_id, "垂直菜单", 28, 204, 120, 28)
    ui.create_menu(
        hwnd, content_id,
        ["工作台", "项目管理", "成员权限", "系统设置"],
        0,
        1,
        28, 242, 220, 188
    )

    ui.create_text(hwnd, content_id, "锚点导航", 294, 204, 120, 28)
    g_anchor_id = ui.create_anchor(
        hwnd, content_id,
        ["总览", "安装", "组件", "主题", "发布"],
        2,
        294, 242, 220, 188
    )

    ui.create_text(hwnd, content_id, "下拉操作", 560, 204, 120, 28)
    g_dropdown_id = ui.create_dropdown(
        hwnd, content_id,
        "更多操作",
        ["查看详情", "编辑记录", "导出数据", "删除记录"],
        0,
        560, 242, 180, 40
    )

    g_update_id = ui.create_button(
        hwnd, content_id,
        "",
        "更新导航状态",
        560, 314, 150, 40
    )

    ui.create_infobox(
        hwnd, content_id,
        "示例说明",
        "点击菜单或锚点可以切换当前项；点击下拉菜单展开操作项；右下角按钮模拟返回顶部。",
        560, 384, 288, 92
    )

    g_backtop_id = ui.create_backtop(hwnd, content_id, "↑", 806, 512, 48, 48)

    for eid in (g_menu_id, g_anchor_id, g_dropdown_id, g_update_id, g_backtop_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("扩展导航组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("扩展导航组件示例结束。")


if __name__ == "__main__":
    main()
