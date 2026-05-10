#include "element_table.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cwctype>
#include <sstream>

static std::wstring lower_key(std::wstring s) {
    std::transform(s.begin(), s.end(), s.begin(), [](wchar_t ch) { return (wchar_t)std::towlower(ch); });
    return s;
}

static int to_int(const std::wstring& s, int fallback = 0) {
    if (s.empty()) return fallback;
    return _wtoi(s.c_str());
}

static bool to_bool(const std::wstring& s, bool fallback = false) {
    if (s.empty()) return fallback;
    std::wstring v = lower_key(s);
    return v == L"1" || v == L"true" || v == L"yes" || v == L"on" || v == L"是";
}

static std::vector<std::wstring> split_escaped(const std::wstring& s, wchar_t sep) {
    std::vector<std::wstring> out;
    std::wstring cur;
    bool esc = false;
    for (wchar_t ch : s) {
        if (esc) {
            if (ch == L'n') cur.push_back(L'\n');
            else if (ch == L't') cur.push_back(L'\t');
            else cur.push_back(ch);
            esc = false;
        } else if (ch == L'\\') {
            esc = true;
        } else if (ch == sep) {
            out.push_back(cur);
            cur.clear();
        } else {
            cur.push_back(ch);
        }
    }
    out.push_back(cur);
    return out;
}

static std::map<std::wstring, std::wstring> parse_kv(const std::wstring& line) {
    std::map<std::wstring, std::wstring> kv;
    int unnamed = 0;
    for (const auto& field : split_escaped(line, L'\t')) {
        if (field.empty()) continue;
        size_t pos = field.find(L'=');
        if (pos == std::wstring::npos) kv[L"$" + std::to_wstring(unnamed++)] = field;
        else kv[lower_key(field.substr(0, pos))] = field.substr(pos + 1);
    }
    return kv;
}

static std::wstring kv_get(const std::map<std::wstring, std::wstring>& kv,
                           const std::wstring& key, const std::wstring& fallback = L"") {
    auto it = kv.find(lower_key(key));
    return it == kv.end() ? fallback : it->second;
}

static TableCellKind kind_from_text(const std::wstring& value) {
    std::wstring v = lower_key(value);
    if (v == L"index") return TableCellKind::Index;
    if (v == L"selection") return TableCellKind::Selection;
    if (v == L"expand") return TableCellKind::Expand;
    if (v == L"button") return TableCellKind::Button;
    if (v == L"buttons") return TableCellKind::Buttons;
    if (v == L"combo") return TableCellKind::Combo;
    if (v == L"switch") return TableCellKind::Switch;
    if (v == L"select") return TableCellKind::Select;
    if (v == L"progress") return TableCellKind::Progress;
    if (v == L"status") return TableCellKind::Status;
    if (v == L"tag") return TableCellKind::Tag;
    if (v == L"popover_tag") return TableCellKind::PopoverTag;
    return TableCellKind::Text;
}

static TableCellKind kind_from_int(int value) {
    if (value < 0 || value > 12) return TableCellKind::Text;
    return (TableCellKind)value;
}

static std::wstring join_parts(const std::vector<std::wstring>& parts) {
    std::wstring out;
    for (size_t i = 0; i < parts.size(); ++i) {
        if (i) out.push_back(L'|');
        out += parts[i];
    }
    return out;
}

static int align_from_text(const std::wstring& value, int fallback = 0) {
    std::wstring v = lower_key(value);
    if (v == L"center" || v == L"居中") return 1;
    if (v == L"right" || v == L"end" || v == L"右") return 2;
    if (v == L"left" || v == L"start" || v == L"左") return 0;
    return value.empty() ? fallback : to_int(value, fallback);
}

static void apply_style(TableStyleOverride& s, Color bg, Color fg, int align, int flags, int font_size) {
    if (bg) { s.has_bg = true; s.bg = bg; }
    if (fg) { s.has_fg = true; s.fg = fg; }
    if (align >= 0) { s.has_align = true; s.align = align; }
    if (flags >= 0) { s.has_font_flags = true; s.font_flags = flags; }
    if (font_size > 0) { s.has_font_size = true; s.font_size = font_size; }
}

static std::wstring fetch_virtual_row_text(const Table& table, int row) {
    if (!table.virtual_row_cb) return L"";
    int needed = table.virtual_row_cb(table.id, row, nullptr, 0);
    if (needed < 0) needed = 0;
    std::vector<unsigned char> buffer((size_t)needed + 1);
    int written = table.virtual_row_cb(table.id, row, buffer.data(), (int)buffer.size());
    if (written < 0) written = 0;
    if (written > (int)buffer.size()) written = (int)buffer.size();
    return utf8_to_wide(buffer.data(), written);
}

