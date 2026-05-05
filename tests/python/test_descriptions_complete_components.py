import time
import ctypes

import test_new_emoji as ui


g_hwnd = None
g_desc_id = 0
g_click_count = 0


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    global g_click_count
    if element_id == g_desc_id:
        g_click_count += 1


def main():
    global g_hwnd, g_desc_id

    hwnd = ui.create_window("📋 描述列表全样式验证", 160, 90, 1180, 760)
    if not hwnd:
        print("错误：窗口创建失败")
        return
    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1140, 700)
    ui.create_text(hwnd, root, "📋 Descriptions 描述列表全样式验证", 28, 18, 520, 34)

    legacy = ui.create_descriptions(
        hwnd, root, "✅ 旧接口兼容",
        [("组件", "Descriptions"), ("状态", "旧 API 可用")],
        2, True, 28, 70, 500, 120,
    )
    assert legacy
    assert ui.get_descriptions_item_count(hwnd, legacy) == 2

    rich_items = [
        {"label": "用户名", "content": "kooriookami", "label_icon": "👤"},
        {"label": "手机号", "content": "18100000000", "label_icon": "📱"},
        {"label": "居住地", "content": "苏州市", "label_icon": "📍", "span": 2},
        {"label": "备注", "content": "学校", "label_icon": "🏷️", "content_type": 1, "tag_type": 1},
        {"label": "联系地址", "content": "江苏省苏州市吴中区吴中大道 1188 号", "label_icon": "🏢", "span": 3, "content_align": 2},
    ]
    g_desc_id = ui.create_descriptions(
        hwnd, root, "⚙️ 高级接口",
        rich_items, 3, True, 560, 70, 540, 180,
        label_width=112, min_row_height=44, wrap_values=True, responsive=False,
    )
    assert g_desc_id
    ui.set_descriptions_layout(hwnd, g_desc_id, direction=0, size=0, columns=3, bordered=True)
    ui.set_descriptions_items_ex(hwnd, g_desc_id, rich_items)
    ui.set_descriptions_colors(hwnd, g_desc_id, 0xFFD2DCEB, 0xFFE1F3D8, 0, 0xFF53627A, 0, 0)
    ui.set_descriptions_extra(hwnd, g_desc_id, "⚙️", "操作", True, 1)
    ui.dll.EU_SetElementClickCallback(hwnd, g_desc_id, on_click)

    vertical = ui.create_descriptions(
        hwnd, root, "📐 垂直带边框",
        rich_items, 4, True, 28, 230, 520, 190,
        label_width=100, min_row_height=62, wrap_values=True, responsive=False,
    )
    assert vertical
    ui.set_descriptions_layout(hwnd, vertical, direction=1, size=1, columns=4, bordered=True)
    ui.set_descriptions_items_ex(hwnd, vertical, rich_items)

    plain = ui.create_descriptions(
        hwnd, root, "🧾 垂直无边框",
        rich_items, 4, False, 580, 280, 520, 160,
        label_width=100, min_row_height=58, wrap_values=True, responsive=False,
    )
    assert plain
    ui.set_descriptions_layout(hwnd, plain, direction=1, size=3, columns=4, bordered=False)
    ui.set_descriptions_items_ex(hwnd, plain, rich_items)

    state = ui.get_descriptions_full_state(hwnd, g_desc_id)
    assert state["direction"] == 0
    assert state["size"] == 0
    assert state["columns"] == 3
    assert state["bordered"] is True
    assert state["item_count"] == len(rich_items)
    assert state["responsive"] is False
    assert state["wrap_values"] is True

    ui.dll.EU_ShowWindow(hwnd, 1)
    user32 = ctypes.windll.user32
    user32.UpdateWindow(hwnd)
    dpi = user32.GetDpiForWindow(hwnd) if hasattr(user32, "GetDpiForWindow") else 96
    scale = dpi / 96.0
    for candidate_scale in (1.0, scale):
        for dx in (28, 56, 92):
            for dy in (14, 22, 30):
                click_x = int((560 + 540 - dx) * candidate_scale)
                click_y = int((70 + dy) * candidate_scale)
                lparam = (click_y << 16) | click_x
                user32.SendMessageW(hwnd, 0x0201, 1, lparam)
                user32.SendMessageW(hwnd, 0x0202, 0, lparam)
    clicked_state = ui.get_descriptions_full_state(hwnd, g_desc_id)
    assert clicked_state["extra_click_count"] >= 1
    assert g_click_count >= 1
    time.sleep(0.8)
    ui.dll.EU_DestroyWindow(hwnd)
    print("✅ Descriptions 描述列表全样式 API 验证完成")


if __name__ == "__main__":
    main()
