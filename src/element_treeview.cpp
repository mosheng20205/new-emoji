#include "element_treeview.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cwctype>
#include <map>
#include <sstream>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

namespace {

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static std::wstring lower_text(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(), [](wchar_t ch) {
        return (wchar_t)towlower(ch);
    });
    return value;
}

static std::wstring json_escape(const std::wstring& value) {
    std::wstring out;
    out.reserve(value.size() + 8);
    for (wchar_t ch : value) {
        switch (ch) {
        case L'\\': out += L"\\\\"; break;
        case L'"': out += L"\\\""; break;
        case L'\n': out += L"\\n"; break;
        case L'\r': out += L"\\r"; break;
        case L'\t': out += L"\\t"; break;
        default:
            if (ch < 32) {
                wchar_t buf[8];
                swprintf_s(buf, L"\\u%04X", (unsigned)ch);
                out += buf;
            } else {
                out += ch;
            }
            break;
        }
    }
    return out;
}

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

struct JsonValue {
    enum Type { Null, Bool, Number, String, Array, Object } type = Null;
    bool b = false;
    double n = 0.0;
    std::wstring s;
    std::vector<JsonValue> a;
    std::map<std::wstring, JsonValue> o;

    bool is_object() const { return type == Object; }
    bool is_array() const { return type == Array; }
    const JsonValue* get(const std::wstring& key) const {
        if (type != Object) return nullptr;
        auto it = o.find(key);
        return it == o.end() ? nullptr : &it->second;
    }
};

class JsonParser {
public:
    explicit JsonParser(const std::wstring& src) : m_src(src) {}

    JsonValue parse() {
        skip_ws();
        JsonValue value = parse_value();
        skip_ws();
        return value;
    }

private:
    const std::wstring& m_src;
    size_t m_pos = 0;

    void skip_ws() {
        while (m_pos < m_src.size() && iswspace(m_src[m_pos])) ++m_pos;
    }

    bool consume(wchar_t ch) {
        skip_ws();
        if (m_pos < m_src.size() && m_src[m_pos] == ch) {
            ++m_pos;
            return true;
        }
        return false;
    }

    bool starts_with(const wchar_t* text) const {
        size_t len = wcslen(text);
        return m_src.compare(m_pos, len, text) == 0;
    }

    JsonValue parse_value() {
        skip_ws();
        if (m_pos >= m_src.size()) return {};
        wchar_t ch = m_src[m_pos];
        if (ch == L'{') return parse_object();
        if (ch == L'[') return parse_array();
        if (ch == L'"') {
            JsonValue v; v.type = JsonValue::String; v.s = parse_string(); return v;
        }
        if (ch == L't' && starts_with(L"true")) {
            m_pos += 4; JsonValue v; v.type = JsonValue::Bool; v.b = true; return v;
        }
        if (ch == L'f' && starts_with(L"false")) {
            m_pos += 5; JsonValue v; v.type = JsonValue::Bool; v.b = false; return v;
        }
        if (ch == L'n' && starts_with(L"null")) {
            m_pos += 4; return {};
        }
        return parse_number();
    }

    JsonValue parse_object() {
        JsonValue v; v.type = JsonValue::Object;
        consume(L'{');
        skip_ws();
        if (consume(L'}')) return v;
        while (m_pos < m_src.size()) {
            std::wstring key = consume(L'"') ? parse_string_body() : L"";
            consume(L':');
            v.o[key] = parse_value();
            skip_ws();
            if (consume(L'}')) break;
            consume(L',');
        }
        return v;
    }

    JsonValue parse_array() {
        JsonValue v; v.type = JsonValue::Array;
        consume(L'[');
        skip_ws();
        if (consume(L']')) return v;
        while (m_pos < m_src.size()) {
            v.a.push_back(parse_value());
            skip_ws();
            if (consume(L']')) break;
            consume(L',');
        }
        return v;
    }

    std::wstring parse_string() {
        consume(L'"');
        return parse_string_body();
    }

    std::wstring parse_string_body() {
        std::wstring out;
        while (m_pos < m_src.size()) {
            wchar_t ch = m_src[m_pos++];
            if (ch == L'"') break;
            if (ch == L'\\' && m_pos < m_src.size()) {
                wchar_t esc = m_src[m_pos++];
                switch (esc) {
                case L'"': out.push_back(L'"'); break;
                case L'\\': out.push_back(L'\\'); break;
                case L'/': out.push_back(L'/'); break;
                case L'b': out.push_back(L'\b'); break;
                case L'f': out.push_back(L'\f'); break;
                case L'n': out.push_back(L'\n'); break;
                case L'r': out.push_back(L'\r'); break;
                case L't': out.push_back(L'\t'); break;
                case L'u':
                    if (m_pos + 4 <= m_src.size()) {
                        unsigned code = 0;
                        for (int i = 0; i < 4; ++i) {
                            wchar_t h = m_src[m_pos++];
                            code <<= 4;
                            if (h >= L'0' && h <= L'9') code += h - L'0';
                            else if (h >= L'a' && h <= L'f') code += h - L'a' + 10;
                            else if (h >= L'A' && h <= L'F') code += h - L'A' + 10;
                        }
                        out.push_back((wchar_t)code);
                    }
                    break;
                default:
                    out.push_back(esc);
                    break;
                }
            } else {
                out.push_back(ch);
            }
        }
        return out;
    }

