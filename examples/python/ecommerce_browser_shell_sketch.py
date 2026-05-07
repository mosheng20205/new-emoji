# -*- coding: utf-8 -*-
import ctypes
import time
from ctypes import wintypes

import new_emoji_ui as ui


BASE_W, BASE_H = 1600, 900
LEFT_W = 350

DARK = {
    "bg": 0xFF0B0F14,
    "sidebar": 0xFF151B24,
    "panel": 0xFF1D2430,
    "panel2": 0xFF202938,
    "content": 0xFF090D12,
    "border": 0xFF303A49,
    "text": 0xFFE7EDF6,
    "muted": 0xFF9AA7B8,
    "menu_hover": 0xFF202A39,
    "table_a": 0xFF111923,
    "table_b": 0xFF20283A,
    "table_sel": 0xFF254E7A,
}

LIGHT = {
    "bg": 0xFFF3F6FA,
    "sidebar": 0xFFFFFFFF,
    "panel": 0xFFFFFFFF,
    "panel2": 0xFFEFF4FB,
    "content": 0xFFF8FAFC,
    "border": 0xFFD6DEE8,
    "text": 0xFF1F2937,
    "muted": 0xFF64748B,
    "menu_hover": 0xFFEAF2FF,
    "table_a": 0xFFFFFFFF,
    "table_b": 0xFFF2F6FC,
    "table_sel": 0xFFDCEBFF,
}

WHITE = 0xFFFFFFFF
BLACK = 0xFF0F172A

GROUPS = [
    {"key": "amazon", "icon": "📁", "label": "Amazon 店群", "prefix": "Am", "envs": [
        {"name": "美区-环境01", "icon": "🇺🇸", "domain": "https://www.baidu.com", "proxy": "直连", "score": "92分"},
        {"name": "美区-环境02", "icon": "🇺🇸", "domain": "https://www.taobao.com", "proxy": "US-Proxy-02", "score": "89分"},
        {"name": "Am-环境1", "icon": "🛒", "domain": "https://sellercentral.amazon.com", "proxy": "US-Proxy-01", "score": "95分"},
        {"name": "Am-环境2", "icon": "🛒", "domain": "https://www.amazon.com", "proxy": "US-Proxy-09", "score": "91分"},
        {"name": "Am-环境3", "icon": "🛒", "domain": "https://www.amazon.com", "proxy": "JP-Proxy-03", "score": "86分"},
    ]},
    {"key": "tiktok", "icon": "📁", "label": "TikTok 店群", "prefix": "Tk", "envs": []},
    {"key": "site", "icon": "📁", "label": "独立站", "prefix": "站点", "envs": []},
    {"key": "shopee", "icon": "📁", "label": "虾皮 店群", "prefix": "虾皮", "envs": []},
]

MODULES = [
    ("proxy", "🌍", "代理管理", "维护代理池，支持搜索、快速导入、编辑和测试入口。"),
    ("group", "📁", "分组管理", "管理店群、平台分组、环境归属和批量移动。"),
    ("fingerprint", "🧬", "指纹管理", "维护浏览器指纹模板、地区配置、设备画像和一致性检测。"),
    ("rpa", "🤖", "RPA自动化", "编排自动化流程，执行打开页面、点击、输入、采集和等待任务。"),
    ("plugin", "🧩", "插件中心", "管理浏览器插件、脚本扩展、启用范围和版本更新。"),
    ("team", "👥", "团队协作", "管理成员、角色、环境共享、操作审计和权限边界。"),
    ("settings", "⚙️", "系统设置", "配置主题、语言、数据目录、更新策略和安全选项。"),
    ("about", "ℹ️", "关于", "查看 new_emoji 开源项目信息、仓库地址和组件能力说明。"),
]

STATE = {
    "hwnd": 0,
    "root": 0,
    "theme": "dark",
    "current_page": "browser",
    "selected_group": "amazon",
    "selected_env": ("amazon", 0),
    "expanded_groups": set(g["key"] for g in GROUPS),
    "pending_delete_env": None,
    "env_counter": 1,
    "bounds": {},
    "panel_roles": {},
    "text_roles": {},
    "tables": [],
    "menu": 0,
    "more_menu": 0,
    "menu_index": {},
    "menu_reverse": {},
    "module_ids": {},
    "browser_ids": [],
    "proxy_ids": [],
    "popup_menus": [],
    "browser_env_text": 0,
    "browser_domain_text": 0,
    "sidebar_panel": 0,
    "bg_panel": 0,
}