bool Table::is_virtual_active() const {
    return virtual_mode && virtual_row_count > 0;
}

TableRow Table::parse_row_line(const std::wstring& line, int row_index) const {
    auto kv = parse_kv(line);
    TableRow row;
    row.key = kv_get(kv, L"key", L"r" + std::to_wstring(row_index));
    row.parent_key = kv_get(kv, L"parent");
    row.level = to_int(kv_get(kv, L"level"), 0);
    row.expanded = to_bool(kv_get(kv, L"expanded"), false);
    row.has_children = to_bool(kv_get(kv, L"children"), false) || to_bool(kv_get(kv, L"haschildren"), false);
    row.lazy = to_bool(kv_get(kv, L"lazy"), false);
    row.selectable = !to_bool(kv_get(kv, L"disabled"), false);
    apply_style(row.style, (Color)to_int(kv_get(kv, L"bg"), 0),
                (Color)to_int(kv_get(kv, L"fg"), 0),
                align_from_text(kv_get(kv, L"align"), -1),
                to_int(kv_get(kv, L"font_flags"), -1),
                to_int(kv_get(kv, L"font_size"), 0));
    int unnamed = 0;
    for (int c = 0; c < (int)adv_columns.size(); ++c) {
        TableCell cell;
        std::wstring base = L"c" + std::to_wstring(c);
        cell.value = kv_get(kv, base, kv_get(kv, L"$" + std::to_wstring(unnamed++)));
        cell.kind = kind_from_int(adv_columns[c].type);
        std::wstring type = kv_get(kv, base + L"_type");
        if (!type.empty()) cell.kind = kind_from_text(type);
        cell.parts = split_escaped(cell.value, L'|');
        cell.options = parse_kv(kv_get(kv, base + L"_options"));
        cell.checked = to_bool(cell.value, false) || to_bool(kv_get(cell.options, L"checked"), false);
        cell.number = to_int(cell.value, to_int(kv_get(cell.options, L"value"), 0));
        cell.status = to_int(kv_get(cell.options, L"status"), cell.number);
        if ((cell.kind == TableCellKind::Select || cell.kind == TableCellKind::Combo) && !cell.parts.empty()) {
            if (cell.value.find(L'|') != std::wstring::npos || cell.value.empty()) {
                cell.value = cell.parts.front();
            }
        }
        row.cells.push_back(cell);
    }
    ensure_cell_count(row);
    return row;
}

void Table::apply_selection_state(TableRow& row, int row_index) const {
    bool checked = std::find(selected_rows.begin(), selected_rows.end(), row_index) != selected_rows.end();
    if (selection_mode == 1 && selected_row == row_index) checked = true;
    for (auto& cell : row.cells) {
        if (cell.kind == TableCellKind::Selection) {
            cell.checked = checked;
            cell.value = checked ? L"1" : L"0";
        }
    }
}

bool Table::ensure_virtual_row(int row) const {
    if (!is_virtual_active() || row < 0 || row >= virtual_row_count) return false;
    auto it = virtual_cache.find(row);
    if (it != virtual_cache.end()) return true;
    TableRow loaded = parse_row_line(fetch_virtual_row_text(*this, row), row);
    apply_selection_state(loaded, row);
    if (!loaded.key.empty() && loaded.key == L"r" + std::to_wstring(row)) {
        // keep provider key if supplied, but ensure stable default exists
    }
    virtual_cache.emplace(row, std::move(loaded));
    return true;
}

void Table::ensure_cell_count(TableRow& row) const {
    while ((int)row.cells.size() < (int)adv_columns.size()) row.cells.push_back({});
}

void Table::sync_legacy_vectors() {
    columns.clear();
    rows.clear();
    for (const auto& col : adv_columns) columns.push_back(col.title);
    if (is_virtual_active()) return;
    for (const auto& row : adv_rows) {
        std::vector<std::wstring> out;
        for (const auto& cell : row.cells) out.push_back(cell.value);
        rows.push_back(out);
    }
}

