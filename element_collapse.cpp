#include "element_collapse.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

float Collapse::header_height() const {
    return (std::max)(style.font_size * 2.65f, 36.0f);
}

void Collapse::set_items(const std::vector<CollapseItem>& values) {
    items = values;
    if (items.empty()) active_index = -1;
    else if (active_index >= (int)items.size()) active_index = 0;
    for (auto it = disabled_indices.begin(); it != disabled_indices.end();) {
        if (*it < 0 || *it >= (int)items.size()) it = disabled_indices.erase(it);
        else ++it;
    }
    invalidate();
}

void Collapse::set_active_index(int value) {
    int old = active_index;
    if (items.empty()) {
        active_index = -1;
    } else {
        if (value < -1) value = -1;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        if (is_disabled(value)) value = next_enabled_index(value, 1);
        active_index = value;
    }
    if (animated && old != active_index) begin_animation(active_index);
    invalidate();
}

void Collapse::set_accordion(bool value) {
    accordion = value;
    invalidate();
}

void Collapse::set_options(bool accordion_value, bool allow_collapse_value,
                           const std::set<int>& disabled, bool animated_value) {
    accordion = accordion_value;
    allow_collapse = allow_collapse_value;
    animated = animated_value;
    disabled_indices.clear();
    for (int index : disabled) {
        if (index >= 0 && index < (int)items.size()) disabled_indices.insert(index);
    }
    if (is_disabled(active_index)) active_index = next_enabled_index(active_index, 1);
    invalidate();
}

void Collapse::begin_animation(int index) {
    m_anim_index = index;
    m_anim_start = GetTickCount64();
}

float Collapse::animation_progress() const {
    if (!animated || m_anim_index < 0 || m_anim_start == 0) return 1.0f;
    ULONGLONG elapsed = GetTickCount64() - m_anim_start;
    float p = (float)elapsed / (float)kAnimDurationMs;
    if (p >= 1.0f) return 1.0f;
    if (p < 0.0f) return 0.0f;
    return 1.0f - (1.0f - p) * (1.0f - p);
}

bool Collapse::is_disabled(int index) const {
    return disabled_indices.find(index) != disabled_indices.end();
}

int Collapse::next_enabled_index(int start, int direction) const {
    if (items.empty()) return -1;
    int count = (int)items.size();
    if (direction == 0) direction = 1;
    int idx = start;
    for (int step = 0; step < count; ++step) {
        if (idx < 0) idx = count - 1;
        if (idx >= count) idx = 0;
        if (!is_disabled(idx)) return idx;
        idx += direction > 0 ? 1 : -1;
    }
    return -1;
}

int Collapse::header_at(int x, int y) const {
    if (x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    float hh = header_height();
    float cy = (float)style.pad_top;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (y >= cy && y < cy + hh) return is_disabled(i) ? -1 : i;
        cy += hh;
        if (i == active_index) {
            float body_h = (std::max)(style.font_size * 3.2f, 48.0f);
            cy += body_h;
        }
    }
    return -1;
}