    JsonValue parse_number() {
        size_t start = m_pos;
        if (m_pos < m_src.size() && m_src[m_pos] == L'-') ++m_pos;
        while (m_pos < m_src.size() && iswdigit(m_src[m_pos])) ++m_pos;
        if (m_pos < m_src.size() && m_src[m_pos] == L'.') {
            ++m_pos;
            while (m_pos < m_src.size() && iswdigit(m_src[m_pos])) ++m_pos;
        }
        JsonValue v; v.type = JsonValue::Number;
        v.n = _wtof(m_src.substr(start, m_pos - start).c_str());
        return v;
    }
};

static std::wstring json_string(const JsonValue* v, const std::wstring& fallback = L"") {
    if (!v) return fallback;
    if (v->type == JsonValue::String) return v->s;
    if (v->type == JsonValue::Number) return std::to_wstring((int)v->n);
    if (v->type == JsonValue::Bool) return v->b ? L"1" : L"0";
    return fallback;
}

static bool json_bool(const JsonValue* v, bool fallback = false) {
    if (!v) return fallback;
    if (v->type == JsonValue::Bool) return v->b;
    if (v->type == JsonValue::Number) return v->n != 0.0;
    if (v->type == JsonValue::String) return v->s == L"1" || v->s == L"true" || v->s == L"True";
    return fallback;
}

static std::wstring prop_name(const std::map<std::wstring, std::wstring>& props,
                              const std::wstring& name) {
    auto it = props.find(name);
    return it == props.end() ? name : it->second;
}

static const JsonValue* get_prop(const JsonValue& obj,
                                 const std::map<std::wstring, std::wstring>& props,
                                 const std::wstring& name) {
    const JsonValue* v = obj.get(prop_name(props, name));
    if (!v) v = obj.get(name);
    if (!v && name == L"key") v = obj.get(L"id");
    if (!v && name == L"key") v = obj.get(L"value");
    if (!v && name == L"label") v = obj.get(L"name");
    if (!v && name == L"children") v = obj.get(L"zones");
    if (!v && name == L"isLeaf") v = obj.get(L"leaf");
    return v;
}

static void read_props(const JsonValue& root, std::map<std::wstring, std::wstring>& props) {
    const JsonValue* p = root.get(L"props");
    if (!p || !p->is_object()) return;
    for (const auto& kv : p->o) {
        props[kv.first] = json_string(&kv.second);
    }
}

static std::vector<std::wstring> json_key_array_from_value(const JsonValue* value) {
    std::vector<std::wstring> keys;
    if (!value) return keys;
    if (value->type == JsonValue::Array) {
        for (const auto& item : value->a) {
            std::wstring key = json_string(&item);
            if (!key.empty()) keys.push_back(key);
        }
    } else {
        std::wstring key = json_string(value);
        if (!key.empty()) keys.push_back(key);
    }
    return keys;
}

static void flatten_nodes(const JsonValue& array_or_node,
                          const std::map<std::wstring, std::wstring>& props,
                          int level,
                          std::vector<TreeViewItem>& out) {
    if (array_or_node.type == JsonValue::Array) {
        for (const auto& child : array_or_node.a) flatten_nodes(child, props, level, out);
        return;
    }
    if (!array_or_node.is_object()) return;

    TreeViewItem item;
    item.key = json_string(get_prop(array_or_node, props, L"key"));
    if (item.key.empty()) item.key = json_string(array_or_node.get(L"id"));
    item.label = json_string(get_prop(array_or_node, props, L"label"), item.key);
    item.icon = json_string(array_or_node.get(L"icon"));
    item.tag = json_string(array_or_node.get(L"tag"));
    item.actions = json_string(array_or_node.get(L"actions"));
    item.level = (std::min)(level, 12);
    item.expanded = json_bool(array_or_node.get(L"expanded"), true);
    item.checked = json_bool(array_or_node.get(L"checked"), false);
    item.indeterminate = json_bool(array_or_node.get(L"indeterminate"), false);
    item.lazy = json_bool(array_or_node.get(L"lazy"), false);
    item.loading = json_bool(array_or_node.get(L"loading"), false);
    item.disabled = json_bool(get_prop(array_or_node, props, L"disabled"), false);
    item.leaf = json_bool(get_prop(array_or_node, props, L"isLeaf"), false);
    out.push_back(item);

    const JsonValue* children = get_prop(array_or_node, props, L"children");
    if (children && children->type == JsonValue::Array) {
        for (const auto& child : children->a) flatten_nodes(child, props, level + 1, out);
    }
}

} // namespace

std::vector<std::wstring> parse_tree_key_array_json(const std::wstring& json) {
    JsonValue root = JsonParser(json).parse();
    if (root.is_object()) {
        if (const JsonValue* keys = root.get(L"keys")) return json_key_array_from_value(keys);
        if (const JsonValue* keys = root.get(L"checkedKeys")) return json_key_array_from_value(keys);
        if (const JsonValue* keys = root.get(L"expandedKeys")) return json_key_array_from_value(keys);
        if (const JsonValue* keys = root.get(L"selectedKeys")) return json_key_array_from_value(keys);
        if (const JsonValue* key = root.get(L"key")) return json_key_array_from_value(key);
    }
    return json_key_array_from_value(&root);
}

