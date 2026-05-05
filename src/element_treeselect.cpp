#include "element_treeselect.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cwctype>
#include <sstream>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color ts_with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static std::wstring ts_lower(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(), [](wchar_t ch) {
        return (wchar_t)towlower(ch);
    });
    return value;
}

static std::wstring ts_json_escape(const std::wstring& value) {
    std::wstring out;
    for (wchar_t ch : value) {
        if (ch == L'\\') out += L"\\\\";
        else if (ch == L'"') out += L"\\\"";
        else if (ch == L'\n') out += L"\\n";
        else if (ch == L'\r') out += L"\\r";
        else if (ch == L'\t') out += L"\\t";
        else out.push_back(ch);
    }
    return out;
}

static bool json_has_true(const std::wstring& json, const wchar_t* name, bool fallback) {
    std::wstring key = L"\"" + std::wstring(name) + L"\"";
    size_t p = json.find(key);
    if (p == std::wstring::npos) return fallback;
    size_t colon = json.find(L":", p + key.size());
    if (colon == std::wstring::npos) return fallback;
    size_t v = json.find_first_not_of(L" \t\r\n", colon + 1);
    if (v == std::wstring::npos) return fallback;
    if (json.compare(v, 4, L"true") == 0 || json.compare(v, 1, L"1") == 0) return true;
    if (json.compare(v, 5, L"false") == 0 || json.compare(v, 1, L"0") == 0) return false;
    return fallback;
}

static std::wstring json_string_value(const std::wstring& json, const wchar_t* name, const std::wstring& fallback) {
    std::wstring key = L"\"" + std::wstring(name) + L"\"";
    size_t p = json.find(key);
    if (p == std::wstring::npos) return fallback;
    size_t colon = json.find(L":", p + key.size());
    if (colon == std::wstring::npos) return fallback;
    size_t v = json.find_first_not_of(L" \t\r\n", colon + 1);
    if (v == std::wstring::npos || json[v] != L'"') return fallback;
    ++v;
    std::wstring out;
    while (v < json.size()) {
        wchar_t ch = json[v++];
        if (ch == L'"') break;
        if (ch == L'\\' && v < json.size()) {
            wchar_t esc = json[v++];
            switch (esc) {
            case L'"': out.push_back(L'"'); break;
            case L'\\': out.push_back(L'\\'); break;
            case L'/': out.push_back(L'/'); break;
            case L'n': out.push_back(L'\n'); break;
            case L'r': out.push_back(L'\r'); break;
            case L't': out.push_back(L'\t'); break;
            default: out.push_back(esc); break;
            }
        } else {
            out.push_back(ch);
        }
    }
    return out;
}

static void ts_draw_text(RenderContext& ctx, const std::wstring& text,
                         const ElementStyle& style, Color color,
                         float x, float y, float w, float h,
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

int TreeSelect::popup_width() const {
    return (std::max)(bounds.w, 280);
}

int TreeSelect::popup_height() const {
    return searchable ? 250 : 220;
}

int TreeSelect::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

int TreeSelect::row_height() const {
    int h = (int)(style.font_size * 2.1f);
    return h < 30 ? 30 : h;
}

void TreeSelect::set_items(const std::vector<TreeViewItem>& values) {
    items = values;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[i].key.empty()) items[i].key = std::to_wstring(i);
    }
    if (items.empty()) selected_index = -1;
    else if (selected_index < 0 || selected_index >= (int)items.size()) selected_index = 0;
    sync_single_from_multi();
    invalidate();
}

void TreeSelect::set_selected_index(int value) {
    if (items.empty()) selected_index = -1;
    else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        selected_index = value;
        if (!multiple) selected_indices = { selected_index };
    }
    invalidate();
}

void TreeSelect::set_open(bool next_open) {
    open = next_open;
    invalidate();
}

bool TreeSelect::is_open() const {
    return open;
}

