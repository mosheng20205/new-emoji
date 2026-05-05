#include "element_rate.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

static Color opaque_color(Color color) {
    return (color != 0 && (color >> 24) == 0) ? (color | 0xFF000000) : color;
}

static std::wstring replace_all(std::wstring value, const std::wstring& from, const std::wstring& to) {
    if (from.empty()) return value;
    size_t pos = 0;
    while ((pos = value.find(from, pos)) != std::wstring::npos) {
        value.replace(pos, from.size(), to);
        pos += to.size();
    }
    return value;
}

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
    if ((int)text_items.size() > max_value) text_items.resize((size_t)max_value);
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

void Rate::set_colors(Color low, Color mid, Color high) {
    low_color = opaque_color(low);
    mid_color = opaque_color(mid);
    high_color = opaque_color(high);
    invalidate();
}

void Rate::set_icons(const std::wstring& full, const std::wstring& empty,
                     const std::wstring& low, const std::wstring& mid, const std::wstring& high) {
    full_icon = full.empty() ? L"\u2605" : full;
    void_icon = empty.empty() ? L"\u2606" : empty;
    low_icon = low;
    mid_icon = mid;
    high_icon = high;
    invalidate();
}

void Rate::set_text_items(const std::vector<std::wstring>& items) {
    text_items = items;
    if ((int)text_items.size() > max_value) text_items.resize((size_t)max_value);
    invalidate();
}

void Rate::set_display_options(bool next_show_text, bool next_show_score,
                               Color next_text_color, const std::wstring& next_score_template) {
    show_text = next_show_text;
    show_score = next_show_score;
    score_text_color = opaque_color(next_text_color);
    score_template = next_score_template.empty() ? L"{value}" : next_score_template;
    show_score_text = show_text || show_score;
    invalidate();
}

Color Rate::active_color(const Theme* theme, int display_value_x2) const {
    if (!enabled) return theme->text_secondary;
    if (display_value_x2 <= 0) return theme->accent;
    if (low_color == 0 && mid_color == 0 && high_color == 0) return theme->accent;
    int max_x2 = (std::max)(1, max_value * 2);
    int percent = display_value_x2 * 100 / max_x2;
    if (percent <= 40) return low_color ? low_color : theme->accent;
    if (percent <= 80) return mid_color ? mid_color : theme->accent;
    return high_color ? high_color : theme->accent;
}

std::wstring Rate::active_icon(int display_value_x2) const {
    if (display_value_x2 <= 0) return full_icon.empty() ? L"\u2605" : full_icon;
    int max_x2 = (std::max)(1, max_value * 2);
    int percent = display_value_x2 * 100 / max_x2;
    if (percent <= 40 && !low_icon.empty()) return low_icon;
    if (percent <= 80 && !mid_icon.empty()) return mid_icon;
    if (percent > 80 && !high_icon.empty()) return high_icon;
    return full_icon.empty() ? L"\u2605" : full_icon;
}

std::wstring Rate::score_text() const {
    std::wstring value_text = (value_x2 % 2) == 0
        ? std::to_wstring(value_x2 / 2)
        : std::to_wstring(value_x2 / 2) + L".5";
    std::wstring result = score_template.empty() ? L"{value}" : score_template;
    result = replace_all(result, L"{value}", value_text);
    result = replace_all(result, L"{max}", std::to_wstring(max_value));
    return result;
}

std::wstring Rate::item_text() const {
    if (value_x2 <= 0) return low_text;
    int index = (value_x2 + 1) / 2 - 1;
    if (index >= 0 && index < (int)text_items.size() && !text_items[(size_t)index].empty()) {
        return text_items[(size_t)index];
    }
    return high_text;
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

    Color fg = score_text_color ? score_text_color : (style.fg_color ? style.fg_color : t->text_primary);
    if (readonly || !enabled) fg = t->text_secondary;
    float label_w = label_width();
    if (!text.empty()) {
        draw_text(ctx, text, style, t->text_secondary, (float)style.pad_left, 0.0f,
                  label_w, (float)bounds.h);
    }

    int display_value_x2 = (enabled && !readonly && m_hover_value_x2 > 0) ? m_hover_value_x2 : value_x2;
    Color filled_color = active_color(t, display_value_x2);
    std::wstring filled_icon = active_icon(display_value_x2);
    float s = star_size();
    float gap = 4.0f * style.font_size / 14.0f;
    float start_x = (float)style.pad_left + label_w + (label_w > 0.0f ? 10.0f : 0.0f);
    for (int i = 0; i < max_value; ++i) {
        int star_full_x2 = (i + 1) * 2;
        int star_half_x2 = i * 2 + 1;
        float sx = start_x + (s + gap) * (float)i;
        draw_text(ctx, void_icon.empty() ? L"\u2606" : void_icon, style, t->border_default,
                  sx, 0.0f, s + gap, (float)bounds.h,
                  1.35f, DWRITE_TEXT_ALIGNMENT_CENTER);
        if (display_value_x2 >= star_full_x2) {
            draw_text(ctx, filled_icon, style, filled_color,
                      sx, 0.0f, s + gap, (float)bounds.h,
                      1.35f, DWRITE_TEXT_ALIGNMENT_CENTER);
        } else if (display_value_x2 == star_half_x2) {
            D2D1_RECT_F clip = { sx, 0.0f, sx + (s + gap) * 0.5f, (float)bounds.h };
            ctx.push_clip(clip);
            draw_text(ctx, filled_icon, style, filled_color,
                      sx, 0.0f, s + gap, (float)bounds.h,
                      1.35f, DWRITE_TEXT_ALIGNMENT_CENTER);
            ctx.pop_clip();
        }
    }

    if (show_score_text) {
        std::wstring score;
        if (show_score) score = score_text();
        if (show_text) {
            std::wstring label = item_text();
            if (!label.empty()) {
                if (!score.empty()) score += L" ";
                score += label;
            }
        } else if (!show_score && (!low_text.empty() || !high_text.empty())) {
            score = score_text();
            score += L"/" + std::to_wstring(max_value) + L" ";
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
