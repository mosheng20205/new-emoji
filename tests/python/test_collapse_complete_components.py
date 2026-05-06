import time
from ctypes import wintypes

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages(seconds=1.0):
    user32 = ui.ctypes.windll.user32
    msg = wintypes.MSG()
    start = time.time()
    while time.time() - start < seconds:
        handled = False
        while user32.PeekMessageW(ui.ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                return
            user32.TranslateMessage(ui.ctypes.byref(msg))
            user32.DispatchMessageW(ui.ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def main():
    hwnd = ui.create_window("📂 折叠面板完整样式验证", 180, 80, 1100, 760)
    assert hwnd, "窗口创建失败"
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1060, 700)

    multi = ui.create_collapse(
        hwnd, root,
        [
            ("一致性 Consistency", "与现实生活一致。\n界面结构一致。", "🎯", "已展开", 0),
            ("反馈 Feedback", "控制反馈。\n页面反馈。", "💬", "已展开", 0),
            ("效率 Efficiency", "简化流程。\n清晰明确。", "⚡", "可展开", 0),
            ("可控 Controllability", "用户决策。\n结果可控。", "🛡️", "可展开", 0),
        ],
        active=[0, 1],
        accordion=False,
        x=30, y=32, w=500, h=280,
    )
    assert multi > 0, "多展开折叠面板创建失败"
    assert ui.get_collapse_item_count(hwnd, multi) == 4
    assert ui.get_collapse_active_items(hwnd, multi) == [0, 1]

    ui.set_collapse_active_items(hwnd, multi, [0, 2, 3])
    assert ui.get_collapse_active_items(hwnd, multi) == [0, 2, 3]
    state = ui.get_collapse_state_json(hwnd, multi)
    assert state["activeIndices"] == [0, 2, 3]
    assert state["accordion"] is False

    accordion = ui.create_collapse(
        hwnd, root,
        [
            {"title": "反馈面板", "body": "一次只展开一个区域。", "icon": "📣", "suffix": "当前"},
            {"title": "效率面板", "body": "点击其他标题自动收起。", "icon": "⚙️", "suffix": "候选"},
            {"title": "禁用面板", "body": "不会响应点击和键盘切换。", "icon": "🚫", "suffix": "禁用", "disabled": True},
        ],
        active=0,
        accordion=True,
        x=560, y=32, w=470, h=250,
    )
    ui.set_collapse_options(hwnd, accordion, accordion=True, allow_collapse=False, disabled_indices=[2], animated=False)
    ui.set_collapse_active_items(hwnd, accordion, [0, 1])
    assert ui.get_collapse_active_items(hwnd, accordion) == [0], "手风琴模式应只保留一个激活项"
    assert ui.get_collapse_options(hwnd, accordion) == (True, False, False, 1)

    ui.dll.EU_SetCollapseActive(hwnd, accordion, 1)
    assert ui.dll.EU_GetCollapseActive(hwnd, accordion) == 1
    assert ui.get_collapse_active_items(hwnd, accordion) == [1]

    custom = ui.create_collapse(hwnd, root, [], active=-1, accordion=False, x=30, y=350, w=1000, h=250)
    ui.set_collapse_items_ex(hwnd, custom, [
        {"title": "组件规范", "body": "标题图标与右侧说明。", "icon": "🧩", "suffix": "说明"},
        {"title": "禁用分组", "body": "弱化并跳过交互。", "icon": "🚫", "suffix": "禁用", "disabled": True},
        {"title": "发布检查", "body": "正文支持显式换行。\n第二行内容可完整显示。", "icon": "✅", "suffix": "2 项"},
    ])
    ui.set_collapse_active_items(hwnd, custom, [0, 2])
    custom_state = ui.get_collapse_state_json(hwnd, custom)
    assert custom_state["activeIndices"] == [0, 2]
    assert custom_state["items"][0]["icon"] == "🧩"
    assert custom_state["items"][1]["disabled"] is True
    assert custom_state["disabledIndices"] == [1]

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(0.3)
    print("[Collapse] 多展开、手风琴、自定义标题、禁用项和状态读回验证成功。")
    pump_messages(1.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
