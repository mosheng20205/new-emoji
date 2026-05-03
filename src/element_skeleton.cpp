#include "element_skeleton.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <windows.h>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

void Skeleton::set_rows(int value) {
    if (value < 1) value = 1;
    if (value > 12) value = 12;
    rows = value;
    invalidate();
}

void Skeleton::set_animated(bool value) {
    animated = value;
    invalidate();
}

void Skeleton::set_loading(bool value) {
    loading = value;
    invalidate();
}

void Skeleton::set_options(int rows_value, bool animated_value, bool loading_value, bool show_avatar_value) {
    set_rows(rows_value);
    animated = animated_value;
    loading = loading_value;
    show_avatar = show_avatar_value;
    invalidate();
}

void Skeleton::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color base = style.bg_color ? style.bg_color : (dark ? 0xFF313244 : 0xFFE9ECF2);
    Color shine = dark ? 0xFF3B3E51 : 0xFFF4F6FA;
    ULONGLONG now = GetTickCount64();
    float phase = animated ? (float)((now / 16) % 120) / 120.0f : 0.18f;

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
            float sw = (std::min)(w * 0.28f, 64.0f);
            float sx = r.left - sw + (w + sw * 2.0f) * phase;
            D2D1_RECT_F s = { sx, r.top, sx + sw, r.bottom };
            ctx.rt->FillRoundedRectangle(ROUNDED(s, row_h * 0.5f, row_h * 0.5f), ctx.get_brush(shine));
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
    if (animated && loading && now - last_animation_tick >= 33) {
        last_animation_tick = now;
        invalidate();
    }
}
