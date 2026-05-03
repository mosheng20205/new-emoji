#pragma once
#include "element_types.h"
#include <string>
#include <vector>
#include <memory>

// Forward declarations
class RenderContext;

class Element {
public:
    int id = 0;
    std::wstring text;
    Rect bounds;
    Rect logical_bounds;
    bool has_logical_bounds = false;
    ElementStyle style;
    ElementStyle logical_style;
    bool has_logical_style = false;
    bool visible = true;
    bool enabled = true;
    bool hovered = false;
    bool pressed = false;
    bool has_focus = false;
    bool mouse_passthrough = false;

    Element* parent = nullptr;
    std::vector<std::unique_ptr<Element>> children;

    // Callbacks (stored per-element, C-style)
    ElementClickCallback click_cb = nullptr;
    ElementKeyCallback   key_cb = nullptr;
    // Owner HWND for invalidation — set by ElementTree
    HWND owner_hwnd = nullptr;

    virtual ~Element() = default;
    virtual const wchar_t* type_name() const { return L"Element"; }

    virtual void layout(const Rect& available);
    virtual void paint(RenderContext& ctx);
    virtual void paint_overlay(RenderContext& ctx);
    virtual Element* hit_test(int x, int y);
    virtual Element* hit_test_overlay(int x, int y);

    // Input events — default no-ops
    virtual void on_mouse_enter();
    virtual void on_mouse_leave();
    virtual void on_mouse_down(int x, int y, MouseButton btn);
    virtual void on_mouse_up(int x, int y, MouseButton btn);
    virtual void on_mouse_move(int x, int y);
    virtual void on_mouse_wheel(int x, int y, int delta);
    virtual void on_key_down(int vk, int mods);
    virtual void on_key_up(int vk, int mods);
    virtual void on_char(wchar_t ch);
    virtual void on_focus();
    virtual void on_blur();
    virtual void on_dpi_scale_changed(float old_scale, float new_scale);

    // Helpers
    void set_logical_bounds(const Rect& r);
    void set_logical_style(const ElementStyle& s);
    virtual void apply_dpi_scale(float scale);
    void invalidate();           // InvalidateRect on owner_hwnd
    Rect content_rect() const;   // bounds minus padding
    void get_absolute_pos(int& ox, int& oy) const;  // cumulative offset from window
    int next_child_id = 1;       // id counter for children
};
