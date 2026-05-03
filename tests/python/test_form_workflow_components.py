import ctypes
from ctypes import wintypes
import sys
import time

import test_new_emoji as ui

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WINDOW_W = 1040
WINDOW_H = 800
CONTENT_W = 1010
CONTENT_H = 750

g_hwnd = None
g_title_input_id = 0
g_tags_id = 0
g_priority_id = 0
g_rate_id = 0
g_color_id = 0
g_progress_id = 0
g_result_id = 0
g_notice_id = 0
g_loading_id = 0
g_dialog_id = 0
g_drawer_id = 0
g_fill_id = 0
g_submit_id = 0
g_reset_id = 0
g_dialog_btn_id = 0
g_drawer_btn_id = 0
g_dark_id = 0
g_light_id = 0
g_submitted = False


def utf8_arg(text: str):
    data = ui.make_utf8(text)
    return ui.bytes_arg(data), len(data)


def set_input(element_id: int, text: str):
    data, length = utf8_arg(text)
    ui.dll.EU_SetInputValue(g_hwnd, element_id, data, length)


def set_tags(tags):
    data, length = utf8_arg("|".join(tags))
    ui.dll.EU_SetInputTagTags(g_hwnd, g_tags_id, data, length)


def set_result(subtitle: str, result_type: int):
    data, length = utf8_arg(subtitle)
    ui.dll.EU_SetResultSubtitle(g_hwnd, g_result_id, data, length)
    ui.dll.EU_SetResultType(g_hwnd, g_result_id, result_type)


def set_notice(body: str, notify_type: int):
    data, length = utf8_arg(body)
    ui.dll.EU_SetNotificationBody(g_hwnd, g_notice_id, data, length)
    ui.dll.EU_SetNotificationType(g_hwnd, g_notice_id, notify_type)


def set_dialog(title: str, body: str):
    title_data, title_len = utf8_arg(title)
    body_data, body_len = utf8_arg(body)
    ui.dll.EU_SetDialogTitle(g_hwnd, g_dialog_id, title_data, title_len)
    ui.dll.EU_SetDialogBody(g_hwnd, g_dialog_id, body_data, body_len)


def set_drawer(title: str, body: str):
    title_data, title_len = utf8_arg(title)
    body_data, body_len = utf8_arg(body)
    ui.dll.EU_SetDrawerTitle(g_hwnd, g_drawer_id, title_data, title_len)
    ui.dll.EU_SetDrawerBody(g_hwnd, g_drawer_id, body_data, body_len)


def read_input(element_id: int) -> str:
    buf = (ctypes.c_ubyte * 512)()
    needed = ui.dll.EU_GetElementText(g_hwnd, element_id, buf, len(buf))
    if needed <= 0:
        return ""
    return bytes(buf[: min(needed, len(buf) - 1)]).decode("utf-8", errors="replace")


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 🧾 表单工作流示例正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ResizeCallback
def on_resize(hwnd, width, height):
    print(f"[窗口尺寸] 🪟 宽 {width}，高 {height}")


@ui.ClickCallback
def on_click(element_id):
    global g_submitted

    if element_id == g_fill_id:
        set_input(g_title_input_id, "🧩 新增自适应数据看板")
        set_tags(["📐 自适应", "🎨 主题", "😊 emoji", "🚀 优先"])
        ui.dll.EU_SetSelectV2Index(g_hwnd, g_priority_id, 2)
        ui.dll.EU_SetRateValue(g_hwnd, g_rate_id, 5)
        ui.dll.EU_SetColorPickerColor(g_hwnd, g_color_id, 0xFF22C55E)
        ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_id, 45)
        set_notice("📝 已填充一组中文 + emoji 的需求草稿。", 0)
        set_result("✍️ 草稿已准备，可以点击提交。", 0)
        print("[表单] 📝 已填充示例数据")

    elif element_id == g_submit_id:
        g_submitted = True
        title = read_input(g_title_input_id) or "未命名需求"
        rate = ui.dll.EU_GetRateValue(g_hwnd, g_rate_id)
        priority = ui.dll.EU_GetSelectV2Index(g_hwnd, g_priority_id)
        color = ui.dll.EU_GetColorPickerColor(g_hwnd, g_color_id) & 0xFFFFFFFF
        ui.dll.EU_SetLoadingActive(g_hwnd, g_loading_id, 1)
        ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_id, 100)
        set_notice(f"✅ 已提交：{title}；优先级索引 {priority}，评分 {rate}，颜色 0x{color:08X}。", 1)
        set_result("✅ 表单已提交，右侧反馈组件已同步更新。", 1)
        set_dialog("✅ 提交成功", f"需求：{title}\n评分：{rate}\n颜色：0x{color:08X}")
        set_drawer("📋 提交详情", f"需求标题：{title}\n标签和选项已写入 DLL 组件状态。\n后续可接入真实业务保存。")
        print(f"[提交] ✅ title={title}, priority={priority}, rate={rate}, color=0x{color:08X}")

    elif element_id == g_reset_id:
        g_submitted = False
        set_input(g_title_input_id, "")
        set_tags(["需求", "评审"])
        ui.dll.EU_SetSelectV2Index(g_hwnd, g_priority_id, 0)
        ui.dll.EU_SetRateValue(g_hwnd, g_rate_id, 3)
        ui.dll.EU_SetColorPickerColor(g_hwnd, g_color_id, 0xFF1E66F5)
        ui.dll.EU_SetProgressPercentage(g_hwnd, g_progress_id, 12)
        ui.dll.EU_SetLoadingActive(g_hwnd, g_loading_id, 0)
        set_notice("♻️ 表单已重置，等待重新填写。", 0)
        set_result("📭 暂无提交结果。", 0)
        print("[表单] ♻️ 已重置")

    elif element_id == g_dialog_btn_id:
        if not g_submitted:
            set_dialog("💡 提示", "请先点击“提交需求”，再查看提交弹窗。")
        ui.dll.EU_SetDialogOpen(g_hwnd, g_dialog_id, 1)
        print("[弹窗] 💬 打开对话框")

    elif element_id == g_drawer_btn_id:
        if not g_submitted:
            set_drawer("📋 草稿详情", "当前仍是草稿状态，可以先填充示例数据再提交。")
        ui.dll.EU_SetDrawerOpen(g_hwnd, g_drawer_id, 1)
        print("[抽屉] 📋 打开抽屉")

    elif element_id == g_dark_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 1)
        print("[主题] 🌙 深色")

    elif element_id == g_light_id:
        ui.dll.EU_SetThemeMode(g_hwnd, 0)
        print("[主题] ☀️ 浅色")


