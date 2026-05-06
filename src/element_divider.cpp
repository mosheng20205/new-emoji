#include "element_divider.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

static int clamp_int(int value, int min_value, int max_value) {
    return (std::max)(min_value, (std::min)(max_value, value));
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

std::wstring Divider::display_text() const {
    if (content_icon.empty()) return text;
    if (text.empty()) return content_icon;
    return content_icon + L" " + text;
}

void Divider::apply_dpi_scale(float scale) {
    Element::apply_dpi_scale(scale);
    if (scale <= 0.0f) scale = 1.0f;
    line_width = logical_line_width > 0.0f ? logical_line_width * scale : 1.0f * scale;
    line_margin = (int)std::lround((float)logical_line_margin * scale);
    text_gap = (int)std::lround((float)logical_text_gap * scale);
}

void Divider::set_direction(int value) {
    direction = value == 1 ? 1 : 0;
    invalidate();
}

void Divider::set_content_position(int value) {
    if (value < 0) value = 0;
    if (value > 2) value = 2;
    content_position = value;
    invalidate();
}

void Divider::set_line_style(int value) {
    line_style = clamp_int(value, 0, 3);
    dashed = line_style == 1;
    invalidate();
}

void Divider::set_options(int new_direction, int position, Color color, float width, int dash, const std::wstring& label) {
    set_direction(new_direction);
    set_content_position(position);
    text = label;
    content_icon.clear();
    logical_line_width = width > 0.0f ? width : 1.0f;
    line_width = logical_line_width;
    set_line_style(dash != 0 ? 1 : 0);
    if (has_logical_style) {
        logical_style.border_color = color;
    } else {
        style.border_color = color;
    }
    invalidate();
}

void Divider::get_options(int& out_direction, int& position, Color& color, float& width, int& dash) const {
    const ElementStyle& s = has_logical_style ? logical_style : style;
    out_direction = direction;
    position = content_position;
    color = s.border_color;
    width = logical_line_width;
    dash = dashed ? 1 : 0;
}

void Divider::set_spacing(int margin, int gap) {
    logical_line_margin = clamp_int(margin, 0, 96);
    logical_text_gap = clamp_int(gap, 0, 40);
    line_margin = logical_line_margin;
    text_gap = logical_text_gap;
    invalidate();
}

void Divider::get_spacing(int& margin, int& gap) const {
    margin = logical_line_margin;
    gap = logical_text_gap;
}

void Divider::set_content(const std::wstring& icon, const std::wstring& label) {
    content_icon = icon;
    text = label;
    invalidate();
}

void Divider::get_content(std::wstring& icon, std::wstring& label) const {
    icon = content_icon;
    label = text;
}

static void draw_line(RenderContext& ctx, D2D1_POINT_2F a, D2D1_POINT_2F b,
                      ID2D1Brush* brush, float width, int line_style) {
    bool horizontal = fabsf(a.y - b.y) < 0.1f;
    float start = horizontal ? a.x : a.y;
    float end = horizontal ? b.x : b.y;
    if (end < start) std::swap(start, end);
    if (end - start <= 0.5f || width <= 0.0f) return;

    if (line_style == 3) {
        float offset = (std::max)(2.0f, width + 2.0f);
        if (horizontal) {
            ctx.rt->DrawLine(D2D1::Point2F(start, a.y - offset), D2D1::Point2F(end, a.y - offset), brush, width);
            ctx.rt->DrawLine(D2D1::Point2F(start, a.y + offset), D2D1::Point2F(end, a.y + offset), brush, width);
        } else {
            ctx.rt->DrawLine(D2D1::Point2F(a.x - offset, start), D2D1::Point2F(a.x - offset, end), brush, width);
            ctx.rt->DrawLine(D2D1::Point2F(a.x + offset, start), D2D1::Point2F(a.x + offset, end), brush, width);
        }
        return;
    }

    if (line_style == 0) {
        ctx.rt->DrawLine(a, b, brush, width);
        return;
    }

    float dash = line_style == 2 ? (std::max)(width, 2.0f) : 8.0f;
    float gap = line_style == 2 ? (std::max)(width * 2.2f, 4.0f) : 5.0f;
    for (float p = start; p < end; p += dash + gap) {
        float q = (std::min)(p + dash, end);
        if (horizontal) {
            ctx.rt->DrawLine(D2D1::Point2F(p, a.y), D2D1::Point2F(q, a.y), brush, width);
        } else {
            ctx.rt->DrawLine(D2D1::Point2F(a.x, p), D2D1::Point2F(a.x, q), brush, width);
        }
    }
}

void Divider::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color line = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float stroke = (std::max)(1.0f, line_width);
    int draw_style = clamp_int(line_style, 0, 3);

    if (direction == 1) {
        float x = (float)bounds.w * 0.5f;
        draw_line(ctx, D2D1::Point2F(x, (float)style.pad_top + (float)line_margin),
                  D2D1::Point2F(x, (float)bounds.h - style.pad_bottom - (float)line_margin),
                  ctx.get_brush(line), stroke, draw_style);
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }

    float y = (float)bounds.h * 0.5f;
    float start_x = (float)style.pad_left + (float)line_margin;
    float end_x = (float)bounds.w - (float)style.pad_right - (float)line_margin;
    if (end_x < start_x) end_x = start_x;
    std::wstring content = display_text();
    if (content.empty()) {
        draw_line(ctx, D2D1::Point2F(start_x, y),
                  D2D1::Point2F(end_x, y),
                  ctx.get_brush(line), stroke, draw_style);
    } else {
        float text_w = (std::min)((float)bounds.w * 0.70f, (float)content.size() * style.font_size * 0.72f + 32.0f);
        float text_h = (std::max)(style.font_size * 1.7f, 24.0f);
        float text_x = ((float)bounds.w - text_w) * 0.5f;
        if (content_position == 0) text_x = (float)style.pad_left + 24.0f;
        if (content_position == 2) text_x = (float)bounds.w - style.pad_right - 24.0f - text_w;
        if (text_x < style.pad_left) text_x = (float)style.pad_left;
        if (text_x + text_w > bounds.w - style.pad_right) text_x = (float)bounds.w - style.pad_right - text_w;

        float gap = (float)text_gap;
        draw_line(ctx, D2D1::Point2F(start_x, y),
                  D2D1::Point2F(text_x - gap, y), ctx.get_brush(line), stroke, draw_style);
        draw_line(ctx, D2D1::Point2F(text_x + text_w + gap, y),
                  D2D1::Point2F(end_x, y), ctx.get_brush(line), stroke, draw_style);
        draw_text(ctx, content, style, fg, text_x, y - text_h * 0.5f, text_w, text_h);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
