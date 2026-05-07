#include "theme.h"
#include "window_state.h"
#include <windows.h>

Theme g_light_theme;
Theme g_dark_theme;
Theme* g_cur_theme = &g_dark_theme;

static bool g_themes_initialized = false;

static int normalize_theme_mode(int mode) {
    if (mode == THEME_MODE_LIGHT || mode == THEME_MODE_DARK || mode == THEME_MODE_SYSTEM) {
        return mode;
    }
    return THEME_MODE_DARK;
}

static bool system_prefers_dark_theme() {
    DWORD value = 1;
    DWORD size = sizeof(value);
    LSTATUS status = RegGetValueW(
        HKEY_CURRENT_USER,
        L"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
        L"AppsUseLightTheme",
        RRF_RT_REG_DWORD,
        nullptr,
        &value,
        &size);
    return status == ERROR_SUCCESS ? value == 0 : false;
}

static bool resolve_dark_from_mode(int mode) {
    mode = normalize_theme_mode(mode);
    if (mode == THEME_MODE_SYSTEM) return system_prefers_dark_theme();
    return mode == THEME_MODE_DARK;
}

static Color* theme_token_ptr(Theme& theme, const std::string& token) {
    if (token == "panel_bg") return &theme.panel_bg;
    if (token == "panel_bg_light") return &theme.panel_bg_light;
    if (token == "button_bg") return &theme.button_bg;
    if (token == "button_hover") return &theme.button_hover;
    if (token == "button_press") return &theme.button_press;
    if (token == "edit_bg") return &theme.edit_bg;
    if (token == "edit_border") return &theme.edit_border;
    if (token == "edit_focus") return &theme.edit_focus;
    if (token == "text_primary") return &theme.text_primary;
    if (token == "text_secondary") return &theme.text_secondary;
    if (token == "text_muted") return &theme.text_muted;
    if (token == "titlebar_bg") return &theme.titlebar_bg;
    if (token == "titlebar_text") return &theme.titlebar_text;
    if (token == "border_default") return &theme.border_default;
    if (token == "accent") return &theme.accent;
    if (token == "chrome.frame_bg") return &theme.chrome_frame_bg;
    if (token == "chrome.frame_fg") return &theme.chrome_frame_fg;
    if (token == "chrome.toolbar_bg") return &theme.chrome_toolbar_bg;
    if (token == "chrome.toolbar_fg") return &theme.chrome_toolbar_fg;
    if (token == "chrome.toolbar_separator") return &theme.chrome_toolbar_separator;
    if (token == "chrome.tab_active_bg") return &theme.chrome_tab_active_bg;
    if (token == "chrome.tab_active_fg") return &theme.chrome_tab_active_fg;
    if (token == "chrome.tab_inactive_bg") return &theme.chrome_tab_inactive_bg;
    if (token == "chrome.tab_inactive_fg") return &theme.chrome_tab_inactive_fg;
    if (token == "chrome.tab_hover_bg") return &theme.chrome_tab_hover_bg;
    if (token == "chrome.tab_border") return &theme.chrome_tab_border;
    if (token == "chrome.tab_loading_color") return &theme.chrome_tab_loading_color;
    if (token == "chrome.tab_alert_color") return &theme.chrome_tab_alert_color;
    if (token == "chrome.omnibox_bg") return &theme.chrome_omnibox_bg;
    if (token == "chrome.omnibox_fg") return &theme.chrome_omnibox_fg;
    if (token == "chrome.omnibox_placeholder") return &theme.chrome_omnibox_placeholder;
    if (token == "chrome.omnibox_focus_bg") return &theme.chrome_omnibox_focus_bg;
    if (token == "chrome.omnibox_border") return &theme.chrome_omnibox_border;
    if (token == "chrome.omnibox_focus_border") return &theme.chrome_omnibox_focus_border;
    if (token == "chrome.omnibox_chip_bg") return &theme.chrome_omnibox_chip_bg;
    if (token == "chrome.omnibox_chip_fg") return &theme.chrome_omnibox_chip_fg;
    if (token == "chrome.icon_button_fg") return &theme.chrome_icon_button_fg;
    if (token == "chrome.icon_button_hover_bg") return &theme.chrome_icon_button_hover_bg;
    if (token == "chrome.icon_button_pressed_bg") return &theme.chrome_icon_button_pressed_bg;
    if (token == "chrome.icon_button_checked_bg") return &theme.chrome_icon_button_checked_bg;
    if (token == "chrome.menu_bg") return &theme.chrome_menu_bg;
    if (token == "chrome.menu_fg") return &theme.chrome_menu_fg;
    if (token == "chrome.menu_secondary_fg") return &theme.chrome_menu_secondary_fg;
    if (token == "chrome.menu_hover_bg") return &theme.chrome_menu_hover_bg;
    if (token == "chrome.menu_separator") return &theme.chrome_menu_separator;
    if (token == "chrome.popover_bg") return &theme.chrome_popover_bg;
    if (token == "chrome.popover_border") return &theme.chrome_popover_border;
    if (token == "chrome.popover_shadow") return &theme.chrome_popover_shadow;
    if (token == "chrome.viewport_bg") return &theme.chrome_viewport_bg;
    if (token == "chrome.viewport_fg") return &theme.chrome_viewport_fg;
    return nullptr;
}

