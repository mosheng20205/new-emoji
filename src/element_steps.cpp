#include "element_steps.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

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

void Steps::set_items(const std::vector<std::wstring>& values) {
    items = values;
    descriptions.assign(items.size(), L"");
    statuses.assign(items.size(), 0);
    activate_index(active_index, 1);
}

void Steps::set_step_items(const std::vector<std::pair<std::wstring, std::wstring>>& values) {
    items.clear();
    descriptions.clear();
    for (const auto& value : values) {
        items.push_back(value.first);
        descriptions.push_back(value.second);
    }
    statuses.assign(items.size(), 0);
    activate_index(active_index, 1);
}

void Steps::set_active_index(int value) {
    activate_index(value, 1);
}

void Steps::activate_index(int value, int action) {
    if (items.empty()) {
        active_index = -1;
    } else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        active_index = value;
    }
    if ((int)statuses.size() < (int)items.size()) statuses.resize(items.size(), 0);
    for (int i = 0; i < (int)items.size(); ++i) {
        if (statuses[i] == 3) continue;
        statuses[i] = i < active_index ? 2 : (i == active_index ? 1 : 0);
    }
    ++change_count;
    last_action = action;
    if (change_cb) change_cb(id, active_index, (int)items.size(), last_action);
    invalidate();
}

void Steps::set_direction(int value) {
    direction = value == 1 ? 1 : 0;
    last_action = 1;
    invalidate();
}

void Steps::set_statuses(const std::vector<int>& values) {
    statuses.assign(items.size(), 0);
    for (int i = 0; i < (int)items.size() && i < (int)values.size(); ++i) {
        int s = values[i];
        statuses[i] = (s >= 0 && s <= 3) ? s : 0;
    }
    last_action = 1;
    invalidate();
}

int Steps::status_at(int index) const {
    if (index < 0 || index >= (int)items.size()) return 0;
    if (index < (int)statuses.size()) return statuses[index];
    if (index < active_index) return 2;
    if (index == active_index) return 1;
    return 0;
}

int Steps::failed_count() const {
    int count = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (status_at(i) == 3) ++count;
    }
    return count;
}