std::wstring serialize_tree_key_array_json(const std::vector<std::wstring>& keys) {
    std::wstringstream ss;
    ss << L"[";
    for (size_t i = 0; i < keys.size(); ++i) {
        if (i) ss << L",";
        ss << L"\"" << json_escape(keys[i]) << L"\"";
    }
    ss << L"]";
    return ss.str();
}

std::vector<TreeViewItem> parse_tree_json_items(const std::wstring& json,
                                                std::vector<std::wstring>* default_expanded_keys,
                                                std::vector<std::wstring>* default_checked_keys,
                                                std::wstring* current_key,
                                                std::wstring* filter_text,
                                                std::wstring* options_json) {
    JsonValue root = JsonParser(json).parse();
    std::map<std::wstring, std::wstring> props;
    const JsonValue* data = &root;
    if (root.is_object()) {
        read_props(root, props);
        if (const JsonValue* d = root.get(L"data")) data = d;
        else if (const JsonValue* d = root.get(L"nodes")) data = d;
        else if (const JsonValue* d = root.get(L"children")) data = d;
        if (default_expanded_keys) *default_expanded_keys = json_key_array_from_value(root.get(L"defaultExpandedKeys"));
        if (default_checked_keys) *default_checked_keys = json_key_array_from_value(root.get(L"defaultCheckedKeys"));
        if (current_key) *current_key = json_string(root.get(L"currentKey"));
        if (filter_text) *filter_text = json_string(root.get(L"filterText"));
        if (options_json) *options_json = json;
    }
    std::vector<TreeViewItem> items;
    flatten_nodes(*data, props, 0, items);
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[i].key.empty()) items[i].key = std::to_wstring(i);
    }
    return items;
}

static int serialize_node(std::wstringstream& ss, const std::vector<TreeViewItem>& items, int index) {
    const TreeViewItem& item = items[index];
    ss << L"{";
    ss << L"\"key\":\"" << json_escape(item.key.empty() ? std::to_wstring(index) : item.key) << L"\",";
    ss << L"\"label\":\"" << json_escape(item.label) << L"\",";
    ss << L"\"level\":" << item.level << L",";
    ss << L"\"expanded\":" << (item.expanded ? L"true" : L"false") << L",";
    ss << L"\"checked\":" << (item.checked ? L"true" : L"false") << L",";
    ss << L"\"indeterminate\":" << (item.indeterminate ? L"true" : L"false") << L",";
    ss << L"\"disabled\":" << (item.disabled ? L"true" : L"false") << L",";
    ss << L"\"leaf\":" << (item.leaf ? L"true" : L"false") << L",";
    ss << L"\"lazy\":" << (item.lazy ? L"true" : L"false") << L",";
    ss << L"\"loading\":" << (item.loading ? L"true" : L"false");
    if (!item.icon.empty()) ss << L",\"icon\":\"" << json_escape(item.icon) << L"\"";
    if (!item.tag.empty()) ss << L",\"tag\":\"" << json_escape(item.tag) << L"\"";
    if (!item.actions.empty()) ss << L",\"actions\":\"" << json_escape(item.actions) << L"\"";

    int next = index + 1;
    bool first_child = true;
    while (next < (int)items.size() && items[next].level > item.level) {
        if (items[next].level == item.level + 1) {
            if (first_child) {
                ss << L",\"children\":[";
                first_child = false;
            } else {
                ss << L",";
            }
            next = serialize_node(ss, items, next);
        } else {
            ++next;
        }
    }
    if (!first_child) ss << L"]";
    ss << L"}";
    return next;
}

std::wstring serialize_tree_json_items(const std::vector<TreeViewItem>& items) {
    std::wstringstream ss;
    ss << L"{\"data\":[";
    bool first = true;
    for (int i = 0; i < (int)items.size();) {
        if (items[i].level != 0) {
            ++i;
            continue;
        }
        if (!first) ss << L",";
        first = false;
        i = serialize_node(ss, items, i);
    }
    ss << L"]}";
    return ss.str();
}

std::wstring tree_item_event_json(const std::vector<TreeViewItem>& items, int index, int extra) {
    std::wstringstream ss;
    ss << L"{\"index\":" << index << L",\"extra\":" << extra;
    if (index >= 0 && index < (int)items.size()) {
        const auto& item = items[index];
        ss << L",\"key\":\"" << json_escape(item.key.empty() ? std::to_wstring(index) : item.key) << L"\"";
        ss << L",\"label\":\"" << json_escape(item.label) << L"\"";
        ss << L",\"checked\":" << (item.checked ? L"true" : L"false");
        ss << L",\"expanded\":" << (item.expanded ? L"true" : L"false");
    }
    ss << L"}";
    return ss.str();
}

float TreeView::row_height() const {
    return (std::max)(style.font_size * 2.25f, 30.0f);
}

