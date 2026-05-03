#include "element_tag.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color tag_base_color(const Theme* t, int type, Color custom) {
    if (custom) return custom;
    switch (type) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFF909399;
    case 3: return 0xFFE6A23C;
    case 4: return 0xFFF56C6C;
    default: return t->accent;
    }
}

static void tag_colors(HWND hwnd, const Theme* t, int type, int effect, Color custom,
                       Color& bg, Color& border, Color& fg) {
    Color base = tag_base_color(t, type, custom);
    bool dark = is_dark_theme_for_window(hwnd);
    if (effect == 1) {
        bg = base;
        border = base;
        fg = 0xFFFFFFFF;
    } else if (effect == 2) {
        bg = 0;
        border = with_alpha(base, dark ? 0xAA : 0x88);
        fg = base;
    } else {
        bg = with_alpha(base, dark ? 0x22 : 0x18);
        border = with_alpha(base, dark ? 0x66 : 0x44);
        fg = base;
    }
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Tag::set_type(int value) {
    if (value < 0) value = 0;
    if (value > 4) value = 4;
    tag_type = value;
    invalidate();
}

void Tag::set_effect(int value) {
    if (value < 0) value = 0;
    if (value > 2) value = 2;
    effect = value;
    invalidate();
}

void Tag::set_closable(bool value) {
    closable = value;
    invalidate();
}

void Tag::set_closed(bool value) {
    closed = value;
    invalidate();
}

void Tag::set_size_preset(int value) {
    if (value < 0) value = 0;
    if (value > 2) value = 2;
    size_preset = value;
    float font_sizes[] = { 12.0f, 13.0f, 15.0f };
    int pad_x[] = { 8, 10, 12 };
    ElementStyle next = has_logical_style ? logical_style : style;
    next.font_size = font_sizes[size_preset];
    next.pad_left = pad_x[size_preset];
    next.pad_right = pad_x[size_preset];
    next.pad_top = 0;
    next.pad_bottom = 0;
    set_logical_style(next);
    invalidate();
}

void Tag::set_theme_color(Color value) {
    theme_color = value;
    invalidate();
}

Rect Tag::close_rect() const {
    int size = round_px(style.font_size * 1.25f);
    if (size < 16) size = 16;
    if (size > bounds.h - 4) size = bounds.h - 4;
    if (size < 8) size = 8;
    int x = bounds.w - style.pad_right - size;
    int y = (bounds.h - size) / 2;
    return { x, y, size, size };
}

bool Tag::close_hit(int x, int y) const {
    if (!closable) return false;
    Rect r = close_rect();
    return r.contains(x, y);
}

void Tag::paint(RenderContext& ctx) {
    if (!visible || closed || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg, border, fg;
    tag_colors(owner_hwnd, t, tag_type, effect, theme_color, bg, border, fg);
    if (style.bg_color) bg = style.bg_color;
    if (style.border_color) border = style.border_color;
    if (style.fg_color) fg = style.fg_color;

    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        ROUNDED(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float right_pad = (float)style.pad_right;
    if (closable) right_pad += (float)close_rect().w + 4.0f;
    float text_w = (float)bounds.w - (float)style.pad_left - right_pad;
    if (text_w < 1.0f) text_w = 1.0f;
    draw_text(ctx, text, style, fg, (float)style.pad_left, 0.0f, text_w, (float)bounds.h);

    if (closable) {
        Rect cr = close_rect();
        Color close_bg = m_close_down ? with_alpha(fg, 0x44) : (m_close_hover ? with_alpha(fg, 0x22) : 0);
        if (close_bg) {
            D2D1_RECT_F close_fill = { (float)cr.x, (float)cr.y, (float)(cr.x + cr.w), (float)(cr.y + cr.h) };
            ctx.rt->FillEllipse(D2D1::Ellipse(
                D2D1::Point2F((float)cr.x + cr.w * 0.5f, (float)cr.y + cr.h * 0.5f),
                cr.w * 0.5f, cr.h * 0.5f), ctx.get_brush(close_bg));
        }
        float cx = (float)cr.x + cr.w * 0.5f;
        float cy = (float)cr.y + cr.h * 0.5f;
        float s = (std::max)(4.0f, style.font_size * 0.28f);
        ctx.rt->DrawLine(D2D1::Point2F(cx - s, cy - s), D2D1::Point2F(cx + s, cy + s),
                         ctx.get_brush(fg), 1.25f);
        ctx.rt->DrawLine(D2D1::Point2F(cx + s, cy - s), D2D1::Point2F(cx - s, cy + s),
                         ctx.get_brush(fg), 1.25f);
    }

    ctx.rt->SetTransform(saved);
}

Element* Tag::hit_test(int x, int y) {
    if (closed) return nullptr;
    return Element::hit_test(x, y);
}

void Tag::on_mouse_move(int x, int y) {
    if (closed) return;
    bool hot = close_hit(x, y);
    if (hot != m_close_hover) {
        m_close_hover = hot;
        invalidate();
    }
}

void Tag::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_close_hover = false;
    m_close_down = false;
    invalidate();
}

void Tag::on_mouse_down(int x, int y, MouseButton) {
    if (closed) return;
    pressed = true;
    m_close_down = close_hit(x, y);
    invalidate();
}

void Tag::on_mouse_up(int x, int y, MouseButton) {
    if (closed) return;
    if (m_close_down && close_hit(x, y)) {
        set_closed(true);
        if (close_cb) close_cb(id);
    }
    pressed = false;
    m_close_down = false;
    invalidate();
}
