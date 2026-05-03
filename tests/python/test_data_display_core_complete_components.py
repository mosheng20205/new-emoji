import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_card_id = 0
g_collapse_id = 0
g_stat_id = 0
g_update_id = 0
g_counter = 1024.0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 数据展示核心完成批次窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_counter

    if element_id == g_update_id:
        g_counter += 128.5
        data = ui.make_utf8(f"{g_counter:.1f}")
        ui.dll.EU_SetStatisticValue(g_hwnd, g_stat_id, ui.bytes_arg(data), len(data))
        next_active = (ui.dll.EU_GetCollapseActive(g_hwnd, g_collapse_id) + 1) % 3
        ui.dll.EU_SetCollapseActive(g_hwnd, g_collapse_id, next_active)
        print(f"[刷新] 统计值={g_counter:.1f}，折叠项={next_active}")
    elif element_id == g_card_id:
        print(f"[卡片操作] 当前操作索引={ui.get_card_action(g_hwnd, g_card_id)}")
    else:
        print(f"[点击] 元素 #{element_id}")


def main():
    global g_hwnd, g_card_id, g_collapse_id, g_stat_id, g_update_id

    hwnd = ui.create_window("📚 数据展示核心组件完成验证", 180, 60, 1080, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 1040, 700)

    ui.create_text(hwnd, content, "📚 数据展示核心组件完成验证", 30, 22, 420, 36)
    ui.create_text(hwnd, content, "卡片、折叠面板、时间线、统计数值均包含中文与 emoji、主题色、交互状态和可读回选项。", 30, 62, 760, 30)

    g_card_id = ui.create_card(
        hwnd, content,
        "🧩 发布卡片",
        "正文区域支持长中文内容换行；下方操作区可点击，点击后可通过 GetCardAction 读取操作索引。",
        2,
        30, 110, 450, 210,
    )
    ui.set_card_footer(hwnd, g_card_id, "📌 最近更新：组件完成批次")
    ui.set_card_actions(hwnd, g_card_id, ["查看", "同步", "归档"])
    ui.set_card_options(hwnd, g_card_id, shadow=2, hoverable=True)

    g_collapse_id = ui.create_collapse(
        hwnd, content,
        [
            ("🎯 创建与绘制", "标题、正文、禁用态和展开体都会随主题刷新。"),
            ("🔒 禁用项目", "这个项目禁用，不参与鼠标命中和键盘切换。"),
            ("⌨️ 键盘与动画", "方向键、Home/End 和展开动画已经接入。"),
        ],
        0,
        True,
        520, 110, 430, 210,
    )
    ui.set_collapse_options(
        hwnd, g_collapse_id,
        accordion=True,
        allow_collapse=True,
        disabled_indices=[1],
        animated=True,
    )

    timeline_id = ui.create_timeline(
        hwnd, content,
        [
            ("09:00", "创建窗口并加载中文 emoji", 0, "🚀"),
            ("10:10", "补齐 C++ Element 本体能力", 1, "✅"),
            ("11:20", "同步 Python 与易语言命令", 2, "🧾"),
            ("12:00", "执行 Win32 / x64 构建验证", 3, "🛠️"),
        ],
        30, 360, 450, 250,
    )
    ui.set_timeline_options(hwnd, timeline_id, position=2, show_time=True)

    g_stat_id = ui.create_statistic(
        hwnd, content,
        "📈 今日访问",
        f"{g_counter:.1f}",
        "🔥 ",
        " 次",
        520, 360, 210, 130,
    )
    ui.set_statistic_options(hwnd, g_stat_id, precision=1, animated=True)
    ui.set_statistic_format(hwnd, g_stat_id, "📈 今日访问", "🔥 ", " 次")

    g_update_id = ui.create_button(hwnd, content, "🔄", "刷新数据", 760, 404, 150, 46)
    ui.dll.EU_SetElementClickCallback(hwnd, g_card_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    print("[读回] 卡片选项=", ui.get_card_options(hwnd, g_card_id))
    print("[读回] 折叠选项=", ui.get_collapse_options(hwnd, g_collapse_id))
    print("[读回] 时间线选项=", ui.get_timeline_options(hwnd, timeline_id))
    print("[读回] 统计选项=", ui.get_statistic_options(hwnd, g_stat_id))
    print("[读回] 时间线项目数=", ui.get_timeline_item_count(hwnd, timeline_id))

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("数据展示核心完成批次示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("数据展示核心完成批次示例结束。")


if __name__ == "__main__":
    main()