void TreeView::set_items(const std::vector<TreeViewItem>& values) {
    items = values;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[i].key.empty()) items[i].key = std::to_wstring(i);
    }
    update_ancestor_checks();
    if (items.empty()) selected_index = -1;
    else if (selected_index >= (int)items.size()) selected_index = 0;
    if (selected_index >= 0 && !is_rendered_item(selected_index)) selected_index = first_visible_index();
    invalidate();
}

void TreeView::set_selected_index(int value) {
    if (items.empty()) selected_index = -1;
    else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        if (!items[value].disabled) selected_index = value;
        if (!is_rendered_item(selected_index)) selected_index = first_visible_index();
    }
    emit_event(event_cb, 1, selected_index);
    invalidate();
}

void TreeView::set_options(bool show_checkbox, bool keyboard_navigation, bool lazy_mode) {
    m_show_checkbox = show_checkbox;
    m_keyboard_navigation = keyboard_navigation;
    m_lazy_mode = lazy_mode;
    invalidate();
}

void TreeView::set_data_json(const std::wstring& json) {
    std::vector<std::wstring> expanded;
    std::vector<std::wstring> checked;
    std::wstring current;
    std::wstring filter;
    set_items(parse_tree_json_items(json, &expanded, &checked, &current, &filter, nullptr));
    if (!expanded.empty()) set_expanded_keys(expanded);
    if (!checked.empty()) set_checked_keys(checked);
    if (!current.empty()) {
        int idx = index_by_key(current);
        if (idx >= 0) selected_index = idx;
    }
    if (!filter.empty()) m_filter_text = filter;
    set_options_json(json);
    invalidate();
}

std::wstring TreeView::data_json() const {
    return serialize_tree_json_items(items);
}

void TreeView::set_options_json(const std::wstring& json) {
    JsonValue root = JsonParser(json).parse();
    if (!root.is_object()) return;
    if (const JsonValue* v = root.get(L"showCheckbox")) m_show_checkbox = json_bool(v, m_show_checkbox);
    if (const JsonValue* v = root.get(L"keyboardNavigation")) m_keyboard_navigation = json_bool(v, m_keyboard_navigation);
    if (const JsonValue* v = root.get(L"lazy")) m_lazy_mode = json_bool(v, m_lazy_mode);
    if (const JsonValue* v = root.get(L"lazyMode")) m_lazy_mode = json_bool(v, m_lazy_mode);
    if (const JsonValue* v = root.get(L"checkStrictly")) m_check_strictly = json_bool(v, m_check_strictly);
    if (const JsonValue* v = root.get(L"accordion")) m_accordion = json_bool(v, m_accordion);
    if (const JsonValue* v = root.get(L"expandOnClickNode")) m_expand_on_click_node = json_bool(v, m_expand_on_click_node);
    if (const JsonValue* v = root.get(L"highlightCurrent")) m_highlight_current = json_bool(v, m_highlight_current);
    if (const JsonValue* v = root.get(L"checkOnClickNode")) m_check_on_click_node = json_bool(v, m_check_on_click_node);
    if (const JsonValue* v = root.get(L"draggable")) m_draggable = json_bool(v, m_draggable);
    if (const JsonValue* v = root.get(L"showActions")) m_show_actions = json_bool(v, m_show_actions);
    if (const JsonValue* v = root.get(L"filterText")) m_filter_text = json_string(v);
    invalidate();
}

std::wstring TreeView::state_json() const {
    std::wstringstream ss;
    ss << L"{";
    ss << L"\"selectedIndex\":" << selected_index << L",";
    ss << L"\"currentKey\":\"" << json_escape(key_at(selected_index)) << L"\",";
    ss << L"\"visibleCount\":" << visible_count() << L",";
    ss << L"\"checkedCount\":" << checked_count() << L",";
    ss << L"\"lastLazyIndex\":" << m_last_lazy_index << L",";
    ss << L"\"lastLazyKey\":\"" << json_escape(key_at(m_last_lazy_index)) << L"\",";
    ss << L"\"showCheckbox\":" << (m_show_checkbox ? L"true" : L"false") << L",";
    ss << L"\"checkStrictly\":" << (m_check_strictly ? L"true" : L"false") << L",";
    ss << L"\"accordion\":" << (m_accordion ? L"true" : L"false") << L",";
    ss << L"\"draggable\":" << (m_draggable ? L"true" : L"false") << L",";
    ss << L"\"filterText\":\"" << json_escape(m_filter_text) << L"\",";
    ss << L"\"checkedKeys\":" << serialize_tree_key_array_json(checked_keys()) << L",";
    ss << L"\"halfCheckedKeys\":" << serialize_tree_key_array_json(half_checked_keys()) << L",";
    ss << L"\"expandedKeys\":" << serialize_tree_key_array_json(expanded_keys()) << L",";
    ss << L"\"dragEventCount\":" << m_drag_event_count;
    ss << L"}";
    return ss.str();
}

void TreeView::set_item_expanded(int index, bool expanded) {
    if (index < 0 || index >= (int)items.size()) return;
    if (!has_children(index) && !items[index].lazy) return;
    set_expanded_internal(index, expanded);
    invalidate();
}

void TreeView::toggle_item_expanded(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    set_item_expanded(index, !items[index].expanded);
}

bool TreeView::get_item_expanded(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].expanded;
}

