import time
from ctypes import wintypes

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    ui.dll.EU_DestroyWindow(hwnd)


def pump_messages(seconds=0.3):
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


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def require_equal(name, actual, expected):
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def require_bounds_inside(name, bounds, limit_w, limit_h, margin=20):
    require(bounds is not None, f"{name} 位置尺寸读回失败")
    x, y, w, h = bounds
    require(x >= 0 and y >= 0, f"{name} 坐标不应为负: {bounds}")
    require(x + w <= limit_w - margin, f"{name} 右侧首屏裁切风险: {bounds}")
    require(y + h <= limit_h - margin, f"{name} 底部首屏裁切风险: {bounds}")


def make_flow(hwnd, parent, x, y, w, h, direction=0, gap=0):
    cid = ui.create_container(hwnd, parent, x, y, w, h)
    require(cid > 0, "Container 创建失败")
    ui.set_panel_style(hwnd, cid, 0x00000000, 0x00000000, 0.0, 0.0, 0)
    ui.set_container_layout(hwnd, cid, True, direction, gap)
    return cid


def assert_region_defaults(hwnd, header, aside, main, footer):
    require_equal("Header 默认背景", ui.get_panel_style(hwnd, header)[0], 0xFFB3C0D1)
    require_equal("Aside 默认背景", ui.get_panel_style(hwnd, aside)[0], 0xFFD3DCE6)
    require_equal("Main 默认背景", ui.get_panel_style(hwnd, main)[0], 0xFFE9EEF3)
    require_equal("Footer 默认背景", ui.get_panel_style(hwnd, footer)[0], 0xFFB3C0D1)

    require_equal("Header 默认高度", ui.get_element_bounds(hwnd, header)[3], 60)
    require_equal("Aside 默认宽度", ui.get_element_bounds(hwnd, aside)[2], 200)
    require_equal("Footer 默认高度", ui.get_element_bounds(hwnd, footer)[3], 60)

    require_equal("Header 文本对齐", ui.get_container_region_text_options(hwnd, header), {"align": 1, "valign": 1, "role": 1})
    require_equal("Aside 文本对齐", ui.get_container_region_text_options(hwnd, aside), {"align": 1, "valign": 1, "role": 2})
    require_equal("Main 文本对齐", ui.get_container_region_text_options(hwnd, main), {"align": 1, "valign": 1, "role": 3})
    require_equal("Footer 文本对齐", ui.get_container_region_text_options(hwnd, footer), {"align": 1, "valign": 1, "role": 4})


def build_seven_layouts(hwnd, root):
    cases = []

    def add_case(title, x, y, w, h, builder, direction=0):
        cid = make_flow(hwnd, root, x, y, w, h, direction, 0)
        builder(cid)
        cases.append((title, cid, ui.get_element_bounds(hwnd, cid)))
        return cid

    add_case("顶栏+主区", 30, 340, 260, 150, lambda c: (
        ui.create_header(hwnd, c, "📌 顶栏", h=42),
        ui.create_main(hwnd, c, "📄 主要区域"),
    ))
    add_case("顶栏+主区+底栏", 310, 340, 260, 150, lambda c: (
        ui.create_header(hwnd, c, "📌 顶栏", h=36),
        ui.create_main(hwnd, c, "📄 主要区域"),
        ui.create_footer(hwnd, c, "✅ 底栏", h=34),
    ))
    add_case("侧栏+主区", 590, 340, 260, 150, lambda c: (
        ui.create_aside(hwnd, c, "🧭 侧栏", w=96),
        ui.create_main(hwnd, c, "📄 主要区域"),
    ))
    def header_aside_main(c):
        ui.create_header(hwnd, c, "📌 顶栏", h=34)
        body = make_flow(hwnd, c, 0, 0, 0, 0, 1)
        ui.create_aside(hwnd, body, "🧭 侧栏", w=92)
        ui.create_main(hwnd, body, "📄 主要区域")

    add_case("顶栏+侧栏+主区", 870, 340, 260, 150, header_aside_main)

    def header_aside_main_footer(c):
        ui.create_header(hwnd, c, "📌 顶栏", h=32)
        body = make_flow(hwnd, c, 0, 0, 0, 0, 1)
        ui.create_aside(hwnd, body, "🧭 侧栏", w=88)
        content = make_flow(hwnd, body, 0, 0, 0, 0, 2)
        ui.create_main(hwnd, content, "📄 主要区域")
        ui.create_footer(hwnd, content, "✅ 底栏", h=28)

    add_case("顶栏+侧栏+主区+底栏", 30, 520, 340, 160, header_aside_main_footer)

    def aside_header_main(c):
        ui.set_container_layout(hwnd, c, True, 1, 0)
        ui.create_aside(hwnd, c, "🧭 侧栏", w=92)
        content = make_flow(hwnd, c, 0, 0, 0, 0, 2)
        ui.create_header(hwnd, content, "📌 顶栏", h=34)
        ui.create_main(hwnd, content, "📄 主要区域")

    add_case("侧栏+顶栏+主区", 390, 520, 340, 160, aside_header_main, direction=1)

    def aside_header_main_footer(c):
        ui.set_container_layout(hwnd, c, True, 1, 0)
        ui.create_aside(hwnd, c, "🧭 侧栏", w=92)
        content = make_flow(hwnd, c, 0, 0, 0, 0, 2)
        ui.create_header(hwnd, content, "📌 顶栏", h=30)
        ui.create_main(hwnd, content, "📄 主要区域")
        ui.create_footer(hwnd, content, "✅ 底栏", h=28)

    add_case("侧栏+顶栏+主区+底栏", 750, 520, 380, 160, aside_header_main_footer, direction=1)
    return cases


