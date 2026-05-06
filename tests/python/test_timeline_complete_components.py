import os
import time
from ctypes import wintypes

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 时间线全样式窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages(seconds):
    msg = wintypes.MSG()
    user32 = ui.ctypes.windll.user32
    start = time.time()
    running = True
    while running and time.time() - start < seconds:
        handled = False
        while user32.PeekMessageW(ui.ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                running = False
                break
            user32.TranslateMessage(ui.ctypes.byref(msg))
            user32.DispatchMessageW(ui.ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)


def main():
    hwnd = ui.create_window("🕒 时间线全样式完成验证", 180, 70, 1180, 780)
    assert hwnd, "窗口创建失败"
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1140, 720)

    ui.create_text(hwnd, root, "🕒 Timeline 时间线全样式完成验证", 30, 24, 560, 36)
    ui.create_text(hwnd, root, "覆盖正序/倒序、图标、类型、自定义颜色、大尺寸节点、顶部时间戳卡片和位置布局。", 30, 64, 880, 30)

    base_id = ui.create_timeline(
        hwnd, root,
        [
            {"timestamp": "2018-04-15", "content": "🎉 活动按期开始", "type": 1, "icon": "✅"},
            {"timestamp": "2018-04-13", "content": "🧾 通过审核", "type": 0, "icon": "📌"},
            {"timestamp": "2018-04-11", "content": "🚀 创建成功", "type": 0, "icon": "🚀"},
        ],
        30, 120, 500, 210,
    )
    assert base_id > 0
    assert ui.get_timeline_item_count(hwnd, base_id) == 3
    ui.set_timeline_advanced_options(hwnd, base_id, position=0, show_time=True, reverse=True, default_placement="bottom")
    assert ui.get_timeline_advanced_options(hwnd, base_id) == {
        "position": 0,
        "show_time": True,
        "reverse": True,
        "default_placement": "bottom",
    }

    node_id = ui.create_timeline(
        hwnd, root,
        [
            {"timestamp": "2018-04-12 20:46", "content": "✨ 支持使用图标", "size": "large", "type": 0, "icon": "el-icon-more"},
            {"timestamp": "2018-04-03 20:46", "content": "🟢 支持自定义颜色", "color": "#0bbd87"},
            {"timestamp": "2018-04-03 20:46", "content": "📏 支持自定义尺寸", "size": "large", "type": 2},
            {"timestamp": "2018-04-03 20:46", "content": "⚪ 默认样式的节点"},
        ],
        570, 120, 520, 250,
    )
    assert node_id > 0
    assert ui.get_timeline_item_count(hwnd, node_id) == 4
    ui.set_timeline_advanced_options(hwnd, node_id, position=0, show_time=True, reverse=False, default_placement="bottom")

    card_id = ui.create_timeline(
        hwnd, root,
        [
            {"timestamp": "2018/4/12", "content": "更新模板", "type": 0, "icon": "🧩", "placement": "top",
             "card_title": "更新项目模板 🧩", "card_body": "王小虎 提交于 2018/4/12 20:46"},
            {"timestamp": "2018/4/3", "content": "同步文档", "type": 1, "icon": "📚", "placement": "top",
             "card_title": "同步组件文档 📚", "card_body": "王小虎 提交于 2018/4/3 20:46"},
            {"timestamp": "2018/4/2", "content": "归档记录", "type": 2, "icon": "🗃️", "placement": "top",
             "card_title": "归档发布记录 🗃️", "card_body": "王小虎 提交于 2018/4/2 20:46"},
        ],
        30, 390, 520, 280,
    )
    assert card_id > 0
    assert ui.get_timeline_item_count(hwnd, card_id) == 3
    ui.set_timeline_advanced_options(hwnd, card_id, position=0, show_time=True, reverse=False, default_placement="top")

    alt_id = ui.create_timeline(
        hwnd, root,
        [
            {"timestamp": "09:00", "content": "🚀 创建任务", "type": 0, "icon": "🚀"},
            {"timestamp": "10:30", "content": "✅ 完成复核", "type": 1, "icon": "✅"},
            {"timestamp": "14:20", "content": "📦 发布版本", "type": 2, "icon": "📦"},
        ],
        590, 430, 480, 210,
    )
    assert alt_id > 0
    ui.set_timeline_advanced_options(hwnd, alt_id, position=2, show_time=True, reverse=False, default_placement="top")

    print("[读回] 基础时间线=", ui.get_timeline_advanced_options(hwnd, base_id))
    print("[读回] 节点样式项目数=", ui.get_timeline_item_count(hwnd, node_id))
    print("[读回] 卡片时间线项目数=", ui.get_timeline_item_count(hwnd, card_id))
    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(int(os.environ.get("NEW_EMOJI_TEST_SECONDS", "6")))
    print("时间线全样式完成验证结束。")


if __name__ == "__main__":
    main()
