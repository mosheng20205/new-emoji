#include "element_dropdown.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cmath>
#include <string>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color mix_color(Color a, Color b, float t) {
    if (t <= 0.0f) return a;
    if (t >= 1.0f) return b;
    auto mix = [t](unsigned ca, unsigned cb) -> unsigned {
        return (unsigned)std::lround((float)ca + ((float)cb - (float)ca) * t);
    };
    unsigned aa = (a >> 24) & 0xFF;
    unsigned ar = (a >> 16) & 0xFF;
    unsigned ag = (a >> 8) & 0xFF;
    unsigned ab = a & 0xFF;
    unsigned ba = (b >> 24) & 0xFF;
    unsigned br = (b >> 16) & 0xFF;
    unsigned bg = (b >> 8) & 0xFF;
    unsigned bb = b & 0xFF;
    return (mix(aa, ba) << 24) | (mix(ar, br) << 16) | (mix(ag, bg) << 8) | mix(ab, bb);
}

static Color variant_color(int variant, const Theme* t) {
    switch (variant) {
    case 1: return t->accent;
    case 2: return 0xFF16A34A;
    case 3: return 0xFFF59E0B;
    case 4: return 0xFFDC2626;
    case 6: return 0xFF0EA5E9;
    default: return t->button_bg;
    }
}

static Color variant_text_color(int variant, const Theme* t) {
    switch (variant) {
    case 1: return 0xFFFFFFFF;
    case 2: return 0xFFFFFFFF;
    case 3: return 0xFF1F2937;
    case 4: return 0xFFFFFFFF;
    case 5: return t->accent;
    case 6: return 0xFFFFFFFF;
    default: return t->text_primary;
    }
}

static Color hover_variant_color(Color solid, bool dark) {
    return dark ? mix_color(solid, 0xFFFFFFFF, 0.10f) : mix_color(solid, 0xFF000000, 0.08f);
}

