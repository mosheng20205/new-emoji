#include "element_mentions.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
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

int Mentions::row_height() const {
    return (std::max)(28, (int)(style.font_size * 1.8f));
}

int Mentions::display_count() const {
    return (std::min)(6, (int)rendered_indices().size());
}

int Mentions::popup_height() const {
    return row_height() * display_count();
}

int Mentions::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

void Mentions::set_value(const std::wstring& next_value) {
    value = next_value;
    update_filter_from_value();
    open = !suggestions.empty() && value.find(trigger_char) != std::wstring::npos;
    invalidate();
}

void Mentions::set_suggestions(const std::vector<std::wstring>& values) {
    suggestions = values;
    if (selected_index < 0 || selected_index >= (int)rendered_indices().size()) selected_index = 0;
    open = !rendered_indices().empty() && value.find(trigger_char) != std::wstring::npos;
    invalidate();
}

void Mentions::set_selected_index(int index) {
    auto visible = rendered_indices();
    if (visible.empty()) {
        selected_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)visible.size()) index = (int)visible.size() - 1;
        selected_index = index;
    }
    invalidate();
}

void Mentions::set_open(bool next_open) {
    open = next_open && !rendered_indices().empty();
    invalidate();
}

void Mentions::set_options(wchar_t trigger, bool next_filter_enabled, bool insert_space) {
    trigger_char = trigger ? trigger : L'@';
    filter_enabled = next_filter_enabled;
    insert_space_after_pick = insert_space;
    update_filter_from_value();
    invalidate();
}

void Mentions::set_filter_text(const std::wstring& text) {
    filter_text = text;
    open = !rendered_indices().empty();
    invalidate();
}

void Mentions::commit_text(const std::wstring& text) {
    if (text.empty()) return;
    value += text;
    update_filter_from_value();
    open = value.find(trigger_char) != std::wstring::npos && !rendered_indices().empty();
    invalidate();
}

void Mentions::insert_selected() {
    auto visible = rendered_indices();
    if (selected_index < 0 || selected_index >= (int)visible.size()) return;
    const std::wstring& picked = suggestions[visible[selected_index]];
    size_t pos = value.find_last_of(trigger_char);
    if (pos == std::wstring::npos) {
        if (!value.empty() && value.back() != L' ') value.push_back(L' ');
        value.push_back(trigger_char);
        value += picked;
    } else {
        value = value.substr(0, pos + 1) + picked;
    }
    if (insert_space_after_pick && (value.empty() || value.back() != L' ')) value.push_back(L' ');
    open = false;
    filter_text.clear();
    invalidate();
}

bool Mentions::is_open() const {
    return open;
}

int Mentions::suggestion_count() const {
    return (int)suggestions.size();
}

int Mentions::matched_count() const {
    return (int)rendered_indices().size();
}

bool Mentions::matches_filter(int index) const {
    if (index < 0 || index >= (int)suggestions.size()) return false;
    if (!filter_enabled || filter_text.empty()) return true;
    return suggestions[index].find(filter_text) != std::wstring::npos;
}

std::vector<int> Mentions::rendered_indices() const {
    std::vector<int> indices;
    for (int i = 0; i < (int)suggestions.size(); ++i) {
        if (matches_filter(i)) indices.push_back(i);
    }
    return indices;
}

void Mentions::update_filter_from_value() {
    if (!filter_enabled) {
        filter_text.clear();
        return;
    }
    size_t pos = value.find_last_of(trigger_char);
    if (pos == std::wstring::npos) {
        filter_text.clear();
        return;
    }
    filter_text = value.substr(pos + 1);
    size_t end = filter_text.find_first_of(L" \t\r\n");
    if (end != std::wstring::npos) filter_text = filter_text.substr(0, end);
}

int Mentions::option_at(int x, int y) const {
    if (!open || rendered_indices().empty()) return -1;
    int py = popup_y();
    int ph = popup_height();
    if (x < 0 || x >= bounds.w || y < py || y >= py + ph) return -1;
    int idx = (y - py) / row_height();
    if (idx < 0 || idx >= display_count()) return -1;
    return idx;
}

Mentions::Part Mentions::part_at(int x, int y, int* option_index) const {
    int idx = option_at(x, y);
    if (option_index) *option_index = idx;
    if (idx >= 0) return PartOption;
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

Element* Mentions::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* Mentions::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return option_at(lx, ly) >= 0 ? this : nullptr;
}

void Mentions::paint(RenderContext& ctx) {
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

    D2D1_RECT_F field = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(field, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        ROUNDED(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    std::wstring prompt = value.empty() ? L"输入 @ 触发提及建议" : value;
    draw_text(ctx, prompt, style, value.empty() ? t->text_secondary : fg,
              (float)style.pad_left, 0.0f, (float)bounds.w - style.pad_left - style.pad_right, (float)bounds.h);
    ctx.rt->SetTransform(saved);
}

void Mentions::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color menu_bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    int py = popup_y();
    int rh = row_height();
    int ph = popup_height();
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F menu = { 0, (float)py, (float)bounds.w, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(menu, radius, radius), ctx.get_brush(menu_bg));
    ctx.rt->DrawRoundedRectangle(
        ROUNDED(D2D1::RectF(menu.left + 0.5f, menu.top + 0.5f,
                            menu.right - 0.5f, menu.bottom - 0.5f), radius, radius),
        ctx.get_brush(t->border_default), 1.0f);

    auto visible = rendered_indices();
    for (int i = 0; i < display_count(); ++i) {
        int source_index = visible[i];
        float y = (float)(py + i * rh);
        if (i == m_hover_index || i == selected_index) {
            Color row_bg = i == selected_index ? with_alpha(t->accent, 0x26) : t->button_hover;
            D2D1_RECT_F row = { 2.0f, y + 1.0f, (float)bounds.w - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(row_bg));
        }
        draw_text(ctx, suggestions[source_index], style, i == selected_index ? t->accent : fg,
                  (float)style.pad_left, y, (float)bounds.w - style.pad_left - style.pad_right, (float)rh);
    }

    ctx.rt->SetTransform(saved);
}

void Mentions::on_mouse_move(int x, int y) {
    int idx = option_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Mentions::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Mentions::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_index);
    pressed = true;
    invalidate();
}

void Mentions::on_mouse_up(int x, int y, MouseButton) {
    int idx = -1;
    Part part = part_at(x, y, &idx);
    if (part == PartOption && m_press_part == PartOption && idx == m_press_index && idx >= 0) {
        selected_index = idx;
        insert_selected();
    } else if (part == PartMain && m_press_part == PartMain) {
        open = !open;
    }
    m_press_part = PartNone;
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Mentions::on_key_down(int vk, int) {
    if (vk == VK_RETURN) {
        if (open) insert_selected();
        else open = !open;
    } else if (vk == VK_SPACE) {
        open = !open;
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_DOWN) {
        if (!open) open = true;
        int count = (int)rendered_indices().size();
        if (count > 0) selected_index = (selected_index + 1) % count;
    } else if (vk == VK_UP) {
        if (!open) open = true;
        int count = (int)rendered_indices().size();
        if (count > 0) selected_index = (selected_index - 1 + count) % count;
    } else if (vk == VK_BACK) {
        if (!value.empty()) value.pop_back();
        update_filter_from_value();
    }
    invalidate();
}

void Mentions::on_char(wchar_t ch) {
    if (ch < 32 || ch == L'\r' || ch == L'\n') return;
    commit_text(std::wstring(1, ch));
}

void Mentions::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    m_press_part = PartNone;
    invalidate();
}
