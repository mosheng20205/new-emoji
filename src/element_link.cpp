#include "element_link.h"
#include "render_context.h"

Element* Link::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (parent && lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    return nullptr;
}

void Link::paint(RenderContext& ctx) {
    Text::paint(ctx);
    if (!visible || !has_focus || bounds.w <= 0 || bounds.h <= 0) return;
    const Theme* theme = theme_for_window(owner_hwnd);
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    D2D1_RECT_F r = { 0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f };
    ctx.rt->DrawRoundedRectangle(D2D1_ROUNDED_RECT{ r, 3.0f, 3.0f },
        ctx.get_brush(theme->edit_focus), 1.0f);
    ctx.rt->SetTransform(saved);
}

Color Link::text_color(const Theme* theme) const {
    if (style.fg_color) return style.fg_color;
    if (!enabled) return theme->text_muted;
    if (visited) return theme->text_secondary;
    return hovered ? theme->text_primary : theme->accent;
}

void Link::on_mouse_up(int x, int y, MouseButton btn) {
    bool was_pressed = pressed;
    Text::on_mouse_up(x, y, btn);
    if (btn == MouseButton::Left && was_pressed && enabled) {
        visited = true;
        invalidate();
    }
}

void Link::on_key_down(int vk, int) {
    if (!enabled) return;
    if (vk == VK_SPACE || vk == VK_RETURN) {
        m_key_armed = true;
        pressed = true;
        invalidate();
    }
}

void Link::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = m_key_armed && enabled;
        if (should_click) visited = true;
        m_key_armed = false;
        pressed = false;
        invalidate();
        if (should_click && click_cb) click_cb(id);
    }
}
