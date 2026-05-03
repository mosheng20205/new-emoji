import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_dropdown_id = 0
g_open_id = 0
g_select_id = 0
g_disable_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 下拉菜单完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_open_id:
        ui.set_dropdown_open(g_hwnd, g_dropdown_id, True)
        print(f"[打开] 状态={ui.get_dropdown_state(g_hwnd, g_dropdown_id)}")
    elif element_id == g_select_id:
        ui.set_dropdown_selected(g_hwnd, g_dropdown_id, 2)
        blocked = ui.get_dropdown_state(g_hwnd, g_dropdown_id)
        ui.set_dropdown_selected(g_hwnd, g_dropdown_id, 5)
        nested = ui.get_dropdown_state(g_hwnd, g_dropdown_id)
        ui.set_dropdown_open(g_hwnd, g_dropdown_id, True)
        print(f"[禁用拦截] 选中禁用项后={blocked}；选中二级项后={nested}")
    elif element_id == g_disable_id:
        ui.set_dropdown_disabled(g_hwnd, g_dropdown_id, [7])
        ui.set_dropdown_selected(g_hwnd, g_dropdown_id, 7)
        ui.set_dropdown_open(g_hwnd, g_dropdown_id, True)
        print(f"[运行时禁用] 状态={ui.get_dropdown_state(g_hwnd, g_dropdown_id)}")


def main():
    global g_hwnd, g_dropdown_id, g_open_id, g_select_id, g_disable_id

    hwnd = ui.create_window("📂 下拉菜单完整组件", 220, 80, 960, 680)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 920, 620)

    ui.create_text(hwnd, content_id, "📂 下拉菜单完整验证", 28, 24, 380, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "本示例验证层级缩进、禁用项绘制与交互拦截、键盘/鼠标选择、滚轮滚动、Set/Get 状态读回和中文 emoji 展示。",
        28, 70, 820, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    items = [
        "📁 常用操作",
        "> ✏️ 编辑资料",
        "> !🚫 删除账户",
        "📊 报表中心",
        "> 📈 查看趋势",
        "> > 📅 本月数据",
        "> > 📦 历史归档",
        "⚙️ 系统设置",
        "> 🔔 通知配置",
        "> 🧪 实验功能",
        "> 🛡️ 安全策略",
    ]

    ui.create_text(hwnd, content_id, "🧭 层级下拉，含禁用项和长列表滚动", 48, 142, 360, 28)
    g_dropdown_id = ui.create_dropdown(
        hwnd, content_id, "🛠️ 选择操作", items, 1,
        48, 178, 320, 42,
    )
    ui.set_dropdown_open(hwnd, g_dropdown_id, True)
    ui.set_dropdown_disabled(hwnd, g_dropdown_id, [10])

    ui.create_infobox(
        hwnd,
        content_id,
        "验证提示",
        "第 3 项带 ! 前缀禁用；“安全策略”由运行时禁用 API 禁用。1 秒后自动打开，2 秒后尝试选中禁用项，3 秒后更新运行时禁用状态。",
        420, 156, 430, 98,
    )

    g_open_id = ui.create_button(hwnd, content_id, "🔓", "打开下拉", 48, 524, 150, 42)
    g_select_id = ui.create_button(hwnd, content_id, "🎯", "测试选择", 220, 524, 150, 42)
    g_disable_id = ui.create_button(hwnd, content_id, "🚫", "运行时禁用", 392, 524, 170, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_open_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_select_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_disable_id, on_click)

    initial = ui.get_dropdown_state(hwnd, g_dropdown_id)
    print(f"[初始] 状态={initial} 打开={ui.get_dropdown_open(hwnd, g_dropdown_id)}")
    if not initial or initial["count"] != len(items) or initial["disabled"] < 2:
        raise RuntimeError("下拉菜单状态读回失败")
    ui.set_dropdown_selected(hwnd, g_dropdown_id, 5)
    nested = ui.get_dropdown_state(hwnd, g_dropdown_id)
    if not nested or nested["selected"] != 5 or nested["level"] != 2:
        raise RuntimeError("下拉菜单层级选中读回失败")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("下拉菜单完整组件示例已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    auto_open = False
    auto_select = False
    auto_disable = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not auto_open and elapsed > 1.0:
            on_click(g_open_id)
            auto_open = True
        if not auto_select and elapsed > 2.0:
            on_click(g_select_id)
            auto_select = True
        if not auto_disable and elapsed > 3.0:
            on_click(g_disable_id)
            auto_disable = True
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

    print("下拉菜单完整组件示例结束。")


if __name__ == "__main__":
    main()
