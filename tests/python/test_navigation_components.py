import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_breadcrumb_id = 0
g_tabs_line_id = 0
g_tabs_card_id = 0
g_pagination_id = 0
g_steps_id = 0
g_update_id = 0
g_vertical_steps_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 导航组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[Resize] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        ui.set_breadcrumb_items(g_hwnd, g_breadcrumb_id, ["🏠 首页", "🧩 组件", "🧭 导航", "✅ 状态"])
        ui.dll.EU_SetBreadcrumbCurrent(g_hwnd, g_breadcrumb_id, 3)
        ui.set_tabs_items(g_hwnd, g_tabs_line_id, ["📋 概览", "⚙️ 配置", "👥 角色", "🚀 发布", "📊 统计"])
        ui.set_tabs_type(g_hwnd, g_tabs_card_id, 1)
        ui.set_pagination(g_hwnd, g_pagination_id, 236, 12, 8)
        ui.set_steps_detail_items(
            g_hwnd,
            g_steps_id,
            [
                ("📝 填写", "准备表单"),
                ("🔎 审核", "校验内容"),
                ("🚀 发布", "推送上线"),
                ("📊 复盘", "查看结果"),
            ],
        )
        ui.dll.EU_SetStepsActive(g_hwnd, g_steps_id, 2)
        ui.set_steps_direction(g_hwnd, g_vertical_steps_id, 1)
        print(
            "[更新] 已切换导航组件状态",
            ui.get_breadcrumb_state(g_hwnd, g_breadcrumb_id),
            ui.get_tabs_state(g_hwnd, g_tabs_line_id),
            ui.get_pagination_state(g_hwnd, g_pagination_id),
            ui.get_steps_state(g_hwnd, g_steps_id),
        )
        return
    if element_id in (g_breadcrumb_id, g_tabs_line_id, g_tabs_card_id,
                      g_pagination_id, g_steps_id, g_vertical_steps_id):
        print(
            "[导航] "
            f"面包屑={ui.dll.EU_GetBreadcrumbCurrent(g_hwnd, g_breadcrumb_id)}/"
            f"{ui.dll.EU_GetBreadcrumbItemCount(g_hwnd, g_breadcrumb_id)}, "
            f"线形标签={ui.dll.EU_GetTabsActive(g_hwnd, g_tabs_line_id)}/"
            f"{ui.dll.EU_GetTabsItemCount(g_hwnd, g_tabs_line_id)}, "
            f"卡片标签={ui.dll.EU_GetTabsActive(g_hwnd, g_tabs_card_id)}, "
            f"页码={ui.dll.EU_GetPaginationCurrent(g_hwnd, g_pagination_id)}/"
            f"{ui.dll.EU_GetPaginationPageCount(g_hwnd, g_pagination_id)}, "
            f"步骤={ui.dll.EU_GetStepsActive(g_hwnd, g_steps_id)}/"
            f"{ui.dll.EU_GetStepsItemCount(g_hwnd, g_steps_id)}"
        )


def main():
    global g_hwnd, g_breadcrumb_id, g_tabs_line_id, g_tabs_card_id
    global g_pagination_id, g_steps_id, g_update_id, g_vertical_steps_id

    hwnd = ui.create_window("🧭 导航组件示例", 260, 120, 900, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 880, 630)

    ui.create_text(
        hwnd, content_id,
        "🧭 导航组件",
        28, 24, 420, 28
    )

    g_breadcrumb_id = ui.create_breadcrumb(
        hwnd, content_id,
        ["🏠 首页", "🧩 组件", "🧭 导航", "面包屑"],
        "›", 3,
        28, 68, 600, 34
    )
    assert ui.get_breadcrumb_state(hwnd, g_breadcrumb_id) == (3, 4)

    ui.create_text(hwnd, content_id, "📑 线形标签页", 28, 120, 160, 24)
    g_tabs_line_id = ui.create_tabs(
        hwnd, content_id,
        ["👤 用户", "⚙️ 配置", "🔐 角色", "✅ 任务"],
        1, 0,
        28, 150, 600, 42
    )
    assert ui.get_tabs_state(hwnd, g_tabs_line_id) == (1, 4, 0)

    ui.create_text(hwnd, content_id, "🗂️ 卡片标签页", 28, 210, 160, 24)
    g_tabs_card_id = ui.create_tabs(
        hwnd, content_id,
        ["今日", "本周", "本月"],
        0, 1,
        28, 240, 420, 42
    )
    assert ui.get_tabs_state(hwnd, g_tabs_card_id) == (0, 3, 1)

    ui.create_text(hwnd, content_id, "📄 分页", 28, 300, 160, 24)
    g_pagination_id = ui.create_pagination(
        hwnd, content_id,
        86, 10, 3,
        28, 330, 620, 42
    )
    assert ui.get_pagination_state(hwnd, g_pagination_id) == (86, 10, 3, 9)

    ui.create_text(hwnd, content_id, "🚦 横向步骤条", 28, 390, 180, 24)
    g_steps_id = ui.create_steps(
        hwnd, content_id,
        ["📝 填写", "🔎 审核", "🚀 发布", "📊 复盘"],
        1,
        28, 420, 620, 104
    )
    ui.set_steps_detail_items(
        hwnd,
        g_steps_id,
        [("📝 填写", "准备资料"), ("🔎 审核", "确认信息"), ("🚀 发布", "上线内容"), ("📊 复盘", "观察数据")],
    )
    assert ui.get_steps_state(hwnd, g_steps_id) == (1, 4, 0)

    ui.create_text(hwnd, content_id, "🧱 纵向步骤", 670, 68, 160, 24)
    g_vertical_steps_id = ui.create_steps(
        hwnd, content_id,
        ["收集", "处理", "完成"],
        1,
        670, 100, 180, 230
    )
    ui.set_steps_detail_items(
        hwnd,
        g_vertical_steps_id,
        [("📥 收集", "接收请求"), ("🛠️ 处理", "执行任务"), ("✅ 完成", "返回结果")],
    )
    ui.set_steps_direction(hwnd, g_vertical_steps_id, 1)
    assert ui.get_steps_state(hwnd, g_vertical_steps_id) == (1, 3, 1)

    g_update_id = ui.create_button(
        hwnd, content_id,
        "🔄",
        "更新导航状态",
        670, 360, 160, 40
    )
    ui.create_infobox(
        hwnd, content_id,
        "✅ 本批完善",
        "面包屑点击、标签页数量、分页页数、步骤描述与纵向布局都已开放 API。",
        28, 550, 620, 54
    )

    for eid in (g_breadcrumb_id, g_tabs_line_id, g_tabs_card_id,
                g_pagination_id, g_steps_id, g_vertical_steps_id, g_update_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[导航组件读回] "
        f"Breadcrumb={ui.get_breadcrumb_state(hwnd, g_breadcrumb_id)} "
        f"TabsLine={ui.get_tabs_state(hwnd, g_tabs_line_id)} "
        f"TabsCard={ui.get_tabs_state(hwnd, g_tabs_card_id)} "
        f"Pagination={ui.get_pagination_state(hwnd, g_pagination_id)} "
        f"Steps={ui.get_steps_state(hwnd, g_steps_id)} "
        f"VerticalSteps={ui.get_steps_state(hwnd, g_vertical_steps_id)}"
    )
    print("导航组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("导航组件示例结束。")


if __name__ == "__main__":
    main()
