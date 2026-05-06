#include "element_autocomplete.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

static int round_px(float v) {
    return (int)std::lround(v);
}

static float measure_text_width(const std::wstring& text, const ElementStyle& style) {
    if (!g_dwrite_factory || text.empty()) return 0.0f;
    IDWriteTextFormat* fmt = nullptr;
    HRESULT hr = g_dwrite_factory->CreateTextFormat(
        style.font_name.c_str(), nullptr,
        DWRITE_FONT_WEIGHT_NORMAL, DWRITE_FONT_STYLE_NORMAL, DWRITE_FONT_STRETCH_NORMAL,
        style.font_size, L"", &fmt);
    if (FAILED(hr) || !fmt) return 0.0f;

    IDWriteTextLayout* layout = nullptr;
    hr = g_dwrite_factory->CreateTextLayout(
        text.c_str(), static_cast<UINT32>(text.size()),
        fmt, 4096.0f, 512.0f, &layout);
    fmt->Release();
    if (FAILED(hr) || !layout) return 0.0f;

    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    DWRITE_TEXT_METRICS tm{};
    float width = 0.0f;
    if (SUCCEEDED(layout->GetMetrics(&tm))) width = tm.widthIncludingTrailingWhitespace;
    layout->Release();
    return width;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT valign = DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                      bool wrap = false) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(valign);
    layout->SetWordWrapping(wrap ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

float Autocomplete::left_padding() const {
    float pad = (float)style.pad_left;
    if (!prefix_icon.empty()) pad += measure_text_width(prefix_icon, style) + 10.0f;
    return pad;
}

float Autocomplete::right_padding() const {
    float pad = (float)style.pad_right;
    if (!suffix_icon.empty()) pad += measure_text_width(suffix_icon, style) + 10.0f;
    return pad;
}

Rect Autocomplete::suffix_icon_rect() const {
    if (suffix_icon.empty()) return {};
    float icon_w = measure_text_width(suffix_icon, style) + 6.0f;
    int width = (int)std::lround((std::max)(18.0f, icon_w));
    return {
        bounds.w - style.pad_right - width,
        (bounds.h - (int)std::lround(style.font_size + 6.0f)) / 2,
        width,
        (int)std::lround(style.font_size + 6.0f)
    };
}

int Autocomplete::row_height() const {
    bool has_subtitle = false;
    for (const auto& item : suggestions) {
        if (!item.subtitle.empty()) {
            has_subtitle = true;
            break;
        }
    }
    int h = round_px(style.font_size * (has_subtitle ? 3.0f : 1.8f));
    return h < (has_subtitle ? 46 : 26) ? (has_subtitle ? 46 : 26) : h;
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

const AutocompleteSuggestion* Autocomplete::selected_suggestion() const {
    if (selected_index < 0 || selected_index >= (int)suggestions.size()) return nullptr;
    return &suggestions[(size_t)selected_index];
}

void Autocomplete::set_suggestions(const std::vector<AutocompleteSuggestion>& values) {
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
    invalidate();
}

void Autocomplete::set_selected_index(int index) {
    if (suggestions.empty()) {
        selected_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)suggestions.size()) index = (int)suggestions.size() - 1;
        selected_index = index;
        const auto& item = suggestions[(size_t)selected_index];
        value = item.value.empty() ? item.title : item.value;
        m_replace_on_next_char = true;
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

void Autocomplete::set_placeholder(const std::wstring& text) {
    placeholder = text.empty() ? L"请输入内容" : text;
    invalidate();
}

void Autocomplete::set_icons(const std::wstring& next_prefix_icon, const std::wstring& next_suffix_icon) {
    prefix_icon = next_prefix_icon;
    suffix_icon = next_suffix_icon;
    invalidate();
}

void Autocomplete::set_behavior(bool next_trigger_on_focus) {
    trigger_on_focus = next_trigger_on_focus;
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
    Rect icon = suffix_icon_rect();
    if (icon.w > 0 && icon.contains(x, y)) return PartSuffixIcon;
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
    bool disabled = !enabled;
    Color bg = disabled ? t->button_bg : (style.bg_color ? style.bg_color : t->edit_bg);
    Color border = disabled ? t->border_default : (open || has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border));
    Color fg = disabled ? t->text_muted : (style.fg_color ? style.fg_color : t->text_primary);
    Color hint = disabled ? t->text_muted : t->text_secondary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    if (!prefix_icon.empty()) {
        draw_text(ctx, prefix_icon, style, hint,
                  (float)style.pad_left, 0.0f,
                  measure_text_width(prefix_icon, style) + 6.0f, (float)bounds.h);
    }
    if (!suffix_icon.empty()) {
        Rect icon = suffix_icon_rect();
        draw_text(ctx, suffix_icon, style, hint,
                  (float)icon.x, 0.0f, (float)icon.w, (float)bounds.h,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    float pad_l = left_padding();
    float pad_r = right_padding();
    draw_text(ctx, value.empty() ? placeholder : value, style,
              value.empty() ? hint : fg,
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
        std::wstring msg = async_loading ? L"⌛ 正在加载建议..." : empty_text;
        draw_text(ctx, msg, style, t->text_secondary,
                  0.0f, (float)my, (float)bounds.w, (float)rh,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
        ctx.rt->SetTransform(saved);
        return;
    }
    for (int i = 0; i < display_count(); ++i) {
        const auto& item = suggestions[(size_t)i];
        float y = (float)(my + i * rh);
        if (i == m_hover_index || i == selected_index) {
            Color row_bg = i == selected_index ? (t->accent & 0x33FFFFFF) : t->button_hover;
            D2D1_RECT_F row = { 2.0f, y + 1.0f, (float)bounds.w - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(row_bg));
        }
        if (item.subtitle.empty()) {
            draw_text(ctx, item.title, style, i == selected_index ? t->accent : fg,
                      (float)style.pad_left, y, (float)bounds.w - style.pad_left - style.pad_right, (float)rh);
        } else {
            float title_h = style.font_size + 8.0f;
            draw_text(ctx, item.title, style, i == selected_index ? t->accent : fg,
                      (float)style.pad_left, y + 4.0f,
                      (float)bounds.w - style.pad_left - style.pad_right, title_h,
                      DWRITE_TEXT_ALIGNMENT_LEADING, DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
            draw_text(ctx, item.subtitle, style, t->text_secondary,
                      (float)style.pad_left, y + title_h,
                      (float)bounds.w - style.pad_left - style.pad_right, (float)rh - title_h - 2.0f,
                      DWRITE_TEXT_ALIGNMENT_LEADING, DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
        }
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
    m_click_callback_armed = false;
    invalidate();
}

void Autocomplete::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_index);
    m_click_callback_armed = (m_press_part == PartSuffixIcon);
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
        if (m_opened_on_focus) {
            set_open(true);
        } else {
            set_open(!open);
        }
    }
    m_press_part = PartNone;
    m_press_index = -1;
    m_opened_on_focus = false;
    pressed = false;
    invalidate();
}

void Autocomplete::on_key_down(int vk, int) {
    m_opened_on_focus = false;
    if (vk == VK_RETURN) {
        if (open && selected_index >= 0 && selected_index < (int)suggestions.size()) {
            set_selected_index(selected_index);
            open = false;
        } else {
            open = !open;
        }
    } else if (vk == VK_SPACE) {
        open = !open;
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_DOWN) {
        if (!open) set_open(true);
        if (!suggestions.empty()) {
            if (selected_index < 0) {
                selected_index = 0;
                invalidate();
            }
            else set_selected_index(selected_index + 1);
        }
    } else if (vk == VK_UP) {
        if (!open) set_open(true);
        if (!suggestions.empty()) {
            if (selected_index < 0) {
                selected_index = 0;
                invalidate();
            }
            else set_selected_index(selected_index - 1);
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
    if (ch == L'\r' || ch == L'\n' || ch == 27 || ch < 32) return;
    m_opened_on_focus = false;
    if (m_replace_on_next_char) {
        value.clear();
        m_replace_on_next_char = false;
    }
    value.push_back(ch);
    set_open(true);
    invalidate();
}

void Autocomplete::on_focus() {
    has_focus = true;
    if (trigger_on_focus) {
        set_open(true);
        m_opened_on_focus = open;
    } else {
        m_opened_on_focus = false;
        invalidate();
    }
}

void Autocomplete::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    m_press_part = PartNone;
    m_opened_on_focus = false;
    m_click_callback_armed = false;
    invalidate();
}
