#include "element_icon_button.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_center_text(RenderContext& ctx, const std::wstring& text,
                             const ElementStyle& style, Color color,
                             float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static int tooltip_text_width(const std::wstring& text, float font_size) {
    float width = 24.0f;
    for (wchar_t ch : text) {
        width += ch <= 0x007F ? font_size * 0.62f : font_size * 1.08f;
    }
    return (int)std::ceil(width);
}

static float tooltip_font_size() {
    return 12.0f;
}

void IconButton::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));
    ctx.push_clip({0, 0, (float)bounds.w, (float)bounds.h});

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = normal_bg;
    if (!enabled) bg = disabled_bg;
    else if (pressed) bg = pressed_bg ? pressed_bg : t->chrome_icon_button_pressed_bg;
    else if (hovered) bg = hover_bg ? hover_bg : t->chrome_icon_button_hover_bg;
    else if (checked) bg = checked_bg ? checked_bg : t->chrome_icon_button_checked_bg;

    float left = (float)style.pad_left;
    float top = (float)style.pad_top;
    float right = (float)(bounds.w - style.pad_right);
    float bottom = (float)(bounds.h - style.pad_bottom);
    if (right < left) right = left;
    if (bottom < top) bottom = top;
    D2D1_RECT_F r = { left, top, right, bottom };
    float radius = style.corner_radius;
    if (shape == 1) radius = (std::min)(right - left, bottom - top) * 0.5f;
    else if (shape == 2) radius = (bottom - top) * 0.5f;
    if ((bg >> 24) != 0) {
        ctx.rt->FillRoundedRectangle(ROUNDED(r, radius, radius), ctx.get_brush(bg));
    }

    ElementStyle icon_style = style;
    icon_style.font_size = (float)icon_size;
    Color fg = enabled
        ? (icon_color ? icon_color : t->chrome_icon_button_fg)
        : (disabled_icon_color ? disabled_icon_color : with_alpha(t->chrome_icon_button_fg, 0x60));
    draw_center_text(ctx, icon.empty() ? text : icon, icon_style, fg,
                     0.0f, 0.0f, (float)bounds.w, (float)bounds.h);

    if (badge_visible && !badge_text.empty()) {
        ElementStyle badge_style = style;
        badge_style.font_size = (std::max)(9.0f, style.font_size - 3.0f);
        float bw = (std::max)(14.0f, 8.0f + (float)badge_text.size() * badge_style.font_size * 0.45f);
        float bh = 14.0f;
        D2D1_RECT_F br = { (float)bounds.w - bw - 2.0f, 1.0f, (float)bounds.w - 2.0f, 1.0f + bh };
        ctx.rt->FillRoundedRectangle(ROUNDED(br, bh * 0.5f, bh * 0.5f),
                                     ctx.get_brush(t->chrome_tab_alert_color));
        draw_center_text(ctx, badge_text, badge_style, 0xFFFFFFFF,
                         br.left, br.top - 0.5f, br.right - br.left, br.bottom - br.top);
    }

    if (has_focus) {
        D2D1_RECT_F fr = { 1.5f, 1.5f, (float)bounds.w - 1.5f, (float)bounds.h - 1.5f };
        ctx.rt->DrawRoundedRectangle(ROUNDED(fr, radius, radius), ctx.get_brush(t->accent), 1.0f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void IconButton::paint_overlay(RenderContext& ctx) {
    if (!visible || !enabled || !hovered || suppress_tooltip_until_leave ||
        tooltip.empty() || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    ElementStyle tip_style = style;
    tip_style.font_size = tooltip_font_size();
    float tw = (float)(std::max)(42, (std::min)(220, tooltip_text_width(tooltip, tip_style.font_size)));
    float th = 24.0f;
    float tx = ((float)bounds.w - tw) * 0.5f;
    float ty = (float)bounds.h + 6.0f;
    D2D1_SIZE_F rt_size = ctx.rt->GetSize();
    float global_left = (float)bounds.x + tx;
    if (global_left < 6.0f) tx += 6.0f - global_left;
    float global_right = (float)bounds.x + tx + tw;
    if (global_right > rt_size.width - 6.0f) tx -= global_right - (rt_size.width - 6.0f);

    D2D1_RECT_F r = { tx, ty, tx + tw, ty + th };
    ctx.rt->FillRoundedRectangle(ROUNDED(r, 5.0f, 5.0f), ctx.get_brush(0xF2222222));
    ctx.rt->DrawRoundedRectangle(ROUNDED(r, 5.0f, 5.0f), ctx.get_brush(0x33FFFFFF), 1.0f);
    draw_center_text(ctx, tooltip, tip_style, 0xFFFFFFFF,
                     r.left + 8.0f, r.top, r.right - r.left - 16.0f, r.bottom - r.top);

    ctx.rt->SetTransform(saved);
}

void IconButton::on_mouse_enter() { hovered = true; invalidate(); }
void IconButton::on_mouse_leave() {
    hovered = false;
    pressed = false;
    keyboard_armed = false;
    suppress_tooltip_until_leave = false;
    invalidate();
}
void IconButton::on_mouse_down(int, int, MouseButton btn) {
    if (btn == MouseButton::Left && enabled) { pressed = true; invalidate(); }
}
void IconButton::on_mouse_up(int, int, MouseButton) {
    pressed = false;
    keyboard_armed = false;
    invalidate();
}
void IconButton::on_key_down(int vk, int) {
    if (!enabled) return;
    if (vk == VK_SPACE || vk == VK_RETURN) {
        pressed = true;
        keyboard_armed = true;
        invalidate();
    }
}
void IconButton::on_key_up(int vk, int) {
    if (keyboard_armed && (vk == VK_SPACE || vk == VK_RETURN)) {
        pressed = false;
        keyboard_armed = false;
        invalidate();
    }
}

void IconButton::set_colors(Color normal, Color hover, Color press, Color checked_color,
                            Color disabled, Color icon_value, Color disabled_icon) {
    normal_bg = normal;
    hover_bg = hover;
    pressed_bg = press;
    checked_bg = checked_color;
    disabled_bg = disabled;
    icon_color = icon_value;
    disabled_icon_color = disabled_icon;
    invalidate();
}

void IconButton::set_shape(int next_shape, int radius) {
    shape = (std::max)(0, (std::min)(2, next_shape));
    style.corner_radius = (float)(std::max)(0, radius);
    logical_style.corner_radius = style.corner_radius;
    has_logical_style = true;
    invalidate();
}

void IconButton::set_padding(int left, int top, int right, int bottom) {
    style.pad_left = (std::max)(0, left);
    style.pad_top = (std::max)(0, top);
    style.pad_right = (std::max)(0, right);
    style.pad_bottom = (std::max)(0, bottom);
    logical_style = style;
    has_logical_style = true;
    invalidate();
}

void IconButton::set_icon_size(int size) {
    icon_size = (std::max)(8, size);
    invalidate();
}

void IconButton::suppress_tooltip_once() {
    suppress_tooltip_until_leave = true;
    invalidate();
}
