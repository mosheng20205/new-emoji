import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_auto_id = 0
g_mentions_id = 0
g_cascader_id = 0
g_open_id = 0
g_update_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 弹层选择状态示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_open_id:
        ui.set_autocomplete_open(g_hwnd, g_auto_id, True)
        ui.set_mentions_open(g_hwnd, g_mentions_id, True)
        ui.set_cascader_open(g_hwnd, g_cascader_id, True)
        print(
            "[打开] "
            f"自动补全={ui.get_autocomplete_open(g_hwnd, g_auto_id)} "
            f"提及={ui.get_mentions_open(g_hwnd, g_mentions_id)} "
            f"级联={ui.get_cascader_open(g_hwnd, g_cascader_id)}"
        )
    elif element_id == g_update_id:
        ui.set_autocomplete_suggestions(
            g_hwnd, g_auto_id,
            ["✨ 设计", "🚀 开发", "🧪 测试", "📦 发布"]
        )
        ui.set_autocomplete_selected(g_hwnd, g_auto_id, 2)
        ui.set_mentions_value(g_hwnd, g_mentions_id, "@")
        ui.set_mentions_suggestions(g_hwnd, g_mentions_id, ["张三", "李四", "王五", "项目组"])
        ui.set_mentions_selected(g_hwnd, g_mentions_id, 3)
        ui.set_cascader_options(
            g_hwnd, g_cascader_id,
            [
                ("浙江", "杭州", "西湖区"),
                ("浙江", "宁波", "海曙区"),
                ("江苏", "南京", "玄武区"),
                ("广东", "深圳", "南山区"),
            ],
        )
        ui.set_cascader_value(g_hwnd, g_cascader_id, ["广东", "深圳", "南山区"])
        ui.set_autocomplete_open(g_hwnd, g_auto_id, True)
        ui.set_mentions_open(g_hwnd, g_mentions_id, True)
        ui.set_cascader_open(g_hwnd, g_cascader_id, True)
        print(
            "[状态] "
            f"自动补全选中={ui.get_autocomplete_selected(g_hwnd, g_auto_id)} "
            f"建议数={ui.get_autocomplete_suggestion_count(g_hwnd, g_auto_id)} "
            f"提及选中={ui.get_mentions_selected(g_hwnd, g_mentions_id)} "
            f"提及数={ui.get_mentions_suggestion_count(g_hwnd, g_mentions_id)} "
            f"级联选项={ui.get_cascader_option_count(g_hwnd, g_cascader_id)} "
            f"路径深度={ui.get_cascader_selected_depth(g_hwnd, g_cascader_id)} "
            f"显示层级={ui.get_cascader_level_count(g_hwnd, g_cascader_id)}"
        )


def main():
    global g_hwnd, g_auto_id, g_mentions_id, g_cascader_id, g_open_id, g_update_id

    hwnd = ui.create_window("🔎 弹层选择状态示例", 220, 80, 960, 640)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 590)

    ui.create_text(hwnd, content_id, "🔎 Autocomplete / Mentions / Cascader", 28, 24, 620, 36)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "这一批补齐弹层选择组件的程序化打开、选中项设置、状态读取和数量读取，方便易语言侧控制复杂输入流程。",
        28, 68, 800, 48,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.create_text(hwnd, content_id, "✨ 自动补全", 40, 144, 160, 28)
    g_auto_id = ui.create_autocomplete(
        hwnd, content_id, "设", ["设计", "设置", "设计器"], 40, 182, 300, 38
    )

    ui.create_text(hwnd, content_id, "📣 提及输入", 40, 260, 160, 28)
    g_mentions_id = ui.create_mentions(
        hwnd, content_id, "@", ["张三", "李四", "王五"], 40, 298, 300, 38
    )

    ui.create_text(hwnd, content_id, "🧭 级联选择", 400, 144, 160, 28)
    g_cascader_id = ui.create_cascader(
        hwnd,
        content_id,
        [("浙江", "杭州", "西湖区"), ("江苏", "南京", "玄武区")],
        ["浙江", "杭州", "西湖区"],
        400, 182, 300, 38,
    )

    g_open_id = ui.create_button(hwnd, content_id, "🔓", "打开弹层", 740, 178, 150, 42)
    g_update_id = ui.create_button(hwnd, content_id, "🚀", "更新并读取", 740, 236, 150, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_open_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_update_id, on_click)

    ui.create_infobox(
        hwnd, content_id,
        "验证提示",
        "示例会在 1 秒后自动打开三个弹层，2 秒后更新数据并读取状态。所有展示文案均为中文并包含 emoji。",
        40, 410, 720, 90,
    )

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("弹层选择状态示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_open = False
    auto_update = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_open and elapsed > 1.0:
            on_click(g_open_id)
            auto_open = True
        if not auto_update and elapsed > 2.0:
            on_click(g_update_id)
            auto_update = True
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

    print("弹层选择状态示例结束。")


if __name__ == "__main__":
    main()
