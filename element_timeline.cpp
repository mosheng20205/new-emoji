#include "element_timeline.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

static Color type_color(const Theme* t, int type) {
    switch (type) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Timeline::set_items(const std::vector<TimelineItem>& values) {
    items = values;
    invalidate();
}

void Timeline::set_options(int position_value, bool show_time_value) {
    if (position_value < 0) position_value = 0;
    if (position_value > 2) position_value = 2;
    position = position_value;
    show_time = show_time_value;
    invalidate();
}

void Timeline::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color line = style.border_color ? style.border_color : t->border_default;
    Color time_fg = t->text_muted;
    Color content_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color card_bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float left = (float)style.pad_left;
    float top = (float)style.pad_top;
    float axis_x = left + 12.0f;
    float row_h = (std::max)(style.font_size * 4.0f, 58.0f);
    float dot_r = (std::max)(4.0f, style.font_size * 0.36f);
    int count = (int)items.size();
    if (count == 0) {
        draw_text(ctx, L"暂无时间线数据", style, t->text_secondary,
                  left, top, (float)bounds.w - style.pad_left - style.pad_right,
                  (float)bounds.h - style.pad_top - style.pad_bottom);
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }

    if (position == 1) {
        axis_x = (float)bounds.w - (float)style.pad_right - 12.0f;
    } else if (position == 2) {
        axis_x = (float)bounds.w * 0.5f;
    }

    float axis_top = top + dot_r;
    float axis_bottom = (std::min)(top + row_h * (float)(count - 1) + dot_r, (float)bounds.h - (float)style.pad_bottom);
    ctx.rt->DrawLine(D2D1::Point2F(axis_x, axis_top),
                     D2D1::Point2F(axis_x, axis_bottom),
                     ctx.get_brush(line), 1.0f);

    for (int i = 0; i < count; ++i) {
        float y = top + row_h * (float)i;
        if (y >= bounds.h) break;
        const TimelineItem& item = items[i];
        Color accent = type_color(t, item.item_type);
        float dot_y = y + dot_r + 1.0f;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(axis_x, dot_y), dot_r + 2.0f, dot_r + 2.0f),
                            ctx.get_brush(card_bg));
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(axis_x, dot_y), dot_r, dot_r),
                            ctx.get_brush(accent));
        if (!item.icon.empty()) {
            float icon_box = (std::max)(18.0f, style.font_size * 1.35f);
            D2D1_RECT_F icon_bg = {
                axis_x - icon_box * 0.5f,
                dot_y - icon_box * 0.5f,
                axis_x + icon_box * 0.5f,
                dot_y + icon_box * 0.5f
            };
            ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(axis_x, dot_y),
                icon_box * 0.5f, icon_box * 0.5f), ctx.get_brush(card_bg));
            ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(axis_x, dot_y),
                icon_box * 0.5f, icon_box * 0.5f), ctx.get_brush(accent), 1.2f);
            draw_text(ctx, item.icon, style, accent,
                      icon_bg.left, icon_bg.top - 1.0f,
                      icon_bg.right - icon_bg.left, icon_bg.bottom - icon_bg.top,
                      0.88f, DWRITE_WORD_WRAPPING_NO_WRAP);
        }

        bool right_side = position == 0 || (position == 2 && (i % 2 == 0));
        float text_x = right_side ? axis_x + 18.0f : left;
        float text_w = right_side
            ? (float)bounds.w - text_x - style.pad_right
            : axis_x - left - 18.0f;
        if (text_w < 1.0f) text_w = 1.0f;
        if (show_time) {
            draw_text(ctx, item.time, style, time_fg,
                      text_x, y - 2.0f, text_w, style.font_size * 1.25f, 0.9f);
        }
        draw_text(ctx, item.content, style, content_fg,
                  text_x, y + (show_time ? style.font_size * 1.35f : 0.0f),
                  text_w, row_h - (show_time ? style.font_size * 1.35f : 0.0f) - 4.0f,
                  1.0f, DWRITE_WORD_WRAPPING_WRAP);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
