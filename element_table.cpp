#include "element_table.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwctype>

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

int Table::row_at(int x, int y) const {
    if (x < style.pad_left || x >= bounds.w - style.pad_right) return -1;
    int header_h = (std::max)(header_height_value, (int)(style.font_size * 2.15f));
    int row_h = (std::max)(row_height_value, (int)(style.font_size * 2.0f));
    int local_y = y - style.pad_top - header_h;
    if (local_y < 0 || row_h <= 0) return -1;
    int idx = local_y / row_h;
    idx += scroll_row;
    if (idx < 0 || idx >= (int)rows.size()) return -1;
    return idx;
}

void Table::clamp_scroll() {
    int header_h = (std::max)(header_height_value, (int)(style.font_size * 2.15f));
    int row_h = (std::max)(row_height_value, (int)(style.font_size * 2.0f));
    int visible_rows = row_h > 0 ? (bounds.h - style.pad_top - style.pad_bottom - header_h) / row_h : 0;
    if (visible_rows < 1) visible_rows = 1;
    int max_scroll = (std::max)(0, (int)rows.size() - visible_rows);
    if (scroll_row < 0) scroll_row = 0;
    if (scroll_row > max_scroll) scroll_row = max_scroll;
}

void Table::set_columns(const std::vector<std::wstring>& values) {
    columns = values;
    invalidate();
}

void Table::set_rows(const std::vector<std::vector<std::wstring>>& values) {
    rows = values;
    set_sort(sort_column, sort_desc);
    clamp_scroll();
    invalidate();
}

void Table::set_striped(bool value) {
    striped = value;
    invalidate();
}

void Table::set_bordered(bool value) {
    bordered = value;
    invalidate();
}

void Table::set_empty_text(const std::wstring& value) {
    empty_text = value.empty() ? L"暂无数据" : value;
    invalidate();
}

void Table::set_selected_row(int value) {
    if (!selectable || rows.empty()) {
        selected_row = -1;
    } else {
        if (value < -1) value = -1;
        if (value >= (int)rows.size()) value = (int)rows.size() - 1;
        selected_row = value;
    }
    invalidate();
}

void Table::set_options(bool striped_value, bool bordered_value, int row_height,
                        int header_height, bool selectable_value) {
    striped = striped_value;
    bordered = bordered_value;
    if (row_height < 24) row_height = 24;
    if (row_height > 80) row_height = 80;
    row_height_value = row_height;
    if (header_height < 26) header_height = 26;
    if (header_height > 90) header_height = 90;
    header_height_value = header_height;
    selectable = selectable_value;
    if (!selectable) selected_row = -1;
    clamp_scroll();
    invalidate();
}

void Table::set_sort(int column_index, bool desc) {
    sort_column = column_index;
    sort_desc = desc;
    if (sort_column >= 0) {
        std::sort(rows.begin(), rows.end(), [this](const auto& a, const auto& b) {
            std::wstring av = sort_column < (int)a.size() ? a[sort_column] : L"";
            std::wstring bv = sort_column < (int)b.size() ? b[sort_column] : L"";
            int cmp = _wcsicmp(av.c_str(), bv.c_str());
            return sort_desc ? cmp > 0 : cmp < 0;
        });
    }
    invalidate();
}

void Table::set_scroll_row(int value) {
    scroll_row = value;
    clamp_scroll();
    invalidate();
}

void Table::set_column_width(int value) {
    if (value < 0) value = 0;
    if (value > 480) value = 480;
    fixed_column_width = value;
    invalidate();
}

