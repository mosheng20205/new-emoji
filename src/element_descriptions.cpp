#include "element_descriptions.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

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

void Descriptions::set_items(const std::vector<std::pair<std::wstring, std::wstring>>& values) {
    items = values;
    invalidate();
}

void Descriptions::set_columns(int value) {
    if (value < 1) value = 1;
    if (value > 4) value = 4;
    columns = value;
    invalidate();
}

void Descriptions::set_bordered(bool value) {
    bordered = value;
    invalidate();
}

void Descriptions::set_options(int column_count, bool has_border, int label_width_value,
                               int min_row_height_value, bool wrap) {
    set_columns(column_count);
    bordered = has_border;
    if (label_width_value < 48) label_width_value = 48;
    if (label_width_value > 220) label_width_value = 220;
    label_width = label_width_value;
    if (min_row_height_value < 24) min_row_height_value = 24;
    if (min_row_height_value > 120) min_row_height_value = 120;
    min_row_height = min_row_height_value;
    wrap_values = wrap;
    invalidate();
}

void Descriptions::set_advanced_options(bool responsive_value, bool last_item_span_value) {
    responsive = responsive_value;
    last_item_span = last_item_span_value;
    invalidate();
}

int Descriptions::effective_columns() const {
    int cols = (std::max)(1, columns);
    if (!responsive) return cols;
    int content_w = bounds.w - style.pad_left - style.pad_right;
    if (content_w < 360) return 1;
    if (content_w < 620) return (std::min)(cols, 2);
    return cols;
}

void Descriptions::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color label_fg = t->text_secondary;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color label_bg = style.bg_color ? style.bg_color : (dark ? 0xFF282A3A : 0xFFF5F7FA);

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float title_h = text.empty() ? 0.0f : style.font_size * 2.0f;
    if (!text.empty()) {
        draw_text(ctx, text, style, fg, (float)style.pad_left, 0.0f,
                  (float)bounds.w - style.pad_left - style.pad_right, title_h);
    }

    int count = (int)items.size();
    int cols = effective_columns();
    int rows = count > 0 ? (count + cols - 1) / cols : 1;
    float top = title_h + 2.0f;
    float grid_h = (float)bounds.h - top - (float)style.pad_bottom;
    if (grid_h < 1.0f) grid_h = 1.0f;
    float row_h = grid_h / (float)rows;
    float min_h = (std::max)((float)min_row_height, style.font_size * 1.8f);
    if (row_h < min_h) row_h = min_h;
    float cell_w = ((float)bounds.w - style.pad_left - style.pad_right) / (float)cols;
    float left = (float)style.pad_left;

    for (int i = 0; i < rows * cols; ++i) {
        int row = i / cols;
        int col = i % cols;
        bool span = last_item_span && i == count - 1 && col != 0;
        float x = left + cell_w * (float)col;
        float y = top + row_h * (float)row;
        if (y >= bounds.h) break;
        float h = (std::min)(row_h, (float)bounds.h - y);
        float current_cell_w = span ? cell_w * (float)(cols - col) : cell_w;
        D2D1_RECT_F cell = { x, y, x + current_cell_w, y + h };
        if (bordered) {
            ctx.rt->DrawRectangle(cell, ctx.get_brush(border), 1.0f);
        }
        if (i >= count) continue;
        float label_w = (std::min)(current_cell_w * 0.48f, (float)label_width * style.font_size / 14.0f);
        if (bordered) {
            D2D1_RECT_F label_rect = { x, y, x + label_w, y + h };
            ctx.rt->FillRectangle(label_rect, ctx.get_brush(label_bg));
            ctx.rt->DrawLine(D2D1::Point2F(x + label_w, y),
                             D2D1::Point2F(x + label_w, y + h),
                             ctx.get_brush(border), 1.0f);
        }
        draw_text(ctx, items[i].first, style, label_fg,
                  x + 8.0f, y, label_w - 12.0f, h);
        if (wrap_values) {
            auto* layout = ctx.create_text_layout(items[i].second, style.font_name, style.font_size,
                                                  current_cell_w - label_w - 14.0f, h);
            if (layout) {
                apply_emoji_font_fallback(layout, items[i].second);
                layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
                layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
                ctx.rt->DrawTextLayout(D2D1::Point2F(x + label_w + 8.0f, y), layout,
                    ctx.get_brush(fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
                layout->Release();
            }
        } else {
            draw_text(ctx, items[i].second, style, fg,
                      x + label_w + 8.0f, y, current_cell_w - label_w - 14.0f, h);
        }
        if (span) i += cols - col - 1;
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
