#include "element_checkbox.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color checkbox_with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void checkbox_size_metrics(int size, float base_font, float& font_size,
                                  float& box, float& pad_x, float& item_h) {
    float scale = base_font > 0.0f ? base_font / 14.0f : 1.0f;
    if (size == 1) {
        font_size = 14.0f * scale;
        box = 16.0f * scale;
        pad_x = 14.0f * scale;
        item_h = 36.0f * scale;
    } else if (size == 2) {
        font_size = 13.0f * scale;
        box = 14.0f * scale;
        pad_x = 12.0f * scale;
        item_h = 32.0f * scale;
    } else if (size == 3) {
        font_size = 12.0f * scale;
        box = 13.0f * scale;
        pad_x = 10.0f * scale;
        item_h = 28.0f * scale;
    } else {
        font_size = base_font > 0.0f ? base_font : 14.0f;
        box = 16.0f * scale;
        pad_x = 14.0f * scale;
        item_h = 40.0f * scale;
    }
    if (box < 12.0f) box = 12.0f;
    if (pad_x < 6.0f) pad_x = 6.0f;
    if (item_h < 24.0f) item_h = 24.0f;
}

static void draw_checkbox_text(RenderContext& ctx, const std::wstring& text,
                               const ElementStyle& style, float font_size,
                               Color color, float x, float y, float w, float h,
                               DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout, ctx.get_brush(color),
                           D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static void draw_checkbox_mark(RenderContext& ctx, const Theme* t, float x, float y,
                               float box, bool checked, bool indeterminate,
                               bool hot, bool disabled) {
    bool active = checked || indeterminate;
    Color border = active ? t->accent : t->border_default;
    if (!active && hot && !disabled) border = t->accent;
    Color fill = active ? t->accent : t->panel_bg;
    if (disabled) {
        border = t->border_default;
        fill = t->button_bg;
    }

    D2D1_RECT_F rect = { x, y, x + box, y + box };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 3.0f, 3.0f), ctx.get_brush(fill));
    ctx.rt->DrawRoundedRectangle(ROUNDED(rect, 3.0f, 3.0f), ctx.get_brush(border), 1.0f);

    Color mark = disabled ? t->text_muted : 0xFFFFFFFF;
    auto* mark_brush = ctx.get_brush(mark);
    if (checked) {
        ctx.rt->DrawLine(D2D1::Point2F(x + box * 0.24f, y + box * 0.53f),
                         D2D1::Point2F(x + box * 0.42f, y + box * 0.72f),
                         mark_brush, 2.0f);
        ctx.rt->DrawLine(D2D1::Point2F(x + box * 0.42f, y + box * 0.72f),
                         D2D1::Point2F(x + box * 0.78f, y + box * 0.30f),
                         mark_brush, 2.0f);
    } else if (indeterminate) {
        ctx.rt->DrawLine(D2D1::Point2F(x + box * 0.24f, y + box * 0.50f),
                         D2D1::Point2F(x + box * 0.76f, y + box * 0.50f),
                         mark_brush, 2.0f);
    }
}

void Checkbox::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float font_size = style.font_size;
    float box = 16.0f;
    float pad_x = 12.0f;
    float item_h = (float)bounds.h;
    checkbox_size_metrics(size, style.font_size, font_size, box, pad_x, item_h);

    float outer_h = (float)bounds.h;
    float content_h = (std::min)(outer_h, item_h);
    float top = (outer_h - content_h) * 0.5f;
    float left = border ? 0.5f : (float)style.pad_left;
    float right = (float)bounds.w - (border ? 0.5f : (float)style.pad_right);
    bool hot = hovered || pressed || has_focus;

    if (style.bg_color) {
        D2D1_RECT_F bg = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(bg, ctx.get_brush(style.bg_color));
    }

    if (border) {
        Color border_color = (checked || indeterminate) ? t->accent : t->border_default;
        Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
        if (hot && enabled) bg = checkbox_with_alpha(t->accent, dark ? 0x24 : 0x12);
        if (!enabled) bg = dark ? 0xFF242637 : 0xFFF3F4F6;
        D2D1_RECT_F r = { 0.5f, top + 0.5f, (float)bounds.w - 0.5f, top + content_h - 0.5f };
        ctx.rt->FillRoundedRectangle(ROUNDED(r, 6.0f, 6.0f), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(r, 6.0f, 6.0f), ctx.get_brush(border_color), 1.0f);
        left = pad_x;
        right = (float)bounds.w - pad_x;
    }

    float bx = left;
    float by = top + (content_h - box) * 0.5f;
    draw_checkbox_mark(ctx, t, bx, by, box, checked, indeterminate, hot, !enabled);
    if (has_focus && enabled) {
        D2D1_RECT_F focus = { bx - 3.0f, by - 3.0f, bx + box + 3.0f, by + box + 3.0f };
        ctx.rt->DrawRoundedRectangle(ROUNDED(focus, 5.0f, 5.0f), ctx.get_brush(t->accent), 1.0f);
    }

    float label_x = bx + box + 8.0f;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    if (!enabled) fg = t->text_muted;
    else if (checked || indeterminate) fg = t->accent;
    draw_checkbox_text(ctx, text, style, font_size, fg, label_x, top, right - label_x, content_h);

    ctx.rt->SetTransform(saved);
}

