#include "element_pageheader.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void PageHeader::set_title(const std::wstring& value) {
    title = value;
    invalidate();
}

void PageHeader::set_subtitle(const std::wstring& value) {
    subtitle = value;
    invalidate();
}

void PageHeader::set_breadcrumbs(const std::vector<std::wstring>& items) {
    breadcrumbs = items;
    if (active_breadcrumb >= (int)breadcrumbs.size()) active_breadcrumb = -1;
    invalidate();
}

void PageHeader::set_actions(const std::vector<std::wstring>& items) {
    actions = items;
    if (active_action >= (int)actions.size()) active_action = -1;
    invalidate();
}

void PageHeader::set_back_text(const std::wstring& value) {
    back_text = value.empty() ? L"返回" : value;
    invalidate();
}

void PageHeader::set_active_action(int index) {
    if (actions.empty()) {
        active_action = -1;
    } else {
        if (index < 0) index = -1;
        if (index >= (int)actions.size()) index = (int)actions.size() - 1;
        active_action = index;
    }
    invalidate();
}

void PageHeader::set_active_breadcrumb(int index) {
    if (breadcrumbs.empty()) {
        active_breadcrumb = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)breadcrumbs.size()) index = (int)breadcrumbs.size() - 1;
        active_breadcrumb = index;
    }
    invalidate();
}

void PageHeader::trigger_back() {
    active_action = -2;
    ++back_clicked_count;
    invalidate();
}

void PageHeader::reset_result() {
    active_action = -1;
    active_breadcrumb = -1;
    back_clicked_count = 0;
    m_back_pressed = false;
    m_action_pressed = -1;
    m_breadcrumb_pressed = -1;
    invalidate();
}

Rect PageHeader::back_rect() const {
    int w = round_px((float)back_text.size() * style.font_size * 0.75f + 34.0f);
    if (w < 68) w = 68;
    int h = round_px(style.font_size * 2.1f);
    if (h < 32) h = 32;
    return { style.pad_left, (bounds.h - h) / 2, w, h };
}

Rect PageHeader::action_rect(int index) const {
    if (index < 0 || index >= (int)actions.size()) return { 0, 0, 0, 0 };
    int gap = 8;
    int right = bounds.w - style.pad_right;
    int h = round_px(style.font_size * 2.05f);
    if (h < 30) h = 30;
    int y = (bounds.h - h) / 2;
    for (int i = (int)actions.size() - 1; i >= index; --i) {
        int w = round_px((float)actions[i].size() * style.font_size * 0.72f + 24.0f);
        if (w < 54) w = 54;
        right -= w;
        if (i == index) return { right, y, w, h };
        right -= gap;
    }
    return { 0, 0, 0, 0 };
}

Rect PageHeader::breadcrumb_rect(int index) const {
    if (index < 0 || index >= (int)breadcrumbs.size()) return { 0, 0, 0, 0 };
    Rect br = back_rect();
    int x = br.x + br.w + 18;
    int y = (int)((float)bounds.h * 0.50f);
    int h = round_px(style.font_size * 1.55f);
    if (h < 22) h = 22;
    for (int i = 0; i <= index; ++i) {
        int w = round_px((float)breadcrumbs[i].size() * style.font_size * 0.70f + 18.0f);
        if (w < 36) w = 36;
        if (i == index) return { x, y, w, h };
        x += w + 16;
    }
    return { 0, 0, 0, 0 };
}

int PageHeader::breadcrumb_at(int x, int y) const {
    for (int i = 0; i < (int)breadcrumbs.size(); ++i) {
        if (breadcrumb_rect(i).contains(x, y)) return i;
    }
    return -1;
}

