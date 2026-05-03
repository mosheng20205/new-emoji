#include "element_tabs.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

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

void Tabs::set_items(const std::vector<std::wstring>& values) {
    items = values;
    m_hover_index = -1;
    m_press_index = -1;
    if (items.empty()) active_index = -1;
    else if (active_index < 0 || active_index >= (int)items.size()) active_index = 0;
    clamp_scroll();
    ensure_active_visible();
    last_action = 1;
    invalidate();
}

void Tabs::set_active_index(int value) {
    select_index(value, 1);
}

void Tabs::set_tab_type(int value) {
    tab_type = value == 1 ? 1 : 0;
    last_action = 1;
    invalidate();
}

void Tabs::set_options(int type, bool close_enabled, bool add_enabled) {
    tab_type = type == 1 ? 1 : 0;
    closable = close_enabled;
    addable = add_enabled;
    clamp_scroll();
    ensure_active_visible();
    last_action = 1;
    invalidate();
}

void Tabs::add_tab(const std::wstring& label) {
    std::wstring text = label.empty() ? L"新标签" : label;
    items.push_back(text);
    last_added_index = (int)items.size() - 1;
    ++add_count;
    last_action = 5;
    select_index(last_added_index, 5);
    if (add_cb) add_cb(id, last_added_index, (int)items.size(), active_index);
}

void Tabs::close_tab(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    items.erase(items.begin() + index);
    last_closed_index = index;
    ++close_count;
    last_action = 4;
    if (items.empty()) active_index = -1;
    else if (active_index > index) --active_index;
    else if (active_index >= (int)items.size()) active_index = (int)items.size() - 1;
    clamp_scroll();
    ensure_active_visible();
    if (close_cb) close_cb(id, index, (int)items.size(), active_index);
    if (change_cb) change_cb(id, active_index, (int)items.size(), last_action);
    invalidate();
}

void Tabs::set_scroll_offset(int offset) {
    clamp_scroll();
    int next = (std::max)(0, (std::min)(offset, max_scroll_offset));
    if (next != scroll_offset) {
        scroll_offset = next;
        ++scroll_count;
    }
    last_action = 6;
    invalidate();
}

void Tabs::scroll_delta(int delta) {
    if (delta == 0) return;
    set_scroll_offset(scroll_offset + delta);
}

float Tabs::tabs_view_width() const {
    float available = (float)bounds.w - style.pad_left - style.pad_right;
    if (addable) available -= 36.0f;
    return (std::max)(0.0f, available);
}

float Tabs::tab_width() const {
    if (items.empty()) return 0.0f;
    float view = tabs_view_width();
    if (view <= 0.0f) return 96.0f;
    if ((int)items.size() <= 4) return (std::max)(72.0f, view / (float)items.size());
    return (std::max)(104.0f, (std::min)(152.0f, view / 4.0f));
}

int Tabs::total_tabs_width() const {
    return (int)(tab_width() * (float)items.size() + 0.5f);
}

void Tabs::clamp_scroll() {
    int view = (int)tabs_view_width();
    max_scroll_offset = (std::max)(0, total_tabs_width() - view);
    if (scroll_offset < 0) scroll_offset = 0;
    if (scroll_offset > max_scroll_offset) scroll_offset = max_scroll_offset;
}

void Tabs::ensure_active_visible() {
    clamp_scroll();
    if (active_index < 0 || active_index >= (int)items.size()) return;
    int left = (int)(tab_width() * (float)active_index);
    int right = left + (int)tab_width();
    int view = (int)tabs_view_width();
    if (left < scroll_offset) scroll_offset = left;
    else if (right > scroll_offset + view) scroll_offset = right - view;
    clamp_scroll();
}

void Tabs::select_index(int value, int action) {
    if (items.empty()) {
        active_index = -1;
    } else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        active_index = value;
    }
    ++select_count;
    last_action = action;
    ensure_active_visible();
    if (change_cb) change_cb(id, active_index, (int)items.size(), last_action);
    invalidate();
}

int Tabs::part_at(int x, int y, int* part) const {
    if (part) *part = 0;
    if (y < 0 || y >= bounds.h) return -1;
    float view_w = tabs_view_width();
    float add_left = (float)style.pad_left + view_w + 4.0f;
    if (addable && x >= (int)add_left && x < (int)add_left + 28) {
        if (part) *part = 3;
        return -1;
    }
    if (items.empty() || x < style.pad_left || x >= style.pad_left + (int)view_w) return -1;
    float local = (float)x - (float)style.pad_left + (float)scroll_offset;
    int idx = (int)(local / tab_width());
    if (idx < 0 || idx >= (int)items.size()) return -1;
    float tab_left = (float)style.pad_left - (float)scroll_offset + tab_width() * (float)idx;
    float close_left = tab_left + tab_width() - 26.0f;
    if (closable && x >= (int)close_left && x <= (int)(tab_left + tab_width() - 8.0f)) {
        if (part) *part = 2;
    } else if (part) {
        *part = 1;
    }
    return idx;
}

int Tabs::tab_at(int x, int y) const {
    int part = 0;
    return part_at(x, y, &part);
}