int Steps::step_at(int x, int y) const {
    if (items.empty() || x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    if (direction == 1) {
        float usable_h = (float)bounds.h - style.pad_top - style.pad_bottom;
        if (usable_h <= 0.0f) return -1;
        int idx = (int)(((float)y - style.pad_top) / (usable_h / (float)items.size()));
        return (idx >= 0 && idx < (int)items.size()) ? idx : -1;
    }
    float usable = (float)bounds.w - style.pad_left - style.pad_right;
    if (usable <= 0.0f) return -1;
    int idx = (int)(((float)x - style.pad_left) / (usable / (float)items.size()));
    return (idx >= 0 && idx < (int)items.size()) ? idx : -1;
}

void Steps::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color done = t->accent;
    Color error = 0xFFE5484D;
    Color normal = style.fg_color ? style.fg_color : t->text_secondary;
    Color muted = t->text_muted;
    Color border = style.border_color ? style.border_color : t->border_default;
    float circle = (std::max)(22.0f, style.font_size * 1.65f);

    ctx.push_clip({ 0, 0, (float)bounds.w, (float)bounds.h });

    if (direction == 1) {
        float usable_h = (float)bounds.h - style.pad_top - style.pad_bottom;
        float segment_h = items.empty() ? usable_h : usable_h / (float)items.size();
        float cx = (float)style.pad_left + circle * 0.5f + 4.0f;
        for (int i = 0; i < (int)items.size(); ++i) {
            float step_y = (float)style.pad_top + segment_h * (float)i + segment_h * 0.5f;
            if (i < (int)items.size() - 1) {
                float ny = (float)style.pad_top + segment_h * (float)(i + 1) + segment_h * 0.5f;
                ctx.rt->DrawLine(D2D1::Point2F(cx, step_y + circle * 0.62f),
                                 D2D1::Point2F(cx, ny - circle * 0.62f),
                                 ctx.get_brush(status_at(i) == 2 ? done : border), 2.0f);
            }
        }
        for (int i = 0; i < (int)items.size(); ++i) {
            float step_y = (float)style.pad_top + segment_h * (float)i + segment_h * 0.5f;
            int st = status_at(i);
            bool is_done = st == 2;
            bool is_active = st == 1 || i == active_index;
            bool is_error = st == 3;
            bool hot = i == m_hover_index;
            Color c = is_error ? error : (is_done || is_active ? done : muted);
            Color fill = is_active ? c : (hot ? t->button_hover : 0);
            D2D1_ELLIPSE e = D2D1::Ellipse(D2D1::Point2F(cx, step_y), circle * 0.5f, circle * 0.5f);
            if (fill) ctx.rt->FillEllipse(e, ctx.get_brush(fill));
            ctx.rt->DrawEllipse(e, ctx.get_brush(c), is_active ? 2.0f : 1.3f);
            std::wstring label = is_error ? L"!" : (is_done ? L"✓" : std::to_wstring(i + 1));
            draw_text(ctx, label, style, is_active ? 0xFFFFFFFF : c,
                      cx - circle * 0.5f, step_y - circle * 0.5f, circle, circle, 0.9f);
            float text_x = cx + circle * 0.8f;
            draw_text(ctx, items[i], style, is_active ? c : normal,
                      text_x, step_y - 22.0f, (float)bounds.w - text_x - style.pad_right,
                      22.0f, 0.94f, DWRITE_TEXT_ALIGNMENT_LEADING);
            if (i < (int)descriptions.size() && !descriptions[i].empty()) {
                draw_text(ctx, descriptions[i], style, muted,
                          text_x, step_y + 1.0f, (float)bounds.w - text_x - style.pad_right,
                          22.0f, 0.82f, DWRITE_TEXT_ALIGNMENT_LEADING);
            }
        }
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }

    float left = (float)style.pad_left;
    float usable = (float)bounds.w - style.pad_left - style.pad_right;
    float segment = items.empty() ? usable : usable / (float)items.size();
    float cy = circle * 0.5f + 4.0f;
    for (int i = 0; i < (int)items.size(); ++i) {
        float cx = left + segment * (float)i + segment * 0.5f;
        if (i < (int)items.size() - 1) {
            float nx = left + segment * (float)(i + 1) + segment * 0.5f;
            ctx.rt->DrawLine(D2D1::Point2F(cx + circle * 0.6f, cy),
                             D2D1::Point2F(nx - circle * 0.6f, cy),
                             ctx.get_brush(status_at(i) == 2 ? done : border), 2.0f);
        }
    }

    for (int i = 0; i < (int)items.size(); ++i) {
        float cx = left + segment * (float)i + segment * 0.5f;
        int st = status_at(i);
        bool is_done = st == 2;
        bool is_active = st == 1 || i == active_index;
        bool is_error = st == 3;
        bool hot = i == m_hover_index;
        Color c = is_error ? error : (is_done || is_active ? done : muted);
        Color fill = is_active ? c : (hot ? t->button_hover : 0);
        D2D1_ELLIPSE e = D2D1::Ellipse(D2D1::Point2F(cx, cy), circle * 0.5f, circle * 0.5f);
        if (fill) ctx.rt->FillEllipse(e, ctx.get_brush(fill));
        ctx.rt->DrawEllipse(e, ctx.get_brush(c), is_active ? 2.0f : 1.3f);
        std::wstring label = is_error ? L"!" : (is_done ? L"✓" : std::to_wstring(i + 1));
        draw_text(ctx, label, style, is_active ? 0xFFFFFFFF : c,
                  cx - circle * 0.5f, cy - circle * 0.5f, circle, circle, 0.9f);
        draw_text(ctx, items[i], style, is_active ? c : normal,
                  cx - segment * 0.5f + 2.0f, cy + circle * 0.55f,
                  segment - 4.0f, 24.0f, 0.92f);
        if (i < (int)descriptions.size() && !descriptions[i].empty()) {
            draw_text(ctx, descriptions[i], style, muted,
                      cx - segment * 0.5f + 2.0f, cy + circle * 0.55f + 22.0f,
                      segment - 4.0f, (float)bounds.h - cy - circle * 0.55f - 22.0f, 0.78f);
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Steps::on_mouse_move(int x, int y) {
    int idx = step_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Steps::on_mouse_leave() {
    m_hover_index = -1;
    m_press_index = -1;
    hovered = false;
    invalidate();
}

void Steps::on_mouse_down(int x, int y, MouseButton) {
    m_press_index = step_at(x, y);
    pressed = true;
    invalidate();
}

void Steps::on_mouse_up(int x, int y, MouseButton) {
    int idx = step_at(x, y);
    if (idx >= 0 && idx == m_press_index) {
        last_clicked_index = idx;
        ++click_count;
        activate_index(idx, 2);
    }
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Steps::on_key_down(int vk, int) {
    if (vk == VK_LEFT || vk == VK_UP) activate_index(active_index - 1, 3);
    else if (vk == VK_RIGHT || vk == VK_DOWN) activate_index(active_index + 1, 3);
    else if (vk == VK_HOME) activate_index(0, 3);
    else if (vk == VK_END) activate_index((int)items.size() - 1, 3);
}
