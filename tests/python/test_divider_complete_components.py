import ctypes
from ctypes import wintypes
import time

import test_new_emoji as ui


@ui.CloseCallback
def on_close(hwnd):
    print("[关闭] 分割线全样式验证窗口正在关闭")
    ui.dll.EU_DestroyWindow(hwnd)


def require(name, condition):
    if not condition:
        raise RuntimeError(f"分割线验证失败：{name}")


def main():
    hwnd = ui.create_window("➗ 分割线组件全样式验证", 240, 90, 920, 650)
    if not hwnd:
        print("错误：窗口创建失败")
        return

    ui.dll.EU_SetWindowCloseCallback(hwnd, on_close)
    content = ui.create_container(hwnd, 0, 0, 0, 880, 590)
    ui.create_text(hwnd, content, "➗ Divider 分割线全样式验证", 30, 24, 360, 34)
    ui.create_text(hwnd, content, "覆盖横线、文字位置、图标内容、竖向分隔、线型、颜色、线宽和间距。", 30, 58, 760, 28)

    plain = ui.create_divider(hwnd, content, "", 0, 1, 40, 104, 760, 28)
    ui.set_divider_options(hwnd, plain, 0, 1, 0xFFE4E7ED, 1.0, False, "")

    left = ui.create_divider(hwnd, content, "少年包青天", 0, 0, 40, 148, 760, 34)
    ui.set_divider_options(hwnd, left, 0, 0, 0xFF409EFF, 1.5, False, "少年包青天")
    ui.set_divider_content(hwnd, left, "⚖️", "少年包青天")
    ui.set_divider_spacing(hwnd, left, margin=18, gap=12)

    center_icon = ui.create_divider(hwnd, content, "", 0, 1, 40, 196, 760, 36)
    ui.set_divider_options(hwnd, center_icon, 0, 1, 0xFF67C23A, 2.0, False, "")
    ui.set_divider_content(hwnd, center_icon, "📱", "")
    ui.set_divider_spacing(hwnd, center_icon, margin=8, gap=18)

    right = ui.create_divider(hwnd, content, "阿里云", 0, 2, 40, 246, 760, 34)
    ui.set_divider_options(hwnd, right, 0, 2, 0xFFE6A23C, 1.5, False, "阿里云")
    ui.set_divider_content(hwnd, right, "☁️", "阿里云")

    ui.create_text(hwnd, content, "雨纷纷", 40, 314, 84, 30)
    v1 = ui.create_divider(hwnd, content, "", 1, 1, 132, 302, 24, 54)
    ui.set_divider_options(hwnd, v1, 1, 1, 0xFF909399, 1.0, False, "")
    ui.create_text(hwnd, content, "旧故里", 166, 314, 84, 30)
    v2 = ui.create_divider(hwnd, content, "", 1, 1, 258, 302, 24, 54)
    ui.set_divider_options(hwnd, v2, 1, 1, 0xFF909399, 1.0, False, "")
    ui.create_text(hwnd, content, "草木深", 292, 314, 84, 30)

    toolbar = ui.create_panel(hwnd, content, 420, 298, 380, 62)
    ui.set_panel_style(hwnd, toolbar, 0xFFF5F7FA, 0xFFD8DFEA, 1.0, 8.0, 8)
    ui.create_button(hwnd, toolbar, "📄", "新建", 14, 14, 86, 34)
    tv1 = ui.create_divider(hwnd, toolbar, "", 1, 1, 112, 12, 20, 38)
    ui.set_divider_options(hwnd, tv1, 1, 1, 0xFFC0C4CC, 1.0, False, "")
    ui.create_button(hwnd, toolbar, "💾", "保存", 144, 14, 86, 34)
    tv2 = ui.create_divider(hwnd, toolbar, "", 1, 1, 242, 12, 20, 38)
    ui.set_divider_options(hwnd, tv2, 1, 1, 0xFFC0C4CC, 1.0, False, "")
    ui.create_button(hwnd, toolbar, "🚀", "发布", 274, 14, 86, 34)

    styles = [
        ("实线", 0, 0xFF409EFF, 1.0, 392),
        ("虚线", 1, 0xFFE6A23C, 1.5, 436),
        ("点线", 2, 0xFF67C23A, 2.0, 480),
        ("双线", 3, 0xFFF56C6C, 1.2, 524),
    ]
    for label, style, color, width, y in styles:
        divider = ui.create_divider(hwnd, content, label, 0, 1, 40, y, 760, 34)
        ui.set_divider_options(hwnd, divider, 0, 1, color, width, False, label)
        ui.set_divider_line_style(hwnd, divider, style)
        ui.set_divider_content(hwnd, divider, "🎨", label)
        ui.set_divider_spacing(hwnd, divider, margin=24, gap=14)

    legacy = ui.create_divider(hwnd, content, "兼容虚线", 0, 1, 40, 568, 360, 28)
    ui.set_divider_options(hwnd, legacy, 0, 1, 0xFF909399, 1.0, True, "兼容虚线")

    require("旧 dashed API 映射为虚线", ui.get_divider_line_style(hwnd, legacy) == 1)
    require("图标内容读回", ui.get_divider_content(hwnd, center_icon) == ("📱", ""))
    require("线型读回", ui.get_divider_line_style(hwnd, right) == 0)
    require("间距读回", ui.get_divider_spacing(hwnd, left) == (18, 12))
    require("选项读回", ui.get_divider_options(hwnd, left)[:2] == (0, 0))

    print("[读回] 左侧分割线选项=", ui.get_divider_options(hwnd, left))
    print("[读回] 左侧分割线间距=", ui.get_divider_spacing(hwnd, left))
    print("[读回] 图标内容=", ui.get_divider_content(hwnd, center_icon))
    print("[读回] 兼容虚线线型=", ui.get_divider_line_style(hwnd, legacy))

    ui.dll.EU_ShowWindow(hwnd, 1)
    print("➗ 分割线全样式验证示例已显示。关闭窗口或等待 60 秒结束。")

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

    print("➗ 分割线全样式验证示例结束。")


if __name__ == "__main__":
    main()
