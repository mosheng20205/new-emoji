#include "element_autocomplete.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

static int round_px(float v) {
    return (int)std::lround(v);
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

int Autocomplete::row_height() const {
    int h = round_px(style.font_size * 1.8f);
    return h < 26 ? 26 : h;
}

int Autocomplete::display_count() const {
    if (async_loading || suggestions.empty()) return open ? 1 : 0;
    return (std::min)(6, (int)suggestions.size());
}

int Autocomplete::menu_height() const {
    return row_height() * display_count();
}

int Autocomplete::menu_y() const {
    int mh = menu_height();
    if (mh <= 0) return bounds.h + 4;
    if (parent && bounds.y + bounds.h + mh + 6 > parent->bounds.h && bounds.y > mh + 6) {
        return -mh - 4;
    }
    return bounds.h + 4;
}

void Autocomplete::set_suggestions(const std::vector<std::wstring>& values) {
    suggestions = values;
    async_loading = false;
    if (selected_index < 0 || selected_index >= (int)suggestions.size()) {
        selected_index = suggestions.empty() ? -1 : 0;
    }
    if (open && suggestions.empty()) selected_index = -1;
    invalidate();
}

void Autocomplete::set_value(const std::wstring& next_value) {
    value = next_value;
    if (!value.empty()) {
        open = true;
        m_replace_on_next_char = false;
    }
    invalidate();
}

void Autocomplete::set_selected_index(int index) {
    if (suggestions.empty()) {
        selected_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)suggestions.size()) index = (int)suggestions.size() - 1;
        selected_index = index;
        value = suggestions[selected_index];
    }
    invalidate();
}

void Autocomplete::set_open(bool next_open) {
    open = next_open && (!suggestions.empty() || async_loading || !empty_text.empty());
    invalidate();
}

void Autocomplete::set_async_state(bool loading, int request_id) {
    async_loading = loading;
    async_request_id = request_id;
    if (loading) open = true;
    invalidate();
}

void Autocomplete::set_empty_text(const std::wstring& text) {
    empty_text = text.empty() ? L"🫥 没有匹配建议" : text;
    invalidate();
}

bool Autocomplete::is_open() const {
    return open;
}

int Autocomplete::suggestion_count() const {
    return (int)suggestions.size();
}

int Autocomplete::option_at(int x, int y) const {
    if (!open || suggestions.empty() || async_loading) return -1;
    int my = menu_y();
    int mh = menu_height();
    if (x < 0 || x >= bounds.w || y < my || y >= my + mh) return -1;
    int idx = (y - my) / row_height();
    if (idx < 0 || idx >= display_count()) return -1;
    return idx;
}

Autocomplete::Part Autocomplete::part_at(int x, int y, int* option_index) const {
    int idx = option_at(x, y);
    if (option_index) *option_index = idx;
    if (idx >= 0) return PartOption;
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

Element* Autocomplete::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* Autocomplete::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return option_at(lx, ly) >= 0 ? this : nullptr;
}

void Autocomplete::paint(RenderContext& ctx) {
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
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    float pad_l = (float)style.pad_left;
    float pad_r = (float)style.pad_right;
    draw_text(ctx, value.empty() ? L"请输入关键字" : value, style,
              value.empty() ? t->text_secondary : fg,
              pad_l, 0.0f, (float)bounds.w - pad_l - pad_r, (float)bounds.h,
              DWRITE_TEXT_ALIGNMENT_LEADING);

    ctx.rt->SetTransform(saved);
}

void Autocomplete::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color menu_bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF242637 : 0xFFFFFFFF;
    int my = menu_y();
    int rh = row_height();
    int mh = menu_height();
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F menu = { 0, (float)my, (float)bounds.w, (float)(my + mh) };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(menu, radius, radius), ctx.get_brush(menu_bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(menu.left + 0.5f, menu.top + 0.5f,
                                      menu.right - 0.5f, menu.bottom - 0.5f), radius, radius),
        ctx.get_brush(t->border_default), 1.0f);
    if (async_loading || suggestions.empty()) {
        std::wstring msg = async_loading ? L"⏳ 正在加载建议..." : empty_text;
        draw_text(ctx, msg, style, t->text_secondary,
                  0.0f, (float)my, (float)bounds.w, (float)rh,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
        ctx.rt->SetTransform(saved);
        return;
    }
    for (int i = 0; i < display_count(); ++i) {
        float y = (float)(my + i * rh);
        if (i == m_hover_index || i == selected_index) {
            Color row_bg = i == selected_index ? (t->accent & 0x33FFFFFF) : t->button_hover;
            D2D1_RECT_F row = { 2.0f, y + 1.0f, (float)bounds.w - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(row_bg));
        }
        draw_text(ctx, suggestions[i], style, i == selected_index ? t->accent : fg,
                  (float)style.pad_left, y, (float)bounds.w - style.pad_left - style.pad_right, (float)rh);
    }

    ctx.rt->SetTransform(saved);
}

void Autocomplete::on_mouse_move(int x, int y) {
    int idx = option_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Autocomplete::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Autocomplete::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_index);
    pressed = true;
    invalidate();
}

void Autocomplete::on_mouse_up(int x, int y, MouseButton) {
    int idx = -1;
    Part part = part_at(x, y, &idx);
    if (part == PartOption && m_press_part == PartOption && idx == m_press_index && idx >= 0) {
        set_selected_index(idx);
        open = false;
    } else if (part == PartMain && m_press_part == PartMain) {
        open = !open;
    }
    m_press_part = PartNone;
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Autocomplete::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        open = !open;
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_DOWN) {
        if (!open) set_open(true);
        if (!suggestions.empty()) {
            set_selected_index(selected_index + 1);
        }
    } else if (vk == VK_UP) {
        if (!open) set_open(true);
        if (!suggestions.empty()) {
            set_selected_index(selected_index - 1);
        }
    } else if (vk == VK_BACK) {
        if (!value.empty()) {
            value.pop_back();
            m_replace_on_next_char = false;
            open = true;
            invalidate();
        }
    }
}

void Autocomplete::on_char(wchar_t ch) {
    if (ch == L'\r' || ch == L'\n' || ch == 27) return;
    if (m_replace_on_next_char) {
        value.clear();
        m_replace_on_next_char = false;
    }
    value.push_back(ch);
    set_open(true);
    invalidate();
}

void Autocomplete::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    m_press_part = PartNone;
    invalidate();
}
