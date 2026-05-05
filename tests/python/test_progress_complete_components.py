import ctypes
from ctypes import wintypes
import os
import time

import test_new_emoji as ui


def require(name, condition):
    if not condition:
        raise RuntimeError(f"Progress 验证失败：{name}")


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages(seconds=0.5):
    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    while time.time() - start < seconds:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                return
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def main():
    hwnd = ui.create_window("📈 Progress 进度条全样式验证", 260, 120, 940, 620)
    require("窗口创建", bool(hwnd))
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 900, 560)

    base = ui.create_progress(hwnd, root, "📦 构建进度", -20, 0, 28, 36, 380, 34)
    require("百分比下限钳制", ui.get_progress_percentage(hwnd, base) == 0)
    ui.set_progress_percentage(hwnd, base, 128)
    require("百分比上限钳制", ui.get_progress_percentage(hwnd, base) == 100)

    for index, status in enumerate([0, 1, 2, 3]):
        eid = ui.create_progress(hwnd, root, f"状态 {status}", 50 + index * 10, status, 28, 88 + index * 42, 380, 34)
        require(f"状态读回 {status}", ui.get_progress_status(hwnd, eid) == status)

    inside = ui.create_progress(
        hwnd, root, "🚀 发布", 70, 0, 450, 36, 380, 36,
        stroke_width=26, text_inside=True, fill_color=0xFF409EFF, track_color=0xFFE4E7ED
    )
    require("内显文本读回", ui.get_progress_text_inside(hwnd, inside) is True)
    require("颜色读回", ui.get_progress_colors(hwnd, inside) == (0xFF409EFF, 0xFFE4E7ED, 0))

    circle = ui.create_progress(hwnd, root, "⭕ 圆形", 100, 1, 450, 96, 126, 126, progress_type=1, stroke_width=10)
    require("圆形类型读回", ui.get_progress_options(hwnd, circle) == (1, 10, True))

    dashboard = ui.create_progress(
        hwnd, root, "🎛️ 仪表盘", 64, 2, 604, 96, 150, 126,
        progress_type=2, stroke_width=12, color_stops=[
            (0xFFF56C6C, 20),
            (0xFFE6A23C, 40),
            (0xFF5CB87A, 60),
            (0xFF1989FA, 80),
            (0xFF6F7AD3, 100),
        ]
    )
    require("仪表盘类型读回", ui.get_progress_options(hwnd, dashboard) == (2, 12, True))
    require("颜色分段数量", ui.get_progress_color_stop_count(hwnd, dashboard) == 5)
    require("颜色分段排序", ui.get_progress_color_stop(hwnd, dashboard, 0) == (0xFFF56C6C, 20))
    require("颜色分段末项", ui.get_progress_color_stop(hwnd, dashboard, 4) == (0xFF6F7AD3, 100))

    ui.set_progress_color_stops(hwnd, dashboard, "#909399\t30|0xFFE6A23C\t70|0xFF67C23A\t100")
    require("字符串颜色分段数量", ui.get_progress_color_stop_count(hwnd, dashboard) == 3)
    require("字符串颜色分段首项", ui.get_progress_color_stop(hwnd, dashboard, 0) == (0xFF909399, 30))
    ui.set_progress_color_stops(hwnd, dashboard, "")
    require("空颜色分段恢复默认", ui.get_progress_color_stop_count(hwnd, dashboard) == 0)

    full_text = ui.create_progress(hwnd, root, "✅ 完成文本", 100, 1, 28, 286, 380, 34, text_format=3, complete_text="满")
    require("完成文本读回", ui.get_progress_complete_text(hwnd, full_text) == "满")
    require("格式选项扩展", ui.get_progress_format_options(hwnd, full_text) == (3, False))

    templated = ui.create_progress(
        hwnd, root, "🧩 模板文本", 82, 0, 28, 334, 380, 34,
        text_format=4, text_template="{status} {percent}"
    )
    require("模板文本读回", ui.get_progress_text_template(hwnd, templated) == "{status} {percent}")
    require("模板格式读回", ui.get_progress_format_options(hwnd, templated) == (4, False))

    hidden = ui.create_progress(hwnd, root, "隐藏文本", 44, 0, 28, 382, 380, 34, show_text=False)
    require("隐藏文本选项", ui.get_progress_options(hwnd, hidden) == (0, 0, False))

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(float(os.environ.get("NEW_EMOJI_TEST_SECONDS", "0.6")))
    ui.dll.EU_DestroyWindow(hwnd)
    print("✅ Progress 进度条全样式验证通过")


if __name__ == "__main__":
    main()
