import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_segmented_id = 0
g_pageheader_id = 0
g_affix_id = 0
g_watermark_id = 0
g_update_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 页面工具组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        items = ui.make_utf8("概览|明细|趋势|日志")
        ui.dll.EU_SetSegmentedItems(g_hwnd, g_segmented_id, ui.bytes_arg(items), len(items))
        ui.dll.EU_SetSegmentedActive(g_hwnd, g_segmented_id, 2)

        title = ui.make_utf8("组件维护计划")
        subtitle = ui.make_utf8("当前批次已切换到页面工具类组件")
        ui.dll.EU_SetPageHeaderText(
            g_hwnd, g_pageheader_id,
            ui.bytes_arg(title), len(title),
            ui.bytes_arg(subtitle), len(subtitle)
        )

        affix_title = ui.make_utf8("固定工具条")
        affix_body = ui.make_utf8("用于展示始终可见的操作入口或状态摘要")
        ui.dll.EU_SetAffixText(
            g_hwnd, g_affix_id,
            ui.bytes_arg(affix_title), len(affix_title),
            ui.bytes_arg(affix_body), len(affix_body)
        )

        mark = ui.make_utf8("New Emoji UI")
        ui.dll.EU_SetWatermarkContent(g_hwnd, g_watermark_id, ui.bytes_arg(mark), len(mark))
        print(f"[更新] Segmented 当前选中：{ui.dll.EU_GetSegmentedActive(g_hwnd, g_segmented_id)}")
    elif element_id == g_segmented_id:
        print(f"[分段控制] 当前选中：{ui.dll.EU_GetSegmentedActive(g_hwnd, g_segmented_id)}")
    else:
        print(f"[页面工具组件] 点击元素 #{element_id}")


def main():
    global g_hwnd, g_segmented_id, g_pageheader_id, g_affix_id, g_watermark_id, g_update_id

    hwnd = ui.create_window("页面工具组件示例", 240, 90, 920, 650)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 900, 600)

    g_pageheader_id = ui.create_pageheader(
        hwnd, content_id,
        "页面工具组件",
        "Segmented / PageHeader / Affix / Watermark",
        "返回",
        28, 24, 820, 78
    )

    ui.create_text(hwnd, content_id, "分段控制", 28, 132, 120, 28)
    g_segmented_id = ui.create_segmented(
        hwnd, content_id,
        ["概览", "明细", "趋势"],
        0,
        28, 170, 360, 48
    )

    g_update_id = ui.create_button(
        hwnd, content_id,
        "",
        "更新组件状态",
        420, 174, 150, 40
    )

    ui.create_text(hwnd, content_id, "固定区域", 28, 252, 120, 28)
    g_affix_id = ui.create_affix(
        hwnd, content_id,
        "批次交付状态",
        "组件封装、导出绑定和 Python 示例已按规则拆分维护。",
        64,
        28, 292, 396, 112
    )

    ui.create_text(hwnd, content_id, "水印区域", 470, 252, 120, 28)
    ui.create_card(
        hwnd, content_id,
        "内容面板",
        "Watermark 组件覆盖在面板区域上方，用于展示低干扰的标识文字。这里保留足够尺寸用于首屏完整显示。",
        1,
        470, 292, 378, 220
    )
    g_watermark_id = ui.create_watermark(
        hwnd, content_id,
        "Element Plus",
        148,
        86,
        470, 292, 378, 220
    )

    ui.create_infobox(
        hwnd, content_id,
        "说明",
        "这批组件属于页面和工具类：分段控制、页头、固定区域和水印。示例窗口已按逻辑尺寸预留首屏余量。",
        28, 438, 396, 90
    )

    for eid in (g_segmented_id, g_update_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("页面工具组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("页面工具组件示例结束。")


if __name__ == "__main__":
    main()
