import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_pagination_id = 0
g_next_id = 0
g_size_id = 0
g_jump_id = 0
g_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 分页完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_pagination_change(element_id, value, page_size, action):
    g_events.append((value, page_size, action))
    print(f"[分页变化回调] 元素={element_id} 当前页={value} 每页={page_size} 动作={action}")


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_next_id:
        state = ui.get_pagination_full_state(g_hwnd, g_pagination_id)
        ui.set_pagination_current(g_hwnd, g_pagination_id, state["current_page"] + 1)
        print("[按钮] 下一页：", ui.get_pagination_full_state(g_hwnd, g_pagination_id))
    elif element_id == g_size_id:
        ui.next_pagination_page_size(g_hwnd, g_pagination_id)
        print("[按钮] 切换每页数量：", ui.get_pagination_full_state(g_hwnd, g_pagination_id))
    elif element_id == g_jump_id:
        ui.set_pagination_jump_page(g_hwnd, g_pagination_id, 12)
        ui.trigger_pagination_jump(g_hwnd, g_pagination_id)
        print("[按钮] 跳转页码：", ui.get_pagination_full_state(g_hwnd, g_pagination_id))


def pump_messages(user32, msg, duration):
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
    return running


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    global g_hwnd, g_pagination_id, g_next_id, g_size_id, g_jump_id

    hwnd = ui.create_window("📚 分页完整样式验证", 220, 80, 1080, 720)
    require(hwnd, "错误：窗口创建失败")

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 1040, 660)

    ui.create_text(hwnd, content_id, "📚 Pagination 分页完整封装", 28, 24, 620, 38)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证基础分页、大页数折叠、pager-count、背景样式、小尺寸、单页隐藏、每页数量、跳转页、键盘导航和变化回调。",
        28, 72, 960, 54,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_pagination_id = ui.create_pagination(
        hwnd, content_id,
        total=1000, page_size=100, current=5,
        x=46, y=150, w=940, h=48,
    )
    ui.set_pagination_options(hwnd, g_pagination_id, show_jumper=True, show_size_changer=True, visible_page_count=11)
    ui.set_pagination_page_size_options(hwnd, g_pagination_id, [100, 200, 300, 400])
    ui.set_pagination_advanced_options(hwnd, g_pagination_id, background=True, small=False, hide_on_single_page=False)
    ui.set_pagination_change_callback(hwnd, g_pagination_id, on_pagination_change)

    small_id = ui.create_pagination(
        hwnd, content_id,
        total=50, page_size=10, current=2,
        x=46, y=220, w=520, h=32,
    )
    ui.set_pagination_options(hwnd, small_id, show_jumper=False, show_size_changer=False, visible_page_count=7)
    ui.set_pagination_advanced_options(hwnd, small_id, background=False, small=True, hide_on_single_page=False)

    hidden_id = ui.create_pagination(
        hwnd, content_id,
        total=5, page_size=20, current=1,
        x=46, y=280, w=520, h=40,
    )
    ui.set_pagination_advanced_options(hwnd, hidden_id, background=True, small=False, hide_on_single_page=True)

    ui.create_infobox(
        hwnd, content_id,
        "✅ 验证提示",
        "分页条包含页码、省略号、每页数量、跳转按钮、背景样式和小尺寸样式；单页隐藏组件不绘制且不响应键盘翻页。",
        46, 340, 900, 92,
    )

    g_next_id = ui.create_button(hwnd, content_id, "➡️", "下一页", 46, 470, 130, 42)
    g_size_id = ui.create_button(hwnd, content_id, "📏", "切换每页", 198, 470, 150, 42)
    g_jump_id = ui.create_button(hwnd, content_id, "🎯", "跳到 12 页", 370, 470, 160, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_next_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_size_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_jump_id, on_click)

    initial = ui.get_pagination_full_state(hwnd, g_pagination_id)
    advanced = ui.get_pagination_advanced_options(hwnd, g_pagination_id)
    print("[初始状态]", initial, advanced)
    require(initial and initial["total"] == 1000, "分页总数读回失败")
    require(initial["page_count"] == 10 and initial["current_page"] == 5, "分页初始页数读回失败")
    require(initial["show_jumper"] == 1 and initial["show_size_changer"] == 1, "分页布局选项读回失败")
    require(initial["visible_page_count"] == 11, "分页 pager-count=11 读回失败")
    require(advanced == {"background": True, "small": False, "hide_on_single_page": False}, "分页高级样式读回失败")

    small_state = ui.get_pagination_advanced_options(hwnd, small_id)
    hidden_state = ui.get_pagination_advanced_options(hwnd, hidden_id)
    require(small_state == {"background": False, "small": True, "hide_on_single_page": False}, "小尺寸样式读回失败")
    require(hidden_state == {"background": True, "small": False, "hide_on_single_page": True}, "单页隐藏样式读回失败")

    ui.set_pagination_jump_page(hwnd, g_pagination_id, 10)
    ui.trigger_pagination_jump(g_hwnd, g_pagination_id)
    jumped = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[程序跳转]", jumped)
    require(jumped["current_page"] == 10 and jumped["jump_count"] >= 1 and jumped["last_action"] == 5, "分页跳转失败")

    ui.next_pagination_page_size(hwnd, g_pagination_id)
    sized = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[每页数量切换]", sized)
    require(sized["page_size"] == 200 and sized["page_count"] == 5 and sized["size_change_count"] >= 1, "分页每页数量切换失败")

    ui.set_pagination_current(hwnd, g_pagination_id, 3)
    selected = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[程序选页]", selected)
    require(selected["current_page"] == 3 and g_events, "分页选择回调失败")

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    ui.dll.EU_SetElementFocus(hwnd, g_pagination_id)
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)
    pump_messages(user32, msg, 0.25)
    key_state = ui.get_pagination_full_state(hwnd, g_pagination_id)
    print("[键盘右移]", key_state)
    require(key_state["current_page"] == 4 and key_state["last_action"] == 3, "分页键盘导航失败")

    before_hidden = ui.get_pagination_full_state(hwnd, hidden_id)
    ui.dll.EU_SetElementFocus(hwnd, hidden_id)
    user32.PostMessageW(hwnd, 0x0100, 0x27, 0)
    pump_messages(user32, msg, 0.25)
    after_hidden = ui.get_pagination_full_state(hwnd, hidden_id)
    print("[单页隐藏键盘忽略]", before_hidden, after_hidden)
    require(after_hidden["current_page"] == before_hidden["current_page"], "单页隐藏不应响应键盘翻页")
    require(after_hidden["last_action"] == before_hidden["last_action"], "单页隐藏不应更新动作状态")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("分页完整样式示例已显示。关闭窗口或等待 60 秒结束。")

    start = time.time()
    running = True
    auto_clicked = False
    while running and time.time() - start < 60:
        if not auto_clicked and time.time() - start > 1.0:
            on_click(g_jump_id)
            auto_clicked = True
        running = pump_messages(user32, msg, 0.05)

    print("分页完整样式示例结束。")


if __name__ == "__main__":
    main()
