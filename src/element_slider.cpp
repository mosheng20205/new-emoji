#include "element_slider.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>
#include <cmath>

static void draw_label(RenderContext& ctx, const Theme* theme, const ElementStyle& style,
                       const std::wstring& text, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(style.fg_color ? style.fg_color : theme->text_primary),
        D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static void draw_value(RenderContext& ctx, const Theme* theme, const ElementStyle& style,
                       int value, float x, float y, float w, float h) {
    std::wstring text = std::to_wstring(value);
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * 0.9f, w, h);
    if (!layout) return;
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_TRAILING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(style.fg_color ? style.fg_color : theme->text_secondary),
        D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

int Slider::clamp_value(int v) const {
    if (min_value > max_value) return v;
    return (std::max)(min_value, (std::min)(max_value, v));
}

int Slider::snap_value(int v) const {
    int clamped = clamp_value(v);
    if (step <= 1) return clamped;
    int offset = clamped - min_value;
    int snapped = min_value + ((offset + step / 2) / step) * step;
    return clamp_value(snapped);
}

void Slider::set_range(int min_v, int max_v) {
    if (min_v == max_v) max_v = min_v + 1;
    if (min_v > max_v) std::swap(min_v, max_v);
    min_value = min_v;
    max_value = max_v;
    value = snap_value(value);
    range_start = snap_value(range_start);
    range_end = snap_value(range_end);
    if (range_start > range_end) std::swap(range_start, range_end);
    invalidate();
}

void Slider::set_value(int new_value) {
    int clamped = snap_value(new_value);
    if (clamped == value) return;
    value = clamped;
    if (!range_mode) {
        range_start = min_value;
        range_end = value;
    }
    invalidate();
    notify_value_changed();
}

void Slider::set_range_value(int start_value, int end_value) {
    int start = snap_value(start_value);
    int end = snap_value(end_value);
    if (start > end) std::swap(start, end);
    bool changed = (start != range_start || end != range_end || value != end);
    range_start = start;
    range_end = end;
    value = end;
    if (changed) {
        invalidate();
        notify_value_changed();
    }
}

void Slider::set_range_mode(bool enabled, int start_value, int end_value) {
    range_mode = enabled;
    if (enabled) {
        set_range_value(start_value, end_value);
    } else {
        set_value(end_value);
    }
    invalidate();
}

void Slider::set_options(int new_step, bool tooltip) {
    if (new_step < 1) new_step = 1;
    step = new_step;
    show_tooltip = tooltip;
    set_value(value);
    invalidate();
}

float Slider::value_to_x(int v, float track_left, float track_w) const {
    float denom = (float)(max_value - min_value);
    float ratio = denom > 0.0f ? (float)(clamp_value(v) - min_value) / denom : 0.0f;
    if (ratio < 0.0f) ratio = 0.0f;
    if (ratio > 1.0f) ratio = 1.0f;
    return track_left + ratio * track_w;
}

int Slider::value_from_local_x(int x) const {
    float left = (float)style.pad_left;
    float right = (float)bounds.w - (float)style.pad_right;
    float usable = right - left;
    if (usable < 1.0f) usable = 1.0f;
    float ratio = ((float)x - left) / usable;
    if (ratio < 0.0f) ratio = 0.0f;
    if (ratio > 1.0f) ratio = 1.0f;
    int next = min_value + (int)((float)(max_value - min_value) * ratio + 0.5f);
    return snap_value(next);
}

void Slider::update_from_local_x(int x) {
    int next = value_from_local_x(x);
    if (range_mode) {
        if (active_thumb <= 0) active_thumb = 2;
        if (active_thumb == 1) {
            set_range_value(next, range_end);
        } else {
            set_range_value(range_start, next);
        }
    } else {
        set_value(next);
    }
}

void Slider::notify_value_changed() {
    if (value_cb) {
        value_cb(id, value, range_start, range_end);
    }
}

void Slider::paint(RenderContext& ctx) {
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

    bool has_label = !text.empty();
    float label_h = has_label ? (style.font_size * 1.15f) : 0.0f;
    float label_y = (float)style.pad_top;
    if (has_label) {
        float value_w = 72.0f;
        draw_label(ctx, t, style, text, (float)style.pad_left, label_y,
                   (float)bounds.w - (float)style.pad_left - (float)style.pad_right - value_w,
                   label_h);
        draw_value(ctx, t, style, value, (float)bounds.w - (float)style.pad_right - value_w,
                   label_y, value_w, label_h);
    }

    float track_left = (float)style.pad_left;
    float track_right = (float)bounds.w - (float)style.pad_right;
    float track_w = track_right - track_left;
    if (track_w < 1.0f) track_w = 1.0f;
    float track_h = 4.0f;
    float track_y = has_label ? (label_y + label_h + 6.0f) : ((float)bounds.h - track_h) * 0.5f;
    float track_bottom = (float)bounds.h - (float)style.pad_bottom;
    if (track_y + track_h > track_bottom) track_y = track_bottom - track_h;
    if (track_y < (float)style.pad_top) track_y = (float)style.pad_top;

    D2D1_RECT_F track = { track_left, track_y, track_left + track_w, track_y + track_h };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(track, track_h * 0.5f, track_h * 0.5f),
                                 ctx.get_brush(t->border_default));

    float denom = (float)(max_value - min_value);
    float ratio = denom > 0.0f ? (float)(value - min_value) / denom : 0.0f;
    if (ratio < 0.0f) ratio = 0.0f;
    if (ratio > 1.0f) ratio = 1.0f;

    float thumb_x = value_to_x(value, track_left, track_w);
    float thumb_y = track_y + track_h * 0.5f;
    float thumb_r = pressed ? 9.0f : 8.0f;
    float fill_left = track_left;
    float fill_right = thumb_x;
    if (range_mode) {
        fill_left = value_to_x(range_start, track_left, track_w);
        fill_right = value_to_x(range_end, track_left, track_w);
        if (fill_left > fill_right) std::swap(fill_left, fill_right);
        thumb_x = (active_thumb == 1) ? fill_left : fill_right;
    }
    D2D1_RECT_F fill_rect = { fill_left, track_y, fill_right, track_y + track_h };
    if (fill_rect.right > fill_rect.left) {
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(fill_rect, track_h * 0.5f, track_h * 0.5f),
                                     ctx.get_brush(t->accent));
    }

    auto draw_thumb = [&](float cx, bool active) {
        float radius = active ? thumb_r : 8.0f;
        D2D1_ELLIPSE thumb = D2D1::Ellipse(D2D1::Point2F(cx, thumb_y), radius, radius);
        ctx.rt->FillEllipse(thumb, ctx.get_brush(enabled ? 0xFFFFFFFF : t->button_press));
        ctx.rt->DrawEllipse(thumb, ctx.get_brush(active || hovered ? t->accent : t->border_default), 1.0f);
    };
    if (range_mode) {
        draw_thumb(fill_left, active_thumb == 1 && pressed);
        draw_thumb(fill_right, active_thumb == 2 && pressed);
    } else {
        draw_thumb(thumb_x, pressed);
    }

    if (show_tooltip && (hovered || pressed)) {
        std::wstring tip = range_mode
            ? (std::to_wstring(range_start) + L" - " + std::to_wstring(range_end))
            : std::to_wstring(value);
        float tip_w = 42.0f + (float)tip.size() * 4.0f;
        float tip_h = 24.0f;
        float tip_x = thumb_x - tip_w * 0.5f;
        if (tip_x < 2.0f) tip_x = 2.0f;
        if (tip_x + tip_w > (float)bounds.w - 2.0f) tip_x = (float)bounds.w - tip_w - 2.0f;
        float tip_y = track_y - tip_h - 8.0f;
        if (tip_y < 2.0f) tip_y = track_y + track_h + 8.0f;
        D2D1_RECT_F tip_rect = { tip_x, tip_y, tip_x + tip_w, tip_y + tip_h };
        Color tip_bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF2F3142 : 0xFFFFFFFF;
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(tip_rect, 5.0f, 5.0f),
                                     ctx.get_brush(tip_bg));
        ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(tip_rect, 5.0f, 5.0f),
                                     ctx.get_brush(t->border_default), 1.0f);
        draw_value(ctx, t, style, value, tip_x + 6.0f, tip_y + 2.0f,
                   tip_w - 12.0f, tip_h - 4.0f);
    }

    ctx.rt->SetTransform(saved);
}

