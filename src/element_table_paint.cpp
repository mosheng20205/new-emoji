#include "element_table.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <cwctype>

static D2D1_RECT_F intersect_rect(const D2D1_RECT_F& a, const D2D1_RECT_F& b) {
    return {
        (std::max)(a.left, b.left),
        (std::max)(a.top, b.top),
        (std::min)(a.right, b.right),
        (std::min)(a.bottom, b.bottom)
    };
}

static bool push_clip_if_visible(RenderContext& ctx, const D2D1_RECT_F& rect) {
    if (rect.right <= rect.left || rect.bottom <= rect.top) return false;
    ctx.push_clip(rect);
    return true;
}

static Color alpha_color(Color c, unsigned a) {
    return (c & 0x00FFFFFF) | ((a & 0xFF) << 24);
}

static void draw_text_ex(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                         Color color, float x, float y, float w, float h,
                         int align = 0, int flags = 0, float size_override = 0.0f) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    float fs = size_override > 0.0f ? size_override : style.font_size;
    auto* layout = ctx.create_text_layout(text, style.font_name, fs, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    DWRITE_TEXT_RANGE range{ 0, (UINT32)text.size() };
    if (flags & 1) layout->SetFontWeight(DWRITE_FONT_WEIGHT_SEMI_BOLD, range);
    if (flags & 2) layout->SetFontStyle(DWRITE_FONT_STYLE_ITALIC, range);
    if (flags & 4) layout->SetUnderline(TRUE, range);
    layout->SetTextAlignment(align == 1 ? DWRITE_TEXT_ALIGNMENT_CENTER : (align == 2 ? DWRITE_TEXT_ALIGNMENT_TRAILING : DWRITE_TEXT_ALIGNMENT_LEADING));
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout, ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

struct TablePaintStyle {
    Color bg = 0;
    Color fg = 0;
    int align = 0;
    int flags = 0;
    float font_size = 0.0f;
};

static void merge_style(TablePaintStyle& out, const TableStyleOverride& in) {
    if (in.has_bg) out.bg = in.bg;
    if (in.has_fg) out.fg = in.fg;
    if (in.has_align) out.align = in.align;
    if (in.has_font_flags) out.flags = in.font_flags;
    if (in.has_font_size) out.font_size = (float)in.font_size;
}

static TablePaintStyle cell_style_for(const Table& table, int row, int col, const Theme* t) {
    TablePaintStyle out;
    out.fg = table.style.fg_color ? table.style.fg_color : t->text_primary;
    out.align = col < (int)table.adv_columns.size() ? table.adv_columns[col].align : 0;
    if (col < (int)table.adv_columns.size()) merge_style(out, table.adv_columns[col].style);
    if (const TableRow* row_ptr = table.row_ptr(row)) {
        merge_style(out, row_ptr->style);
        if (col >= 0 && col < (int)row_ptr->cells.size()) {
            merge_style(out, row_ptr->cells[col].style);
        }
    }
    return out;
}

static void draw_check(RenderContext& ctx, const D2D1_RECT_F& r, bool checked, const Theme* t) {
    float s = (std::min)(r.right - r.left, r.bottom - r.top) - 10.0f;
    if (s < 12.0f) s = 12.0f;
    float x = r.left + ((r.right - r.left) - s) * 0.5f;
    float y = r.top + ((r.bottom - r.top) - s) * 0.5f;
    D2D1_RECT_F box{ x, y, x + s, y + s };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(box, 3, 3), ctx.get_brush(checked ? t->accent : 0xFFFFFFFF));
    ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(box, 3, 3), ctx.get_brush(checked ? t->accent : t->border_default), 1.0f);
    if (checked) {
        ctx.rt->DrawLine(D2D1::Point2F(x + s * .25f, y + s * .52f), D2D1::Point2F(x + s * .43f, y + s * .70f), ctx.get_brush(0xFFFFFFFF), 2.0f);
        ctx.rt->DrawLine(D2D1::Point2F(x + s * .43f, y + s * .70f), D2D1::Point2F(x + s * .76f, y + s * .30f), ctx.get_brush(0xFFFFFFFF), 2.0f);
    }
}

static void draw_status(RenderContext& ctx, const D2D1_RECT_F& r, const ElementStyle& style,
                        const TableCell& cell, Color fg, const Theme* t, int align, int flags, float fs) {
    Color colors[] = { t->accent, 0xFF67C23A, 0xFFE6A23C, 0xFFF56C6C, 0xFF909399 };
    int idx = (std::max)(0, (std::min)(4, cell.status));
    float cy = (r.top + r.bottom) * .5f;
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(r.left + 18.0f, cy), 4.5f, 4.5f), ctx.get_brush(colors[idx]));
    draw_text_ex(ctx, cell.value, style, fg, r.left + 30.0f, r.top, r.right - r.left - 38.0f, r.bottom - r.top, align, flags, fs);
}