def theme():
    return DARK if STATE["theme"] == "dark" else LIGHT


def bytes_text(ptr, length):
    if not ptr or length <= 0:
        return ""
    return bytes(ptr[:length]).decode("utf-8", errors="replace")


def remember(eid, x, y, w, h, role=None, text_role=None):
    if eid:
        STATE["bounds"][eid] = (x, y, w, h)
        if role:
            STATE["panel_roles"][eid] = role
        if text_role:
            STATE["text_roles"][eid] = text_role
    return eid


def set_bounds(eid, x, y, w, h):
    if eid:
        ui.dll.EU_SetElementBounds(STATE["hwnd"], eid, int(x), int(y), int(w), int(h))


def panel(hwnd, parent, x, y, w, h, role="panel", radius=6, border_role="border"):
    t = theme()
    bg = t.get(role, t["panel"])
    border = t.get(border_role, t["border"])
    eid = ui.create_panel(hwnd, parent, x, y, w, h, bg)
    ui.set_panel_style(hwnd, eid, bg=bg, border=border, border_width=1.0, radius=radius, padding=0)
    return remember(eid, x, y, w, h, role=role)


def label(hwnd, parent, value, x, y, w, h, role="text", align=0):
    t = theme()
    eid = ui.create_text(hwnd, parent, value, x, y, w, h)
    ui.set_element_color(hwnd, eid, 0x00000000, t[role])
    ui.set_text_options(hwnd, eid, align=align, valign=1, wrap=False, ellipsis=True)
    return remember(eid, x, y, w, h, text_role=role)


def button(hwnd, parent, emoji, value, x, y, w, h, variant=1, callback=None):
    eid = ui.create_button(hwnd, parent, emoji, value, x, y, w, h, variant=variant)
    remember(eid, x, y, w, h)
    if callback:
        ui.dll.EU_SetElementClickCallback(hwnd, eid, callback)
    return eid


def input_box(hwnd, parent, value, placeholder, x, y, w, h, prefix_icon=""):
    eid = ui.create_input(
        hwnd, parent, value=value, placeholder=placeholder,
        prefix_icon=prefix_icon, clearable=False, x=x, y=y, w=w, h=h
    )
    return remember(eid, x, y, w, h)


def link(hwnd, parent, value, href, x, y, w, h):
    eid = ui.create_link(
        hwnd, parent, value, x=x, y=y, w=w, h=h,
        type=0, underline=True, auto_open=True, visited=False,
        prefix_icon="🔗", href=href, target="_blank",
    )
    remember(eid, x, y, w, h, text_role="text")
    return eid


def apply_theme():
    hwnd = STATE["hwnd"]
    t = theme()
    ui.dll.EU_SetThemeMode(hwnd, 1 if STATE["theme"] == "dark" else 0)
    for eid, role in STATE["panel_roles"].items():
        bg = t.get(role, t["panel"])
        border = t["border"] if role not in ("bg",) else bg
        ui.set_panel_style(hwnd, eid, bg=bg, border=border, border_width=1.0, radius=6 if role not in ("bg",) else 0, padding=0)
        ui.set_element_color(hwnd, eid, bg, t["text"])
    for eid, role in STATE["text_roles"].items():
        ui.set_element_color(hwnd, eid, 0x00000000, t.get(role, t["text"]))
    if STATE["menu"]:
        ui.set_menu_colors(
            hwnd, STATE["menu"],
            bg=t["sidebar"], text_color=t["text"], active_text_color=t["text"],
            hover_bg=t["menu_hover"], disabled_text_color=t["muted"], border=t["sidebar"],
        )
    for popup_menu in STATE["popup_menus"]:
        ui.set_menu_colors(
            hwnd, popup_menu,
            bg=t["panel"], text_color=t["text"], active_text_color=t["text"],
            hover_bg=t["menu_hover"], disabled_text_color=t["muted"], border=t["border"],
        )
    for table, rows in STATE["tables"]:
        style_table_rows(hwnd, table, rows)


def style_table_rows(hwnd, table, rows, selected_row=0):
    t = theme()
    for row_index in range(len(rows)):
        bg = t["table_b"] if row_index % 2 else t["table_a"]
        if row_index == selected_row:
            bg = t["table_sel"]
        ui.set_table_row_style(hwnd, table, row_index, bg=bg, fg=t["text"], align=0, font_flags=0, font_size=0)


