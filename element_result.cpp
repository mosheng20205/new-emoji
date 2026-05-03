#include "element_result.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

static Color result_color(const Theme* t, int type) {
    switch (type) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

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

static void draw_wrapped_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                              Color color, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * 0.92f, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Result::set_subtitle(const std::wstring& value) {
    subtitle = value;
    last_action_source = 1;
    invalidate();
}

void Result::set_extra_content(const std::wstring& value) {
    extra_content = value;
    last_action_source = 1;
    invalidate();
}

void Result::set_type(int value) {
    if (value < 0) value = 0;
    if (value > 3) value = 3;
    result_type = value;
    last_action_source = 1;
    invalidate();
}

void Result::set_actions(const std::vector<std::wstring>& values) {
    actions = values;
    if ((int)actions.size() > 4) actions.resize(4);
    last_action = -1;
    m_hover_action = actions.empty() ? -1 : 0;
    m_press_action = -1;
    last_action_source = 1;
    invalidate();
}

void Result::trigger_action(int index, int source) {
    if (index < 0 || index >= (int)actions.size()) return;
    last_action = index;
    last_action_source = source;
    ++action_click_count;
    m_hover_action = index;
    if (action_cb) action_cb(id, last_action, (int)actions.size(), last_action_source);
    invalidate();
}

Rect Result::action_rect(int index) const {
    if (index < 0 || index >= (int)actions.size()) return {};
    int button_w = 86;
    int button_h = 32;
    int gap = 10;
    int count = (int)actions.size();
    int total_w = count * button_w + (count - 1) * gap;
    int x = (bounds.w - total_w) / 2 + index * (button_w + gap);
    int y = bounds.h - style.pad_bottom - button_h - 4;
    return { x, y, button_w, button_h };
}

int Result::action_at(int x, int y) const {
    for (int i = 0; i < (int)actions.size(); ++i) {
        if (action_rect(i).contains(x, y)) return i;
    }
    return -1;
}

void Result::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color accent = result_color(t, result_type);
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color sub_fg = t->text_secondary;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float icon_d = (std::min)((float)bounds.h * 0.36f, (float)bounds.w * 0.24f);
    if (icon_d < 42.0f) icon_d = 42.0f;
    float total_h = icon_d + style.font_size * 4.0f;
    float top = ((float)bounds.h - total_h) * 0.5f;
    if (top < 6.0f) top = 6.0f;
    float icon_x = ((float)bounds.w - icon_d) * 0.5f;

    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(icon_x + icon_d * 0.5f, top + icon_d * 0.5f),
                                      icon_d * 0.5f, icon_d * 0.5f),
                        ctx.get_brush(accent));
    std::wstring icon = result_type == 1 ? L"\u2713" : (result_type == 2 ? L"!" : (result_type == 3 ? L"x" : L"i"));
    draw_text(ctx, icon, style, 0xFFFFFFFF, icon_x, top, icon_d, icon_d, 1.55f);

    float title_y = top + icon_d + style.font_size * 0.55f;
    draw_text(ctx, text.empty() ? L"Result" : text, style, title_fg,
              (float)style.pad_left, title_y,
              (float)bounds.w - style.pad_left - style.pad_right,
              style.font_size * 1.7f, 1.12f);
    float subtitle_y = title_y + style.font_size * 1.75f;
    draw_text(ctx, subtitle, style, sub_fg,
              (float)style.pad_left, subtitle_y,
              (float)bounds.w - style.pad_left - style.pad_right,
              style.font_size * 1.55f, 0.95f);
    if (!extra_content.empty()) {
        draw_wrapped_text(ctx, extra_content, style, sub_fg,
                          (float)style.pad_left + 10.0f,
                          subtitle_y + style.font_size * 1.55f,
                          (float)bounds.w - style.pad_left - style.pad_right - 20.0f,
                          style.font_size * 2.6f);
    }

    for (int i = 0; i < (int)actions.size(); ++i) {
        Rect r = action_rect(i);
        D2D1_RECT_F rr = { (float)r.x, (float)r.y, (float)(r.x + r.w), (float)(r.y + r.h) };
        Color bg = i == 0 ? accent : (i == m_hover_action ? t->button_hover : 0);
        if (i == m_press_action) bg = t->button_press;
        Color border = i == 0 ? accent : t->border_default;
        Color fg = i == 0 ? 0xFFFFFFFF : title_fg;
        if (bg) ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ rr, 5.0f, 5.0f }, ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(D2D1_ROUNDED_RECT{ D2D1::RectF(rr.left + 0.5f, rr.top + 0.5f,
            rr.right - 0.5f, rr.bottom - 0.5f), 5.0f, 5.0f }, ctx.get_brush(border), 1.0f);
        draw_text(ctx, actions[i], style, fg, rr.left, rr.top, (float)r.w, (float)r.h, 0.92f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Result::on_mouse_move(int x, int y) {
    int idx = action_at(x, y);
    if (idx != m_hover_action) {
        m_hover_action = idx;
        invalidate();
    }
}

void Result::on_mouse_leave() {
    m_hover_action = -1;
    m_press_action = -1;
    hovered = false;
    invalidate();
}

void Result::on_mouse_down(int x, int y, MouseButton) {
    m_press_action = action_at(x, y);
    pressed = true;
    invalidate();
}

void Result::on_mouse_up(int x, int y, MouseButton) {
    int idx = action_at(x, y);
    if (idx >= 0 && idx == m_press_action) {
        trigger_action(idx, 2);
    }
    m_press_action = -1;
    pressed = false;
    invalidate();
}

void Result::on_key_down(int vk, int) {
    if (actions.empty()) return;
    int idx = m_hover_action >= 0 ? m_hover_action : (last_action >= 0 ? last_action : 0);
    if (vk == VK_LEFT || vk == VK_UP) {
        m_hover_action = (std::max)(0, idx - 1);
        invalidate();
    } else if (vk == VK_RIGHT || vk == VK_DOWN) {
        m_hover_action = (std::min)((int)actions.size() - 1, idx + 1);
        invalidate();
    } else if (vk == VK_HOME) {
        m_hover_action = 0;
        invalidate();
    } else if (vk == VK_END) {
        m_hover_action = (int)actions.size() - 1;
        invalidate();
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        trigger_action(idx, 3);
    }
}