void Table::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color header_bg = style.bg_color ? style.bg_color : (dark ? 0xFF282A3A : 0xFFF5F7FA);
    Color stripe_bg = dark ? 0xFF242637 : 0xFFFAFAFA;
    Color hover_bg = dark ? 0xFF2B2E42 : 0xFFF0F7FF;
    Color selected_bg = dark ? 0xFF1E3A5F : 0xFFE6F4FF;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    int col_count = (int)columns.size();
    if (col_count <= 0) col_count = 1;
    float left = (float)style.pad_left;
    float top = (float)style.pad_top;
    float table_w = (float)bounds.w - style.pad_left - style.pad_right;
    if (table_w < 1.0f) table_w = 1.0f;
    float col_w = fixed_column_width > 0 ? (float)fixed_column_width : table_w / (float)col_count;
    float header_h = (std::max)((float)header_height_value, style.font_size * 2.15f);
    float row_h = (std::max)((float)row_height_value, style.font_size * 2.0f);

    D2D1_RECT_F header = { left, top, left + table_w, top + header_h };
    ctx.rt->FillRectangle(header, ctx.get_brush(header_bg));
    ctx.rt->DrawLine(D2D1::Point2F(left, top + header_h),
                     D2D1::Point2F(left + table_w, top + header_h),
                     ctx.get_brush(border), 1.0f);

    for (int c = 0; c < col_count; ++c) {
        float x = left + col_w * (float)c;
        if (x >= left + table_w) break;
        if (bordered && c > 0) {
            ctx.rt->DrawLine(D2D1::Point2F(x, top), D2D1::Point2F(x, (float)bounds.h),
                             ctx.get_brush(border), 1.0f);
        }
        std::wstring name = c < (int)columns.size() ? columns[c] : L"Column";
        if (c == sort_column) name += sort_desc ? L" ↓" : L" ↑";
        draw_text(ctx, name, style, muted, x + 10.0f, top, col_w - 16.0f, header_h);
    }

    if (rows.empty()) {
        draw_text(ctx, empty_text, style, t->text_secondary,
                  left, top + header_h, table_w,
                  (float)bounds.h - top - header_h - style.pad_bottom,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    int visible_rows = (int)((float)bounds.h - top - header_h) / (int)row_h;
    if (visible_rows < 0) visible_rows = 0;
    visible_rows = (std::min)(visible_rows, (int)rows.size());
    for (int r = 0; r < visible_rows; ++r) {
        int row_index = scroll_row + r;
        if (row_index < 0 || row_index >= (int)rows.size()) break;
        float y = top + header_h + row_h * (float)r;
        D2D1_RECT_F row_rect = { left, y, left + table_w, y + row_h };
        if (row_index == selected_row) {
            ctx.rt->FillRectangle(row_rect, ctx.get_brush(selected_bg));
        } else if (row_index == m_hover_row) {
            ctx.rt->FillRectangle(row_rect, ctx.get_brush(hover_bg));
        } else if (striped && (row_index % 2 == 1)) {
            ctx.rt->FillRectangle(row_rect, ctx.get_brush(stripe_bg));
        }
        ctx.rt->DrawLine(D2D1::Point2F(left, y + row_h),
                         D2D1::Point2F(left + table_w, y + row_h),
                         ctx.get_brush(border), 1.0f);
        for (int c = 0; c < col_count; ++c) {
            float x = left + col_w * (float)c;
            if (x >= left + table_w) break;
            std::wstring cell = (c < (int)rows[row_index].size()) ? rows[row_index][c] : L"";
            draw_text(ctx, cell, style, fg, x + 10.0f, y, col_w - 16.0f, row_h);
        }
    }

    if (bordered) {
        D2D1_RECT_F outer = { left, top, left + table_w, (float)bounds.h - (float)style.pad_bottom };
        ctx.rt->DrawRectangle(outer, ctx.get_brush(border), 1.0f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Table::on_mouse_move(int x, int y) {
    int idx = selectable ? row_at(x, y) : -1;
    if (idx != m_hover_row) {
        m_hover_row = idx;
        invalidate();
    }
}

void Table::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_row = -1;
    m_press_row = -1;
    invalidate();
}

void Table::on_mouse_down(int x, int y, MouseButton) {
    if (!selectable) return;
    m_press_row = row_at(x, y);
    pressed = true;
    invalidate();
}

void Table::on_mouse_up(int x, int y, MouseButton) {
    if (!selectable) return;
    int idx = row_at(x, y);
    if (idx >= 0 && idx == m_press_row) set_selected_row(idx);
    m_press_row = -1;
    pressed = false;
    invalidate();
}

void Table::on_key_down(int vk, int) {
    if (!selectable || rows.empty()) return;
    if (vk == VK_UP) set_selected_row(selected_row <= 0 ? 0 : selected_row - 1);
    else if (vk == VK_DOWN) set_selected_row(selected_row < 0 ? 0 : selected_row + 1);
    else if (vk == VK_HOME) set_selected_row(0);
    else if (vk == VK_END) set_selected_row((int)rows.size() - 1);
}
