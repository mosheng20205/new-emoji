#include "element_alert.h"
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

static Color feedback_color(const Theme* t, int type) {
    switch (type) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Alert::set_description(const std::wstring& value) {
    description = value;
    invalidate();
}

void Alert::set_type(int value) {
    if (value < 0) value = 0;
    if (value > 3) value = 3;
    alert_type = value;
    last_action = 1;
    invalidate();
}

void Alert::set_effect(int value) {
    effect = value == 1 ? 1 : 0;
    last_action = 1;
    invalidate();
}

void Alert::set_closable(bool value) {
    closable = value;
    last_action = 1;
    invalidate();
}

void Alert::set_closed(bool value) {
    closed = value;
    visible = !closed;
    last_action = 1;
    invalidate();
}

void Alert::close_alert(int action) {
    if (!closable || closed) return;
    closed = true;
    visible = false;
    ++close_count;
    last_action = action;
    if (close_cb) close_cb(id, close_count, alert_type, last_action);
    invalidate();
}

Rect Alert::close_rect() const {
    int size = round_px(style.font_size * 1.45f);
    if (size < 18) size = 18;
    if (size > bounds.h - 8) size = bounds.h - 8;
    int x = bounds.w - style.pad_right - size;
    int y = (bounds.h - size) / 2;
    return { x, y, size, size };
}

bool Alert::close_hit(int x, int y) const {
    return closable && close_rect().contains(x, y);
}

void Alert::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color base = feedback_color(t, alert_type);
    Color bg = effect == 1 ? base : with_alpha(base, is_dark_theme_for_window(owner_hwnd) ? 0x26 : 0x18);
    Color border = effect == 1 ? base : with_alpha(base, is_dark_theme_for_window(owner_hwnd) ? 0x66 : 0x44);
    Color fg = effect == 1 ? 0xFFFFFFFF : base;
    Color body = effect == 1 ? 0xFFFFFFFF : (style.fg_color ? style.fg_color : t->text_primary);
    if (style.bg_color) bg = style.bg_color;
    if (style.border_color) border = style.border_color;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float icon_d = (std::max)(18.0f, style.font_size * 1.35f);
    float icon_x = (float)style.pad_left;
    float icon_y = ((float)bounds.h - icon_d) * 0.5f;
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(icon_x + icon_d * 0.5f, icon_y + icon_d * 0.5f),
                                      icon_d * 0.5f, icon_d * 0.5f),
                        ctx.get_brush(fg));
    std::wstring icon = alert_type == 1 ? L"✓" : (alert_type == 2 ? L"!" : (alert_type == 3 ? L"x" : L"i"));
    draw_text(ctx, icon, style, effect == 1 ? base : 0xFFFFFFFF,
              icon_x, icon_y, icon_d, icon_d, 0.9f, DWRITE_TEXT_ALIGNMENT_CENTER);

    float text_x = icon_x + icon_d + 10.0f;
    float right = closable ? (float)close_rect().x - 8.0f : (float)bounds.w - style.pad_right;
    float text_w = right - text_x;
    if (text_w < 1.0f) text_w = 1.0f;
    float title_h = description.empty() ? (float)bounds.h : style.font_size * 1.55f;
    float title_y = description.empty() ? 0.0f : (float)style.pad_top;
    draw_text(ctx, text.empty() ? L"Alert" : text, style, body,
              text_x, title_y, text_w, title_h);
    if (!description.empty()) {
        draw_text(ctx, description, style, effect == 1 ? 0xFFEFF6FF : t->text_secondary,
                  text_x, title_y + title_h - 2.0f, text_w,
                  (float)bounds.h - title_y - title_h, 0.92f);
    }

    if (closable) {
        Rect cr = close_rect();
        Color close_fg = effect == 1 ? 0xFFFFFFFF : t->text_secondary;
        if (m_close_hover || m_close_down) {
            ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((float)cr.x + cr.w * 0.5f,
                                                            (float)cr.y + cr.h * 0.5f),
                                              cr.w * 0.5f, cr.h * 0.5f),
                                ctx.get_brush(with_alpha(close_fg, m_close_down ? 0x44 : 0x22)));
        }
        float cx = (float)cr.x + cr.w * 0.5f;
        float cy = (float)cr.y + cr.h * 0.5f;
        float s = (std::max)(4.0f, style.font_size * 0.32f);
        ctx.rt->DrawLine(D2D1::Point2F(cx - s, cy - s), D2D1::Point2F(cx + s, cy + s),
                         ctx.get_brush(close_fg), 1.2f);
        ctx.rt->DrawLine(D2D1::Point2F(cx + s, cy - s), D2D1::Point2F(cx - s, cy + s),
                         ctx.get_brush(close_fg), 1.2f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Alert::on_mouse_move(int x, int y) {
    bool hot = close_hit(x, y);
    if (hot != m_close_hover) {
        m_close_hover = hot;
        invalidate();
    }
}

void Alert::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_close_hover = false;
    m_close_down = false;
    invalidate();
}

void Alert::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_close_down = close_hit(x, y);
    invalidate();
}

void Alert::on_mouse_up(int x, int y, MouseButton) {
    if (m_close_down && close_hit(x, y)) {
        close_alert(2);
    }
    pressed = false;
    m_close_down = false;
    invalidate();
}

void Alert::on_key_down(int vk, int) {
    if ((vk == VK_DELETE || vk == VK_ESCAPE || vk == VK_RETURN || vk == VK_SPACE) && closable) {
        close_alert(3);
    }
}
