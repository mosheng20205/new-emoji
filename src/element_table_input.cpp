#include "element_table.h"
#include "render_context.h"
#include <algorithm>
#include <cmath>
#include <cwctype>
#include <map>

static bool point_in_rect(float x, float y, const D2D1_RECT_F& r) {
    return x >= r.left && x < r.right && y >= r.top && y < r.bottom;
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

static bool table_has_grouped_header(const Table& table) {
    for (const auto& col : table.adv_columns) if (!col.parent_title.empty()) return true;
    return false;
}

static int header_resize_column_at(const Table& table, int x, int y) {
    if (!table.header_column_resize || !table.show_header) return -1;
    int top = table.style.pad_top;
    int header_h = table.header_height_px();
    if (y < top || y >= top + header_h) return -1;
    float left = (float)table.style.pad_left;
    float table_w = (float)table.bounds.w - table.style.pad_left - table.style.pad_right;
    float hit = 5.0f;
    for (int c = 0; c < (int)table.adv_columns.size(); ++c) {
        float cx = table.column_x(c, left, table_w);
        float cw = table.column_width_at(c, table_w);
        if (cw <= 0.0f) continue;
        float edge = cx + cw;
        if ((float)x >= edge - hit && (float)x <= edge + hit) return c;
    }
    return -1;
}

static bool header_height_resize_hit(const Table& table, int x, int y) {
    if (!table.header_height_resize || !table.show_header) return false;
    float left = (float)table.style.pad_left;
    float right = (float)table.bounds.w - (float)table.style.pad_right;
    float edge = (float)table.style.pad_top + (float)table.header_height_px();
    return (float)x >= left && (float)x <= right && std::fabs((float)y - edge) <= 5.0f;
}

int Table::header_height_px() const {
    if (!show_header) return 0;
    bool grouped = false;
    for (const auto& col : adv_columns) if (!col.parent_title.empty()) grouped = true;
    int base = (std::max)(header_height_value, (int)(style.font_size * 2.15f));
    return grouped ? base * 2 : base;
}

int Table::row_height_px() const {
    return (std::max)(row_height_value, (int)(style.font_size * 2.0f));
}

int Table::summary_height_px() const {
    return show_summary ? row_height_px() : 0;
}

int Table::table_height_px() const {
    int h = bounds.h;
    if (max_height_value > 0) h = (std::min)(h, max_height_value);
    return (std::max)(0, h);
}

int Table::visible_row_count() const {
    int body_h = table_height_px() - style.pad_top - style.pad_bottom - header_height_px() - summary_height_px();
    if (needs_horizontal_scrollbar()) body_h -= (int)kScrollbarSize;
    int visible_rows = row_height_px() > 0 ? body_h / row_height_px() : 0;
    return (std::max)(1, visible_rows);
}

int Table::max_scroll_row() const {
    int total = virtual_mode ? virtual_row_count : (int)visible_row_indices().size();
    return (std::max)(0, total - visible_row_count());
}

int Table::max_scroll_x() const {
    if (!horizontal_scroll) return 0;
    float table_w = (float)bounds.w - style.pad_left - style.pad_right;
    float fixed_left = 0.0f;
    float fixed_right = 0.0f;
    float normal_total = 0.0f;
    for (int c = 0; c < (int)adv_columns.size(); ++c) {
        float cw = column_width_at(c, table_w);
        if (adv_columns[c].fixed == -1) fixed_left += cw;
        else if (adv_columns[c].fixed == 1) fixed_right += cw;
        else normal_total += cw;
    }
    float viewport = (std::max)(0.0f, table_w - fixed_left - fixed_right);
    return (int)(std::max)(0.0f, normal_total - viewport);
}

bool Table::needs_vertical_scrollbar() const {
    return max_scroll_row() > 0;
}

bool Table::needs_horizontal_scrollbar() const {
    return max_scroll_x() > 0;
}

float Table::column_width_at(int col, float table_w) const {
    if (col < 0 || col >= (int)adv_columns.size()) return 0.0f;
    auto base_width = [this](int index) -> float {
        if (index < 0 || index >= (int)adv_columns.size()) return 0.0f;
        if (adv_columns[index].width > 0) return (float)adv_columns[index].width;
        if (fixed_column_width > 0) return (float)fixed_column_width;
        return (float)adv_columns[index].min_width;
    };

    float fixed_total = 0.0f;
    float normal_total = 0.0f;
    int grow_progress = -1;
    for (int i = 0; i < (int)adv_columns.size(); ++i) {
        float cw = base_width(i);
        if (adv_columns[i].fixed == 0) {
            normal_total += cw;
            if (grow_progress < 0 && adv_columns[i].type == (int)TableCellKind::Progress) {
                grow_progress = i;
            }
        } else {
            fixed_total += cw;
        }
    }

    float width = base_width(col);
    if (adv_columns[col].fixed == 0 && col == grow_progress) {
        float available_normal = (std::max)(0.0f, table_w - fixed_total);
        float extra = available_normal - normal_total;
        if (extra > 0.0f) width += extra;
    }
    return (std::max)((float)adv_columns[col].min_width, width);
}

float Table::column_x(int col, float left, float table_w) const {
    if (col < 0 || col >= (int)adv_columns.size()) return left;
    const int fixed = adv_columns[col].fixed;
    if (fixed == -1) {
        float x = left;
        for (int i = 0; i < col; ++i) if (adv_columns[i].fixed == -1) x += column_width_at(i, table_w);
        return x;
    }
    if (fixed == 1) {
        float x = left + table_w;
        for (int i = (int)adv_columns.size() - 1; i >= col; --i) {
            if (adv_columns[i].fixed == 1) x -= column_width_at(i, table_w);
        }
        return x;
    }
    float x = left - (horizontal_scroll ? (float)scroll_x : 0.0f);
    for (int i = 0; i < (int)adv_columns.size(); ++i) if (adv_columns[i].fixed == -1) x += column_width_at(i, table_w);
    for (int i = 0; i < col; ++i) if (adv_columns[i].fixed == 0) x += column_width_at(i, table_w);
    return x;
}

static bool row_matches_filter(const TableRow& row, const std::map<int, std::wstring>& filters) {
    for (const auto& pair : filters) {
        int col = pair.first;
        if (pair.second.empty()) continue;
        if (col < 0 || col >= (int)row.cells.size()) return false;
        if (row.cells[col].value != pair.second) return false;
    }
    return true;
}

static bool row_matches_search(const TableRow& row, const std::vector<TableColumn>& cols,
                               const std::wstring& search) {
    if (search.empty()) return true;
    for (int i = 0; i < (int)row.cells.size(); ++i) {
        if (i < (int)cols.size() && !cols[i].searchable) continue;
        std::wstring v = row.cells[i].value;
        std::transform(v.begin(), v.end(), v.begin(), [](wchar_t ch) { return (wchar_t)std::towlower(ch); });
        if (v.find(search) != std::wstring::npos) return true;
    }
    return false;
}

std::vector<int> Table::visible_row_indices() const {
    if (virtual_mode) {
        std::vector<int> out;
        out.reserve((size_t)virtual_row_count);
        for (int i = 0; i < virtual_row_count; ++i) out.push_back(i);
        return out;
    }
    std::vector<int> out;
    std::map<std::wstring, int> by_key;
    for (int i = 0; i < (int)adv_rows.size(); ++i) if (!adv_rows[i].key.empty()) by_key[adv_rows[i].key] = i;
    for (int i = 0; i < (int)adv_rows.size(); ++i) {
        const TableRow& row = adv_rows[i];
        if (!row_matches_filter(row, filters) || !row_matches_search(row, adv_columns, search_text)) continue;
        bool hidden_by_parent = false;
        if (tree_mode) {
            std::wstring parent = row.parent_key;
            int guard = 0;
            while (!parent.empty() && guard++ < 64) {
                auto it = by_key.find(parent);
                if (it == by_key.end()) break;
                const TableRow& p = adv_rows[it->second];
                if (!p.expanded) { hidden_by_parent = true; break; }
                parent = p.parent_key;
            }
        }
        if (!hidden_by_parent) out.push_back(i);
    }
    return out;
}

void Table::clamp_scroll() {
    int max_scroll = max_scroll_row();
    if (scroll_row < 0) scroll_row = 0;
    if (scroll_row > max_scroll) scroll_row = max_scroll;
    if (scroll_x < 0) scroll_x = 0;
    if (!horizontal_scroll) {
        scroll_x = 0;
    } else {
        int max_x = max_scroll_x();
        if (scroll_x > max_x) scroll_x = max_x;
    }
}

int Table::row_at(int x, int y) const {
    D2D1_RECT_F vtrack{}, htrack{};
    if ((vertical_scroll_track(*this, vtrack) && point_in_rect((float)x, (float)y, vtrack)) ||
        (horizontal_scroll_track(*this, htrack) && point_in_rect((float)x, (float)y, htrack))) {
        return -1;
    }
    if (x < style.pad_left || x >= bounds.w - style.pad_right) return -1;
    int local_y = y - style.pad_top - header_height_px();
    int body_h = table_height_px() - style.pad_top - style.pad_bottom - header_height_px() - summary_height_px();
    if (needs_horizontal_scrollbar()) body_h -= (int)kScrollbarSize;
    if (local_y < 0 || local_y >= body_h || row_height_px() <= 0) return -1;
    int visible_slot = local_y / row_height_px() + scroll_row;
    if (virtual_mode) {
        return (visible_slot >= 0 && visible_slot < virtual_row_count) ? visible_slot : -1;
    }
    auto visible = visible_row_indices();
    if (visible_slot < 0 || visible_slot >= (int)visible.size()) return -1;
    return visible[visible_slot];
}

int Table::column_at(int x, int) const {
    float left = (float)style.pad_left;
    float table_w = (float)bounds.w - style.pad_left - style.pad_right;
    for (int c = (int)adv_columns.size() - 1; c >= 0; --c) {
        float cx = column_x(c, left, table_w);
        float cw = column_width_at(c, table_w);
        if ((float)x >= cx && (float)x < cx + cw) return c;
    }
    return -1;
}

bool Table::is_span_hidden(int row, int col) const {
    for (const auto& sp : spans) {
        if (row == sp.row && col == sp.col) return false;
        if (row >= sp.row && row < sp.row + sp.rowspan && col >= sp.col && col < sp.col + sp.colspan) return true;
    }
    return false;
}

TableSpan Table::span_for(int row, int col) const {
    for (const auto& sp : spans) if (sp.row == row && sp.col == col) return sp;
    return { row, col, 1, 1 };
}

void Table::on_mouse_move(int x, int y) {
    if (m_header_drag == 1) {
        if (m_header_drag_col >= 0 && m_header_drag_col < (int)adv_columns.size()) {
            int width = m_header_drag_origin + (x - m_header_drag_start);
            width = (std::max)(header_min_col_width, (std::min)(header_max_col_width, width));
            adv_columns[m_header_drag_col].width = width;
            clamp_scroll();
            invalidate();
        }
        return;
    }
    if (m_header_drag == 2) {
        int total = m_header_drag_origin + (y - m_header_drag_start);
        total = (std::max)(header_min_height, (std::min)(header_max_height, total));
        header_height_value = table_has_grouped_header(*this) ? (std::max)(1, total / 2) : total;
        clamp_scroll();
        invalidate();
        return;
    }

    if (m_scroll_drag == 1) {
        D2D1_RECT_F track{}, thumb{};
        if (vertical_scroll_track(*this, track) && vertical_scroll_thumb(*this, thumb)) {
            float track_h = (track.bottom - track.top - kScrollbarPad * 2.0f);
            float thumb_h = thumb.bottom - thumb.top;
            float travel = (std::max)(1.0f, track_h - thumb_h);
            int max_row = max_scroll_row();
            scroll_row = m_scroll_drag_origin + (int)std::lround((float)(y - m_scroll_drag_start) * (float)max_row / travel);
            clamp_scroll();
            invalidate();
        }
        return;
    }
    if (m_scroll_drag == 2) {
        D2D1_RECT_F track{}, thumb{};
        if (horizontal_scroll_track(*this, track) && horizontal_scroll_thumb(*this, thumb)) {
            float track_w = (track.right - track.left - kScrollbarPad * 2.0f);
            float thumb_w = thumb.right - thumb.left;
            float travel = (std::max)(1.0f, track_w - thumb_w);
            int max_x = max_scroll_x();
            scroll_x = m_scroll_drag_origin + (int)std::lround((float)(x - m_scroll_drag_start) * (float)max_x / travel);
            clamp_scroll();
            invalidate();
        }
        return;
    }

    int r = row_at(x, y);
    int c = column_at(x, y);
    if (popup_row >= 0 && popup_col >= 0) {
        D2D1_RECT_F pop{};
        if (table_popup_rect(*this, popup_row, popup_col, pop) && point_in_rect((float)x, (float)y, pop)) {
            int item_h = (std::max)(28, row_height_px());
            popup_hover = (int)((y - pop.top) / item_h);
            const TableRow* popup_row_ptr = row_ptr(popup_row);
            if (!popup_row_ptr || popup_col < 0 || popup_col >= (int)popup_row_ptr->cells.size()) popup_hover = -1;
            else if (popup_hover >= (int)popup_row_ptr->cells[popup_col].parts.size()) popup_hover = (int)popup_row_ptr->cells[popup_col].parts.size() - 1;
        } else {
            popup_hover = -1;
        }
    }
    if (r != m_hover_row || c != m_hover_col) {
        m_hover_row = r;
        m_hover_col = c;
        invalidate();
    }
}

void Table::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_scroll_drag = 0;
    m_header_drag = 0;
    m_header_drag_col = -1;
    m_hover_row = m_hover_col = m_press_row = m_press_col = -1;
    popup_row = popup_col = -1;
    popup_hover = -1;
    invalidate();
}