void TreeView::set_item_checked(int index, bool checked) {
    if (index < 0 || index >= (int)items.size() || items[index].disabled) return;
    if (m_check_strictly) {
        items[index].checked = checked;
        items[index].indeterminate = false;
    } else {
        set_subtree_checked(index, checked);
        update_ancestor_checks();
    }
    emit_event(event_cb, 2, index);
    invalidate();
}

bool TreeView::get_item_checked(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].checked;
}

void TreeView::set_item_lazy(int index, bool lazy) {
    if (index < 0 || index >= (int)items.size()) return;
    items[index].lazy = lazy;
    items[index].loading = false;
    if (!lazy && m_last_lazy_index == index) m_last_lazy_index = -1;
    invalidate();
}

bool TreeView::get_item_lazy(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].lazy;
}

int TreeView::visible_count() const {
    int count = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_rendered_item(i)) ++count;
    }
    return count;
}

int TreeView::checked_count() const {
    int count = 0;
    for (const auto& item : items) {
        if (item.checked) ++count;
    }
    return count;
}

int TreeView::lazy_count() const {
    int count = 0;
    for (const auto& item : items) {
        if (item.lazy) ++count;
    }
    return count;
}

void TreeView::set_checked_keys(const std::vector<std::wstring>& keys) {
    for (auto& item : items) {
        item.checked = false;
        item.indeterminate = false;
    }
    for (const auto& key : keys) {
        int idx = index_by_key(key);
        if (idx >= 0) {
            if (m_check_strictly) {
                if (!items[idx].disabled) items[idx].checked = true;
            } else {
                set_subtree_checked(idx, true);
            }
        }
    }
    update_ancestor_checks();
    invalidate();
}

std::vector<std::wstring> TreeView::checked_keys() const {
    std::vector<std::wstring> keys;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[i].checked) keys.push_back(key_at(i));
    }
    return keys;
}

std::vector<std::wstring> TreeView::half_checked_keys() const {
    std::vector<std::wstring> keys;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[i].indeterminate) keys.push_back(key_at(i));
    }
    return keys;
}

void TreeView::set_expanded_keys(const std::vector<std::wstring>& keys) {
    for (auto& item : items) item.expanded = false;
    for (const auto& key : keys) {
        int idx = index_by_key(key);
        if (idx >= 0) set_expanded_internal(idx, true);
    }
    invalidate();
}

std::vector<std::wstring> TreeView::expanded_keys() const {
    std::vector<std::wstring> keys;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[i].expanded && (has_children(i) || items[i].lazy)) keys.push_back(key_at(i));
    }
    return keys;
}

void TreeView::append_node_json(const std::wstring& parent_key, const std::wstring& json) {
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
    update_ancestor_checks();
    invalidate();
}

void TreeView::update_node_json(const std::wstring& key, const std::wstring& json) {
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

void TreeView::remove_node_by_key(const std::wstring& key) {
    int idx = index_by_key(key);
    if (idx < 0) return;
    int end = subtree_end(idx);
    items.erase(items.begin() + idx, items.begin() + end);
    if (selected_index >= (int)items.size()) selected_index = (int)items.size() - 1;
    update_ancestor_checks();
    invalidate();
}

int TreeView::index_by_key(const std::wstring& key) const {
    if (key.empty()) return -1;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (key_at(i) == key) return i;
    }
    return -1;
}

std::wstring TreeView::key_at(int index) const {
    if (index < 0 || index >= (int)items.size()) return L"";
    return items[index].key.empty() ? std::to_wstring(index) : items[index].key;
}

void TreeView::set_filter_text(const std::wstring& value) {
    m_filter_text = value;
    m_hover_index = -1;
    invalidate();
}

bool TreeView::has_children(int index) const {
    if (index < 0 || index + 1 >= (int)items.size()) return false;
    return items[index + 1].level > items[index].level;
}

bool TreeView::is_visible_item(int index) const {
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

bool TreeView::matches_filter(int index) const {
    if (m_filter_text.empty()) return true;
    if (index < 0 || index >= (int)items.size()) return false;
    std::wstring needle = lower_text(m_filter_text);
    std::wstring text = lower_text(items[index].label + L" " + items[index].key + L" " + items[index].tag);
    return text.find(needle) != std::wstring::npos;
}

bool TreeView::has_matching_descendant(int index) const {
    int end = subtree_end(index);
    for (int i = index + 1; i < end; ++i) {
        if (matches_filter(i)) return true;
    }
    return false;
}

bool TreeView::is_rendered_item(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    if (m_filter_text.empty()) return is_visible_item(index);
    if (!is_visible_item(index)) return false;
    if (matches_filter(index) || has_matching_descendant(index)) return true;
    int p = parent_index(index);
    while (p >= 0) {
        if (matches_filter(p)) return true;
        p = parent_index(p);
    }
    return false;
}

int TreeView::item_at(int x, int y) const {
    if (x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    float rh = row_height();
    float cy = (float)style.pad_top;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_rendered_item(i)) continue;
        if (y >= cy && y < cy + rh) return i;
        cy += rh;
    }
    return -1;
}