void Table::sync_selection_cells() {
    if (is_virtual_active()) {
        for (auto& entry : virtual_cache) {
            apply_selection_state(entry.second, entry.first);
        }
        return;
    }
    for (int r = 0; r < (int)adv_rows.size(); ++r) {
        bool checked = std::find(selected_rows.begin(), selected_rows.end(), r) != selected_rows.end();
        if (selection_mode == 1 && selected_row == r) checked = true;
        for (auto& cell : adv_rows[r].cells) {
            if (cell.kind == TableCellKind::Selection) {
                cell.checked = checked;
                cell.value = checked ? L"1" : L"0";
            }
        }
    }
}

void Table::set_columns(const std::vector<std::wstring>& values) {
    if (is_editing_cell()) commit_cell_edit();
    clear_virtual_cache();
    adv_columns.clear();
    for (size_t i = 0; i < values.size(); ++i) {
        TableColumn c;
        c.title = values[i];
        c.key = L"c" + std::to_wstring((int)i);
        c.width = fixed_column_width;
        adv_columns.push_back(c);
    }
    if (adv_columns.empty()) adv_columns.push_back({ L"c0", L"列", L"", 0 });
    for (auto& row : adv_rows) ensure_cell_count(row);
    sync_legacy_vectors();
    invalidate();
}

void Table::set_rows(const std::vector<std::vector<std::wstring>>& values) {
    if (is_editing_cell()) commit_cell_edit();
    virtual_mode = false;
    virtual_row_count = 0;
    clear_virtual_cache();
    adv_rows.clear();
    for (size_t r = 0; r < values.size(); ++r) {
        TableRow row;
        row.key = L"r" + std::to_wstring((int)r);
        for (const auto& value : values[r]) {
            TableCell cell;
            cell.value = value;
            row.cells.push_back(cell);
        }
        ensure_cell_count(row);
        adv_rows.push_back(row);
    }
    set_sort(sort_column, sort_desc);
    clamp_scroll();
    sync_legacy_vectors();
    invalidate();
}

void Table::set_columns_ex(const std::wstring& spec) {
    if (is_editing_cell()) commit_cell_edit();
    clear_virtual_cache();
    adv_columns.clear();
    for (const auto& line : split_escaped(spec, L'\n')) {
        if (line.empty()) continue;
        auto kv = parse_kv(line);
        TableColumn c;
        c.title = kv_get(kv, L"title", kv_get(kv, L"label", kv_get(kv, L"$0", L"列")));
        c.key = kv_get(kv, L"key", L"c" + std::to_wstring((int)adv_columns.size()));
        c.parent_title = kv_get(kv, L"parent");
        c.width = to_int(kv_get(kv, L"width"), 0);
        c.min_width = to_int(kv_get(kv, L"min_width"), 80);
        std::wstring fixed = lower_key(kv_get(kv, L"fixed"));
        c.fixed = fixed == L"left" ? -1 : (fixed == L"right" ? 1 : to_int(fixed, 0));
        c.type = (int)kind_from_text(kv_get(kv, L"type"));
        int default_align = (c.type == (int)TableCellKind::Tag ||
                             c.type == (int)TableCellKind::PopoverTag) ? 1 : 0;
        c.align = align_from_text(kv_get(kv, L"align"), default_align);
        c.sortable = to_bool(kv_get(kv, L"sortable"), false);
        c.filterable = to_bool(kv_get(kv, L"filterable"), false);
        c.searchable = to_bool(kv_get(kv, L"searchable"), true);
        c.overflow_tooltip = to_bool(kv_get(kv, L"tooltip"), false);
        c.options = split_escaped(kv_get(kv, L"options"), L'|');
        apply_style(c.style, (Color)to_int(kv_get(kv, L"bg"), 0),
                    (Color)to_int(kv_get(kv, L"fg"), 0), c.align, -1,
                    to_int(kv_get(kv, L"font_size"), 0));
        adv_columns.push_back(c);
    }
    if (adv_columns.empty()) set_columns({ L"名称", L"状态" });
    for (auto& row : adv_rows) ensure_cell_count(row);
    sync_legacy_vectors();
    invalidate();
}