void Checkbox::on_mouse_down(int, int, MouseButton) {
    if (!enabled) return;
    pressed = true;
    invalidate();
}

void Checkbox::on_mouse_up(int, int, MouseButton) {
    if (pressed && enabled) {
        toggle();
    }
    pressed = false;
    invalidate();
}

void Checkbox::on_key_down(int vk, int) {
    if (!enabled) return;
    if (vk == VK_SPACE || vk == VK_RETURN) {
        key_armed = true;
        pressed = true;
        invalidate();
    }
}

void Checkbox::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = enabled && key_armed;
        if (should_click) toggle();
        key_armed = false;
        pressed = false;
        invalidate();
        if (should_click && click_cb) click_cb(id);
    }
}

void Checkbox::set_checked(bool value) {
    checked = value;
    if (value) indeterminate = false;
    invalidate();
}

void Checkbox::set_indeterminate(bool value) {
    indeterminate = value;
    if (value) checked = false;
    invalidate();
}

void Checkbox::set_options(bool border_value, int size_value) {
    border = border_value;
    if (size_value < 0) size_value = 0;
    if (size_value > 3) size_value = 3;
    size = size_value;
    invalidate();
}

void Checkbox::toggle() {
    if (indeterminate) {
        indeterminate = false;
        checked = true;
    } else {
        checked = !checked;
    }
    invalidate();
}

void CheckboxGroup::set_items(const std::vector<CheckboxGroupItem>& next_items) {
    std::vector<std::wstring> old_values;
    for (const auto& item : items) {
        if (item.checked) old_values.push_back(item.value.empty() ? item.text : item.value);
    }

    items = next_items;
    for (auto& item : items) {
        if (item.value.empty()) item.value = item.text;
        if (!old_values.empty()) {
            item.checked = std::find(old_values.begin(), old_values.end(), item.value) != old_values.end();
        }
    }
    if (m_focus_index < 0 || m_focus_index >= (int)items.size() || is_item_disabled(m_focus_index)) {
        m_focus_index = next_enabled_index(-1, 1);
    }
    last_action = 4;
    invalidate();
}

void CheckboxGroup::set_checked_values(const std::vector<std::wstring>& values) {
    for (auto& item : items) {
        item.checked = std::find(values.begin(), values.end(), item.value) != values.end();
    }
    last_action = 1;
    invalidate();
}

std::wstring CheckboxGroup::checked_values() const {
    std::wstring result;
    for (const auto& item : items) {
        if (!item.checked) continue;
        if (!result.empty()) result += L"\n";
        result += item.value;
    }
    return result;
}

void CheckboxGroup::set_options(bool disabled_value, int style_value, int size_value,
                                int min_value, int max_value) {
    group_disabled = disabled_value;
    if (style_value < 0) style_value = 0;
    if (style_value > 2) style_value = 2;
    style_mode = style_value;
    if (size_value < 0) size_value = 0;
    if (size_value > 3) size_value = 3;
    size = size_value;
    min_checked = (std::max)(0, min_value);
    max_checked = (std::max)(0, max_value);
    if (max_checked > 0 && min_checked > max_checked) min_checked = max_checked;
    invalidate();
}

int CheckboxGroup::item_count() const {
    return (int)items.size();
}

int CheckboxGroup::checked_count() const {
    int count = 0;
    for (const auto& item : items) {
        if (item.checked) ++count;
    }
    return count;
}