def tune_table(hwnd, table, columns, rows, selected_row=0):
    ui.set_table_columns_ex(hwnd, table, columns)
    ui.set_table_rows_ex(hwnd, table, rows, columns)
    ui.set_table_options(hwnd, table, striped=True, bordered=True, row_height=44, header_height=44, selectable=True)
    ui.set_table_viewport_options(hwnd, table, max_height=0, fixed_header=True, horizontal_scroll=False)
    ui.set_table_selection_mode(hwnd, table, 1)
    ui.set_table_selected_row(hwnd, table, selected_row)
    STATE["tables"].append((table, rows))
    style_table_rows(hwnd, table, rows, selected_row)


def group_by_key(key):
    return next((g for g in GROUPS if g["key"] == key), GROUPS[0])


def current_env():
    group_key, env_index = STATE["selected_env"]
    group = group_by_key(group_key)
    if 0 <= env_index < len(group["envs"]):
        return group, group["envs"][env_index]
    for g in GROUPS:
        if g["envs"]:
            STATE["selected_env"] = (g["key"], 0)
            STATE["selected_group"] = g["key"]
            return g, g["envs"][0]
    return GROUPS[0], None


def build_menu_items():
    items = ["🌐 环境切换"]
    index = 1
    menu_index = {}
    menu_reverse = {}
    group_indices = [0]
    for group in GROUPS:
        items.append(f"> {group['icon']} {group['label']}")
        menu_index[index] = ("group", group["key"], None)
        menu_reverse[("group", group["key"])] = index
        if group["key"] in STATE["expanded_groups"]:
            group_indices.append(index)
        index += 1
        for env_index, env in enumerate(group["envs"]):
            items.append(f">> {env.get('icon', '🌐')} {env['name']}")
            menu_index[index] = ("env", group["key"], env_index)
            menu_reverse[("env", group["key"], env_index)] = index
            index += 1
    for page, icon, title, _subtitle in MODULES:
        items.append(f"{icon} {title}")
        menu_index[index] = ("module", page, None)
        menu_reverse[("module", page)] = index
        index += 1
    STATE["menu_index"] = menu_index
    STATE["menu_reverse"] = menu_reverse
    return items, group_indices


def refresh_menu(active_index=None):
    items, group_indices = build_menu_items()
    if STATE["menu"]:
        ui.set_menu_items(STATE["hwnd"], STATE["menu"], items)
        apply_theme()
        if active_index is None:
            active_index = active_menu_index()
        ui.set_menu_active(STATE["hwnd"], STATE["menu"], active_index)
        ui.set_menu_expanded(STATE["hwnd"], STATE["menu"], group_indices)


def active_menu_index():
    if STATE["current_page"] == "browser":
        group_key, env_index = STATE["selected_env"]
        return STATE["menu_reverse"].get(("env", group_key, env_index), 0)
    return STATE["menu_reverse"].get(("module", STATE["current_page"]), 0)


def set_group_visible(ids, visible):
    for eid in ids:
        ui.set_element_visible(STATE["hwnd"], eid, visible)


def show_page(page):
    STATE["current_page"] = page
    if STATE["more_menu"]:
        ui.set_popup_open(STATE["hwnd"], STATE["more_menu"], False)
    set_group_visible(STATE["browser_ids"], page == "browser")
    set_group_visible(STATE["proxy_ids"], page == "proxy")
    for page_name, ids in STATE["module_ids"].items():
        set_group_visible(ids, page == page_name)
    refresh_menu()


def select_environment(group_key, env_index):
    group = group_by_key(group_key)
    if not (0 <= env_index < len(group["envs"])):
        return
    STATE["selected_group"] = group_key
    STATE["selected_env"] = (group_key, env_index)
    env = group["envs"][env_index]
    ui.set_element_text(
        STATE["hwnd"], STATE["browser_env_text"],
        f"当前环境：{env['name']}    分组：{group['label']}    状态：创建中    评分：{env['score']}"
    )
    ui.set_element_text(
        STATE["hwnd"], STATE["browser_domain_text"],
        f"域名：{env['domain']}    代理：{env['proxy']}"
    )
    show_page("browser")


