#include "element_segmented.h"
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

void Segmented::set_items(const std::vector<std::wstring>& values) {
    items = values;
    disabled_items.assign(items.size(), false);
    set_active_index(active_index);
}

void Segmented::set_active_index(int index) {
    if (items.empty()) {
        active_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)items.size()) index = (int)items.size() - 1;
        if (is_disabled(index)) {
            int next = -1;
            for (int i = index + 1; i < (int)items.size(); ++i) {
                if (!is_disabled(i)) { next = i; break; }
            }
            for (int i = index - 1; next < 0 && i >= 0; --i) {
                if (!is_disabled(i)) { next = i; break; }
            }
            active_index = next;
        } else {
            active_index = index;
        }
    }
    invalidate();
}

int Segmented::item_count() const {
    return (int)items.size();
}

void Segmented::set_disabled_indices(const std::vector<int>& indices) {
    disabled_items.assign(items.size(), false);
    for (int index : indices) {
        if (index >= 0 && index < (int)disabled_items.size()) disabled_items[index] = true;
    }
    if (active_index >= 0 && is_disabled(active_index)) set_active_index(active_index);
    invalidate();
}

int Segmented::disabled_count() const {
    int count = 0;
    for (bool disabled : disabled_items) {
        if (disabled) ++count;
    }
    return count;
}

int Segmented::hover_index() const {
    return m_hover_index;
}

bool Segmented::is_disabled(int index) const {
    return index < 0 || index >= (int)disabled_items.size() || disabled_items[index];
}

float Segmented::segment_width() const {
    if (items.empty()) return 0.0f;
    float w = (float)bounds.w - style.pad_left - style.pad_right;
    return w > 0.0f ? w / (float)items.size() : 0.0f;
}

int Segmented::segment_at(int x, int y) const {
    if (items.empty() || y < style.pad_top || y >= bounds.h - style.pad_bottom ||
        x < style.pad_left || x >= bounds.w - style.pad_right) return -1;
    float sw = segment_width();
    if (sw <= 0.0f) return -1;
    int idx = (int)(((float)x - style.pad_left) / sw);
    return idx >= 0 && idx < (int)items.size() ? idx : -1;
}

void Segmented::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color frame_bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFE9ECF2);
    Color selected_bg = dark ? 0xFF313244 : 0xFFFFFFFF;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F frame = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(frame, radius, radius), ctx.get_brush(frame_bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float sw = segment_width();
    float top = (float)style.pad_top;
    float h = (float)bounds.h - style.pad_top - style.pad_bottom;
    for (int i = 0; i < (int)items.size(); ++i) {
        float x = (float)style.pad_left + sw * (float)i;
        bool active = i == active_index;
        bool hot = i == m_hover_index;
        bool disabled = is_disabled(i);
        if (!disabled && (active || hot)) {
            D2D1_RECT_F r = { x + 3.0f, top + 3.0f, x + sw - 3.0f, top + h - 3.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(r, radius - 2.0f, radius - 2.0f),
                ctx.get_brush(active ? selected_bg : t->button_hover));
            if (active) {
                ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(r.left + 0.5f, r.top + 0.5f,
                    r.right - 0.5f, r.bottom - 0.5f), radius - 2.0f, radius - 2.0f),
                    ctx.get_brush(t->accent), 1.0f);
            }
        }
        draw_text(ctx, items[i], style, disabled ? t->text_secondary : (active ? t->accent : fg),
                  x + 4.0f, top, sw - 8.0f, h);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Segmented::on_mouse_move(int x, int y) {
    int idx = segment_at(x, y);
    if (is_disabled(idx)) idx = -1;
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Segmented::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Segmented::on_mouse_down(int x, int y, MouseButton) {
    m_press_index = segment_at(x, y);
    if (is_disabled(m_press_index)) m_press_index = -1;
    pressed = true;
    invalidate();
}

void Segmented::on_mouse_up(int x, int y, MouseButton) {
    int idx = segment_at(x, y);
    if (idx >= 0 && idx == m_press_index && !is_disabled(idx)) set_active_index(idx);
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Segmented::on_key_down(int vk, int) {
    if (vk == VK_LEFT) {
        for (int i = active_index - 1; i >= 0; --i) {
            if (!is_disabled(i)) { set_active_index(i); break; }
        }
    } else if (vk == VK_RIGHT) {
        for (int i = active_index + 1; i < (int)items.size(); ++i) {
            if (!is_disabled(i)) { set_active_index(i); break; }
        }
    } else if (vk == VK_HOME) {
        for (int i = 0; i < (int)items.size(); ++i) {
            if (!is_disabled(i)) { set_active_index(i); break; }
        }
    } else if (vk == VK_END) {
        for (int i = (int)items.size() - 1; i >= 0; --i) {
            if (!is_disabled(i)) { set_active_index(i); break; }
        }
    }
}