void Table::on_mouse_down(int x, int y, MouseButton) {
    if (header_height_resize_hit(*this, x, y)) {
        m_header_drag = 2;
        m_header_drag_col = -1;
        m_header_drag_start = y;
        m_header_drag_origin = header_height_px();
        pressed = true;
        invalidate();
        return;
    }
    int resize_col = header_resize_column_at(*this, x, y);
    if (resize_col >= 0) {
        float table_w = (float)bounds.w - style.pad_left - style.pad_right;
        m_header_drag = 1;
        m_header_drag_col = resize_col;
        m_header_drag_start = x;
        m_header_drag_origin = (int)column_width_at(resize_col, table_w);
        if (adv_columns[resize_col].width <= 0) adv_columns[resize_col].width = m_header_drag_origin;
        pressed = true;
        invalidate();
        return;
    }

    D2D1_RECT_F track{}, thumb{};
    if (vertical_scroll_track(*this, track) && point_in_rect((float)x, (float)y, track)) {
        if (vertical_scroll_thumb(*this, thumb) && point_in_rect((float)x, (float)y, thumb)) {
            m_scroll_drag = 1;
            m_scroll_drag_start = y;
            m_scroll_drag_origin = scroll_row;
        } else {
            scroll_row += ((float)y < thumb.top) ? -visible_row_count() : visible_row_count();
            clamp_scroll();
        }
        pressed = true;
        invalidate();
        return;
    }
    if (horizontal_scroll_track(*this, track) && point_in_rect((float)x, (float)y, track)) {
        if (horizontal_scroll_thumb(*this, thumb) && point_in_rect((float)x, (float)y, thumb)) {
            m_scroll_drag = 2;
            m_scroll_drag_start = x;
            m_scroll_drag_origin = scroll_x;
        } else {
            float viewport_step = (float)bounds.w - style.pad_left - style.pad_right;
            scroll_x += ((float)x < thumb.left) ? -(int)viewport_step : (int)viewport_step;
            clamp_scroll();
        }
        pressed = true;
        invalidate();
        return;
    }

    if (popup_row >= 0 && popup_col >= 0) {
        D2D1_RECT_F pop{};
        if (!table_popup_rect(*this, popup_row, popup_col, pop) || !point_in_rect((float)x, (float)y, pop)) {
            popup_row = popup_col = -1;
            popup_hover = -1;
        }
    }
    m_press_row = row_at(x, y);
    m_press_col = column_at(x, y);
    m_press_action = 0;
    pressed = true;
    invalidate();
}