void Slider::on_mouse_down(int x, int, MouseButton) {
    pressed = true;
    if (range_mode) {
        float track_left = (float)style.pad_left;
        float track_w = (float)bounds.w - (float)style.pad_left - (float)style.pad_right;
        if (track_w < 1.0f) track_w = 1.0f;
        float start_x = value_to_x(range_start, track_left, track_w);
        float end_x = value_to_x(range_end, track_left, track_w);
        active_thumb = (std::abs((float)x - start_x) <= std::abs((float)x - end_x)) ? 1 : 2;
    } else {
        active_thumb = 2;
    }
    update_from_local_x(x);
}

void Slider::on_mouse_up(int x, int, MouseButton) {
    if (pressed) update_from_local_x(x);
    pressed = false;
    active_thumb = 0;
}

void Slider::on_mouse_move(int x, int) {
    if (pressed) update_from_local_x(x);
}

void Slider::on_key_down(int vk, int) {
    if (range_mode && active_thumb == 0) active_thumb = 2;
    switch (vk) {
    case VK_LEFT:
    case VK_DOWN:
        if (range_mode) {
            if (active_thumb == 1) set_range_value(range_start - step, range_end);
            else set_range_value(range_start, range_end - step);
        } else {
            set_value(value - step);
        }
        break;
    case VK_RIGHT:
    case VK_UP:
        if (range_mode) {
            if (active_thumb == 1) set_range_value(range_start + step, range_end);
            else set_range_value(range_start, range_end + step);
        } else {
            set_value(value + step);
        }
        break;
    case VK_HOME:
        if (range_mode && active_thumb == 1) set_range_value(min_value, range_end);
        else if (range_mode) set_range_value(range_start, min_value);
        else set_value(min_value);
        break;
    case VK_END:
        if (range_mode && active_thumb == 1) set_range_value(max_value, range_end);
        else if (range_mode) set_range_value(range_start, max_value);
        else set_value(max_value);
        break;
    case VK_PRIOR:
        if (range_mode && active_thumb == 1) set_range_value(range_start - step * 10, range_end);
        else if (range_mode) set_range_value(range_start, range_end - step * 10);
        else set_value(value - step * 10);
        break;
    case VK_NEXT:
        if (range_mode && active_thumb == 1) set_range_value(range_start + step * 10, range_end);
        else if (range_mode) set_range_value(range_start, range_end + step * 10);
        else set_value(value + step * 10);
        break;
    default:
        break;
    }
}