@ui.MenuSelectCallback
def on_sidebar_select(element_id, index, path_ptr, path_len, command_ptr, command_len):
    entry = STATE["menu_index"].get(index)
    if not entry:
        return
    kind, key, extra = entry
    if kind == "group":
        STATE["selected_group"] = key
        STATE["selected_env"] = (key, -1)
        if key in STATE["expanded_groups"]:
            STATE["expanded_groups"].remove(key)
        else:
            STATE["expanded_groups"].add(key)
        refresh_menu(index)
    elif kind == "env":
        select_environment(key, extra)
    elif kind == "module":
        show_page(key)


@ui.MenuSelectCallback
def on_more_menu_select(element_id, index, path_ptr, path_len, command_ptr, command_len):
    if STATE["more_menu"]:
        ui.set_popup_open(STATE["hwnd"], STATE["more_menu"], False)


@ui.ClickCallback
def on_new_env(_element_id):
    group_key = STATE["selected_group"]
    if STATE["current_page"] == "browser" and STATE["selected_env"][1] >= 0:
        group_key = STATE["selected_env"][0]
    group = group_by_key(group_key)
    STATE["env_counter"] += 1
    name = f"{group['prefix']}-新环境{STATE['env_counter']:02d}"
    group["envs"].append({
        "name": name,
        "icon": "🆕",
        "domain": "https://example.com",
        "proxy": "待设置",
        "score": "80分",
    })
    STATE["expanded_groups"].add(group_key)
    select_environment(group_key, len(group["envs"]) - 1)


@ui.MessageBoxExCallback
def on_delete_confirm(_box_id, action, _value_ptr, _value_len):
    if action != 1 or not STATE["pending_delete_env"]:
        STATE["pending_delete_env"] = None
        return
    group_key, env_index = STATE["pending_delete_env"]
    STATE["pending_delete_env"] = None
    group = group_by_key(group_key)
    if 0 <= env_index < len(group["envs"]):
        del group["envs"][env_index]
    if group["envs"]:
        select_environment(group_key, max(0, min(env_index, len(group["envs"]) - 1)))
    else:
        STATE["selected_group"] = group_key
        STATE["selected_env"] = (group_key, -1)
        show_page("browser")


@ui.ClickCallback
def on_delete_env(_element_id):
    group_key, env_index = STATE["selected_env"]
    group = group_by_key(group_key)
    if not (0 <= env_index < len(group["envs"])):
        ui.show_alert_box(STATE["hwnd"], "提示", "请先选择一个要删除的环境。", "知道了")
        return
    env = group["envs"][env_index]
    STATE["pending_delete_env"] = (group_key, env_index)
    ui.show_confirm_box(
        STATE["hwnd"],
        "🗑️ 确认删除环境",
        f"确定要删除「{env['name']}」吗？此操作只影响草图菜单数据。",
        confirm="删除",
        cancel="取消",
        box_type=2,
        center=True,
        callback=on_delete_confirm,
    )


@ui.ClickCallback
def on_toggle_theme(_element_id):
    STATE["theme"] = "light" if STATE["theme"] == "dark" else "dark"
    apply_theme()


@ui.ResizeCallback
def on_resize(_hwnd, width, height):
    width = max(980, int(width))
    height = max(620, int(height))
    right_x = LEFT_W + 16
    for eid, (x, y, w, h) in STATE["bounds"].items():
        nx, ny, nw, nh = x, y, w, h

        if eid in (STATE["root"], STATE["bg_panel"]):
            nx, ny, nw, nh = 0, 0, width, height
        elif eid == STATE["sidebar_panel"]:
            nx, ny, nw, nh = 16, 16, LEFT_W - 32, max(120, height - 32)
        elif eid == STATE["menu"]:
            nx, ny, nw, nh = 30, 142, 304, max(120, height - 180)
        else:
            if x >= right_x:
                base_right_gap = BASE_W - (x + w)
                if base_right_gap in (16, 32, 34, 52):
                    nw = max(80, width - x - base_right_gap)

            base_bottom_gap = BASE_H - (y + h)
            if base_bottom_gap in (26, 32, 50, 138):
                nh = max(40, height - y - base_bottom_gap)

        set_bounds(eid, nx, ny, nw, nh)


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages():
    user32 = ctypes.windll.user32
    msg = wintypes.MSG()
    running = True
    while running:
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


