import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_image_id = 0
g_carousel_id = 0
g_upload_id = 0
g_infinite_scroll_id = 0
g_preview_id = 0
g_next_id = 0
g_retry_id = 0
g_clear_id = 0
g_scroll_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 媒体工具增强示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_preview_id:
        next_open = not bool(ui.get_image_preview_open(g_hwnd, g_image_id))
        ui.set_image_preview(g_hwnd, g_image_id, next_open)
        print("[图片] 预览打开:", ui.get_image_preview_open(g_hwnd, g_image_id))
    elif element_id == g_next_id:
        ui.carousel_advance(g_hwnd, g_carousel_id, 1)
        print("[走马灯] 当前页:", ui.dll.EU_GetCarouselActive(g_hwnd, g_carousel_id))
    elif element_id == g_retry_id:
        ui.retry_upload_file(g_hwnd, g_upload_id, 1)
        print("[上传] 第2项已重试，文件数:", ui.dll.EU_GetUploadFileCount(g_hwnd, g_upload_id))
    elif element_id == g_clear_id:
        ui.clear_upload_files(g_hwnd, g_upload_id)
        print("[上传] 已清空，文件数:", ui.dll.EU_GetUploadFileCount(g_hwnd, g_upload_id))
    elif element_id == g_scroll_id:
        ui.set_infinite_scroll_scroll(g_hwnd, g_infinite_scroll_id, 120)
        print("[无限滚动] 当前状态:", ui.get_infinite_scroll_full_state(g_hwnd, g_infinite_scroll_id))


def main():
    global g_hwnd, g_image_id, g_carousel_id, g_upload_id, g_infinite_scroll_id
    global g_preview_id, g_next_id, g_retry_id, g_clear_id, g_scroll_id

    hwnd = ui.create_window("🖼️ 媒体工具增强组件", 220, 80, 1040, 700)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1020, 650)

    ui.create_text(hwnd, content_id, "🖼️ 媒体工具增强组件", 28, 24, 360, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐图片预览、走马灯推进/自动播放标记、上传失败重试/清空，以及无限滚动列表 API。",
        28, 68, 900, 46,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "🖼️ 图片预览", 28, 134, 180, 28)
    g_image_id = ui.create_image(
        hwnd, content_id,
        "",
        "🖼️ 图片预览占位：可通过 API 打开预览层",
        0,
        28, 170, 280, 205,
    )
    ui.set_image_preview_enabled(hwnd, g_image_id, True)
    assert ui.get_image_options(hwnd, g_image_id) == (0, True, False, 0)

    ui.create_text(hwnd, content_id, "🎬 走马灯", 340, 134, 180, 28)
    g_carousel_id = ui.create_carousel(
        hwnd, content_id,
        ["📌 项目看板", "📤 上传队列", "🖼️ 资源预览", "🧭 滚动定位"],
        0,
        0,
        340, 170, 570, 205,
    )
    ui.set_carousel_options(g_hwnd, g_carousel_id, True, 0, True, True)
    ui.set_carousel_autoplay(hwnd, g_carousel_id, True, 2000)
    assert ui.get_carousel_options(hwnd, g_carousel_id) == (True, 0, True, True, True, 2000)

    ui.create_text(hwnd, content_id, "📤 上传队列", 28, 405, 180, 28)
    g_upload_id = ui.create_upload(
        hwnd, content_id,
        "📤 选择资源并加入上传队列",
        "支持等待、上传中、成功、失败和重试状态",
        [],
        28, 440, 420, 170,
    )
    ui.set_upload_file_items(
        hwnd,
        g_upload_id,
        [
            ("封面图.png", 1, 100),
            ("品牌素材.zip", 3, 42),
            ("演示视频.mp4", 2, 65),
        ],
    )
    assert ui.get_upload_file_status(hwnd, g_upload_id, 1) == (3, 42)

    ui.create_text(hwnd, content_id, "♾️ 无限滚动任务", 500, 405, 220, 28)
    g_infinite_scroll_id = ui.create_infinite_scroll(
        hwnd,
        content_id,
        [
            ("🖼️ 打开预览层", "图片预览覆盖层可用", "预览"),
            ("🎬 推进走马灯", "按钮和自动推进都会更新状态", "轮播"),
            ("📤 重试失败上传", "失败文件可重试并读回状态", "上传"),
            ("🧹 清空上传队列", "清空后保持界面稳定", "队列"),
            ("♾️ 滚动到底部", "触底后由回调追加数据", "加载"),
        ],
        500, 440, 386, 170,
    )
    ui.set_infinite_scroll_options(hwnd, g_infinite_scroll_id, 48, 6, 40, 2, True, True)
    assert ui.get_infinite_scroll_full_state(hwnd, g_infinite_scroll_id)["item_count"] == 5

    g_preview_id = ui.create_button(hwnd, content_id, "🔍", "打开预览", 28, 620, 120, 36)
    g_next_id = ui.create_button(hwnd, content_id, "⏭️", "下一页", 164, 620, 110, 36)
    g_retry_id = ui.create_button(hwnd, content_id, "🔁", "重试失败", 290, 620, 120, 36)
    g_clear_id = ui.create_button(hwnd, content_id, "🧹", "清空队列", 426, 620, 120, 36)
    g_scroll_id = ui.create_button(hwnd, content_id, "⬇️", "滚动一步", 562, 620, 120, 36)
    for eid in (g_preview_id, g_next_id, g_retry_id, g_clear_id, g_scroll_id):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print(
        "[媒体工具读回] "
        f"Image={ui.get_image_options(hwnd, g_image_id)} "
        f"Carousel={ui.get_carousel_options(hwnd, g_carousel_id)} "
        f"Upload#2={ui.get_upload_file_status(hwnd, g_upload_id, 1)} "
        f"InfiniteScroll={ui.get_infinite_scroll_full_state(hwnd, g_infinite_scroll_id)}"
    )
    print("媒体工具增强示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_next = 0
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if elapsed > 1.0 and auto_next < 3:
            ui.carousel_advance(g_hwnd, g_carousel_id, 1)
            auto_next += 1
            print("[自动推进] 走马灯当前页:", ui.dll.EU_GetCarouselActive(g_hwnd, g_carousel_id))
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

    print("媒体工具增强示例结束。")


if __name__ == "__main__":
    main()
