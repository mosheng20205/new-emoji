import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "examples", "python")))
import new_emoji_ui as ui


def assert_state(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    hwnd = ui.create_window("主题 token 验证 🎨", 220, 120, 520, 320)
    assert_state(hwnd, "窗口创建失败")

    ui.set_chrome_theme_preset(hwnd, 0)
    light_bg = ui.get_theme_token(hwnd, "chrome.toolbar_bg")
    assert_state(light_bg is not None, "亮色主题 token 读回失败")

    ui.set_chrome_theme_preset(hwnd, 1)
    dark_bg = ui.get_theme_token(hwnd, "chrome.toolbar_bg")
    assert_state(dark_bg is not None and dark_bg != light_bg, "暗色主题 token 未变化")

    ui.set_incognito_mode(hwnd, True)
    incognito_bg = ui.get_theme_token(hwnd, "chrome.frame_bg")
    assert_state(incognito_bg is not None, "隐身主题 token 读回失败")

    ui.set_theme_token(hwnd, "chrome.icon_button_hover_bg", 0x3300AAFF)
    assert_state(ui.get_theme_token(hwnd, "chrome.icon_button_hover_bg") == 0x3300AAFF, "自定义 token 读回失败")

    ui.set_high_contrast_mode(hwnd, True)
    assert_state(ui.get_theme_token(hwnd, "chrome.omnibox_border") is not None, "高对比 token 读回失败")

    ui.dll.EU_DestroyWindow(hwnd)
    print("Chrome 主题 token 验证通过")


if __name__ == "__main__":
    main()
