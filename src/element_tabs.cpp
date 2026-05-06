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

static void draw_wrapped_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                              Color color, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Tabs::sync_legacy_items() {
    items.clear();
    for (const auto& item : tab_items) {
        items.push_back(item.label);
    }
}

void Tabs::set_items(const std::vector<std::wstring>& values) {
    tab_items.clear();
    tab_items.reserve(values.size());
    for (size_t i = 0; i < values.size(); ++i) {
        TabsItem item;
        item.label = values[i];
        item.name = std::to_wstring(i + 1);
        item.content = values[i];
        tab_items.push_back(item);
    }
    sync_legacy_items();
    m_hover_index = -1;
    m_press_index = -1;
    if (tab_items.empty()) active_index = -1;
    else if (active_index < 0 || active_index >= (int)tab_items.size()) active_index = 0;
    clamp_scroll();
    ensure_active_visible();
    last_action = 1;
    invalidate();
}

void Tabs::set_items_ex(const std::vector<TabsItem>& values) {
    tab_items = values;
    for (size_t i = 0; i < tab_items.size(); ++i) {
        if (tab_items[i].label.empty()) tab_items[i].label = L"标签";
        if (tab_items[i].name.empty()) tab_items[i].name = std::to_wstring(i + 1);
        if (tab_items[i].content.empty()) tab_items[i].content = tab_items[i].label;
    }
    sync_legacy_items();
    m_hover_index = -1;
    m_press_index = -1;
    if (tab_items.empty()) active_index = -1;
    else if (active_index < 0 || active_index >= (int)tab_items.size()) active_index = 0;
    clamp_scroll();
    ensure_active_visible();
    last_action = 1;
    invalidate();
}

void Tabs::set_active_index(int value) {
    select_index(value, 1);
}

void Tabs::set_active_name(const std::wstring& name) {
    if (name.empty()) return;
    for (int i = 0; i < (int)tab_items.size(); ++i) {
        if (tab_items[i].name == name) {
            select_index(i, 1);
            return;
        }
    }
}

void Tabs::set_tab_type(int value) {
    tab_type = (std::max)(0, (std::min)(value, 2));
    last_action = 1;
    invalidate();
}

void Tabs::set_tab_position(int value) {
    tab_position = (value >= 0 && value <= 3) ? value : 0;
    clamp_scroll();
    ensure_active_visible();
    last_action = 1;
    invalidate();
}

void Tabs::set_header_align(int value) {
    header_align = (value >= 0 && value <= 2) ? value : 0;
    last_action = 1;
    invalidate();
}

void Tabs::set_options(int type, bool close_enabled, bool add_enabled) {
    tab_type = (std::max)(0, (std::min)(type, 2));
    closable = close_enabled;
    addable = add_enabled;
    clamp_scroll();
    ensure_active_visible();
    last_action = 1;
    invalidate();
}

void Tabs::set_editable(bool value) {
    editable = value;
    closable = value || closable;
    addable = value || addable;
    clamp_scroll();
    ensure_active_visible();
    last_action = 1;
    invalidate();
}

void Tabs::set_content_visible(bool value) {
    content_visible = value;
    last_action = 1;
    invalidate();
}

void Tabs::add_tab(const std::wstring& label) {
    TabsItem item;
    item.label = label.empty() ? L"✨ 新标签" : label;
    item.name = L"tab-" + std::to_wstring(add_count + (int)tab_items.size() + 1);
    item.content = item.label + L" 的内容";
    tab_items.push_back(item);
    sync_legacy_items();
    last_added_index = (int)tab_items.size() - 1;
    ++add_count;
    last_action = 5;
    select_index(last_added_index, 5);
    if (add_cb) add_cb(id, last_added_index, (int)tab_items.size(), active_index);
}

