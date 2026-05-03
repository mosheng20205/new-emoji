#include "element_loading.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <map>

std::map<UINT_PTR, Loading*> g_loading_timer_map;

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
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

Loading::~Loading() {
    stop_timer();
}

void Loading::set_active(bool value) {
    active = value;
    last_action = 1;
    if (active) ensure_timer();
    else stop_timer();
    invalidate();
}

void Loading::set_options(bool value, bool full, int percent) {
    active = value;
    fullscreen = full;
    if (percent < 0) progress = -1;
    else if (percent > 100) progress = 100;
    else progress = percent;
    last_action = 1;
    if (active) ensure_timer();
    else stop_timer();
    invalidate();
}

void Loading::set_target(int id, int padding) {
    target_id = (std::max)(0, id);
    target_padding = (std::max)(0, padding);
    last_action = 1;
    invalidate();
}

void Loading::tick(int elapsed_ms) {
    if (!active) {
        stop_timer();
        return;
    }
    int step = (std::max)(1, elapsed_ms) * 360 / 900;
    if (step <= 0) step = 1;
    animation_angle = (animation_angle + step) % 360;
    ++tick_count;
    last_action = 2;
    invalidate();
}

void Loading::ensure_timer() {
    if (m_timer_id || !owner_hwnd || !active) return;
    m_timer_id = 0xE000 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 33, nullptr);
    if (m_timer_id) g_loading_timer_map[m_timer_id] = this;
}

void Loading::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_loading_timer_map.erase(m_timer_id);
    m_timer_id = 0;
}

void Loading::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    if (active) ensure_timer();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color overlay = style.bg_color ? style.bg_color : (dark ? 0x66181825 : 0x66FFFFFF);
    Color accent = style.border_color ? style.border_color : t->accent;
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    if (fullscreen) overlay = dark ? 0xAA11131C : 0xAAFFFFFF;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    ctx.rt->FillRectangle(clip, ctx.get_brush(overlay));

    float cx = (float)bounds.w * 0.5f;
    float cy = (float)bounds.h * 0.5f - style.font_size * 0.65f;
    float radius = (std::min)((float)bounds.w, (float)bounds.h) * 0.16f;
    if (radius < 14.0f) radius = 14.0f;
    if (radius > 28.0f) radius = 28.0f;

    if (active) {
        for (int i = 0; i < 8; ++i) {
            float angle = 6.2831853f * ((float)i / 8.0f + (float)animation_angle / 360.0f);
            float px = cx + std::cos(angle) * radius;
            float py = cy + std::sin(angle) * radius;
            float dot = (std::max)(3.0f, style.font_size * 0.23f);
            unsigned alpha = 0x44 + (unsigned)(i * 0x16);
            if (alpha > 0xFF) alpha = 0xFF;
            ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(px, py), dot, dot),
                                ctx.get_brush(with_alpha(accent, alpha)));
        }
    } else {
        ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), radius, radius),
                            ctx.get_brush(t->border_default), 1.4f);
    }

    std::wstring label = text.empty() ? (active ? L"Loading" : L"Loaded") : text;
    if (progress >= 0) label += L" " + std::to_wstring(progress) + L"%";
    draw_text(ctx, label, style, fg,
              (float)style.pad_left, cy + radius + 8.0f,
              (float)bounds.w - style.pad_left - style.pad_right,
              style.font_size * 1.7f);
    if (progress >= 0) {
        float bar_w = (std::min)(220.0f, (float)bounds.w - style.pad_left - style.pad_right);
        float x = ((float)bounds.w - bar_w) * 0.5f;
        float y = cy + radius + 8.0f + style.font_size * 1.8f;
        D2D1_RECT_F track = { x, y, x + bar_w, y + 6.0f };
        D2D1_RECT_F fill = { x, y, x + bar_w * (float)progress / 100.0f, y + 6.0f };
        ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ track, 3.0f, 3.0f },
                                     ctx.get_brush(with_alpha(fg, 0x22)));
        ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ fill, 3.0f, 3.0f },
                                     ctx.get_brush(accent));
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
