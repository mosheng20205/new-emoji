#include "element_scrollbar.h"
#include "element_tree.h"
#include "render_context.h"
#include "theme.h"
#include "window_state.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

int Scrollbar::clamp_value(int candidate) const {
    if (candidate < 0) return 0;
    if (candidate > max_value) return max_value;
    return candidate;
}

void Scrollbar::set_value(int new_value) {
    update_value(new_value, 1);
}

void Scrollbar::update_value(int new_value, int action) {
    int clamped = clamp_value(new_value);
    if (clamped == value) return;
    value = clamped;
    content_offset = value;
    last_action = action;
    ++change_count;
    apply_binding();
    if (change_cb) change_cb(id, value, 0, max_value);
    invalidate();
}

void Scrollbar::set_max_value(int new_max) {
    if (new_max < 0) new_max = 0;
    max_value = new_max;
    value = clamp_value(value);
    content_offset = value;
    apply_binding();
    invalidate();
}

void Scrollbar::set_range(int new_max, int new_page_size) {
    if (new_page_size < 1) new_page_size = 1;
    page_size = new_page_size;
    set_max_value(new_max);
}

void Scrollbar::set_orientation(int next) {
    orientation = next == 0 ? 0 : 1;
    invalidate();
}

void Scrollbar::set_options(int new_max, int new_page_size, int new_orientation, int auto_hide_enabled) {
    auto_hide = auto_hide_enabled != 0;
    set_orientation(new_orientation);
    set_range(new_max, new_page_size);
}

void Scrollbar::set_wheel_step(int step) {
    if (step < 1) step = 1;
    if (step > 1000) step = 1000;
    wheel_step = step;
    invalidate();
}

void Scrollbar::scroll_delta(int delta) {
    if (delta == 0) return;
    update_value(value + delta * wheel_step, 2);
}

void Scrollbar::wheel_delta(int delta) {
    if (delta == 0) return;
    int steps = delta / WHEEL_DELTA;
    if (steps == 0) steps = delta > 0 ? 1 : -1;
    last_wheel_delta = delta;
    ++wheel_event_count;
    update_value(value - steps * wheel_step, 3);
}

void Scrollbar::bind_content(int element_id, const Rect& base, int new_content_size, int new_viewport_size) {
    bound_element_id = element_id;
    bound_base = base;
    if (new_content_size < 0) new_content_size = 0;
    if (new_viewport_size < 1) new_viewport_size = 1;
    content_size = new_content_size;
    viewport_size = new_viewport_size;
    page_size = viewport_size;
    max_value = (std::max)(0, content_size - viewport_size);
    value = clamp_value(value);
    content_offset = value;
    last_action = 6;
    apply_binding();
    invalidate();
}

void Scrollbar::apply_binding() {
    if (!owner_hwnd || bound_element_id <= 0) return;
    WindowState* st = window_state(owner_hwnd);
    if (!st || !st->element_tree) return;
    Element* target = st->element_tree->find_by_id(bound_element_id);
    if (!target) return;
    Rect next = bound_base;
    if (orientation == 0) next.x = bound_base.x - value;
    else next.y = bound_base.y - value;
    target->set_logical_bounds(next);
    target->apply_dpi_scale(st->dpi_scale);
    target->invalidate();
}

Rect Scrollbar::track_rect() const {
    int pad = 4;
    if (orientation == 0) {
        int h = (std::min)(12, (std::max)(8, bounds.h - pad * 2));
        return { pad, (bounds.h - h) / 2, (std::max)(1, bounds.w - pad * 2), h };
    }
    int w = (std::min)(12, (std::max)(8, bounds.w - pad * 2));
    return { (bounds.w - w) / 2, pad, w, (std::max)(1, bounds.h - pad * 2) };
}

Rect Scrollbar::thumb_rect() const {
    Rect track = track_rect();
    if (orientation == 0) {
        int min_thumb = (std::min)(54, (std::max)(28, track.w / 6));
        int proportional = max_value > 0 ? (int)((double)track.w * page_size / (max_value + page_size) + 0.5) : track.w;
        int thumb_w = (std::min)(track.w, (std::max)(min_thumb, proportional));
        int travel = (std::max)(0, track.w - thumb_w);
        int x = track.x + (max_value > 0 ? (int)((double)travel * value / max_value + 0.5) : 0);
        return { x, track.y, thumb_w, track.h };
    }
    int min_thumb = (std::min)(54, (std::max)(28, track.h / 6));
    int proportional = max_value > 0 ? (int)((double)track.h * page_size / (max_value + page_size) + 0.5) : track.h;
    int thumb_h = (std::min)(track.h, (std::max)(min_thumb, proportional));
    int travel = (std::max)(0, track.h - thumb_h);
    int y = track.y + (max_value > 0 ? (int)((double)travel * value / max_value + 0.5) : 0);
    return { track.x, y, track.w, thumb_h };
}