static void draw_tag(RenderContext& ctx, const D2D1_RECT_F& r, const ElementStyle& style,
                     const TableCell& cell, Color fg, const Theme* t, int align, int flags, float fs) {
    Color fill = cell.kind == TableCellKind::PopoverTag ? 0xFFFFF7E6 : alpha_color(t->accent, 0x18);
    Color stroke = cell.kind == TableCellKind::PopoverTag ? 0xFFFFC069 : alpha_color(t->accent, 0x99);
    float cell_w = r.right - r.left;
    float tag_w = (std::min)(cell_w - 18.0f, (float)(cell.value.size() * 12 + 24));
    tag_w = (std::max)(84.0f, tag_w);
    float tag_x = align == 2 ? r.right - tag_w - 8.0f : r.left + 8.0f;
    if (align == 1 || cell.kind == TableCellKind::Tag || cell.kind == TableCellKind::PopoverTag) {
        tag_x = r.left + (cell_w - tag_w) * .5f;
    }
    D2D1_RECT_F tag{ tag_x, r.top + 6.0f, tag_x + tag_w, r.bottom - 6.0f };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(tag, 5, 5), ctx.get_brush(fill));
    ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(tag, 5, 5), ctx.get_brush(stroke), 1.0f);
    draw_text_ex(ctx, cell.value, style, fg, tag.left + 8.0f, tag.top, tag.right - tag.left - 16.0f, tag.bottom - tag.top, 1, flags, fs);
}

static void draw_progress_cell(RenderContext& ctx, const D2D1_RECT_F& r, const ElementStyle& style,
                               const TableCell& cell, const Theme* t, int flags, float fs) {
    int pct = (std::max)(0, (std::min)(100, cell.number));
    D2D1_RECT_F bar{ r.left + 8.0f, (r.top + r.bottom) * .5f - 5.0f, r.right - 46.0f, (r.top + r.bottom) * .5f + 5.0f };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(bar, 5, 5), ctx.get_brush(0xFFE4E7ED));
    D2D1_RECT_F fill = bar;
    fill.right = fill.left + (bar.right - bar.left) * pct / 100.0f;
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(fill, 5, 5), ctx.get_brush(pct >= 90 ? 0xFF67C23A : t->accent));
    draw_text_ex(ctx, std::to_wstring(pct) + L"%", style, t->text_secondary, r.right - 42.0f, r.top, 38.0f, r.bottom - r.top, 2, flags, fs);
}

static void draw_button_like(RenderContext& ctx, const D2D1_RECT_F& r, const ElementStyle& style,
                             const std::wstring& text, const Theme* t, int variant = 0, bool hovered = false) {
    Color fill = variant == 4 ? 0xFFF56C6C : (variant == 2 ? 0xFF67C23A : t->accent);
    D2D1_RECT_F br = r;
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(br, 5, 5), ctx.get_brush(fill));
    if (hovered) {
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(br, 5, 5), ctx.get_brush(0x18FFFFFF));
        ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(br, 5, 5), ctx.get_brush(0x99FFFFFF), 1.0f);
    }
    draw_text_ex(ctx, text, style, 0xFFFFFFFF, br.left + 8.0f, br.top, br.right - br.left - 16.0f, br.bottom - br.top, 1, 0, (std::max)(9.5f, style.font_size - 4.0f));
}

static std::wstring current_option_text(const TableCell& cell) {
    if (cell.parts.empty()) return cell.value;
    auto it = std::find(cell.parts.begin(), cell.parts.end(), cell.value);
    if (it != cell.parts.end()) return cell.value;
    return cell.parts.front();
}

static void draw_dropdown_cell(RenderContext& ctx, const D2D1_RECT_F& r, const ElementStyle& style,
                               const TableCell& cell, Color fg, const Theme* t, int align, int flags, float fs) {
    D2D1_RECT_F box{ r.left + 8.0f, r.top + 5.0f, r.right - 8.0f, r.bottom - 5.0f };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(box, 5, 5), ctx.get_brush(0xFF2F3550));
    ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(box, 5, 5), ctx.get_brush(t->border_default), 1.0f);
    std::wstring text = current_option_text(cell);
    draw_text_ex(ctx, text, style, fg, box.left + 8.0f, box.top, box.right - box.left - 26.0f, box.bottom - box.top, align, flags, fs);
    draw_text_ex(ctx, L"⌄", style, t->text_secondary, box.right - 20.0f, box.top, 16.0f, box.bottom - box.top, 1, 0, (std::max)(11.0f, style.font_size - 4.0f));
}