def main():
    hwnd = ui.create_window("📦 Container 容器五件套完整验证", 160, 70, 1260, 820)
    require(hwnd, "窗口创建失败")
    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    root = ui.create_container(hwnd, 0, 0, 0, 1220, 760)
    ui.set_panel_style(hwnd, root, 0x00000000, 0x00000000, 0.0, 0.0, 0)

    suite = make_flow(hwnd, root, 30, 30, 560, 240, 0, 12)
    header = ui.create_header(hwnd, suite, "📌 顶栏")
    body = make_flow(hwnd, suite, 0, 0, 0, 0, 1, 0)
    aside = ui.create_aside(hwnd, body, "🧭 侧边栏")
    main_area = ui.create_main(hwnd, body, "📄 主要区域")
    footer = ui.create_footer(hwnd, suite, "✅ 底栏")
    assert_region_defaults(hwnd, header, aside, main_area, footer)

    ui.set_element_text(hwnd, main_area, "📄 主区文本已更新")
    require_equal("Main 文本读回", ui.get_element_text(hwnd, main_area), "📄 主区文本已更新")
    ui.set_container_region_text_options(hwnd, aside, 0, 2)
    require_equal("Aside 文本选项读回", ui.get_container_region_text_options(hwnd, aside), {"align": 0, "valign": 2, "role": 2})

    suite_layout = ui.get_container_layout(hwnd, suite)
    require_equal("Container 自动纵向", suite_layout, {"enabled": True, "direction": 0, "gap": 12, "actual_direction": 2})
    body_layout = ui.get_container_layout(hwnd, body)
    require_equal("Container 显式横向", body_layout, {"enabled": True, "direction": 1, "gap": 0, "actual_direction": 1})

    horizontal = make_flow(hwnd, root, 630, 30, 420, 120, 0, 0)
    ui.create_aside(hwnd, horizontal, "🧭 侧边栏", w=140)
    ui.create_main(hwnd, horizontal, "📄 主要区域")
    require_equal("自动方向无顶底栏时横向", ui.get_container_layout(hwnd, horizontal)["actual_direction"], 1)

    legacy = ui.create_container(hwnd, root, 630, 174, 420, 96)
    ui.create_header(hwnd, legacy, "📌 旧绝对定位顶栏", 24, 18, 240, 52)
    require_equal("旧 Container 未启用流式布局", ui.get_container_layout(hwnd, legacy), {"enabled": False, "direction": 0, "gap": 0, "actual_direction": 0})

    seven = build_seven_layouts(hwnd, root)
    for title, _cid, bounds in seven:
        require_bounds_inside(title, bounds, 1220, 760)

    ui.dll.EU_ShowWindow(hwnd, 1)
    pump_messages(0.4)
    print("[Container] 五件套创建、默认样式、文本读写、布局读回、七布局首屏边界和旧语义兼容验证成功。")
    ui.dll.EU_DestroyWindow(hwnd)


if __name__ == "__main__":
    main()