void Table::set_rows_ex(const std::wstring& spec) {
    if (is_editing_cell()) commit_cell_edit();
    virtual_mode = false;
    virtual_row_count = 0;
    clear_virtual_cache();
    adv_rows.clear();
    for (const auto& line : split_escaped(spec, L'\n')) {
        if (line.empty()) continue;
        auto kv = parse_kv(line);
        TableRow row;
        row.key = kv_get(kv, L"key", L"r" + std::to_wstring((int)adv_rows.size()));
        row.parent_key = kv_get(kv, L"parent");
        row.level = to_int(kv_get(kv, L"level"), 0);
        row.expanded = to_bool(kv_get(kv, L"expanded"), false);
        row.has_children = to_bool(kv_get(kv, L"children"), false) || to_bool(kv_get(kv, L"haschildren"), false);
        row.lazy = to_bool(kv_get(kv, L"lazy"), false);
        row.selectable = !to_bool(kv_get(kv, L"disabled"), false);
        apply_style(row.style, (Color)to_int(kv_get(kv, L"bg"), 0),
                    (Color)to_int(kv_get(kv, L"fg"), 0),
                    align_from_text(kv_get(kv, L"align"), -1),
                    to_int(kv_get(kv, L"font_flags"), -1),
                    to_int(kv_get(kv, L"font_size"), 0));
        int unnamed = 0;
        for (int c = 0; c < (int)adv_columns.size(); ++c) {
            TableCell cell;
            std::wstring base = L"c" + std::to_wstring(c);
            cell.value = kv_get(kv, base, kv_get(kv, L"$" + std::to_wstring(unnamed++)));
            cell.kind = kind_from_int(adv_columns[c].type);
            std::wstring type = kv_get(kv, base + L"_type");
            if (!type.empty()) cell.kind = kind_from_text(type);
            cell.parts = split_escaped(cell.value, L'|');
            cell.options = parse_kv(kv_get(kv, base + L"_options"));
            cell.checked = to_bool(cell.value, false) || to_bool(kv_get(cell.options, L"checked"), false);
            cell.number = to_int(cell.value, to_int(kv_get(cell.options, L"value"), 0));
            cell.status = to_int(kv_get(cell.options, L"status"), cell.number);
            if ((cell.kind == TableCellKind::Select || cell.kind == TableCellKind::Combo) && !cell.parts.empty()) {
                if (cell.value.find(L'|') != std::wstring::npos || cell.value.empty()) {
                    cell.value = cell.parts.front();
                }
            }
            row.cells.push_back(cell);
        }
        ensure_cell_count(row);
        adv_rows.push_back(row);
    }
    set_sort(sort_column, sort_desc);
    clamp_scroll();
    sync_selection_cells();
    sync_legacy_vectors();
    invalidate();
}

int Table::add_row_ex(const std::wstring& spec) {
    return insert_row_ex((int)adv_rows.size(), spec);
}

int Table::insert_row_ex(int row_index, const std::wstring& spec) {
    if (is_editing_cell()) commit_cell_edit();
    if (virtual_mode || row_index < 0) return -1;
    if (row_index > (int)adv_rows.size()) row_index = (int)adv_rows.size();

    std::wstring line = spec;
    size_t line_end = line.find_first_of(L"\r\n");
    if (line_end != std::wstring::npos) line = line.substr(0, line_end);

    TableRow row = parse_row_line(line, row_index);
    adv_rows.insert(adv_rows.begin() + row_index, std::move(row));

    if (selected_row >= row_index) ++selected_row;
    for (int& selected : selected_rows) {
        if (selected >= row_index) ++selected;
    }
    for (auto& span : spans) {
        if (span.row >= row_index) ++span.row;
        else if (span.row + span.rowspan > row_index) ++span.rowspan;
    }

    int actual_index = row_index;
    std::wstring inserted_key = adv_rows[row_index].key;
    if (sort_column >= 0 && !tree_mode) {
        std::wstring selected_key = (selected_row >= 0 && selected_row < (int)adv_rows.size()) ? adv_rows[selected_row].key : L"";
        std::vector<std::wstring> selected_keys;
        for (int selected : selected_rows) {
            if (selected >= 0 && selected < (int)adv_rows.size()) selected_keys.push_back(adv_rows[selected].key);
        }
        set_sort(sort_column, sort_desc);
        if (!selected_key.empty()) {
            selected_row = -1;
            for (int i = 0; i < (int)adv_rows.size(); ++i) {
                if (adv_rows[i].key == selected_key) {
                    selected_row = i;
                    break;
                }
            }
        }
        if (!selected_keys.empty()) {
            selected_rows.clear();
            for (const auto& key : selected_keys) {
                for (int i = 0; i < (int)adv_rows.size(); ++i) {
                    if (adv_rows[i].key == key) {
                        selected_rows.push_back(i);
                        break;
                    }
                }
            }
        }
        clamp_scroll();
        sync_selection_cells();
        sync_legacy_vectors();
        invalidate();
        for (int i = 0; i < (int)adv_rows.size(); ++i) {
            if (adv_rows[i].key == inserted_key) {
                actual_index = i;
                break;
            }
        }
    } else {
        clamp_scroll();
        sync_selection_cells();
        sync_legacy_vectors();
        invalidate();
        invalidate();
    }
    return actual_index;
}