static void draw_control_cell(RenderContext& ctx, const D2D1_RECT_F& r, const ElementStyle& style,
                              const TableCell& cell, Color fg, const Theme* t, int align, int flags, float fs, bool hovered) {
    switch (cell.kind) {
    case TableCellKind::Index:
    case TableCellKind::Text:
        draw_text_ex(ctx, cell.value, style, fg, r.left + 10.0f, r.top, r.right - r.left - 16.0f, r.bottom - r.top, align, flags, fs);
        break;
    case TableCellKind::Selection:
        draw_check(ctx, r, cell.checked, t);
        break;
    case TableCellKind::Expand:
        draw_text_ex(ctx, cell.value.empty() ? L"›" : cell.value, style, fg, r.left + 10.0f, r.top, r.right - r.left - 16.0f, r.bottom - r.top, 1, flags, fs);
        break;
    case TableCellKind::Switch: {
        float w = 42.0f, h = 22.0f, x = r.left + ((r.right - r.left) - w) * .5f, y = (r.top + r.bottom - h) * .5f;
        D2D1_RECT_F tr{ x, y, x + w, y + h };
        ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(tr, 11, 11), ctx.get_brush(cell.checked ? t->accent : 0xFFD1D5DB));
        float kx = cell.checked ? tr.right - 11.0f : tr.left + 11.0f;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(kx, y + 11.0f), 8.0f, 8.0f), ctx.get_brush(0xFFFFFFFF));
        break;
    }
    case TableCellKind::Progress:
        draw_progress_cell(ctx, r, style, cell, t, flags, fs);
        break;
    case TableCellKind::Status:
        draw_status(ctx, r, style, cell, fg, t, align, flags, fs);
        break;
    case TableCellKind::Tag:
    case TableCellKind::PopoverTag:
        draw_tag(ctx, r, style, cell, fg, t, 1, flags, fs);
        break;
    case TableCellKind::Button: {
        D2D1_RECT_F br{ r.left + 6.0f, r.top + 6.0f, r.right - 6.0f, r.bottom - 6.0f };
        draw_button_like(ctx, br, style, cell.value.empty() ? L"查看" : cell.value, t, 0, hovered);
        break;
    }
    case TableCellKind::Select:
    case TableCellKind::Combo:
        draw_dropdown_cell(ctx, r, style, cell, fg, t, align, flags, fs);
        break;
    case TableCellKind::Buttons: {
        auto labels = cell.parts.empty() ? std::vector<std::wstring>{ L"查看", L"编辑" } : cell.parts;
        std::vector<float> widths;
        widths.reserve(labels.size());
        float total = 0.0f;
        for (int i = 0; i < (int)labels.size() && i < 3; ++i) {
            float estimate = (float)labels[i].size() * 7.5f + 28.0f;
            float bw = (std::max)(72.0f, (std::min)(108.0f, estimate));
            widths.push_back(bw);
            total += bw;
        }
        if (!widths.empty()) total += (float)((int)widths.size() - 1) * 6.0f;
        float x = r.left + (r.right - r.left - total) * 0.5f;
        if (x < r.left + 4.0f) x = r.left + 4.0f;
        for (int i = 0; i < (int)labels.size() && i < 3; ++i) {
            D2D1_RECT_F br{ x, r.top + 6.0f, x + widths[i], r.bottom - 6.0f };
            draw_button_like(ctx, br, style, labels[i], t, i == 2 ? 4 : 0, hovered);
            x += widths[i] + 6.0f;
        }
        break;
    }
    }
}

static std::wstring summary_for(const Table& table, int col) {
    if (col < (int)table.summary_values.size() && !table.summary_values[col].empty()) return table.summary_values[col];
    if (col == 0) return L"合计";
    double sum = 0.0;
    bool any = false;
    for (int r = 0; r < table.row_count(); ++r) {
        const TableRow* row = table.row_ptr(r);
        if (!row || col >= (int)row->cells.size()) continue;
        wchar_t* end = nullptr;
        double v = wcstod(row->cells[col].value.c_str(), &end);
        if (end && end != row->cells[col].value.c_str()) { sum += v; any = true; }
    }
    if (!any) return L"";
    int whole = (int)std::round(sum);
    return std::to_wstring(whole);
}

static float fixed_width_for(const Table& table, int fixed, float table_w) {
    float total = 0.0f;
    for (int c = 0; c < (int)table.adv_columns.size(); ++c) {
        if (table.adv_columns[c].fixed == fixed) total += table.column_width_at(c, table_w);
    }
    return total;
}

static constexpr float kScrollbarSize = 14.0f;
static constexpr float kScrollbarPad = 2.0f;
static constexpr float kScrollbarMinThumb = 32.0f;

static bool vertical_scroll_track(const Table& table, D2D1_RECT_F& out) {
    if (!table.needs_vertical_scrollbar()) return false;
    float table_h = (float)table.table_height_px();
    float bottom = table_h - (float)table.style.pad_bottom - (float)table.summary_height_px();
    if (table.needs_horizontal_scrollbar()) bottom -= kScrollbarSize;
    out = {
        (float)table.bounds.w - (float)table.style.pad_right - kScrollbarSize,
        (float)table.style.pad_top + (float)table.header_height_px(),
        (float)table.bounds.w - (float)table.style.pad_right,
        bottom
    };
    return out.right > out.left && out.bottom > out.top;
}

static bool vertical_scroll_thumb(const Table& table, D2D1_RECT_F& out) {
    D2D1_RECT_F track{};
    if (!vertical_scroll_track(table, track)) return false;
    int max_row = table.max_scroll_row();
    int visible = table.visible_row_count();
    int total = (std::max)(visible + max_row, 1);
    float track_h = track.bottom - track.top - kScrollbarPad * 2.0f;
    if (track_h <= 0.0f) return false;
    float thumb_h = (std::max)(kScrollbarMinThumb, track_h * (float)visible / (float)total);
    thumb_h = (std::min)(thumb_h, track_h);
    float travel = (std::max)(0.0f, track_h - thumb_h);
    float y = track.top + kScrollbarPad + (max_row > 0 ? travel * (float)table.scroll_row / (float)max_row : 0.0f);
    out = { track.left + kScrollbarPad, y, track.right - kScrollbarPad, y + thumb_h };
    return true;
}

