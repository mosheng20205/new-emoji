#include "element_select.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <cwctype>

static int select_round_px(float v) {
    return (int)std::lround(v);
}

static Color select_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static std::wstring select_lower_copy(const std::wstring& value) {
    std::wstring out = value;
    std::transform(out.begin(), out.end(), out.begin(), [](wchar_t ch) {
        return (wchar_t)std::towlower(ch);
    });
    return out;
}

static void select_draw_text(RenderContext& ctx, const std::wstring& text,
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

static DWRITE_TEXT_ALIGNMENT select_text_alignment_from_int(int alignment) {
    if (alignment == 1) return DWRITE_TEXT_ALIGNMENT_CENTER;
    if (alignment == 2) return DWRITE_TEXT_ALIGNMENT_TRAILING;
    return DWRITE_TEXT_ALIGNMENT_LEADING;
}

int Select::option_height() const {
    int h = select_round_px(style.font_size * 1.8f);
    return h < 26 ? 26 : h;
}

std::vector<int> Select::visible_indices() const {
    std::vector<int> visible;
    std::wstring query = select_lower_copy(search_text);
    for (int i = 0; i < (int)options.size(); ++i) {
        if (query.empty() || select_lower_copy(options[i]).find(query) != std::wstring::npos) {
            visible.push_back(i);
        }
    }
    return visible;
}

int Select::menu_height() const {
    int count = (int)visible_indices().size();
    return option_height() * (count > 0 ? count : 1);
}

int Select::menu_y() const {
    int mh = menu_height();
    if (mh <= 0) return bounds.h + 4;
    if (parent && bounds.y + bounds.h + mh + 6 > parent->bounds.h && bounds.y > mh + 6) {
        return -mh - 4;
    }
    return bounds.h + 4;
}

int Select::option_at(int x, int y) const {
    if (!open) return -1;
    int my = menu_y();
    int mh = menu_height();
    if (x < 0 || x >= bounds.w || y < my || y >= my + mh) return -1;
    std::vector<int> visible = visible_indices();
    if (visible.empty()) return -1;
    int row = (y - my) / option_height();
    if (row < 0 || row >= (int)visible.size()) return -1;
    return visible[row];
}

Select::Part Select::part_at(int x, int y, int* option_index) const {
    int idx = option_at(x, y);
    if (option_index) *option_index = idx;
    if (idx >= 0) return PartOption;
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

std::wstring Select::selected_text() const {
    if (multiple) {
        if (selected_indices.empty()) return placeholder.empty() ? L"\u8bf7\u9009\u62e9" : placeholder;
        std::wstring joined;
        int count = 0;
        for (int idx : selected_indices) {
            if (idx < 0 || idx >= (int)options.size()) continue;
            if (!joined.empty()) joined += L"\uff0c";
            joined += options[idx];
            ++count;
            if (count >= 2 && (int)selected_indices.size() > 2) {
                joined += L"\uff0c+" + std::to_wstring((int)selected_indices.size() - 2);
                break;
            }
        }
        return joined.empty() ? (placeholder.empty() ? L"\u8bf7\u9009\u62e9" : placeholder) : joined;
    }
    if (selected_index >= 0 && selected_index < (int)options.size()) return options[selected_index];
    return placeholder.empty() ? L"\u8bf7\u9009\u62e9" : placeholder;
}

bool Select::is_option_disabled(int index) const {
    return disabled_indices.find(index) != disabled_indices.end();
}

int Select::option_count() const {
    return (int)options.size();
}

int Select::matched_count() const {
    return (int)visible_indices().size();
}

int Select::selected_count() const {
    return multiple ? (int)selected_indices.size() : (selected_index >= 0 ? 1 : 0);
}

int Select::selected_at(int position) const {
    if (position < 0) return -1;
    if (!multiple) return position == 0 ? selected_index : -1;
    int i = 0;
    for (int idx : selected_indices) {
        if (i == position) return idx;
        ++i;
    }
    return -1;
}

void Select::select_relative(int delta) {
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
            if (multiple) {
                selected_indices.insert(idx);
            }
            invalidate();
            notify_changed();
            return;
        }
    }
}

void Select::select_first_or_last(bool last) {
    std::vector<int> visible = visible_indices();
    if (visible.empty()) return;
    if (last) {
        for (auto it = visible.rbegin(); it != visible.rend(); ++it) {
            if (!is_option_disabled(*it)) {
                selected_index = *it;
                if (multiple) selected_indices.insert(*it);
                invalidate();
                notify_changed();
                return;
            }
        }
    } else {
        for (int idx : visible) {
            if (!is_option_disabled(idx)) {
                selected_index = idx;
                if (multiple) selected_indices.insert(idx);
                invalidate();
                notify_changed();
                return;
            }
        }
    }
}