static int clamp_int(int value, int lo, int hi) {
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

static const Element* root_element(const Element* el) {
    const Element* root = el;
    while (root && root->parent) root = root->parent;
    return root;
}

static const Element* find_element_by_id(const Element* el, int id) {
    if (!el) return nullptr;
    if (el->id == id) return el;
    for (const auto& ch : el->children) {
        if (const Element* found = find_element_by_id(ch.get(), id)) return found;
    }
    return nullptr;
}

static int popup_side(int placement) {
    if (placement >= 0 && placement <= 2) return 0;
    if (placement >= 3 && placement <= 5) return 1;
    if (placement >= 6 && placement <= 8) return 2;
    return 3;
}

static int popup_align(int placement) {
    int pos = placement % 3;
    return pos == 0 ? -1 : (pos == 2 ? 1 : 0);
}

static std::wstring trim_marker_space(const std::wstring& value) {
    size_t start = 0;
    while (start < value.size() && (value[start] == L' ' || value[start] == L'\t')) ++start;
    size_t end = value.size();
    while (end > start && (value[end - 1] == L' ' || value[end - 1] == L'\t')) --end;
    return value.substr(start, end - start);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
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

float Dropdown::effective_font_size() const {
    float base = style.font_size > 0.0f ? style.font_size : 14.0f;
    if (size == 2) return base * (13.0f / 14.0f);
    if (size == 3) return base * (12.0f / 14.0f);
    return base;
}

int Dropdown::trigger_pad_x() const {
    float scale = style.font_size > 0.0f ? style.font_size / 14.0f : 1.0f;
    int pad = 12;
    if (size == 1) pad = 10;
    else if (size == 2) pad = 8;
    else if (size == 3) pad = 6;
    return (std::max)(4, round_px((float)pad * scale));
}

int Dropdown::row_height() const {
    float scale = style.font_size > 0.0f ? style.font_size / 14.0f : 1.0f;
    int h = 34;
    if (size == 1) h = 32;
    else if (size == 2) h = 30;
    else if (size == 3) h = 28;
    return (std::max)(24, round_px((float)h * scale));
}

int Dropdown::arrow_width() const {
    float scale = style.font_size > 0.0f ? style.font_size / 14.0f : 1.0f;
    return (std::max)(20, round_px(24.0f * scale));
}

int Dropdown::split_arrow_width() const {
    float scale = style.font_size > 0.0f ? style.font_size / 14.0f : 1.0f;
    return (std::max)(32, round_px(38.0f * scale));
}

int Dropdown::visible_row_count() const {
    int count = (int)items.size();
    if (count > 8) count = 8;
    return count < 1 ? 1 : count;
}

int Dropdown::menu_width() const {
    int min_width = split_button ? bounds.w : (std::max)(bounds.w, 150);
    return (std::max)(min_width, 150);
}

int Dropdown::menu_height() const {
    return row_height() * visible_row_count();
}

int Dropdown::menu_x() const {
    if (popup_anchor_point_active) {
        int own_x = 0, own_y = 0;
        get_absolute_pos(own_x, own_y);
        int mw = menu_width();
        int x = popup_anchor_point_x;
        int side = popup_side(popup_placement);
        int align = popup_align(popup_placement);
        if (side == 2) {
            x = popup_anchor_point_x - mw - popup_offset;
        } else if (side == 3) {
            x = popup_anchor_point_x + popup_offset;
        } else {
            if (align > 0) x = popup_anchor_point_x - mw;
        }
        x += popup_offset_x;
        const Element* root = root_element(this);
        if (root) {
            int rx = 0, ry = 0;
            root->get_absolute_pos(rx, ry);
            int min_x = rx + 6;
            int max_x = rx + root->bounds.w - mw - 6;
            if (max_x < min_x) max_x = min_x;
            x = (std::max)(min_x, (std::min)(max_x, x));
        }
        return x - own_x;
    }
    if (popup_anchor_element_id <= 0) return 0;
    const Element* root = root_element(this);
    const Element* anchor = find_element_by_id(root, popup_anchor_element_id);
    if (!anchor) return 0;

    int own_x = 0, own_y = 0;
    int ax = 0, ay = 0;
    get_absolute_pos(own_x, own_y);
    anchor->get_absolute_pos(ax, ay);

    int mw = menu_width();
    int mh = menu_height();
    int x = ax + (anchor->bounds.w - mw) / 2;
    int side = popup_side(popup_placement);
    int align = popup_align(popup_placement);
    if (side == 2) {
        x = ax - mw - popup_offset;
    } else if (side == 3) {
        x = ax + anchor->bounds.w + popup_offset;
    } else {
        if (align < 0) x = ax;
        else if (align > 0) x = ax + anchor->bounds.w - mw;
    }

    x += popup_offset_x;
    if (root) {
        int rx = 0, ry = 0;
        root->get_absolute_pos(rx, ry);
        int min_x = rx + 6;
        int max_x = rx + root->bounds.w - mw - 6;
        if (max_x < min_x) max_x = min_x;
        x = (std::max)(min_x, (std::min)(max_x, x));
    }
    (void)mh;
    return x - own_x;
}

int Dropdown::menu_y() const {
    if (popup_anchor_point_active) {
        int own_x = 0, own_y = 0;
        get_absolute_pos(own_x, own_y);
        int mh = menu_height();
        int y = popup_anchor_point_y + popup_offset;
        int side = popup_side(popup_placement);
        if (side == 0) {
            y = popup_anchor_point_y - mh - popup_offset;
        } else if (side == 2 || side == 3) {
            y = popup_anchor_point_y - mh / 2;
            int align = popup_align(popup_placement);
            if (align < 0) y = popup_anchor_point_y;
            else if (align > 0) y = popup_anchor_point_y - mh;
        }
        y += popup_offset_y;
        const Element* root = root_element(this);
        if (root) {
            int rx = 0, ry = 0;
            root->get_absolute_pos(rx, ry);
            int min_y = ry + 6;
            int max_y = ry + root->bounds.h - mh - 6;
            if (max_y < min_y) max_y = min_y;
            y = (std::max)(min_y, (std::min)(max_y, y));
        }
        return y - own_y;
    }
    if (popup_anchor_element_id > 0) {
        const Element* root = root_element(this);
        const Element* anchor = find_element_by_id(root, popup_anchor_element_id);
        if (!anchor) return bounds.h + 4;

        int own_x = 0, own_y = 0;
        int ax = 0, ay = 0;
        get_absolute_pos(own_x, own_y);
        anchor->get_absolute_pos(ax, ay);

        int mh = menu_height();
        int y = ay + anchor->bounds.h + popup_offset;
        int side = popup_side(popup_placement);
        int align = popup_align(popup_placement);
        if (side == 2 || side == 3) {
            y = ay + (anchor->bounds.h - mh) / 2;
            if (align < 0) y = ay;
            else if (align > 0) y = ay + anchor->bounds.h - mh;
        } else if (side == 0) {
            y = ay - mh - popup_offset;
        }
        y += popup_offset_y;

        if (root) {
            int rx = 0, ry = 0;
            root->get_absolute_pos(rx, ry);
            int min_y = ry + 6;
            int max_y = ry + root->bounds.h - mh - 6;
            if (max_y < min_y) max_y = min_y;
            y = (std::max)(min_y, (std::min)(max_y, y));
        }
        return y - own_y;
    }
    int mh = menu_height();
    if (parent && bounds.y + bounds.h + mh + 6 > parent->bounds.h && bounds.y > mh + 6) {
        return -mh - 4;
    }
    return bounds.h + 4;
}

void Dropdown::resize_meta() {
    item_icons.resize(items.size());
    item_commands.resize(items.size());
    divided_items.resize(items.size(), false);
    marker_disabled_items.resize(items.size(), false);
    if (disabled_items.size() != items.size()) disabled_items.resize(items.size(), false);

    disabled_items = marker_disabled_items;
    for (int index : m_runtime_disabled_indices) {
        if (index >= 0 && index < (int)disabled_items.size()) disabled_items[index] = true;
    }
}

void Dropdown::set_items(const std::vector<std::wstring>& values) {
    items = values;
    display_items.clear();
    item_levels.clear();
    marker_disabled_items.clear();
    display_items.reserve(items.size());
    item_levels.reserve(items.size());
    marker_disabled_items.reserve(items.size());

    for (const auto& raw_value : items) {
        std::wstring value = trim_marker_space(raw_value);
        int level = 0;
        bool disabled = false;
        bool consumed = true;
        while (consumed && !value.empty()) {
            consumed = false;
            if (!value.empty() && value[0] == L'!') {
                disabled = true;
                value = trim_marker_space(value.substr(1));
                consumed = true;
            }
            while (!value.empty() && value[0] == L'>') {
                ++level;
                value = trim_marker_space(value.substr(1));
                consumed = true;
            }
        }
        display_items.push_back(value.empty() ? raw_value : value);
        item_levels.push_back(level);
        marker_disabled_items.push_back(disabled);
    }

    m_scroll = 0;
    m_hover_index = -1;
    resize_meta();
    if (items.empty()) selected_index = -1;
    else set_selected_index(selected_index);
    invalidate();
}

void Dropdown::set_selected_index(int index) {
    if (items.empty()) {
        selected_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)items.size()) index = (int)items.size() - 1;
        if (is_disabled(index)) {
            int next = next_enabled_index(index, 1);
            if (next < 0) next = next_enabled_index(index, -1);
            selected_index = next;
        } else {
            selected_index = index;
        }
    }
    ensure_selected_visible();
    invalidate();
}

