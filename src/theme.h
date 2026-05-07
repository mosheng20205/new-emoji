#pragma once
#include "element_types.h"
#include <string>
#include <memory>
#include <vector>

struct Theme {
    Color panel_bg        = 0xFF1E1E2E;  // dark base
    Color panel_bg_light  = 0xFFF5F5F5;  // light base
    Color button_bg       = 0xFF45475A;
    Color button_hover    = 0xFF585B70;
    Color button_press    = 0xFF313244;
    Color edit_bg         = 0xFF313244;
    Color edit_border     = 0xFF585B70;
    Color edit_focus      = 0xFF89B4FA;
    Color text_primary    = 0xFFCDD6F4;
    Color text_secondary  = 0xFFA6ADC8;
    Color text_muted      = 0xFF6C7086;
    Color titlebar_bg     = 0xFF181825;
    Color titlebar_text   = 0xFFCDD6F4;
    Color border_default  = 0xFF45475A;
    Color accent          = 0xFF89B4FA;   // Catppuccin blue

    Color chrome_frame_bg = 0xFFEAF0F9;
    Color chrome_frame_fg = 0xFF202124;
    Color chrome_toolbar_bg = 0xFFF8FAFD;
    Color chrome_toolbar_fg = 0xFF202124;
    Color chrome_toolbar_separator = 0xFFE0E3E7;
    Color chrome_tab_active_bg = 0xFFFFFFFF;
    Color chrome_tab_active_fg = 0xFF202124;
    Color chrome_tab_inactive_bg = 0xFFEAF0F9;
    Color chrome_tab_inactive_fg = 0xFF3C4043;
    Color chrome_tab_hover_bg = 0xFFF2F5FA;
    Color chrome_tab_border = 0xFFDADCE0;
    Color chrome_tab_loading_color = 0xFF1A73E8;
    Color chrome_tab_alert_color = 0xFFD93025;
    Color chrome_omnibox_bg = 0xFFEFF3F8;
    Color chrome_omnibox_fg = 0xFF202124;
    Color chrome_omnibox_placeholder = 0xFF5F6368;
    Color chrome_omnibox_focus_bg = 0xFFFFFFFF;
    Color chrome_omnibox_border = 0x00000000;
    Color chrome_omnibox_focus_border = 0xFF1A73E8;
    Color chrome_omnibox_chip_bg = 0xFFE8F0FE;
    Color chrome_omnibox_chip_fg = 0xFF1967D2;
    Color chrome_icon_button_fg = 0xFF5F6368;
    Color chrome_icon_button_hover_bg = 0x1A000000;
    Color chrome_icon_button_pressed_bg = 0x26000000;
    Color chrome_icon_button_checked_bg = 0x22000000;
    Color chrome_menu_bg = 0xFFFFFFFF;
    Color chrome_menu_fg = 0xFF202124;
    Color chrome_menu_secondary_fg = 0xFF5F6368;
    Color chrome_menu_hover_bg = 0xFFF1F3F4;
    Color chrome_menu_separator = 0xFFE0E0E0;
    Color chrome_popover_bg = 0xFFFFFFFF;
    Color chrome_popover_border = 0xFFDADCE0;
    Color chrome_popover_shadow = 0x33000000;
    Color chrome_viewport_bg = 0xFFFFFFFF;
    Color chrome_viewport_fg = 0xFF202124;
};

/** Current theme pointer — global for now, per-window later. */
extern Theme g_light_theme;
extern Theme g_dark_theme;
extern Theme* g_cur_theme;

enum ThemeMode {
    THEME_MODE_LIGHT = 0,
    THEME_MODE_DARK = 1,
    THEME_MODE_SYSTEM = 2
};

void init_themes();
void set_dark_mode(bool dark);
const Theme* theme_for_window(HWND hwnd);
bool is_dark_theme_for_window(HWND hwnd);
int get_window_theme_mode(HWND hwnd);
void set_window_theme_mode(HWND hwnd, int mode);
bool set_window_theme_color(HWND hwnd, const std::string& token, Color value);
bool get_window_theme_color(HWND hwnd, const std::string& token, Color* value);
void set_window_chrome_preset(HWND hwnd, int preset);
void set_window_high_contrast_mode(HWND hwnd, bool enabled);
void set_window_incognito_mode(HWND hwnd, bool enabled);
void reset_window_theme(HWND hwnd);