bool TreeView::is_checkbox_hit(int index, int x) const {
    if (!m_show_checkbox || index < 0 || index >= (int)items.size()) return false;
    float indent = (float)items[index].level * 18.0f;
    float ax = (float)style.pad_left + 10.0f + indent;
    float box_x = ax + 16.0f;
    return x >= (int)box_x - 3 && x <= (int)box_x + 19;
}

bool TreeView::is_expander_hit(int index, int x) const {
    if (index < 0 || index >= (int)items.size()) return false;
    float indent = (float)items[index].level * 18.0f;
    float ax = (float)style.pad_left + 10.0f + indent;
    return x >= (int)ax - 10 && x <= (int)ax + 14;
}

int TreeView::first_visible_index() const {
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_rendered_item(i) && !items[i].disabled) return i;
    }
    return -1;
}

int TreeView::last_visible_index() const {
    for (int i = (int)items.size() - 1; i >= 0; --i) {
        if (is_rendered_item(i) && !items[i].disabled) return i;
    }
    return -1;
}

int TreeView::next_visible_index(int from, int delta) const {
    if (items.empty()) return -1;
    if (from < 0) return first_visible_index();
    int i = from + delta;
    while (i >= 0 && i < (int)items.size()) {
        if (is_rendered_item(i) && !items[i].disabled) return i;
        i += delta;
    }
    return from;
}

int TreeView::parent_index(int index) const {
    if (index <= 0 || index >= (int)items.size()) return -1;
    int level = items[index].level;
    for (int i = index - 1; i >= 0; --i) {
        if (items[i].level < level) return i;
    }
    return -1;
}

int TreeView::subtree_end(int index) const {
    if (index < 0 || index >= (int)items.size()) return index;
    int level = items[index].level;
    int i = index + 1;
    while (i < (int)items.size() && items[i].level > level) ++i;
    return i;
}

void TreeView::request_lazy_load(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    m_last_lazy_index = index;
    items[index].loading = true;
    emit_event(lazy_cb, 10, index);
}

void TreeView::set_expanded_internal(int index, bool expanded) {
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
    if (expanded && m_lazy_mode && items[index].lazy) request_lazy_load(index);
    items[index].expanded = expanded;
    emit_event(event_cb, expanded ? 3 : 4, index);
}

void TreeView::set_subtree_checked(int index, bool checked) {
    int end = subtree_end(index);
    for (int i = index; i < end; ++i) {
        if (items[i].disabled) continue;
        items[i].checked = checked;
        items[i].indeterminate = false;
    }
}

void TreeView::update_ancestor_checks() {
    if (m_check_strictly) return;
    for (int i = (int)items.size() - 1; i >= 0; --i) {
        if (!has_children(i) || items[i].disabled) continue;
        int end = subtree_end(i);
        bool any = false;
        bool all = true;
        bool has_checkable = false;
        for (int j = i + 1; j < end; ++j) {
            if (items[j].level != items[i].level + 1 || items[j].disabled) continue;
            has_checkable = true;
            any = any || items[j].checked || items[j].indeterminate;
            all = all && items[j].checked && !items[j].indeterminate;
        }
        if (has_checkable) {
            items[i].checked = all;
            items[i].indeterminate = any && !all;
        }
    }
}

void TreeView::emit_event(TreeNodeEventCallback cb, int event_code, int index, int extra) {
    if (!cb) return;
    std::string payload = wide_to_utf8(tree_item_event_json(items, index, extra));
    cb(id, event_code, index, (const unsigned char*)payload.data(), (int)payload.size());
}

bool TreeView::can_drag(int index) const {
    if (!m_draggable || index < 0 || index >= (int)items.size() || items[index].disabled) return false;
    if (!allow_drag_cb) return true;
    std::string key = wide_to_utf8(key_at(index));
    return allow_drag_cb(id, (const unsigned char*)key.data(), (int)key.size()) != 0;
}

bool TreeView::can_drop(int drag_index, int drop_index, int drop_type) const {
    if (drag_index < 0 || drop_index < 0 || drag_index == drop_index) return false;
    int drag_end = subtree_end(drag_index);
    if (drop_index > drag_index && drop_index < drag_end) return false;
    if (items[drop_index].disabled) return false;
    if (!allow_drop_cb) return true;
    std::string drag_key = wide_to_utf8(key_at(drag_index));
    std::string drop_key = wide_to_utf8(key_at(drop_index));
    return allow_drop_cb(id,
        (const unsigned char*)drag_key.data(), (int)drag_key.size(),
        (const unsigned char*)drop_key.data(), (int)drop_key.size(), drop_type) != 0;
}

void TreeView::move_subtree(int drag_index, int drop_index, int drop_type) {
    if (!can_drop(drag_index, drop_index, drop_type)) return;
    int drag_end = subtree_end(drag_index);
    std::vector<TreeViewItem> moving(items.begin() + drag_index, items.begin() + drag_end);
    int old_level = moving.front().level;
    items.erase(items.begin() + drag_index, items.begin() + drag_end);
    if (drop_index > drag_index) drop_index -= (drag_end - drag_index);

    int insert_at = drop_index;
    int new_level = items[drop_index].level;
    if (drop_type == 1) {
        insert_at = subtree_end(drop_index);
        new_level = items[drop_index].level + 1;
        items[drop_index].expanded = true;
    } else if (drop_type > 1) {
        insert_at = subtree_end(drop_index);
    }
    int delta = new_level - old_level;
    for (auto& item : moving) item.level = (std::max)(0, item.level + delta);
    items.insert(items.begin() + insert_at, moving.begin(), moving.end());
    selected_index = insert_at;
    ++m_drag_event_count;
    emit_event(drag_cb, 20, selected_index, drop_type);
    invalidate();
}

