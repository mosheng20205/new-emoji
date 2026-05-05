import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_carousel_id = 0
g_upload_id = 0
g_infinite_scroll_id = 0
g_update_id = 0
g_remove_id = 0
g_options_id = 0
g_image_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 内容媒体组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] {width}x{height}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_update_id:
        ui.set_carousel_items(g_hwnd, g_carousel_id, ["🏠 项目概览", "📤 上传进度", "🖼️ 图片预览", "🧭 滚动定位"])
        ui.dll.EU_SetCarouselActive(g_hwnd, g_carousel_id, 2)
        ui.dll.EU_SetCarouselOptions(g_hwnd, g_carousel_id, 1, 0, 1, 1)

        ui.set_upload_file_items(
            g_hwnd,
            g_upload_id,
            [
                ("产品截图.png", 1, 100),
                ("合同附件.pdf", 2, 68),
                ("图标资源.zip", 0, 0),
                ("发布说明.md", 3, 32),
            ],
        )

        ui.append_infinite_scroll_items(
            g_hwnd,
            g_infinite_scroll_id,
            [
                ("🧭 图片预览已更新", "用户切换到失败占位后记录状态", "新"),
                ("📤 上传队列刷新", "新增 4 个上传状态用于核对", "队列"),
            ],
        )
        ui.set_infinite_scroll_state(g_hwnd, g_infinite_scroll_id, loading=False, no_more=True)
        print(
            "[更新] 轮播当前页:",
            ui.dll.EU_GetCarouselActive(g_hwnd, g_carousel_id),
            "轮播数量:",
            ui.dll.EU_GetCarouselItemCount(g_hwnd, g_carousel_id),
            "上传文件:",
            ui.dll.EU_GetUploadFileCount(g_hwnd, g_upload_id),
            "无限滚动:",
            ui.get_infinite_scroll_full_state(g_hwnd, g_infinite_scroll_id),
        )
    elif element_id == g_remove_id:
        ui.dll.EU_RemoveUploadFile(g_hwnd, g_upload_id, 1)
        print("[上传] 删除第 2 个文件后剩余:", ui.dll.EU_GetUploadFileCount(g_hwnd, g_upload_id))
    elif element_id == g_options_id:
        ui.dll.EU_SetImageFit(g_hwnd, g_image_id, 1)
        ui.set_image_source(g_hwnd, g_image_id, "assets/missing-preview.png", "⚠️ 图片加载失败状态")
        print("[图片] 当前加载状态:", ui.dll.EU_GetImageStatus(g_hwnd, g_image_id))
    elif element_id == g_carousel_id:
        print("[轮播] 当前页:", ui.dll.EU_GetCarouselActive(g_hwnd, g_carousel_id))
    else:
        print(f"[内容媒体组件] 点击元素 #{element_id}")


def main():
    global g_hwnd, g_carousel_id, g_upload_id, g_infinite_scroll_id, g_update_id, g_remove_id, g_options_id, g_image_id

    hwnd = ui.create_window("🖼️ 内容媒体组件示例", 240, 90, 960, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 630)

    ui.create_text(hwnd, content_id, "🖼️ 图片预览", 28, 24, 160, 28)
    g_image_id = ui.create_image(
        hwnd, content_id,
        "assets/banner-preview.png",
        "示例图片：支持本地加载和失败占位 😀",
        0,
        28, 60, 250, 180
    )
    assert ui.get_image_options(hwnd, g_image_id) == (0, True, False, 2)

    ui.create_text(hwnd, content_id, "🎠 轮播展示", 318, 24, 180, 28)
    g_carousel_id = ui.create_carousel(
        hwnd, content_id,
        ["👋 欢迎页", "📊 数据看板", "📤 上传任务"],
        0,
        0,
        318, 60, 530, 200
    )
    ui.set_carousel_options(hwnd, g_carousel_id, True, 0, True, True)
    ui.set_carousel_autoplay(hwnd, g_carousel_id, False, 2500)
    assert ui.get_carousel_options(hwnd, g_carousel_id) == (True, 0, True, True, False, 2500)

    ui.create_text(hwnd, content_id, "📤 上传队列", 28, 260, 160, 28)
    g_upload_id = ui.create_upload(
        hwnd, content_id,
        "📤 点击或拖拽文件到此处上传",
        "支持等待、上传中、成功、失败状态",
        ["界面截图.png", "组件说明.docx", "emoji-资源.zip"],
        28, 296, 390, 210
    )
    assert ui.get_upload_file_status(hwnd, g_upload_id, 0) == (1, 100)

    ui.create_text(hwnd, content_id, "♾️ 无限滚动记录", 458, 260, 210, 28)
    g_infinite_scroll_id = ui.create_infinite_scroll(
        hwnd,
        content_id,
        [
            ("🖼️ 预览图已加载", "图片组件返回本地资源状态", "完成"),
            ("🎠 轮播已就绪", "支持循环、指示器和手动切换", "运行中"),
            ("📤 上传队列待处理", "等待用户确认资源清单", "等待"),
            ("🧾 媒体元数据同步", "记录文件类型、大小和状态", "同步"),
        ],
        458, 296, 360, 210,
    )
    ui.set_infinite_scroll_options(hwnd, g_infinite_scroll_id, 58, 8, 48, 1, True, True)
    state = ui.get_infinite_scroll_full_state(hwnd, g_infinite_scroll_id)
    assert state and state["item_count"] == 4 and state["style_mode"] == 1

    g_update_id = ui.create_button(
        hwnd, content_id,
        "🔄",
        "更新媒体状态",
        458, 520, 180, 40
    )
    g_remove_id = ui.create_button(
        hwnd, content_id,
        "🗑️",
        "删除上传项",
        652, 520, 140, 40
    )
    g_options_id = ui.create_button(
        hwnd, content_id,
        "🖼️",
        "切换图片状态",
        28, 590, 150, 34
    )
    ui.create_infobox(
        hwnd, content_id,
        "✅ 本批完善",
        "图片加载状态、轮播循环选项、上传队列状态和无限滚动读回均已开放 API。",
        196, 582, 500, 42
    )

    for eid in (g_carousel_id, g_update_id, g_remove_id, g_options_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[媒体组件读回] "
        f"Image={ui.get_image_options(hwnd, g_image_id)} "
        f"Carousel={ui.get_carousel_options(hwnd, g_carousel_id)} "
        f"Upload#1={ui.get_upload_file_status(hwnd, g_upload_id, 0)} "
        f"InfiniteScroll={ui.get_infinite_scroll_full_state(hwnd, g_infinite_scroll_id)}"
    )
    print("内容媒体组件示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("内容媒体组件示例结束。")


if __name__ == "__main__":
    main()
