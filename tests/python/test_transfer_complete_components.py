import ctypes
import os
import time
from ctypes import wintypes

import test_new_emoji as ui


g_hwnd = None
g_transfer_id = 0
g_status_id = 0


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] Transfer 完整样式验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def set_status(text):
    if g_status_id:
        ui.set_element_text(g_hwnd, g_status_id, text)


def run_api_checks(hwnd, transfer_id):
    options = ui.get_transfer_options(hwnd, transfer_id)
    assert options and options["filterable"]
    assert options["multiple"]
    assert options["show_footer"]
    assert ui.get_transfer_text(hwnd, transfer_id, 0) == "📥 来源列表"
    assert ui.get_transfer_text(hwnd, transfer_id, 1) == "📤 目标列表"
    assert "{key}" in ui.get_transfer_text(hwnd, transfer_id, 6)
    assert ui.get_transfer_text(hwnd, transfer_id, 9) == "请输入城市拼音 🔎"

    ui.set_transfer_filters(hwnd, transfer_id, "bei", "")
    assert ui.get_transfer_matched_count(hwnd, transfer_id, 0) == 1
    ui.set_transfer_item_disabled(hwnd, transfer_id, 0, 0, True)
    assert ui.get_transfer_item_disabled(hwnd, transfer_id, 0, 0) == 1
    assert ui.get_transfer_disabled_count(hwnd, transfer_id, 0) >= 1

    ui.set_transfer_checked_keys(hwnd, transfer_id, ["guangzhou", "shenzhen"], ["shanghai"])
    assert ui.get_transfer_checked_count(hwnd, transfer_id, 0) == 2
    assert ui.get_transfer_checked_count(hwnd, transfer_id, 1) == 1

    ui.set_transfer_filters(hwnd, transfer_id, "", "")
    ui.transfer_move_right(hwnd, transfer_id)
    values = ui.get_transfer_value_keys(hwnd, transfer_id)
    assert "shanghai" in values and "guangzhou" in values and "shenzhen" in values

    message = (
        f"✅ API 验证通过：左侧 {ui.get_transfer_count(hwnd, transfer_id, 0)} 项，"
        f"右侧 {ui.get_transfer_count(hwnd, transfer_id, 1)} 项，目标值 {values}"
    )
    set_status(message)
    print("[验证通过]", message)


def main():
    global g_hwnd, g_transfer_id, g_status_id

    hwnd = ui.create_window("🔁 Transfer 完整样式验证", 230, 90, 980, 640)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 940, 580)

    ui.create_text(hwnd, content_id, "🔁 Transfer：搜索、禁用、模板、字段映射、底部操作", 28, 24, 760, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证 Element UI Transfer 的核心样式与扩展 API：目标值、默认勾选、格式模板、筛选匹配和禁用项读回。",
        28, 64, 860, 44,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    items = [
        {"key": "beijing", "label": "🏛️ 北京", "value": "beijing", "desc": "华北", "pinyin": "beijing"},
        {"key": "shanghai", "label": "🏙️ 上海", "value": "shanghai", "desc": "华东", "pinyin": "shanghai"},
        {"key": "guangzhou", "label": "🌸 广州", "value": "guangzhou", "desc": "华南", "pinyin": "guangzhou"},
        {"key": "shenzhen", "label": "🚄 深圳", "value": "shenzhen", "desc": "科技", "pinyin": "shenzhen"},
        {"key": "nanjing", "label": "🌙 南京", "value": "nanjing", "desc": "古都", "pinyin": "nanjing"},
    ]
    g_transfer_id = ui.create_transfer_ex(
        hwnd,
        content_id,
        items,
        target_keys=["shanghai"],
        filterable=True,
        multiple=True,
        show_footer=True,
        titles=("📥 来源列表", "📤 目标列表"),
        button_texts=("到左边", "到右边"),
        fmt=("${total}", "${checked}/${total}"),
        item_template="{key} - {label} · {desc}",
        footer_texts=("⚙️ 来源操作", "✅ 目标操作"),
        filter_placeholder="请输入城市拼音 🔎",
        x=28, y=126, w=860, h=260,
    )

    g_status_id = ui.create_text(hwnd, content_id, "⏳ 正在验证 Transfer 扩展 API...", 28, 414, 860, 38)
    ui.set_text_options(hwnd, g_status_id, align=0, valign=0, wrap=True, ellipsis=False)

    ui.dll.EU_ShowWindow(hwnd, 1)
    run_api_checks(hwnd, g_transfer_id)

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    timeout = int(os.environ.get("NEW_EMOJI_TEST_SECONDS", "8"))
    start = time.time()
    while time.time() - start < timeout:
        handled = False
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            handled = True
            if msg.message in (0x0012, 0x0002):
                return
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        if not handled:
            time.sleep(0.01)

    print("[结束] Transfer 完整样式验证结束")


if __name__ == "__main__":
    main()