def main():
    global g_hwnd, g_title_input_id, g_tags_id, g_priority_id, g_rate_id, g_color_id
    global g_progress_id, g_result_id, g_notice_id, g_loading_id, g_dialog_id, g_drawer_id
    global g_fill_id, g_submit_id, g_reset_id, g_dialog_btn_id, g_drawer_btn_id, g_dark_id, g_light_id

    hwnd = ui.create_window("🧾 表单工作流组件示例", 210, 70, WINDOW_W, WINDOW_H)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)

    content_id = ui.create_container(hwnd, 0, 0, 0, CONTENT_W, CONTENT_H)
    ui.create_text(hwnd, content_id, "🧾 表单工作流组件", 28, 24, 320, 32)
    ui.create_divider(
        hwnd, content_id,
        "✍️ 输入 / 🏷️ 标签 / 🎚️ 选择评分 / 🔔 反馈 / 💬 弹窗抽屉",
        0, 1, 28, 66, 932, 34
    )

    ui.create_text(hwnd, content_id, "✍️ 需求信息", 28, 120, 180, 26)
    g_title_input_id = ui.create_input(
        hwnd, content_id,
        "", "请输入需求标题", "🧩", "", True,
        28, 158, 420, 40
    )
    g_tags_id = ui.create_input_tag(
        hwnd, content_id,
        ["需求", "评审"], "输入标签",
        28, 218, 420, 76
    )
    g_priority_id = ui.create_select_v2(
        hwnd, content_id,
        "🚦 优先级",
        ["低优先级", "普通优先级", "高优先级", "紧急上线"],
        0, 4, 28, 314, 420, 40
    )
    g_rate_id = ui.create_rate(hwnd, content_id, "⭐ 体验评分", 3, 5, 28, 374, 220, 40)
    g_color_id = ui.create_colorpicker(hwnd, content_id, "🎨 主题色", 0xFF1E66F5, 268, 374, 180, 40)
    g_progress_id = ui.create_progress(hwnd, content_id, "🚚 提交流程", 12, 0, 28, 438, 420, 44)

    g_fill_id = ui.create_button(hwnd, content_id, "📝", "填充示例", 28, 520, 122, 42)
    g_submit_id = ui.create_button(hwnd, content_id, "✅", "提交需求", 166, 520, 122, 42)
    g_reset_id = ui.create_button(hwnd, content_id, "♻️", "重置表单", 304, 520, 122, 42)
    g_dialog_btn_id = ui.create_button(hwnd, content_id, "💬", "查看弹窗", 28, 580, 122, 42)
    g_drawer_btn_id = ui.create_button(hwnd, content_id, "📋", "查看抽屉", 166, 580, 122, 42)
    g_dark_id = ui.create_button(hwnd, content_id, "🌙", "深色主题", 304, 580, 122, 42)
    g_light_id = ui.create_button(hwnd, content_id, "☀️", "浅色主题", 304, 640, 122, 42)

    ui.create_text(hwnd, content_id, "🔔 处理反馈", 500, 120, 180, 26)
    g_result_id = ui.create_result(
        hwnd, content_id,
        "📭 等待提交", "📭 暂无提交结果。",
        0, 500, 158, 220, 170
    )
    g_notice_id = ui.create_notification(
        hwnd, content_id,
        "🔔 工作流通知", "📝 请填写左侧表单，或点击填充示例。",
        0, True, 740, 158, 220, 118
    )
    g_loading_id = ui.create_loading(
        hwnd, content_id,
        "⏳ 提交状态",
        False, 740, 300, 220, 150
    )
    ui.create_alert(
        hwnd, content_id,
        "📐 首屏尺寸",
        f"🖥️ 窗口 {WINDOW_W}x{WINDOW_H}，容器 {CONTENT_W}x{CONTENT_H}；内容右边界 960，底边界 704。",
        0, 0, False,
        500, 486, 460, 56
    )

    g_dialog_id = ui.create_dialog(
        hwnd, "💡 提示", "请先点击“提交需求”，再查看提交弹窗。",
        True, True, 460, 250
    )
    g_drawer_id = ui.create_drawer(
        hwnd, "📋 草稿详情", "当前仍是草稿状态，可以先填充示例数据再提交。",
        1, True, True, 320
    )

    for eid in (
        g_fill_id, g_submit_id, g_reset_id, g_dialog_btn_id, g_drawer_btn_id,
        g_dark_id, g_light_id,
    ):
        ui.dll.EU_SetElementClickCallback(hwnd, eid, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("🧾 表单工作流组件示例已显示。关闭窗口或等待 60 秒。")

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

    print("🧾 表单工作流组件示例结束。")


if __name__ == "__main__":
    main()