static bool horizontal_scroll_track(const Table& table, D2D1_RECT_F& out) {
    if (!table.needs_horizontal_scrollbar()) return false;
    float table_h = (float)table.table_height_px();
    float bottom = table_h - (float)table.style.pad_bottom - (float)table.summary_height_px();
    float table_w = (float)table.bounds.w - table.style.pad_left - table.style.pad_right;
    float fixed_left = 0.0f;
    float fixed_right = 0.0f;
    for (int c = 0; c < (int)table.adv_columns.size(); ++c) {
        float cw = table.column_width_at(c, table_w);
        if (table.adv_columns[c].fixed == -1) fixed_left += cw;
        else if (table.adv_columns[c].fixed == 1) fixed_right += cw;
    }
    float left = (float)table.style.pad_left + fixed_left;
    float right = (float)table.style.pad_left + table_w - fixed_right;
    if (table.needs_vertical_scrollbar()) right -= kScrollbarSize;
    out = {
        left,
        bottom - kScrollbarSize,
        right,
        bottom
    };
    return out.right > out.left && out.bottom > out.top;
}

static bool horizontal_scroll_thumb(const Table& table, D2D1_RECT_F& out) {
    D2D1_RECT_F track{};
    if (!horizontal_scroll_track(table, track)) return false;
    int max_x = table.max_scroll_x();
    float table_w = (float)table.bounds.w - table.style.pad_left - table.style.pad_right;
    float fixed_left = 0.0f;
    float fixed_right = 0.0f;
    float normal_total = 0.0f;
    for (int c = 0; c < (int)table.adv_columns.size(); ++c) {
        float cw = table.column_width_at(c, table_w);
        if (table.adv_columns[c].fixed == -1) fixed_left += cw;
        else if (table.adv_columns[c].fixed == 1) fixed_right += cw;
        else normal_total += cw;
    }
    float viewport = (std::max)(1.0f, table_w - fixed_left - fixed_right);
    float total = (std::max)(viewport + (float)max_x, normal_total);
    float track_w = track.right - track.left - kScrollbarPad * 2.0f;
    if (track_w <= 0.0f) return false;
    float thumb_w = (std::max)(kScrollbarMinThumb, track_w * viewport / (std::max)(viewport, total));
    thumb_w = (std::min)(thumb_w, track_w);
    float travel = (std::max)(0.0f, track_w - thumb_w);
    float x = track.left + kScrollbarPad + (max_x > 0 ? travel * (float)table.scroll_x / (float)max_x : 0.0f);
    out = { x, track.top + kScrollbarPad, x + thumb_w, track.bottom - kScrollbarPad };
    return true;
}

static void draw_scrollbar(RenderContext& ctx, const D2D1_RECT_F& track, const D2D1_RECT_F& thumb,
                           const Theme* t, bool active) {
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(track, 6, 6), ctx.get_brush(0x26000000));
    Color thumb_color = active ? t->accent : alpha_color(t->text_secondary, 0x88);
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(thumb, 5, 5), ctx.get_brush(thumb_color));
    if (active) {
        ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(thumb, 5, 5), ctx.get_brush(0xCCFFFFFF), 1.0f);
    }
}

static bool table_cell_rect(const Table& table, int row, int col, D2D1_RECT_F& out) {
    int slot = -1;
    if (table.virtual_mode) {
        if (row < table.scroll_row) return false;
        slot = row - table.scroll_row;
    } else {
        auto visible = table.visible_row_indices();
        auto it = std::find(visible.begin(), visible.end(), row);
        if (it == visible.end()) return false;
        slot = (int)(it - visible.begin()) - table.scroll_row;
    }
    if (slot < 0) return false;
    int row_h = table.row_height_px();
    int header_h = table.header_height_px();
    float left = (float)table.style.pad_left;
    float top = (float)table.style.pad_top + (float)header_h + slot * (float)row_h;
    float table_w = (float)table.bounds.w - table.style.pad_left - table.style.pad_right;
    float x = table.column_x(col, left, table_w);
    float cw = table.column_width_at(col, table_w);
    out = { x, top, x + cw, top + (float)row_h };
    return true;
}