void TreeSelect::set_options(bool next_multiple, bool next_clearable, bool next_searchable) {
    multiple = next_multiple;
    clearable = next_clearable;
    searchable = next_searchable;
    if (!multiple && selected_indices.size() > 1) {
        selected_indices = selected_index >= 0 ? std::vector<int>{ selected_index } : std::vector<int>{};
    } else if (multiple && selected_indices.empty() && selected_index >= 0) {
        selected_indices = { selected_index };
    }
    invalidate();
}

void TreeSelect::set_search_text(const std::wstring& value) {
    search_text = value;
    m_hover_index = -1;
    if (!search_text.empty()) open = true;
    invalidate();
}

void TreeSelect::clear_selection() {
    selected_index = -1;
    selected_indices.clear();
    invalidate();
}

void TreeSelect::set_selected_items(const std::vector<int>& indices) {
    selected_indices.clear();
    for (int index : indices) {
        if (index >= 0 && index < (int)items.size() &&
            std::find(selected_indices.begin(), selected_indices.end(), index) == selected_indices.end()) {
            selected_indices.push_back(index);
        }
    }
    sync_single_from_multi();
    invalidate();
}

int TreeSelect::selected_count() const {
    return multiple ? (int)selected_indices.size() : (selected_index >= 0 ? 1 : 0);
}

int TreeSelect::selected_item(int position) const {
    if (multiple) {
        if (position < 0 || position >= (int)selected_indices.size()) return -1;
        return selected_indices[position];
    }
    return position == 0 ? selected_index : -1;
}

int TreeSelect::matched_count() const {
    int count = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_rendered_item(i)) ++count;
    }
    return count;
}

void TreeSelect::set_item_expanded(int index, bool expanded) {
    if (index < 0 || index >= (int)items.size()) return;
    if (!has_children(index) && !items[index].lazy) return;
    set_expanded_internal(index, expanded);
    invalidate();
}

void TreeSelect::toggle_item_expanded(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    set_item_expanded(index, !items[index].expanded);
}

bool TreeSelect::get_item_expanded(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].expanded;
}

void TreeSelect::set_data_json(const std::wstring& json) {
    std::vector<std::wstring> expanded;
    std::vector<std::wstring> selected;
    std::wstring current;
    std::wstring filter;
    set_items(parse_tree_json_items(json, &expanded, &selected, &current, &filter, nullptr));
    if (!expanded.empty()) set_expanded_keys(expanded);
    if (!selected.empty()) set_selected_keys(selected);
    if (!current.empty()) {
        int idx = index_by_key(current);
        if (idx >= 0) set_selected_index(idx);
    }
    if (!filter.empty()) search_text = filter;
    set_options_json(json);
    invalidate();
}

std::wstring TreeSelect::data_json() const {
    return serialize_tree_json_items(items);
}

void TreeSelect::set_options_json(const std::wstring& json) {
    multiple = json_has_true(json, L"multiple", multiple);
    clearable = json_has_true(json, L"clearable", clearable);
    searchable = json_has_true(json, L"searchable", searchable);
    open = json_has_true(json, L"open", open);
    m_check_strictly = json_has_true(json, L"checkStrictly", m_check_strictly);
    m_accordion = json_has_true(json, L"accordion", m_accordion);
    m_draggable = json_has_true(json, L"draggable", m_draggable);
    m_show_actions = json_has_true(json, L"showActions", m_show_actions);
    search_text = json_string_value(json, L"searchText",
        json_string_value(json, L"filterText", search_text));
    invalidate();
}

