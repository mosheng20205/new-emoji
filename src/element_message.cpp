#include "element_message.h"
#include "element_rich_text.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <map>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

std::map<UINT_PTR, Message*> g_message_timer_map;

static int round_px(float v) {
    return (int)std::lround(v);
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static Color message_color(const Theme* t, int type) {
    switch (type) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

static std::wstring message_icon(int type) {
    switch (type) {
    case 1: return L"✓";
    case 2: return L"!";
    case 3: return L"×";
    default: return L"i";
    }
}

Message::~Message() {
    stop_timer();
}

void Message::set_text(const std::wstring& value) {
    text = value;
    last_action = 1;
    invalidate();
}

void Message::set_options(int type, bool closeable, bool centered, bool rich_text, int duration, int top_offset) {
    message_type = (std::max)(0, (std::min)(3, type));
    closable = closeable;
    center = centered;
    rich = rich_text;
    duration_ms = duration < 0 ? 3000 : duration;
    offset = (std::max)(0, top_offset);
    last_action = 1;
    reset_timer();
    invalidate();
}

void Message::set_closed(bool value) {
    closed = value;
    visible = !closed;
    if (closed) stop_timer();
    else reset_timer();
    last_action = 1;
    invalidate();
}

void Message::set_stack(int index, int gap) {
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

void Message::close_message(int action) {
    if (!closable && action != 5 && action != 4) return;
    if (closed) return;
    closed = true;
    visible = false;
    last_action = action;
    ++close_count;
    stop_timer();
    if (close_cb) close_cb(id, close_count, message_type, last_action);
    invalidate();
}

void Message::reset_timer() {
    timer_elapsed_ms = 0;
    if (!closed && duration_ms > 0) ensure_timer();
    else stop_timer();
}

void Message::tick(int elapsed_ms) {
    if (closed || duration_ms <= 0) {
        stop_timer();
        return;
    }
    timer_elapsed_ms += (std::max)(1, elapsed_ms);
    if (timer_elapsed_ms >= duration_ms) close_message(5);
}

void Message::ensure_timer() {
    if (m_timer_id || !owner_hwnd || duration_ms <= 0 || closed) return;
    m_timer_id = 0xE000 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 50, nullptr);
    if (m_timer_id) g_message_timer_map[m_timer_id] = this;
}

void Message::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_message_timer_map.erase(m_timer_id);
    m_timer_id = 0;
}

Rect Message::close_rect() const {
    int size = round_px(style.font_size * 1.45f);
    if (size < 18) size = 18;
    return { bounds.w - style.pad_right - size, (bounds.h - size) / 2, size, size };
}

bool Message::close_hit(int x, int y) const {
    return closable && close_rect().contains(x, y);
}

void Message::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    if (duration_ms > 0) ensure_timer();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color accent = message_color(t, message_type);
    Color bg = dark ? 0xFF242637 : with_alpha(accent, 0x14);
    Color border = with_alpha(accent, dark ? 0x66 : 0x44);
    Color fg = style.fg_color ? style.fg_color : (dark ? t->text_primary : 0xFF303133);

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, style.corner_radius, style.corner_radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f,
        (float)bounds.h - 0.5f), style.corner_radius, style.corner_radius), ctx.get_brush(border), 1.0f);

    float icon_d = (std::max)(18.0f, style.font_size * 1.25f);
    float icon_x = (float)style.pad_left;
    float icon_y = ((float)bounds.h - icon_d) * 0.5f;
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(icon_x + icon_d * 0.5f, icon_y + icon_d * 0.5f),
        icon_d * 0.5f, icon_d * 0.5f), ctx.get_brush(accent));
    draw_rich_text(ctx, message_icon(message_type), style, 0xFFFFFFFF, icon_x, icon_y, icon_d, icon_d,
                   false, DWRITE_TEXT_ALIGNMENT_CENTER, false, 0.88f, true);

    float text_x = icon_x + icon_d + 10.0f;
    float right = closable ? (float)close_rect().x - 8.0f : (float)bounds.w - style.pad_right;
    float text_w = (std::max)(1.0f, right - text_x);
    draw_rich_text(ctx, text, style, fg, text_x, 0.0f, text_w, (float)bounds.h, rich,
                   center ? DWRITE_TEXT_ALIGNMENT_CENTER : DWRITE_TEXT_ALIGNMENT_LEADING, false, 1.0f, true);

    if (closable) {
        Rect cr = close_rect();
        Color close_fg = t->text_secondary;
        if (m_close_hover || m_close_down) {
            ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((float)cr.x + cr.w * 0.5f,
                (float)cr.y + cr.h * 0.5f), cr.w * 0.5f, cr.h * 0.5f),
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

    ctx.rt->SetTransform(saved);
}

void Message::on_mouse_move(int x, int y) {
    bool hot = close_hit(x, y);
    if (hot != m_close_hover) {
        m_close_hover = hot;
        invalidate();
    }
}

void Message::on_mouse_leave() {
    m_close_hover = false;
    m_close_down = false;
    invalidate();
}

void Message::on_mouse_down(int x, int y, MouseButton) {
    m_close_down = close_hit(x, y);
    invalidate();
}

void Message::on_mouse_up(int x, int y, MouseButton) {
    if (m_close_down && close_hit(x, y)) close_message(2);
    m_close_down = false;
    invalidate();
}

void Message::on_key_down(int vk, int) {
    if (vk == VK_ESCAPE || vk == VK_DELETE || vk == VK_RETURN || vk == VK_SPACE) close_message(3);
}
