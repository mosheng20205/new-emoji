import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tag_id = 0
g_badge_id = 0
g_progress_bar_id = 0
g_progress_circle_id = 0
g_avatar_id = 0
g_empty_id = 0
g_skeleton_id = 0
g_apply_id = 0
g_reset_id = 0


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 展示状态组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.dll.EU_SetTagClosed(g_hwnd, g_tag_id, 0)
        ui.dll.EU_SetTagClosable(g_hwnd, g_tag_id, 1)
        ui.dll.EU_SetBadgeValue(g_hwnd, g_badge_id, *utf8_arg("0"))
        ui.dll.EU_SetBadgeOptions(g_hwnd, g_badge_id, 0, 0, -8, 2)
        ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_bar_id, 82)
        ui.dll.EU_SetProgressStatus(g_hwnd, g_progress_bar_id, 1)
        ui.dll.EU_SetProgressOptions(g_hwnd, g_progress_circle_id, 1, 8, 1)
        ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_circle_id, 68)
        ui.dll.EU_SetAvatarSource(g_hwnd, g_avatar_id, *utf8_arg("不存在的头像.png"))
        ui.dll.EU_SetAvatarFit(g_hwnd, g_avatar_id, 1)
        ui.dll.EU_SetEmptyDescription(g_hwnd, g_empty_id, *utf8_arg("当前筛选条件下没有结果，换个关键词试试。"))
        ui.dll.EU_SetEmptyOptions(g_hwnd, g_empty_id, *utf8_arg("🔎"), *utf8_arg("清空筛选"))
        ui.dll.EU_SetSkeletonOptions(g_hwnd, g_skeleton_id, 4, 1, 1, 0)
        print(
            "[应用] "
            f"标签关闭={ui.dll.EU_GetTagClosed(g_hwnd, g_tag_id)} "
            f"徽标隐藏={ui.dll.EU_GetBadgeHidden(g_hwnd, g_badge_id)} "
            f"进度={ui.dll.EU_GetProgressPercentage(g_hwnd, g_progress_bar_id)} "
            f"头像状态={ui.dll.EU_GetAvatarImageStatus(g_hwnd, g_avatar_id)} "
            f"骨架加载={ui.dll.EU_GetSkeletonLoading(g_hwnd, g_skeleton_id)}"
        )
    elif element_id == g_reset_id:
        ui.dll.EU_SetTagClosed(g_hwnd, g_tag_id, 0)
        ui.dll.EU_SetBadgeValue(g_hwnd, g_badge_id, *utf8_arg("128"))
        ui.dll.EU_SetBadgeOptions(g_hwnd, g_badge_id, 0, 1, 0, 0)
        ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_bar_id, 45)
        ui.dll.EU_SetProgressStatus(g_hwnd, g_progress_bar_id, 2)
        ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_circle_id, 36)
        ui.dll.EU_SetAvatarSource(g_hwnd, g_avatar_id, *utf8_arg(""))
        ui.dll.EU_SetEmptyDescription(g_hwnd, g_empty_id, *utf8_arg("暂无内容，可稍后刷新。"))
        ui.dll.EU_SetEmptyOptions(g_hwnd, g_empty_id, *utf8_arg("📭"), *utf8_arg("刷新"))
        ui.dll.EU_SetSkeletonOptions(g_hwnd, g_skeleton_id, 3, 1, 0, 1)
        print("[重置] 展示状态组件已恢复默认")


def main():
    global g_hwnd, g_tag_id, g_badge_id, g_progress_bar_id, g_progress_circle_id
    global g_avatar_id, g_empty_id, g_skeleton_id, g_apply_id, g_reset_id

    hwnd = ui.create_window("🏷️ 展示状态组件测试", 220, 120, 940, 680)
    if not hwnd:
        print("ERROR: failed to create window")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 630)

    ui.create_text(hwnd, content_id, "🎯 展示与状态组件", 24, 18, 300, 30)
    ui.create_divider(hwnd, content_id, "标签 / 徽标 / 进度 / 头像 / 空状态 / 骨架屏", 0, 1, 24, 56, 860, 26)

    ui.create_text(hwnd, content_id, "🏷️ 标签与徽标", 24, 94, 200, 26)
    g_tag_id = ui.create_tag(hwnd, content_id, "可关闭标签 ✨", 1, 0, True, 24, 128, 170, 34)
    g_badge_id = ui.create_badge(
        hwnd, content_id, "消息提醒 🔔", "128", 99, False,
        220, 128, 250, 36, show_zero=True
    )

    ui.create_text(hwnd, content_id, "📈 进度状态", 24, 190, 200, 26)
    g_progress_bar_id = ui.create_progress(
        hwnd, content_id, "同步进度 🚀", 45, 2,
        24, 224, 430, 38, stroke_width=10, show_text=True
    )
    g_progress_circle_id = ui.create_progress(
        hwnd, content_id, "", 36, 0,
        500, 128, 130, 130, progress_type=1, stroke_width=8, show_text=True
    )

    ui.create_text(hwnd, content_id, "👤 头像状态", 674, 94, 180, 26)
    g_avatar_id = ui.create_avatar(
        hwnd, content_id, "易", 0,
        690, 130, 86, 86, fit=1
    )
    ui.create_text(hwnd, content_id, "图片失败时会回退到文字头像。", 638, 226, 250, 26)

    ui.create_text(hwnd, content_id, "📭 空状态", 24, 300, 180, 26)
    g_empty_id = ui.create_empty(
        hwnd, content_id,
        "暂无数据 📭", "暂无内容，可稍后刷新。",
        24, 334, 400, 170, icon="📭", action="刷新"
    )

    ui.create_text(hwnd, content_id, "💤 骨架屏", 470, 300, 180, 26)
    g_skeleton_id = ui.create_skeleton(
        hwnd, content_id, 3, True,
        470, 334, 360, 130, loading=True, show_avatar=True
    )

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "应用演示状态", 470, 520, 170, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "🔄", "恢复默认状态", 658, 520, 170, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "🧪 验证重点",
        "本窗口覆盖标签关闭状态、徽标隐藏零值与偏移、圆形进度、头像图片失败回退、空状态操作按钮和骨架屏加载切换。",
        24, 520, 410, 86
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("展示状态组件测试窗口已显示，60 秒后自动结束。")

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

    print("展示状态组件测试结束。")


if __name__ == "__main__":
    main()
