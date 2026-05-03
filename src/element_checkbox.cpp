#include "element_checkbox.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

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

void Checkbox::paint(RenderContext& ctx) {
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

    float box = style.font_size * 1.05f;
    box = (std::max)(14.0f, (std::min)(18.0f, box));
    float max_box_h = (float)bounds.h - (float)style.pad_top - (float)style.pad_bottom;
    if (max_box_h > 0.0f) box = (std::min)(box, max_box_h);
    if (box < 12.0f) box = 12.0f;

    float bx = (float)style.pad_left;
    float by = ((float)bounds.h - box) * 0.5f;
    if (by < (float)style.pad_top) by = (float)style.pad_top;

    bool active = checked || indeterminate;
    Color border = active ? t->accent : (style.border_color ? style.border_color : t->border_default);
    if (!active && (hovered || pressed)) border = t->accent;
    Color fill = active ? t->accent : t->panel_bg;
    if (!enabled) {
        border = t->border_default;
        fill = t->button_bg;
    }

    D2D1_RECT_F rect = { bx, by, bx + box, by + box };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 3.0f, 3.0f), ctx.get_brush(fill));
    ctx.rt->DrawRoundedRectangle(ROUNDED(rect, 3.0f, 3.0f), ctx.get_brush(border), 1.0f);
    if (has_focus) {
        D2D1_RECT_F focus = { bx - 3.0f, by - 3.0f, bx + box + 3.0f, by + box + 3.0f };
        ctx.rt->DrawRoundedRectangle(ROUNDED(focus, 5.0f, 5.0f), ctx.get_brush(t->accent), 1.0f);
    }

    auto* mark_brush = ctx.get_brush(0xFFFFFFFF);
    if (checked) {
        ctx.rt->DrawLine(
            D2D1::Point2F(bx + box * 0.24f, by + box * 0.53f),
            D2D1::Point2F(bx + box * 0.42f, by + box * 0.72f),
            mark_brush, 2.0f);
        ctx.rt->DrawLine(
            D2D1::Point2F(bx + box * 0.42f, by + box * 0.72f),
            D2D1::Point2F(bx + box * 0.78f, by + box * 0.30f),
            mark_brush, 2.0f);
    } else if (indeterminate) {
        ctx.rt->DrawLine(
            D2D1::Point2F(bx + box * 0.24f, by + box * 0.50f),
            D2D1::Point2F(bx + box * 0.76f, by + box * 0.50f),
            mark_brush, 2.0f);
    }

    float label_x = bx + box + 8.0f;
    float label_w = (float)bounds.w - label_x - (float)style.pad_right;
    ElementStyle label_style = style;
    if (!enabled && !label_style.fg_color) label_style.fg_color = t->text_muted;
    draw_label(ctx, t, label_style, text, label_x, (float)style.pad_top, label_w,
               (float)bounds.h - (float)style.pad_top - (float)style.pad_bottom);

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

void Checkbox::toggle() {
    if (indeterminate) {
        indeterminate = false;
        checked = true;
    } else {
        checked = !checked;
    }
    invalidate();
}
