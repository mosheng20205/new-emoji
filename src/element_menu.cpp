#include "element_menu.h"
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

void Menu::set_items(const std::vector<std::wstring>& values) {
    items = values;
    display_items.clear();
    item_levels.clear();
    disabled_items.clear();
    expanded_items.clear();
    display_items.reserve(items.size());
    item_levels.reserve(items.size());
    disabled_items.reserve(items.size());
    expanded_items.reserve(items.size());

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
        expanded_items.push_back(true);
    }
    set_active_index(active_index);
}

void Menu::set_active_index(int index) {
    if (items.empty()) {
        active_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)items.size()) index = (int)items.size() - 1;
        if (is_disabled(index) || !is_visible_item(index)) {
            int next = next_visible_enabled(index, 1);
            if (next < 0) next = next_visible_enabled(index, -1);
            active_index = next;
        } else {
            active_index = index;
        }
    }
    invalidate();
}

void Menu::set_orientation(int value) {
    orientation = value == 1 ? 1 : 0;
    invalidate();
}

int Menu::item_count() const {
    return (int)items.size();
}

void Menu::set_expanded_indices(const std::vector<int>& indices) {
    expanded_items.assign(items.size(), false);
    for (int index : indices) {
        if (index >= 0 && index < (int)expanded_items.size() && has_child(index)) {
            expanded_items[index] = true;
        }
    }
    if (active_index >= 0 && !is_visible_item(active_index)) set_active_index(active_index);
    invalidate();
}

int Menu::visible_count() const {
    return (int)visible_indices().size();
}

int Menu::expanded_count() const {
    int count = 0;
    for (int i = 0; i < (int)expanded_items.size(); ++i) {
        if (expanded_items[i] && has_child(i)) ++count;
    }
    return count;
}

int Menu::active_level() const {
    if (active_index < 0 || active_index >= (int)item_levels.size()) return -1;
    return item_levels[active_index];
}

int Menu::hover_index() const {
    return m_hover_index;
}

std::wstring Menu::active_path() const {
    if (active_index < 0 || active_index >= (int)items.size()) return L"";
    std::vector<std::wstring> parts;
    int level = active_level();
    for (int i = active_index; i >= 0; --i) {
        if (i >= (int)item_levels.size()) continue;
        if (item_levels[i] <= level) {
            parts.push_back(i < (int)display_items.size() ? display_items[i] : items[i]);
            level = item_levels[i] - 1;
        }
    }
    std::wstring path;
    for (auto it = parts.rbegin(); it != parts.rend(); ++it) {
        if (!path.empty()) path += L" / ";
        path += *it;
    }
    return path;
}

bool Menu::is_disabled(int index) const {
    return index < 0 || index >= (int)disabled_items.size() || disabled_items[index];
}

bool Menu::has_child(int index) const {
    return index >= 0 && index + 1 < (int)item_levels.size() &&
           item_levels[index + 1] > item_levels[index];
}

bool Menu::is_expanded(int index) const {
    return index >= 0 && index < (int)expanded_items.size() && expanded_items[index];
}

bool Menu::is_visible_item(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    int level = item_levels[index];
    for (int i = index - 1; i >= 0 && level > 0; --i) {
        if (item_levels[i] < level) {
            if (!is_expanded(i)) return false;
            level = item_levels[i];
        }
    }
    return true;
}

int Menu::visible_position(int index) const {
    int pos = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_visible_item(i)) continue;
        if (i == index) return pos;
        ++pos;
    }
    return -1;
}

std::vector<int> Menu::visible_indices() const {
    std::vector<int> result;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_visible_item(i)) result.push_back(i);
    }
    return result;
}

int Menu::next_visible_enabled(int start, int delta) const {
    std::vector<int> visible = visible_indices();
    if (visible.empty() || delta == 0) return -1;
    int pos = -1;
    for (int i = 0; i < (int)visible.size(); ++i) {
        if (visible[i] == start) {
            pos = i;
            break;
        }
    }
    if (pos < 0) pos = delta > 0 ? -1 : (int)visible.size();
    for (;;) {
        pos += delta > 0 ? 1 : -1;
        if (pos < 0 || pos >= (int)visible.size()) return -1;
        if (!is_disabled(visible[pos])) return visible[pos];
    }
}

void Menu::toggle_expanded(int index) {
    if (!has_child(index) || index < 0 || index >= (int)expanded_items.size()) return;
    expanded_items[index] = !expanded_items[index];
    if (active_index >= 0 && !is_visible_item(active_index)) active_index = index;
}