void Dropdown::set_open(bool next_open) {
    open = next_open && !items.empty();
    if (open) ensure_selected_visible();
    invalidate();
}

void Dropdown::set_options(int next_trigger_mode, int next_hide_on_click, int next_split_button,
                           int next_button_variant, int next_size, int next_trigger_style) {
    trigger_mode = clamp_int(next_trigger_mode, 0, 2);
    hide_on_click = next_hide_on_click != 0;
    split_button = next_split_button != 0;
    button_variant = clamp_int(next_button_variant, 0, 6);
    size = clamp_int(next_size, 0, 3);
    trigger_style = clamp_int(next_trigger_style, 0, 1);
    if (trigger_mode == 2) m_hover_part = PartNone;
    invalidate();
}

void Dropdown::set_item_meta(const std::vector<std::wstring>& icons,
                             const std::vector<std::wstring>& commands,
                             const std::vector<int>& divided_indices) {
    item_icons.assign(items.size(), L"");
    item_commands.assign(items.size(), L"");
    divided_items.assign(items.size(), false);

    for (size_t i = 0; i < item_icons.size() && i < icons.size(); ++i) item_icons[i] = icons[i];
    for (size_t i = 0; i < item_commands.size() && i < commands.size(); ++i) item_commands[i] = commands[i];
    for (int index : divided_indices) {
        if (index >= 0 && index < (int)divided_items.size()) divided_items[index] = true;
    }
    invalidate();
}

