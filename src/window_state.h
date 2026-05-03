#pragma once
#include <windows.h>
#include <d2d1.h>
#include <map>
#include "element_types.h"
#include "theme.h"

class ElementTree;

struct WindowState {
    HWND hwnd = nullptr;
    ID2D1HwndRenderTarget* render_target = nullptr;
    ElementTree* element_tree = nullptr;
    Color titlebar_color = 0;
    bool dark_mode = true;
    int theme_mode = THEME_MODE_DARK;
    Theme custom_theme;
    bool has_custom_theme = false;
    bool in_live_resize = false;
    float dpi_scale = 1.0f;
    float last_dpi = 96.0f;
    bool  pm_aware = false;      // true if WM_DPICHANGED will fire

    // Manual resize tracking (for WS_POPUP without WS_THICKFRAME)
    bool sizing = false;
    int  size_dir = 0;           // HTLEFT, HTRIGHT, etc.
    POINT size_start = {0, 0};  // mouse pos at start
    RECT  size_rect = {0};      // window rect at start

    WindowResizeCallback resize_cb = nullptr;
    WindowCloseCallback close_cb = nullptr;
};

extern std::map<HWND, WindowState*> g_windows;

WindowState* window_state(HWND hwnd);
void register_window_class();
void recreate_render_target(WindowState* st);
