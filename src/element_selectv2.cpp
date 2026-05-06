#include "element_selectv2.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <cwctype>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color sv2_with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static int sv2_round_px(float v) {
    return (int)std::lround(v);
}

static std::wstring sv2_lower_copy(const std::wstring& value) {
    std::wstring out = value;
    std::transform(out.begin(), out.end(), out.begin(), [](wchar_t ch) {
        return (wchar_t)std::towlower(ch);
    });
    return out;
}

static void sv2_draw_text(RenderContext& ctx, const std::wstring& text,
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

static DWRITE_TEXT_ALIGNMENT sv2_text_alignment_from_int(int alignment) {
    if (alignment == 1) return DWRITE_TEXT_ALIGNMENT_CENTER;
    if (alignment == 2) return DWRITE_TEXT_ALIGNMENT_TRAILING;
    return DWRITE_TEXT_ALIGNMENT_LEADING;
}

int SelectV2::option_height() const {
    int h = sv2_round_px(style.font_size * 1.8f);
    return h < 26 ? 26 : h;
}

std::vector<int> SelectV2::visible_indices() const {
    std::vector<int> visible;
    std::wstring query = sv2_lower_copy(search_text);
    for (int i = 0; i < (int)options.size(); ++i) {
        if (query.empty() || sv2_lower_copy(options[i]).find(query) != std::wstring::npos) {
            visible.push_back(i);
        }
    }
    return visible;
}

int SelectV2::menu_height() const {
    int count = (std::min)(visible_count, (int)visible_indices().size());
    return option_height() * (count > 0 ? count : 1);
}

int SelectV2::menu_y() const {
    int mh = menu_height();
    if (mh <= 0) return bounds.h + 4;
    if (parent && bounds.y + bounds.h + mh + 6 > parent->bounds.h && bounds.y > mh + 6) {
        return -mh - 4;
    }
    return bounds.h + 4;
}

void SelectV2::set_options(const std::vector<std::wstring>& values) {
    options = values;
    disabled_indices.clear();
    search_text.clear();
    if (options.empty()) selected_index = -1;
    else if (selected_index < 0 || selected_index >= (int)options.size()) selected_index = 0;
    ensure_selected_visible();
    invalidate();
}

void SelectV2::set_selected_index(int index) {
    if (options.empty()) selected_index = -1;
    else {
        if (index < 0) index = 0;
        if (index >= (int)options.size()) index = (int)options.size() - 1;
        selected_index = index;
        if (is_option_disabled(selected_index)) select_relative(1);
    }
    ensure_selected_visible();
    invalidate();
    notify_changed();
}

void SelectV2::set_visible_count(int count) {
    if (count < 3) count = 3;
    if (count > 12) count = 12;
    visible_count = count;
    ensure_selected_visible();
    invalidate();
}

void SelectV2::set_open(bool is_open) {
    open = is_open;
    if (!open) {
        m_hover_index = -1;
        search_text.clear();
    }
    ensure_selected_visible();
    invalidate();
}

void SelectV2::set_search_text(const std::wstring& value) {
    search_text = value;
    open = true;
    m_scroll_index = 0;
    std::vector<int> visible = visible_indices();
    m_hover_index = visible.empty() ? -1 : visible.front();
    invalidate();
}

void SelectV2::set_option_disabled(int index, bool disabled) {
    if (index < 0 || index >= (int)options.size()) return;
    if (disabled) disabled_indices.insert(index);
    else disabled_indices.erase(index);
    if (selected_index == index && disabled) select_relative(1);
    invalidate();
}

void SelectV2::set_option_alignment(int alignment) {
    if (alignment < 0) alignment = 0;
    if (alignment > 2) alignment = 2;
    if (option_alignment == alignment) return;
    option_alignment = alignment;
    invalidate();
}

void SelectV2::set_value_alignment(int alignment) {
    if (alignment < 0) alignment = 0;
    if (alignment > 2) alignment = 2;
    if (value_alignment == alignment) return;
    value_alignment = alignment;
    invalidate();
}

void SelectV2::set_scroll_index(int index) {
    std::vector<int> visible = visible_indices();
    int max_scroll = (std::max)(0, (int)visible.size() - visible_count);
    if (index < 0) index = 0;
    if (index > max_scroll) index = max_scroll;
    if (m_scroll_index == index) return;
    m_scroll_index = index;
    invalidate();
}

void SelectV2::scroll_by(int delta_rows) {
    set_scroll_index(m_scroll_index + delta_rows);
}

int SelectV2::option_count() const {
    return (int)options.size();
}

int SelectV2::matched_count() const {
    return (int)visible_indices().size();
}

bool SelectV2::is_option_disabled(int index) const {
    return disabled_indices.find(index) != disabled_indices.end();
}

void SelectV2::ensure_selected_visible() {
    std::vector<int> visible = visible_indices();
    if (selected_index < 0 || visible.empty()) {
        m_scroll_index = 0;
        return;
    }
    int pos = 0;
    for (int i = 0; i < (int)visible.size(); ++i) {
        if (visible[i] == selected_index) {
            pos = i;
            break;
        }
    }
    int max_scroll = (std::max)(0, (int)visible.size() - visible_count);
    if (m_scroll_index > max_scroll) m_scroll_index = max_scroll;
    if (pos < m_scroll_index) m_scroll_index = pos;
    if (pos >= m_scroll_index + visible_count) m_scroll_index = pos - visible_count + 1;
    if (m_scroll_index < 0) m_scroll_index = 0;
}

void SelectV2::select_relative(int delta) {
    std::vector<int> visible = visible_indices();
    if (visible.empty()) return;
    int pos = 0;
    for (int i = 0; i < (int)visible.size(); ++i) {
        if (visible[i] == selected_index) {
            pos = i;
            break;
        }
    }
    int step = delta >= 0 ? 1 : -1;
    int next_pos = pos;
    for (int n = 0; n < (int)visible.size(); ++n) {
        next_pos += step;
        if (next_pos < 0) next_pos = (int)visible.size() - 1;
        if (next_pos >= (int)visible.size()) next_pos = 0;
        int idx = visible[next_pos];
        if (!is_option_disabled(idx)) {
            selected_index = idx;
            ensure_selected_visible();
            invalidate();
            notify_changed();
            return;
        }
    }
}

void SelectV2::select_first_or_last(bool last) {
    std::vector<int> visible = visible_indices();
    if (visible.empty()) return;
    if (last) {
        for (auto it = visible.rbegin(); it != visible.rend(); ++it) {
            if (!is_option_disabled(*it)) {
                selected_index = *it;
                ensure_selected_visible();
                invalidate();
                notify_changed();
                return;
            }
        }
    } else {
        for (int idx : visible) {
            if (!is_option_disabled(idx)) {
                selected_index = idx;
                ensure_selected_visible();
                invalidate();
                notify_changed();
                return;
            }
        }
    }
}

void SelectV2::notify_changed() {
    if (change_cb) change_cb(id, selected_index, matched_count(), open ? 1 : 0);
}

std::wstring SelectV2::selected_text() const {
    if (selected_index >= 0 && selected_index < (int)options.size()) return options[selected_index];
    return L"\u8bf7\u9009\u62e9";
}

int SelectV2::option_at(int x, int y) const {
    if (!open) return -1;
    int my = menu_y();
    int mh = menu_height();
    if (x < 0 || x >= bounds.w || y < my || y >= my + mh) return -1;
    std::vector<int> visible = visible_indices();
    if (visible.empty()) return -1;
    int pos = m_scroll_index + (y - my) / option_height();
    return (pos >= 0 && pos < (int)visible.size()) ? visible[pos] : -1;
}

SelectV2::Part SelectV2::part_at(int x, int y, int* option_index) const {
    int idx = option_at(x, y);
    if (option_index) *option_index = idx;
    if (idx >= 0) return PartOption;
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

Element* SelectV2::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* SelectV2::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return option_at(lx, ly) >= 0 ? this : nullptr;
}

void SelectV2::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = open || has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    Color fg = enabled ? (style.fg_color ? style.fg_color : t->text_primary) : t->text_secondary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F field = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(field, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        ROUNDED(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    float label_w = text.empty() ? 0.0f : (std::min)((float)bounds.w * 0.32f, 90.0f);
    if (!text.empty()) {
        sv2_draw_text(ctx, text, style, t->text_secondary, (float)style.pad_left, 0.0f, label_w, (float)bounds.h);
    }
    float value_x = (float)style.pad_left + label_w + (label_w > 0.0f ? 6.0f : 0.0f);
    float arrow_w = 24.0f;
    std::wstring value_text = !search_text.empty() && open ? search_text : selected_text();
    sv2_draw_text(ctx, value_text, style, fg, value_x, 0.0f,
                  (float)bounds.w - value_x - style.pad_right - arrow_w, (float)bounds.h,
                  sv2_text_alignment_from_int(value_alignment));
    sv2_draw_text(ctx, open ? L"\u25b2" : L"\u25bc", style, t->text_secondary,
                  (float)bounds.w - style.pad_right - arrow_w, 0.0f,
                  arrow_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_CENTER);

    ctx.rt->SetTransform(saved);
}

void SelectV2::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color menu_bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF242637 : 0xFFFFFFFF;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    int my = menu_y();
    int item_h = option_height();
    int mh = menu_height();
    std::vector<int> visible = visible_indices();
    int last = (std::min)((int)visible.size(), m_scroll_index + visible_count);

    D2D1_RECT_F menu = { 0, (float)my, (float)bounds.w, (float)(my + mh) };
    ctx.rt->FillRoundedRectangle(ROUNDED(menu, radius, radius), ctx.get_brush(menu_bg));
    ctx.rt->DrawRoundedRectangle(
        ROUNDED(D2D1::RectF(menu.left + 0.5f, menu.top + 0.5f,
                            menu.right - 0.5f, menu.bottom - 0.5f), radius, radius),
        ctx.get_brush(t->border_default), 1.0f);

    if (visible.empty()) {
        sv2_draw_text(ctx, L"\u6682\u65e0\u5339\u914d\u9009\u9879", style, t->text_secondary,
                      (float)style.pad_left, (float)my,
                      (float)bounds.w - style.pad_left - style.pad_right - 10.0f, (float)item_h);
    }
    for (int pos = m_scroll_index; pos < last; ++pos) {
        int i = visible[pos];
        float y = (float)(my + (pos - m_scroll_index) * item_h);
        if (i == m_hover_index || i == selected_index) {
            Color row_bg = i == selected_index ? sv2_with_alpha(t->accent, 0x33) : t->button_hover;
            D2D1_RECT_F row = { 2.0f, y + 1.0f, (float)bounds.w - 2.0f, y + (float)item_h - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(row_bg));
        }
        Color item_color = is_option_disabled(i) ? t->text_secondary : (i == selected_index ? t->accent : fg);
        sv2_draw_text(ctx, options[i], style, item_color,
                      (float)style.pad_left, y,
                      (float)bounds.w - style.pad_left - style.pad_right - 10.0f, (float)item_h,
                      sv2_text_alignment_from_int(option_alignment));
    }

    if ((int)visible.size() > visible_count) {
        float track_h = (float)mh - 8.0f;
        float thumb_h = (std::max)(24.0f, track_h * ((float)visible_count / (float)visible.size()));
        int max_scroll = (std::max)(1, (int)visible.size() - visible_count);
        float top = (float)my + 4.0f + (track_h - thumb_h) * ((float)m_scroll_index / (float)max_scroll);
        D2D1_RECT_F thumb = { (float)bounds.w - 7.0f, top, (float)bounds.w - 3.0f, top + thumb_h };
        ctx.rt->FillRoundedRectangle(ROUNDED(thumb, 2.0f, 2.0f), ctx.get_brush(t->border_default));
    }

    ctx.rt->SetTransform(saved);
}

void SelectV2::on_mouse_move(int x, int y) {
    int idx = option_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void SelectV2::on_mouse_leave() {
    m_hover_index = -1;
    hovered = false;
    invalidate();
}

void SelectV2::on_mouse_wheel(int, int, int delta) {
    if (!open) return;
    scroll_by(delta < 0 ? 3 : -3);
}

void SelectV2::on_mouse_down(int x, int y, MouseButton) {
    int idx = -1;
    m_press_part = part_at(x, y, &idx);
    m_press_index = idx;
    pressed = true;
    invalidate();
}

void SelectV2::on_mouse_up(int x, int y, MouseButton) {
    int idx = -1;
    Part part = part_at(x, y, &idx);
    if (part == PartOption && m_press_part == PartOption && idx == m_press_index && idx >= 0 && !is_option_disabled(idx)) {
        set_selected_index(idx);
        set_open(false);
    } else if (part == PartMain && m_press_part == PartMain) {
        set_open(!open);
    }
    m_press_part = PartNone;
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void SelectV2::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) set_open(!open);
    else if (vk == VK_ESCAPE) set_open(false);
    else if (vk == VK_DOWN) { if (!open) open = true; select_relative(1); }
    else if (vk == VK_UP) { if (!open) open = true; select_relative(-1); }
    else if (vk == VK_NEXT) { if (!open) open = true; for (int i = 0; i < visible_count; ++i) select_relative(1); }
    else if (vk == VK_PRIOR) { if (!open) open = true; for (int i = 0; i < visible_count; ++i) select_relative(-1); }
    else if (vk == VK_HOME) { if (!open) open = true; select_first_or_last(false); }
    else if (vk == VK_END) { if (!open) open = true; select_first_or_last(true); }
    else if (vk == VK_BACK && !search_text.empty()) { search_text.pop_back(); m_scroll_index = 0; }
    invalidate();
}

void SelectV2::on_char(wchar_t ch) {
    if (!open || ch < 32) return;
    search_text.push_back(ch);
    m_scroll_index = 0;
    std::vector<int> visible = visible_indices();
    if (!visible.empty()) m_hover_index = visible.front();
    invalidate();
}

void SelectV2::on_blur() {
    has_focus = false;
    open = false;
    search_text.clear();
    m_hover_index = -1;
    m_press_part = PartNone;
    invalidate();
}