void Dropdown::set_disabled_indices(const std::vector<int>& indices) {
    m_runtime_disabled_indices = indices;
    resize_meta();
    if (selected_index >= 0 && is_disabled(selected_index)) set_selected_index(selected_index);
    clamp_scroll();
    invalidate();
}

const std::wstring& Dropdown::item_icon(int index) const {
    static const std::wstring empty;
    if (index < 0 || index >= (int)item_icons.size()) return empty;
    return item_icons[(size_t)index];
}

const std::wstring& Dropdown::item_command(int index) const {
    static const std::wstring empty;
    if (index < 0 || index >= (int)item_commands.size()) return empty;
    return item_commands[(size_t)index];
}

bool Dropdown::is_divided(int index) const {
    return index >= 0 && index < (int)divided_items.size() && divided_items[(size_t)index];
}

bool Dropdown::is_open() const {
    return open;
}

void Dropdown::set_popup_anchor(int anchor_id) {
    popup_anchor_element_id = anchor_id;
    popup_anchor_point_active = false;
    trigger_mode = 2;
    invalidate();
}

void Dropdown::set_popup_anchor_point(int absolute_x, int absolute_y) {
    popup_anchor_point_active = true;
    popup_anchor_element_id = 0;
    popup_anchor_point_x = absolute_x;
    popup_anchor_point_y = absolute_y;
    trigger_mode = 2;
    invalidate();
}

void Dropdown::set_popup_placement(int placement, int offset_x, int offset_y) {
    popup_placement = clamp_int(placement, 0, 11);
    popup_offset_x = offset_x;
    popup_offset_y = offset_y;
    invalidate();
}

void Dropdown::set_popup_dismiss_behavior(bool close_on_outside, bool close_on_escape) {
    popup_close_on_outside = close_on_outside;
    popup_close_on_escape = close_on_escape;
    invalidate();
}

Rect Dropdown::popup_rect() const {
    return { menu_x(), menu_y(), menu_width(), menu_height() };
}

int Dropdown::item_count() const {
    return (int)items.size();
}

int Dropdown::disabled_count() const {
    int count = 0;
    for (bool disabled : disabled_items) {
        if (disabled) ++count;
    }
    return count;
}

int Dropdown::selected_level() const {
    if (selected_index < 0 || selected_index >= (int)item_levels.size()) return -1;
    return item_levels[selected_index];
}

int Dropdown::hover_index() const {
    return m_hover_index;
}

bool Dropdown::is_disabled(int index) const {
    return index < 0 || index >= (int)disabled_items.size() || disabled_items[(size_t)index];
}

bool Dropdown::has_child(int index) const {
    return index >= 0 && index + 1 < (int)item_levels.size() &&
           item_levels[index + 1] > item_levels[index];
}

void Dropdown::clamp_scroll() {
    int max_scroll = (std::max)(0, (int)items.size() - visible_row_count());
    if (m_scroll < 0) m_scroll = 0;
    if (m_scroll > max_scroll) m_scroll = max_scroll;
}

void Dropdown::ensure_selected_visible() {
    if (selected_index < 0) {
        clamp_scroll();
        return;
    }
    int visible = visible_row_count();
    if (selected_index < m_scroll) m_scroll = selected_index;
    if (selected_index >= m_scroll + visible) m_scroll = selected_index - visible + 1;
    clamp_scroll();
}

int Dropdown::next_enabled_index(int start, int delta) const {
    if (items.empty() || delta == 0) return -1;
    int index = start;
    if (index < 0 || index >= (int)items.size()) index = delta > 0 ? -1 : (int)items.size();
    for (int step = 0; step < (int)items.size(); ++step) {
        index += delta > 0 ? 1 : -1;
        if (index < 0 || index >= (int)items.size()) return -1;
        if (!is_disabled(index)) return index;
    }
    return -1;
}

