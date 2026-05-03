#include "element_badge.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwctype>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
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

static bool parse_positive_int(const std::wstring& value, int& out) {
    if (value.empty()) return false;
    int total = 0;
    for (wchar_t ch : value) {
        if (!iswdigit(ch)) return false;
        total = total * 10 + (ch - L'0');
        if (total > 1000000) return false;
    }
    out = total;
    return true;
}

void Badge::set_value(const std::wstring& value_text) {
    value = value_text;
    hidden = is_hidden();
    invalidate();
}

void Badge::set_max_value(int new_value) {
    if (new_value < 0) new_value = 0;
    max_value = new_value;
    invalidate();
}

void Badge::set_dot(bool new_value) {
    dot = new_value;
    hidden = is_hidden();
    invalidate();
}

void Badge::set_options(bool dot_value, bool show_zero_value, int offset_x_value, int offset_y_value) {
    dot = dot_value;
    show_zero = show_zero_value;
    offset_x = offset_x_value;
    offset_y = offset_y_value;
    hidden = is_hidden();
    invalidate();
}

void Badge::set_layout_options(int placement_value, bool standalone_value) {
    if (placement_value < 0) placement_value = 0;
    if (placement_value > 3) placement_value = 3;
    placement = placement_value;
    standalone = standalone_value;
    invalidate();
}

bool Badge::is_hidden() const {
    if (dot) return false;
    if (value.empty()) return true;
    int numeric = 0;
    return !show_zero && parse_positive_int(value, numeric) && numeric == 0;
}

std::wstring Badge::display_value() const {
    if (dot) return L"";
    int numeric = 0;
    if (max_value > 0 && parse_positive_int(value, numeric) && numeric > max_value) {
        return std::to_wstring(max_value) + L"+";
    }
    return value;
}

Rect Badge::badge_rect(const std::wstring& badge_text) const {
    float badge_h = dot ? (float)(std::min)(bounds.h, 10) : (std::min)((float)bounds.h, style.font_size * 1.55f);
    if (badge_h < 8.0f) badge_h = 8.0f;
    float badge_w = badge_h;
    if (!dot) {
        badge_w = (float)(std::max)((int)badge_h, (int)(badge_text.size() * style.font_size * 0.68f + style.font_size));
        if (!standalone && badge_w > bounds.w * 0.55f) badge_w = bounds.w * 0.55f;
        if (standalone && badge_w > bounds.w - 2.0f) badge_w = bounds.w - 2.0f;
    }
    float x = 1.0f;
    float y = 1.0f;
    switch (placement) {
    case 1:
        x = 1.0f;
        y = 1.0f;
        break;
    case 2:
        x = (float)bounds.w - badge_w - 1.0f;
        y = (float)bounds.h - badge_h - 1.0f;
        break;
    case 3:
        x = 1.0f;
        y = (float)bounds.h - badge_h - 1.0f;
        break;
    default:
        x = (float)bounds.w - badge_w - 1.0f;
        y = 1.0f;
        break;
    }
    x += (float)offset_x;
    y += (float)offset_y;
    return { (int)x, (int)y, (int)badge_w, (int)badge_h };
}

void Badge::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color badge_bg = style.bg_color ? style.bg_color : 0xFFF56C6C;
    Color badge_fg = 0xFFFFFFFF;

    std::wstring badge_text = display_value();
    if (is_hidden()) badge_text.clear();
    Rect br = badge_rect(badge_text);
    float badge_x = (float)br.x;
    float badge_y = (float)br.y;
    float badge_w = (float)br.w;
    float badge_h = (float)br.h;
    float label_right = standalone ? (float)bounds.w : badge_x - 6.0f;

    if (!standalone && !text.empty()) {
        float text_w = label_right - (float)style.pad_left;
        if (text_w < 1.0f) text_w = 1.0f;
        draw_text(ctx, text, style, fg, (float)style.pad_left, 0.0f, text_w, (float)bounds.h);
    }

    if (dot) {
        float r = badge_h * 0.5f;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(badge_x + r, badge_y + r), r, r),
                            ctx.get_brush(badge_bg));
    } else if (!badge_text.empty()) {
        D2D1_RECT_F pill = { badge_x, badge_y, badge_x + badge_w, badge_y + badge_h };
        float radius = badge_h * 0.5f;
        ctx.rt->FillRoundedRectangle(ROUNDED(pill, radius, radius), ctx.get_brush(badge_bg));
        draw_text(ctx, badge_text, style, badge_fg, badge_x, badge_y, badge_w, badge_h,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    ctx.rt->SetTransform(saved);
}
