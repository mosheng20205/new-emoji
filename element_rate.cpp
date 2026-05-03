#include "element_rate.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
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

float Rate::label_width() const {
    if (text.empty()) return 0.0f;
    float w = (float)bounds.w * 0.34f;
    float cap = 120.0f * style.font_size / 14.0f;
    return (std::min)(w, cap);
}

float Rate::star_size() const {
    float s = style.font_size * 1.35f;
    return s < 16.0f ? 16.0f : s;
}

void Rate::set_max_value(int max_v) {
    if (max_v < 1) max_v = 1;
    if (max_v > 10) max_v = 10;
    max_value = max_v;
    set_value_x2(value_x2);
}

void Rate::set_value(int new_value) {
    set_value_x2(new_value * 2);
}

void Rate::set_value_x2(int new_value_x2) {
    int old_value_x2 = value_x2;
    if (new_value_x2 < 0) new_value_x2 = 0;
    if (new_value_x2 > max_value * 2) new_value_x2 = max_value * 2;
    if (!allow_half && (new_value_x2 % 2) != 0) new_value_x2 += 1;
    if (new_value_x2 > max_value * 2) new_value_x2 = max_value * 2;
    value_x2 = new_value_x2;
    value = value_x2 / 2;
    invalidate();
    if (old_value_x2 != value_x2) notify_changed();
}

void Rate::set_options(bool allow_clear_value, bool allow_half_value, bool readonly_value) {
    allow_clear = allow_clear_value;
    allow_half = allow_half_value;
    readonly = readonly_value;
    set_value_x2(value_x2);
    invalidate();
}

void Rate::set_texts(const std::wstring& low, const std::wstring& high, bool show_score) {
    low_text = low;
    high_text = high;
    show_score_text = show_score;
    invalidate();
}

void Rate::notify_changed() {
    if (change_cb) change_cb(id, value_x2, value, max_value);
}

int Rate::value_x2_at(int x, int y) const {
    if (x < 0 || y < 0 || y >= bounds.h) return 0;
    float label_w = label_width();
    float start_x = (float)style.pad_left + label_w + (label_w > 0.0f ? 10.0f : 0.0f);
    float s = star_size();
    float gap = 4.0f * style.font_size / 14.0f;
    for (int i = 0; i < max_value; ++i) {
        float sx = start_x + (s + gap) * (float)i;
        if ((float)x >= sx && (float)x < sx + s + gap) {
            if (allow_half && (float)x < sx + s * 0.5f) return i * 2 + 1;
            return (i + 1) * 2;
        }
    }
    return 0;
}

void Rate::paint(RenderContext& ctx) {
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

    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    if (readonly || !enabled) fg = t->text_secondary;
    float label_w = label_width();
    if (!text.empty()) {
        draw_text(ctx, text, style, t->text_secondary, (float)style.pad_left, 0.0f,
                  label_w, (float)bounds.h);
    }

    int display_value_x2 = (enabled && !readonly && m_hover_value_x2 > 0) ? m_hover_value_x2 : value_x2;
    float s = star_size();
    float gap = 4.0f * style.font_size / 14.0f;
    float start_x = (float)style.pad_left + label_w + (label_w > 0.0f ? 10.0f : 0.0f);
    for (int i = 0; i < max_value; ++i) {
        int star_full_x2 = (i + 1) * 2;
        int star_half_x2 = i * 2 + 1;
        float sx = start_x + (s + gap) * (float)i;
        draw_text(ctx, L"\u2606", style, t->border_default,
                  sx, 0.0f, s + gap, (float)bounds.h,
                  1.35f, DWRITE_TEXT_ALIGNMENT_CENTER);
        if (display_value_x2 >= star_full_x2) {
            draw_text(ctx, L"\u2605", style, enabled ? t->accent : t->text_secondary,
                      sx, 0.0f, s + gap, (float)bounds.h,
                      1.35f, DWRITE_TEXT_ALIGNMENT_CENTER);
        } else if (display_value_x2 == star_half_x2) {
            D2D1_RECT_F clip = { sx, 0.0f, sx + (s + gap) * 0.5f, (float)bounds.h };
            ctx.push_clip(clip);
            draw_text(ctx, L"\u2605", style, enabled ? t->accent : t->text_secondary,
                      sx, 0.0f, s + gap, (float)bounds.h,
                      1.35f, DWRITE_TEXT_ALIGNMENT_CENTER);
            ctx.pop_clip();
        }
    }

    if (show_score_text) {
        std::wstring score = (value_x2 % 2) == 0
            ? std::to_wstring(value_x2 / 2)
            : std::to_wstring(value_x2 / 2) + L".5";
        score += L"/" + std::to_wstring(max_value);
        if (!low_text.empty() || !high_text.empty()) {
            score += L" ";
            score += value_x2 > 0 ? high_text : low_text;
        }
        float text_x = start_x + (s + gap) * (float)max_value + 8.0f;
        draw_text(ctx, score, style, fg, text_x, 0.0f,
                  (float)bounds.w - text_x - (float)style.pad_right, (float)bounds.h);
    }

    ctx.rt->SetTransform(saved);
}

void Rate::on_mouse_move(int x, int y) {
    if (readonly || !enabled) return;
    int v = value_x2_at(x, y);
    if (v != m_hover_value_x2) {
        m_hover_value_x2 = v;
        m_hover_value = v / 2;
        invalidate();
    }
}

void Rate::on_mouse_leave() {
    m_hover_value = 0;
    m_press_value = 0;
    m_hover_value_x2 = 0;
    m_press_value_x2 = 0;
    hovered = false;
    invalidate();
}

void Rate::on_mouse_down(int x, int y, MouseButton) {
    if (readonly || !enabled) return;
    m_press_value_x2 = value_x2_at(x, y);
    m_press_value = m_press_value_x2 / 2;
    pressed = true;
    invalidate();
}

void Rate::on_mouse_up(int x, int y, MouseButton) {
    if (readonly || !enabled) return;
    int v = value_x2_at(x, y);
    if (v > 0 && v == m_press_value_x2) {
        set_value_x2(allow_clear && value_x2 == v ? 0 : v);
    }
    m_press_value = 0;
    m_press_value_x2 = 0;
    pressed = false;
    invalidate();
}

void Rate::on_key_down(int vk, int) {
    if (readonly || !enabled) return;
    int delta = allow_half ? 1 : 2;
    if (vk == VK_LEFT || vk == VK_DOWN) set_value_x2(value_x2 - delta);
    else if (vk == VK_RIGHT || vk == VK_UP) set_value_x2(value_x2 + delta);
    else if (vk == VK_HOME) set_value_x2(0);
    else if (vk == VK_END) set_value_x2(max_value * 2);
}