void PageHeader::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color sub_fg = t->text_secondary;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F frame = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRectangle(frame, ctx.get_brush(bg));
    ctx.rt->DrawLine(D2D1::Point2F(0.0f, (float)bounds.h - 1.0f),
                     D2D1::Point2F((float)bounds.w, (float)bounds.h - 1.0f),
                     ctx.get_brush(border), 1.0f);

    Rect br = back_rect();
    if (m_back_hover || m_back_pressed) {
        D2D1_RECT_F rr = { (float)br.x, (float)br.y, (float)(br.x + br.w), (float)(br.y + br.h) };
        ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
            ctx.get_brush(m_back_pressed ? t->button_press : t->button_hover));
    }
    draw_text(ctx, L"< " + back_text, style, m_back_hover ? t->accent : sub_fg,
              (float)br.x + 8.0f, (float)br.y, (float)br.w - 16.0f, (float)br.h);

    float title_x = (float)(br.x + br.w + 18);
    float action_left = (float)bounds.w - style.pad_right;
    for (int i = 0; i < (int)actions.size(); ++i) {
        Rect ar = action_rect(i);
        if (ar.w <= 0) continue;
        action_left = (std::min)(action_left, (float)ar.x);
        Color action_bg = (i == active_action) ? t->button_press : t->button_bg;
        if (i == m_action_hover) action_bg = t->button_hover;
        if (i == m_action_pressed) action_bg = t->button_press;
        D2D1_RECT_F rr = { (float)ar.x, (float)ar.y, (float)(ar.x + ar.w), (float)(ar.y + ar.h) };
        ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(action_bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(border), 1.0f);
        draw_text(ctx, actions[i], style, (i == active_action) ? t->accent : title_fg,
                  (float)ar.x + 8.0f, (float)ar.y, (float)ar.w - 16.0f, (float)ar.h,
                  0.92f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    float title_w = action_left - title_x - 14.0f;
    if (title_w < 80.0f) title_w = (float)bounds.w - title_x - style.pad_right;
    draw_text(ctx, title.empty() ? L"页面标题" : title, style, title_fg,
              title_x, 8.0f, title_w, (float)bounds.h * 0.48f,
              1.22f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    if (!breadcrumbs.empty()) {
        for (size_t i = 0; i < breadcrumbs.size(); ++i) {
            Rect cr = breadcrumb_rect((int)i);
            bool active = (int)i == active_breadcrumb;
            bool hot = (int)i == m_breadcrumb_hover;
            if (active || hot) {
                D2D1_RECT_F rr = { (float)cr.x, (float)cr.y,
                                   (float)(cr.x + cr.w), (float)(cr.y + cr.h) };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                    ctx.get_brush(active ? (t->accent & 0x33FFFFFF) : t->button_hover));
            }
            draw_text(ctx, breadcrumbs[i], style, active ? t->accent : (hot ? t->accent : sub_fg),
                      (float)cr.x + 6.0f, (float)cr.y, (float)cr.w - 12.0f, (float)cr.h,
                      0.92f);
            if (i + 1 < breadcrumbs.size()) {
                draw_text(ctx, L"/", style, sub_fg,
                          (float)(cr.x + cr.w + 4), (float)cr.y, 10.0f, (float)cr.h,
                          0.9f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_TEXT_ALIGNMENT_CENTER);
            }
        }
    }
    if (!subtitle.empty()) {
        float sub_x = title_x;
        if (!breadcrumbs.empty()) {
            Rect last = breadcrumb_rect((int)breadcrumbs.size() - 1);
            sub_x = (float)(last.x + last.w + 18);
        }
        draw_text(ctx, subtitle, style, sub_fg,
                  sub_x, (float)bounds.h * 0.50f, title_w - (sub_x - title_x), (float)bounds.h * 0.36f,
                  0.95f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void PageHeader::on_mouse_move(int x, int y) {
    bool hot = back_rect().contains(x, y);
    int breadcrumb_hot = breadcrumb_at(x, y);
    int action_hot = -1;
    for (int i = 0; i < (int)actions.size(); ++i) {
        if (action_rect(i).contains(x, y)) {
            action_hot = i;
            break;
        }
    }
    if (hot != m_back_hover || action_hot != m_action_hover || breadcrumb_hot != m_breadcrumb_hover) {
        m_back_hover = hot;
        m_breadcrumb_hover = breadcrumb_hot;
        m_action_hover = action_hot;
        invalidate();
    }
}

void PageHeader::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_back_hover = false;
    m_back_pressed = false;
    m_action_hover = -1;
    m_action_pressed = -1;
    m_breadcrumb_hover = -1;
    m_breadcrumb_pressed = -1;
    invalidate();
}

void PageHeader::on_mouse_down(int x, int y, MouseButton) {
    m_back_pressed = back_rect().contains(x, y);
    m_breadcrumb_pressed = breadcrumb_at(x, y);
    m_action_pressed = -1;
    for (int i = 0; i < (int)actions.size(); ++i) {
        if (action_rect(i).contains(x, y)) {
            m_action_pressed = i;
            break;
        }
    }
    pressed = true;
    invalidate();
}

void PageHeader::on_mouse_up(int x, int y, MouseButton) {
    if (m_back_pressed && back_rect().contains(x, y)) {
        trigger_back();
    } else if (m_breadcrumb_pressed >= 0 && breadcrumb_rect(m_breadcrumb_pressed).contains(x, y)) {
        set_active_breadcrumb(m_breadcrumb_pressed);
    } else if (m_action_pressed >= 0 && action_rect(m_action_pressed).contains(x, y)) {
        active_action = m_action_pressed;
        invalidate();
    }
    m_back_pressed = false;
    m_action_pressed = -1;
    m_breadcrumb_pressed = -1;
    pressed = false;
    invalidate();
}

void PageHeader::on_key_down(int vk, int) {
    if (vk == VK_BACK || vk == VK_ESCAPE) {
        trigger_back();
    } else if (vk == VK_LEFT) {
        if (!breadcrumbs.empty()) set_active_breadcrumb(active_breadcrumb <= 0 ? 0 : active_breadcrumb - 1);
    } else if (vk == VK_RIGHT) {
        if (!breadcrumbs.empty()) set_active_breadcrumb(active_breadcrumb + 1);
    } else if (vk == VK_HOME) {
        if (!breadcrumbs.empty()) set_active_breadcrumb(0);
    } else if (vk == VK_END) {
        if (!breadcrumbs.empty()) set_active_breadcrumb((int)breadcrumbs.size() - 1);
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        if (m_action_hover >= 0) active_action = m_action_hover;
        else if (m_breadcrumb_hover >= 0) set_active_breadcrumb(m_breadcrumb_hover);
        else trigger_back();
        invalidate();
    }
}
