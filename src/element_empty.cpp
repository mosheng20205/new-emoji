#include "element_empty.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Empty::set_description(const std::wstring& value) {
    description = value;
    invalidate();
}

void Empty::set_icon(const std::wstring& value) {
    icon = value.empty() ? L"📭" : value;
    invalidate();
}

void Empty::set_action(const std::wstring& value) {
    action_text = value;
    action_clicked = false;
    invalidate();
}

void Empty::set_action_clicked(bool value) {
    action_clicked = value;
    invalidate();
}

Rect Empty::action_rect() const {
    if (action_text.empty()) return { 0, 0, 0, 0 };
    float icon_w = (std::min)((float)bounds.w * 0.36f, style.font_size * 5.2f);
    if (icon_w < 42.0f) icon_w = 42.0f;
    float icon_h = icon_w * 0.62f;
    float action_h = style.font_size * 2.15f;
    float total_h = icon_h + style.font_size * 3.2f + action_h;
    float top = ((float)bounds.h - total_h) * 0.5f;
    if (top < 4.0f) top = 4.0f;
    float title_y = top + icon_h + 6.0f;
    float btn_w = (std::min)((float)bounds.w - style.pad_left - style.pad_right,
                             (float)action_text.size() * style.font_size + 34.0f);
    if (btn_w < 96.0f) btn_w = 96.0f;
    float btn_h = style.font_size * 2.15f;
    float btn_x = ((float)bounds.w - btn_w) * 0.5f;
    float btn_y = title_y + style.font_size * 3.2f;
    return { (int)std::lround(btn_x), (int)std::lround(btn_y),
             (int)std::lround(btn_w), (int)std::lround(btn_h) };
}

bool Empty::action_hit(int x, int y) const {
    Rect r = action_rect();
    return r.w > 0 && r.h > 0 && r.contains(x, y);
}

Element* Empty::hit_test(int x, int y) {
    return Element::hit_test(x, y) ? this : nullptr;
}

void Empty::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_secondary;
    Color muted = dark ? 0xFF585B70 : 0xFFC0C4CC;
    Color action_bg = style.bg_color ? style.bg_color : t->accent;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float icon_w = (std::min)((float)bounds.w * 0.36f, style.font_size * 5.2f);
    if (icon_w < 42.0f) icon_w = 42.0f;
    float icon_h = icon_w * 0.62f;
    float action_h = action_text.empty() ? 0.0f : style.font_size * 2.15f;
    float total_h = icon_h + style.font_size * 3.2f + action_h;
    float top = ((float)bounds.h - total_h) * 0.5f;
    if (top < 4.0f) top = 4.0f;
    float icon_x = ((float)bounds.w - icon_w) * 0.5f;
    float icon_y = top;

    draw_text(ctx, icon, style, muted, icon_x, icon_y, icon_w, icon_h, 2.4f);

    float title_y = icon_y + icon_h + 6.0f;
    draw_text(ctx, text.empty() ? L"暂无数据" : text, style, fg,
              0.0f, title_y, (float)bounds.w, style.font_size * 1.7f, 1.0f);
    draw_text(ctx, description, style, t->text_muted,
              (float)style.pad_left, title_y + style.font_size * 1.55f,
              (float)bounds.w - style.pad_left - style.pad_right,
              style.font_size * 1.6f, 0.92f);

    if (!action_text.empty()) {
        float btn_w = (std::min)((float)bounds.w - style.pad_left - style.pad_right,
                                 (float)action_text.size() * style.font_size + 34.0f);
        if (btn_w < 96.0f) btn_w = 96.0f;
        float btn_h = style.font_size * 2.15f;
        float btn_x = ((float)bounds.w - btn_w) * 0.5f;
        float btn_y = title_y + style.font_size * 3.2f;
        D2D1_RECT_F btn = { btn_x, btn_y, btn_x + btn_w, btn_y + btn_h };
        Color btn_bg = m_action_down ? t->button_press : (m_action_hover ? t->button_hover : action_bg);
        ctx.rt->FillRoundedRectangle(ROUNDED(btn, 5.0f, 5.0f), ctx.get_brush(btn_bg));
        if (m_action_hover || m_action_down) {
            ctx.rt->DrawRoundedRectangle(ROUNDED(btn, 5.0f, 5.0f), ctx.get_brush(action_bg), 1.0f);
        }
        draw_text(ctx, action_text, style, 0xFFFFFFFF, btn_x, btn_y, btn_w, btn_h, 0.95f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Empty::on_mouse_move(int x, int y) {
    bool hot = action_hit(x, y);
    if (hot != m_action_hover) {
        m_action_hover = hot;
        invalidate();
    }
}

void Empty::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_action_hover = false;
    m_action_down = false;
    invalidate();
}

void Empty::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_action_down = action_hit(x, y);
    invalidate();
}

void Empty::on_mouse_up(int x, int y, MouseButton) {
    if (m_action_down && action_hit(x, y)) {
        action_clicked = true;
        if (action_cb) action_cb(id);
    }
    pressed = false;
    m_action_down = false;
    invalidate();
}