void Dropdown::fire_command(int index) {
    if (!command_cb || index < 0 || index >= (int)items.size()) return;
    std::wstring value = item_command(index);
    if (value.empty()) value = index < (int)display_items.size() ? display_items[index] : items[index];
    std::string utf8 = wide_to_utf8(value);
    command_cb(id, index, reinterpret_cast<const unsigned char*>(utf8.data()), (int)utf8.size());
}

void Dropdown::choose_item(int index) {
    if (is_disabled(index)) return;
    set_selected_index(index);
    fire_command(index);
    if (hide_on_click) open = false;
}

int Dropdown::item_at(int x, int y) const {
    if (!open || items.empty()) return -1;
    int mx = menu_x();
    int my = menu_y();
    int mh = menu_height();
    int mw = menu_width();
    if (x < mx || x >= mx + mw || y < my || y >= my + mh) return -1;
    int idx = m_scroll + (y - my) / row_height();
    return (idx >= 0 && idx < (int)items.size()) ? idx : -1;
}

bool Dropdown::hover_bridge_contains(int x, int y) const {
    if (!open || trigger_mode != 1 || items.empty()) return false;

    Rect trigger = { 0, 0, bounds.w, bounds.h };
    Rect menu = popup_rect();
    int left = (std::min)(trigger.x, menu.x);
    int top = (std::min)(trigger.y, menu.y);
    int right = (std::max)(trigger.right(), menu.right());
    int bottom = (std::max)(trigger.bottom(), menu.bottom());

    Rect bridge;
    if (trigger.bottom() <= menu.y) {
        bridge = { left, trigger.bottom(), right - left, menu.y - trigger.bottom() };
    } else if (menu.bottom() <= trigger.y) {
        bridge = { left, menu.bottom(), right - left, trigger.y - menu.bottom() };
    } else if (trigger.right() <= menu.x) {
        bridge = { trigger.right(), top, menu.x - trigger.right(), bottom - top };
    } else if (menu.right() <= trigger.x) {
        bridge = { menu.right(), top, trigger.x - menu.right(), bottom - top };
    } else {
        return false;
    }
    return bridge.w > 0 && bridge.h > 0 && bridge.contains(x, y);
}

Dropdown::Part Dropdown::part_at(int x, int y, int* item_index) const {
    int idx = item_at(x, y);
    if (item_index) *item_index = idx;
    if (idx >= 0) return PartItem;
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        if (split_button && trigger_style == 0) {
            return x >= bounds.w - split_arrow_width() ? PartSplitArrow : PartSplitMain;
        }
        return PartMain;
    }
    return PartNone;
}

Element* Dropdown::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* Dropdown::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return (item_at(lx, ly) >= 0 || hover_bridge_contains(lx, ly)) ? this : nullptr;
}