static bool set_theme_token(Theme& theme, const std::string& token, Color value) {
    Color* ptr = theme_token_ptr(theme, token);
    if (!ptr) return false;
    *ptr = value;
    return true;
}

static bool get_theme_token(Theme& theme, const std::string& token, Color* value) {
    Color* ptr = theme_token_ptr(theme, token);
    if (!ptr || !value) return false;
    *value = *ptr;
    return true;
}

static void apply_chrome_light(Theme& theme) {
    theme.chrome_frame_bg = 0xFFEAF0F9;
    theme.chrome_frame_fg = 0xFF202124;
    theme.chrome_toolbar_bg = 0xFFF8FAFD;
    theme.chrome_toolbar_fg = 0xFF202124;
    theme.chrome_toolbar_separator = 0xFFE0E3E7;
    theme.chrome_tab_active_bg = 0xFFFFFFFF;
    theme.chrome_tab_active_fg = 0xFF202124;
    theme.chrome_tab_inactive_bg = 0xFFEAF0F9;
    theme.chrome_tab_inactive_fg = 0xFF3C4043;
    theme.chrome_tab_hover_bg = 0xFFF2F5FA;
    theme.chrome_tab_border = 0xFFDADCE0;
    theme.chrome_tab_loading_color = 0xFF1A73E8;
    theme.chrome_tab_alert_color = 0xFFD93025;
    theme.chrome_omnibox_bg = 0xFFEFF3F8;
    theme.chrome_omnibox_fg = 0xFF202124;
    theme.chrome_omnibox_placeholder = 0xFF5F6368;
    theme.chrome_omnibox_focus_bg = 0xFFFFFFFF;
    theme.chrome_omnibox_border = 0x00000000;
    theme.chrome_omnibox_focus_border = 0xFF1A73E8;
    theme.chrome_omnibox_chip_bg = 0xFFE8F0FE;
    theme.chrome_omnibox_chip_fg = 0xFF1967D2;
    theme.chrome_icon_button_fg = 0xFF5F6368;
    theme.chrome_icon_button_hover_bg = 0x1A000000;
    theme.chrome_icon_button_pressed_bg = 0x26000000;
    theme.chrome_icon_button_checked_bg = 0x22000000;
    theme.chrome_menu_bg = 0xFFFFFFFF;
    theme.chrome_menu_fg = 0xFF202124;
    theme.chrome_menu_secondary_fg = 0xFF5F6368;
    theme.chrome_menu_hover_bg = 0xFFF1F3F4;
    theme.chrome_menu_separator = 0xFFE0E0E0;
    theme.chrome_popover_bg = 0xFFFFFFFF;
    theme.chrome_popover_border = 0xFFDADCE0;
    theme.chrome_popover_shadow = 0x33000000;
    theme.chrome_viewport_bg = 0xFFFFFFFF;
    theme.chrome_viewport_fg = 0xFF202124;
}