std::wstring TreeSelect::state_json() const {
    std::wstringstream ss;
    ss << L"{";
    ss << L"\"selectedIndex\":" << selected_index << L",";
    ss << L"\"selectedKeys\":" << serialize_tree_key_array_json(selected_keys()) << L",";
    ss << L"\"expandedKeys\":" << serialize_tree_key_array_json(expanded_keys()) << L",";
    ss << L"\"open\":" << (open ? L"true" : L"false") << L",";
    ss << L"\"multiple\":" << (multiple ? L"true" : L"false") << L",";
    ss << L"\"clearable\":" << (clearable ? L"true" : L"false") << L",";
    ss << L"\"searchable\":" << (searchable ? L"true" : L"false") << L",";
    ss << L"\"searchText\":\"" << ts_json_escape(search_text) << L"\",";
    ss << L"\"matchedCount\":" << matched_count() << L",";
    ss << L"\"lastLazyIndex\":" << m_last_lazy_index << L",";
    ss << L"\"dragEventCount\":" << m_drag_event_count;
    ss << L"}";
    return ss.str();
}

void TreeSelect::set_selected_keys(const std::vector<std::wstring>& keys) {
    selected_indices.clear();
    for (const auto& key : keys) {
        int idx = index_by_key(key);
        if (idx >= 0 && !items[idx].disabled &&
            std::find(selected_indices.begin(), selected_indices.end(), idx) == selected_indices.end()) {
            selected_indices.push_back(idx);
            if (!multiple) break;
        }
    }
    selected_index = selected_indices.empty() ? -1 : selected_indices[0];
    invalidate();
}

std::vector<std::wstring> TreeSelect::selected_keys() const {
    std::vector<std::wstring> keys;
    if (multiple) {
        for (int index : selected_indices) keys.push_back(key_at(index));
    } else if (selected_index >= 0) {
        keys.push_back(key_at(selected_index));
    }
    return keys;
}

void TreeSelect::set_expanded_keys(const std::vector<std::wstring>& keys) {
    for (auto& item : items) item.expanded = false;
    for (const auto& key : keys) {
        int idx = index_by_key(key);
        if (idx >= 0) set_expanded_internal(idx, true);
    }
    invalidate();
}

std::vector<std::wstring> TreeSelect::expanded_keys() const {
    std::vector<std::wstring> keys;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[i].expanded && (has_children(i) || items[i].lazy)) keys.push_back(key_at(i));
    }
    return keys;
}

void TreeSelect::append_node_json(const std::wstring& parent_key, const std::wstring& json) {
    std::vector<TreeViewItem> nodes = parse_tree_json_items(json);
    int parent = index_by_key(parent_key);
    int insert_at = parent >= 0 ? subtree_end(parent) : (int)items.size();
    int base_level = parent >= 0 ? items[parent].level + 1 : 0;
    bool expand_parent_after_append = false;
    if (parent >= 0) {
        expand_parent_after_append = items[parent].lazy || items[parent].loading;
    }
    for (auto& node : nodes) node.level += base_level;
    items.insert(items.begin() + insert_at, nodes.begin(), nodes.end());
    if (parent >= 0) {
        items[parent].lazy = false;
        items[parent].loading = false;
        if (expand_parent_after_append) items[parent].expanded = true;
        items[parent].leaf = false;
    }
    invalidate();
}

void TreeSelect::update_node_json(const std::wstring& key, const std::wstring& json) {
    int idx = index_by_key(key);
    if (idx < 0) return;
    std::vector<TreeViewItem> nodes = parse_tree_json_items(json);
    if (nodes.empty()) return;
    int keep_level = items[idx].level;
    TreeViewItem next = nodes[0];
    next.level = keep_level;
    if (next.key.empty()) next.key = key;
    items[idx] = next;
    invalidate();
}

void TreeSelect::remove_node_by_key(const std::wstring& key) {
    int idx = index_by_key(key);
    if (idx < 0) return;
    int end = subtree_end(idx);
    items.erase(items.begin() + idx, items.begin() + end);
    selected_indices.erase(std::remove_if(selected_indices.begin(), selected_indices.end(),
        [idx, end](int v) { return v >= idx && v < end; }), selected_indices.end());
    for (int& v : selected_indices) if (v >= end) v -= (end - idx);
    selected_index = selected_indices.empty() ? -1 : selected_indices[0];
    invalidate();
}

