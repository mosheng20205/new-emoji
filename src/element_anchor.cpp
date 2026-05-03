#include "element_anchor.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

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

int Anchor::row_height() const {
    int h = round_px(style.font_size * 2.0f);
    return h < 30 ? 30 : h;
}

void Anchor::set_items(const std::vector<std::wstring>& values) {
    items = values;
    if ((int)target_positions.size() != (int)items.size()) {
        target_positions.clear();
        for (int i = 0; i < (int)items.size(); ++i) target_positions.push_back(i * 360);
    }
    set_active_index(active_index);
}

void Anchor::set_active_index(int index) {
    if (items.empty()) {
        active_index = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)items.size()) index = (int)items.size() - 1;
        active_index = index;
        last_target_position = target_position_for(active_index);
    }
    invalidate();
}

void Anchor::set_targets(const std::vector<int>& positions) {
    target_positions = positions;
    if ((int)target_positions.size() < (int)items.size()) {
        int start = target_positions.empty() ? 0 : target_positions.back() + 360;
        while ((int)target_positions.size() < (int)items.size()) {
            target_positions.push_back(start);
            start += 360;
        }
    }
    set_scroll_position(scroll_position);
    invalidate();
}

void Anchor::set_options(int scroll_offset, int target_container_id) {
    offset = scroll_offset < 0 ? 0 : scroll_offset;
    container_id = target_container_id < 0 ? 0 : target_container_id;
    set_scroll_position(scroll_position);
}

void Anchor::set_scroll_position(int position) {
    scroll_position = position < 0 ? 0 : position;
    if (items.empty()) {
        active_index = -1;
        last_target_position = 0;
    } else {
        int next_active = 0;
        int probe = scroll_position + offset;
        for (int i = 0; i < (int)items.size(); ++i) {
            int target = i < (int)target_positions.size() ? target_positions[i] : i * 360;
            if (target <= probe) next_active = i;
        }
        active_index = next_active;
        last_target_position = target_position_for(active_index);
    }
    invalidate();
}

int Anchor::item_count() const {
    return (int)items.size();
}

int Anchor::hover_index() const {
    return m_hover_index;
}

int Anchor::target_position_for(int index) const {
    if (index < 0 || index >= (int)items.size()) return 0;
    int target = index < (int)target_positions.size() ? target_positions[index] : index * 360;
    target -= offset;
    return target < 0 ? 0 : target;
}

int Anchor::item_at(int x, int y) const {
    if (x < 0 || y < style.pad_top || x >= bounds.w || y >= bounds.h - style.pad_bottom) return -1;
    int idx = (y - style.pad_top) / row_height();
    return idx >= 0 && idx < (int)items.size() ? idx : -1;
}

void Anchor::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    Color border = style.border_color ? style.border_color : t->border_default;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float rail_x = (float)style.pad_left + 4.0f;
    ctx.rt->DrawLine(D2D1::Point2F(rail_x, (float)style.pad_top),
                     D2D1::Point2F(rail_x, (float)bounds.h - style.pad_bottom),
                     ctx.get_brush(border), 1.0f);

    int rh = row_height();
    for (int i = 0; i < (int)items.size(); ++i) {
        float y = (float)(style.pad_top + i * rh);
        bool active = i == active_index;
        bool hot = i == m_hover_index;
        if (active || hot) {
            D2D1_RECT_F row = { rail_x + 8.0f, y + 2.0f,
                                (float)bounds.w - style.pad_right, y + (float)rh - 2.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
                ctx.get_brush(active ? (t->accent & 0x33FFFFFF) : t->button_hover));
        }
        if (active) {
            ctx.rt->DrawLine(D2D1::Point2F(rail_x, y + 6.0f),
                             D2D1::Point2F(rail_x, y + (float)rh - 6.0f),
                             ctx.get_brush(t->accent), 3.0f);
        }
        draw_text(ctx, items[i], style, active ? t->accent : fg,
                  rail_x + 16.0f, y, (float)bounds.w - rail_x - 18.0f - style.pad_right, (float)rh);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Anchor::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Anchor::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Anchor::on_mouse_down(int x, int y, MouseButton) {
    m_press_index = item_at(x, y);
    pressed = true;
    invalidate();
}

void Anchor::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (idx >= 0 && idx == m_press_index) set_active_index(idx);
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Anchor::on_key_down(int vk, int) {
    if (vk == VK_UP) set_active_index(active_index - 1);
    else if (vk == VK_DOWN) set_active_index(active_index + 1);
    else if (vk == VK_HOME) set_active_index(0);
    else if (vk == VK_END) set_active_index((int)items.size() - 1);
}
