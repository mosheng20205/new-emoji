#include "element_base.h"
#include "render_context.h"
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int scale_int(int v, float scale) {
    return (int)std::lround((float)v * scale);
}

static float scale_float(float v, float scale) {
    return v * scale;
}

static Rect scale_rect(const Rect& r, float scale) {
    return { scale_int(r.x, scale), scale_int(r.y, scale),
             scale_int(r.w, scale), scale_int(r.h, scale) };
}

static ElementStyle scale_style(const ElementStyle& src, float scale) {
    ElementStyle dst = src;
    dst.border_width = scale_float(src.border_width, scale);
    dst.corner_radius = scale_float(src.corner_radius, scale);
    dst.pad_left = scale_int(src.pad_left, scale);
    dst.pad_top = scale_int(src.pad_top, scale);
    dst.pad_right = scale_int(src.pad_right, scale);
    dst.pad_bottom = scale_int(src.pad_bottom, scale);
    dst.font_size = scale_float(src.font_size, scale);
    return dst;
}

void Element::layout(const Rect& available) {
    bounds = available;
    for (auto& ch : children) {
        if (ch->visible) ch->layout(ch->bounds);
    }
}

void Element::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    // Save transform; apply translation to local origin
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    D2D1_MATRIX_3X2_F local = saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y);
    ctx.rt->SetTransform(local);

    // Clip to local bounds
    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    // Draw background at (0,0)
    if (style.bg_color != 0) {
        auto* br = ctx.get_brush(style.bg_color);
        D2D1_RECT_F r = { 0, 0, (float)bounds.w, (float)bounds.h };
        if (style.corner_radius > 0) {
            ctx.rt->FillRoundedRectangle(
                ROUNDED(r, style.corner_radius, style.corner_radius), br);
        } else {
            ctx.rt->FillRectangle(r, br);
        }
    }

    // Paint children (each applies its own transform)
    for (auto& ch : children) {
        if (ch->visible) ch->paint(ctx);
    }

    // Border at (0,0)
    if (style.border_width > 0 && style.border_color != 0) {
        auto* br = ctx.get_brush(style.border_color);
        float hw = style.border_width * 0.5f;
        D2D1_RECT_F r = { hw, hw,
                          (float)bounds.w - hw, (float)bounds.h - hw };
        if (style.corner_radius > 0) {
            ctx.rt->DrawRoundedRectangle(
                ROUNDED(r, style.corner_radius, style.corner_radius), br, style.border_width);
        } else {
            ctx.rt->DrawRectangle(r, br, style.border_width);
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);   // Restore parent transform
}

void Element::paint_overlay(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    for (auto& ch : children) {
        if (ch->visible) ch->paint_overlay(ctx);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

// ── Hit test ─────────────────────────────────────────────────────────

Element* Element::hit_test(int x, int y) {
    if (!visible) return nullptr;
    // x,y is in PARENT space; offset to local
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (parent != nullptr) {
        for (auto it = children.rbegin(); it != children.rend(); ++it) {
            Element* hit = (*it)->hit_test_overlay(lx, ly);
            if (hit) return hit;
        }
    }
    for (auto it = children.rbegin(); it != children.rend(); ++it) {
        if (parent == nullptr) {
            Element* overlay_hit = (*it)->hit_test_overlay(lx, ly);
            if (overlay_hit) return overlay_hit;
        }
        Element* hit = (*it)->hit_test(lx, ly);
        if (hit) return hit;
    }
    if (!mouse_passthrough && parent != nullptr && 0 <= lx && lx < bounds.w && 0 <= ly && ly < bounds.h)
        return this;
    return nullptr;
}

Element* Element::hit_test_overlay(int x, int y) {
    if (!visible) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    for (auto it = children.rbegin(); it != children.rend(); ++it) {
        Element* hit = (*it)->hit_test_overlay(lx, ly);
        if (hit) return hit;
    }
    return nullptr;
}

// ── Input stubs ──────────────────────────────────────────────────────

void Element::set_logical_bounds(const Rect& r) {
    logical_bounds = r;
    has_logical_bounds = true;
}

void Element::set_logical_style(const ElementStyle& s) {
    logical_style = s;
    has_logical_style = true;
}

void Element::apply_dpi_scale(float scale) {
    if (has_logical_bounds) bounds = scale_rect(logical_bounds, scale);
    if (has_logical_style) style = scale_style(logical_style, scale);
    for (auto& ch : children) {
        if (ch) ch->apply_dpi_scale(scale);
    }
}

void Element::on_mouse_enter()  { hovered = true; invalidate(); }
void Element::on_mouse_leave()  { hovered = false; pressed = false; invalidate(); }
void Element::on_mouse_down(int, int, MouseButton) { pressed = true; invalidate(); }
void Element::on_mouse_up(int, int, MouseButton)   { pressed = false; invalidate(); }
void Element::on_mouse_move(int, int) {}
void Element::on_mouse_wheel(int, int, int) {}
void Element::on_key_down(int, int) {}
void Element::on_key_up(int, int) {}
void Element::on_char(wchar_t) {}
void Element::on_focus()  { has_focus = true; invalidate(); }
void Element::on_blur()   { has_focus = false; invalidate(); }
void Element::on_dpi_scale_changed(float, float) {}

void Element::invalidate() {
    if (owner_hwnd) InvalidateRect(owner_hwnd, nullptr, FALSE);
}

void Element::get_absolute_pos(int& ox, int& oy) const {
    ox = 0; oy = 0;
    for (const Element* e = this; e; e = e->parent) {
        ox += e->bounds.x;
        oy += e->bounds.y;
    }
}

Rect Element::content_rect() const {
    Rect r;
    r.x = style.pad_left;
    r.y = style.pad_top;
    r.w = bounds.w - style.pad_left - style.pad_right;
    r.h = bounds.h - style.pad_top - style.pad_bottom;
    if (r.w < 0) r.w = 0;
    if (r.h < 0) r.h = 0;
    return r;
}