int TreeSelect::index_by_key(const std::wstring& key) const {
    for (int i = 0; i < (int)items.size(); ++i) {
        if (key_at(i) == key) return i;
    }
    return -1;
}

std::wstring TreeSelect::key_at(int index) const {
    if (index < 0 || index >= (int)items.size()) return L"";
    return items[index].key.empty() ? std::to_wstring(index) : items[index].key;
}

bool TreeSelect::has_children(int index) const {
    if (index < 0 || index + 1 >= (int)items.size()) return false;
    return items[index + 1].level > items[index].level;
}

bool TreeSelect::is_visible_item(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    int level = items[index].level;
    for (int i = index - 1; i >= 0; --i) {
        if (items[i].level < level) {
            if (!items[i].expanded) return false;
            level = items[i].level;
        }
    }
    return true;
}

bool TreeSelect::matches_filter(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    if (search_text.empty()) return true;
    std::wstring needle = ts_lower(search_text);
    std::wstring text = ts_lower(items[index].label + L" " + items[index].key + L" " + items[index].tag);
    return text.find(needle) != std::wstring::npos;
}

bool TreeSelect::is_rendered_item(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    if (search_text.empty()) return is_visible_item(index);
    if (!is_visible_item(index)) return false;
    if (matches_filter(index)) return true;
    int end = subtree_end(index);
    for (int i = index + 1; i < end; ++i) {
        if (matches_filter(i)) return true;
    }
    int p = parent_index(index);
    while (p >= 0) {
        if (matches_filter(p)) return true;
        p = parent_index(p);
    }
    return false;
}

int TreeSelect::item_at(int x, int y) const {
    if (!open) return -1;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    if (x < 0 || x >= pw || y < py || y >= py + ph) return -1;
    int cy = py + style.pad_top + (searchable ? row_height() : 0);
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_rendered_item(i)) continue;
        if (y >= cy && y < cy + row_height()) return i;
        cy += row_height();
        if (cy >= py + ph - style.pad_bottom) break;
    }
    return -1;
}

std::wstring TreeSelect::selected_text() const {
    if (multiple) {
        if (selected_indices.empty()) return L"请选择";
        if (selected_indices.size() == 1) {
            int index = selected_indices[0];
            if (index >= 0 && index < (int)items.size()) return items[index].label;
        }
        return L"已选择 " + std::to_wstring(selected_indices.size()) + L" 项";
    }
    if (selected_index >= 0 && selected_index < (int)items.size()) return items[selected_index].label;
    return L"请选择";
}

void TreeSelect::sync_single_from_multi() {
    if (!selected_indices.empty()) {
        selected_index = selected_indices[0];
    } else if (selected_index >= 0 && selected_index < (int)items.size()) {
        if (multiple) selected_indices = { selected_index };
    } else {
        selected_index = items.empty() ? -1 : 0;
        if (multiple && selected_index >= 0) selected_indices = { selected_index };
    }
}

bool TreeSelect::is_selected_multi(int index) const {
    if (multiple) {
        return std::find(selected_indices.begin(), selected_indices.end(), index) != selected_indices.end();
    }
    return index == selected_index;
}

void TreeSelect::toggle_selected_multi(int index) {
    if (index < 0 || index >= (int)items.size() || items[index].disabled) return;
    if (!multiple) {
        selected_index = index;
        selected_indices = { index };
        emit_event(event_cb, 2, index);
        return;
    }
    auto it = std::find(selected_indices.begin(), selected_indices.end(), index);
    if (it == selected_indices.end()) selected_indices.push_back(index);
    else selected_indices.erase(it);
    selected_index = selected_indices.empty() ? -1 : selected_indices[0];
    emit_event(event_cb, 2, index);
}

