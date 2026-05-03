#include "element_metrics.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color status_color(const Theme* t, int status) {
    switch (status) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    case 4: return 0xFF909399;
    default: return t->accent;
    }
}

static Color trend_color(const Theme* t, int trend_type) {
    if (trend_type > 0) return 0xFF67C23A;
    if (trend_type < 0) return 0xFFF56C6C;
    return t->text_secondary;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static void draw_card_shell(RenderContext& ctx, HWND hwnd, const Element& el, Color accent) {
    const Theme* t = theme_for_window(hwnd);
    bool dark = is_dark_theme_for_window(hwnd);
    Color bg = el.style.bg_color ? el.style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = el.style.border_color ? el.style.border_color : t->border_default;
    float radius = el.style.corner_radius > 0.0f ? el.style.corner_radius : 6.0f;
    D2D1_RECT_F rect = { 0, 0, (float)el.bounds.w, (float)el.bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)el.bounds.w - 0.5f, (float)el.bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);
    ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(0.0f, 0.0f, 5.0f, (float)el.bounds.h),
        radius, radius), ctx.get_brush(accent));
}

void KpiCard::set_title(const std::wstring& next_title) {
    title = next_title;
    invalidate();
}

void KpiCard::set_value(const std::wstring& next_value) {
    value = next_value;
    text = next_value;
    invalidate();
}

void KpiCard::set_subtitle(const std::wstring& next_subtitle) {
    subtitle = next_subtitle;
    invalidate();
}

void KpiCard::set_trend(const std::wstring& next_trend, int next_type) {
    trend = next_trend;
    trend_type = (std::max)(-1, (std::min)(1, next_type));
    invalidate();
}

void KpiCard::set_options(bool loading_value, const std::wstring& helper_text) {
    loading = loading_value;
    helper = helper_text;
    invalidate();
}

void KpiCard::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color accent = trend_color(t, trend_type);
    Color title_fg = t->text_secondary;
    Color value_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color sub_fg = t->text_muted;

    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    draw_card_shell(ctx, owner_hwnd, *this, accent);

    if (loading) {
        Color shimmer = with_alpha(t->text_secondary, is_dark_theme_for_window(owner_hwnd) ? 0x24 : 0x18);
        float sx = (float)style.pad_left + 9.0f;
        float sw = (float)bounds.w - sx - (float)style.pad_right;
        for (int i = 0; i < 3; ++i) {
            float sy = (float)style.pad_top + 8.0f + (float)i * 28.0f;
            float width = sw * (i == 1 ? 0.72f : 0.92f);
            ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(sx, sy, sx + width, sy + 14.0f),
                7.0f, 7.0f), ctx.get_brush(shimmer));
        }
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }

    float x = (float)style.pad_left + 5.0f;
    float y = (float)style.pad_top;
    float w = (float)bounds.w - x - (float)style.pad_right;
    if (w < 1.0f) w = 1.0f;

    draw_text(ctx, title.empty() ? L"指标" : title, style, title_fg,
              x, y, w, 22.0f * style.font_size / 14.0f, 0.92f);

    float value_scale = bounds.w < 170 ? 1.55f : 1.85f;
    draw_text(ctx, value.empty() ? L"0" : value, style, value_fg,
              x, y + 28.0f * style.font_size / 14.0f, w, 42.0f * style.font_size / 14.0f,
              value_scale, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    float chip_h = (std::max)(20.0f, style.font_size * 1.45f);
    float chip_w = trend.empty() ? 0.0f : (std::min)(w, (float)trend.size() * style.font_size * 0.72f + 30.0f);
    float bottom_y = (float)bounds.h - (float)style.pad_bottom - chip_h;
    if (chip_w > 0.0f) {
        D2D1_RECT_F chip = { x, bottom_y, x + chip_w, bottom_y + chip_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(chip, chip_h * 0.5f, chip_h * 0.5f),
                                     ctx.get_brush(with_alpha(accent, is_dark_theme_for_window(owner_hwnd) ? 0x30 : 0x18)));
        std::wstring arrow = trend_type > 0 ? L"↑ " : (trend_type < 0 ? L"↓ " : L"• ");
        draw_text(ctx, arrow + trend, style, accent, x + 9.0f, bottom_y, chip_w - 12.0f, chip_h, 0.9f);
    }
    float sub_x = chip_w > 0.0f ? x + chip_w + 8.0f : x;
    draw_text(ctx, subtitle, style, sub_fg, sub_x, bottom_y,
              (std::max)(1.0f, x + w - sub_x), chip_h, 0.86f);
    if (!helper.empty()) {
        draw_text(ctx, helper, style, sub_fg, x, bottom_y - chip_h - 4.0f,
                  w, chip_h, 0.8f, DWRITE_FONT_WEIGHT_NORMAL,
                  DWRITE_TEXT_ALIGNMENT_TRAILING);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Trend::set_title(const std::wstring& next_title) {
    title = next_title;
    invalidate();
}

void Trend::set_value(const std::wstring& next_value) {
    value = next_value;
    text = next_value;
    invalidate();
}

void Trend::set_percent(const std::wstring& next_percent) {
    percent = next_percent;
    invalidate();
}

void Trend::set_detail(const std::wstring& next_detail) {
    detail = next_detail;
    invalidate();
}

void Trend::set_direction(int next_direction) {
    direction = (std::max)(-1, (std::min)(1, next_direction));
    invalidate();
}

void Trend::set_options(bool inverse_value, bool show_icon_value) {
    inverse = inverse_value;
    show_icon = show_icon_value;
    invalidate();
}

void Trend::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    int visual_direction = inverse ? -direction : direction;
    Color accent = trend_color(t, visual_direction);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;

    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float icon = (std::max)(28.0f, style.font_size * 2.2f);
    float x = (float)style.pad_left;
    if (show_icon) {
        float cx = (float)style.pad_left + icon * 0.5f;
        float cy = (float)bounds.h * 0.5f;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), icon * 0.5f, icon * 0.5f),
                            ctx.get_brush(with_alpha(accent, dark ? 0x2F : 0x1B)));
        std::wstring arrow = direction > 0 ? L"↑" : (direction < 0 ? L"↓" : L"•");
        draw_text(ctx, arrow, style, accent, cx - icon * 0.35f, cy - icon * 0.36f,
                  icon * 0.7f, icon * 0.72f, 1.45f, DWRITE_FONT_WEIGHT_SEMI_BOLD,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
        x += icon + 12.0f;
    }
    float right = (float)bounds.w - (float)style.pad_right;
    float main_w = (std::max)(1.0f, right - x);
    draw_text(ctx, title.empty() ? L"趋势" : title, style, muted, x, 8.0f, main_w, 20.0f, 0.88f);
    draw_text(ctx, value.empty() ? L"0" : value, style, fg, x, 31.0f, main_w * 0.55f, 34.0f,
              1.45f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, percent, style, accent, x + main_w * 0.55f, 33.0f, main_w * 0.45f, 30.0f,
              1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD, DWRITE_TEXT_ALIGNMENT_TRAILING);
    draw_text(ctx, detail, style, muted, x, 66.0f, main_w, 22.0f, 0.86f);

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void StatusDot::set_label(const std::wstring& next_label) {
    label = next_label;
    text = next_label;
    invalidate();
}

