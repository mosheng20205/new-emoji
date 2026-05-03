#include "element_breadcrumb.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

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

void Breadcrumb::set_items(const std::vector<std::wstring>& values) {
    items = values;
    if (current_index < 0 || current_index >= (int)items.size()) current_index = (int)items.size() - 1;
    invalidate();
}

void Breadcrumb::set_separator(const std::wstring& value) {
    separator = value.empty() ? L"/" : value;
    invalidate();
}

void Breadcrumb::set_current_index(int value) {
    activate_index(value, 1);
}

void Breadcrumb::activate_index(int value, int action) {
    if (items.empty()) {
        current_index = -1;
    } else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        current_index = value;
        last_clicked_index = value;
        ++click_count;
        last_action = action;
        if (select_cb) select_cb(id, current_index, click_count, (int)items.size());
    }
    invalidate();
}

Rect Breadcrumb::item_rect(int index) const {
    if (index < 0 || index >= (int)items.size()) return {};
    float x = (float)style.pad_left;
    float sep_w = style.font_size * 1.2f;
    for (int i = 0; i <= index; ++i) {
        float item_w = (std::min)((float)items[i].size() * style.font_size * 0.72f + 12.0f,
                                  (float)bounds.w - x - style.pad_right);
        if (i == index) {
            return { (int)x, 0, (int)item_w, bounds.h };
        }
        x += item_w + sep_w;
    }
    return {};
}

int Breadcrumb::item_at(int x, int y) const {
    if (y < 0 || y >= bounds.h) return -1;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (item_rect(i).contains(x, y)) return i;
    }
    return -1;
}

void Breadcrumb::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color normal = style.fg_color ? style.fg_color : t->text_secondary;
    Color active = t->text_primary;
    Color sep = t->text_muted;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float x = (float)style.pad_left;
    float y = 0.0f;
    float h = (float)bounds.h;
    float sep_w = style.font_size * 1.2f;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (x >= bounds.w - style.pad_right) break;
        float item_w = (std::min)((float)items[i].size() * style.font_size * 0.72f + 8.0f,
                                  (float)bounds.w - x - style.pad_right);
        if (i == m_hover_index && i != current_index) {
            D2D1_RECT_F hover = { x, 4.0f, x + item_w, (float)bounds.h - 4.0f };
            ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ hover, 4.0f, 4.0f },
                                         ctx.get_brush(t->button_hover));
        }
        draw_text(ctx, items[i], style, i == current_index ? active : normal,
                  x, y, item_w, h);
        x += item_w;
        if (i < (int)items.size() - 1) {
            draw_text(ctx, separator, style, sep, x, y, sep_w, h,
                      DWRITE_TEXT_ALIGNMENT_CENTER);
            x += sep_w;
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Breadcrumb::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Breadcrumb::on_mouse_leave() {
    m_hover_index = -1;
    m_press_index = -1;
    hovered = false;
    invalidate();
}

void Breadcrumb::on_mouse_down(int x, int y, MouseButton) {
    m_press_index = item_at(x, y);
    pressed = true;
    invalidate();
}

void Breadcrumb::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (idx >= 0 && idx == m_press_index) activate_index(idx, 2);
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Breadcrumb::on_key_down(int vk, int) {
    if (items.empty()) return;
    if (vk == VK_LEFT || vk == VK_UP) {
        activate_index(current_index - 1, 3);
    } else if (vk == VK_RIGHT || vk == VK_DOWN) {
        activate_index(current_index + 1, 3);
    } else if (vk == VK_HOME) {
        activate_index(0, 3);
    } else if (vk == VK_END) {
        activate_index((int)items.size() - 1, 3);
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        activate_index(current_index, 3);
    }
}
