import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 940
WINDOW_H = 680
CONTENT_W = 920
CONTENT_H = 630

g_hwnd = None
g_tag_id = 0
g_badge_id = 0
g_progress_id = 0
g_avatar_id = 0
g_empty_id = 0
g_skeleton_id = 0
g_apply_id = 0
g_reset_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 展示状态组件示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def print_state(prefix):
    print(
        f"{prefix} "
        f"标签={ui.get_tag_options(g_hwnd, g_tag_id)} "
        f"徽标隐藏={ui.get_badge_hidden(g_hwnd, g_badge_id)} "
        f"徽标选项={ui.get_badge_options(g_hwnd, g_badge_id)} "
        f"进度={ui.get_progress_percentage(g_hwnd, g_progress_id)} "
        f"进度选项={ui.get_progress_options(g_hwnd, g_progress_id)} "
        f"头像={ui.get_avatar_options(g_hwnd, g_avatar_id)} "
        f"头像图像={ui.get_avatar_image_status(g_hwnd, g_avatar_id)} "
        f"空状态操作={ui.get_empty_action_clicked(g_hwnd, g_empty_id)} "
        f"骨架={ui.get_skeleton_options(g_hwnd, g_skeleton_id)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_tag_type(g_hwnd, g_tag_id, 4)
        ui.set_tag_effect(g_hwnd, g_tag_id, 1)
        ui.set_tag_closable(g_hwnd, g_tag_id, True)
        ui.set_tag_closed(g_hwnd, g_tag_id, False)

        ui.set_badge_value(g_hwnd, g_badge_id, "0")
        ui.set_badge_options(g_hwnd, g_badge_id, dot=False, show_zero=False, offset_x=-6, offset_y=2)

        ui.set_progress_percentage(g_hwnd, g_progress_id, 86)
        ui.set_progress_status(g_hwnd, g_progress_id, 1)
        ui.set_progress_options(g_hwnd, g_progress_id, progress_type=1, stroke_width=10, show_text=True)

        ui.set_avatar_shape(g_hwnd, g_avatar_id, 1)
        ui.set_avatar_fit(g_hwnd, g_avatar_id, 1)
        ui.set_avatar_source(g_hwnd, g_avatar_id, r"T:\不存在的头像.png")

        ui.set_empty_description(g_hwnd, g_empty_id, "筛选后没有结果，稍后可以换一个关键词再试 🔎")
        ui.set_empty_options(g_hwnd, g_empty_id, "🧭", "重新筛选")
        ui.set_empty_action_clicked(g_hwnd, g_empty_id, True)

        ui.set_skeleton_options(g_hwnd, g_skeleton_id, rows=5, animated=False, loading=False, show_avatar=False)
        print_state("[应用展示状态]")
    elif element_id == g_reset_id:
        ui.set_tag_type(g_hwnd, g_tag_id, 1)
        ui.set_tag_effect(g_hwnd, g_tag_id, 0)
        ui.set_tag_closed(g_hwnd, g_tag_id, False)

        ui.set_badge_value(g_hwnd, g_badge_id, "128")
        ui.set_badge_options(g_hwnd, g_badge_id, dot=False, show_zero=True, offset_x=0, offset_y=0)

        ui.set_progress_percentage(g_hwnd, g_progress_id, 48)
        ui.set_progress_status(g_hwnd, g_progress_id, 2)
        ui.set_progress_options(g_hwnd, g_progress_id, progress_type=0, stroke_width=8, show_text=True)

        ui.set_avatar_shape(g_hwnd, g_avatar_id, 0)
        ui.set_avatar_fit(g_hwnd, g_avatar_id, 0)
        ui.set_avatar_source(g_hwnd, g_avatar_id, "")

        ui.set_empty_description(g_hwnd, g_empty_id, "当前列表暂时为空，点击操作按钮会记录状态 ✅")
        ui.set_empty_options(g_hwnd, g_empty_id, "📭", "创建内容")
        ui.set_empty_action_clicked(g_hwnd, g_empty_id, False)

        ui.set_skeleton_options(g_hwnd, g_skeleton_id, rows=4, animated=True, loading=True, show_avatar=True)
        print_state("[恢复展示状态]")


def main():
    global g_hwnd, g_tag_id, g_badge_id, g_progress_id, g_avatar_id
    global g_empty_id, g_skeleton_id, g_apply_id, g_reset_id

    hwnd = ui.create_window("🎛️ 展示状态组件测试", 220, 90, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "🎛️ Tag / Badge / Progress / Avatar / Empty / Skeleton", 28, 22, 680, 32)
    ui.create_divider(hwnd, content_id, "展示状态、数据读回、中文 emoji 与首次窗口尺寸适配", 0, 1, 28, 62, 840, 30)

    ui.create_text(hwnd, content_id, "🏷️ 标签与徽标", 28, 112, 180, 26)
    g_tag_id = ui.create_tag(hwnd, content_id, "新品 🏷️", 1, 0, True, 28, 146, 160, 34)
    g_badge_id = ui.create_badge(hwnd, content_id, "消息中心 🔔", "128", 99, False, 216, 146, 260, 36)

    ui.create_text(hwnd, content_id, "📈 进度与头像", 28, 220, 180, 26)
    g_progress_id = ui.create_progress(
        hwnd, content_id, "完成率", 48, 2, 28, 254, 360, 38,
        progress_type=0, stroke_width=8, show_text=True
    )
    g_avatar_id = ui.create_avatar(hwnd, content_id, "小易 😊", 0, 420, 238, 76, 76)

    ui.create_text(hwnd, content_id, "📭 空状态与骨架", 28, 338, 200, 26)
    g_empty_id = ui.create_empty(
        hwnd, content_id,
        "暂无数据 📭",
        "当前列表暂时为空，点击操作按钮会记录状态 ✅",
        28, 372, 360, 140,
        icon="📭",
        action="创建内容",
    )
    g_skeleton_id = ui.create_skeleton(
        hwnd, content_id,
        4,
        True,
        420,
        372,
        360,
        140,
        loading=True,
        show_avatar=True,
    )

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "应用展示状态", 420, 548, 160, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "↩", "恢复默认状态", 600, 548, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_alert(
        hwnd,
        content_id,
        "📐 首屏尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 780，最下内容约 590，保留 20px 以上余量。",
        0,
        0,
        False,
        28,
        548,
        360,
        62,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print_state("[初始展示状态]")
    print("展示状态组件测试窗口已显示，请观察 60 秒或手动关闭。")

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