void StatusDot::set_description(const std::wstring& next_description) {
    description = next_description;
    invalidate();
}

void StatusDot::set_status(int next_status) {
    if (next_status < 0) next_status = 0;
    if (next_status > 4) next_status = 4;
    status = next_status;
    invalidate();
}

void StatusDot::set_options(bool pulse_value, bool compact_value) {
    pulse = pulse_value;
    compact = compact_value;
    invalidate();
}

void StatusDot::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color accent = status_color(t, status);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;

    float dot = (std::max)(8.0f, style.font_size * (compact ? 0.58f : 0.72f));
    float cx = (float)style.pad_left + dot * 0.5f;
    float cy = description.empty() ? (float)bounds.h * 0.5f : (float)style.pad_top + style.font_size * 0.95f;
    if (pulse) {
        float phase = (float)((GetTickCount64() / 16ULL) % 90ULL) / 90.0f;
        float wave = 0.5f + 0.5f * std::sin(phase * 6.2831853f);
        float radius = dot * (1.08f + wave * 0.58f);
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), radius, radius),
                            ctx.get_brush(with_alpha(accent, 0x20)));
        if (owner_hwnd) SetTimer(owner_hwnd, 0x5000 + id, 33, nullptr);
    } else if (owner_hwnd) {
        KillTimer(owner_hwnd, 0x5000 + id);
    }
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), dot * 0.5f, dot * 0.5f),
                        ctx.get_brush(accent));
    ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), dot * 0.95f, dot * 0.95f),
                        ctx.get_brush(with_alpha(accent, 0x44)), 1.0f);

    float x = (float)style.pad_left + dot + 9.0f;
    float w = (float)bounds.w - x - (float)style.pad_right;
    draw_text(ctx, label.empty() ? L"状态" : label, style, fg,
              x, (float)style.pad_top, (std::max)(1.0f, w),
              description.empty() ? (float)bounds.h - style.pad_top - style.pad_bottom : style.font_size * 1.45f,
              compact ? 0.9f : 1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    if (!description.empty() && !compact) {
        draw_text(ctx, description, style, muted, x,
                  (float)style.pad_top + style.font_size * 1.45f,
                  (std::max)(1.0f, w), (float)bounds.h - style.pad_top - style.pad_bottom - style.font_size * 1.45f,
                  0.86f);
    }

    ctx.rt->SetTransform(saved);
}