int CheckboxGroup::disabled_count() const {
    int count = group_disabled ? item_count() : 0;
    if (!group_disabled) {
        for (const auto& item : items) {
            if (item.disabled) ++count;
        }
    }
    return count;
}

int CheckboxGroup::hover_index() const { return m_hover_index; }
int CheckboxGroup::press_index() const { return m_press_index; }
int CheckboxGroup::focus_index() const { return m_focus_index; }

bool CheckboxGroup::is_item_disabled(int index) const {
    return group_disabled || index < 0 || index >= (int)items.size() ||
           items[(size_t)index].disabled;
}

bool CheckboxGroup::can_toggle_index(int index) const {
    if (is_item_disabled(index)) return false;
    const auto& item = items[(size_t)index];
    int count = checked_count();
    if (item.checked) return min_checked <= 0 || count > min_checked;
    return max_checked <= 0 || count < max_checked;
}

int CheckboxGroup::next_enabled_index(int from, int delta) const {
    if (items.empty() || delta == 0) return -1;
    int count = (int)items.size();
    int start = from;
    if (start < 0 || start >= count) start = delta > 0 ? -1 : count;
    for (int step = 0; step < count; ++step) {
        int idx = start + delta * (step + 1);
        while (idx < 0) idx += count;
        while (idx >= count) idx -= count;
        if (!is_item_disabled(idx)) return idx;
    }
    return -1;
}

int CheckboxGroup::item_at(int x, int y) const {
    if (items.empty() || x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    float font_size = style.font_size;
    float box = 16.0f;
    float pad_x = 12.0f;
    float item_h = 36.0f;
    checkbox_size_metrics(size, style.font_size, font_size, box, pad_x, item_h);
    float inner_x = (float)style.pad_left;
    float inner_y = (float)style.pad_top;
    float inner_w = (float)bounds.w - style.pad_left - style.pad_right;
    float inner_h = (float)bounds.h - style.pad_top - style.pad_bottom;
    if (inner_w <= 0.0f || inner_h <= 0.0f ||
        x < inner_x || x >= inner_x + inner_w || y < inner_y || y >= inner_y + inner_h) {
        return -1;
    }
    float item_w = inner_w / (float)items.size();
    int idx = (int)(((float)x - inner_x) / item_w);
    return idx >= 0 && idx < (int)items.size() ? idx : -1;
}

void CheckboxGroup::toggle_index(int index, int action) {
    if (!can_toggle_index(index)) return;
    items[(size_t)index].checked = !items[(size_t)index].checked;
    m_focus_index = index;
    last_action = action;
    if (change_cb) change_cb(id, index, checked_count(), last_action);
    invalidate();
}

void CheckboxGroup::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float font_size = style.font_size;
    float box = 16.0f;
    float pad_x = 12.0f;
    float item_h = 36.0f;
    checkbox_size_metrics(size, style.font_size, font_size, box, pad_x, item_h);
    float x0 = (float)style.pad_left;
    float y0 = (float)style.pad_top;
    float w0 = (float)bounds.w - style.pad_left - style.pad_right;
    float h0 = (float)bounds.h - style.pad_top - style.pad_bottom;
    if (w0 <= 0.0f || h0 <= 0.0f || items.empty()) {
        ctx.rt->SetTransform(saved);
        return;
    }

    if (style.bg_color) {
        D2D1_RECT_F bg = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(bg, ctx.get_brush(style.bg_color));
    }

    float item_w = w0 / (float)items.size();
    float top = y0 + (h0 - (std::min)(h0, item_h)) * 0.5f;
    float h = (std::min)(h0, item_h);
    Color button_bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color button_hover = checkbox_with_alpha(t->accent, dark ? 0x26 : 0x14);

    for (int i = 0; i < (int)items.size(); ++i) {
        const auto& item = items[(size_t)i];
        float x = x0 + item_w * (float)i;
        bool hot = i == m_hover_index || i == m_focus_index;
        bool down = i == m_press_index;
        bool disabled = is_item_disabled(i);
        Color fg = style.fg_color ? style.fg_color : t->text_primary;
        if (disabled) fg = t->text_muted;
        else if (item.checked) fg = t->accent;

        if (style_mode == 1) {
            D2D1_RECT_F r = { x + 0.5f, top + 0.5f, x + item_w + 0.5f, top + h - 0.5f };
            if (i == (int)items.size() - 1) r.right = x0 + w0 - 0.5f;
            Color bg = item.checked ? t->accent : button_bg;
            Color border = item.checked ? t->accent : t->border_default;
            if (hot && !disabled && !item.checked) bg = button_hover;
            if (down && !disabled && !item.checked) bg = checkbox_with_alpha(t->accent, dark ? 0x38 : 0x20);
            if (disabled) bg = dark ? 0xFF242637 : 0xFFF3F4F6;
            if (item.checked && !disabled) fg = 0xFFFFFFFF;
            ctx.rt->FillRectangle(r, ctx.get_brush(bg));
            ctx.rt->DrawRectangle(r, ctx.get_brush(border), 1.0f);
            draw_checkbox_text(ctx, item.text, style, font_size, fg, r.left + 8.0f, r.top,
                               r.right - r.left - 16.0f, r.bottom - r.top,
                               DWRITE_TEXT_ALIGNMENT_CENTER);
        } else {
            bool bordered = style_mode == 2;
            float mark_x = x + (bordered ? pad_x : 0.0f);
            float mark_y = top + (h - box) * 0.5f;
            float text_x = mark_x + box + 8.0f;
            if (bordered) {
                D2D1_RECT_F r = { x + 2.0f, top + 0.5f, x + item_w - 4.0f, top + h - 0.5f };
                Color border = item.checked ? t->accent : t->border_default;
                Color bg = button_bg;
                if (hot && !disabled) bg = button_hover;
                if (disabled) bg = dark ? 0xFF242637 : 0xFFF3F4F6;
                ctx.rt->FillRoundedRectangle(ROUNDED(r, 6.0f, 6.0f), ctx.get_brush(bg));
                ctx.rt->DrawRoundedRectangle(ROUNDED(r, 6.0f, 6.0f), ctx.get_brush(border), 1.0f);
            }
            draw_checkbox_mark(ctx, t, mark_x, mark_y, box, item.checked, false, hot, disabled);
            draw_checkbox_text(ctx, item.text, style, font_size, fg, text_x, top,
                               x + item_w - text_x - 6.0f, h);
        }
    }

    ctx.rt->SetTransform(saved);
}