void Tabs::close_tab(int index) {
    if (index < 0 || index >= (int)tab_items.size() || !item_close_enabled(index)) return;
    tab_items.erase(tab_items.begin() + index);
    sync_legacy_items();
    last_closed_index = index;
    ++close_count;
    last_action = 4;
    if (tab_items.empty()) active_index = -1;
    else if (active_index > index) --active_index;
    else if (active_index >= (int)tab_items.size()) active_index = (int)tab_items.size() - 1;
    clamp_scroll();
    ensure_active_visible();
    if (close_cb) close_cb(id, index, (int)tab_items.size(), active_index);
    if (change_cb) change_cb(id, active_index, (int)tab_items.size(), last_action);
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

std::wstring Tabs::active_name() const {
    if (active_index < 0 || active_index >= (int)tab_items.size()) return L"";
    return tab_items[active_index].name;
}

std::wstring Tabs::item_content(int index) const {
    if (index < 0 || index >= (int)tab_items.size()) return L"";
    return tab_items[index].content;
}

bool Tabs::is_vertical() const {
    return tab_position == 1 || tab_position == 3;
}

float Tabs::header_extent() const {
    if (!content_visible) return is_vertical() ? (float)bounds.w : (float)bounds.h;
    if (is_vertical()) return (std::max)(120.0f, (std::min)(190.0f, (float)bounds.w * 0.32f));
    return (std::max)(38.0f, (std::min)(52.0f, (float)bounds.h * 0.28f));
}

D2D1_RECT_F Tabs::header_rect() const {
    float he = header_extent();
    if (!content_visible) return D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h);
    if (tab_position == 1) return D2D1::RectF((float)bounds.w - he, 0, (float)bounds.w, (float)bounds.h);
    if (tab_position == 2) return D2D1::RectF(0, (float)bounds.h - he, (float)bounds.w, (float)bounds.h);
    if (tab_position == 3) return D2D1::RectF(0, 0, he, (float)bounds.h);
    return D2D1::RectF(0, 0, (float)bounds.w, he);
}

D2D1_RECT_F Tabs::content_rect() const {
    if (!content_visible) return D2D1::RectF(0, 0, 0, 0);
    float he = header_extent();
    if (tab_position == 1) return D2D1::RectF(0, 0, (float)bounds.w - he, (float)bounds.h);
    if (tab_position == 2) return D2D1::RectF(0, 0, (float)bounds.w, (float)bounds.h - he);
    if (tab_position == 3) return D2D1::RectF(he, 0, (float)bounds.w, (float)bounds.h);
    return D2D1::RectF(0, he, (float)bounds.w, (float)bounds.h);
}

float Tabs::tabs_view_extent() const {
    D2D1_RECT_F hr = header_rect();
    float available = (is_vertical() ? (hr.bottom - hr.top) : (hr.right - hr.left)) - style.pad_left - style.pad_right;
    if (addable || editable) available -= 36.0f;
    return (std::max)(0.0f, available);
}

float Tabs::tab_extent() const {
    if (tab_items.empty()) return 0.0f;
    float view = tabs_view_extent();
    if (view <= 0.0f) return is_vertical() ? 42.0f : 96.0f;
    if (is_vertical()) return 42.0f;
    if ((int)tab_items.size() <= 4) return (std::max)(72.0f, view / (float)tab_items.size());
    return (std::max)(104.0f, (std::min)(152.0f, view / 4.0f));
}

int Tabs::total_tabs_extent() const {
    return (int)(tab_extent() * (float)tab_items.size() + 0.5f);
}

bool Tabs::item_close_enabled(int index) const {
    return (closable || editable) && index >= 0 && index < (int)tab_items.size() && tab_items[index].closable;
}

void Tabs::clamp_scroll() {
    int view = (int)tabs_view_extent();
    max_scroll_offset = (std::max)(0, total_tabs_extent() - view);
    if (scroll_offset < 0) scroll_offset = 0;
    if (scroll_offset > max_scroll_offset) scroll_offset = max_scroll_offset;
}

void Tabs::ensure_active_visible() {
    clamp_scroll();
    if (active_index < 0 || active_index >= (int)tab_items.size()) return;
    int left = (int)(tab_extent() * (float)active_index);
    int right = left + (int)tab_extent();
    int view = (int)tabs_view_extent();
    if (left < scroll_offset) scroll_offset = left;
    else if (right > scroll_offset + view) scroll_offset = right - view;
    clamp_scroll();
}

void Tabs::select_index(int value, int action) {
    if (tab_items.empty()) {
        active_index = -1;
    } else {
        if (value < 0) value = 0;
        if (value >= (int)tab_items.size()) value = (int)tab_items.size() - 1;
        if (tab_items[value].disabled) return;
        active_index = value;
    }
    ++select_count;
    last_action = action;
    ensure_active_visible();
    if (change_cb) change_cb(id, active_index, (int)tab_items.size(), last_action);
    invalidate();
}

