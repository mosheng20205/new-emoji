#include "element_radio.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>
#include <cmath>

#define ROUNDED_RECT(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color radio_with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color radio_mix_color(Color a, Color b, float t) {
    if (t <= 0.0f) return a;
    if (t >= 1.0f) return b;
    auto mix = [t](unsigned ca, unsigned cb) -> unsigned {
        return (unsigned)std::lround((float)ca + ((float)cb - (float)ca) * t);
    };
    unsigned aa = (a >> 24) & 0xFF;
    unsigned ar = (a >> 16) & 0xFF;
    unsigned ag = (a >> 8) & 0xFF;
    unsigned ab = a & 0xFF;
    unsigned ba = (b >> 24) & 0xFF;
    unsigned br = (b >> 16) & 0xFF;
    unsigned bg = (b >> 8) & 0xFF;
    unsigned bb = b & 0xFF;
    return (mix(aa, ba) << 24) | (mix(ar, br) << 16) | (mix(ag, bg) << 8) | mix(ab, bb);
}

static void radio_size_metrics(int size, float base_font, float& font_size,
                               float& circle, float& pad_x, float& item_h) {
    float scale = base_font > 0.0f ? base_font / 14.0f : 1.0f;
    if (size == 1) {
        font_size = 14.0f * scale;
        circle = 16.0f * scale;
        pad_x = 14.0f * scale;
        item_h = 36.0f * scale;
    } else if (size == 2) {
        font_size = 13.0f * scale;
        circle = 14.0f * scale;
        pad_x = 12.0f * scale;
        item_h = 32.0f * scale;
    } else if (size == 3) {
        font_size = 12.0f * scale;
        circle = 13.0f * scale;
        pad_x = 10.0f * scale;
        item_h = 28.0f * scale;
    } else {
        font_size = base_font > 0.0f ? base_font : 14.0f;
        circle = 16.0f * scale;
        pad_x = 14.0f * scale;
        item_h = 40.0f * scale;
    }
    if (circle < 12.0f) circle = 12.0f;
    if (pad_x < 6.0f) pad_x = 6.0f;
    if (item_h < 24.0f) item_h = 24.0f;
}

static void draw_radio_text(RenderContext& ctx, const std::wstring& text,
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

static void draw_radio_mark(RenderContext& ctx, const Theme* t, float cx, float cy,
                            float box, bool checked, bool hot, bool disabled) {
    Color border = checked ? t->accent : t->border_default;
    if (!checked && hot && !disabled) border = t->accent;
    Color fill = disabled ? t->button_bg : t->panel_bg;
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), box * 0.5f, box * 0.5f),
                        ctx.get_brush(fill));
    ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), box * 0.5f, box * 0.5f),
                        ctx.get_brush(border), 1.0f);
    if (checked) {
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), box * 0.25f, box * 0.25f),
                            ctx.get_brush(disabled ? t->text_muted : t->accent));
    }
}

void Radio::paint(RenderContext& ctx) {
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
    radio_size_metrics(size, style.font_size, font_size, box, pad_x, item_h);

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
        Color border_color = checked ? t->accent : t->border_default;
        Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
        if (hot && enabled) bg = radio_with_alpha(t->accent, dark ? 0x24 : 0x12);
        if (!enabled) bg = dark ? 0xFF242637 : 0xFFF3F4F6;
        D2D1_RECT_F r = { 0.5f, top + 0.5f, (float)bounds.w - 0.5f, top + content_h - 0.5f };
        ctx.rt->FillRoundedRectangle(ROUNDED_RECT(r, 6.0f, 6.0f), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED_RECT(r, 6.0f, 6.0f), ctx.get_brush(border_color), 1.0f);
        left = pad_x;
        right = (float)bounds.w - pad_x;
    }

    float cx = left + box * 0.5f;
    float cy = top + content_h * 0.5f;
    draw_radio_mark(ctx, t, cx, cy, box, checked, hot, !enabled);
    if (has_focus && enabled) {
        ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(cx, cy), box * 0.5f + 3.0f, box * 0.5f + 3.0f),
                            ctx.get_brush(t->accent), 1.0f);
    }

    float label_x = cx + box * 0.5f + 8.0f;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    if (!enabled) fg = t->text_muted;
    else if (checked) fg = t->accent;
    draw_radio_text(ctx, text, style, font_size, fg, label_x, top, right - label_x, content_h);

    ctx.rt->SetTransform(saved);
}

void Radio::on_mouse_down(int, int, MouseButton) {
    if (!enabled) return;
    pressed = true;
    invalidate();
}

void Radio::on_mouse_up(int, int, MouseButton) {
    if (pressed && enabled) set_checked(true);
    pressed = false;
}

void Radio::on_key_down(int vk, int) {
    if (!enabled) return;
    if (vk == VK_SPACE || vk == VK_RETURN) {
        key_armed = true;
        pressed = true;
        invalidate();
    } else if (vk == VK_LEFT || vk == VK_UP) {
        select_relative(-1);
    } else if (vk == VK_RIGHT || vk == VK_DOWN) {
        select_relative(1);
    }
}