void TreeView::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color selected_bg = with_alpha(t->accent, dark ? 0x44 : 0x22);
    Color hover_bg = dark ? 0xFF313244 : 0xFFF5F7FA;

    ctx.push_clip(D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h));
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float rh = row_height();
    float y = (float)style.pad_top;
    int rendered = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_rendered_item(i)) continue;
        ++rendered;
        if (y >= bounds.h - style.pad_bottom) break;

        bool selected = i == selected_index && m_highlight_current;
        bool hot = i == m_hover_index;
        D2D1_RECT_F row = { (float)style.pad_left, y,
            (float)bounds.w - style.pad_right, (std::min)(y + rh, (float)bounds.h - style.pad_bottom) };
        if (selected || hot) {
            ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f), ctx.get_brush(selected ? selected_bg : hover_bg));
        }
        if (m_dragging && i == m_drop_index) {
            float line_y = m_drop_type == 2 ? row.bottom - 1.0f : row.top + 1.0f;
            if (m_drop_type == 1) {
                ctx.rt->DrawRoundedRectangle(ROUNDED(row, 4.0f, 4.0f), ctx.get_brush(t->accent), 1.5f);
            } else {
                ctx.rt->DrawLine(D2D1::Point2F(row.left + 6.0f, line_y), D2D1::Point2F(row.right - 6.0f, line_y),
                    ctx.get_brush(t->accent), 2.0f);
            }
        }

        float indent = (float)items[i].level * 18.0f;
        float ax = (float)style.pad_left + 10.0f + indent;
        float ay = y + rh * 0.5f;
        bool expandable = has_children(i) || (m_lazy_mode && items[i].lazy && !items[i].leaf);
        if (expandable) {
            auto* br = ctx.get_brush(items[i].disabled ? with_alpha(muted, 0x88) : muted);
            if (items[i].expanded) {
                ctx.rt->DrawLine(D2D1::Point2F(ax - 4.0f, ay - 2.0f), D2D1::Point2F(ax, ay + 3.0f), br, 1.4f);
                ctx.rt->DrawLine(D2D1::Point2F(ax, ay + 3.0f), D2D1::Point2F(ax + 5.0f, ay - 3.0f), br, 1.4f);
            } else {
                ctx.rt->DrawLine(D2D1::Point2F(ax - 2.0f, ay - 5.0f), D2D1::Point2F(ax + 3.0f, ay), br, 1.4f);
                ctx.rt->DrawLine(D2D1::Point2F(ax + 3.0f, ay), D2D1::Point2F(ax - 2.0f, ay + 5.0f), br, 1.4f);
            }
        }

        float text_x = ax + 14.0f;
        if (m_show_checkbox) {
            float box_x = ax + 16.0f;
            D2D1_RECT_F cb = D2D1::RectF(box_x, ay - 7.0f, box_x + 14.0f, ay + 7.0f);
            bool checked = items[i].checked;
            bool half = items[i].indeterminate;
            Color cb_border = (checked || half) ? t->accent : border;
            Color cb_fill = checked ? t->accent : bg;
            if (items[i].disabled) {
                cb_border = with_alpha(cb_border, 0x88);
                cb_fill = dark ? 0xFF2D3044 : 0xFFF2F3F5;
            }
            ctx.rt->FillRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f), ctx.get_brush(cb_fill));
            ctx.rt->DrawRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f), ctx.get_brush(cb_border), 1.2f);
            if (checked) {
                auto* br = ctx.get_brush(0xFFFFFFFF);
                ctx.rt->DrawLine(D2D1::Point2F(box_x + 3.2f, ay), D2D1::Point2F(box_x + 6.0f, ay + 3.5f), br, 1.7f);
                ctx.rt->DrawLine(D2D1::Point2F(box_x + 6.0f, ay + 3.5f), D2D1::Point2F(box_x + 11.0f, ay - 4.0f), br, 1.7f);
            } else if (half) {
                ctx.rt->DrawLine(D2D1::Point2F(box_x + 3.0f, ay), D2D1::Point2F(box_x + 11.0f, ay), ctx.get_brush(t->accent), 1.8f);
            }
            text_x = box_x + 22.0f;
        }

        if (!items[i].icon.empty()) {
            draw_text(ctx, items[i].icon, style, items[i].disabled ? muted : fg, text_x, y, 22.0f, rh);
            text_x += 24.0f;
        }

        float right_limit = (float)bounds.w - style.pad_right - 8.0f;
        float actions_w = 0.0f;
        if (m_show_actions && (hot || selected) && !items[i].actions.empty()) {
            actions_w = (std::min)(112.0f, 22.0f + (float)items[i].actions.size() * style.font_size * 0.55f);
            float actions_x = (std::max)(text_x, right_limit - actions_w);
            draw_text(ctx, items[i].actions, style, t->accent, actions_x, y, right_limit - actions_x, rh);
            right_limit = actions_x - 8.0f;
        }
        if (m_lazy_mode && items[i].lazy) {
            std::wstring badge = items[i].loading ? L"加载中..." : L"待加载";
            float badge_w = items[i].loading ? 78.0f : 58.0f;
            float badge_x = (std::max)(text_x, right_limit - badge_w);
            draw_text(ctx, badge, style, muted, badge_x, y, right_limit - badge_x, rh);
            right_limit = badge_x - 8.0f;
        }
        if (!items[i].tag.empty()) {
            float tag_w = (std::min)(96.0f, 24.0f + (float)items[i].tag.size() * style.font_size * 0.55f);
            float tag_right = right_limit;
            float tag_left = (std::max)(text_x, tag_right - tag_w);
            D2D1_RECT_F tag_rect = D2D1::RectF(tag_left, y + 6.0f, tag_right, y + rh - 6.0f);
            ctx.rt->FillRoundedRectangle(ROUNDED(tag_rect, 10.0f, 10.0f), ctx.get_brush(with_alpha(t->accent, 0x22)));
            draw_text(ctx, items[i].tag, style, t->accent, tag_rect.left + 8.0f, y,
                (std::max)(0.0f, tag_rect.right - tag_rect.left - 16.0f), rh);
            right_limit = tag_left - 8.0f;
        }

        Color text_color = items[i].disabled ? with_alpha(muted, 0xAA) : (selected ? t->accent : fg);
        draw_text(ctx, items[i].label, style, text_color, text_x, y,
            (std::max)(0.0f, right_limit - text_x), rh);
        y += rh;
    }
    if (rendered == 0) {
        draw_text(ctx, L"🔎 没有匹配的节点", style, muted, 0.0f, (float)style.pad_top + 20.0f, (float)bounds.w, rh,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void TreeView::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (pressed && m_draggable && m_press_index >= 0 && can_drag(m_press_index)) {
        m_dragging = true;
        m_drop_index = idx;
        m_drop_type = 0;
        if (idx >= 0) {
            float rh = row_height();
            int row = 0;
            for (int i = 0; i < (int)items.size(); ++i) {
                if (!is_rendered_item(i)) continue;
                if (i == idx) break;
                ++row;
            }
            float local_y = y - ((float)style.pad_top + row * rh);
            m_drop_type = local_y > rh * 0.70f ? 2 : (local_y > rh * 0.35f ? 1 : 0);
        }
    }
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void TreeView::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    m_dragging = false;
    invalidate();
}

void TreeView::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_index = item_at(x, y);
    m_drag_index = m_press_index;
    invalidate();
}

