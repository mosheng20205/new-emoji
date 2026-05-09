#include "element_skeleton.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <map>
#include <windows.h>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

std::map<UINT_PTR, Skeleton*> g_skeleton_timer_map;

static int round_px(float v) {
    return (int)std::lround(v);
}

static Color with_alpha(Color color, unsigned char alpha) {
    return ((Color)alpha << 24) | (color & 0x00FFFFFF);
}

Skeleton::~Skeleton() {
    stop_timer();
}

void Skeleton::set_rows(int value) {
    if (value < 1) value = 1;
    if (value > 12) value = 12;
    rows = value;
    invalidate();
}

void Skeleton::set_animated(bool value) {
    animated = value;
    if (animated && loading) ensure_timer();
    else stop_timer();
    invalidate();
}

void Skeleton::set_loading(bool value) {
    loading = value;
    if (animated && loading) ensure_timer();
    else stop_timer();
    invalidate();
}

void Skeleton::set_options(int rows_value, bool animated_value, bool loading_value, bool show_avatar_value) {
    set_rows(rows_value);
    animated = animated_value;
    loading = loading_value;
    show_avatar = show_avatar_value;
    if (animated && loading) ensure_timer();
    else stop_timer();
    invalidate();
}

void Skeleton::tick(int elapsed_ms) {
    if (!animated || !loading || !visible) {
        stop_timer();
        return;
    }

    ULONGLONG now = GetTickCount64();
    int actual_elapsed = elapsed_ms;
    if (last_animation_tick != 0) {
        ULONGLONG delta = now - last_animation_tick;
        if (delta > 0 && delta < 250) actual_elapsed = (int)delta;
    }
    last_animation_tick = now;

    const float animation_ms = 1450.0f;
    animation_phase += (float)(std::max)(1, actual_elapsed) / animation_ms;
    animation_phase = std::fmod(animation_phase, 1.0f);
    invalidate();
}

void Skeleton::ensure_timer() {
    if (m_timer_id || !owner_hwnd || !animated || !loading) return;
    UINT_PTR timer_id = 0x5A00 + (UINT_PTR)id;
    last_animation_tick = GetTickCount64();
    m_timer_id = SetTimer(owner_hwnd, timer_id, 16, nullptr);
    if (m_timer_id) g_skeleton_timer_map[m_timer_id] = this;
}

void Skeleton::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_skeleton_timer_map.erase(m_timer_id);
    m_timer_id = 0;
    last_animation_tick = 0;
}

void Skeleton::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    if (animated && loading) ensure_timer();
    else stop_timer();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color base = style.bg_color ? style.bg_color : (dark ? 0xFF313244 : 0xFFE9ECF2);
    Color shine = dark ? 0xFF565A70 : 0xFFFFFFFF;
    float phase = animated ? animation_phase : 0.18f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    if (!loading) {
        const Theme* t = theme_for_window(owner_hwnd);
        D2D1_RECT_F done = { (float)style.pad_left, (float)style.pad_top,
                             (float)bounds.w - (float)style.pad_right,
                             (float)bounds.h - (float)style.pad_bottom };
        ctx.rt->FillRoundedRectangle(ROUNDED(done, 6.0f, 6.0f), ctx.get_brush(dark ? 0xFF242637 : 0xFFFFFFFF));
        ctx.rt->DrawRoundedRectangle(ROUNDED(done, 6.0f, 6.0f), ctx.get_brush(t->border_default), 1.0f);
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }

    float pad_l = (float)style.pad_left;
    float pad_r = (float)style.pad_right;
    float pad_t = (float)style.pad_top;
    float row_h = (std::max)(10.0f, style.font_size * 0.9f);
    float gap = (std::max)(8.0f, style.font_size * 0.65f);
    float avatar_size = (std::min)(style.font_size * 2.6f, (float)bounds.h - pad_t * 2.0f);
    if (avatar_size < 24.0f) avatar_size = 24.0f;
    float content_x = pad_l + avatar_size + 14.0f;
    float content_w = (float)bounds.w - content_x - pad_r;
    if (content_w < 24.0f) {
        content_x = pad_l;
        content_w = (float)bounds.w - pad_l - pad_r;
        avatar_size = 0.0f;
    }

    if (!show_avatar) {
        avatar_size = 0.0f;
        content_x = pad_l;
        content_w = (float)bounds.w - pad_l - pad_r;
    }

    if (avatar_size > 0.0f) {
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(pad_l + avatar_size * 0.5f,
                                                        pad_t + avatar_size * 0.5f),
                                          avatar_size * 0.5f, avatar_size * 0.5f),
                            ctx.get_brush(base));
    }

    for (int i = 0; i < rows; ++i) {
        float y = pad_t + (row_h + gap) * (float)i;
        if (y + row_h > bounds.h - style.pad_bottom) break;
        float ratio = (i == rows - 1) ? 0.62f : (i == 0 ? 0.92f : 0.82f);
        float w = content_w * ratio;
        D2D1_RECT_F r = { content_x, y, content_x + w, y + row_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(r, row_h * 0.5f, row_h * 0.5f), ctx.get_brush(base));
        if (animated) {
            float sw = (std::min)((std::max)(w * 0.42f, 54.0f), 96.0f);
            float sx = r.left - sw + (w + sw * 2.0f) * phase;
            float side_w = sw * 0.45f;
            float core_w = sw * 0.34f;
            D2D1_RECT_F left = { sx, r.top, sx + side_w, r.bottom };
            D2D1_RECT_F core = { sx + side_w * 0.72f, r.top, sx + side_w * 0.72f + core_w, r.bottom };
            D2D1_RECT_F right = { sx + sw - side_w, r.top, sx + sw, r.bottom };
            float radius = row_h * 0.5f;
            ctx.rt->FillRoundedRectangle(ROUNDED(left, radius, radius),
                                         ctx.get_brush(with_alpha(shine, dark ? 0x2A : 0x42)));
            ctx.rt->FillRoundedRectangle(ROUNDED(core, radius, radius),
                                         ctx.get_brush(with_alpha(shine, dark ? 0x4A : 0x72)));
            ctx.rt->FillRoundedRectangle(ROUNDED(right, radius, radius),
                                         ctx.get_brush(with_alpha(shine, dark ? 0x22 : 0x34)));
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