bool Table::delete_row(int row_index) {
    if (is_editing_cell()) commit_cell_edit();
    if (virtual_mode || row_index < 0 || row_index >= (int)adv_rows.size()) return false;
    adv_rows.erase(adv_rows.begin() + row_index);

    if (selected_row == row_index) selected_row = -1;
    else if (selected_row > row_index) --selected_row;

    std::vector<int> next_selected;
    for (int selected : selected_rows) {
        if (selected == row_index) continue;
        next_selected.push_back(selected > row_index ? selected - 1 : selected);
    }
    selected_rows = std::move(next_selected);
    if (selection_mode == 2 && selected_row < 0 && !selected_rows.empty()) selected_row = selected_rows.front();

    std::vector<TableSpan> next_spans;
    for (auto span : spans) {
        if (span.row == row_index) continue;
        if (span.row > row_index) --span.row;
        else if (span.row + span.rowspan > row_index) {
            --span.rowspan;
            if (span.rowspan <= 0) continue;
        }
        next_spans.push_back(span);
    }
    spans = std::move(next_spans);

    if (sort_column >= 0 && !tree_mode) {
        std::wstring selected_key = (selected_row >= 0 && selected_row < (int)adv_rows.size()) ? adv_rows[selected_row].key : L"";
        std::vector<std::wstring> selected_keys;
        for (int selected : selected_rows) {
            if (selected >= 0 && selected < (int)adv_rows.size()) selected_keys.push_back(adv_rows[selected].key);
        }
        set_sort(sort_column, sort_desc);
        if (!selected_key.empty()) {
            selected_row = -1;
            for (int i = 0; i < (int)adv_rows.size(); ++i) {
                if (adv_rows[i].key == selected_key) {
                    selected_row = i;
                    break;
                }
            }
        }
        if (!selected_keys.empty()) {
            selected_rows.clear();
            for (const auto& key : selected_keys) {
                for (int i = 0; i < (int)adv_rows.size(); ++i) {
                    if (adv_rows[i].key == key) {
                        selected_rows.push_back(i);
                        break;
                    }
                }
            }
        }
        clamp_scroll();
        sync_selection_cells();
        sync_legacy_vectors();
    } else {
        clamp_scroll();
        sync_selection_cells();
        sync_legacy_vectors();
        invalidate();
    }
    return true;
}

bool Table::clear_rows() {
    if (is_editing_cell()) commit_cell_edit();
    if (virtual_mode) return false;
    adv_rows.clear();
    selected_row = -1;
    selected_rows.clear();
    spans.clear();
    scroll_row = 0;
    scroll_x = 0;
    clear_virtual_cache();
    sync_legacy_vectors();
    invalidate();
    return true;
}

void Table::set_cell_ex(int row, int col, int type, const std::wstring& value, const std::wstring& options) {
    if (is_editing_cell()) commit_cell_edit();
    if (row < 0 || col < 0) return;
    if (virtual_mode) {
        if (!ensure_virtual_row(row)) return;
        auto it = virtual_cache.find(row);
        if (it == virtual_cache.end()) return;
        ensure_cell_count(it->second);
        if (col >= (int)it->second.cells.size()) return;
        TableCell& cell = it->second.cells[col];
        cell.kind = kind_from_int(type);
        cell.value = value;
        cell.parts = split_escaped(value, L'|');
        cell.options = parse_kv(options);
        cell.checked = to_bool(value, false) || to_bool(kv_get(cell.options, L"checked"), false);
        cell.number = to_int(value, to_int(kv_get(cell.options, L"value"), 0));
        cell.status = to_int(kv_get(cell.options, L"status"), cell.number);
        if ((cell.kind == TableCellKind::Select || cell.kind == TableCellKind::Combo) && !cell.parts.empty()) {
            if (cell.value.find(L'|') != std::wstring::npos || cell.value.empty()) {
                cell.value = cell.parts.front();
            }
        }
        apply_selection_state(it->second, row);
        invalidate();
        return;
    }
    while (row >= (int)adv_rows.size()) {
        TableRow r;
        r.key = L"r" + std::to_wstring((int)adv_rows.size());
        ensure_cell_count(r);
        adv_rows.push_back(r);
    }
    ensure_cell_count(adv_rows[row]);
    if (col >= (int)adv_rows[row].cells.size()) return;
    TableCell& cell = adv_rows[row].cells[col];
    cell.kind = kind_from_int(type);
    cell.value = value;
    cell.parts = split_escaped(value, L'|');
    cell.options = parse_kv(options);
    cell.checked = to_bool(value, false) || to_bool(kv_get(cell.options, L"checked"), false);
    cell.number = to_int(value, to_int(kv_get(cell.options, L"value"), 0));
    cell.status = to_int(kv_get(cell.options, L"status"), cell.number);
    if ((cell.kind == TableCellKind::Select || cell.kind == TableCellKind::Combo) && !cell.parts.empty()) {
        if (cell.value.find(L'|') != std::wstring::npos || cell.value.empty()) {
            cell.value = cell.parts.front();
        }
    }
    sync_legacy_vectors();
    invalidate();
}