int Tabs::part_at(int x, int y, int* part) const {
    if (part) *part = 0;
    if (x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    D2D1_RECT_F hr = header_rect();
    if ((float)x < hr.left || (float)x >= hr.right || (float)y < hr.top || (float)y >= hr.bottom) return -1;
    float view = tabs_view_extent();
    float axis = is_vertical() ? ((float)y - hr.top) : ((float)x - hr.left);
    float cross = is_vertical() ? ((float)x - hr.left) : ((float)y - hr.top);
    float cross_size = is_vertical() ? (hr.right - hr.left) : (hr.bottom - hr.top);
    float add_start = (float)style.pad_left + view + 4.0f;
    if ((addable || editable) && axis >= add_start && axis < add_start + 28.0f) {
        if (part) *part = 3;
        return -1;
    }
    if (tab_items.empty() || axis < style.pad_left || axis >= style.pad_left + view) return -1;
    float local = axis - (float)style.pad_left + (float)scroll_offset;
    int idx = (int)(local / tab_extent());
    if (idx < 0 || idx >= (int)tab_items.size()) return -1;
    float tab_start = (float)style.pad_left - (float)scroll_offset + tab_extent() * (float)idx;
    float close_start = tab_start + tab_extent() - 26.0f;
    if (item_close_enabled(idx) && axis >= close_start && axis <= tab_start + tab_extent() - 8.0f &&
        cross >= 6.0f && cross <= cross_size - 6.0f) {
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
    D2D1_RECT_F hr = header_rect();
    D2D1_RECT_F cr = content_rect();
    bool vertical = is_vertical();
    float tab_e = tab_extent();
    float view_e = tabs_view_extent();

    D2D1_RECT_F full = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(full);

    if (content_visible) {
        Color content_bg = dark ? 0xFF202437 : 0xFFFFFFFF;
        if (tab_type == 2) {
            ctx.rt->FillRoundedRectangle(ROUNDED(full, 6.0f, 6.0f), ctx.get_brush(content_bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), 6.0f, 6.0f),
                                         ctx.get_brush(border), 1.0f);
        } else {
            ctx.rt->FillRectangle(cr, ctx.get_brush(dark ? 0xFF242941 : 0xFFF8FAFC));
        }
    }

    if (tab_type == 0) {
        if (vertical) {
            float x = tab_position == 1 ? hr.left : hr.right - 1.0f;
            ctx.rt->DrawLine(D2D1::Point2F(x, hr.top + style.pad_left),
                             D2D1::Point2F(x, hr.bottom - style.pad_right),
                             ctx.get_brush(border), 1.0f);
        } else {
            float y = tab_position == 2 ? hr.top : hr.bottom - 1.0f;
            ctx.rt->DrawLine(D2D1::Point2F(hr.left + style.pad_left, y),
                             D2D1::Point2F(hr.right - style.pad_right, y),
                             ctx.get_brush(border), 1.0f);
        }
    }

    D2D1_RECT_F tab_clip = vertical
        ? D2D1::RectF(hr.left, hr.top + style.pad_left, hr.right, hr.top + style.pad_left + view_e)
        : D2D1::RectF(hr.left + style.pad_left, hr.top, hr.left + style.pad_left + view_e, hr.bottom);
    ctx.push_clip(tab_clip);
    for (int i = 0; i < (int)tab_items.size(); ++i) {
        float start = (float)style.pad_left - (float)scroll_offset + tab_e * (float)i;
        if (start + tab_e < style.pad_left || start > style.pad_left + view_e) continue;
        bool is_active = i == active_index;
        bool hot = i == m_hover_index;
        bool close_hot = hot && m_hover_part == 2;
        bool disabled = tab_items[i].disabled;
        D2D1_RECT_F r = vertical
            ? D2D1::RectF(hr.left + 3.0f, hr.top + start + 2.0f, hr.right - 3.0f, hr.top + start + tab_e - 2.0f)
            : D2D1::RectF(hr.left + start + 1.0f, hr.top + 2.0f, hr.left + start + tab_e - 2.0f, hr.bottom - 2.0f);
        if (tab_type == 1 || tab_type == 2) {
            Color bg = is_active ? (dark ? 0xFF313244 : 0xFFFFFFFF) : (hot && !disabled ? t->button_hover : 0);
            if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(r, 4.0f, 4.0f), ctx.get_brush(bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(r, 4.0f, 4.0f),
                                         ctx.get_brush(is_active ? active : border), 1.0f);
        } else if (hot && !is_active && !disabled) {
            ctx.rt->FillRoundedRectangle(ROUNDED(r, 4.0f, 4.0f), ctx.get_brush(t->button_hover));
        }

        float close_e = item_close_enabled(i) ? 24.0f : 0.0f;
        std::wstring title = tab_items[i].icon.empty() ? tab_items[i].label : (tab_items[i].icon + L" " + tab_items[i].label);
        Color text_color = disabled ? t->text_muted : (is_active ? active : fg);
        DWRITE_TEXT_ALIGNMENT title_align = DWRITE_TEXT_ALIGNMENT_LEADING;
        if (header_align == 1) title_align = DWRITE_TEXT_ALIGNMENT_CENTER;
        else if (header_align == 2) title_align = DWRITE_TEXT_ALIGNMENT_TRAILING;
        draw_text(ctx, title, style, text_color,
                  r.left + 8.0f, r.top, r.right - r.left - 14.0f - close_e, r.bottom - r.top,
                  title_align);
        if (item_close_enabled(i)) {
            D2D1_RECT_F xr = D2D1::RectF(r.right - 25.0f, r.top + 7.0f, r.right - 7.0f, r.bottom - 7.0f);
            if (close_hot) {
                ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((xr.left + xr.right) * 0.5f, (xr.top + xr.bottom) * 0.5f), 9.0f, 9.0f),
                                    ctx.get_brush(t->button_hover));
            }
            draw_text(ctx, L"x", style, close_hot ? active : t->text_secondary, xr.left, xr.top, xr.right - xr.left, xr.bottom - xr.top);
        }
        if (tab_type == 0 && is_active) {
            if (vertical) {
                float x = tab_position == 1 ? r.left + 1.5f : r.right - 1.5f;
                ctx.rt->DrawLine(D2D1::Point2F(x, r.top + 6.0f), D2D1::Point2F(x, r.bottom - 6.0f), ctx.get_brush(active), 2.0f);
            } else {
                float y = tab_position == 2 ? r.top + 1.5f : r.bottom - 1.5f;
                ctx.rt->DrawLine(D2D1::Point2F(r.left + 7.0f, y), D2D1::Point2F(r.right - 7.0f, y), ctx.get_brush(active), 2.0f);
            }
        }
    }
    ctx.pop_clip();

    if (max_scroll_offset > 0) {
        Color hint = t->text_secondary;
        if (vertical) {
            if (scroll_offset > 0) draw_text(ctx, L"^", style, hint, hr.left, hr.top, hr.right - hr.left, 18.0f);
            if (scroll_offset < max_scroll_offset) draw_text(ctx, L"v", style, hint, hr.left, hr.bottom - 18.0f, hr.right - hr.left, 18.0f);
        } else {
            if (scroll_offset > 0) draw_text(ctx, L"<", style, hint, hr.left, hr.top, 18.0f, hr.bottom - hr.top);
            if (scroll_offset < max_scroll_offset) draw_text(ctx, L">", style, hint, hr.left + style.pad_left + view_e - 18.0f, hr.top, 18.0f, hr.bottom - hr.top);
        }
    }
    if (addable || editable) {
        float start = (float)style.pad_left + view_e + 4.0f;
        D2D1_RECT_F ar = vertical
            ? D2D1::RectF(hr.left + 8.0f, hr.top + start + 5.0f, hr.right - 8.0f, hr.top + start + 33.0f)
            : D2D1::RectF(hr.left + start, hr.top + 6.0f, hr.left + start + 28.0f, hr.bottom - 6.0f);
        Color bg = m_hover_part == 3 ? t->button_hover : (tab_type == 0 ? 0 : (dark ? 0xFF313244 : 0xFFFFFFFF));
        if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(ar, 4.0f, 4.0f), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(ar, 4.0f, 4.0f), ctx.get_brush(border), 1.0f);
        draw_text(ctx, L"+", style, m_hover_part == 3 ? active : fg, ar.left, ar.top, ar.right - ar.left, ar.bottom - ar.top);
    }

    if (content_visible && cr.right > cr.left && cr.bottom > cr.top) {
        D2D1_RECT_F inner = D2D1::RectF(cr.left + 18.0f, cr.top + 18.0f, cr.right - 18.0f, cr.bottom - 18.0f);
        std::wstring content = item_content(active_index);
        if (content.empty()) content = L"📄 当前标签暂无内容";
        draw_wrapped_text(ctx, content, style, t->text_primary, inner.left, inner.top, inner.right - inner.left, inner.bottom - inner.top);
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
        add_tab(L"✨ 新标签");
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
    int prev_key = is_vertical() ? VK_UP : VK_LEFT;
    int next_key = is_vertical() ? VK_DOWN : VK_RIGHT;
    if (vk == prev_key) select_index(active_index - 1, 3);
    else if (vk == next_key) select_index(active_index + 1, 3);
    else if (vk == VK_HOME) select_index(0, 3);
    else if (vk == VK_END) select_index((int)tab_items.size() - 1, 3);
    else if (vk == VK_PRIOR) scroll_delta(-96);
    else if (vk == VK_NEXT) scroll_delta(96);
    else if ((vk == VK_DELETE || vk == VK_BACK) && active_index >= 0) close_tab(active_index);
    else if ((vk == VK_INSERT || vk == VK_OEM_PLUS) && (addable || editable)) add_tab(L"✨ 新标签");
}
