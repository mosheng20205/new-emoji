import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_drawer_id = 0
g_close_events = []
g_before_events = []


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 抽屉完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ValueCallback
def on_drawer_close(element_id, close_count, placement, action):
    g_close_events.append((element_id, close_count, placement, action))
    print(f"[抽屉关闭回调] 元素={element_id} 次数={close_count} 位置={placement} 动作={action}")


@ui.BeforeCloseCallback
def on_before_close(element_id, action):
    g_before_events.append((element_id, action))
    print(f"[抽屉关闭拦截] 元素={element_id} 动作={action}")
    return 0


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


def assert_true(value, message):
    if not value:
        raise RuntimeError(message)


def assert_equal(actual, expected, message):
    if actual != expected:
        raise RuntimeError(f"{message}: actual={actual!r} expected={expected!r}")


def main():
    global g_hwnd, g_drawer_id

    hwnd = ui.create_window("🧭 抽屉完整组件验证", 220, 80, 1080, 760)
    assert_true(hwnd, "窗口创建失败")
    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)

    content_id = ui.create_container(hwnd, 0, 0, 0, 1040, 700)
    ui.create_text(hwnd, content_id, "🧭 Drawer 抽屉完整封装", 32, 28, 620, 40)
    intro_id = ui.create_text(
        hwnd,
        content_id,
        "验证方向、百分比尺寸、无标题栏、真实表格/表单 slot、before-close、ESC 开关和嵌套抽屉。",
        32,
        78,
        900,
        56,
    )
    ui.set_text_options(hwnd, intro_id, align=0, valign=0, wrap=True, ellipsis=False)
    ui.create_button(hwnd, content_id, "📌", "背景操作：抽屉覆盖其上", 52, 168, 250, 44)
    ui.create_text(hwnd, content_id, "✨ 首屏保留足够余量，右侧抽屉宽度 320px。", 52, 238, 620, 34)

    g_drawer_id = ui.create_drawer(
        hwnd,
        title="🧭 任务详情",
        body="这里显示中文说明、emoji 状态和抽屉内容。打开动画、关闭动作和状态读回都应可验证。",
        placement=1,
        modal=True,
        closable=True,
        size=320,
    )
    ui.set_drawer_animation(hwnd, g_drawer_id, 360)
    ui.set_drawer_options(hwnd, g_drawer_id, placement=1, open=True,
                          modal=True, closable=True, close_on_mask=True, size=320)
    ui.set_drawer_close_callback(hwnd, g_drawer_id, on_drawer_close)

    assert_true("任务详情" in ui.get_drawer_text(hwnd, g_drawer_id, 0), "抽屉标题读回失败")
    assert_true("中文说明" in ui.get_drawer_text(hwnd, g_drawer_id, 1), "抽屉正文读回失败")

    content_parent = ui.get_drawer_content_parent(hwnd, g_drawer_id)
    footer_parent = ui.get_drawer_footer_parent(hwnd, g_drawer_id)
    assert_true(content_parent > 0 and footer_parent > 0, "抽屉 slot 容器读回失败")

    advanced = ui.get_drawer_advanced_options(hwnd, g_drawer_id)
    assert_true(advanced is not None, "抽屉高级状态读回失败")
    assert_equal(advanced["content_parent_id"], content_parent, "内容 slot ID 不一致")
    assert_equal(advanced["footer_parent_id"], footer_parent, "页脚 slot ID 不一致")
    assert_true(advanced["show_header"] and advanced["show_close"] and advanced["close_on_escape"],
                "默认标题栏/关闭/ESC 状态失败")

    ui.create_table(
        hwnd,
        content_parent,
        columns=["日期", "姓名", "地址"],
        rows=[
            ["2026-05-02", "王小虎", "上海市普陀区金沙江路 1518 弄"],
            ["2026-05-04", "李小萌", "北京市朝阳区望京路 88 号"],
            ["2026-05-06", "陈小南", "杭州市西湖区文三路 99 号"],
        ],
        x=0, y=0, w=360, h=150,
    )
    ui.create_input(hwnd, content_parent, value="春日活动", placeholder="请输入活动名称",
                    prefix_icon="🎪", clearable=True, x=0, y=170, w=250, h=36)
    ui.create_select(hwnd, content_parent, text="请选择活动区域",
                     options=["区域一", "区域二", "区域三"], selected=1,
                     x=0, y=218, w=250, h=36)
    ui.create_button(hwnd, footer_parent, "❌", "取消", 120, 12, 90, 36)
    ui.create_button(hwnd, footer_parent, "✅", "确定", 224, 12, 90, 36)

    initial = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[初始完整状态]", initial)
    assert_true(initial and initial["open"], "抽屉初始打开状态失败")
    assert_equal(initial["placement"], 1, "右侧抽屉方向失败")
    assert_equal(initial["size"], 320, "右侧抽屉尺寸失败")
    assert_true(initial["timer_running"], "抽屉动画计时器未启动")

    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    pump_messages(user32, msg, 0.45)
    animated = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[动画推进状态]", animated)
    assert_true(animated["tick_count"] > initial["tick_count"], "抽屉动画推进失败")
    assert_true(animated["animation_progress"] >= 75, "抽屉动画进度不足")

    for placement, size in ((0, 300), (1, 320), (2, 220), (3, 240)):
        ui.set_drawer_options(hwnd, g_drawer_id, placement=placement, open=True,
                              modal=True, closable=True, close_on_mask=True, size=size)
        state = ui.get_drawer_options(hwnd, g_drawer_id)
        assert_equal(state[0], placement, "抽屉方向读回失败")
        assert_equal(state[5], size, "抽屉像素尺寸读回失败")

    ui.set_drawer_options(hwnd, g_drawer_id, placement=1, open=True,
                          modal=True, closable=True, close_on_mask=True, size=320)
    ui.set_drawer_advanced_options(hwnd, g_drawer_id, size_mode=1, size_value=50)
    advanced = ui.get_drawer_advanced_options(hwnd, g_drawer_id)
    assert_equal(advanced["size_mode"], 1, "抽屉百分比尺寸模式失败")
    assert_equal(advanced["size_value"], 50, "抽屉百分比尺寸值失败")

    ui.set_drawer_advanced_options(hwnd, g_drawer_id, show_header=False,
                                   show_close=False, close_on_escape=False,
                                   content_padding=18, footer_height=64,
                                   size_mode=0, size_value=340)
    advanced = ui.get_drawer_advanced_options(hwnd, g_drawer_id)
    assert_true(not advanced["show_header"] and not advanced["show_close"], "抽屉无标题栏状态失败")
    assert_true(not advanced["close_on_escape"], "抽屉 ESC 关闭开关失败")
    assert_equal(advanced["content_padding"], 18, "抽屉内容 padding 读回失败")
    assert_equal(advanced["footer_height"], 64, "抽屉页脚高度读回失败")

    ui.dll.EU_SetElementFocus(hwnd, g_drawer_id)
    user32.PostMessageW(hwnd, 0x0100, 0x1B, 0)  # VK_ESCAPE
    pump_messages(user32, msg, 0.25)
    assert_true(ui.get_drawer_full_state(hwnd, g_drawer_id)["open"], "关闭 ESC 后抽屉不应关闭")

    ui.set_drawer_advanced_options(hwnd, g_drawer_id, show_header=True,
                                   show_close=True, close_on_escape=True,
                                   content_padding=20, footer_height=58,
                                   size_mode=0, size_value=320)
    ui.set_drawer_before_close_callback(hwnd, g_drawer_id, on_before_close)
    ui.trigger_drawer_close(hwnd, g_drawer_id)
    blocked = ui.get_drawer_advanced_options(hwnd, g_drawer_id)
    assert_true(ui.get_drawer_full_state(hwnd, g_drawer_id)["open"], "before-close 拦截后抽屉应保持打开")
    assert_true(blocked["close_pending"], "before-close pending 状态失败")
    assert_true(g_before_events and g_before_events[-1] == (g_drawer_id, 4), "before-close 回调失败")

    ui.confirm_drawer_close(hwnd, g_drawer_id, False)
    canceled = ui.get_drawer_advanced_options(hwnd, g_drawer_id)
    assert_true(not canceled["close_pending"], "取消关闭后 pending 应清除")
    assert_true(ui.get_drawer_full_state(hwnd, g_drawer_id)["open"], "取消关闭后抽屉应仍打开")

    ui.trigger_drawer_close(hwnd, g_drawer_id)
    ui.confirm_drawer_close(hwnd, g_drawer_id, True)
    closed = ui.get_drawer_full_state(hwnd, g_drawer_id)
    print("[确认关闭状态]", closed)
    assert_true(not closed["open"], "确认关闭后抽屉应关闭")
    assert_true(g_close_events and g_close_events[-1][1] == closed["close_count"], "抽屉关闭回调失败")

    outer = ui.create_drawer(hwnd, "🧳 外层抽屉", "外层内容 slot 中可以打开内层。", 1, True, True, 460)
    ui.set_drawer_options(hwnd, outer, placement=1, open=True, modal=True,
                          closable=True, close_on_mask=True, size=460)
    outer_content = ui.get_drawer_content_parent(hwnd, outer)
    ui.create_button(hwnd, outer_content, "🧩", "打开内层抽屉", 0, 0, 180, 38)
    inner = ui.create_drawer(hwnd, "🪆 内层抽屉", "这是 append-to-body 等价的根级内层抽屉。", 1, True, True, 280)
    ui.set_drawer_options(hwnd, inner, placement=1, open=True, modal=True,
                          closable=True, close_on_mask=True, size=280)
    assert_true(ui.get_drawer_full_state(hwnd, outer)["open"], "外层抽屉打开失败")
    assert_true(ui.get_drawer_full_state(hwnd, inner)["open"], "内层抽屉打开失败")
    assert_true(inner > outer, "内层抽屉应后创建并位于更高绘制层")

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("[提示] 窗口将保持 60 秒，可检查中文、emoji、表格/表单 slot、无标题栏、嵌套抽屉和首屏尺寸。")
    pump_messages(user32, msg, 60.0)
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