void Radio::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = enabled && key_armed;
        if (should_click) set_checked(true);
        key_armed = false;
        pressed = false;
        invalidate();
        if (should_click && click_cb) click_cb(id);
    }
}

void Radio::set_checked(bool next_value) {
    if (next_value && parent) {
        for (auto& sibling : parent->children) {
            if (sibling.get() == this) continue;
            auto* radio = dynamic_cast<Radio*>(sibling.get());
            if (radio && radio->checked &&
                (group_name.empty() || radio->group_name == group_name)) {
                radio->checked = false;
                radio->invalidate();
            }
        }
    }
    checked = next_value;
    invalidate();
}

void Radio::set_group_name(const std::wstring& next_value) {
    group_name = next_value;
    if (checked) set_checked(true);
    else invalidate();
}

void Radio::set_value(const std::wstring& next_value) {
    value = next_value;
    invalidate();
}

void Radio::set_options(bool border_value, int size_value) {
    border = border_value;
    if (size_value < 0) size_value = 0;
    if (size_value > 3) size_value = 3;
    size = size_value;
    invalidate();
}

void Radio::select_relative(int delta) {
    if (!parent || delta == 0) return;
    std::vector<Radio*> group;
    int current = -1;
    for (auto& sibling : parent->children) {
        auto* radio = dynamic_cast<Radio*>(sibling.get());
        if (!radio || !radio->enabled) continue;
        if (!group_name.empty() && radio->group_name != group_name) continue;
        if (group_name.empty() && !radio->group_name.empty()) continue;
        if (radio == this) current = (int)group.size();
        group.push_back(radio);
    }
    if (group.empty() || current < 0) return;
    int next = (current + delta + (int)group.size()) % (int)group.size();
    group[next]->set_checked(true);
    if (group[next]->click_cb) group[next]->click_cb(group[next]->id);
}

void RadioGroup::set_items(const std::vector<RadioGroupItem>& next_items) {
    items = next_items;
    if (!items.empty()) {
        for (auto& item : items) {
            if (item.value.empty()) item.value = item.text;
        }
    }
    if (selected_index < 0 || selected_index >= (int)items.size() ||
        is_item_disabled(selected_index)) {
        selected_index = next_enabled_index(-1, 1);
    }
    last_action = 4;
    invalidate();
}

void RadioGroup::set_value(const std::wstring& value) {
    for (int i = 0; i < (int)items.size(); ++i) {
        if (items[(size_t)i].value == value && !is_item_disabled(i)) {
            select_index(i, 1);
            return;
        }
    }
    invalidate();
}

std::wstring RadioGroup::selected_value() const {
    if (selected_index < 0 || selected_index >= (int)items.size()) return L"";
    return items[(size_t)selected_index].value;
}

void RadioGroup::set_options(bool disabled_value, int style_value, int size_value) {
    group_disabled = disabled_value;
    if (style_value < 0) style_value = 0;
    if (style_value > 2) style_value = 2;
    style_mode = style_value;
    if (size_value < 0) size_value = 0;
    if (size_value > 3) size_value = 3;
    size = size_value;
    invalidate();
}

int RadioGroup::item_count() const {
    return (int)items.size();
}

int RadioGroup::disabled_count() const {
    int count = group_disabled ? item_count() : 0;
    if (!group_disabled) {
        for (const auto& item : items) {
            if (item.disabled) ++count;
        }
    }
    return count;
}

int RadioGroup::hover_index() const {
    return m_hover_index;
}

int RadioGroup::press_index() const {
    return m_press_index;
}

bool RadioGroup::is_item_disabled(int index) const {
    return group_disabled || index < 0 || index >= (int)items.size() ||
           items[(size_t)index].disabled;
}