void Dropdown::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    ElementStyle text_style = style;
    text_style.font_size = effective_font_size();
    int pad_x = trigger_pad_x();
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    Color accent = t->accent;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;

    if (trigger_style == 1) {
        Color link_color = style.fg_color ? style.fg_color : accent;
        if (hovered || open) link_color = hover_variant_color(link_color, dark);
        float arrow_w = (float)arrow_width();
        draw_text(ctx, text.empty() ? L"下拉菜单" : text, text_style, link_color,
                  0.0f, 0.0f, (float)bounds.w - arrow_w, (float)bounds.h,
                  DWRITE_TEXT_ALIGNMENT_LEADING);
        draw_text(ctx, open ? L"▲" : L"▼", text_style, link_color,
                  (float)bounds.w - arrow_w, 0.0f, arrow_w, (float)bounds.h);
        ctx.rt->SetTransform(saved);
        return;
    }

    Color bg = style.bg_color ? style.bg_color : t->button_bg;
    Color border = style.border_color ? style.border_color : t->border_default;
    if (button_variant >= 1) {
        bg = variant_color(button_variant, t);
        border = bg;
        fg = variant_text_color(button_variant, t);
    }
    if (!enabled) {
        bg = dark ? 0xFF2A2D3A : 0xFFE5E7EB;
        border = dark ? 0xFF3A3D4C : 0xFFD1D5DB;
        fg = t->text_muted;
    } else if (pressed) {
        bg = button_variant >= 1 ? hover_variant_color(bg, dark) : t->button_press;
        border = button_variant >= 1 ? bg : t->button_press;
    } else if (hovered || open || has_focus) {
        bg = button_variant >= 1 ? hover_variant_color(bg, dark) : t->button_hover;
        border = open || has_focus ? t->edit_focus : (button_variant >= 1 ? bg : t->button_hover);
    }

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    float arrow_w = split_button ? (float)split_arrow_width() : (float)arrow_width();
    if (split_button) {
        float split_x = (float)bounds.w - arrow_w;
        D2D1_RECT_F arrow_rect = { split_x, 1.0f, (float)bounds.w - 1.0f, (float)bounds.h - 1.0f };
        Color overlay = 0;
        if (m_press_part == PartSplitArrow) overlay = with_alpha(0xFF000000, dark ? 0x26 : 0x12);
        else if (m_hover_part == PartSplitArrow || open) overlay = with_alpha(0xFFFFFFFF, dark ? 0x12 : 0x22);
        if (overlay) ctx.rt->FillRectangle(arrow_rect, ctx.get_brush(overlay));
        ctx.rt->DrawLine(D2D1::Point2F(split_x, 6.0f),
                         D2D1::Point2F(split_x, (float)bounds.h - 6.0f),
                         ctx.get_brush(with_alpha(fg, 0x66)), 1.0f);
    }

    draw_text(ctx, text.empty() ? L"下拉菜单" : text, text_style, fg,
              (float)pad_x, 0.0f,
              (float)bounds.w - (float)pad_x * 2.0f - arrow_w,
              (float)bounds.h, DWRITE_TEXT_ALIGNMENT_CENTER);
    draw_text(ctx, open ? L"▲" : L"▼", text_style, fg,
              (float)bounds.w - arrow_w, 0.0f, arrow_w, (float)bounds.h);

    ctx.rt->SetTransform(saved);
}

void Dropdown::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || items.empty() || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    ElementStyle text_style = style;
    text_style.font_size = effective_font_size();
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF242637 : 0xFFFFFFFF;
    int my = menu_y();
    int mw = menu_width();
    int rh = row_height();
    int mh = menu_height();
    int mx = menu_x();
    D2D1_RECT_F menu = { (float)mx, (float)my, (float)(mx + mw), (float)(my + mh) };
    ctx.rt->FillRoundedRectangle(ROUNDED(menu, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(menu.left + 0.5f, menu.top + 0.5f,
        menu.right - 0.5f, menu.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    int visible = visible_row_count();
    int end = (std::min)((int)items.size(), m_scroll + visible);
    for (int i = m_scroll; i < end; ++i) {
        float y = (float)(my + (i - m_scroll) * rh);
        bool disabled = is_disabled(i);
        if (is_divided(i)) {
            ctx.rt->DrawLine(D2D1::Point2F((float)mx + 8.0f, y + 0.5f),
                             D2D1::Point2F((float)(mx + mw) - 8.0f, y + 0.5f),
                             ctx.get_brush(t->border_default), 1.0f);
        }
        if (!disabled && (i == m_hover_index || i == selected_index)) {
            Color row_bg = i == selected_index ? (t->accent & 0x33FFFFFF) : t->button_hover;
            D2D1_RECT_F row = { (float)mx + 2.0f, y + 1.0f, (float)(mx + mw) - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(row_bg));
        }
        int level = i < (int)item_levels.size() ? item_levels[i] : 0;
        float indent = (float)(mx + trigger_pad_x() + level * 18);
        Color item_color = disabled ? t->text_secondary : (i == selected_index ? t->accent : fg);
        const std::wstring& icon = item_icon(i);
        float icon_w = icon.empty() ? 0.0f : 22.0f;
        if (!icon.empty()) {
            draw_text(ctx, icon, text_style, item_color, indent, y, icon_w, (float)rh);
        }
        draw_text(ctx, i < (int)display_items.size() ? display_items[i] : items[i], text_style, item_color,
                  indent + icon_w, y, (float)(mx + mw) - indent - icon_w - style.pad_right - 20.0f, (float)rh,
                  DWRITE_TEXT_ALIGNMENT_LEADING);
        if (has_child(i)) {
            draw_text(ctx, L">", text_style, disabled ? t->text_secondary : t->text_secondary,
                      (float)(mx + mw) - style.pad_right - 18.0f, y, 18.0f, (float)rh);
        }
    }

    if ((int)items.size() > visible) {
        float track_x = (float)(mx + mw) - 5.0f;
        float track_h = (float)mh - 8.0f;
        float thumb_h = (std::max)(18.0f, track_h * visible / (float)items.size());
        int max_scroll = (std::max)(1, (int)items.size() - visible);
        float thumb_y = (float)my + 4.0f + (track_h - thumb_h) * m_scroll / (float)max_scroll;
        D2D1_RECT_F thumb = { track_x, thumb_y, track_x + 3.0f, thumb_y + thumb_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(thumb, 1.5f, 1.5f), ctx.get_brush(t->border_default));
    }

    ctx.rt->SetTransform(saved);
}

void Dropdown::on_mouse_enter() {
    hovered = true;
    if (trigger_mode == 1) set_open(true);
    invalidate();
}

void Dropdown::on_mouse_move(int x, int y) {
    int idx = -1;
    Part part = part_at(x, y, &idx);
    if (idx >= 0 && is_disabled(idx)) idx = -1;
    if (trigger_mode == 1 && (part == PartMain || part == PartSplitArrow || part == PartSplitMain)) {
        set_open(true);
    }
    if (idx != m_hover_index || part != m_hover_part) {
        m_hover_index = idx;
        m_hover_part = part;
        invalidate();
    }
}

void Dropdown::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    if (trigger_mode == 1) open = false;
    invalidate();
}

void Dropdown::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_index);
    if (m_press_part == PartItem && is_disabled(m_press_index)) {
        m_press_part = PartNone;
        m_press_index = -1;
    }
    pressed = true;
    invalidate();
}