void Select::set_options(const std::vector<std::wstring>& values) {
    options = values;
    disabled_indices.clear();
    search_text.clear();
    if (options.empty()) selected_index = -1;
    else if (selected_index < 0 || selected_index >= (int)options.size()) selected_index = 0;
    for (auto it = selected_indices.begin(); it != selected_indices.end();) {
        if (*it < 0 || *it >= (int)options.size()) it = selected_indices.erase(it);
        else ++it;
    }
    invalidate();
}

void Select::set_selected_index(int index) {
    if (options.empty()) {
        selected_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)options.size()) index = (int)options.size() - 1;
        selected_index = index;
        if (is_option_disabled(selected_index)) select_relative(1);
        if (multiple && !is_option_disabled(selected_index)) {
            selected_indices.clear();
            selected_indices.insert(selected_index);
        }
    }
    invalidate();
    notify_changed();
}

void Select::set_open(bool is_open) {
    open = is_open;
    if (!open) {
        m_hover_index = -1;
        search_text.clear();
    }
    invalidate();
}

void Select::set_search_text(const std::wstring& value) {
    search_text = value;
    open = true;
    std::vector<int> visible = visible_indices();
    m_hover_index = visible.empty() ? -1 : visible.front();
    invalidate();
}

void Select::set_placeholder(const std::wstring& value) {
    placeholder = value.empty() ? L"\u8bf7\u9009\u62e9" : value;
    invalidate();
}

void Select::set_option_disabled(int index, bool disabled) {
    if (index < 0 || index >= (int)options.size()) return;
    if (disabled) disabled_indices.insert(index);
    else disabled_indices.erase(index);
    if (selected_index == index && disabled) select_relative(1);
    if (disabled) selected_indices.erase(index);
    invalidate();
}

void Select::set_option_alignment(int alignment) {
    if (alignment < 0) alignment = 0;
    if (alignment > 2) alignment = 2;
    if (option_alignment == alignment) return;
    option_alignment = alignment;
    invalidate();
}

void Select::set_value_alignment(int alignment) {
    if (alignment < 0) alignment = 0;
    if (alignment > 2) alignment = 2;
    if (value_alignment == alignment) return;
    value_alignment = alignment;
    invalidate();
}

void Select::set_multiple(bool enabled) {
    multiple = enabled;
    if (multiple) {
        selected_indices.clear();
        if (selected_index >= 0 && selected_index < (int)options.size() && !is_option_disabled(selected_index)) {
            selected_indices.insert(selected_index);
        }
    } else if (!selected_indices.empty()) {
        selected_index = *selected_indices.begin();
        selected_indices.clear();
    }
    invalidate();
    notify_changed();
}

void Select::set_selected_indices(const std::vector<int>& indices) {
    selected_indices.clear();
    for (int idx : indices) {
        if (idx >= 0 && idx < (int)options.size() && !is_option_disabled(idx)) {
            selected_indices.insert(idx);
        }
    }
    if (!selected_indices.empty()) selected_index = *selected_indices.begin();
    else selected_index = -1;
    multiple = true;
    invalidate();
    notify_changed();
}

void Select::toggle_index(int index) {
    if (index < 0 || index >= (int)options.size() || is_option_disabled(index)) return;
    if (!multiple) {
        set_selected_index(index);
        return;
    }
    if (selected_indices.find(index) != selected_indices.end()) selected_indices.erase(index);
    else selected_indices.insert(index);
    selected_index = selected_indices.empty() ? -1 : index;
    invalidate();
    notify_changed();
}

void Select::notify_changed() {
    if (change_cb) change_cb(id, selected_index, selected_count(), open ? 1 : 0);
}

Element* Select::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* Select::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return option_at(lx, ly) >= 0 ? this : nullptr;
}