def build_sidebar(hwnd, root):
    STATE["sidebar_panel"] = panel(hwnd, root, 16, 16, LEFT_W - 32, BASE_H - 32, "sidebar", 4, "sidebar")
    label(hwnd, root, "🌐 环境面板", 36, 34, 180, 34)
    button(hwnd, root, "➕", "新建环境", 36, 82, 112, 38, variant=1, callback=on_new_env)
    button(hwnd, root, "🗑️", "删除环境", 160, 82, 112, 38, variant=3, callback=on_delete_env)
    button(hwnd, root, "☀️", "", 286, 82, 42, 38, variant=2, callback=on_toggle_theme)
    items, group_indices = build_menu_items()
    menu = ui.create_menu(hwnd, root, items, active=active_menu_index(), orientation=1, x=30, y=142, w=304, h=720)
    remember(menu, 30, 142, 304, 720)
    STATE["menu"] = menu
    ui.set_menu_select_callback(hwnd, menu, on_sidebar_select)
    ui.set_menu_expanded(hwnd, menu, group_indices)


def build_browser_page(hwnd, root):
    ids = STATE["browser_ids"]
    x0 = LEFT_W + 16
    right_w = BASE_W - x0 - 16
    ids.append(panel(hwnd, root, x0, 16, right_w, 66, "panel", 0, "panel"))
    env_text = label(hwnd, root, "", x0 + 18, 28, 780, 22)
    domain_text = label(hwnd, root, "", x0 + 18, 52, 580, 22, "muted")
    STATE["browser_env_text"] = env_text
    STATE["browser_domain_text"] = domain_text
    ids.extend([env_text, domain_text])

    ids.append(panel(hwnd, root, x0, 94, right_w, 70, "panel", 0, "panel"))
    tx = x0 + 18
    more_button = 0
    for emoji, text_value, bw, variant in [
        ("🚀", "启动浏览器", 130, 1), ("⬅️", "后退", 88, 0), ("➡️", "前进", 88, 0),
        ("⏹️", "停止", 88, 2), ("🔄", "刷新", 88, 1), ("🖥️", "打开后台", 116, 5),
        ("🍪", "同步Cookie", 124, 4), ("🌐", "切换代理", 116, 5),
        ("⚙️", "更多操作", 116, 0), ("🛑", "关闭浏览器", 130, 3),
    ]:
        btn = button(hwnd, root, emoji, text_value, tx, 110, bw, 38, variant=variant)
        ids.append(btn)
        if text_value == "更多操作":
            more_button = btn
        tx += bw + 10
    ids.append(input_box(hwnd, root, "https://www.baidu.com/", "输入网址", x0 + 16, 182, right_w - 32, 38, "🔒"))

    browser_y = 238
    browser_h = BASE_H - browser_y - 26
    ids.append(panel(hwnd, root, x0, browser_y, right_w, browser_h, "content", 0, "border"))
    ids.append(label(hwnd, root, "浏览器宿主空白区", x0 + 20, browser_y + 18, 220, 28, "muted"))
    ids.append(label(hwnd, root, "后续可在这块区域放 WebView2 / CEF / 外部浏览器句柄", x0 + 20, browser_y + 48, 560, 24, "muted"))
    ids.append(panel(hwnd, root, x0 + 18, browser_y + 88, right_w - 36, browser_h - 112, "panel", 4, "border"))
    ids.append(label(hwnd, root, "🌐 空白浏览器画布", x0 + 40, browser_y + 110, 260, 30))
    ids.append(label(hwnd, root, "这里不绘制网页，只保留可嵌入区域。", x0 + 40, browser_y + 142, 380, 26, "muted"))
    if more_button:
        more_menu = ui.create_menu(
            hwnd, root,
            ["📝 编辑环境", "📋 复制环境", "🍪 Cookie 设置", "🧪 检测环境", "📤 导出配置"],
            active=0, orientation=1, x=-900, y=0, w=210, h=228,
        )
        remember(more_menu, -900, 0, 210, 228)
        ids.append(more_menu)
        STATE["more_menu"] = more_menu
        STATE["popup_menus"].append(more_menu)
        ui.set_menu_select_callback(hwnd, more_menu, on_more_menu_select)
        ui.set_popup_anchor_element(hwnd, more_menu, more_button)
        ui.set_popup_placement(hwnd, more_menu, placement=5, offset_x=0, offset_y=8)
        ui.set_popup_dismiss_behavior(hwnd, more_menu, close_on_outside=True, close_on_escape=True)
        ui.set_popup_open(hwnd, more_menu, False)
        ui.set_element_popup(hwnd, more_button, more_menu, "click")
    select_environment(*STATE["selected_env"])


