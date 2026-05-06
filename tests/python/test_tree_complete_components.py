import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


g_hwnd = None
g_tree_id = 0
g_json_tree_id = 0
g_expand_id = 0
g_check_id = 0


TREE_ITEMS = [
    ("📦 组件库", 0, True, True, False),
    ("🧱 基础组件", 1, True, True, False),
    ("🔘 按钮组件", 2, True, False, False),
    ("📝 输入组件", 2, True, False, False),
    ("🧭 导航组件", 1, False, False, True),
    ("🌲 树选择器", 2, True, False, False),
    ("🔀 穿梭框", 2, True, False, False),
    ("📊 数据展示", 1, True, False, False),
]

TREE_JSON_DATA = {
    "props": {"label": "name", "children": "zones", "isLeaf": "leaf"},
    "defaultExpandedKeys": ["json-root", "json-team"],
    "defaultCheckedKeys": ["json-ui"],
    "currentKey": "json-ui",
    "data": [
        {
            "key": "json-root",
            "name": "📦 JSON 项目资源",
            "icon": "📦",
            "tag": "主目录",
            "zones": [
                {
                    "key": "json-team",
                    "name": "👥 研发小组",
                    "icon": "👥",
                    "tag": "展开",
                    "zones": [
                        {"key": "json-ui", "name": "🎨 界面任务", "leaf": True, "tag": "进行中"},
                        {"key": "json-disabled", "name": "🔒 冻结节点", "leaf": True, "disabled": True},
                    ],
                },
                {"key": "json-lazy", "name": "⏳ 懒加载分支", "lazy": True, "leaf": False},
            ],
        }
    ],
}


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 树组件完整验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


@ui.ClickCallback
def on_click(element_id):
    if element_id == g_expand_id:
        ui.set_tree_item_expanded(g_hwnd, g_tree_id, 4, True)
        options = ui.get_tree_options(g_hwnd, g_tree_id)
        print(
            "[懒加载] "
            f"可见节点={ui.get_tree_visible_count(g_hwnd, g_tree_id)} "
            f"最后请求={options['last_lazy_index']} "
            f"待加载={ui.get_tree_item_lazy(g_hwnd, g_tree_id, 4)}"
        )
    elif element_id == g_check_id:
        ui.set_tree_item_checked(g_hwnd, g_tree_id, 5, True)
        ui.set_tree_selected(g_hwnd, g_tree_id, 5)
        options = ui.get_tree_options(g_hwnd, g_tree_id)
        print(
            "[勾选] "
            f"选中={ui.get_tree_selected(g_hwnd, g_tree_id)} "
            f"已勾选={options['checked_count']} "
            f"节点勾选={ui.get_tree_item_checked(g_hwnd, g_tree_id, 5)}"
        )


