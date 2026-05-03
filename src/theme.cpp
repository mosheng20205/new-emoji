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

static bool set_theme_token(Theme& theme, const std::string& token, Color value) {
    if (token == "panel_bg") theme.panel_bg = value;
    else if (token == "panel_bg_light") theme.panel_bg_light = value;
    else if (token == "button_bg") theme.button_bg = value;
    else if (token == "button_hover") theme.button_hover = value;
    else if (token == "button_press") theme.button_press = value;
    else if (token == "edit_bg") theme.edit_bg = value;
    else if (token == "edit_border") theme.edit_border = value;
    else if (token == "edit_focus") theme.edit_focus = value;
    else if (token == "text_primary") theme.text_primary = value;
    else if (token == "text_secondary") theme.text_secondary = value;
    else if (token == "text_muted") theme.text_muted = value;
    else if (token == "titlebar_bg") theme.titlebar_bg = value;
    else if (token == "titlebar_text") theme.titlebar_text = value;
    else if (token == "border_default") theme.border_default = value;
    else if (token == "accent") theme.accent = value;
    else return false;
    return true;
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

void reset_window_theme(HWND hwnd) {
    WindowState* st = window_state(hwnd);
    if (!st) return;
    st->has_custom_theme = false;
}