int TreeSelect::first_rendered_index() const {
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_rendered_item(i)) return i;
    }
    return -1;
}

int TreeSelect::next_rendered_index(int from, int delta) const {
    if (items.empty()) return -1;
    if (from < 0) return first_rendered_index();
    int i = from + delta;
    while (i >= 0 && i < (int)items.size()) {
        if (is_rendered_item(i)) return i;
        i += delta;
    }
    return from;
}

int TreeSelect::parent_index(int index) const {
    if (index <= 0 || index >= (int)items.size()) return -1;
    int level = items[index].level;
    for (int i = index - 1; i >= 0; --i) {
        if (items[i].level < level) return i;
    }
    return -1;
}

int TreeSelect::subtree_end(int index) const {
    if (index < 0 || index >= (int)items.size()) return index;
    int level = items[index].level;
    int i = index + 1;
    while (i < (int)items.size() && items[i].level > level) ++i;
    return i;
}

void TreeSelect::set_expanded_internal(int index, bool expanded) {
    if (index < 0 || index >= (int)items.size() || items[index].disabled) return;
    if (expanded && m_accordion) {
        int p = parent_index(index);
        int level = items[index].level;
        int start = p >= 0 ? p + 1 : 0;
        int end = p >= 0 ? subtree_end(p) : (int)items.size();
        for (int i = start; i < end; ++i) {
            if (i != index && items[i].level == level) items[i].expanded = false;
        }
    }
    if (expanded && items[index].lazy) {
        m_last_lazy_index = index;
        items[index].loading = true;
        emit_event(lazy_cb, 10, index);
    }
    items[index].expanded = expanded;
    emit_event(event_cb, expanded ? 3 : 4, index);
}

void TreeSelect::emit_event(TreeNodeEventCallback cb, int event_code, int index, int extra) {
    if (!cb) return;
    std::string payload = wide_to_utf8(tree_item_event_json(items, index, extra));
    cb(id, event_code, index, (const unsigned char*)payload.data(), (int)payload.size());
}

bool TreeSelect::can_drag(int index) const {
    if (!m_draggable || index < 0 || index >= (int)items.size() || items[index].disabled) return false;
    if (!allow_drag_cb) return true;
    std::string key = wide_to_utf8(key_at(index));
    return allow_drag_cb(id, (const unsigned char*)key.data(), (int)key.size()) != 0;
}

bool TreeSelect::can_drop(int drag_index, int drop_index, int drop_type) const {
    if (drag_index < 0 || drop_index < 0 || drag_index == drop_index) return false;
    int drag_end = subtree_end(drag_index);
    if (drop_index > drag_index && drop_index < drag_end) return false;
    if (items[drop_index].disabled) return false;
    if (drop_type == 1 && items[drop_index].leaf) return false;
    if (!allow_drop_cb) return true;
    std::string drag_key = wide_to_utf8(key_at(drag_index));
    std::string drop_key = wide_to_utf8(key_at(drop_index));
    return allow_drop_cb(id,
        (const unsigned char*)drag_key.data(), (int)drag_key.size(),
        (const unsigned char*)drop_key.data(), (int)drop_key.size(),
        drop_type) != 0;
}