void Table::set_row_style(int row, Color bg, Color fg, int align, int flags, int font_size) {
    TableRow* target = row_ptr(row);
    if (!target) return;
    apply_style(target->style, bg, fg, align, flags, font_size);
    invalidate();
}

void Table::set_cell_style(int row, int col, Color bg, Color fg, int align, int flags, int font_size) {
    TableRow* target = row_ptr(row);
    if (!target || col < 0) return;
    ensure_cell_count(*target);
    if (col >= (int)target->cells.size()) return;
    apply_style(target->cells[col].style, bg, fg, align, flags, font_size);
    invalidate();
}

void Table::set_striped(bool value) { striped = value; invalidate(); }
void Table::set_bordered(bool value) { bordered = value; invalidate(); }
void Table::set_empty_text(const std::wstring& value) { empty_text = value.empty() ? L"暂无数据" : value; invalidate(); }

void Table::set_selection_mode(int mode) {
    if (mode < 0) mode = 0;
    if (mode > 2) mode = 2;
    selection_mode = mode;
    selectable = mode != 0;
    if (!selectable) { selected_row = -1; selected_rows.clear(); }
    sync_selection_cells();
    invalidate();
}

void Table::set_selected_row(int value) {
    if (!selectable || row_count() <= 0) selected_row = -1;
    else {
        if (value < -1) value = -1;
        if (value >= row_count()) value = row_count() - 1;
        selected_row = value;
        if (selection_mode == 2 && value >= 0) selected_rows = { value };
    }
    sync_selection_cells();
    invalidate();
}

void Table::set_selected_rows_text(const std::wstring& spec) {
    selected_rows.clear();
    for (const auto& part : split_escaped(spec, L'|')) {
        int idx = to_int(part, -1);
        if (idx >= 0 && idx < row_count()) selected_rows.push_back(idx);
    }
    if (!selected_rows.empty()) selected_row = selected_rows.front();
    sync_selection_cells();
    invalidate();
}

void Table::set_options(bool striped_value, bool bordered_value, int row_height, int header_height, bool selectable_value) {
    striped = striped_value;
    bordered = bordered_value;
    row_height_value = (std::min)(80, (std::max)(24, row_height));
    header_height_value = (std::min)(90, (std::max)(26, header_height));
    set_selection_mode(selectable_value ? selection_mode == 0 ? 1 : selection_mode : 0);
    clamp_scroll();
    invalidate();
}

void Table::set_sort(int column_index, bool desc) {
    if (is_editing_cell()) commit_cell_edit();
    sort_column = column_index;
    sort_desc = desc;
    if (!is_virtual_active() && sort_column >= 0 && !tree_mode) {
        std::sort(adv_rows.begin(), adv_rows.end(), [this](const TableRow& a, const TableRow& b) {
            std::wstring av = sort_column < (int)a.cells.size() ? a.cells[sort_column].value : L"";
            std::wstring bv = sort_column < (int)b.cells.size() ? b.cells[sort_column].value : L"";
            int cmp = _wcsicmp(av.c_str(), bv.c_str());
            return sort_desc ? cmp > 0 : cmp < 0;
        });
    }
    sync_legacy_vectors();
    invalidate();
}