def build_proxy_page(hwnd, root):
    ids = STATE["proxy_ids"]
    x0 = LEFT_W + 16
    right_w = BASE_W - x0 - 16
    ids.append(panel(hwnd, root, x0, 16, right_w, 66, "panel", 0, "panel"))
    ids.append(label(hwnd, root, "当前模块：代理管理", x0 + 18, 34, 360, 26))
    ids.append(label(hwnd, root, "维护代理池，支持搜索、快速导入、编辑和测试入口。", x0 + 18, 58, 760, 22, "muted"))
    ids.append(panel(hwnd, root, x0, 94, right_w, 70, "panel", 0, "panel"))
    ids.append(label(hwnd, root, "🌍 代理管理草图区", x0 + 28, 112, 260, 32))
    ids.append(label(hwnd, root, "点击左侧环境项可返回浏览器草图区。", x0 + 350, 116, 420, 24, "muted"))

    content_top = 188
    ids.append(panel(hwnd, root, x0, content_top, right_w, BASE_H - content_top - 26, "content", 0, "border"))
    ids.append(label(hwnd, root, "代理列表", x0 + 28, content_top + 30, 160, 28))
    ids.append(input_box(hwnd, root, "", "搜索代理", x0 + 28, content_top + 70, 420, 36, "🔍"))
    ids.append(button(hwnd, root, "🔎", "筛选", x0 + 462, content_top + 70, 92, 36, variant=5))
    ids.append(input_box(hwnd, root, "127.0.0.1:7890", "host:port:user:pass", x0 + 28, content_top + 118, 420, 36, "⚡"))
    ids.append(button(hwnd, root, "🧩", "解析", x0 + 462, content_top + 118, 92, 36, variant=5))

    columns = [
        {"title": "状态", "key": "status", "width": 96},
        {"title": "代理名称", "key": "name", "width": 188},
        {"title": "类型", "key": "type", "width": 98},
        {"title": "地址", "key": "addr", "width": 238},
    ]
    rows = [
        {"status": "在线", "name": "US-Proxy-01", "type": "HTTP", "addr": "127.0.0.1:7890"},
        {"status": "在线", "name": "US-Proxy-02", "type": "HTTP", "addr": "127.0.0.1:7891"},
        {"status": "认证", "name": "JP-Proxy-03", "type": "HTTP", "addr": "127.0.0.1:7892"},
        {"status": "待测", "name": "US-Proxy-09", "type": "SOCKS5", "addr": "127.0.0.1:1080"},
    ]
    table = ui.create_table(hwnd, root, ["状态", "代理名称", "类型", "地址"], [["", "", "", ""]],
                            True, True, x0 + 28, content_top + 176, 620, 330)
    remember(table, x0 + 28, content_top + 176, 620, 330)
    ids.append(table)
    tune_table(hwnd, table, columns, rows)

    form_x = x0 + 680
    ids.append(label(hwnd, root, "代理设置", form_x, content_top + 30, 180, 28))
    ids.append(input_box(hwnd, root, "US-Proxy-01", "代理名称", form_x, content_top + 70, 260, 36, "🏷️"))
    ids.append(ui.create_segmented(hwnd, root, ["HTTP", "SOCKS5"], active=0, x=form_x + 286, y=content_top + 70, w=220, h=36))
    remember(ids[-1], form_x + 286, content_top + 70, 220, 36)
    ids.append(input_box(hwnd, root, "127.0.0.1", "主机地址", form_x, content_top + 118, 260, 36, "🖧"))
    ids.append(input_box(hwnd, root, "7890", "端口", form_x + 286, content_top + 118, 170, 36, "🔌"))
    ids.append(input_box(hwnd, root, "", "用户名", form_x, content_top + 166, 260, 36, "👤"))
    ids.append(input_box(hwnd, root, "", "密码", form_x + 286, content_top + 166, 260, 36, "🔑"))
    ids.append(label(hwnd, root, "开源版支持 HTTP、HTTP 账号密码代理以及 SOCKS5。", form_x, content_top + 226, 620, 26, "muted"))
    for i, (emoji, text_value, variant) in enumerate([("💾", "保存修改", 1), ("➕", "新增代理", 2), ("🗑️", "删除代理", 3), ("🧪", "测试代理", 4)]):
        ids.append(button(hwnd, root, emoji, text_value, form_x + i * 132, content_top + 282, 118, 38, variant=variant))