Rect Menu::item_rect(int index) const {
    if (items.empty()) return {};
    int pos = visible_position(index);
    if (pos < 0) return {};
    if (orientation == 1) {
        int h = round_px(style.font_size * 2.4f);
        if (h < 34) h = 34;
        return { style.pad_left, style.pad_top + pos * h,
                 bounds.w - style.pad_left - style.pad_right, h };
    }
    int gap = round_px(6.0f * style.font_size / 14.0f);
    int x = style.pad_left;
    std::vector<int> visible = visible_indices();
    for (int i = 0; i < pos; ++i) {
        int item_index = visible[i];
        int level = item_index < (int)item_levels.size() ? item_levels[item_index] : 0;
        int label_len = item_index < (int)display_items.size() ? (int)display_items[item_index].size() : (int)items[item_index].size();
        x += round_px((float)label_len * style.font_size * 0.76f + 34.0f + level * 14.0f) + gap;
    }
    int level = index < (int)item_levels.size() ? item_levels[index] : 0;
    int label_len = index < (int)display_items.size() ? (int)display_items[index].size() : (int)items[index].size();
    int w = round_px((float)label_len * style.font_size * 0.76f + 34.0f + level * 14.0f);
    int h = bounds.h - style.pad_top - style.pad_bottom;
    if (h < 28) h = 28;
    return { x, style.pad_top, w, h };
}

int Menu::item_at(int x, int y) const {
    std::vector<int> visible = visible_indices();
    for (int i : visible) {
        if (item_rect(i).contains(x, y)) return i;
    }
    return -1;
}

void Menu::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F frame = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(frame, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    std::vector<int> visible = visible_indices();
    for (int i : visible) {
        Rect r = item_rect(i);
        if (r.x >= bounds.w || r.y >= bounds.h) break;
        bool active = i == active_index;
        bool hot = i == m_hover_index;
        bool disabled = is_disabled(i);
        if (!disabled && (active || hot)) {
            D2D1_RECT_F rr = { (float)r.x + 3.0f, (float)r.y + 3.0f,
                               (float)(r.x + r.w) - 3.0f, (float)(r.y + r.h) - 3.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                ctx.get_brush(active ? (t->accent & 0x33FFFFFF) : t->button_hover));
        }
        int level = i < (int)item_levels.size() ? item_levels[i] : 0;
        float indent = orientation == 1 ? (float)(level * 18) : (float)(level * 10);
        Color item_color = disabled ? t->text_secondary : (active ? t->accent : fg);
        if (has_child(i)) {
            draw_text(ctx, is_expanded(i) ? L"v" : L">", style, item_color,
                      (float)r.x + 8.0f + indent, (float)r.y, 14.0f, (float)r.h);
        }
        float text_x = (float)r.x + 8.0f + indent + (has_child(i) ? 16.0f : 0.0f);
        draw_text(ctx, i < (int)display_items.size() ? display_items[i] : items[i], style, item_color,
                  text_x, (float)r.y, (float)(r.x + r.w) - text_x - 8.0f, (float)r.h,
                  orientation == 1 ? DWRITE_TEXT_ALIGNMENT_LEADING : DWRITE_TEXT_ALIGNMENT_CENTER);
        if (active && !disabled) {
            if (orientation == 1) {
                ctx.rt->DrawLine(D2D1::Point2F((float)r.x + 2.0f, (float)r.y + 8.0f),
                                 D2D1::Point2F((float)r.x + 2.0f, (float)(r.y + r.h) - 8.0f),
                                 ctx.get_brush(t->accent), 3.0f);
            } else {
                ctx.rt->DrawLine(D2D1::Point2F((float)r.x + 12.0f, (float)(r.y + r.h) - 2.0f),
                                 D2D1::Point2F((float)(r.x + r.w) - 12.0f, (float)(r.y + r.h) - 2.0f),
                                 ctx.get_brush(t->accent), 2.0f);
            }
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Menu::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (idx >= 0 && is_disabled(idx)) idx = -1;
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Menu::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Menu::on_mouse_down(int x, int y, MouseButton) {
    m_press_index = item_at(x, y);
    if (is_disabled(m_press_index)) m_press_index = -1;
    pressed = true;
    invalidate();
}

void Menu::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (idx >= 0 && idx == m_press_index && !is_disabled(idx)) {
        if (has_child(idx)) toggle_expanded(idx);
        set_active_index(idx);
    }
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Menu::on_key_down(int vk, int) {
    if (vk == VK_LEFT || vk == VK_UP) {
        int next = next_visible_enabled(active_index, -1);
        if (next >= 0) set_active_index(next);
    } else if (vk == VK_RIGHT || vk == VK_DOWN) {
        int next = next_visible_enabled(active_index, 1);
        if (next >= 0) set_active_index(next);
    } else if (vk == VK_HOME) {
        int next = next_visible_enabled(-1, 1);
        if (next >= 0) set_active_index(next);
    } else if (vk == VK_END) {
        int next = next_visible_enabled((int)items.size(), -1);
        if (next >= 0) set_active_index(next);
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        if (active_index >= 0 && has_child(active_index)) {
            toggle_expanded(active_index);
            invalidate();
        }
    }
}
