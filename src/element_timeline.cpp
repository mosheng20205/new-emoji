#include "element_timeline.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

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
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
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

void Timeline::set_advanced_options(int position_value, bool show_time_value,
                                    bool reverse_value, int default_placement_value) {
    if (position_value < 0) position_value = 0;
    if (position_value > 2) position_value = 2;
    if (default_placement_value < 0) default_placement_value = 0;
    if (default_placement_value > 1) default_placement_value = 1;
    position = position_value;
    show_time = show_time_value;
    reverse = reverse_value;
    default_placement = default_placement_value;
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
    Color card_border = dark ? 0xFF3D4668 : 0xFFD2DCEB;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float left = (float)style.pad_left;
    float top = (float)style.pad_top;
    float axis_x = left + 12.0f;
    float normal_row_h = (std::max)(style.font_size * 4.3f, 64.0f);
    float card_row_h = (std::max)(style.font_size * 7.8f, 118.0f);
    float base_dot_r = (std::max)(4.0f, style.font_size * 0.36f);
    int count = (int)items.size();
    if (count == 0) {
        draw_text(ctx, L"📭 暂无时间线数据", style, t->text_secondary,
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

    std::vector<float> row_heights;
    row_heights.reserve(items.size());
    for (int i = 0; i < count; ++i) {
        const TimelineItem& item = items[i];
        float h = (!item.card_title.empty() || !item.card_body.empty()) ? card_row_h : normal_row_h;
        if (item.size > 0) h += 8.0f;
        row_heights.push_back(h);
    }
    float total_h = 0.0f;
    for (int i = 0; i + 1 < count; ++i) {
        int item_index = reverse ? (count - 1 - i) : i;
        total_h += row_heights[item_index];
    }

    float axis_top = top + base_dot_r;
    float axis_bottom = (std::min)(top + total_h + base_dot_r, (float)bounds.h - (float)style.pad_bottom);
    ctx.rt->DrawLine(D2D1::Point2F(axis_x, axis_top),
                     D2D1::Point2F(axis_x, axis_bottom),
                     ctx.get_brush(line), 1.0f);

    float y_cursor = top;
    for (int i = 0; i < count; ++i) {
        float y = y_cursor;
        if (y >= bounds.h) break;
        int item_index = reverse ? (count - 1 - i) : i;
        const TimelineItem& item = items[item_index];
        bool card_mode = !item.card_title.empty() || !item.card_body.empty();
        int placement = item.placement >= 0 ? item.placement : default_placement;
        Color accent = item.color ? item.color : type_color(t, item.item_type);
        float row_h = row_heights[item_index];
        float dot_r = item.size > 0 ? (std::max)(6.0f, style.font_size * 0.48f) : base_dot_r;
        float dot_y = y + dot_r + 1.0f;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(axis_x, dot_y), dot_r + 2.4f, dot_r + 2.4f),
                            ctx.get_brush(card_bg));
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(axis_x, dot_y), dot_r, dot_r),
                            ctx.get_brush(accent));
        if (!item.icon.empty()) {
            float icon_box = item.size > 0
                ? (std::max)(24.0f, style.font_size * 1.75f)
                : (std::max)(18.0f, style.font_size * 1.35f);
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

        float time_h = show_time ? style.font_size * 1.35f : 0.0f;
        if (card_mode) {
            float card_y = y + (show_time && placement == 0 ? time_h + 4.0f : 0.0f);
            float card_h = row_h - (show_time ? time_h + 8.0f : 4.0f);
            if (card_h < 58.0f) card_h = 58.0f;
            if (show_time && placement == 0) {
                draw_text(ctx, item.time, style, time_fg,
                          text_x, y - 1.0f, text_w, time_h, 0.9f);
            }

            D2D1_RECT_F card = { text_x, card_y, text_x + text_w, card_y + card_h };
            ctx.rt->FillRoundedRectangle(ROUNDED(card, 6.0f, 6.0f), ctx.get_brush(card_bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(card.left + 0.5f, card.top + 0.5f,
                card.right - 0.5f, card.bottom - 0.5f), 6.0f, 6.0f), ctx.get_brush(card_border), 1.0f);

            std::wstring title = item.card_title.empty() ? item.content : item.card_title;
            std::wstring body = item.card_body.empty() ? item.content : item.card_body;
            draw_text(ctx, title, style, content_fg,
                      card.left + 14.0f, card.top + 10.0f,
                      card.right - card.left - 28.0f, style.font_size * 1.45f,
                      1.0f, DWRITE_WORD_WRAPPING_NO_WRAP, DWRITE_FONT_WEIGHT_SEMI_BOLD);
            draw_text(ctx, body, style, t->text_secondary,
                      card.left + 14.0f, card.top + 36.0f,
                      card.right - card.left - 28.0f, card.bottom - card.top - 44.0f,
                      0.95f, DWRITE_WORD_WRAPPING_WRAP);
            if (show_time && placement == 1) {
                draw_text(ctx, item.time, style, time_fg,
                          text_x, card.bottom + 4.0f, text_w, time_h, 0.9f);
            }
        } else {
            if (show_time && placement == 0) {
                draw_text(ctx, item.time, style, time_fg,
                          text_x, y - 2.0f, text_w, time_h, 0.9f);
            }
            float content_y = y + (show_time && placement == 0 ? time_h : 0.0f);
            float content_h = row_h - (show_time ? time_h : 0.0f) - (placement == 1 ? 10.0f : 4.0f);
            draw_text(ctx, item.content, style, content_fg,
                      text_x, content_y, text_w, content_h,
                      1.0f, DWRITE_WORD_WRAPPING_WRAP);
            if (show_time && placement == 1) {
                draw_text(ctx, item.time, style, time_fg,
                          text_x, y + row_h - time_h - 6.0f, text_w, time_h, 0.9f);
            }
        }
        y_cursor += row_h;
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