def main():
    global g_hwnd, g_tree_id, g_json_tree_id, g_expand_id, g_check_id

    hwnd = ui.create_window("🌲 树组件完整验证", 220, 80, 760, 560)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    g_hwnd = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content_id = ui.create_container(hwnd, 0, 0, 0, 740, 510)

    ui.create_text(hwnd, content_id, "🌲 树组件：复选、键盘、懒加载", 28, 24, 520, 36)
    desc_id = ui.create_text(
        hwnd,
        content_id,
        "本窗口验证树节点展开、复选框、懒加载请求状态、可见节点数量和方向键/空格键导航。",
        28, 66, 640, 48,
    )
    ui.set_text_options(hwnd, desc_id, align=0, valign=0, wrap=True, ellipsis=False)

    g_tree_id = ui.create_tree(hwnd, content_id, TREE_ITEMS, 0, 28, 128, 420, 300)
    ui.set_tree_options(hwnd, g_tree_id, show_checkbox=True, keyboard_navigation=True, lazy_mode=True)
    ui.set_tree_item_lazy(hwnd, g_tree_id, 4, True)

    ui.create_text(hwnd, content_id, "🧩 JSON 高级树", 482, 128, 220, 30)
    g_json_tree_id = ui.create_tree_json(
        hwnd, content_id, TREE_JSON_DATA,
        options={
            "showCheckbox": True,
            "lazy": True,
            "accordion": True,
            "draggable": True,
            "showActions": True,
            "filterText": "JSON",
        },
        x=482, y=164, w=230, h=128,
    )
    ui.append_tree_node_json(hwnd, g_json_tree_id, "json-team", {
        "key": "json-added",
        "label": "✨ 动态追加",
        "leaf": True,
        "tag": "新增",
    })
    ui.update_tree_node_json(hwnd, g_json_tree_id, "json-added", {
        "key": "json-added",
        "label": "✨ 动态已更新",
        "leaf": True,
        "tag": "更新",
    })
    ui.set_tree_checked_keys_json(hwnd, g_json_tree_id, ["json-ui", "json-disabled"])
    ui.set_tree_expanded_keys_json(hwnd, g_json_tree_id, ["json-root", "json-team", "json-lazy"])
    ui.set_tree_expanded_keys_json(hwnd, g_json_tree_id, ["json-root"])
    ui.append_tree_node_json(hwnd, g_json_tree_id, "json-team", {
        "key": "json-hidden-add",
        "label": "✨ 折叠父级下的新增项",
        "leaf": True,
        "tag": "隐藏",
    })
    collapsed_after_append = ui.get_tree_state_json(hwnd, g_json_tree_id)
    if "json-team" in collapsed_after_append.get("expandedKeys", []):
        raise AssertionError(f"普通追加不应强制展开父节点: {collapsed_after_append}")
    ui.set_tree_options_json(hwnd, g_json_tree_id, {"filterText": "动态"})
    ui.set_tree_expanded_keys_json(hwnd, g_json_tree_id, [])
    filtered_collapsed = ui.get_tree_state_json(hwnd, g_json_tree_id)
    if filtered_collapsed.get("visibleCount", 0) > 1:
        raise AssertionError(f"过滤状态折叠根节点后仍暴露子节点: {filtered_collapsed}")
    ui.set_tree_options_json(hwnd, g_json_tree_id, {"filterText": "JSON"})
    ui.set_tree_expanded_keys_json(hwnd, g_json_tree_id, ["json-root", "json-lazy"])

    g_expand_id = ui.create_button(hwnd, content_id, "⏳", "展开待加载", 482, 310, 180, 42)
    g_check_id = ui.create_button(hwnd, content_id, "✅", "勾选树选择器", 482, 366, 180, 42)
    ui.dll.EU_SetElementClickCallback(hwnd, g_expand_id, on_click)
    ui.dll.EU_SetElementClickCallback(hwnd, g_check_id, on_click)

    ui.dll.EU_ShowWindow(hwnd, 1)
    ui.dll.EU_SetElementFocus(hwnd, g_tree_id)

    initial = ui.get_tree_options(hwnd, g_tree_id)
    json_state = ui.get_tree_state_json(hwnd, g_json_tree_id)
    checked_keys = ui.get_tree_checked_keys_json(hwnd, g_json_tree_id)
    expanded_keys = ui.get_tree_expanded_keys_json(hwnd, g_json_tree_id)
    if "json-ui" not in checked_keys or "json-disabled" in checked_keys:
        raise AssertionError(f"JSON 勾选键读回异常: {checked_keys}")
    if "json-root" not in expanded_keys or "json-lazy" not in expanded_keys:
        raise AssertionError(f"JSON 展开键读回异常: {expanded_keys}")
    if not json_state.get("showCheckbox") or not json_state.get("draggable"):
        raise AssertionError(f"JSON 选项读回异常: {json_state}")
    print(
        "[初始] "
        f"复选={initial['show_checkbox']} "
        f"键盘={initial['keyboard_navigation']} "
        f"懒加载={initial['lazy_mode']} "
        f"可见节点={ui.get_tree_visible_count(hwnd, g_tree_id)}"
    )
    print(f"[JSON] 状态={json_state} 勾选={checked_keys} 展开={expanded_keys}")
    print("树组件完整验证已显示。关闭窗口或等待 60 秒结束。")

    msg = wintypes.MSG()
    user32 = ctypes.windll.user32
    start = time.time()
    running = True
    did_expand = False
    did_check = False
    did_key = False
    while running and time.time() - start < 60:
        elapsed = time.time() - start
        if not did_expand and elapsed > 1.0:
            on_click(g_expand_id)
            did_expand = True
        if not did_check and elapsed > 2.0:
            on_click(g_check_id)
            did_check = True
        if not did_key and elapsed > 3.0:
            user32.PostMessageW(hwnd, 0x0100, 0x28, 0)
            user32.PostMessageW(hwnd, 0x0100, 0x20, 0)
            did_key = True

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

    final_options = ui.get_tree_options(hwnd, g_tree_id)
    final_json = ui.get_tree_state_json(hwnd, g_json_tree_id)
    print(
        "[结果] "
        f"选中={ui.get_tree_selected(hwnd, g_tree_id)} "
        f"已勾选={final_options['checked_count']} "
        f"最后懒加载={final_options['last_lazy_index']}"
    )
    print(f"[JSON结果] {final_json}")
    print("树组件完整验证结束。")


if __name__ == "__main__":
    main()
