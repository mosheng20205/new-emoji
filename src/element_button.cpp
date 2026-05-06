#include "element_button.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <map>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

std::map<UINT_PTR, Button*> g_button_timer_map;

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color mix_color(Color a, Color b, float t) {
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

static Color hover_variant_color(Color solid, bool dark, bool enabled) {
    if (!enabled) return solid;
    return dark ? mix_color(solid, 0xFFFFFFFF, 0.10f) : mix_color(solid, 0xFF000000, 0.08f);
}

static Color variant_color(int variant, const Theme* t) {
    switch (variant) {
    case 1: return t->accent;
    case 2: return 0xFF16A34A;
    case 3: return 0xFFF59E0B;
    case 4: return 0xFFDC2626;
    case 6: return 0xFF0EA5E9;
    default: return t->button_bg;
    }
}

static Color variant_text_color(int variant, const Theme* t, bool plain) {
    switch (variant) {
    case 1: return plain ? t->accent : 0xFFFFFFFF;
    case 2: return plain ? 0xFF16A34A : 0xFFFFFFFF;
    case 3: return plain ? 0xFFD97706 : 0xFF1F2937;
    case 4: return plain ? 0xFFDC2626 : 0xFFFFFFFF;
    case 5: return t->accent;
    case 6: return plain ? 0xFF0EA5E9 : 0xFFFFFFFF;
    default: return t->text_primary;
    }
}

static void button_size_metrics(const ElementStyle& style, int size,
                                float& font_size, int& pad_x, int& pad_y) {
    float scale = style.font_size > 0.0f ? style.font_size / 14.0f : 1.0f;
    font_size = style.font_size;
    pad_x = style.pad_left;
    pad_y = style.pad_top;
    if (size == 1) {
        font_size = 14.0f * scale;
        pad_x = (int)std::lround(10.0f * scale);
        pad_y = (int)std::lround(5.0f * scale);
    } else if (size == 2) {
        font_size = 13.0f * scale;
        pad_x = (int)std::lround(8.0f * scale);
        pad_y = (int)std::lround(4.0f * scale);
    } else if (size == 3) {
        font_size = 12.0f * scale;
        pad_x = (int)std::lround(6.0f * scale);
        pad_y = (int)std::lround(3.0f * scale);
    }
    if (pad_x < 2) pad_x = 2;
    if (pad_y < 1) pad_y = 1;
}

static void draw_loading_spinner(RenderContext& ctx, float cx, float cy,
                                 float radius, Color color, int angle_degrees) {
    const float two_pi = 6.2831853f;
    float dot = (std::max)(2.0f, radius * 0.22f);
    for (int i = 0; i < 8; ++i) {
        float angle = two_pi * ((float)i / 8.0f + (float)angle_degrees / 360.0f);
        float px = cx + std::cos(angle) * radius;
        float py = cy + std::sin(angle) * radius;
        unsigned alpha = 0x44 + (unsigned)(i * 0x18);
        if (alpha > 0xFF) alpha = 0xFF;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(px, py), dot, dot),
                            ctx.get_brush(with_alpha(color, alpha)));
    }
}

Button::~Button() {
    stop_timer();
}

