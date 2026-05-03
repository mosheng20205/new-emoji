#include "element_dropdown.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
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

int Dropdown::row_height() const {
    int h = round_px(style.font_size * 1.9f);
    return h < 28 ? 28 : h;
}

int Dropdown::visible_row_count() const {
    int count = (int)items.size();
    if (count > 8) count = 8;
    return count < 1 ? 1 : count;
}

int Dropdown::menu_width() const {
    return (std::max)(bounds.w, 150);
}

int Dropdown::menu_height() const {
    return row_height() * visible_row_count();
}

int Dropdown::menu_y() const {
    int mh = menu_height();
    if (parent && bounds.y + bounds.h + mh + 6 > parent->bounds.h && bounds.y > mh + 6) {
        return -mh - 4;
    }
    return bounds.h + 4;
}

void Dropdown::set_items(const std::vector<std::wstring>& values) {
    items = values;
    display_items.clear();
    item_levels.clear();
    disabled_items.clear();
    display_items.reserve(items.size());
    item_levels.reserve(items.size());
    disabled_items.reserve(items.size());

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
        disabled_items.push_back(disabled);
    }

    m_scroll = 0;
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

bool Dropdown::is_open() const {
    return open;
}

int Dropdown::item_count() const {
    return (int)items.size();
}

void Dropdown::set_disabled_indices(const std::vector<int>& indices) {
    if (disabled_items.size() != items.size()) disabled_items.assign(items.size(), false);
    for (int index : indices) {
        if (index >= 0 && index < (int)disabled_items.size()) disabled_items[index] = true;
    }
    if (selected_index >= 0 && is_disabled(selected_index)) set_selected_index(selected_index);
    clamp_scroll();
    invalidate();
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
    return index < 0 || index >= (int)disabled_items.size() || disabled_items[index];
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

int Dropdown::item_at(int x, int y) const {
    if (!open || items.empty()) return -1;
    int my = menu_y();
    int mh = menu_height();
    if (x < 0 || x >= menu_width() || y < my || y >= my + mh) return -1;
    int idx = m_scroll + (y - my) / row_height();
    return (idx >= 0 && idx < (int)items.size()) ? idx : -1;
}

Dropdown::Part Dropdown::part_at(int x, int y, int* item_index) const {
    int idx = item_at(x, y);
    if (item_index) *item_index = idx;
    if (idx >= 0) return PartItem;
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
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
    return item_at(lx, ly) >= 0 ? this : nullptr;
}

void Dropdown::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->button_bg;
    Color border = open || has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->border_default);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    if (hovered && !open) bg = t->button_hover;
    if (pressed) bg = t->button_press;

    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    float arrow_w = 24.0f;
    draw_text(ctx, text.empty() ? L"下拉菜单" : text, style, fg,
              (float)style.pad_left, 0.0f,
              (float)bounds.w - style.pad_left - style.pad_right - arrow_w,
              (float)bounds.h, DWRITE_TEXT_ALIGNMENT_LEADING);
    draw_text(ctx, open ? L"▲" : L"▼", style, t->text_secondary,
              (float)bounds.w - style.pad_right - arrow_w, 0.0f, arrow_w, (float)bounds.h);

    ctx.rt->SetTransform(saved);
}

void Dropdown::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || items.empty() || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF242637 : 0xFFFFFFFF;
    int my = menu_y();
    int mw = menu_width();
    int rh = row_height();
    int mh = menu_height();
    D2D1_RECT_F menu = { 0, (float)my, (float)mw, (float)(my + mh) };
    ctx.rt->FillRoundedRectangle(ROUNDED(menu, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(menu.left + 0.5f, menu.top + 0.5f,
        menu.right - 0.5f, menu.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    int visible = visible_row_count();
    int end = (std::min)((int)items.size(), m_scroll + visible);
    for (int i = m_scroll; i < end; ++i) {
        float y = (float)(my + (i - m_scroll) * rh);
        bool disabled = is_disabled(i);
        if (!disabled && (i == m_hover_index || i == selected_index)) {
            Color row_bg = i == selected_index ? (t->accent & 0x33FFFFFF) : t->button_hover;
            D2D1_RECT_F row = { 2.0f, y + 1.0f, (float)mw - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(row_bg));
        }
        int level = i < (int)item_levels.size() ? item_levels[i] : 0;
        float indent = (float)(style.pad_left + level * 18);
        Color item_color = disabled ? t->text_secondary : (i == selected_index ? t->accent : fg);
        draw_text(ctx, i < (int)display_items.size() ? display_items[i] : items[i], style, item_color,
                  indent, y, (float)mw - indent - style.pad_right - 20.0f, (float)rh,
                  DWRITE_TEXT_ALIGNMENT_LEADING);
        if (has_child(i)) {
            draw_text(ctx, L">", style, disabled ? t->text_secondary : t->text_secondary,
                      (float)mw - style.pad_right - 18.0f, y, 18.0f, (float)rh);
        }
    }

    if ((int)items.size() > visible) {
        float track_x = (float)mw - 5.0f;
        float track_h = (float)mh - 8.0f;
        float thumb_h = (std::max)(18.0f, track_h * visible / (float)items.size());
        int max_scroll = (std::max)(1, (int)items.size() - visible);
        float thumb_y = (float)my + 4.0f + (track_h - thumb_h) * m_scroll / (float)max_scroll;
        D2D1_RECT_F thumb = { track_x, thumb_y, track_x + 3.0f, thumb_y + thumb_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(thumb, 1.5f, 1.5f), ctx.get_brush(t->border_default));
    }

    ctx.rt->SetTransform(saved);
}

void Dropdown::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (idx >= 0 && is_disabled(idx)) idx = -1;
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Dropdown::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    m_press_part = PartNone;
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
        set_selected_index(idx);
        open = false;
    } else if (part == PartMain && m_press_part == PartMain) {
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
        if (!open) {
            open = true;
            ensure_selected_visible();
        } else {
            int idx = m_hover_index >= 0 ? m_hover_index : selected_index;
            if (!is_disabled(idx)) {
                set_selected_index(idx);
                open = false;
            }
        }
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_DOWN) {
        if (!open) open = true;
        int next = next_enabled_index(selected_index, 1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_UP) {
        if (!open) open = true;
        int next = next_enabled_index(selected_index, -1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_NEXT) {
        if (!open) open = true;
        for (int i = 0; i < visible_row_count(); ++i) {
            int next = next_enabled_index(selected_index, 1);
            if (next >= 0) set_selected_index(next);
        }
    } else if (vk == VK_PRIOR) {
        if (!open) open = true;
        for (int i = 0; i < visible_row_count(); ++i) {
            int next = next_enabled_index(selected_index, -1);
            if (next >= 0) set_selected_index(next);
        }
    } else if (vk == VK_HOME) {
        if (!open) open = true;
        int next = next_enabled_index(-1, 1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_END) {
        if (!open) open = true;
        int next = next_enabled_index((int)items.size(), -1);
        if (next >= 0) set_selected_index(next);
    }
    invalidate();
}

void Dropdown::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    m_press_part = PartNone;
    invalidate();
}
