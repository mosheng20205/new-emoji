#include "element_menu.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cmath>
#include <shellapi.h>
#include <string>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static D2D1_RECT_F to_d2d_rect(const Rect& r) {
    return D2D1::RectF((float)r.x, (float)r.y, (float)(r.x + r.w), (float)(r.y + r.h));
}

static std::wstring trim_marker_space(const std::wstring& value) {
    size_t start = 0;
    while (start < value.size() && (value[start] == L' ' || value[start] == L'\t')) ++start;
    size_t end = value.size();
    while (end > start && (value[end - 1] == L' ' || value[end - 1] == L'\t')) --end;
    return value.substr(start, end - start);
}

static std::wstring collapsed_glyph(const std::wstring& icon, const std::wstring& text) {
    if (!icon.empty()) return icon;
    if (text.empty()) return L"•";
    if (text.size() >= 2 && text[0] >= 0xD800 && text[0] <= 0xDBFF) return text.substr(0, 2);
    return text.substr(0, 1);
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

void Menu::resize_meta() {
    item_icons.resize(items.size());
    item_hrefs.resize(items.size());
    item_targets.resize(items.size());
    item_commands.resize(items.size());
    group_items.resize(items.size(), false);
}

void Menu::set_items(const std::vector<std::wstring>& values) {
    items = values;
    display_items.clear();
    item_levels.clear();
    disabled_items.clear();
    expanded_items.clear();
    item_icons.clear();
    item_hrefs.clear();
    item_targets.clear();
    item_commands.clear();
    group_items.clear();
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
    resize_meta();
    clamp_scroll();
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
    ensure_item_visible(active_index);
    invalidate();
}

void Menu::set_orientation(int value) {
    orientation = value == 1 ? 1 : 0;
    clamp_scroll();
    invalidate();
}

void Menu::set_colors(Color bg, Color text_color, Color active_text_color,
                      Color hover_bg, Color disabled_text_color, Color border) {
    menu_bg_color = bg;
    menu_text_color = text_color;
    menu_active_text_color = active_text_color;
    menu_hover_bg_color = hover_bg;
    menu_disabled_text_color = disabled_text_color;
    menu_border_color = border;
    invalidate();
}

void Menu::set_collapsed(bool value) {
    collapsed = value;
    if (active_index >= 0 && !is_visible_item(active_index)) set_active_index(active_index);
    clamp_scroll();
    invalidate();
}

void Menu::set_item_meta(const std::vector<std::wstring>& icons,
                         const std::vector<int>& group_indices,
                         const std::vector<std::wstring>& hrefs,
                         const std::vector<std::wstring>& targets,
                         const std::vector<std::wstring>& commands) {
    item_icons.assign(items.size(), L"");
    item_hrefs.assign(items.size(), L"");
    item_targets.assign(items.size(), L"");
    item_commands.assign(items.size(), L"");
    group_items.assign(items.size(), false);

    for (size_t i = 0; i < item_icons.size() && i < icons.size(); ++i) item_icons[i] = icons[i];
    for (size_t i = 0; i < item_hrefs.size() && i < hrefs.size(); ++i) item_hrefs[i] = hrefs[i];
    for (size_t i = 0; i < item_targets.size() && i < targets.size(); ++i) item_targets[i] = targets[i];
    for (size_t i = 0; i < item_commands.size() && i < commands.size(); ++i) item_commands[i] = commands[i];
    for (int index : group_indices) {
        if (index >= 0 && index < (int)group_items.size()) group_items[(size_t)index] = true;
    }
    if (active_index >= 0 && is_disabled(active_index)) set_active_index(active_index);
    clamp_scroll();
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
    clamp_scroll();
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
            if (!is_group(i)) parts.push_back(i < (int)display_items.size() ? display_items[i] : items[i]);
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

const std::wstring& Menu::item_icon(int index) const {
    static const std::wstring empty;
    if (index < 0 || index >= (int)item_icons.size()) return empty;
    return item_icons[(size_t)index];
}

const std::wstring& Menu::item_href(int index) const {
    static const std::wstring empty;
    if (index < 0 || index >= (int)item_hrefs.size()) return empty;
    return item_hrefs[(size_t)index];
}

const std::wstring& Menu::item_target(int index) const {
    static const std::wstring empty;
    if (index < 0 || index >= (int)item_targets.size()) return empty;
    return item_targets[(size_t)index];
}

const std::wstring& Menu::item_command(int index) const {
    static const std::wstring empty;
    if (index < 0 || index >= (int)item_commands.size()) return empty;
    return item_commands[(size_t)index];
}

bool Menu::is_group(int index) const {
    return index >= 0 && index < (int)group_items.size() && group_items[(size_t)index];
}

bool Menu::is_disabled(int index) const {
    return index < 0 || index >= (int)disabled_items.size() ||
           disabled_items[(size_t)index] || is_group(index);
}

bool Menu::has_child(int index) const {
    return index >= 0 && index + 1 < (int)item_levels.size() &&
           item_levels[index + 1] > item_levels[index];
}

bool Menu::is_expanded(int index) const {
    return index >= 0 && index < (int)expanded_items.size() && expanded_items[(size_t)index];
}

bool Menu::is_visible_item(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    if (collapsed && orientation == 1) {
        return item_levels[index] == 0 && !is_group(index);
    }
    int level = item_levels[index];
    for (int i = index - 1; i >= 0 && level > 0; --i) {
        if (item_levels[i] < level) {
            if (!is_group(i) && !is_expanded(i)) return false;
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
    expanded_items[(size_t)index] = !expanded_items[(size_t)index];
    if (active_index >= 0 && !is_visible_item(active_index)) active_index = index;
    clamp_scroll();
    ensure_item_visible(active_index);
}

void Menu::fire_select(int index) {
    if (!select_cb || index < 0 || index >= (int)items.size()) return;
    std::string path_utf8 = wide_to_utf8(active_path());
    std::wstring command = item_command(index);
    if (command.empty()) command = index < (int)display_items.size() ? display_items[index] : items[index];
    std::string command_utf8 = wide_to_utf8(command);
    select_cb(id, index,
              reinterpret_cast<const unsigned char*>(path_utf8.data()), (int)path_utf8.size(),
              reinterpret_cast<const unsigned char*>(command_utf8.data()), (int)command_utf8.size());
}

void Menu::open_href_if_needed(int index) {
    const std::wstring& href = item_href(index);
    if (!href.empty()) ShellExecuteW(nullptr, L"open", href.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
}

void Menu::choose_item(int index) {
    if (is_disabled(index)) return;
    if (has_child(index)) toggle_expanded(index);
    set_active_index(index);
    fire_select(index);
    open_href_if_needed(index);
}

int Menu::content_height() const {
    if (orientation != 1) return bounds.h;
    int h = style.pad_top + style.pad_bottom;
    for (int item_index : visible_indices()) {
        h += item_height(item_index);
    }
    return h;
}

int Menu::viewport_height() const {
    return (std::max)(0, bounds.h);
}

int Menu::max_scroll() const {
    if (orientation != 1) return 0;
    return (std::max)(0, content_height() - viewport_height());
}

void Menu::clamp_scroll() {
    int max_value = max_scroll();
    if (m_scroll_y < 0) m_scroll_y = 0;
    if (m_scroll_y > max_value) m_scroll_y = max_value;
}

void Menu::update_scroll(int value) {
    int old = m_scroll_y;
    m_scroll_y = value;
    clamp_scroll();
    if (m_scroll_y != old) invalidate();
}

void Menu::ensure_item_visible(int index) {
    if (orientation != 1 || index < 0 || index >= (int)items.size()) return;
    if (!is_visible_item(index)) return;
    int y = style.pad_top;
    for (int item_index : visible_indices()) {
        if (item_index == index) break;
        y += item_height(item_index);
    }
    int h = item_height(index);
    int view_top = m_scroll_y + style.pad_top;
    int view_bottom = m_scroll_y + bounds.h - style.pad_bottom;
    if (y < view_top) {
        update_scroll(y - style.pad_top);
    } else if (y + h > view_bottom) {
        update_scroll(y + h - bounds.h + style.pad_bottom);
    }
}

bool Menu::has_vertical_scrollbar() const {
    return orientation == 1 && max_scroll() > 0;
}

Rect Menu::scrollbar_track_rect() const {
    int track_w = (std::max)(6, round_px(7.0f * style.font_size / 14.0f));
    int pad = (std::max)(4, round_px(4.0f * style.font_size / 14.0f));
    return { bounds.w - style.pad_right - track_w - 2, style.pad_top + pad,
             track_w, (std::max)(0, bounds.h - style.pad_top - style.pad_bottom - pad * 2) };
}

Rect Menu::scrollbar_thumb_rect() const {
    Rect track = scrollbar_track_rect();
    int max_value = max_scroll();
    if (track.h <= 0 || max_value <= 0) return { track.x, track.y, track.w, track.h };
    int ch = content_height();
    int thumb_h = (std::max)(28, (int)std::lround((double)track.h * (double)viewport_height() / (double)(std::max)(1, ch)));
    if (thumb_h > track.h) thumb_h = track.h;
    int travel = (std::max)(1, track.h - thumb_h);
    int thumb_y = track.y + (int)std::lround((double)m_scroll_y * (double)travel / (double)max_value);
    return { track.x, thumb_y, track.w, thumb_h };
}

void Menu::update_scroll_from_thumb(int y) {
    Rect track = scrollbar_track_rect();
    Rect thumb = scrollbar_thumb_rect();
    int max_value = max_scroll();
    int travel = track.h - thumb.h;
    if (max_value <= 0 || travel <= 0) {
        update_scroll(0);
        return;
    }
    int thumb_y = y - m_drag_offset;
    if (thumb_y < track.y) thumb_y = track.y;
    if (thumb_y > track.y + travel) thumb_y = track.y + travel;
    int next = (int)std::lround((double)(thumb_y - track.y) * (double)max_value / (double)travel);
    update_scroll(next);
}

int Menu::item_height(int index) const {
    if (orientation == 0) {
        int h = bounds.h - style.pad_top - style.pad_bottom;
        return h < 28 ? 28 : h;
    }
    float scale = style.font_size > 0.0f ? style.font_size / 14.0f : 1.0f;
    if (collapsed) return (std::max)(38, round_px(44.0f * scale));
    if (is_group(index)) return (std::max)(24, round_px(28.0f * scale));
    return (std::max)(34, round_px(38.0f * scale));
}

int Menu::collapsed_width() const {
    float scale = style.font_size > 0.0f ? style.font_size / 14.0f : 1.0f;
    return (std::max)(48, round_px(58.0f * scale));
}

Rect Menu::item_rect(int index) const {
    if (items.empty()) return {};
    int pos = visible_position(index);
    if (pos < 0) return {};
    std::vector<int> visible = visible_indices();
    if (orientation == 1) {
        int y = style.pad_top;
        for (int item_index : visible) {
            if (item_index == index) break;
            y += item_height(item_index);
        }
        y -= m_scroll_y;
        int width = collapsed ? (std::min)(bounds.w - style.pad_left - style.pad_right, collapsed_width())
                              : bounds.w - style.pad_left - style.pad_right;
        if (has_vertical_scrollbar()) {
            Rect tr = scrollbar_track_rect();
            width = (std::max)(0, tr.x - style.pad_left - 4);
        }
        return { style.pad_left, y, width, item_height(index) };
    }
    int gap = round_px(6.0f * style.font_size / 14.0f);
    int x = style.pad_left;
    for (int item_index : visible) {
        if (item_index == index) break;
        x += item_rect(item_index).w + gap;
    }
    int level = index < (int)item_levels.size() ? item_levels[index] : 0;
    int label_len = index < (int)display_items.size() ? (int)display_items[index].size() : (int)items[index].size();
    int icon_w = item_icon(index).empty() ? 0 : round_px(24.0f * style.font_size / 14.0f);
    int child_w = has_child(index) ? 16 : 0;
    int w = is_group(index)
        ? round_px((float)label_len * style.font_size * 0.70f + 28.0f)
        : round_px((float)label_len * style.font_size * 0.76f + 34.0f + icon_w + child_w + level * 14.0f);
    int h = item_height(index);
    return { x, style.pad_top, w, h };
}

int Menu::item_at(int x, int y) const {
    if (has_vertical_scrollbar() && scrollbar_track_rect().contains(x, y)) return -1;
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
    Color fg = menu_text_color ? menu_text_color : (style.fg_color ? style.fg_color : t->text_secondary);
    Color active_fg = menu_active_text_color ? menu_active_text_color : t->accent;
    Color disabled_fg = menu_disabled_text_color ? menu_disabled_text_color : t->text_muted;
    Color hover_bg = menu_hover_bg_color ? menu_hover_bg_color : t->button_hover;
    Color bg = menu_bg_color ? menu_bg_color : (style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF));
    Color border = menu_border_color ? menu_border_color : (style.border_color ? style.border_color : t->border_default);
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
        if (r.x >= bounds.w) break;
        if (r.y + r.h < 0) continue;
        if (r.y >= bounds.h) break;
        bool active = i == active_index;
        bool hot = i == m_hover_index;
        bool disabled = is_disabled(i);
        bool group = is_group(i);
        int level = i < (int)item_levels.size() ? item_levels[i] : 0;

        if (group) {
            if (collapsed && orientation == 1) continue;
            ElementStyle group_style = style;
            group_style.font_size = style.font_size * 0.82f;
            draw_text(ctx, i < (int)display_items.size() ? display_items[i] : items[i], group_style,
                      disabled_fg, (float)r.x + 8.0f + (float)level * 16.0f, (float)r.y,
                      (float)r.w - 16.0f, (float)r.h, DWRITE_TEXT_ALIGNMENT_LEADING);
            continue;
        }

        if (!disabled && (active || hot)) {
            D2D1_RECT_F rr = { (float)r.x + 3.0f, (float)r.y + 3.0f,
                               (float)(r.x + r.w) - 3.0f, (float)(r.y + r.h) - 3.0f };
            Color fill = active ? with_alpha(active_fg, dark ? 0x2E : 0x20) : hover_bg;
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(fill));
        }

        Color item_color = disabled ? disabled_fg : (active ? active_fg : fg);
        float indent = orientation == 1 ? (float)(level * 18) : (float)(level * 10);
        if (collapsed && orientation == 1) {
            std::wstring glyph = collapsed_glyph(item_icon(i), i < (int)display_items.size() ? display_items[i] : items[i]);
            draw_text(ctx, glyph, style, item_color, (float)r.x, (float)r.y, (float)r.w, (float)r.h);
        } else {
            float x = (float)r.x + 8.0f + indent;
            if (has_child(i)) {
                draw_text(ctx, is_expanded(i) ? L"v" : L">", style, item_color,
                          x, (float)r.y, 14.0f, (float)r.h);
                x += 16.0f;
            }
            const std::wstring& icon = item_icon(i);
            if (!icon.empty()) {
                draw_text(ctx, icon, style, item_color, x, (float)r.y, 22.0f, (float)r.h);
                x += 24.0f;
            }
            draw_text(ctx, i < (int)display_items.size() ? display_items[i] : items[i], style, item_color,
                      x, (float)r.y, (float)(r.x + r.w) - x - 8.0f, (float)r.h,
                      orientation == 1 ? DWRITE_TEXT_ALIGNMENT_LEADING : DWRITE_TEXT_ALIGNMENT_CENTER);
        }

        if (active && !disabled) {
            if (orientation == 1) {
                ctx.rt->DrawLine(D2D1::Point2F((float)r.x + 2.0f, (float)r.y + 8.0f),
                                 D2D1::Point2F((float)r.x + 2.0f, (float)(r.y + r.h) - 8.0f),
                                 ctx.get_brush(active_fg), 3.0f);
            } else {
                ctx.rt->DrawLine(D2D1::Point2F((float)r.x + 12.0f, (float)(r.y + r.h) - 2.0f),
                                 D2D1::Point2F((float)(r.x + r.w) - 12.0f, (float)(r.y + r.h) - 2.0f),
                                 ctx.get_brush(active_fg), 2.0f);
            }
        }
    }

    if (has_vertical_scrollbar()) {
        Rect tr = scrollbar_track_rect();
        Rect th = scrollbar_thumb_rect();
        float radius = (float)tr.w * 0.5f;
        ctx.rt->FillRoundedRectangle(ROUNDED(to_d2d_rect(tr), radius, radius),
                                     ctx.get_brush(dark ? with_alpha(0xFFFFFFFF, 0x14) : with_alpha(0xFF000000, 0x10)));
        ctx.rt->FillRoundedRectangle(ROUNDED(to_d2d_rect(th), radius, radius),
                                     ctx.get_brush(m_dragging_scrollbar ? active_fg : with_alpha(fg, dark ? 0x9A : 0x78)));
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Menu::on_mouse_move(int x, int y) {
    if (pressed && m_dragging_scrollbar) {
        update_scroll_from_thumb(y);
        return;
    }
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
    m_dragging_scrollbar = false;
    invalidate();
}

void Menu::on_mouse_down(int x, int y, MouseButton) {
    if (has_vertical_scrollbar()) {
        Rect thumb = scrollbar_thumb_rect();
        Rect track = scrollbar_track_rect();
        if (thumb.contains(x, y)) {
            m_dragging_scrollbar = true;
            m_drag_offset = y - thumb.y;
            m_press_index = -1;
            pressed = true;
            invalidate();
            return;
        }
        if (track.contains(x, y)) {
            m_dragging_scrollbar = true;
            m_drag_offset = thumb.h / 2;
            m_press_index = -1;
            pressed = true;
            update_scroll_from_thumb(y);
            invalidate();
            return;
        }
    }
    m_press_index = item_at(x, y);
    if (is_disabled(m_press_index)) m_press_index = -1;
    pressed = true;
    invalidate();
}

void Menu::on_mouse_up(int x, int y, MouseButton) {
    if (!m_dragging_scrollbar) {
        int idx = item_at(x, y);
        if (idx >= 0 && idx == m_press_index && !is_disabled(idx)) {
            choose_item(idx);
        }
    }
    m_press_index = -1;
    m_dragging_scrollbar = false;
    m_drag_offset = 0;
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
    } else if (vk == VK_PRIOR) {
        update_scroll(m_scroll_y - (std::max)(item_height(active_index), bounds.h - item_height(active_index)));
    } else if (vk == VK_NEXT) {
        update_scroll(m_scroll_y + (std::max)(item_height(active_index), bounds.h - item_height(active_index)));
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        if (active_index >= 0) choose_item(active_index);
    }
}

void Menu::on_mouse_wheel(int, int, int delta) {
    if (orientation != 1 || delta == 0 || max_scroll() <= 0) return;
    int steps = delta / WHEEL_DELTA;
    if (steps == 0) steps = delta > 0 ? 1 : -1;
    int step = (std::max)(24, item_height(active_index >= 0 ? active_index : 0));
    update_scroll(m_scroll_y - steps * step * 2);
}