void TreeSelect::move_subtree(int drag_index, int drop_index, int drop_type) {
    if (!can_drop(drag_index, drop_index, drop_type)) return;
    std::vector<std::wstring> selected = selected_keys();
    std::wstring moved_key = key_at(drag_index);
    int drag_end = subtree_end(drag_index);
    std::vector<TreeViewItem> moving(items.begin() + drag_index, items.begin() + drag_end);
    int old_level = moving.front().level;
    items.erase(items.begin() + drag_index, items.begin() + drag_end);
    if (drop_index > drag_index) drop_index -= (drag_end - drag_index);
    if (drop_index < 0 || drop_index >= (int)items.size()) return;

    int insert_at = drop_index;
    int new_level = items[drop_index].level;
    if (drop_type == 1) {
        insert_at = subtree_end(drop_index);
        new_level = items[drop_index].level + 1;
        items[drop_index].expanded = true;
        items[drop_index].leaf = false;
    } else if (drop_type > 1) {
        insert_at = subtree_end(drop_index);
    }
    int delta = new_level - old_level;
    for (auto& item : moving) item.level = (std::max)(0, item.level + delta);
    items.insert(items.begin() + insert_at, moving.begin(), moving.end());
    set_selected_keys(selected);
    int moved_index = index_by_key(moved_key);
    if (moved_index >= 0) selected_index = moved_index;
    ++m_drag_event_count;
    emit_event(drag_cb, 20, moved_index, drop_type);
    invalidate();
}

Element* TreeSelect::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (item_at(lx, ly) >= 0) return this;
    if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    return nullptr;
}

Element* TreeSelect::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return item_at(lx, ly) >= 0 ? this : nullptr;
}