static void apply_chrome_dark(Theme& theme) {
    theme.chrome_frame_bg = 0xFF202124;
    theme.chrome_frame_fg = 0xFFE8EAED;
    theme.chrome_toolbar_bg = 0xFF292A2D;
    theme.chrome_toolbar_fg = 0xFFE8EAED;
    theme.chrome_toolbar_separator = 0xFF3C4043;
    theme.chrome_tab_active_bg = 0xFF292A2D;
    theme.chrome_tab_active_fg = 0xFFE8EAED;
    theme.chrome_tab_inactive_bg = 0xFF202124;
    theme.chrome_tab_inactive_fg = 0xFFBDC1C6;
    theme.chrome_tab_hover_bg = 0xFF303134;
    theme.chrome_tab_border = 0xFF3C4043;
    theme.chrome_tab_loading_color = 0xFF8AB4F8;
    theme.chrome_tab_alert_color = 0xFFF28B82;
    theme.chrome_omnibox_bg = 0xFF202124;
    theme.chrome_omnibox_fg = 0xFFE8EAED;
    theme.chrome_omnibox_placeholder = 0xFFBDC1C6;
    theme.chrome_omnibox_focus_bg = 0xFF303134;
    theme.chrome_omnibox_border = 0x00000000;
    theme.chrome_omnibox_focus_border = 0xFF8AB4F8;
    theme.chrome_omnibox_chip_bg = 0xFF303134;
    theme.chrome_omnibox_chip_fg = 0xFF8AB4F8;
    theme.chrome_icon_button_fg = 0xFFBDC1C6;
    theme.chrome_icon_button_hover_bg = 0x26FFFFFF;
    theme.chrome_icon_button_pressed_bg = 0x33FFFFFF;
    theme.chrome_icon_button_checked_bg = 0x30FFFFFF;
    theme.chrome_menu_bg = 0xFF303134;
    theme.chrome_menu_fg = 0xFFE8EAED;
    theme.chrome_menu_secondary_fg = 0xFFBDC1C6;
    theme.chrome_menu_hover_bg = 0xFF3C4043;
    theme.chrome_menu_separator = 0xFF5F6368;
    theme.chrome_popover_bg = 0xFF303134;
    theme.chrome_popover_border = 0xFF5F6368;
    theme.chrome_popover_shadow = 0x66000000;
    theme.chrome_viewport_bg = 0xFF202124;
    theme.chrome_viewport_fg = 0xFFE8EAED;
}

static void apply_chrome_incognito(Theme& theme) {
    apply_chrome_dark(theme);
    theme.chrome_frame_bg = 0xFF2B213A;
    theme.chrome_toolbar_bg = 0xFF332940;
    theme.chrome_tab_active_bg = 0xFF332940;
    theme.chrome_tab_inactive_bg = 0xFF2B213A;
    theme.chrome_omnibox_focus_border = 0xFFD7AEFB;
    theme.accent = 0xFFD7AEFB;
}

static void apply_chrome_high_contrast(Theme& theme) {
    theme.chrome_frame_bg = 0xFF000000;
    theme.chrome_frame_fg = 0xFFFFFFFF;
    theme.chrome_toolbar_bg = 0xFF000000;
    theme.chrome_toolbar_fg = 0xFFFFFFFF;
    theme.chrome_toolbar_separator = 0xFFFFFFFF;
    theme.chrome_tab_active_bg = 0xFF000000;
    theme.chrome_tab_active_fg = 0xFFFFFFFF;
    theme.chrome_tab_inactive_bg = 0xFF000000;
    theme.chrome_tab_inactive_fg = 0xFFFFFFFF;
    theme.chrome_tab_hover_bg = 0xFF1A1A1A;
    theme.chrome_tab_border = 0xFFFFFFFF;
    theme.chrome_omnibox_bg = 0xFF000000;
    theme.chrome_omnibox_fg = 0xFFFFFFFF;
    theme.chrome_omnibox_placeholder = 0xFFFFFFFF;
    theme.chrome_omnibox_focus_bg = 0xFF000000;
    theme.chrome_omnibox_border = 0xFFFFFFFF;
    theme.chrome_omnibox_focus_border = 0xFFFFFF00;
    theme.chrome_icon_button_fg = 0xFFFFFFFF;
    theme.chrome_icon_button_hover_bg = 0x33FFFFFF;
    theme.chrome_menu_bg = 0xFF000000;
    theme.chrome_menu_fg = 0xFFFFFFFF;
    theme.chrome_menu_secondary_fg = 0xFFFFFFFF;
    theme.chrome_menu_hover_bg = 0xFF1A1A1A;
    theme.chrome_popover_bg = 0xFF000000;
    theme.chrome_popover_border = 0xFFFFFFFF;
    theme.chrome_viewport_bg = 0xFF000000;
    theme.chrome_viewport_fg = 0xFFFFFFFF;
    theme.accent = 0xFFFFFF00;
}

