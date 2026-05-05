import ctypes
import time
from ctypes import wintypes

import test_new_emoji as ui


g_hwnd = None
g_feedback_id = 0
g_game_id = 0
g_tomorrow_id = 0
g_pause_btn = 0
g_status_id = 0
g_liked = True
g_paused = False


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Statistic 完整组件窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_suffix_click(_element_id):
    global g_liked
    g_liked = not g_liked
    value = "521" if g_liked else "520"
    data = ui.make_utf8(value)
    ui.dll.EU_SetStatisticValue(g_hwnd, g_feedback_id, ui.bytes_arg(data), len(data))
    ui.set_statistic_affix_options(
        g_hwnd, g_feedback_id, "", " ★" if g_liked else " ☆",
        suffix_color=0xFFFFC107, value_color=0xFFEAF0FF, suffix_clickable=True,
    )
    ui.set_element_text(g_hwnd, g_status_id, "⭐ 后缀点击回调：已收藏" if g_liked else "☆ 后缀点击回调：已取消")


@ui.ClickCallback
def on_finish(_element_id):
    ui.set_element_text(g_hwnd, g_status_id, "⏰ 倒计时 finish 回调已触发")


@ui.ClickCallback
def on_add_time(_element_id):
    ui.add_statistic_countdown_time(g_hwnd, g_game_id, 10000)
    ui.set_element_text(g_hwnd, g_status_id, "➕ 已增加 10 秒")


@ui.ClickCallback
def on_pause(_element_id):
    global g_paused
    g_paused = not g_paused
    ui.set_statistic_countdown_state(g_hwnd, g_tomorrow_id, g_paused)
    ui.set_element_text(g_hwnd, g_pause_btn, "继续" if g_paused else "暂停")
    ui.set_element_text(g_hwnd, g_status_id, "⏸️ 已暂停倒计时" if g_paused else "▶️ 已继续倒计时")


def main():
    global g_hwnd, g_feedback_id, g_game_id, g_tomorrow_id, g_pause_btn, g_status_id

    hwnd = ui.create_window("📊 Statistic 统计数值完整验证", 180, 80, 1180, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1140, 700)
    ui.create_text(hwnd, root, "📊 Statistic 统计数值完整验证", 30, 24, 520, 36)
    g_status_id = ui.create_text(hwnd, root, "✅ 正在验证数值、formatter、前后缀、点击后缀和倒计时。", 30, 62, 920, 30)

    stat1 = ui.create_statistic(hwnd, root, "📈 增长人数", "1314", "", " 人", 30, 110, 250, 120)
    ui.set_statistic_number_options(hwnd, stat1, precision=2, animated=True, group_separator=True)
    ui.set_statistic_affix_options(hwnd, stat1, "", " 人", suffix_color=0xFF67C23A, value_color=0xFF67C23A)

    stat2 = ui.create_statistic(hwnd, root, "👥 男女比", "0", "", "", 310, 110, 250, 120)
    ui.set_statistic_display_text(hwnd, stat2, "456/2")

    stat3 = ui.create_statistic(hwnd, root, "🚩 活跃金额", "4154.564", "🚩 ", " 🚩", 590, 110, 250, 120)
    ui.set_statistic_number_options(hwnd, stat3, precision=2, animated=True, group_separator=True, decimal_separator=".")
    ui.set_statistic_affix_options(hwnd, stat3, "🚩 ", " 🚩", 0xFFF56C6C, 0xFF409EFF, 0xFFEAF0FF)

    g_feedback_id = ui.create_statistic(hwnd, root, "⭐ 用户反馈", "521", "", " ★", 870, 110, 230, 120)
    ui.set_statistic_number_options(hwnd, g_feedback_id, precision=0, animated=True)
    ui.set_statistic_affix_options(hwnd, g_feedback_id, "", " ★", suffix_color=0xFFFFC107, value_color=0xFFEAF0FF, suffix_clickable=True)
    ui.set_statistic_suffix_click_callback(hwnd, g_feedback_id, on_suffix_click)

    now_ms = int(time.time() * 1000)
    sale = ui.create_statistic(hwnd, root, "🎉 商品降价 🎉", "0", "", " 抢购即将开始", 30, 280, 500, 120)
    ui.set_statistic_countdown(hwnd, sale, now_ms + 1000 * 60 * 60 * 8)
    ui.set_statistic_affix_options(hwnd, sale, "", " 抢购即将开始", suffix_color=0xFFF56C6C, value_color=0xFF67C23A)

    g_game_id = ui.create_statistic(hwnd, root, "🎮 时间游戏", "0", "", " 后结束", 570, 280, 500, 120)
    ui.set_statistic_countdown(hwnd, g_game_id, now_ms + 3000, "HH:mm:ss")
    ui.set_statistic_affix_options(hwnd, g_game_id, "", " 后结束", suffix_color=0xFF7AA7FF)
    ui.set_statistic_finish_callback(hwnd, g_game_id, on_finish)

    add_btn = ui.create_button(hwnd, root, "➕", "增加 10 秒", 570, 420, 150, 38)
    ui.dll.EU_SetElementClickCallback(hwnd, add_btn, on_add_time)

    solar = ui.create_statistic(hwnd, root, "🚩 距离立夏还有", "0", "", "", 30, 486, 500, 120)
    ui.set_statistic_countdown(hwnd, solar, now_ms + 1000 * 60 * 60 * 24 * 18, "DD天HH小时mm分钟")
    ui.set_statistic_affix_options(hwnd, solar, "", "", value_color=0xFFE6A23C)

    g_tomorrow_id = ui.create_statistic(hwnd, root, "📜 距离明日", "0", "", "", 570, 486, 500, 120)
    ui.set_statistic_countdown(hwnd, g_tomorrow_id, now_ms + 1000 * 60 * 60 * 6, "HH:mm:ss")
    ui.set_statistic_affix_options(hwnd, g_tomorrow_id, "", "", value_color=0xFF67C23A)
    g_pause_btn = ui.create_button(hwnd, root, "⏸️", "暂停", 570, 626, 120, 38)
    ui.dll.EU_SetElementClickCallback(hwnd, g_pause_btn, on_pause)

    state = ui.get_statistic_full_state(hwnd, g_game_id)
    print("[读回] 时间游戏状态=", state)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("Statistic 完整组件窗口已显示。关闭窗口或等待 10 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < 10:
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

    print("[读回] 结束状态=", ui.get_statistic_full_state(hwnd, g_game_id))
    print("Statistic 完整组件验证结束。")


if __name__ == "__main__":
    main()
