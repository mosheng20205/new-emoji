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
void reset_window_theme(HWND hwnd);