void Collapse::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF1E1E2E : 0xFFFFFFFF);
    Color panel_bg = dark ? 0xFF242637 : 0xFFFAFAFA;
    Color hover_bg = dark ? 0xFF2B2E42 : 0xFFF5F7FA;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = t->text_secondary;
    Color accent = t->accent;
    Color disabled_fg = t->text_muted;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);
    ctx.rt->FillRectangle(clip, ctx.get_brush(bg));

    float left = (float)style.pad_left;
    float right = (float)bounds.w - (float)style.pad_right;
    if (right < left) right = left;
    float hh = header_height();
    float body_h = (std::max)(style.font_size * 3.2f, 48.0f);
    float y = (float)style.pad_top;

    for (int i = 0; i < (int)items.size(); ++i) {
        if (y >= bounds.h) break;
        bool active = i == active_index;
        D2D1_RECT_F header = { left, y, right, (std::min)(y + hh, (float)bounds.h) };
        if (i == m_hover_index || i == m_press_index) {
            ctx.rt->FillRectangle(header, ctx.get_brush(hover_bg));
        }
        bool disabled = is_disabled(i);
        ctx.rt->DrawLine(D2D1::Point2F(left, y),
                         D2D1::Point2F(right, y),
                         ctx.get_brush(border), 1.0f);

        float arrow_x = left + 10.0f;
        float arrow_y = y + hh * 0.5f;
        auto* arrow_br = ctx.get_brush(disabled ? disabled_fg : (active ? accent : t->text_secondary));
        if (active) {
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x - 4.0f, arrow_y - 2.0f),
                             D2D1::Point2F(arrow_x, arrow_y + 3.0f), arrow_br, 1.5f);
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x, arrow_y + 3.0f),
                             D2D1::Point2F(arrow_x + 5.0f, arrow_y - 3.0f), arrow_br, 1.5f);
        } else {
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x - 2.0f, arrow_y - 5.0f),
                             D2D1::Point2F(arrow_x + 3.0f, arrow_y), arrow_br, 1.5f);
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x + 3.0f, arrow_y),
                             D2D1::Point2F(arrow_x - 2.0f, arrow_y + 5.0f), arrow_br, 1.5f);
        }
        draw_text(ctx, items[i].title.empty() ? L"Collapse Item" : items[i].title, style,
                  disabled ? disabled_fg : (active ? accent : title_fg),
                  left + 28.0f, y, right - left - 36.0f, hh,
                  1.0f, active ? DWRITE_FONT_WEIGHT_SEMI_BOLD : DWRITE_FONT_WEIGHT_NORMAL);
        y += hh;

        if (active && y < bounds.h) {
            float progress = (i == m_anim_index) ? animation_progress() : 1.0f;
            float current_body_h = body_h * progress;
            D2D1_RECT_F body = { left, y, right, (std::min)(y + current_body_h, (float)bounds.h) };
            ctx.rt->FillRectangle(body, ctx.get_brush(panel_bg));
            D2D1_RECT_F body_clip = { left, y, right, (std::min)(y + current_body_h, (float)bounds.h) };
            ctx.push_clip(body_clip);
            draw_text(ctx, items[i].body, style, body_fg,
                      left + 28.0f, y + 9.0f, right - left - 42.0f, body_h - 18.0f,
                      0.95f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_WORD_WRAPPING_WRAP);
            ctx.pop_clip();
            if (progress < 1.0f) invalidate();
            y += current_body_h;
        }
    }

    ctx.rt->DrawLine(D2D1::Point2F(left, (std::min)(y, (float)bounds.h - 1.0f)),
                     D2D1::Point2F(right, (std::min)(y, (float)bounds.h - 1.0f)),
                     ctx.get_brush(border), 1.0f);
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Collapse::on_mouse_move(int x, int y) {
    int idx = header_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Collapse::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Collapse::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_index = header_at(x, y);
    invalidate();
}

void Collapse::on_mouse_up(int x, int y, MouseButton) {
    int idx = header_at(x, y);
    if (idx >= 0 && idx == m_press_index) {
        set_active_index((allow_collapse && active_index == idx) ? -1 : idx);
    }
    pressed = false;
    m_press_index = -1;
    m_hover_index = idx;
    invalidate();
}

void Collapse::on_key_down(int vk, int) {
    if (items.empty()) return;
    if (vk == VK_UP) set_active_index(next_enabled_index(active_index - 1, -1));
    else if (vk == VK_DOWN) set_active_index(next_enabled_index(active_index + 1, 1));
    else if (vk == VK_HOME) set_active_index(next_enabled_index(0, 1));
    else if (vk == VK_END) set_active_index(next_enabled_index((int)items.size() - 1, -1));
    else if ((vk == VK_RETURN || vk == VK_SPACE) && allow_collapse && active_index >= 0) set_active_index(-1);
}
