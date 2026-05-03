#include "element_radio.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>

static void draw_label(RenderContext& ctx, const Theme* theme, const ElementStyle& style,
                       const std::wstring& text, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(style.fg_color ? style.fg_color : theme->text_primary),
        D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Radio::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    if (style.bg_color) {
        D2D1_RECT_F bg = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(bg, ctx.get_brush(style.bg_color));
    }

    float box = style.font_size * 1.0f;
    box = (std::max)(14.0f, (std::min)(18.0f, box));
    float max_box_h = (float)bounds.h - (float)style.pad_top - (float)style.pad_bottom;
    if (max_box_h > 0.0f) box = (std::min)(box, max_box_h);
    if (box < 12.0f) box = 12.0f;

    float bx = (float)style.pad_left;
    float by = ((float)bounds.h - box) * 0.5f;
    if (by < (float)style.pad_top) by = (float)style.pad_top;

    Color border = checked ? t->accent : (style.border_color ? style.border_color : t->border_default);
    if (!checked && (hovered || pressed)) border = t->accent;
    Color fill = t->panel_bg;
    if (!enabled) {
        border = t->border_default;
        fill = t->button_bg;
    }

    D2D1_ELLIPSE outer = D2D1::Ellipse(
        D2D1::Point2F(bx + box * 0.5f, by + box * 0.5f), box * 0.5f, box * 0.5f);
    ctx.rt->FillEllipse(outer, ctx.get_brush(fill));
    ctx.rt->DrawEllipse(outer, ctx.get_brush(border), 1.0f);
    if (has_focus) {
        D2D1_ELLIPSE focus = D2D1::Ellipse(
            D2D1::Point2F(bx + box * 0.5f, by + box * 0.5f), box * 0.5f + 3.0f, box * 0.5f + 3.0f);
        ctx.rt->DrawEllipse(focus, ctx.get_brush(t->accent), 1.0f);
    }
    if (checked) {
        D2D1_ELLIPSE inner = D2D1::Ellipse(
            D2D1::Point2F(bx + box * 0.5f, by + box * 0.5f), box * 0.25f, box * 0.25f);
        ctx.rt->FillEllipse(inner, ctx.get_brush(t->accent));
    }

    float label_x = bx + box + 8.0f;
    float label_w = (float)bounds.w - label_x - (float)style.pad_right;
    ElementStyle label_style = style;
    if (!enabled && !label_style.fg_color) label_style.fg_color = t->text_muted;
    draw_label(ctx, t, label_style, text, label_x, (float)style.pad_top, label_w,
               (float)bounds.h - (float)style.pad_top - (float)style.pad_bottom);

    ctx.rt->SetTransform(saved);
}

void Radio::on_mouse_down(int, int, MouseButton) {
    if (!enabled) return;
    pressed = true;
    invalidate();
}

void Radio::on_mouse_up(int, int, MouseButton) {
    if (pressed && enabled) {
        set_checked(true);
    }
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

void Radio::set_checked(bool value) {
    if (value && parent) {
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
    checked = value;
    invalidate();
}

void Radio::set_group_name(const std::wstring& value) {
    group_name = value;
    if (checked) set_checked(true);
    else invalidate();
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
