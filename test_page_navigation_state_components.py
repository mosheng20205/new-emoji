import time
from ctypes import wintypes

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 页面工具状态组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def main():
    hwnd = ui.create_window("📌 页面工具状态组件", 120, 120, 980, 680)
    ui.dll.EU_SetThemeMode(hwnd, 0)
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    root = ui.create_panel(hwnd, 0, 0, 0, 940, 620, 0xFFF7F9FC)
    header = ui.create_pageheader(
        hwnd,
        root,
        "📄 页面详情",
        "补齐面包屑与操作区状态",
        "返回",
        24,
        24,
        880,
        82,
    )
    ui.set_pageheader_breadcrumbs(hwnd, header, ["🏠 首页", "🧩 组件", "页面头"])
    ui.set_pageheader_actions(hwnd, header, ["刷新", "保存"])

    affix = ui.create_affix(
        hwnd,
        root,
        "📌 固定提示",
        "滚动超过阈值后进入固定状态",
        96,
        24,
        130,
        360,
        96,
    )
    ui.set_affix_state(hwnd, affix, 140, 96)
    assert ui.get_affix_fixed(hwnd, affix) == 1
    assert ui.get_affix_state(hwnd, affix) == (140, 96, True)

    mark_panel = ui.create_panel(hwnd, root, 420, 130, 420, 260, 0xFFFFFFFF)
    ui.create_text(
        hwnd,
        mark_panel,
        "🔖 水印区域保留中文和 emoji，低透明度平铺显示",
        24,
        28,
        360,
        44,
    )
    watermark = ui.create_watermark(hwnd, mark_panel, "new_emoji 📌", 130, 78, 0, 0, 420, 260)
    ui.set_watermark_options(hwnd, watermark, 120, 72, -24, 62)
    assert ui.get_watermark_options(hwnd, watermark) == (120, 72, -24, 62)

    backtop = ui.create_backtop(hwnd, root, "↑", 842, 520, 48, 48)
    ui.set_backtop_state(hwnd, backtop, 80, 160, 0)
    assert ui.get_backtop_visible(hwnd, backtop) == 0
    ui.set_backtop_state(hwnd, backtop, 260, 160, 0)
    assert ui.get_backtop_visible(hwnd, backtop) == 1
    assert ui.get_backtop_state(hwnd, backtop) == (260, 160, 0)

    tour = ui.create_tour(
        hwnd,
        root,
        [("🧭 第一步", "查看固定提示状态"), ("🎯 第二步", "检查水印和返回顶部")],
        1,
        True,
        520,
        420,
        340,
        150,
    )
    ui.set_tour_options(hwnd, tour, open=True, mask=True, target=(420, 130, 220, 120))
    assert ui.get_tour_active(hwnd, tour) == 1
    assert ui.get_tour_open(hwnd, tour) == 1
    assert ui.get_tour_step_count(hwnd, tour) == 2
    assert ui.get_tour_options(hwnd, tour) == (True, True, 420, 130, 220, 120)

    ui.create_text(
        hwnd,
        root,
        "✅ 已验证：Backtop 阈值、Affix 固定状态、PageHeader 面包屑/操作区、水印选项和引导状态读回。",
        24,
        430,
        480,
        48,
    )

    print(
        "[页面工具读回] "
        f"Backtop={ui.get_backtop_state(hwnd, backtop)} 可见={ui.get_backtop_visible(hwnd, backtop)} "
        f"Affix={ui.get_affix_state(hwnd, affix)} "
        f"Watermark={ui.get_watermark_options(hwnd, watermark)} "
        f"Tour={ui.get_tour_options(hwnd, tour)} active={ui.get_tour_active(hwnd, tour)} steps={ui.get_tour_step_count(hwnd, tour)}"
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("页面工具状态组件示例已打开。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ui.ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < 60:
        handled = False
        while user32.PeekMessageW(ui.ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                running = False
                break
            user32.TranslateMessage(ui.ctypes.byref(msg))
            user32.DispatchMessageW(ui.ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)

    print("页面工具状态组件示例结束。")


if __name__ == "__main__":
    main()
