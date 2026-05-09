#pragma once
#include <windows.h>
#include <d2d1.h>
#include <map>
#include <vector>
#include "element_types.h"
#include "theme.h"

class ElementTree;

constexpr int EU_WINDOW_FRAME_DEFAULT = 0x0000;
constexpr int EU_WINDOW_FRAME_BORDERLESS = 0x0001;
constexpr int EU_WINDOW_FRAME_CUSTOM_CAPTION = 0x0002;
constexpr int EU_WINDOW_FRAME_CUSTOM_BUTTONS = 0x0004;
constexpr int EU_WINDOW_FRAME_RESIZABLE = 0x0008;
constexpr int EU_WINDOW_FRAME_ROUNDED = 0x0010;
constexpr int EU_WINDOW_FRAME_HIDE_TITLEBAR = 0x0020;
constexpr int EU_WINDOW_FRAME_BROWSER_SHELL =
    EU_WINDOW_FRAME_BORDERLESS |
    EU_WINDOW_FRAME_CUSTOM_CAPTION |
    EU_WINDOW_FRAME_CUSTOM_BUTTONS |
    EU_WINDOW_FRAME_RESIZABLE |
    EU_WINDOW_FRAME_ROUNDED |
    EU_WINDOW_FRAME_HIDE_TITLEBAR;

struct WindowCreateParams {
    Color titlebar_color = 0;
    int frame_flags = EU_WINDOW_FRAME_DEFAULT;
};

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
    bool titlebar_visible = true;
    int titlebar_logical_height = 30;
    int caption_button_x = -1;
    int caption_button_y = -1;
    int caption_button_w = 0;
    int caption_button_h = 0;
    int titlebar_button_w = 46;
    int titlebar_button_h = 30;
    Color titlebar_button_icon_color = 0;
    Color titlebar_button_hover_bg = 0;
    Color titlebar_close_hover_bg = 0;
    bool rounded_corners = false;
    int rounded_corner_radius = 0;
    bool rounded_layered_active = false;
    int rounded_layered_radius_px = 0;
    int rounded_layered_failures = 0;
    int frame_flags = EU_WINDOW_FRAME_DEFAULT;
    bool frame_flags_explicit = false;
    int resize_border_left = 6;
    int resize_border_top = 6;
    int resize_border_right = 6;
    int resize_border_bottom = 6;
    std::vector<Rect> drag_regions;
    std::vector<Rect> no_drag_regions;
    HICON window_icon_big = nullptr;
    HICON window_icon_small = nullptr;

    // Manual resize tracking (for WS_POPUP without WS_THICKFRAME)
    bool sizing = false;
    int  size_dir = 0;           // HTLEFT, HTRIGHT, etc.
    POINT size_start = {0, 0};  // mouse pos at start
    RECT  size_rect = {0};      // window rect at start

    WindowResizeCallback resize_cb = nullptr;
    WindowCloseCallback close_cb = nullptr;
};

extern std::map<HWND, WindowState*> g_windows;
extern thread_local WindowCreateParams* g_pending_create_params;

WindowState* window_state(HWND hwnd);
void register_window_class();
void recreate_render_target(WindowState* st);
void apply_window_rounded_corners(WindowState* st);
void apply_window_frame_flags(WindowState* st, int flags, bool explicit_flags);