def build_module_page(hwnd, root, page_name, icon, title, subtitle, cards, actions):
    ids = []
    STATE["module_ids"][page_name] = ids
    x0 = LEFT_W + 16
    right_w = BASE_W - x0 - 16
    content_top = 188
    ids.append(panel(hwnd, root, x0, 16, right_w, 66, "panel", 0, "panel"))
    ids.append(label(hwnd, root, f"当前模块：{title}", x0 + 18, 34, 360, 26))
    ids.append(label(hwnd, root, subtitle, x0 + 18, 58, 760, 22, "muted"))
    ids.append(panel(hwnd, root, x0, 94, right_w, 70, "panel", 0, "panel"))
    tx = x0 + 24
    for emoji, text_value, variant in actions:
        ids.append(button(hwnd, root, emoji, text_value, tx, 110, 128, 38, variant=variant))
        tx += 142
    ids.append(panel(hwnd, root, x0, content_top, right_w, BASE_H - content_top - 26, "content", 0, "border"))
    ids.append(label(hwnd, root, f"{icon} {title}", x0 + 28, content_top + 26, 300, 36))
    ids.append(label(hwnd, root, "此处是独立功能页，不显示浏览器宿主空白区。", x0 + 28, content_top + 62, 520, 24, "muted"))

    card_w, card_h = 360, 128
    start_x, start_y = x0 + 28, content_top + 116
    for i, (card_icon, card_title, card_desc) in enumerate(cards):
        cx = start_x + (i % 3) * (card_w + 22)
        cy = start_y + (i // 3) * (card_h + 22)
        ids.append(panel(hwnd, root, cx, cy, card_w, card_h, "panel", 6, "border"))
        ids.append(label(hwnd, root, f"{card_icon} {card_title}", cx + 20, cy + 18, card_w - 40, 30))
        ids.append(label(hwnd, root, card_desc, cx + 20, cy + 56, card_w - 40, 48, "muted"))

    table_y = start_y + 2 * (card_h + 22) + 18
    ids.append(label(hwnd, root, "最近记录", x0 + 28, table_y, 160, 28))
    table_w = right_w - 56
    columns = [
        {"title": "时间", "key": "time", "width": 120},
        {"title": "对象", "key": "target", "width": 440},
        {"title": "状态", "key": "state", "width": 150},
        {"title": "备注", "key": "note", "width": max(300, table_w - 710)},
    ]
    rows = [
        {"time": "09:20", "target": f"{title} 示例项 A", "state": "正常", "note": "已同步，可继续编辑"},
        {"time": "10:15", "target": f"{title} 示例项 B", "state": "待处理", "note": "等待补充配置"},
        {"time": "11:05", "target": f"{title} 示例项 C", "state": "完成", "note": "已生成模块记录"},
        {"time": "13:40", "target": f"{title} 示例项 D", "state": "检查中", "note": "正在验证当前设置"},
    ]
    table = ui.create_table(hwnd, root, ["时间", "对象", "状态", "备注"], [["", "", "", ""]],
                            True, True, x0 + 28, table_y + 40, table_w, 218)
    remember(table, x0 + 28, table_y + 40, table_w, 218)
    ids.append(table)
    tune_table(hwnd, table, columns, rows)


def build_feature_pages(hwnd, root):
    common_cards = [
        ("📦", "结构管理", "维护当前模块的数据结构和层级关系。"),
        ("🔁", "批量操作", "对多条记录执行移动、启用、停用或同步。"),
        ("🧾", "规则配置", "设置命名、排序、权限和默认策略。"),
        ("🔍", "快速筛选", "按平台、地区、状态快速定位数据。"),
        ("📊", "统计概览", "查看数量、启用率和异常数量。"),
        ("🧩", "模板复用", "复用常用配置模板，提高创建效率。"),
    ]
    for page, icon, title, subtitle in MODULES[1:-1]:
        build_module_page(
            hwnd, root, page, icon, title, subtitle, common_cards,
            [("➕", "新增项目", 1), ("📥", "导入数据", 5), ("🧹", "整理排序", 0)],
        )
    build_about_page(hwnd, root)


def build_about_page(hwnd, root):
    page_name = "about"
    ids = []
    STATE["module_ids"][page_name] = ids
    x0 = LEFT_W + 16
    right_w = BASE_W - x0 - 16
    content_top = 188
    repo_url = "https://github.com/mosheng20205/new-emoji"

    ids.append(panel(hwnd, root, x0, 16, right_w, 66, "panel", 0, "panel"))
    ids.append(label(hwnd, root, "当前模块：关于", x0 + 18, 34, 360, 26))
    ids.append(label(hwnd, root, "new_emoji 是一个单 HWND、纯 D2D 渲染的中文 emoji UI 组件库。", x0 + 18, 58, 760, 22, "muted"))

    ids.append(panel(hwnd, root, x0, 94, right_w, 70, "panel", 0, "panel"))
    ids.append(label(hwnd, root, "ℹ️ 开源项目信息", x0 + 28, 112, 240, 32))
    ids.append(label(hwnd, root, "点击仓库链接可打开 GitHub 项目页面。", x0 + 300, 116, 420, 24, "muted"))

    ids.append(panel(hwnd, root, x0, content_top, right_w, BASE_H - content_top - 26, "content", 0, "border"))
    ids.append(label(hwnd, root, "🌈 new_emoji", x0 + 40, content_top + 36, 320, 44))
    ids.append(label(hwnd, root, "一个面向易语言 / C# / Python 调用的 Windows 原生 DLL UI 库。", x0 + 40, content_top + 82, 720, 28, "muted"))
    ids.append(label(hwnd, root, "核心理念：单一 HWND + Direct2D / DirectWrite 纯自绘，减少传统 GDI 子窗口带来的闪烁问题。", x0 + 40, content_top + 122, 980, 28, "muted"))

    ids.append(panel(hwnd, root, x0 + 40, content_top + 178, right_w - 80, 126, "panel", 6, "border"))
    ids.append(label(hwnd, root, "📦 开源仓库", x0 + 64, content_top + 200, 180, 30))
    ids.append(label(hwnd, root, "GitHub 地址：", x0 + 64, content_top + 240, 120, 28, "muted"))
    ids.append(link(hwnd, root, repo_url, repo_url, x0 + 180, content_top + 240, 520, 28))

    cards = [
        ("🪟", "单 HWND 架构", "所有组件都是虚拟 Element，在同一个渲染周期中绘制。"),
        ("😀", "彩色 emoji 支持", "DirectWrite 配合彩色字体选项，适合中文和 emoji 界面。"),
        ("🧩", "组件化封装", "Panel、Button、Input、Table、Menu、Tabs 等组件可组合复杂业务界面。"),
        ("🌗", "主题能力", "支持深色、浅色以及 token 级别的颜色调整。"),
        ("📚", "多语言绑定", "提供 DLL 导出，便于易语言、C#、Python 等宿主调用。"),
        ("🛠️", "示例驱动", "通过 Python 示例快速验证组件组合和交互草图。"),
    ]
    card_w, card_h = 360, 116
    start_x, start_y = x0 + 40, content_top + 340
    for i, (card_icon, card_title, card_desc) in enumerate(cards):
        cx = start_x + (i % 3) * (card_w + 22)
        cy = start_y + (i // 3) * (card_h + 22)
        ids.append(panel(hwnd, root, cx, cy, card_w, card_h, "panel", 6, "border"))
        ids.append(label(hwnd, root, f"{card_icon} {card_title}", cx + 20, cy + 16, card_w - 40, 28))
        ids.append(label(hwnd, root, card_desc, cx + 20, cy + 52, card_w - 40, 46, "muted"))


def main():
    hwnd = ui.create_window_ex("🧳 电商多账号浏览器 - 草图", 120, 80, BASE_W, BASE_H, 0xFF111827)
    if not hwnd:
        print("窗口创建失败")
        return
    STATE["hwnd"] = hwnd
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    ui.dll.EU_SetWindowResizeCallback(hwnd, on_resize)
    ui.dll.EU_SetThemeMode(hwnd, 1)

    root = ui.create_container(hwnd, 0, 0, 0, BASE_W, BASE_H)
    STATE["root"] = remember(root, 0, 0, BASE_W, BASE_H)
    STATE["bg_panel"] = panel(hwnd, root, 0, 0, BASE_W, BASE_H, "bg", 0, "bg")
    build_sidebar(hwnd, root)
    build_browser_page(hwnd, root)
    build_proxy_page(hwnd, root)
    build_feature_pages(hwnd, root)
    apply_theme()
    show_page("browser")

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages()


if __name__ == "__main__":
    main()
