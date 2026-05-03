import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


WINDOW_W = 920
WINDOW_H = 660
CONTENT_W = 900
CONTENT_H = 610

g_hwnd = None
g_select_id = 0
g_select_v2_id = 0
g_rate_id = 0
g_color_id = 0
g_apply_id = 0
g_reset_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 表单选择与评分颜色示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def print_state(prefix):
    color = ui.get_colorpicker_color(g_hwnd, g_color_id) & 0xFFFFFFFF
    rate_options = ui.get_rate_options(g_hwnd, g_rate_id)
    print(
        f"{prefix} "
        f"选择器={ui.get_select_index(g_hwnd, g_select_id)}/"
        f"{ui.get_select_option_count(g_hwnd, g_select_id)} "
        f"匹配={ui.get_select_matched_count(g_hwnd, g_select_id)} "
        f"增强选择器={ui.get_select_v2_index(g_hwnd, g_select_v2_id)} "
        f"可见={ui.get_select_v2_visible_count(g_hwnd, g_select_v2_id)} "
        f"评分半星={ui.get_rate_value_x2(g_hwnd, g_rate_id)} "
        f"评分选项={rate_options} "
        f"颜色=0x{color:08X} "
        f"透明度={ui.get_colorpicker_alpha(g_hwnd, g_color_id)} "
        f"预设色={ui.get_colorpicker_palette_count(g_hwnd, g_color_id)}"
    )


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_apply_id:
        ui.set_select_open(g_hwnd, g_select_id, True)
        ui.set_select_search(g_hwnd, g_select_id, "🍊")
        ui.set_select_option_disabled(g_hwnd, g_select_id, 1, True)
        ui.set_select_index(g_hwnd, g_select_id, 2)

        ui.set_select_v2_options(
            g_hwnd,
            g_select_v2_id,
            [
                "北京 🏙️", "上海 🌃", "杭州 🌿", "深圳 🚀", "成都 🍵",
                "武汉 🌉", "南京 🏯", "苏州 🪷", "厦门 🌊", "青岛 ⛵",
                "西安 🏮", "长沙 🌶️", "宁波 ⚓", "广州 🍲", "天津 🌊",
            ],
        )
        ui.set_select_v2_visible_count(g_hwnd, g_select_v2_id, 5)
        ui.set_select_v2_search(g_hwnd, g_select_v2_id, "州")
        ui.set_select_v2_option_disabled(g_hwnd, g_select_v2_id, 0, True)
        ui.set_select_v2_index(g_hwnd, g_select_v2_id, 7)

        ui.set_rate_options(g_hwnd, g_rate_id, allow_clear=True, allow_half=True, readonly=False)
        ui.set_rate_texts(g_hwnd, g_rate_id, "待体验 💤", "很满意 🎉", True)
        ui.set_rate_value_x2(g_hwnd, g_rate_id, 9)

        ui.set_colorpicker_palette(
            g_hwnd,
            g_color_id,
            [
                0xFF1E66F5, 0xFF43A047, 0xFFFFB300, 0xFFE53935,
                0xFF8E24AA, 0xFF00ACC1, 0xFF303133, 0xFFFFFFFF,
                0xFFFF7043, 0xFF26A69A, 0xFF5C6BC0, 0xFFEC407A,
            ],
        )
        ui.set_colorpicker_color(g_hwnd, g_color_id, 0xFF43A047)
        ui.set_colorpicker_alpha(g_hwnd, g_color_id, 188)
        ui.set_colorpicker_open(g_hwnd, g_color_id, True)
        print_state("[应用增强状态]")
    elif element_id == g_reset_id:
        ui.set_select_search(g_hwnd, g_select_id, "")
        ui.set_select_open(g_hwnd, g_select_id, False)
        ui.set_select_option_disabled(g_hwnd, g_select_id, 1, False)
        ui.set_select_index(g_hwnd, g_select_id, 0)

        ui.set_select_v2_search(g_hwnd, g_select_v2_id, "")
        ui.set_select_v2_open(g_hwnd, g_select_v2_id, False)
        ui.set_select_v2_visible_count(g_hwnd, g_select_v2_id, 7)
        ui.set_select_v2_index(g_hwnd, g_select_v2_id, 3)

        ui.set_rate_options(g_hwnd, g_rate_id, allow_clear=True, allow_half=True, readonly=True)
        ui.set_rate_texts(g_hwnd, g_rate_id, "待评分 😴", "已评分 🌟", True)
        ui.set_rate_value_x2(g_hwnd, g_rate_id, 6)

        ui.set_colorpicker_color(g_hwnd, g_color_id, 0xFF1E66F5)
        ui.set_colorpicker_alpha(g_hwnd, g_color_id, 255)
        ui.set_colorpicker_open(g_hwnd, g_color_id, False)
        print_state("[恢复默认状态]")