void CheckboxGroup::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (is_item_disabled(idx)) idx = -1;
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void CheckboxGroup::on_mouse_leave() {
    hovered = false;
    pressed = false;
    suppress_click = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void CheckboxGroup::on_mouse_down(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    suppress_click = !can_toggle_index(idx);
    m_press_index = suppress_click ? -1 : idx;
    pressed = m_press_index >= 0;
    invalidate();
}

void CheckboxGroup::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (!suppress_click && idx >= 0 && idx == m_press_index && can_toggle_index(idx)) {
        toggle_index(idx, 2);
    }
    m_press_index = -1;
    pressed = false;
    suppress_click = false;
    invalidate();
}

void CheckboxGroup::on_key_down(int vk, int) {
    if (!enabled || group_disabled) return;
    if (m_focus_index < 0) m_focus_index = next_enabled_index(-1, 1);
    if (vk == VK_LEFT || vk == VK_UP) {
        int next = next_enabled_index(m_focus_index, -1);
        if (next >= 0) {
            m_focus_index = next;
            invalidate();
        }
    } else if (vk == VK_RIGHT || vk == VK_DOWN) {
        int next = next_enabled_index(m_focus_index, 1);
        if (next >= 0) {
            m_focus_index = next;
            invalidate();
        }
    } else if (vk == VK_HOME) {
        int next = next_enabled_index(-1, 1);
        if (next >= 0) {
            m_focus_index = next;
            invalidate();
        }
    } else if (vk == VK_END) {
        int next = next_enabled_index((int)items.size(), -1);
        if (next >= 0) {
            m_focus_index = next;
            invalidate();
        }
    } else if (vk == VK_SPACE || vk == VK_RETURN) {
        m_key_armed = true;
        pressed = true;
        m_press_index = m_focus_index;
        invalidate();
    }
}

void CheckboxGroup::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = enabled && !group_disabled && m_key_armed &&
                            m_focus_index >= 0 && can_toggle_index(m_focus_index);
        m_key_armed = false;
        pressed = false;
        m_press_index = -1;
        if (should_click) {
            toggle_index(m_focus_index, 3);
            if (click_cb) click_cb(id);
        }
        invalidate();
    }
}