void TreeSelect::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = open || has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    float arrow_w = 24.0f;
    float clear_w = (clearable && selected_count() > 0) ? 22.0f : 0.0f;
    ts_draw_text(ctx, selected_text(), style, fg,
                 (float)style.pad_left, 0.0f,
                 (float)bounds.w - style.pad_left - style.pad_right - arrow_w - clear_w,
                 (float)bounds.h);
    if (clear_w > 0.0f) {
        ts_draw_text(ctx, L"×", style, t->text_secondary,
                     (float)bounds.w - style.pad_right - arrow_w - clear_w, 0.0f,
                     clear_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    ts_draw_text(ctx, open ? L"⌃" : L"⌄", style, t->text_secondary,
                 (float)bounds.w - style.pad_right - arrow_w, 0.0f,
                 arrow_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_CENTER);

    ctx.rt->SetTransform(saved);
}

void TreeSelect::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFF5F7FA;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    int cy = py + style.pad_top;
    int rh = row_height();
    if (searchable) {
        D2D1_RECT_F search_rect = {
            (float)style.pad_left + 6.0f, (float)cy + 4.0f,
            (float)pw - style.pad_right - 6.0f, (float)(cy + rh - 4)
        };
        ctx.rt->FillRoundedRectangle(ROUNDED(search_rect, 4.0f, 4.0f),
            ctx.get_brush(dark ? 0xFF1D1F2E : 0xFFF7F8FA));
        ctx.rt->DrawRoundedRectangle(ROUNDED(search_rect, 4.0f, 4.0f),
            ctx.get_brush(t->border_default), 1.0f);
        std::wstring hint = search_text.empty() ? L"🔍 搜索节点" : L"🔍 " + search_text;
        ts_draw_text(ctx, hint, style, search_text.empty() ? t->text_secondary : fg,
                     search_rect.left + 10.0f, (float)cy,
                     search_rect.right - search_rect.left - 20.0f, (float)rh);
        cy += rh;
    }

    int rendered = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_rendered_item(i)) continue;
        ++rendered;
        if (cy + rh > py + ph - style.pad_bottom) break;
        bool selected = is_selected_multi(i);
        bool hot = i == m_hover_index;
        D2D1_RECT_F row = { (float)style.pad_left, (float)cy,
            (float)pw - style.pad_right, (float)(cy + rh) };
        if (selected || hot) {
            ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
                ctx.get_brush(selected ? ts_with_alpha(t->accent, 0x33) : hover_bg));
        }
        if (m_dragging && i == m_drop_index) {
            float line_y = m_drop_type == 2 ? row.bottom - 1.0f : row.top + 1.0f;
            if (m_drop_type == 1) {
                ctx.rt->DrawRoundedRectangle(ROUNDED(row, 4.0f, 4.0f), ctx.get_brush(t->accent), 1.5f);
            } else {
                ctx.rt->DrawLine(D2D1::Point2F(row.left + 6.0f, line_y),
                    D2D1::Point2F(row.right - 6.0f, line_y), ctx.get_brush(t->accent), 2.0f);
            }
        }
        float indent = (float)items[i].level * 18.0f;
        float x = (float)style.pad_left + 8.0f + indent;
        bool expandable = has_children(i) || (items[i].lazy && !items[i].leaf);
        if (expandable) {
            ts_draw_text(ctx, items[i].expanded ? L"⌄" : L"›", style, t->text_secondary,
                         x, (float)cy, 16.0f, (float)rh, DWRITE_TEXT_ALIGNMENT_CENTER);
            x += 18.0f;
        } else {
            x += 18.0f;
        }
        if (multiple) {
            D2D1_RECT_F cb = D2D1::RectF(x, (float)cy + rh * 0.5f - 7.0f,
                x + 14.0f, (float)cy + rh * 0.5f + 7.0f);
            ctx.rt->FillRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f),
                ctx.get_brush(selected ? t->accent : bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f),
                ctx.get_brush(items[i].disabled ? t->text_secondary : (selected ? t->accent : t->border_default)), 1.1f);
            if (selected) {
                auto* br = ctx.get_brush(0xFFFFFFFF);
                float mid = (float)cy + rh * 0.5f;
                ctx.rt->DrawLine(D2D1::Point2F(x + 3.0f, mid),
                    D2D1::Point2F(x + 6.0f, mid + 3.5f), br, 1.6f);
                ctx.rt->DrawLine(D2D1::Point2F(x + 6.0f, mid + 3.5f),
                    D2D1::Point2F(x + 11.0f, mid - 4.0f), br, 1.6f);
            }
            x += 22.0f;
        }
        if (!items[i].icon.empty()) {
            ts_draw_text(ctx, items[i].icon, style, items[i].disabled ? t->text_secondary : fg,
                         x, (float)cy, 22.0f, (float)rh);
            x += 24.0f;
        }
        float text_right = (float)pw - style.pad_right - 18.0f;
        if (!items[i].tag.empty()) {
            float tag_w = (std::min)(88.0f, 24.0f + (float)items[i].tag.size() * style.font_size * 0.55f);
            float tag_right = text_right;
            float tag_left = (std::max)(x, tag_right - tag_w);
            D2D1_RECT_F tag_rect = D2D1::RectF(tag_left, (float)cy + 6.0f,
                tag_right, (float)cy + rh - 6.0f);
            ctx.rt->FillRoundedRectangle(ROUNDED(tag_rect, 10.0f, 10.0f), ctx.get_brush(ts_with_alpha(t->accent, 0x22)));
            ts_draw_text(ctx, items[i].tag, style, t->accent, tag_rect.left + 8.0f, (float)cy,
                (std::max)(0.0f, tag_rect.right - tag_rect.left - 16.0f), (float)rh);
            text_right = tag_left - 8.0f;
        }
        if (items[i].lazy && items[i].loading) {
            float loading_w = 78.0f;
            float loading_x = (std::max)(x, text_right - loading_w);
            ts_draw_text(ctx, L"加载中...", style, t->text_secondary,
                         loading_x, (float)cy, text_right - loading_x, (float)rh);
            text_right = loading_x - 8.0f;
        }
        ts_draw_text(ctx, items[i].label, style,
                     items[i].disabled ? t->text_secondary : (selected ? t->accent : fg),
                     x, (float)cy, (std::max)(0.0f, text_right - x), (float)rh);
        cy += rh;
    }
    if (rendered == 0) {
        ts_draw_text(ctx, L"🫥 没有匹配的节点", style, t->text_secondary,
                     0.0f, (float)cy + 12.0f, (float)pw, (float)rh,
                     DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    ctx.rt->SetTransform(saved);
}

void TreeSelect::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (pressed && m_press_part == PartItem && can_drag(m_press_index)) {
        m_dragging = true;
        m_drag_index = m_press_index;
        m_drop_index = idx;
        m_drop_type = 0;
        if (idx >= 0) {
            int py = popup_y();
            int rh = row_height();
            int cy = py + style.pad_top + (searchable ? rh : 0);
            for (int i = 0; i < (int)items.size(); ++i) {
                if (!is_rendered_item(i)) continue;
                if (i == idx) break;
                cy += rh;
            }
            float local_y = (float)(y - cy);
            m_drop_type = local_y > rh * 0.70f ? 2 : (local_y > rh * 0.35f ? 1 : 0);
        }
    }
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void TreeSelect::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    m_press_part = PartNone;
    m_dragging = false;
    m_drag_index = -1;
    m_drop_index = -1;
    invalidate();
}