void TreeView::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (m_dragging) {
        if (idx >= 0) move_subtree(m_drag_index, idx, m_drop_type);
    } else if (idx >= 0 && idx == m_press_index && !items[idx].disabled) {
        selected_index = idx;
        if (is_checkbox_hit(idx, x)) {
            set_item_checked(idx, !items[idx].checked);
        } else if (is_expander_hit(idx, x) || (m_expand_on_click_node && (has_children(idx) || items[idx].lazy))) {
            set_item_expanded(idx, !items[idx].expanded);
        } else if (m_check_on_click_node && m_show_checkbox) {
            set_item_checked(idx, !items[idx].checked);
        }
        emit_event(event_cb, 1, idx);
    }
    pressed = false;
    m_press_index = -1;
    m_drag_index = -1;
    m_dragging = false;
    m_drop_index = -1;
    m_hover_index = idx;
    invalidate();
}

void TreeView::on_key_down(int vk, int) {
    if (!m_keyboard_navigation || items.empty()) return;
    if (selected_index < 0 || !is_rendered_item(selected_index)) {
        selected_index = first_visible_index();
        invalidate();
        return;
    }

    if (vk == VK_UP) selected_index = next_visible_index(selected_index, -1);
    else if (vk == VK_DOWN) selected_index = next_visible_index(selected_index, 1);
    else if (vk == VK_HOME) selected_index = first_visible_index();
    else if (vk == VK_END) selected_index = last_visible_index();
    else if (vk == VK_LEFT) {
        if ((has_children(selected_index) || items[selected_index].lazy) && items[selected_index].expanded) {
            set_expanded_internal(selected_index, false);
        } else {
            int parent = parent_index(selected_index);
            if (parent >= 0) selected_index = parent;
        }
    } else if (vk == VK_RIGHT) {
        if (has_children(selected_index) || items[selected_index].lazy) {
            if (!items[selected_index].expanded) {
                set_expanded_internal(selected_index, true);
            } else {
                int child = next_visible_index(selected_index, 1);
                if (child != selected_index && parent_index(child) == selected_index) selected_index = child;
            }
        }
    } else if (vk == VK_SPACE && m_show_checkbox) {
        set_item_checked(selected_index, !items[selected_index].checked);
    } else if (vk == VK_RETURN && (has_children(selected_index) || items[selected_index].lazy)) {
        set_expanded_internal(selected_index, !items[selected_index].expanded);
    } else {
        return;
    }
    invalidate();
}