void Button::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    if (loading) ensure_timer();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    bool text_variant = variant == 5;
    bool plain_mode = plain && !text_variant;
    Color solid = variant_color(variant, t);
    Color bg = style.bg_color ? style.bg_color : t->button_bg;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;

    if (text_variant) {
        bg = 0;
        border = 0;
        fg = style.fg_color ? style.fg_color : variant_text_color(variant, t, true);
    } else if (plain_mode) {
        bg = variant == 0 ? 0 : with_alpha(solid, dark ? 0x2A : 0x18);
        border = variant == 0 ? t->border_default : solid;
        fg = variant == 0 ? t->text_primary : variant_text_color(variant, t, true);
    } else if (variant >= 1) {
        bg = solid;
        border = solid;
        fg = variant_text_color(variant, t, false);
    }

    bool active = (pressed || keyboard_armed) && !loading;
    if (!enabled) {
        bg = text_variant ? 0 : (dark ? 0xFF2A2D3A : 0xFFE5E7EB);
        border = text_variant ? 0 : (dark ? 0xFF3A3D4C : 0xFFD1D5DB);
        fg = t->text_muted;
    } else if (active) {
        if (press_bg) bg = press_bg;
        else if (text_variant) bg = 0;
        else if (plain_mode) bg = variant == 0 ? with_alpha(t->accent, dark ? 0x26 : 0x16)
                                               : with_alpha(solid, dark ? 0x42 : 0x2A);
        else if (variant == 0) bg = t->button_press;
        else bg = hover_variant_color(solid, dark, true);
        if (press_border) border = press_border;
        else if (variant == 0 && !plain_mode && !text_variant) border = t->button_press;
        else if (variant >= 1 && !plain_mode && !text_variant) border = hover_variant_color(solid, dark, true);
        if (press_fg) fg = press_fg;
    } else if (hovered && !loading) {
        if (hover_bg) bg = hover_bg;
        else if (text_variant) bg = 0;
        else if (plain_mode) bg = variant == 0 ? with_alpha(t->accent, dark ? 0x1E : 0x10)
                                               : with_alpha(solid, dark ? 0x34 : 0x22);
        else if (variant == 0) bg = t->button_hover;
        else bg = hover_variant_color(solid, dark, true);
        if (hover_border) border = hover_border;
        else if (variant == 0 && !plain_mode && !text_variant) border = t->button_hover;
        else if (variant >= 1 && !plain_mode && !text_variant) border = hover_variant_color(solid, dark, true);
        if (hover_fg) fg = hover_fg;
    }

    float font_size = style.font_size;
    int pad_x = style.pad_left;
    int pad_y = style.pad_top;
    button_size_metrics(style, size, font_size, pad_x, pad_y);

    float r = style.corner_radius > 0 ? style.corner_radius : 6.0f;
    if (round) r = (std::max)(r, (float)bounds.h * 0.45f);
    if (circle) r = (std::min)((float)bounds.w, (float)bounds.h) * 0.5f;

    if (bg) {
        auto* br = ctx.get_brush(bg);
        D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRoundedRectangle(ROUNDED(rect, r, r), br);
    }

    if (border) {
        auto* br = ctx.get_brush(border);
        D2D1_RECT_F rect = { 0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f };
        ctx.rt->DrawRoundedRectangle(ROUNDED(rect, r, r), br, 1.0f);
    }

    if (has_focus) {
        D2D1_RECT_F focus = { 2.5f, 2.5f, (float)bounds.w - 2.5f, (float)bounds.h - 2.5f };
        ctx.rt->DrawRoundedRectangle(ROUNDED(focus, (std::max)(0.0f, r - 2.0f), (std::max)(0.0f, r - 2.0f)),
            ctx.get_brush(t->edit_focus), 1.2f);
    }

    std::wstring display = emoji + text;
    float spinner_radius = (std::max)(4.0f, font_size * 0.32f);
    float spinner_diameter = spinner_radius * 2.0f;
    bool has_spinner = loading;
    if (has_spinner) {
        float sx = circle ? (float)bounds.w * 0.5f : (float)pad_x + spinner_radius + 2.0f;
        float sy = (float)bounds.h * 0.5f;
        if (circle && !display.empty()) sx = (std::max)(spinner_radius + 3.0f, (float)bounds.w * 0.32f);
        draw_loading_spinner(ctx, sx, sy, spinner_radius, fg, animation_angle);
    }

    if (!display.empty()) {
        float text_x = (float)pad_x;
        float text_w = (float)(bounds.w - pad_x * 2);
        if (has_spinner && !circle) {
            text_x += spinner_diameter + 6.0f;
            text_w -= spinner_diameter + 6.0f;
        }
        if (text_w < 1.0f) text_w = 1.0f;
        auto* layout = ctx.create_text_layout(display, style.font_name, font_size,
                                              text_w, (float)bounds.h - pad_y * 2);
        if (layout) {
            apply_emoji_font_fallback(layout, display);
            layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
            ctx.rt->DrawTextLayout(D2D1::Point2F(text_x, (float)pad_y), layout,
                                   ctx.get_brush(fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    for (auto& ch : children) {
        if (ch->visible) ch->paint(ctx);
    }

    ctx.rt->SetTransform(saved);
}

void Button::on_mouse_enter() { hovered = true; invalidate(); }
void Button::on_mouse_leave() { hovered = false; pressed = false; keyboard_armed = false; invalidate(); }
void Button::on_mouse_down(int, int, MouseButton) {
    if (enabled && !loading) pressed = true;
    invalidate();
}
void Button::on_mouse_up(int, int, MouseButton) {
    pressed = false;
    invalidate();
}

void Button::on_key_down(int vk, int) {
    if (!enabled || loading) return;
    if (vk == VK_SPACE || vk == VK_RETURN) {
        keyboard_armed = true;
        pressed = true;
        invalidate();
    }
}

void Button::on_key_up(int vk, int) {
    if (vk == VK_SPACE || vk == VK_RETURN) {
        bool should_click = enabled && !loading && keyboard_armed;
        keyboard_armed = false;
        pressed = false;
        invalidate();
        if (should_click && click_cb) click_cb(id);
    }
}

void Button::set_variant(int value) {
    if (value < 0) value = 0;
    if (value > 6) value = 6;
    variant = value;
    invalidate();
}

void Button::set_options(int variant_value, int plain_value, int round_value,
                         int circle_value, int loading_value, int size_value) {
    set_variant(variant_value);
    plain = plain_value != 0;
    round = round_value != 0;
    circle = circle_value != 0;
    if (size_value < 0) size_value = 0;
    if (size_value > 3) size_value = 3;
    size = size_value;
    set_loading(loading_value != 0);
    invalidate();
}

void Button::set_loading(bool value) {
    loading = value;
    pressed = false;
    keyboard_armed = false;
    if (loading) ensure_timer();
    else stop_timer();
    invalidate();
}

void Button::tick(int elapsed_ms) {
    if (!loading) {
        stop_timer();
        return;
    }
    int step = (std::max)(1, elapsed_ms) * 360 / 900;
    if (step <= 0) step = 1;
    animation_angle = (animation_angle + step) % 360;
    ++tick_count;
    invalidate();
}

void Button::ensure_timer() {
    if (m_timer_id || !owner_hwnd || !loading) return;
    m_timer_id = 0xB000 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 33, nullptr);
    if (m_timer_id) g_button_timer_map[m_timer_id] = this;
}

void Button::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_button_timer_map.erase(m_timer_id);
    m_timer_id = 0;
}
