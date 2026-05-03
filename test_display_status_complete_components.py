import ctypes
from ctypes import wintypes
import os
import time

import test_new_emoji as ui


WINDOW_W = 980
WINDOW_H = 700
CONTENT_W = 950
CONTENT_H = 650

g_hwnd = None
g_tag_id = 0
g_empty_id = 0
g_badge_id = 0
g_progress_id = 0
g_skeleton_id = 0
g_apply_id = 0
g_reset_id = 0
g_tag_close_count = 0
g_empty_action_count = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 展示状态完成度测试正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_tag_close(element_id):
    global g_tag_close_count
    g_tag_close_count += 1
    print(f"[标签关闭回调] 元素={element_id} 次数={g_tag_close_count}")


@ui.ClickCallback
def on_empty_action(element_id):
    global g_empty_action_count
    g_empty_action_count += 1
    print(f"[空状态操作回调] 元素={element_id} 次数={g_empty_action_count}")


def dump_state(prefix):
    print(
        f"{prefix} "
        f"标签={ui.get_tag_options(g_hwnd, g_tag_id)} "
        f"标签视觉={ui.get_tag_visual_options(g_hwnd, g_tag_id)} "
        f"徽标={ui.get_badge_options(g_hwnd, g_badge_id)} "
        f"徽标布局={ui.get_badge_layout_options(g_hwnd, g_badge_id)} "
        f"进度={ui.get_progress_percentage(g_hwnd, g_progress_id)} "
        f"进度格式={ui.get_progress_format_options(g_hwnd, g_progress_id)} "
        f"骨架={ui.get_skeleton_options(g_hwnd, g_skeleton_id)} "
        f"空状态点击={ui.get_empty_action_clicked(g_hwnd, g_empty_id)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_tag_closed(g_hwnd, g_tag_id, False)
        ui.set_tag_size(g_hwnd, g_tag_id, 2)
        ui.set_tag_theme_color(g_hwnd, g_tag_id, 0xFF8E44AD)
        ui.set_badge_value(g_hwnd, g_badge_id, "0")
        ui.set_badge_options(g_hwnd, g_badge_id, dot=False, show_zero=False, offset_x=-10, offset_y=4)
        ui.set_badge_layout_options(g_hwnd, g_badge_id, placement=2, standalone=False)
        ui.set_progress_percentage(g_hwnd, g_progress_id, 76)
        ui.set_progress_status(g_hwnd, g_progress_id, 1)
        ui.set_progress_format_options(g_hwnd, g_progress_id, text_format=1, striped=True)
        ui.set_empty_options(g_hwnd, g_empty_id, "🧭", "重新筛选")
        ui.set_empty_action_clicked(g_hwnd, g_empty_id, False)
        ui.set_skeleton_options(g_hwnd, g_skeleton_id, rows=5, animated=True, loading=True, show_avatar=True)
        dump_state("[应用完成状态]")
    elif element_id == g_reset_id:
        ui.set_tag_closed(g_hwnd, g_tag_id, False)
        ui.set_tag_size(g_hwnd, g_tag_id, 1)
        ui.set_tag_theme_color(g_hwnd, g_tag_id, 0)
        ui.set_badge_value(g_hwnd, g_badge_id, "128")
        ui.set_badge_options(g_hwnd, g_badge_id, dot=False, show_zero=True, offset_x=0, offset_y=0)
        ui.set_badge_layout_options(g_hwnd, g_badge_id, placement=0, standalone=False)
        ui.set_progress_percentage(g_hwnd, g_progress_id, 42)
        ui.set_progress_status(g_hwnd, g_progress_id, 2)
        ui.set_progress_format_options(g_hwnd, g_progress_id, text_format=2, striped=False)
        ui.set_skeleton_options(g_hwnd, g_skeleton_id, rows=4, animated=False, loading=False, show_avatar=False)
        dump_state("[恢复完成状态]")


def main():
    global g_hwnd, g_tag_id, g_empty_id, g_badge_id, g_progress_id
    global g_skeleton_id, g_apply_id, g_reset_id

    hwnd = ui.create_window("🏁 展示状态组件完成验证", 180, 80, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "🏁 展示状态组件完成验证", 28, 20, 360, 34)
    ui.create_divider(hwnd, content_id, "标签 / 徽标 / 进度 / 头像 / 空状态 / 骨架屏", 0, 1, 28, 62, 880, 30)

    ui.create_text(hwnd, content_id, "🏷️ 标签：尺寸、主题色、关闭回调", 28, 112, 330, 28)
    g_tag_id = ui.create_tag(hwnd, content_id, "可关闭完成标签 ✨", 1, 0, True, 28, 150, 210, 38)
    ui.set_tag_close_callback(hwnd, g_tag_id, on_tag_close)
    ui.set_tag_size(hwnd, g_tag_id, 1)

    ui.create_text(hwnd, content_id, "🔔 徽标：零值隐藏、四角定位、独立布局", 300, 112, 420, 28)
    g_badge_id = ui.create_badge(
        hwnd, content_id, "消息中心 🔔", "128", 99, False,
        300, 150, 300, 40, show_zero=True, placement=0, standalone=False
    )
    ui.create_badge(
        hwnd, content_id, "", "9", 99, False,
        628, 150, 58, 32, placement=1, standalone=True
    )

    ui.create_text(hwnd, content_id, "📈 进度：中文状态文本、条纹、圆形模式", 28, 230, 420, 28)
    g_progress_id = ui.create_progress(
        hwnd, content_id, "部署进度 🚀", 42, 2, 28, 268, 520, 42,
        progress_type=0, stroke_width=12, show_text=True, text_format=2, striped=False
    )
    ui.create_progress(
        hwnd, content_id, "", 88, 1, 594, 224, 120, 120,
        progress_type=1, stroke_width=10, show_text=True, text_format=1
    )

    ui.create_text(hwnd, content_id, "👤 头像：图片失败回退、圆形/方形、适配读回", 28, 358, 450, 28)
    ui.create_avatar(hwnd, content_id, "易 😊", 0, 28, 396, 78, 78, source=r"T:\不存在的头像.png", fit=1)
    ui.create_avatar(hwnd, content_id, "设", 1, 126, 396, 78, 78, fit=2)

    ui.create_text(hwnd, content_id, "📭 空状态与骨架屏：操作回调、加载切换、真实闪动", 300, 358, 520, 28)
    g_empty_id = ui.create_empty(
        hwnd, content_id,
        "暂无记录 📭",
        "当前没有匹配结果，操作按钮会触发专用回调 ✅",
        300, 396, 300, 150,
        icon="📭",
        action="创建记录",
    )
    ui.set_empty_action_callback(hwnd, g_empty_id, on_empty_action)
    g_skeleton_id = ui.create_skeleton(
        hwnd, content_id, 4, True, 628, 396, 280, 150,
        loading=True, show_avatar=True
    )

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "应用完成状态", 300, 576, 170, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "🔄", "恢复默认状态", 490, 576, 170, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "📐 首次窗口尺寸检查",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 908，最下内容约 618，保留 20px 以上余量。",
        28, 564, 250, 70
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[窗口] 展示状态完成验证窗口已显示", flush=True)
    dump_state("[初始完成状态]")
    duration = int(os.environ.get("EU_TEST_SECONDS", "30"))
    print(f"展示状态完成验证窗口已显示，请观察 {duration} 秒或手动关闭。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < duration:
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

    ui.dll.EU_DestroyWindow(hwnd)
    print("展示状态完成验证结束。")


if __name__ == "__main__":
    main()