void Scrollbar::update_from_point(int x, int y) {
    Rect track = track_rect();
    Rect thumb = thumb_rect();
    int travel = orientation == 0 ? track.w - thumb.w : track.h - thumb.h;
    if (travel <= 0) {
        set_value(0);
        return;
    }

    int pos = orientation == 0 ? x - track.x - m_drag_offset
                               : y - track.y - m_drag_offset;
    if (pos < 0) pos = 0;
    if (pos > travel) pos = travel;
    set_value((int)((double)max_value * pos / travel + 0.5));
}

void Scrollbar::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    if (auto_hide && max_value <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    if (style.bg_color) {
        D2D1_RECT_F bg = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(bg, ctx.get_brush(style.bg_color));
    }

    Rect track_r = track_rect();
    Rect thumb_r = thumb_rect();
    D2D1_RECT_F track = {
        (float)track_r.x, (float)track_r.y,
        (float)(track_r.x + track_r.w), (float)(track_r.y + track_r.h)
    };
    D2D1_RECT_F thumb = {
        (float)thumb_r.x, (float)thumb_r.y,
        (float)(thumb_r.x + thumb_r.w), (float)(thumb_r.y + thumb_r.h)
    };
    float track_radius = orientation == 0 ? track_r.h * 0.5f : track_r.w * 0.5f;
    float thumb_radius = orientation == 0 ? thumb_r.h * 0.5f : thumb_r.w * 0.5f;

    Color track_color = dark ? with_alpha(0xFFFFFFFF, 0x12) : with_alpha(0xFF000000, 0x0A);
    Color thumb_color = pressed ? t->accent
        : (hovered ? with_alpha(t->accent, 0xCC) : with_alpha(t->text_secondary, dark ? 0xAA : 0x90));
    ctx.rt->FillRoundedRectangle(ROUNDED(track, track_radius, track_radius),
                                 ctx.get_brush(track_color));
    ctx.rt->FillRoundedRectangle(ROUNDED(thumb, thumb_radius, thumb_radius),
                                 ctx.get_brush(thumb_color));

    ctx.rt->SetTransform(saved);
}

void Scrollbar::on_mouse_enter() {
    hovered = true;
    invalidate();
}

void Scrollbar::on_mouse_leave() {
    hovered = false;
    if (!pressed) invalidate();
}

void Scrollbar::on_mouse_down(int x, int y, MouseButton) {
    Rect thumb = thumb_rect();
    pressed = true;
    m_drag_start_value = value;
    if (thumb.contains(x, y)) {
        m_drag_offset = orientation == 0 ? x - thumb.x : y - thumb.y;
    } else {
        m_drag_offset = orientation == 0 ? thumb.w / 2 : thumb.h / 2;
        update_from_point(x, y);
        last_action = 5;
    }
    invalidate();
}

void Scrollbar::on_mouse_up(int x, int y, MouseButton) {
    if (pressed) update_from_point(x, y);
    if (value != m_drag_start_value) {
        ++drag_event_count;
        last_action = 4;
    }
    pressed = false;
    m_drag_offset = 0;
    invalidate();
}

void Scrollbar::on_mouse_move(int x, int y) {
    if (pressed) update_from_point(x, y);
}

void Scrollbar::on_mouse_wheel(int, int, int delta) {
    wheel_delta(delta);
}

void Scrollbar::on_key_down(int vk, int) {
    switch (vk) {
    case VK_LEFT:
    case VK_UP:
        update_value(value - 5, 7);
        break;
    case VK_RIGHT:
    case VK_DOWN:
        update_value(value + 5, 7);
        break;
    case VK_PRIOR:
        update_value(value - page_size, 7);
        break;
    case VK_NEXT:
        update_value(value + page_size, 7);
        break;
    case VK_HOME:
        update_value(0, 7);
        break;
    case VK_END:
        update_value(max_value, 7);
        break;
    default:
        break;
    }
}
