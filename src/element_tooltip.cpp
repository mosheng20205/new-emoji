#include "element_tooltip.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <map>

std::map<UINT_PTR, Tooltip*> g_tooltip_timer_map;

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static void keep_rect_inside_parent(const Element* el, Rect& r, int margin) {
    if (!el || !el->parent) return;
    int min_x = margin - el->bounds.x;
    int min_y = margin - el->bounds.y;
    int max_x = el->parent->bounds.w - el->bounds.x - r.w - margin;
    int max_y = el->parent->bounds.h - el->bounds.y - r.h - margin;
    if (max_x < min_x) max_x = min_x;
    if (max_y < min_y) max_y = min_y;
    if (r.x < min_x) r.x = min_x;
    if (r.x > max_x) r.x = max_x;
    if (r.y < min_y) r.y = min_y;
    if (r.y > max_y) r.y = max_y;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER,
                      DWRITE_PARAGRAPH_ALIGNMENT paragraph = DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(paragraph);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

float Tooltip::scale() const {
    float s = style.font_size / 14.0f;
    return s < 0.75f ? 0.75f : s;
}

Tooltip::~Tooltip() {
    stop_timer();
}

void Tooltip::set_content(const std::wstring& value) {
    content = value;
    last_action = 1;
    invalidate();
}

void Tooltip::set_placement(int value) {
    if (value < 0) value = 0;
    if (value > 3) value = 3;
    placement = value;
    last_action = 1;
    invalidate();
}

void Tooltip::set_open(bool value) {
    m_forced_open = value;
    stop_timer();
    apply_open(value || (hovered && hover_enabled()) || (has_focus && focus_enabled()), 1);
}

void Tooltip::set_behavior(int show_delay, int hide_delay, int trigger, int arrow) {
    show_delay_ms = show_delay < 0 ? 0 : show_delay;
    hide_delay_ms = hide_delay < 0 ? 0 : hide_delay;
    if (trigger < 0) trigger = 0;
    if (trigger > 3) trigger = 3;
    trigger_mode = trigger;
    show_arrow = arrow != 0;
    last_action = 1;
    invalidate();
}

void Tooltip::set_options(int new_placement, int open, int max_width) {
    set_placement(new_placement);
    m_max_width = max_width > 80 ? max_width : 280;
    set_open(open != 0);
}

Element* Tooltip::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h ? this : nullptr;
}

Element* Tooltip::hit_test_overlay(int, int) {
    return nullptr;
}

bool Tooltip::hover_enabled() const {
    return trigger_mode == 0 || trigger_mode == 1;
}

bool Tooltip::focus_enabled() const {
    return trigger_mode == 0 || trigger_mode == 2;
}

void Tooltip::apply_open(bool open, int action) {
    if (m_open == open) {
        last_action = action;
        invalidate();
        return;
    }
    m_open = open;
    last_action = action;
    if (open) ++open_count;
    else ++close_count;
    invalidate();
}

void Tooltip::ensure_timer(int phase, int action) {
    stop_timer();
    if (!owner_hwnd) return;
    m_timer_phase = phase;
    m_timer_elapsed = 0;
    m_pending_action = action;
    int target = phase == 1 ? show_delay_ms : hide_delay_ms;
    if (target <= 0) {
        apply_open(phase == 1, action);
        m_timer_phase = 0;
        return;
    }
    m_timer_id = 0xE900 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 33, nullptr);
    if (m_timer_id) g_tooltip_timer_map[m_timer_id] = this;
}

void Tooltip::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_tooltip_timer_map.erase(m_timer_id);
    m_timer_id = 0;
    m_timer_phase = 0;
    m_timer_elapsed = 0;
}

void Tooltip::schedule_open(int action) {
    if (m_forced_open || m_open) {
        apply_open(true, action);
        return;
    }
    ensure_timer(1, action);
}

void Tooltip::schedule_close(int action) {
    if (m_forced_open) {
        stop_timer();
        apply_open(true, action);
        return;
    }
    ensure_timer(2, action);
}

void Tooltip::trigger_open(bool open, int action) {
    m_forced_open = open;
    stop_timer();
    apply_open(open, action);
}

void Tooltip::tick(int elapsed_ms) {
    if (m_timer_phase == 0) {
        stop_timer();
        return;
    }
    m_timer_elapsed += (std::max)(1, elapsed_ms);
    int target = m_timer_phase == 1 ? show_delay_ms : hide_delay_ms;
    if (m_timer_elapsed >= target) {
        int phase = m_timer_phase;
        int action = m_pending_action ? m_pending_action : 6;
        stop_timer();
        apply_open(phase == 1, action == 0 ? 6 : action);
        last_action = 6;
    }
}