void Table::on_mouse_up(int x, int y, MouseButton) {
    if (m_header_drag != 0) {
        m_header_drag = 0;
        m_header_drag_col = -1;
        pressed = false;
        clamp_scroll();
        invalidate();
        return;
    }
    if (m_scroll_drag != 0) {
        m_scroll_drag = 0;
        pressed = false;
        invalidate();
        return;
    }
    if (popup_row >= 0 && popup_col >= 0) {
        D2D1_RECT_F pop{};
        if (table_popup_rect(*this, popup_row, popup_col, pop) && point_in_rect((float)x, (float)y, pop)) {
            int item_h = (std::max)(28, row_height_px());
            int idx = (int)((y - pop.top) / item_h);
            int sel_row = popup_row;
            int sel_col = popup_col;
            TableRow* popup_row_ptr = row_ptr(sel_row);
            if (popup_row_ptr && sel_col >= 0 && sel_col < (int)popup_row_ptr->cells.size()) {
                TableCell& popup_cell = popup_row_ptr->cells[sel_col];
                if (idx >= 0 && idx < (int)popup_cell.parts.size()) {
                    popup_cell.value = popup_cell.parts[idx];
                    if (!virtual_mode) sync_legacy_vectors();
                    popup_row = popup_col = -1;
                    popup_hover = -1;
                    invoke_cell(sel_row, sel_col, 5, idx);
                    invalidate();
                    return;
                }
            }
            if (!virtual_mode) sync_legacy_vectors();
        }
        popup_row = popup_col = -1;
        popup_hover = -1;
    }
    int row = row_at(x, y);
    int col = column_at(x, y);
    if (row >= 0 && col >= 0 && row == m_press_row && col == m_press_col) {
        TableRow* row_ptr_val = row_ptr(row);
        if (!row_ptr_val || col < 0 || col >= (int)row_ptr_val->cells.size()) {
            m_press_row = m_press_col = -1;
            pressed = false;
            return;
        }
        TableCell& cell = row_ptr_val->cells[col];
        invoke_cell_click(row, col);
        int action = 1;
        int value = 0;
        if (cell.kind == TableCellKind::Selection || (selection_mode == 2 && col == 0)) {
            auto it = std::find(selected_rows.begin(), selected_rows.end(), row);
            bool was_selected = it != selected_rows.end();
            if (!was_selected) selected_rows.push_back(row); else selected_rows.erase(it);
            selected_row = selected_rows.empty() ? -1 : selected_rows.front();
            sync_selection_cells();
            action = 2; value = was_selected ? 0 : 1;
        } else if (cell.kind == TableCellKind::Expand) {
            row_ptr_val->expanded = !row_ptr_val->expanded;
            action = 3; value = row_ptr_val->expanded ? 1 : 0;
        } else if (cell.kind == TableCellKind::Switch) {
            cell.checked = !cell.checked;
            cell.value = cell.checked ? L"1" : L"0";
            action = 4; value = cell.checked ? 1 : 0;
        } else if ((cell.kind == TableCellKind::Select || cell.kind == TableCellKind::Combo) && cell.parts.size() > 1) {
            popup_row = row;
            popup_col = col;
            popup_hover = -1;
            action = 5; value = 0;
        } else if (cell.kind == TableCellKind::Button || cell.kind == TableCellKind::Buttons) {
            action = 6; value = col;
        } else if (selection_mode == 1 && selectable && row_ptr_val->selectable) {
            set_selected_row(row);
            action = 7; value = row;
        }
        if (!virtual_mode) sync_legacy_vectors();
        invoke_cell(row, col, action, value);
    } else if (row < 0 && y >= style.pad_top && y < style.pad_top + header_height_px() && col >= 0) {
        if (col < (int)adv_columns.size() && adv_columns[col].sortable) {
            set_sort(col, sort_column == col ? !sort_desc : false);
            invoke_cell(-1, col, 8, sort_desc ? 1 : 0);
        }
    }
    m_press_row = m_press_col = -1;
    pressed = false;
    clamp_scroll();
    invalidate();
}

void Table::on_mouse_wheel(int, int, int delta) {
    scroll_row += delta < 0 ? 1 : -1;
    clamp_scroll();
    invalidate();
}

void Table::on_key_down(int vk, int) {
    if (!selectable || row_count() <= 0) return;
    if (virtual_mode) {
        int pos = selected_row < 0 ? 0 : selected_row;
        if (vk == VK_UP) pos = (std::max)(0, pos - 1);
        else if (vk == VK_DOWN) pos = (std::min)(row_count() - 1, pos + 1);
        else if (vk == VK_HOME) pos = 0;
        else if (vk == VK_END) pos = row_count() - 1;
        else return;
        set_selected_row(pos);
        return;
    }
    auto visible = visible_row_indices();
    if (visible.empty()) return;
    auto it = std::find(visible.begin(), visible.end(), selected_row);
    int pos = it == visible.end() ? 0 : (int)(it - visible.begin());
    if (vk == VK_UP) pos = (std::max)(0, pos - 1);
    else if (vk == VK_DOWN) pos = (std::min)((int)visible.size() - 1, pos + 1);
    else if (vk == VK_HOME) pos = 0;
    else if (vk == VK_END) pos = (int)visible.size() - 1;
    else return;
    set_selected_row(visible[pos]);
}