static bool table_popup_rect(const Table& table, int row, int col, D2D1_RECT_F& out) {
    const TableRow* row_ptr = table.row_ptr(row);
    if (!row_ptr || col < 0 || col >= (int)table.adv_columns.size()) return false;
    const TableCell& cell = row_ptr->cells[col];
    if (cell.parts.size() < 2) return false;
    D2D1_RECT_F cell_rect{};
    if (!table_cell_rect(table, row, col, cell_rect)) return false;
    float width = (std::max)(cell_rect.right - cell_rect.left, 160.0f);
    float item_h = (std::max)(28.0f, (float)table.row_height_px());
    float height = (std::min)(item_h * (float)cell.parts.size(), 240.0f);
    float x = cell_rect.left;
    float y = cell_rect.bottom + 2.0f;
    float bottom_limit = (float)table.bounds.h - (float)table.style.pad_bottom;
    if (y + height > bottom_limit) y = cell_rect.top - height - 2.0f;
    if (y < (float)table.style.pad_top) y = (float)table.style.pad_top;
    if (x + width > (float)table.bounds.w - table.style.pad_right) {
        x = (float)table.bounds.w - table.style.pad_right - width;
    }
    if (x < (float)table.style.pad_left) x = (float)table.style.pad_left;
    out = { x, y, x + width, y + height };
    return true;
}