void Tooltip::update_popup_rect() {
    float s = scale();
    int gap = round_px(8.0f * s);
    int pw = round_px((float)(std::max)(120, (int)content.size() * 8 + 28) * s);
    int ph = round_px(36.0f * s);
    if (pw > round_px((float)m_max_width * s)) pw = round_px((float)m_max_width * s);
    int x = (bounds.w - pw) / 2;
    int y = -ph - gap;
    if (placement == 0) {
        x = -pw - gap;
        y = (bounds.h - ph) / 2;
    } else if (placement == 1) {
        x = bounds.w + gap;
        y = (bounds.h - ph) / 2;
    } else if (placement == 3) {
        x = (bounds.w - pw) / 2;
        y = bounds.h + gap;
    }
    m_popup_rect = { x, y, pw, ph };
    keep_rect_inside_parent(this, m_popup_rect, round_px(6.0f * s));
}

void Tooltip::draw_trigger(RenderContext& ctx) {
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF313244 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : (m_open || hovered ? t->accent : t->border_default);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f * scale();

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);
    draw_text(ctx, text.empty() ? L"Tooltip" : text, style, fg,
              (float)style.pad_left, 0.0f,
              (float)bounds.w - style.pad_left - style.pad_right,
              (float)bounds.h);
}

void Tooltip::draw_popup(RenderContext& ctx) {
    if (!m_open) return;
    update_popup_rect();

    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFFE5EAF3 : 0xFF303133;
    Color fg = dark ? 0xFF303133 : 0xFFFFFFFF;
    float radius = 4.0f * scale();

    D2D1_RECT_F rect = {
        (float)m_popup_rect.x,
        (float)m_popup_rect.y,
        (float)(m_popup_rect.x + m_popup_rect.w),
        (float)(m_popup_rect.y + m_popup_rect.h)
    };
    if (show_arrow) draw_arrow(ctx, bg);
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    draw_text(ctx, content.empty() ? L"Tooltip content" : content, style, fg,
              rect.left + 10.0f * scale(), rect.top,
              (float)m_popup_rect.w - 20.0f * scale(), (float)m_popup_rect.h,
              DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
              DWRITE_WORD_WRAPPING_NO_WRAP);
}

void Tooltip::draw_arrow(RenderContext& ctx, Color bg) {
    float s = scale();
    float size = 9.0f * s;
    float cx = (float)m_popup_rect.x + m_popup_rect.w * 0.5f;
    float cy = (float)m_popup_rect.y + m_popup_rect.h * 0.5f;
    if (placement == 0) cx = (float)m_popup_rect.x + m_popup_rect.w;
    else if (placement == 1) cx = (float)m_popup_rect.x;
    else if (placement == 2) cy = (float)m_popup_rect.y + m_popup_rect.h;
    else cy = (float)m_popup_rect.y;

    D2D1_RECT_F diamond = {
        cx - size * 0.5f, cy - size * 0.5f,
        cx + size * 0.5f, cy + size * 0.5f
    };
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Rotation(45.0f, D2D1::Point2F(cx, cy)));
    ctx.rt->FillRectangle(diamond, ctx.get_brush(bg));
    ctx.rt->SetTransform(saved);
}

void Tooltip::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));
    draw_trigger(ctx);
    ctx.rt->SetTransform(saved);
}

void Tooltip::paint_overlay(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));
    draw_popup(ctx);
    ctx.rt->SetTransform(saved);
}

void Tooltip::on_mouse_enter() {
    hovered = true;
    if (hover_enabled()) schedule_open(2);
    invalidate();
}

void Tooltip::on_mouse_leave() {
    hovered = false;
    if (hover_enabled()) schedule_close(2);
    invalidate();
}

void Tooltip::on_mouse_down(int, int, MouseButton) {
    pressed = true;
    invalidate();
}

void Tooltip::on_mouse_up(int, int, MouseButton) {
    pressed = false;
    if (hovered && hover_enabled()) schedule_open(2);
    invalidate();
}

void Tooltip::on_focus() {
    Element::on_focus();
    if (focus_enabled()) schedule_open(3);
}

void Tooltip::on_blur() {
    Element::on_blur();
    if (focus_enabled()) schedule_close(3);
}

void Tooltip::on_key_down(int vk, int) {
    if (vk == VK_ESCAPE) {
        m_forced_open = false;
        stop_timer();
        apply_open(false, 4);
    } else if ((vk == VK_RETURN || vk == VK_SPACE) && focus_enabled()) {
        schedule_open(4);
    }
}
