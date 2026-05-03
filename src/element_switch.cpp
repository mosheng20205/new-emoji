#include "element_switch.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>

static void draw_label(RenderContext& ctx, const Theme* theme, const ElementStyle& style,
                       const std::wstring& text, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(style.fg_color ? style.fg_color : theme->text_primary),
        D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Switch::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    if (style.bg_color) {
        D2D1_RECT_F bg = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(bg, ctx.get_brush(style.bg_color));
    }

    float track_h = (std::max)(14.0f, style.font_size * 1.1f);
    track_h = (std::min)(track_h, 22.0f);
    if (size == 1) { track_h -= 3.0f; } else if (size == 2) { track_h -= 6.0f; }
    float track_w = (std::max)(34.0f, track_h * 1.9f);
    if (size == 1) track_w -= 4.0f; else if (size == 2) track_w -= 8.0f;
    float track_x = (float)style.pad_left;
    float track_y = ((float)bounds.h - track_h) * 0.5f;
    if (track_y < (float)style.pad_top) track_y = (float)style.pad_top;

    float radius = track_h * 0.5f;
    Color track_fill = loading ? 0xFFE6A23C
        : (checked ? (active_color ? active_color : t->accent)
                   : (inactive_color ? inactive_color : (hovered ? t->button_hover : t->button_bg)));
    Color track_border = loading ? 0xFFE6A23C
        : (checked ? (active_color ? active_color : t->accent)
                   : (inactive_color ? inactive_color : (style.border_color ? style.border_color : t->border_default)));
    if (!enabled) {
        track_fill = t->button_bg;
        track_border = t->border_default;
    }

    D2D1_RECT_F track = { track_x, track_y, track_x + track_w, track_y + track_h };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(track, radius, radius), ctx.get_brush(track_fill));
    ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(track, radius, radius), ctx.get_brush(track_border), 1.0f);
    if (has_focus) {
        D2D1_RECT_F focus = { track.left - 3.0f, track.top - 3.0f, track.right + 3.0f, track.bottom + 3.0f };
        ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(focus, radius + 3.0f, radius + 3.0f), ctx.get_brush(t->accent), 1.0f);
    }

    float knob_r = radius - 2.0f;
    if (knob_r < 5.0f) knob_r = 5.0f;
    float knob_x = checked ? (track_x + track_w - radius) : (track_x + radius);
    float knob_y = track_y + radius;
    D2D1_ELLIPSE knob = D2D1::Ellipse(D2D1::Point2F(knob_x, knob_y), knob_r, knob_r);
    ctx.rt->FillEllipse(knob, ctx.get_brush(0xFFFFFFFF));
    if (hovered || pressed) {
        ctx.rt->DrawEllipse(knob, ctx.get_brush(t->accent), 1.0f);
    }
    if (loading) {
        float s = knob_r * 0.72f;
        ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(knob_x, knob_y), s, s),
                            ctx.get_brush(0xFFE6A23C), 1.4f);
    }

    float label_x = track_x + track_w + 10.0f;
    float label_w = (float)bounds.w - label_x - (float)style.pad_right;
    std::wstring label = text;
    std::wstring state_text = checked ? active_text : inactive_text;
    if (!state_text.empty()) label = text.empty() ? state_text : (text + L" " + state_text);
    if (loading) label = label.empty() ? L"加载中" : (label + L" · 加载中");
    ElementStyle label_style = style;
    if (!enabled && !label_style.fg_color) label_style.fg_color = t->text_muted;
    draw_label(ctx, t, label_style, label, label_x, (float)style.pad_top, label_w,
               (float)bounds.h - (float)style.pad_top - (float)style.pad_bottom);

    ctx.rt->SetTransform(saved);
}

void Switch::on_mouse_down(int, int, MouseButton) {
    if (!enabled || loading) return;
    pressed = true;
    invalidate();
}

void Switch::on_mouse_up(int, int, MouseButton) {
    if (pressed && enabled && !loading) {
        set_checked(!checked);
    }
    pressed = false;
}

void Switch::on_key_down(int vk, int) {
    if (!enabled || loading) return;
    if (vk == VK_SPACE || vk == VK_RETURN) {
        key_armed = true;
        pressed = true;
        invalidate();
    }
}

void Switch::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = enabled && !loading && key_armed;
        if (should_click) set_checked(!checked);
        key_armed = false;
        pressed = false;
        invalidate();
        if (should_click && click_cb) click_cb(id);
    }
}

void Switch::set_checked(bool val) {
    checked = val;
    value = checked ? active_value : inactive_value;
    invalidate();
}

void Switch::set_loading(bool val) {
    loading = val;
    invalidate();
}

void Switch::set_value(int v) {
    value = v;
    if (v == active_value) checked = true;
    else if (v == inactive_value) checked = false;
    else checked = (std::abs)(v - active_value) <= (std::abs)(v - inactive_value);
    value = checked ? active_value : inactive_value;
    invalidate();
}

int Switch::get_value() const {
    return checked ? active_value : inactive_value;
}

void Switch::set_active_color(Color c) {
    active_color = c;
    invalidate();
}

void Switch::set_inactive_color(Color c) {
    inactive_color = c;
    invalidate();
}

void Switch::set_size(int sz) {
    if (sz < 0) sz = 0; else if (sz > 2) sz = 2;
    size = sz;
    invalidate();
}

void Switch::set_texts(const std::wstring& active, const std::wstring& inactive) {
    active_text = active;
    inactive_text = inactive;
    invalidate();
}