void Table::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color header_bg = style.bg_color ? style.bg_color : (dark ? 0xFF282A3A : 0xFFF5F7FA);
    Color stripe_bg = dark ? 0xFF242637 : 0xFFFAFAFA;
    Color hover_bg = dark ? 0xFF2B2E42 : 0xFFF0F7FF;
    Color selected_bg = dark ? 0xFF1E3A5F : 0xFFE6F4FF;

    float left = (float)style.pad_left;
    float top = (float)style.pad_top;
    float table_w = (float)bounds.w - style.pad_left - style.pad_right;
    float table_h = (float)table_height_px();
    D2D1_RECT_F clip{ 0, 0, (float)bounds.w, table_h };
    ctx.push_clip(clip);

    int header_h = header_height_px();
    int row_h = row_height_px();
    int sum_h = summary_height_px();
    float body_top = top + (float)header_h;
    float body_h = table_h - top - style.pad_bottom - header_h - sum_h;
    if (needs_horizontal_scrollbar()) body_h -= kScrollbarSize;
    int max_slots = row_h > 0 ? (int)(body_h / row_h) : 0;
    float table_bottom = table_h - (float)style.pad_bottom;
    float column_grid_bottom = body_top + (float)max_slots * (float)row_h;
    if (show_summary) column_grid_bottom = table_h - (float)style.pad_bottom - (float)sum_h;
    column_grid_bottom = (std::min)(table_bottom, (std::max)(body_top, column_grid_bottom));
    std::vector<int> visible;
    if (!virtual_mode) visible = visible_row_indices();
    int col_count = (int)adv_columns.size();
    float fixed_left_w = fixed_width_for(*this, -1, table_w);
    float fixed_right_w = fixed_width_for(*this, 1, table_w);
    D2D1_RECT_F scroll_clip{
        left + fixed_left_w,
        top,
        left + (std::max)(fixed_left_w, table_w - fixed_right_w),
        table_h - (float)style.pad_bottom
    };
    D2D1_RECT_F fixed_left_clip{ left, top, left + fixed_left_w, table_h - (float)style.pad_bottom };
    D2D1_RECT_F fixed_right_clip{ left + table_w - fixed_right_w, top, left + table_w, table_h - (float)style.pad_bottom };

    ctx.rt->FillRectangle({ left, top, left + table_w, top + (float)header_h }, ctx.get_brush(header_bg));
    bool grouped = false;
    for (const auto& c : adv_columns) if (!c.parent_title.empty()) grouped = true;
    int header_row_h = grouped ? header_h / 2 : header_h;

    auto paint_header_group = [&](int fixed_kind, const D2D1_RECT_F& layer_clip) {
        if (!push_clip_if_visible(ctx, layer_clip)) return;
        int start = 0;
        while (start < col_count) {
            if (adv_columns[start].fixed != fixed_kind) {
                ++start;
                continue;
            }
            std::wstring title = adv_columns[start].parent_title;
            int end = start + 1;
            if (!title.empty()) {
                while (end < col_count && adv_columns[end].fixed == fixed_kind && adv_columns[end].parent_title == title) ++end;
            }
            float x = column_x(start, left, table_w);
            float w = 0.0f;
            for (int i = start; i < end; ++i) w += column_width_at(i, table_w);
            D2D1_RECT_F cell_clip = intersect_rect({ x, top, x + w, top + (float)header_row_h }, layer_clip);
            if (!title.empty() && push_clip_if_visible(ctx, cell_clip)) {
                draw_text_ex(ctx, title, style, t->text_secondary, x + 8.0f, top, w - 16.0f, (float)header_row_h, 1, 1);
                ctx.pop_clip();
            }
            start = end;
        }
        ctx.pop_clip();
    };

    auto paint_header_columns = [&](int fixed_kind, const D2D1_RECT_F& layer_clip) {
        if (!push_clip_if_visible(ctx, layer_clip)) return;
        for (int c = 0; c < col_count; ++c) {
            if (adv_columns[c].fixed != fixed_kind) continue;
            float x = column_x(c, left, table_w);
            float cw = column_width_at(c, table_w);
            if (x + cw < layer_clip.left || x > layer_clip.right) continue;
            if (bordered && c > 0) ctx.rt->DrawLine(D2D1::Point2F(x, top), D2D1::Point2F(x, column_grid_bottom), ctx.get_brush(border), 1.0f);
            std::wstring name = adv_columns[c].title;
            if (c == sort_column) name += sort_desc ? L" ↓" : L" ↑";
            if (adv_columns[c].filterable && filters.find(c) != filters.end()) name += L" 🔎";
            int header_align = adv_columns[c].align;
            if (adv_columns[c].type == (int)TableCellKind::Tag ||
                adv_columns[c].type == (int)TableCellKind::PopoverTag) {
                header_align = 1;
            }
            float hy = top + (grouped ? (float)header_row_h : 0.0f);
            D2D1_RECT_F cell_clip = intersect_rect({ x, hy, x + cw, hy + (float)header_row_h }, layer_clip);
            if (push_clip_if_visible(ctx, cell_clip)) {
                draw_text_ex(ctx, name, style, t->text_secondary, x + 8.0f, hy, cw - 16.0f, (float)header_row_h, header_align, 1);
                ctx.pop_clip();
            }
        }
        ctx.pop_clip();
    };

    if (grouped) {
        paint_header_group(0, scroll_clip);
        paint_header_group(-1, fixed_left_clip);
        paint_header_group(1, fixed_right_clip);
    }
    paint_header_columns(0, scroll_clip);
    paint_header_columns(-1, fixed_left_clip);
    paint_header_columns(1, fixed_right_clip);
    ctx.rt->DrawLine(D2D1::Point2F(left, top + (float)header_h), D2D1::Point2F(left + table_w, top + (float)header_h), ctx.get_brush(border), 1.0f);

    int total_rows = row_count();
    if (total_rows <= 0 || (!virtual_mode && visible.empty())) {
        draw_text_ex(ctx, empty_text, style, t->text_secondary, left, body_top, table_w, body_h, 1);
    }
    for (int slot = 0; slot < max_slots; ++slot) {
        int r = virtual_mode ? (scroll_row + slot) : (scroll_row + slot);
        if (virtual_mode) {
            if (r < 0 || r >= total_rows) break;
        } else {
            int visible_pos = scroll_row + slot;
            if (visible_pos < 0 || visible_pos >= (int)visible.size()) break;
            r = visible[visible_pos];
        }
        const TableRow* row = row_ptr(r);
        if (!row) continue;
        float y = body_top + (float)slot * row_h;
        D2D1_RECT_F rr{ left, y, left + table_w, y + (float)row_h };
        bool selected = r == selected_row || std::find(selected_rows.begin(), selected_rows.end(), r) != selected_rows.end();
        Color row_bg = row->style.has_bg ? row->style.bg : 0;
        if (row_bg) ctx.rt->FillRectangle(rr, ctx.get_brush(row_bg));
        else if (selected) ctx.rt->FillRectangle(rr, ctx.get_brush(selected_bg));
        else if (r == m_hover_row) ctx.rt->FillRectangle(rr, ctx.get_brush(hover_bg));
        else if (striped && (r % 2 == 1)) ctx.rt->FillRectangle(rr, ctx.get_brush(stripe_bg));
        ctx.rt->DrawLine(D2D1::Point2F(left, y + row_h), D2D1::Point2F(left + table_w, y + row_h), ctx.get_brush(border), 1.0f);
        auto paint_body_columns = [&](int fixed_kind, const D2D1_RECT_F& layer_clip) {
            if (!push_clip_if_visible(ctx, layer_clip)) return;
            for (int c = 0; c < col_count; ++c) {
                if (adv_columns[c].fixed != fixed_kind) continue;
                if (is_span_hidden(r, c)) continue;
                TableSpan sp = span_for(r, c);
                float x = column_x(c, left, table_w);
                float cw = 0.0f;
                for (int i = 0; i < sp.colspan && c + i < col_count; ++i) cw += column_width_at(c + i, table_w);
                if (x + cw < layer_clip.left || x > layer_clip.right) continue;
                D2D1_RECT_F cr{ x, y, x + cw, y + row_h * (float)sp.rowspan };
                D2D1_RECT_F cell_clip = intersect_rect(cr, layer_clip);
                TablePaintStyle ps = cell_style_for(*this, r, c, t);
                if (ps.bg && push_clip_if_visible(ctx, cell_clip)) {
                    ctx.rt->FillRectangle(cr, ctx.get_brush(ps.bg));
                    ctx.pop_clip();
                }
                if (c < (int)row->cells.size() && push_clip_if_visible(ctx, cell_clip)) {
                    D2D1_RECT_F draw_rect = cr;
                    if (tree_mode && c == 0) {
                        draw_rect.left += row->level * (float)tree_indent;
                        if (row->has_children || row->lazy) {
                            draw_text_ex(ctx, row->expanded ? L"⌄" : L"›", style, t->text_secondary, draw_rect.left + 4.0f, draw_rect.top, 18.0f, draw_rect.bottom - draw_rect.top, 1);
                            draw_rect.left += 18.0f;
                        }
                    }
                    bool cell_hovered = (r == m_hover_row && c == m_hover_col);
                    const TableCell& cell = row->cells[c];
                    if (cell.kind == TableCellKind::Index && cell.value.empty()) {
                        TableCell temp = cell;
                        temp.value = std::to_wstring(r + 1);
                        draw_control_cell(ctx, draw_rect, style, temp, ps.fg, t, ps.align, ps.flags, ps.font_size, cell_hovered);
                    } else {
                        draw_control_cell(ctx, draw_rect, style, cell, ps.fg, t, ps.align, ps.flags, ps.font_size, cell_hovered);
                    }
                    ctx.pop_clip();
                }
            }
            ctx.pop_clip();
        };

        paint_body_columns(0, scroll_clip);
        paint_body_columns(-1, fixed_left_clip);
        paint_body_columns(1, fixed_right_clip);
    }

    if (show_summary) {
        float y = table_h - style.pad_bottom - (float)sum_h;
        ctx.rt->FillRectangle({ left, y, left + table_w, y + (float)sum_h }, ctx.get_brush(dark ? 0xFF2D3145 : 0xFFF7FAFC));
        auto paint_summary_columns = [&](int fixed_kind, const D2D1_RECT_F& layer_clip) {
            if (!push_clip_if_visible(ctx, layer_clip)) return;
            for (int c = 0; c < col_count; ++c) {
                if (adv_columns[c].fixed != fixed_kind) continue;
                float x = column_x(c, left, table_w);
                float cw = column_width_at(c, table_w);
                D2D1_RECT_F cell_clip = intersect_rect({ x, y, x + cw, y + (float)sum_h }, layer_clip);
                if (push_clip_if_visible(ctx, cell_clip)) {
                    draw_text_ex(ctx, summary_for(*this, c), style, c == 0 ? t->text_primary : t->text_secondary, x + 10.0f, y, cw - 16.0f, (float)sum_h, c == 0 ? 0 : 2, 1);
                    ctx.pop_clip();
                }
            }
            ctx.pop_clip();
        };
        paint_summary_columns(0, scroll_clip);
        paint_summary_columns(-1, fixed_left_clip);
        paint_summary_columns(1, fixed_right_clip);
        ctx.rt->DrawLine(D2D1::Point2F(left, y), D2D1::Point2F(left + table_w, y), ctx.get_brush(border), 1.0f);
    }

    if (bordered) ctx.rt->DrawRectangle({ left, top, left + table_w, table_h - (float)style.pad_bottom }, ctx.get_brush(border), 1.0f);
    D2D1_RECT_F track{}, thumb{};
    if (vertical_scroll_track(*this, track) && vertical_scroll_thumb(*this, thumb)) {
        draw_scrollbar(ctx, track, thumb, t, m_scroll_drag == 1);
    }
    if (horizontal_scroll_track(*this, track) && horizontal_scroll_thumb(*this, thumb)) {
        draw_scrollbar(ctx, track, thumb, t, m_scroll_drag == 2);
    }
    if (is_editing_cell()) {
        D2D1_RECT_F edit_cell{};
        if (table_cell_rect(*this, editing_row, editing_col, edit_cell)) {
            D2D1_RECT_F editor{
                edit_cell.left + 4.0f,
                edit_cell.top + 4.0f,
                edit_cell.right - 4.0f,
                edit_cell.bottom - 4.0f
            };
            D2D1_RECT_F editor_clip = intersect_rect(editor, { left, body_top, left + table_w, table_bottom });
            if (push_clip_if_visible(ctx, editor_clip)) {
                Color editor_bg = dark ? 0xFF1F2433 : 0xFFFFFFFF;
                ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(editor, 5.0f, 5.0f), ctx.get_brush(editor_bg));
                ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(editor, 5.0f, 5.0f), ctx.get_brush(t->accent), 1.5f);

                float pad = 8.0f;
                float text_w = (std::max)(1.0f, editor.right - editor.left - pad * 2.0f);
                float text_h = (std::max)(1.0f, editor.bottom - editor.top);
                int cursor = (std::max)(0, (std::min)(editing_cursor, (int)editing_text.size()));
                std::wstring display = editing_text.substr(0, cursor) +
                    editing_composition_text + editing_text.substr(cursor);
                std::wstring layout_text = display.empty() ? L" " : display;
                IDWriteTextLayout* layout = ctx.create_text_layout(layout_text, style.font_name, style.font_size, text_w, text_h);
                if (layout) {
                    apply_emoji_font_fallback(layout, layout_text);
                    int align = editing_col < (int)adv_columns.size() ? adv_columns[editing_col].align : 0;
                    layout->SetTextAlignment(align == 1 ? DWRITE_TEXT_ALIGNMENT_CENTER :
                                             (align == 2 ? DWRITE_TEXT_ALIGNMENT_TRAILING : DWRITE_TEXT_ALIGNMENT_LEADING));
                    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
                    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
                    if (editing_sel_start >= 0 && editing_sel_end >= 0 && editing_sel_start != editing_sel_end) {
                        int s = editing_sel_start;
                        int e = editing_sel_end;
                        if (s > e) std::swap(s, e);
                        s = (std::max)(0, (std::min)(s, (int)editing_text.size()));
                        e = (std::max)(0, (std::min)(e, (int)editing_text.size()));
                        if (e > s) {
                            DWRITE_HIT_TEST_METRICS metrics[16]{};
                            UINT32 actual = 0;
                            if (SUCCEEDED(layout->HitTestTextRange((UINT32)s, (UINT32)(e - s), 0.0f, 0.0f,
                                                                   metrics, 16, &actual))) {
                                for (UINT32 i = 0; i < actual; ++i) {
                                    D2D1_RECT_F sr{
                                        editor.left + pad + metrics[i].left,
                                        editor.top + metrics[i].top,
                                        editor.left + pad + metrics[i].left + metrics[i].width,
                                        editor.top + metrics[i].top + metrics[i].height
                                    };
                                    ctx.rt->FillRectangle(sr, ctx.get_brush(dark ? 0xFF305A8A : 0xFFBBD7FF));
                                }
                            }
                        }
                    }
                    ctx.rt->DrawTextLayout(D2D1::Point2F(editor.left + pad, editor.top), layout,
                                           ctx.get_brush(t->text_primary), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
                    float cx = 0.0f, cy = 0.0f;
                    DWRITE_HIT_TEST_METRICS caret{};
                    UINT32 caret_pos = (UINT32)(cursor + (int)editing_composition_text.size());
                    if (SUCCEEDED(layout->HitTestTextPosition(caret_pos, FALSE, &cx, &cy, &caret))) {
                        float caret_x = editor.left + pad + cx;
                        float caret_top = editor.top + cy + 4.0f;
                        float caret_bottom = editor.top + cy + (caret.height > 1.0f ? caret.height : text_h) - 4.0f;
                        ctx.rt->DrawLine(D2D1::Point2F(caret_x, caret_top),
                                         D2D1::Point2F(caret_x, caret_bottom),
                                         ctx.get_brush(t->accent), 1.4f);
                    }
                    layout->Release();
                }
                ctx.pop_clip();
            }
        }
    }
    if (m_header_drag == 1 && m_header_drag_col >= 0 && m_header_drag_col < col_count) {
        float x = column_x(m_header_drag_col, left, table_w) + column_width_at(m_header_drag_col, table_w);
        ctx.rt->DrawLine(D2D1::Point2F(x, top), D2D1::Point2F(x, table_h - (float)style.pad_bottom),
                         ctx.get_brush(t->accent), 2.0f);
    } else if (m_header_drag == 2) {
        float y = top + (float)header_h;
        ctx.rt->DrawLine(D2D1::Point2F(left, y), D2D1::Point2F(left + table_w, y),
                         ctx.get_brush(t->accent), 2.0f);
    }
    if (m_hover_row >= 0 && m_hover_col >= 0 && m_hover_col < col_count && adv_columns[m_hover_col].overflow_tooltip) {
        std::wstring text = get_cell_value(m_hover_row, m_hover_col);
        if (text.size() > 12) {
            D2D1_RECT_F tip{ left + 24.0f, table_h - 42.0f, left + (std::min)(table_w - 24.0f, 520.0f), table_h - 12.0f };
            ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(tip, 5, 5), ctx.get_brush(0xEE111827));
            draw_text_ex(ctx, text, style, 0xFFFFFFFF, tip.left + 10.0f, tip.top, tip.right - tip.left - 20.0f, tip.bottom - tip.top, 0);
        }
    }

    ctx.pop_clip();

    if (popup_row >= 0 && popup_col >= 0 && popup_col < (int)adv_columns.size()) {
        D2D1_RECT_F popup{};
        if (table_popup_rect(*this, popup_row, popup_col, popup)) {
            const TableRow* popup_row_ptr = row_ptr(popup_row);
            if (popup_row_ptr && popup_col < (int)popup_row_ptr->cells.size()) {
                const TableCell& cell = popup_row_ptr->cells[popup_col];
                if (cell.parts.size() > 1) {
                ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(popup, 6, 6), ctx.get_brush(dark ? 0xFF262B40 : 0xFFF8FAFC));
                ctx.rt->DrawRoundedRectangle(D2D1::RoundedRect(popup, 6, 6), ctx.get_brush(border), 1.0f);
                float item_h = (std::max)(28.0f, (float)row_height_px());
                for (int i = 0; i < (int)cell.parts.size(); ++i) {
                    D2D1_RECT_F item{ popup.left + 1.0f, popup.top + i * item_h + 1.0f, popup.right - 1.0f, popup.top + (i + 1) * item_h - 1.0f };
                    if (item.bottom > popup.bottom - 1.0f) item.bottom = popup.bottom - 1.0f;
                    if (i == popup_hover || cell.parts[i] == cell.value) {
                        ctx.rt->FillRectangle(item, ctx.get_brush(dark ? 0xFF30466B : 0xFFEAF2FF));
                    }
                    draw_text_ex(ctx, cell.parts[i], style, i == popup_hover ? t->accent : t->text_primary, item.left + 10.0f, item.top, item.right - item.left - 20.0f, item.bottom - item.top, 0, 0, (std::max)(11.0f, style.font_size - 1.0f));
                }
                }
            }
        }
    }

    ctx.rt->SetTransform(saved);
}
