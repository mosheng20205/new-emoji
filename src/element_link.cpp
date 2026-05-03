#include "element_link.h"
#include "render_context.h"
#include <shellapi.h>

static Color link_type_color(int type, const Theme* theme) {
    switch (type) {
    case 1: return theme->accent;
    case 2: return 0xFF16A34A;
    case 3: return 0xFFD97706;
    case 4: return 0xFFDC2626;
    case 5: return 0xFF0EA5E9;
    default: return theme->text_primary;
    }
}

static Color mix_link_color(Color a, Color b, float t) {
    auto mix = [t](unsigned ca, unsigned cb) -> unsigned {
        return (unsigned)((float)ca + ((float)cb - (float)ca) * t + 0.5f);
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

Element* Link::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (parent && lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    return nullptr;
}

void Link::paint(RenderContext& ctx) {
    std::wstring saved_text = text;
    std::wstring display = display_text();
    if (display != text) text = display;
    Text::paint(ctx);
    text = saved_text;
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
    Color base = link_type_color(link_type, theme);
    return hovered ? mix_link_color(base, theme->text_primary, link_type == 0 ? 0.18f : 0.32f) : base;
}

void Link::on_mouse_up(int x, int y, MouseButton btn) {
    bool was_pressed = pressed;
    Text::on_mouse_up(x, y, btn);
    if (btn == MouseButton::Left && was_pressed && enabled) {
        visited = true;
        open_href_if_needed();
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
        if (should_click) {
            visited = true;
            open_href_if_needed();
        }
        m_key_armed = false;
        pressed = false;
        invalidate();
        if (should_click && click_cb) click_cb(id);
    }
}

void Link::set_options(int type, int underline, int open, int is_visited) {
    if (type < 0) type = 0;
    if (type > 5) type = 5;
    link_type = type;
    underline_enabled = underline != 0;
    auto_open = open != 0;
    visited = is_visited != 0;
    invalidate();
}

void Link::set_content(const std::wstring& prefix, const std::wstring& suffix,
                       const std::wstring& link_href, const std::wstring& link_target) {
    prefix_icon = prefix;
    suffix_icon = suffix;
    href = link_href;
    target = link_target;
    invalidate();
}

std::wstring Link::display_text() const {
    std::wstring value;
    if (!prefix_icon.empty()) {
        value += prefix_icon;
        value += L" ";
    }
    value += text;
    if (!suffix_icon.empty()) {
        value += L" ";
        value += suffix_icon;
    }
    return value;
}

void Link::open_href_if_needed() {
    if (!auto_open || href.empty()) return;
    ShellExecuteW(nullptr, L"open", href.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
}
