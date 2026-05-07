# Chrome Theme Token

Chrome 外壳主题通过 token 设置颜色，旧 `EU_SetThemeColor` 保持兼容，新接口为：

```text
EU_SetChromeThemePreset(hwnd, preset)
EU_SetThemeToken(hwnd, token_bytes, token_len, color)
EU_GetThemeToken(hwnd, token_bytes, token_len, color*)
EU_SetHighContrastMode(hwnd, enabled)
EU_SetIncognitoMode(hwnd, enabled)
```

预设：`0=ChromeLight`，`1=ChromeDark`，`2=ChromeIncognito`，`3=ChromeHighContrast`。

主要 token：

```text
chrome.frame_bg
chrome.toolbar_bg
chrome.tab_active_bg
chrome.tab_inactive_bg
chrome.omnibox_bg
chrome.omnibox_focus_border
chrome.icon_button_fg
chrome.icon_button_hover_bg
chrome.menu_bg
chrome.popover_bg
chrome.viewport_bg
```

完整列表以 `src/theme.cpp` 的 token 映射为准。
