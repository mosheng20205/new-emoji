#include "element_button.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

void Button::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    // Save transform and translate to local coords
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);

    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg     = style.bg_color ? style.bg_color : t->button_bg;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg     = style.fg_color ? style.fg_color : t->text_primary;
    if (variant == 1) { bg = t->accent; border = t->accent; fg = 0xFFFFFFFF; }
    else if (variant == 2) { bg = 0xFF16A34A; border = 0xFF16A34A; fg = 0xFFFFFFFF; }
    else if (variant == 3) { bg = 0xFFF59E0B; border = 0xFFF59E0B; fg = 0xFF1F2937; }
    else if (variant == 4) { bg = 0xFFDC2626; border = 0xFFDC2626; fg = 0xFFFFFFFF; }
    else if (variant == 5) { bg = 0; border = 0; fg = style.fg_color ? style.fg_color : t->accent; }

    bool active = pressed || keyboard_armed;
    if (!enabled) {
        bg = variant == 5 ? 0 : (dark ? 0xFF2A2D3A : 0xFFE5E7EB);
        border = dark ? 0xFF3A3D4C : 0xFFD1D5DB;
        fg = t->text_muted;
    } else if (active) {
        bg     = press_bg ? press_bg : t->button_press;
        border = press_border ? press_border : t->button_press;
        fg     = press_fg ? press_fg : fg;
        if (variant >= 1 && variant <= 4) border = bg;
    } else if (hovered) {
        bg     = hover_bg ? hover_bg : t->button_hover;
        border = hover_border ? hover_border : t->button_hover;
        fg     = hover_fg ? hover_fg : fg;
        if (variant >= 1 && variant <= 4) border = bg;
    }

    float r = style.corner_radius > 0 ? style.corner_radius : 6.0f;

    // Background at (0,0)
    {
        if (bg) {
            auto* br = ctx.get_brush(bg);
            D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
            ctx.rt->FillRoundedRectangle(ROUNDED(rect, r, r), br);
        }
    }

    // Border at (0,0)
    {
        if (border) {
            auto* br = ctx.get_brush(border);
            D2D1_RECT_F rect = { 0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f };
            ctx.rt->DrawRoundedRectangle(ROUNDED(rect, r, r), br, 1.0f);
        }
    }

    if (has_focus) {
        D2D1_RECT_F focus = { 2.5f, 2.5f, (float)bounds.w - 2.5f, (float)bounds.h - 2.5f };
        ctx.rt->DrawRoundedRectangle(ROUNDED(focus, (std::max)(0.0f, r - 2.0f), (std::max)(0.0f, r - 2.0f)),
            ctx.get_brush(t->edit_focus), 1.2f);
    }

    // Text + emoji at (0,0)
    std::wstring display = emoji + text;
    if (!display.empty()) {
        float text_w = (float)(bounds.w - style.pad_left - style.pad_right);
        if (text_w < 1.0f) text_w = 1.0f;
        auto* layout = ctx.create_text_layout(display, style.font_name, style.font_size,
                                              text_w, (float)bounds.h);
        if (layout) {
            apply_emoji_font_fallback(layout, display);
            layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            auto* fg_brush = ctx.get_brush(fg);
            D2D1_POINT_2F pt = { (float)style.pad_left, 0 };
            ctx.rt->DrawTextLayout(pt, layout, fg_brush, D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    ctx.rt->SetTransform(saved);
}

void Button::on_mouse_enter() { hovered = true; invalidate(); }
void Button::on_mouse_leave() { hovered = false; pressed = false; keyboard_armed = false; invalidate(); }
void Button::on_mouse_down(int, int, MouseButton) { if (enabled) pressed = true; invalidate(); }
void Button::on_mouse_up(int, int, MouseButton)   { pressed = false; invalidate(); }

void Button::on_key_down(int vk, int) {
    if (!enabled) return;
    if (vk == VK_SPACE || vk == VK_RETURN) {
        keyboard_armed = true;
        pressed = true;
        invalidate();
    }
}

void Button::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = enabled && keyboard_armed;
        keyboard_armed = false;
        pressed = false;
        invalidate();
        if (should_click && click_cb) click_cb(id);
    }
}

void Button::set_variant(int value) {
    if (value < 0) value = 0;
    if (value > 5) value = 5;
    variant = value;
    invalidate();
}