void Select::paint(RenderContext& ctx) {
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
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(field, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    float pad_l = (float)style.pad_left;
    float pad_r = (float)style.pad_right;
    float arrow_w = 24.0f;
    float label_w = text.empty() ? 0.0f :
        (float)((std::min)(select_round_px(bounds.w * 0.34f), select_round_px(120.0f * style.font_size / 14.0f)));
    if (!text.empty()) {
        select_draw_text(ctx, text, style, t->text_secondary, pad_l, 0.0f, label_w, (float)bounds.h);
    }

    float value_x = pad_l + label_w + (label_w > 0.0f ? 6.0f : 0.0f);
    float value_w = (float)bounds.w - value_x - pad_r - arrow_w;
    if (value_w < 1.0f) value_w = 1.0f;
    std::wstring value_text = !search_text.empty() && open ? search_text : selected_text();
    select_draw_text(ctx, value_text, style, fg, value_x, 0.0f, value_w, (float)bounds.h,
                     select_text_alignment_from_int(value_alignment));
    select_draw_text(ctx, open ? L"\u25b2" : L"\u25bc", style, t->text_secondary,
                     (float)bounds.w - pad_r - arrow_w, 0.0f, arrow_w, (float)bounds.h,
                     DWRITE_TEXT_ALIGNMENT_CENTER);

    ctx.rt->SetTransform(saved);
}

void Select::paint_dropdown(RenderContext& ctx) {
    if (!open) return;

    const Theme* t = theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    float pad_l = (float)style.pad_left;
    float pad_r = (float)style.pad_right;

    int my = menu_y();
    int item_h = option_height();
    int mh = menu_height();
    std::vector<int> visible = visible_indices();
    D2D1_RECT_F menu = { 0, (float)my, (float)bounds.w, (float)(my + mh) };
    Color menu_bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF242637 : 0xFFFFFFFF;
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(menu, radius, radius), ctx.get_brush(menu_bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(menu.left + 0.5f, menu.top + 0.5f,
                                      menu.right - 0.5f, menu.bottom - 0.5f), radius, radius),
        ctx.get_brush(t->border_default), 1.0f);

    if (visible.empty()) {
        select_draw_text(ctx, L"\u6682\u65e0\u5339\u914d\u9009\u9879", style, t->text_secondary,
                         pad_l, (float)my, (float)bounds.w - pad_l - pad_r, (float)item_h);
    }

    for (int row = 0; row < (int)visible.size(); ++row) {
        int i = visible[row];
        float y = (float)(my + row * item_h);
        if (i == m_hover_index || i == selected_index) {
            Color row_bg = i == selected_index ? select_alpha(t->accent, 0x33) : t->button_hover;
            D2D1_RECT_F row_rect = { 2.0f, y + 1.0f, (float)bounds.w - 2.0f, y + (float)item_h - 1.0f };
            ctx.rt->FillRectangle(row_rect, ctx.get_brush(row_bg));
        }
        bool chosen = multiple ? (selected_indices.find(i) != selected_indices.end()) : (i == selected_index);
        Color item_color = is_option_disabled(i) ? t->text_secondary : (chosen ? t->accent : fg);
        if (multiple) {
            select_draw_text(ctx, chosen ? L"\u2713" : L"", style, item_color,
                             pad_l, y, 20.0f, (float)item_h, DWRITE_TEXT_ALIGNMENT_CENTER);
        }
        select_draw_text(ctx, options[i], style, item_color,
                         pad_l + (multiple ? 24.0f : 0.0f), y,
                         (float)bounds.w - pad_l - pad_r - (multiple ? 24.0f : 0.0f), (float)item_h,
                         select_text_alignment_from_int(option_alignment));
    }
}

void Select::paint_overlay(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    paint_dropdown(ctx);
    ctx.rt->SetTransform(saved);
}

void Select::on_mouse_move(int x, int y) {
    int idx = option_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Select::on_mouse_leave() {
    m_hover_index = -1;
    hovered = false;
    invalidate();
}

void Select::on_mouse_down(int x, int y, MouseButton) {
    int idx = -1;
    m_press_part = part_at(x, y, &idx);
    m_press_index = idx;
    pressed = true;
    invalidate();
}

void Select::on_mouse_up(int x, int y, MouseButton) {
    int idx = -1;
    Part part = part_at(x, y, &idx);
    if (part == PartOption && m_press_part == PartOption && idx == m_press_index && idx >= 0 && !is_option_disabled(idx)) {
        if (multiple) {
            toggle_index(idx);
        } else {
            set_selected_index(idx);
            set_open(false);
        }
    } else if (part == PartMain && m_press_part == PartMain) {
        set_open(!open);
    }
    m_press_part = PartNone;
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Select::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) set_open(!open);
    else if (vk == VK_ESCAPE) set_open(false);
    else if (vk == VK_DOWN) { if (!open) open = true; select_relative(1); }
    else if (vk == VK_UP) { if (!open) open = true; select_relative(-1); }
    else if (vk == VK_HOME) { if (!open) open = true; select_first_or_last(false); }
    else if (vk == VK_END) { if (!open) open = true; select_first_or_last(true); }
    else if (vk == VK_BACK && !search_text.empty()) search_text.pop_back();
    invalidate();
}

void Select::on_char(wchar_t ch) {
    if (!open || ch < 32) return;
    search_text.push_back(ch);
    std::vector<int> visible = visible_indices();
    if (!visible.empty()) m_hover_index = visible.front();
    invalidate();
}

void Select::on_blur() {
    has_focus = false;
    open = false;
    search_text.clear();
    m_hover_index = -1;
    m_press_part = PartNone;
    invalidate();
}
