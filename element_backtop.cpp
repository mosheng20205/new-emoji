#include "element_backtop.h"
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

void Backtop::set_state(int scroll, int show_threshold, int target) {
    set_options(scroll, show_threshold, target, container_id, duration_ms);
}

void Backtop::set_options(int scroll, int show_threshold, int target, int target_container_id, int duration) {
    threshold = (std::max)(0, show_threshold);
    target_position = (std::max)(0, target);
    container_id = (std::max)(0, target_container_id);
    duration_ms = duration < 0 ? 0 : duration;
    set_scroll_position(scroll);
}

void Backtop::set_scroll_position(int scroll) {
    scroll_position = (std::max)(0, scroll);
    visible = scroll_position >= threshold;
    invalidate();
}

void Backtop::trigger_backtop() {
    last_scroll_before_jump = scroll_position;
    scroll_position = target_position;
    ++activated_count;
    visible = scroll_position >= threshold;
    pressed = false;
    invalidate();
}

int Backtop::is_shown() const {
    return visible ? 1 : 0;
}

void Backtop::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF2B2E42 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->accent;
    if (hovered) bg = t->button_hover;
    if (pressed) bg = t->button_press;

    float radius = style.corner_radius > 0.0f ? style.corner_radius : 18.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    std::wstring label = text.empty() ? L"↑" : text;
    draw_text(ctx, label, style, fg, 0.0f, 0.0f, (float)bounds.w, (float)bounds.h);

    ctx.rt->SetTransform(saved);
}

void Backtop::on_mouse_down(int, int, MouseButton) {
    pressed = true;
    invalidate();
}

void Backtop::on_mouse_up(int, int, MouseButton) {
    trigger_backtop();
}

void Backtop::on_mouse_leave() {
    hovered = false;
    pressed = false;
    invalidate();
}

void Backtop::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        trigger_backtop();
    }
}