void TreeSelect::on_mouse_down(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (idx >= 0) {
        m_press_part = PartItem;
        m_press_index = idx;
        m_drag_index = idx;
    } else if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        m_press_part = PartMain;
        m_press_index = -1;
        m_drag_index = -1;
    } else {
        m_press_part = PartNone;
        m_press_index = -1;
        m_drag_index = -1;
    }
    pressed = true;
    invalidate();
}

void TreeSelect::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (m_dragging) {
        if (idx >= 0) move_subtree(m_drag_index, idx, m_drop_type);
    } else if (m_press_part == PartMain && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        float clear_left = (float)bounds.w - style.pad_right - 46.0f;
        float clear_right = clear_left + 22.0f;
        if (clearable && selected_count() > 0 && x >= clear_left && x <= clear_right) {
            clear_selection();
        } else {
            open = !open;
        }
    } else if (m_press_part == PartItem && idx >= 0 && idx == m_press_index && !items[idx].disabled) {
        if (has_children(idx) || items[idx].lazy) {
            set_expanded_internal(idx, !items[idx].expanded);
        } else {
            toggle_selected_multi(idx);
            emit_event(event_cb, 1, idx);
            if (!multiple) open = false;
        }
    }
    pressed = false;
    m_press_part = PartNone;
    m_press_index = -1;
    m_dragging = false;
    m_drag_index = -1;
    m_drop_index = -1;
    m_hover_index = idx;
    invalidate();
}

void TreeSelect::on_key_down(int vk, int) {
    if (searchable && open && vk == VK_BACK) {
        if (!search_text.empty()) search_text.pop_back();
    } else if (clearable && vk == VK_DELETE) {
        clear_selection();
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        if (open && selected_index >= 0 && !has_children(selected_index) && !items[selected_index].lazy && vk == VK_SPACE) {
            toggle_selected_multi(selected_index);
        } else if (open && selected_index >= 0 && (has_children(selected_index) || items[selected_index].lazy) && vk == VK_RETURN) {
            set_expanded_internal(selected_index, !items[selected_index].expanded);
        } else {
            open = !open;
        }
    } else if (vk == VK_ESCAPE) {
        if (!search_text.empty()) search_text.clear();
        open = false;
    } else if (vk == VK_DOWN) {
        int next = next_rendered_index(selected_index, 1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_UP) {
        int next = next_rendered_index(selected_index, -1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_HOME) {
        int first = first_rendered_index();
        if (first >= 0) set_selected_index(first);
    } else if (vk == VK_END) {
        int last = selected_index;
        for (int i = 0; i < (int)items.size(); ++i) {
            if (is_rendered_item(i)) last = i;
        }
        if (last >= 0) set_selected_index(last);
    }
    invalidate();
}

void TreeSelect::on_char(wchar_t ch) {
    if (!searchable) return;
    if (!open) open = true;
    if (ch >= 32 && ch != 127) {
        search_text.push_back(ch);
        invalidate();
    }
}

void TreeSelect::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    m_press_part = PartNone;
    invalidate();
}
