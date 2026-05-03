#include "element_statistic.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwchar>
#include <iomanip>
#include <sstream>

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
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

void Statistic::set_title(const std::wstring& value) {
    title = value;
    invalidate();
}

void Statistic::set_value(const std::wstring& next_value) {
    value = next_value;
    text = next_value;
    wchar_t* end = nullptr;
    double parsed = std::wcstod(value.c_str(), &end);
    if (end != value.c_str()) {
        target_value = parsed;
        reset_animation();
    }
    invalidate();
}

void Statistic::set_prefix(const std::wstring& next_value) {
    prefix = next_value;
    invalidate();
}

void Statistic::set_suffix(const std::wstring& next_value) {
    suffix = next_value;
    invalidate();
}

void Statistic::set_format(const std::wstring& title_value,
                           const std::wstring& prefix_value,
                           const std::wstring& suffix_value) {
    title = title_value;
    prefix = prefix_value;
    suffix = suffix_value;
    invalidate();
}

void Statistic::set_options(int precision_value, bool animated_value) {
    if (precision_value < -1) precision_value = -1;
    if (precision_value > 6) precision_value = 6;
    precision = precision_value;
    animated = animated_value;
    reset_animation();
    invalidate();
}

void Statistic::reset_animation() {
    if (!animated) {
        display_value = target_value;
        anim_start = 0;
        return;
    }
    anim_start = GetTickCount64();
}

std::wstring Statistic::display_number() const {
    if (precision < 0) return value.empty() ? text : value;
    double shown = display_value;
    std::wostringstream ss;
    ss << std::fixed << std::setprecision(precision) << shown;
    return ss.str();
}

void Statistic::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = t->text_secondary;
    Color value_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color accent = t->accent;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ rect, radius, radius }, ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(D2D1_ROUNDED_RECT{
        D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f),
        radius, radius }, ctx.get_brush(border), 1.0f);

    float x = (float)style.pad_left;
    float y = (float)style.pad_top;
    float w = (float)bounds.w - style.pad_left - style.pad_right;
    if (w < 1.0f) w = 1.0f;
    float title_h = (std::max)(style.font_size * 1.45f, 20.0f);
    draw_text(ctx, title.empty() ? L"Statistic" : title, style, title_fg,
              x, y, w, title_h, 0.92f);

    if (precision >= 0 && animated && anim_start != 0) {
        ULONGLONG elapsed = GetTickCount64() - anim_start;
        float p = (std::min)(1.0f, (float)elapsed / 320.0f);
        display_value = target_value * (1.0 - (1.0 - p) * (1.0 - p));
        if (p < 1.0f) invalidate();
    } else if (precision >= 0) {
        display_value = target_value;
    }
    std::wstring display = prefix + display_number() + suffix;
    float value_h = (float)bounds.h - y - title_h - style.pad_bottom;
    if (value_h < style.font_size * 2.0f) value_h = style.font_size * 2.0f;
    float value_scale = bounds.w < 130 ? 1.45f : 1.8f;
    draw_text(ctx, display, style, value_fg,
              x, y + title_h + 2.0f, w, value_h,
              value_scale, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    ctx.rt->FillRectangle(D2D1::RectF(0.0f, 0.0f, 4.0f, (float)bounds.h),
                          ctx.get_brush(accent));

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