void Table::set_filter(int col, const std::wstring& value) { if (is_editing_cell()) commit_cell_edit(); if (col >= 0) filters[col] = value; clamp_scroll(); invalidate(); }
void Table::clear_filter(int col) { if (is_editing_cell()) commit_cell_edit(); if (col < 0) filters.clear(); else filters.erase(col); clamp_scroll(); invalidate(); }
void Table::set_search(const std::wstring& value) { if (is_editing_cell()) commit_cell_edit(); search_text = lower_key(value); clamp_scroll(); invalidate(); }
void Table::set_scroll_row(int value) { if (is_editing_cell()) commit_cell_edit(); scroll_row = value; clamp_scroll(); invalidate(); }
void Table::set_column_width(int value) { fixed_column_width = (std::min)(480, (std::max)(0, value)); for (auto& c : adv_columns) if (!c.width) c.width = fixed_column_width; invalidate(); }
void Table::set_scroll(int row, int x) { if (is_editing_cell()) commit_cell_edit(); scroll_row = row; scroll_x = (std::max)(0, x); clamp_scroll(); invalidate(); }
void Table::set_header_drag_options(bool column_resize, bool height_resize,
                                    int min_col_width, int max_col_width,
                                    int min_header_height, int max_header_height) {
    header_column_resize = column_resize;
    header_height_resize = height_resize;
    header_min_col_width = (std::max)(24, min_col_width);
    header_max_col_width = (std::max)(header_min_col_width, max_col_width);
    header_min_height = (std::max)(24, min_header_height);
    header_max_height = (std::max)(header_min_height, max_header_height);
    m_header_drag = 0;
    m_header_drag_col = -1;
    invalidate();
}
void Table::set_tree_options(bool enabled, int indent, bool lazy) { tree_mode = enabled; tree_indent = (std::max)(8, indent); lazy_mode = lazy; invalidate(); }
void Table::set_viewport_options(int max_height, bool fh, bool hs, bool ss) { max_height_value = max_height; fixed_header = fh; horizontal_scroll = hs; show_summary = ss; clamp_scroll(); invalidate(); }

static int table_edit_override_value(int value) {
    if (value < -1) return -1;
    if (value > 1) return 1;
    return value;
}

void Table::set_double_click_edit(bool enabled) {
    if (!enabled && is_editing_cell()) commit_cell_edit();
    double_click_edit_enabled = enabled;
    invalidate();
}

void Table::set_column_double_click_edit(int col, int editable) {
    if (col < 0) return;
    int value = table_edit_override_value(editable);
    if (value == -1) column_editable_overrides.erase(col);
    else column_editable_overrides[col] = value;
    if (is_editing_cell() && editing_col == col && !is_cell_double_click_editable(editing_row, editing_col)) {
        commit_cell_edit();
    }
    invalidate();
}

void Table::set_cell_double_click_edit(int row, int col, int editable) {
    if (row < 0 || col < 0) return;
    int value = table_edit_override_value(editable);
    std::pair<int, int> key(row, col);
    if (value == -1) cell_editable_overrides.erase(key);
    else cell_editable_overrides[key] = value;
    if (is_editing_cell() && editing_row == row && editing_col == col &&
        !is_cell_double_click_editable(editing_row, editing_col)) {
        commit_cell_edit();
    }
    invalidate();
}

bool Table::is_cell_double_click_editable(int row, int col) const {
    if (!double_click_edit_enabled || is_virtual_active()) return false;
    const TableRow* target = row_ptr(row);
    if (!target || col < 0 || col >= (int)target->cells.size()) return false;
    if (target->cells[col].kind != TableCellKind::Text) return false;
    auto cell_it = cell_editable_overrides.find(std::pair<int, int>(row, col));
    if (cell_it != cell_editable_overrides.end()) return cell_it->second == 1;
    auto col_it = column_editable_overrides.find(col);
    if (col_it != column_editable_overrides.end()) return col_it->second == 1;
    return true;
}

void Table::set_span(int row, int col, int rowspan, int colspan) {
    if (row < 0 || col < 0) return;
    spans.push_back({ row, col, (std::max)(1, rowspan), (std::max)(1, colspan) });
    invalidate();
}

void Table::clear_spans() { spans.clear(); invalidate(); }
void Table::set_row_expanded(int row, bool expanded) {
    TableRow* target = row_ptr(row);
    if (!target) return;
    target->expanded = expanded;
    invalidate();
}

void Table::set_summary(const std::wstring& spec) {
    summary_values = split_escaped(spec, L'|');
    show_summary = true;
    invalidate();
}

void Table::invoke_cell(int row, int col, int action, int value) {
    if (cell_cb) cell_cb(id, row, col, action, value);
}

void Table::invoke_cell_click(int row, int col) {
    if (cell_click_cb) cell_click_cb(id, row, col, 1, 0);
}