int RadioGroup::next_enabled_index(int from, int delta) const {
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

int RadioGroup::item_at(int x, int y) const {
    if (items.empty() || x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    float font_size = style.font_size;
    float circle = 16.0f;
    float pad_x = 12.0f;
    float item_h = 36.0f;
    radio_size_metrics(size, style.font_size, font_size, circle, pad_x, item_h);
    float inner_x = (float)style.pad_left;
    float inner_y = (float)style.pad_top;
    float inner_w = (float)bounds.w - style.pad_left - style.pad_right;
    float inner_h = (float)bounds.h - style.pad_top - style.pad_bottom;
    if (inner_w <= 0.0f || inner_h <= 0.0f ||
        x < inner_x || x >= inner_x + inner_w || y < inner_y || y >= inner_y + inner_h) {
        return -1;
    }
    if (style_mode == 0) {
        float item_w = inner_w / (float)items.size();
        int idx = (int)(((float)x - inner_x) / item_w);
        return idx >= 0 && idx < (int)items.size() ? idx : -1;
    }
    float item_w = inner_w / (float)items.size();
    int idx = (int)(((float)x - inner_x) / item_w);
    return idx >= 0 && idx < (int)items.size() ? idx : -1;
}

void RadioGroup::select_index(int index, int action) {
    if (is_item_disabled(index)) return;
    bool changed = selected_index != index;
    selected_index = index;
    last_action = action;
    if (changed && change_cb) change_cb(id, selected_index, item_count(), last_action);
    invalidate();
}

void RadioGroup::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float font_size = style.font_size;
    float circle = 16.0f;
    float pad_x = 12.0f;
    float item_h = 36.0f;
    radio_size_metrics(size, style.font_size, font_size, circle, pad_x, item_h);
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
    Color button_hover = radio_with_alpha(t->accent, dark ? 0x26 : 0x14);

    for (int i = 0; i < (int)items.size(); ++i) {
        const auto& item = items[(size_t)i];
        float x = x0 + item_w * (float)i;
        bool selected = i == selected_index;
        bool hot = i == m_hover_index;
        bool down = i == m_press_index;
        bool disabled = is_item_disabled(i);
        Color fg = style.fg_color ? style.fg_color : t->text_primary;
        if (disabled) fg = t->text_muted;
        else if (selected) fg = t->accent;

        if (style_mode == 1) {
            D2D1_RECT_F r = { x + 0.5f, top + 0.5f, x + item_w + 0.5f, top + h - 0.5f };
            if (i == (int)items.size() - 1) r.right = x0 + w0 - 0.5f;
            Color bg = selected ? t->accent : button_bg;
            Color border = selected ? t->accent : t->border_default;
            if (hot && !disabled && !selected) bg = button_hover;
            if (down && !disabled && !selected) bg = radio_with_alpha(t->accent, dark ? 0x38 : 0x20);
            if (disabled) bg = dark ? 0xFF242637 : 0xFFF3F4F6;
            if (selected && !disabled) fg = 0xFFFFFFFF;
            ctx.rt->FillRectangle(r, ctx.get_brush(bg));
            ctx.rt->DrawRectangle(r, ctx.get_brush(border), 1.0f);
            draw_radio_text(ctx, item.text, style, font_size, fg, r.left + 8.0f, r.top,
                            r.right - r.left - 16.0f, r.bottom - r.top,
                            DWRITE_TEXT_ALIGNMENT_CENTER);
        } else {
            bool bordered = style_mode == 2;
            float mark_x = x + (bordered ? pad_x : 0.0f) + circle * 0.5f;
            float mark_y = top + h * 0.5f;
            float text_x = mark_x + circle * 0.5f + 8.0f;
            if (bordered) {
                D2D1_RECT_F r = { x + 2.0f, top + 0.5f, x + item_w - 4.0f, top + h - 0.5f };
                Color border = selected ? t->accent : t->border_default;
                Color bg = button_bg;
                if (hot && !disabled) bg = button_hover;
                if (disabled) bg = dark ? 0xFF242637 : 0xFFF3F4F6;
                ctx.rt->FillRoundedRectangle(ROUNDED_RECT(r, 6.0f, 6.0f), ctx.get_brush(bg));
                ctx.rt->DrawRoundedRectangle(ROUNDED_RECT(r, 6.0f, 6.0f), ctx.get_brush(border), 1.0f);
            }
            draw_radio_mark(ctx, t, mark_x, mark_y, circle, selected, hot, disabled);
            draw_radio_text(ctx, item.text, style, font_size, fg, text_x, top,
                            x + item_w - text_x - 6.0f, h);
        }
    }

    ctx.rt->SetTransform(saved);
}

void RadioGroup::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (is_item_disabled(idx)) idx = -1;
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void RadioGroup::on_mouse_leave() {
    hovered = false;
    pressed = false;
    suppress_click = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void RadioGroup::on_mouse_down(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    suppress_click = is_item_disabled(idx);
    m_press_index = suppress_click ? -1 : idx;
    pressed = m_press_index >= 0;
    invalidate();
}

void RadioGroup::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (!suppress_click && idx >= 0 && idx == m_press_index && !is_item_disabled(idx)) {
        select_index(idx, 2);
    }
    m_press_index = -1;
    pressed = false;
    suppress_click = false;
    invalidate();
}

void RadioGroup::on_key_down(int vk, int) {
    if (!enabled || group_disabled) return;
    if (vk == VK_LEFT || vk == VK_UP) {
        int next = next_enabled_index(selected_index, -1);
        if (next >= 0) select_index(next, 3);
    } else if (vk == VK_RIGHT || vk == VK_DOWN) {
        int next = next_enabled_index(selected_index, 1);
        if (next >= 0) select_index(next, 3);
    } else if (vk == VK_HOME) {
        int next = next_enabled_index(-1, 1);
        if (next >= 0) select_index(next, 3);
    } else if (vk == VK_END) {
        int next = next_enabled_index((int)items.size(), -1);
        if (next >= 0) select_index(next, 3);
    } else if (vk == VK_SPACE || vk == VK_RETURN) {
        m_key_armed = true;
        pressed = true;
        invalidate();
    }
}

void RadioGroup::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = enabled && !group_disabled && m_key_armed && selected_index >= 0;
        m_key_armed = false;
        pressed = false;
        if (should_click) {
            last_action = 3;
            if (click_cb) click_cb(id);
            if (change_cb) change_cb(id, selected_index, item_count(), last_action);
        }
        invalidate();
    }
}