def main():
    global g_hwnd, g_select_id, g_select_v2_id, g_rate_id, g_color_id
    global g_apply_id, g_reset_id

    hwnd = ui.create_window("🧪 选择评分颜色组件测试", 220, 100, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)

    ui.create_text(hwnd, content_id, "🧪 选择器 / 虚拟选择器 / 评分 / 颜色", 28, 22, 520, 32)
    ui.create_divider(hwnd, content_id, "本测试覆盖搜索、禁用项、打开状态、半星、评分文案、透明度与预设色", 0, 1, 28, 62, 830, 30)

    ui.create_text(hwnd, content_id, "🍱 普通选择器", 28, 110, 180, 26)
    g_select_id = ui.create_select(
        hwnd,
        content_id,
        "午餐",
        ["米饭 🍚", "面条 🍜", "橙汁 🍊", "沙拉 🥗"],
        0,
        28,
        144,
        320,
        42,
    )
    ui.set_select_option_disabled(hwnd, g_select_id, 1, True)
    ui.set_select_open(hwnd, g_select_id, True)

    ui.create_text(hwnd, content_id, "🏙️ 增强选择器", 28, 220, 180, 26)
    g_select_v2_id = ui.create_select_v2(
        hwnd,
        content_id,
        "城市",
        [f"城市 {i} ✨" for i in range(1, 31)],
        3,
        7,
        28,
        254,
        320,
        42,
    )
    ui.set_select_v2_open(hwnd, g_select_v2_id, True)

    ui.create_text(hwnd, content_id, "⭐ 半星评分", 420, 110, 180, 26)
    g_rate_id = ui.create_rate(
        hwnd,
        content_id,
        "体验",
        3,
        5,
        420,
        144,
        390,
        42,
        allow_clear=True,
        allow_half=True,
        readonly=True,
        value_x2=6,
    )
    ui.set_rate_texts(hwnd, g_rate_id, "待评分 😴", "已评分 🌟", True)

    ui.create_text(hwnd, content_id, "🎨 颜色选择器", 420, 220, 180, 26)
    g_color_id = ui.create_colorpicker(
        hwnd,
        content_id,
        "主题色",
        0xFF1E66F5,
        420,
        254,
        330,
        42,
        alpha=255,
        open_panel=True,
        palette=[
            0xFF1E66F5, 0xFF43A047, 0xFFFFB300, 0xFFE53935,
            0xFF8E24AA, 0xFF00ACC1, 0xFF303133, 0xFFFFFFFF,
        ],
    )

    g_apply_id = ui.create_button(hwnd, content_id, "✅", "应用增强状态", 420, 396, 160, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "↩", "恢复默认状态", 600, 396, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_apply_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_reset_id, on_click)

    ui.create_infobox(
        hwnd,
        content_id,
        "🔎 验证要点",
        "四个组件均为 C++ Element 本体：普通选择器支持搜索和禁用项；增强选择器支持大列表可视窗口；评分支持半星、只读和文案；颜色选择器支持透明度、弹层和预设色数量读取。",
        28,
        382,
        360,
        120,
    )
    ui.create_alert(
        hwnd,
        content_id,
        "📐 首屏尺寸",
        f"窗口 {WINDOW_W}×{WINDOW_H}，容器 {CONTENT_W}×{CONTENT_H}，最右内容约 810，最下内容约 502，保留足够逻辑余量。",
        0,
        0,
        False,
        28,
        526,
        780,
        58,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print_state("[初始状态]")
    print("选择评分颜色组件测试窗口已显示，请观察 60 秒或手动关闭。")

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

    print("选择评分颜色组件测试结束。")


if __name__ == "__main__":
    main()