void init_themes() {
    if (g_themes_initialized) return;
    g_themes_initialized = true;

    // Light theme — Catppuccin Latte
    g_light_theme.panel_bg       = 0xFFEFF1F5;
    g_light_theme.panel_bg_light = 0xFFF5F5F5;
    g_light_theme.button_bg      = 0xFFCCD0DA;
    g_light_theme.button_hover   = 0xFFBCC0CC;
    g_light_theme.button_press   = 0xFFACB0BE;
    g_light_theme.edit_bg        = 0xFFE6E9EF;
    g_light_theme.edit_border    = 0xFFBCC0CC;
    g_light_theme.edit_focus     = 0xFF1E66F5;
    g_light_theme.text_primary   = 0xFF4C4F69;
    g_light_theme.text_secondary = 0xFF5C5F77;
    g_light_theme.text_muted     = 0xFF8C8FA1;
    g_light_theme.titlebar_bg    = 0xFFDCE0E8;
    g_light_theme.titlebar_text  = 0xFF4C4F69;
    g_light_theme.border_default = 0xFFBCC0CC;
    g_light_theme.accent         = 0xFF1E66F5;
    apply_chrome_light(g_light_theme);

    // Dark theme — Catppuccin Mocha
    g_dark_theme.panel_bg       = 0xFF1E1E2E;
    g_dark_theme.panel_bg_light = 0xFFF5F5F5;  // not used in dark
    g_dark_theme.button_bg      = 0xFF45475A;
    g_dark_theme.button_hover   = 0xFF585B70;
    g_dark_theme.button_press   = 0xFF313244;
    g_dark_theme.edit_bg        = 0xFF313244;
    g_dark_theme.edit_border    = 0xFF585B70;
    g_dark_theme.edit_focus     = 0xFF89B4FA;
    g_dark_theme.text_primary   = 0xFFCDD6F4;
    g_dark_theme.text_secondary = 0xFFA6ADC8;
    g_dark_theme.text_muted     = 0xFF6C7086;
    g_dark_theme.titlebar_bg    = 0xFF181825;
    g_dark_theme.titlebar_text  = 0xFFCDD6F4;
    g_dark_theme.border_default = 0xFF45475A;
    g_dark_theme.accent         = 0xFF89B4FA;
    apply_chrome_dark(g_dark_theme);
}

void set_dark_mode(bool dark) {
    g_cur_theme = dark ? &g_dark_theme : &g_light_theme;
}

const Theme* theme_for_window(HWND hwnd) {
    init_themes();
    WindowState* st = window_state(hwnd);
    if (!st) return g_cur_theme ? g_cur_theme : &g_dark_theme;
    if (st->has_custom_theme) return &st->custom_theme;
    return resolve_dark_from_mode(st->theme_mode) ? &g_dark_theme : &g_light_theme;
}

bool is_dark_theme_for_window(HWND hwnd) {
    WindowState* st = window_state(hwnd);
    if (!st) return g_cur_theme == &g_dark_theme;
    return resolve_dark_from_mode(st->theme_mode);
}

int get_window_theme_mode(HWND hwnd) {
    WindowState* st = window_state(hwnd);
    return st ? normalize_theme_mode(st->theme_mode) : THEME_MODE_DARK;
}

void set_window_theme_mode(HWND hwnd, int mode) {
    WindowState* st = window_state(hwnd);
    if (!st) return;
    st->theme_mode = normalize_theme_mode(mode);
    st->dark_mode = resolve_dark_from_mode(st->theme_mode);
    set_dark_mode(st->dark_mode);
}

bool set_window_theme_color(HWND hwnd, const std::string& token, Color value) {
    WindowState* st = window_state(hwnd);
    if (!st) return false;
    if (!st->has_custom_theme) {
        st->custom_theme = *theme_for_window(hwnd);
        st->has_custom_theme = true;
    }
    return set_theme_token(st->custom_theme, token, value);
}

bool get_window_theme_color(HWND hwnd, const std::string& token, Color* value) {
    WindowState* st = window_state(hwnd);
    if (!st || !value) return false;
    Theme theme = *theme_for_window(hwnd);
    return get_theme_token(theme, token, value);
}

void set_window_chrome_preset(HWND hwnd, int preset) {
    WindowState* st = window_state(hwnd);
    if (!st) return;
    st->custom_theme = *theme_for_window(hwnd);
    st->has_custom_theme = true;
    if (preset == 0) apply_chrome_light(st->custom_theme);
    else if (preset == 2) apply_chrome_incognito(st->custom_theme);
    else if (preset == 3) apply_chrome_high_contrast(st->custom_theme);
    else apply_chrome_dark(st->custom_theme);
}

void set_window_high_contrast_mode(HWND hwnd, bool enabled) {
    if (enabled) set_window_chrome_preset(hwnd, 3);
    else reset_window_theme(hwnd);
}

void set_window_incognito_mode(HWND hwnd, bool enabled) {
    if (enabled) set_window_chrome_preset(hwnd, 2);
    else reset_window_theme(hwnd);
}

void reset_window_theme(HWND hwnd) {
    WindowState* st = window_state(hwnd);
    if (!st) return;
    st->has_custom_theme = false;
}