void Table::invoke_cell_edit(int row, int col, int action, const std::wstring& value) {
    if (!cell_edit_cb) return;
    std::string utf8 = wide_to_utf8(value);
    cell_edit_cb(id, row, col, action,
                 reinterpret_cast<const unsigned char*>(utf8.data()),
                 (int)utf8.size());
}

bool Table::is_editing_cell() const {
    return editing_row >= 0 && editing_col >= 0;
}

void Table::clear_cell_edit_state() {
    editing_row = -1;
    editing_col = -1;
    editing_original_text.clear();
    editing_text.clear();
    editing_composition_text.clear();
    editing_cursor = 0;
    editing_sel_start = -1;
    editing_sel_end = -1;
    editing_composing = false;
}

bool Table::begin_cell_edit(int row, int col) {
    if (!is_cell_double_click_editable(row, col)) return false;
    if (is_editing_cell()) {
        if (editing_row == row && editing_col == col) return true;
        commit_cell_edit();
    }
    const TableRow* target = row_ptr(row);
    if (!target || col < 0 || col >= (int)target->cells.size()) return false;
    editing_row = row;
    editing_col = col;
    editing_original_text = target->cells[col].value;
    editing_text = editing_original_text;
    editing_composition_text.clear();
    editing_cursor = (int)editing_text.size();
    editing_sel_start = -1;
    editing_sel_end = -1;
    editing_composing = false;
    invoke_cell_edit(row, col, 1, editing_text);
    invalidate();
    return true;
}

void Table::commit_cell_edit() {
    if (!is_editing_cell()) return;
    int row = editing_row;
    int col = editing_col;
    int cursor = (std::max)(0, (std::min)(editing_cursor, (int)editing_text.size()));
    std::wstring value = editing_text.substr(0, cursor) +
        editing_composition_text + editing_text.substr(cursor);
    TableRow* target = row_ptr(row);
    if (target && col >= 0 && col < (int)target->cells.size() &&
        target->cells[col].kind == TableCellKind::Text && !is_virtual_active()) {
        target->cells[col].value = value;
        sync_legacy_vectors();
    }
    clear_cell_edit_state();
    invoke_cell_edit(row, col, 2, value);
    invalidate();
}

void Table::cancel_cell_edit() {
    if (!is_editing_cell()) return;
    int row = editing_row;
    int col = editing_col;
    std::wstring value = editing_original_text;
    clear_cell_edit_state();
    invoke_cell_edit(row, col, 3, value);
    invalidate();
}

std::wstring Table::get_cell_value(int row, int col) const {
    const TableRow* target = row_ptr(row);
    if (!target || col < 0 || col >= (int)target->cells.size()) return L"";
    return target->cells[col].value;
}

std::wstring Table::full_state_text() const {
    std::wstringstream ss;
    ss << L"rows=" << row_count() << L"\tcols=" << adv_columns.size()
       << L"\tselected=" << selected_row << L"\tscroll_row=" << scroll_row
       << L"\tscroll_x=" << scroll_x << L"\tfilters=" << filters.size()
       << L"\tsearch=" << search_text
       << L"\tvirtual=" << (is_virtual_active() ? 1 : 0);
    return ss.str();
}

int Table::row_count() const {
    return is_virtual_active() ? virtual_row_count : (int)adv_rows.size();
}

void Table::clear_virtual_cache() {
    virtual_cache.clear();
}

void Table::set_virtual_options(bool enabled, int row_count_value, int cache_window_value) {
    if (is_editing_cell()) commit_cell_edit();
    virtual_mode = enabled && row_count_value > 0;
    virtual_row_count = (std::max)(0, row_count_value);
    virtual_cache_window = (std::max)(0, cache_window_value);
    clear_virtual_cache();
    clamp_scroll();
    invalidate();
}

void Table::set_virtual_row_provider(TableVirtualRowCallback cb) {
    if (is_editing_cell()) commit_cell_edit();
    virtual_row_cb = cb;
    clear_virtual_cache();
    invalidate();
}

const TableRow* Table::row_ptr(int row) const {
    if (row < 0 || row >= row_count()) return nullptr;
    if (!is_virtual_active()) {
        if (row >= (int)adv_rows.size()) return nullptr;
        return &adv_rows[row];
    }
    ensure_virtual_row(row);
    auto it = virtual_cache.find(row);
    return it == virtual_cache.end() ? nullptr : &it->second;
}

TableRow* Table::row_ptr(int row) {
    return const_cast<TableRow*>(static_cast<const Table*>(this)->row_ptr(row));
}