void Dropdown::on_mouse_up(int x, int y, MouseButton) {
    int idx = -1;
    Part part = part_at(x, y, &idx);
    if (part == PartItem && m_press_part == PartItem && idx == m_press_index && !is_disabled(idx)) {
        choose_item(idx);
    } else if (split_button && part == PartSplitMain && m_press_part == PartSplitMain) {
        if (main_click_cb) main_click_cb(id);
    } else if ((part == PartMain || part == PartSplitArrow) &&
               (m_press_part == PartMain || m_press_part == PartSplitArrow) &&
               trigger_mode == 0) {
        open = !open;
        if (open) ensure_selected_visible();
    }
    m_press_part = PartNone;
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Dropdown::on_mouse_wheel(int, int, int delta) {
    if (!open || items.empty()) return;
    m_scroll += delta > 0 ? -3 : 3;
    clamp_scroll();
    invalidate();
}

void Dropdown::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        if (!open && trigger_mode != 2) {
            open = true;
            ensure_selected_visible();
        } else if (open) {
            int idx = m_hover_index >= 0 ? m_hover_index : selected_index;
            if (!is_disabled(idx)) choose_item(idx);
        }
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_DOWN) {
        if (!open && trigger_mode != 2) open = true;
        int next = next_enabled_index(selected_index, 1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_UP) {
        if (!open && trigger_mode != 2) open = true;
        int next = next_enabled_index(selected_index, -1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_NEXT) {
        if (!open && trigger_mode != 2) open = true;
        for (int i = 0; i < visible_row_count(); ++i) {
            int next = next_enabled_index(selected_index, 1);
            if (next >= 0) set_selected_index(next);
        }
    } else if (vk == VK_PRIOR) {
        if (!open && trigger_mode != 2) open = true;
        for (int i = 0; i < visible_row_count(); ++i) {
            int next = next_enabled_index(selected_index, -1);
            if (next >= 0) set_selected_index(next);
        }
    } else if (vk == VK_HOME) {
        if (!open && trigger_mode != 2) open = true;
        int next = next_enabled_index(-1, 1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_END) {
        if (!open && trigger_mode != 2) open = true;
        int next = next_enabled_index((int)items.size(), -1);
        if (next >= 0) set_selected_index(next);
    }
    invalidate();
}

void Dropdown::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    invalidate();
}
