#include "element_notification.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <map>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

std::map<UINT_PTR, Notification*> g_notification_timer_map;

static int round_px(float v) {
    return (int)std::lround(v);
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color notify_color(const Theme* t, int type) {
    switch (type) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

Notification::~Notification() {
    stop_timer();
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Notification::set_body(const std::wstring& value) {
    body = value;
    last_action = 1;
    invalidate();
}

void Notification::set_type(int value) {
    if (value < 0) value = 0;
    if (value > 3) value = 3;
    notify_type = value;
    last_action = 1;
    invalidate();
}

void Notification::set_closable(bool value) {
    closable = value;
    last_action = 1;
    invalidate();
}

void Notification::set_closed(bool value) {
    closed = value;
    visible = !closed;
    if (closed) stop_timer();
    else reset_timer();
    last_action = 1;
    invalidate();
}

void Notification::set_options(int type, bool closeable, int duration) {
    set_type(type);
    closable = closeable;
    duration_ms = duration < 0 ? 0 : duration;
    reset_timer();
    last_action = 1;
    invalidate();
}

void Notification::set_stack(int index, int gap) {
    if (!m_has_base_y) {
        m_base_y = logical_bounds.y;
        m_has_base_y = true;
    }
    stack_index = (std::max)(0, index);
    stack_gap = (std::max)(0, gap);
    Rect r = logical_bounds;
    r.y = m_base_y + stack_index * (logical_bounds.h + stack_gap);
    set_logical_bounds(r);
    last_action = 1;
    invalidate();
}

void Notification::close_notification(int action) {
    if (!closable && action != 5) return;
    if (closed) return;
    closed = true;
    visible = false;
    last_action = action;
    ++close_count;
    stop_timer();
    if (close_cb) close_cb(id, close_count, notify_type, last_action);
    invalidate();
}

void Notification::reset_timer() {
    timer_elapsed_ms = 0;
    if (!closed && duration_ms > 0) ensure_timer();
    else stop_timer();
}

void Notification::tick(int elapsed_ms) {
    if (closed || duration_ms <= 0) {
        stop_timer();
        return;
    }
    timer_elapsed_ms += (std::max)(1, elapsed_ms);
    if (timer_elapsed_ms >= duration_ms) {
        close_notification(5);
        return;
    }
    invalidate();
}

void Notification::ensure_timer() {
    if (m_timer_id || !owner_hwnd || duration_ms <= 0 || closed) return;
    m_timer_id = 0xD000 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 50, nullptr);
    if (m_timer_id) g_notification_timer_map[m_timer_id] = this;
}

void Notification::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_notification_timer_map.erase(m_timer_id);
    m_timer_id = 0;
}

Rect Notification::close_rect() const {
    int size = round_px(style.font_size * 1.45f);
    if (size < 18) size = 18;
    int x = bounds.w - style.pad_right - size;
    int y = style.pad_top;
    return { x, y, size, size };
}

bool Notification::close_hit(int x, int y) const {
    return closable && close_rect().contains(x, y);
}

void Notification::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    if (duration_ms > 0) ensure_timer();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color accent = notify_color(t, notify_type);
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = t->text_secondary;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);
    ctx.rt->FillRectangle(D2D1::RectF(0.0f, 0.0f, 4.0f, (float)bounds.h), ctx.get_brush(accent));

    float icon_d = (std::max)(18.0f, style.font_size * 1.35f);
    float icon_x = (float)style.pad_left;
    float icon_y = (float)style.pad_top + 2.0f;
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(icon_x + icon_d * 0.5f, icon_y + icon_d * 0.5f),
                                      icon_d * 0.5f, icon_d * 0.5f),
                        ctx.get_brush(with_alpha(accent, 0x33)));
    ctx.rt->DrawEllipse(D2D1::Ellipse(D2D1::Point2F(icon_x + icon_d * 0.5f, icon_y + icon_d * 0.5f),
                                      icon_d * 0.5f, icon_d * 0.5f),
                        ctx.get_brush(accent), 1.0f);

    float text_x = icon_x + icon_d + 10.0f;
    float right = closable ? (float)close_rect().x - 8.0f : (float)bounds.w - style.pad_right;
    float text_w = right - text_x;
    if (text_w < 1.0f) text_w = 1.0f;
    draw_text(ctx, text.empty() ? L"Notification" : text, style, title_fg,
              text_x, (float)style.pad_top, text_w, style.font_size * 1.5f, 1.05f);
    draw_text(ctx, body, style, body_fg,
              text_x, (float)style.pad_top + style.font_size * 1.75f,
              text_w, (float)bounds.h - style.pad_top - style.pad_bottom - style.font_size * 1.75f,
              0.95f, DWRITE_TEXT_ALIGNMENT_LEADING, DWRITE_WORD_WRAPPING_WRAP);
    if (duration_ms > 0) {
        float bar_w = (float)bounds.w - 12.0f;
        float progress = 1.0f - (float)timer_elapsed_ms / (float)(std::max)(1, duration_ms);
        if (progress < 0.0f) progress = 0.0f;
        if (progress > 1.0f) progress = 1.0f;
        D2D1_RECT_F bar = { 6.0f, (float)bounds.h - 5.0f, 6.0f + bar_w, (float)bounds.h - 3.0f };
        ctx.rt->FillRoundedRectangle(ROUNDED(bar, 1.0f, 1.0f), ctx.get_brush(with_alpha(accent, 0x22)));
        D2D1_RECT_F fill = { bar.left, bar.top, bar.left + bar_w * progress, bar.bottom };
        ctx.rt->FillRoundedRectangle(ROUNDED(fill, 1.0f, 1.0f), ctx.get_brush(with_alpha(accent, 0xAA)));
    }

    if (closable) {
        Rect cr = close_rect();
        Color close_fg = t->text_secondary;
        if (m_close_hover || m_close_down) {
            ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((float)cr.x + cr.w * 0.5f,
                                                            (float)cr.y + cr.h * 0.5f),
                                              cr.w * 0.5f, cr.h * 0.5f),
                                ctx.get_brush(with_alpha(close_fg, m_close_down ? 0x44 : 0x22)));
        }
        float cx = (float)cr.x + cr.w * 0.5f;
        float cy = (float)cr.y + cr.h * 0.5f;
        float s = (std::max)(4.0f, style.font_size * 0.32f);
        ctx.rt->DrawLine(D2D1::Point2F(cx - s, cy - s), D2D1::Point2F(cx + s, cy + s),
                         ctx.get_brush(close_fg), 1.2f);
        ctx.rt->DrawLine(D2D1::Point2F(cx + s, cy - s), D2D1::Point2F(cx - s, cy + s),
                         ctx.get_brush(close_fg), 1.2f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Notification::on_mouse_move(int x, int y) {
    bool hot = close_hit(x, y);
    if (hot != m_close_hover) {
        m_close_hover = hot;
        invalidate();
    }
}

void Notification::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_close_hover = false;
    m_close_down = false;
    invalidate();
}

void Notification::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_close_down = close_hit(x, y);
    invalidate();
}

void Notification::on_mouse_up(int x, int y, MouseButton) {
    if (m_close_down && close_hit(x, y)) {
        close_notification(2);
    }
    pressed = false;
    m_close_down = false;
    invalidate();
}

void Notification::on_key_down(int vk, int) {
    if (vk == VK_ESCAPE || vk == VK_DELETE || vk == VK_RETURN || vk == VK_SPACE) {
        close_notification(3);
    }
}