void Tabs::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    Tabs* self = const_cast<Tabs*>(this);
    self->clamp_scroll();
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color active = t->accent;
    float tab_w = tab_width();
    float tab_h = (float)bounds.h - 2.0f;
    float view_w = tabs_view_width();

    D2D1_RECT_F full_clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(full_clip);
    if (tab_type == 0) {
        ctx.rt->DrawLine(D2D1::Point2F((float)style.pad_left, (float)bounds.h - 1.0f),
                         D2D1::Point2F((float)bounds.w - style.pad_right, (float)bounds.h - 1.0f),
                         ctx.get_brush(border), 1.0f);
    }

    D2D1_RECT_F tab_clip = { (float)style.pad_left, 0, (float)style.pad_left + view_w, (float)bounds.h };
    ctx.push_clip(tab_clip);
    for (int i = 0; i < (int)items.size(); ++i) {
        float x = (float)style.pad_left - (float)scroll_offset + tab_w * (float)i;
        if (x + tab_w < style.pad_left || x > style.pad_left + view_w) continue;
        bool is_active = i == active_index;
        bool hot = i == m_hover_index;
        bool close_hot = hot && m_hover_part == 2;
        if (tab_type == 1) {
            Color bg = is_active ? (dark ? 0xFF313244 : 0xFFFFFFFF) : (hot ? t->button_hover : 0);
            D2D1_RECT_F r = { x, 1.0f, x + tab_w - 2.0f, tab_h };
            if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(r, 4.0f, 4.0f), ctx.get_brush(bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(r, 4.0f, 4.0f),
                                         ctx.get_brush(is_active ? active : border), 1.0f);
        } else if (hot && !is_active) {
            D2D1_RECT_F r = { x + 2.0f, 4.0f, x + tab_w - 4.0f, tab_h - 3.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(r, 4.0f, 4.0f), ctx.get_brush(t->button_hover));
        }
        float close_w = closable ? 24.0f : 0.0f;
        draw_text(ctx, items[i], style, is_active ? active : fg,
                  x + 8.0f, 0.0f, tab_w - 14.0f - close_w, tab_h,
                  DWRITE_TEXT_ALIGNMENT_LEADING);
        if (closable) {
            D2D1_RECT_F cr = { x + tab_w - 25.0f, 7.0f, x + tab_w - 7.0f, (float)bounds.h - 7.0f };
            if (close_hot) ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((cr.left + cr.right) * 0.5f, (cr.top + cr.bottom) * 0.5f), 9.0f, 9.0f), ctx.get_brush(t->button_hover));
            draw_text(ctx, L"x", style, close_hot ? active : t->text_secondary, cr.left, cr.top, cr.right - cr.left, cr.bottom - cr.top);
        }
        if (tab_type == 0 && is_active) {
            ctx.rt->DrawLine(D2D1::Point2F(x + 8.0f, (float)bounds.h - 1.5f),
                             D2D1::Point2F(x + tab_w - 8.0f, (float)bounds.h - 1.5f),
                             ctx.get_brush(active), 2.0f);
        }
    }
    ctx.pop_clip();

    if (max_scroll_offset > 0) {
        Color hint = t->text_secondary;
        if (scroll_offset > 0) draw_text(ctx, L"<", style, hint, 0.0f, 0.0f, 18.0f, (float)bounds.h);
        if (scroll_offset < max_scroll_offset) draw_text(ctx, L">", style, hint, (float)style.pad_left + view_w - 18.0f, 0.0f, 18.0f, (float)bounds.h);
    }
    if (addable) {
        float ax = (float)style.pad_left + view_w + 4.0f;
        D2D1_RECT_F ar = { ax, 5.0f, ax + 28.0f, (float)bounds.h - 5.0f };
        Color bg = m_hover_part == 3 ? t->button_hover : (tab_type == 1 ? (dark ? 0xFF313244 : 0xFFFFFFFF) : 0);
        if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(ar, 4.0f, 4.0f), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(ar, 4.0f, 4.0f), ctx.get_brush(border), 1.0f);
        draw_text(ctx, L"+", style, m_hover_part == 3 ? active : fg, ar.left, ar.top, ar.right - ar.left, ar.bottom - ar.top);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Tabs::on_mouse_move(int x, int y) {
    int part = 0;
    int idx = part_at(x, y, &part);
    if (idx != m_hover_index || part != m_hover_part) {
        m_hover_index = idx;
        m_hover_part = part;
        invalidate();
    }
}

void Tabs::on_mouse_leave() {
    m_hover_index = -1;
    m_press_index = -1;
    m_hover_part = 0;
    m_press_part = 0;
    hovered = false;
    invalidate();
}

void Tabs::on_mouse_down(int x, int y, MouseButton) {
    m_press_index = part_at(x, y, &m_press_part);
    if (m_press_part == 3) m_press_index = -1;
    pressed = true;
    invalidate();
}

void Tabs::on_mouse_up(int x, int y, MouseButton) {
    int part = 0;
    int idx = part_at(x, y, &part);
    if (part == 3 && m_press_part == 3) {
        add_tab(L"新标签");
    } else if (idx >= 0 && idx == m_press_index && part == m_press_part) {
        if (part == 2) close_tab(idx);
        else if (part == 1) select_index(idx, 2);
    }
    m_press_index = -1;
    m_press_part = 0;
    pressed = false;
    invalidate();
}

void Tabs::on_mouse_wheel(int, int, int delta) {
    if (max_scroll_offset <= 0) return;
    int steps = delta / WHEEL_DELTA;
    if (steps == 0) steps = delta > 0 ? 1 : -1;
    scroll_delta(-steps * 48);
}

void Tabs::on_key_down(int vk, int) {
    if (vk == VK_LEFT) select_index(active_index - 1, 3);
    else if (vk == VK_RIGHT) select_index(active_index + 1, 3);
    else if (vk == VK_HOME) select_index(0, 3);
    else if (vk == VK_END) select_index((int)items.size() - 1, 3);
    else if (vk == VK_PRIOR) scroll_delta(-96);
    else if (vk == VK_NEXT) scroll_delta(96);
    else if ((vk == VK_DELETE || vk == VK_BACK) && closable && active_index >= 0) close_tab(active_index);
    else if ((vk == VK_INSERT || vk == VK_OEM_PLUS) && addable) add_tab(L"新标签");
}
