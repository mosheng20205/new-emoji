#include "element_drawer.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <map>

std::map<UINT_PTR, Drawer*> g_drawer_timer_map;

static int round_px(float v) {
    return (int)std::lround(v);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT paragraph = DWRITE_PARAGRAPH_ALIGNMENT_NEAR,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(paragraph);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

float Drawer::scale() const {
    float s = style.font_size / 14.0f;
    return s < 0.75f ? 0.75f : s;
}

Drawer::~Drawer() {
    stop_timer();
}

void Drawer::set_title(const std::wstring& value) {
    title = value;
    last_action = 1;
    invalidate();
}

void Drawer::set_body(const std::wstring& value) {
    text = value;
    last_action = 1;
    invalidate();
}

void Drawer::set_placement(int value) {
    if (value < 0) value = 0;
    if (value > 3) value = 3;
    placement = value;
    last_action = 1;
    invalidate();
}

void Drawer::set_modal(bool value) {
    modal = value;
    last_action = 1;
    invalidate();
}

void Drawer::set_closable(bool value) {
    closable = value;
    last_action = 1;
    invalidate();
}

void Drawer::set_open(bool value) {
    visible = value;
    animation_progress = value ? 0 : 100;
    last_action = 1;
    if (value) ensure_timer();
    else stop_timer();
    invalidate();
}

void Drawer::set_options(int new_placement, bool open, bool modal_value,
                         bool closable_value, bool mask_close, int size) {
    set_placement(new_placement);
    visible = open;
    modal = modal_value;
    closable = closable_value;
    close_on_mask = mask_close;
    if (size > 0) set_logical_bounds({ logical_bounds.x, logical_bounds.y, size, size });
    animation_progress = open ? 0 : 100;
    last_action = 1;
    if (open) ensure_timer();
    else stop_timer();
    invalidate();
}

void Drawer::set_animation(int duration_ms) {
    animation_ms = duration_ms < 0 ? 0 : duration_ms;
    last_action = 1;
    invalidate();
}

void Drawer::close_drawer(int action) {
    if (!closable && action != 5) return;
    if (!visible) return;
    visible = false;
    animation_progress = 0;
    last_action = action;
    ++close_count;
    stop_timer();
    if (close_cb) close_cb(id, close_count, placement, last_action);
    invalidate();
}

void Drawer::tick(int elapsed_ms) {
    if (!visible) {
        stop_timer();
        return;
    }
    if (animation_ms <= 0) animation_progress = 100;
    else animation_progress += (std::max)(1, elapsed_ms) * 100 / animation_ms;
    if (animation_progress >= 100) {
        animation_progress = 100;
        stop_timer();
    }
    ++tick_count;
    last_action = 6;
    invalidate();
}

void Drawer::ensure_timer() {
    if (m_timer_id || !owner_hwnd || !visible || animation_progress >= 100) return;
    m_timer_id = 0xE800 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 33, nullptr);
    if (m_timer_id) g_drawer_timer_map[m_timer_id] = this;
}

void Drawer::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_drawer_timer_map.erase(m_timer_id);
    m_timer_id = 0;
}

void Drawer::layout(const Rect& available) {
    bounds = available;
    update_layout();
}

void Drawer::update_layout() {
    float s = scale();
    int default_side = round_px(300.0f * s);
    int panel_w = logical_bounds.w > 0 ? round_px((float)logical_bounds.w * s) : default_side;
    int panel_h = logical_bounds.h > 0 ? round_px((float)logical_bounds.h * s) : default_side;

    if (placement == 0 || placement == 1) {
        if (panel_w > bounds.w) panel_w = bounds.w;
        panel_h = bounds.h;
        int x = placement == 0 ? 0 : bounds.w - panel_w;
        m_panel_rect = { x, 0, panel_w, panel_h };
    } else {
        panel_w = bounds.w;
        if (panel_h > bounds.h) panel_h = bounds.h;
        int y = placement == 2 ? 0 : bounds.h - panel_h;
        m_panel_rect = { 0, y, panel_w, panel_h };
    }

    int close_size = round_px(28.0f * s);
    int pad = round_px(16.0f * s);
    m_close_rect = {
        m_panel_rect.x + m_panel_rect.w - pad - close_size,
        m_panel_rect.y + round_px(12.0f * s),
        close_size,
        close_size
    };
}

Drawer::Part Drawer::part_at(int x, int y) const {
    if (closable && m_close_rect.contains(x, y)) return PartClose;
    if (m_panel_rect.contains(x, y)) return PartPanel;
    return modal ? PartMask : PartNone;
}

Element* Drawer::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

void Drawer::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    update_layout();
    if (animation_progress < 100) ensure_timer();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();

    if (modal) {
        D2D1_RECT_F overlay = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(overlay, ctx.get_brush(dark ? 0x99000000 : 0x66000000));
    }

    Rect panel_rect = m_panel_rect;
    float p = (float)animation_progress / 100.0f;
    if (p < 0.0f) p = 0.0f;
    if (p > 1.0f) p = 1.0f;
    if (placement == 0) panel_rect.x -= (int)((1.0f - p) * panel_rect.w);
    else if (placement == 1) panel_rect.x += (int)((1.0f - p) * panel_rect.w);
    else if (placement == 2) panel_rect.y -= (int)((1.0f - p) * panel_rect.h);
    else panel_rect.y += (int)((1.0f - p) * panel_rect.h);
    D2D1_RECT_F panel = {
        (float)panel_rect.x,
        (float)panel_rect.y,
        (float)(panel_rect.x + panel_rect.w),
        (float)(panel_rect.y + panel_rect.h)
    };
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = t->text_secondary;

    ctx.rt->FillRectangle(panel, ctx.get_brush(bg));
    ctx.rt->DrawRectangle(D2D1::RectF(panel.left + 0.5f, panel.top + 0.5f,
        panel.right - 0.5f, panel.bottom - 0.5f), ctx.get_brush(border), 1.0f);

    float pad = 20.0f * s;
    float header_h = 54.0f * s;
    int dx = panel_rect.x - m_panel_rect.x;
    int dy = panel_rect.y - m_panel_rect.y;
    Rect old_panel = m_panel_rect;
    Rect old_close = m_close_rect;
    m_panel_rect = panel_rect;
    m_close_rect.x += dx;
    m_close_rect.y += dy;

    draw_text(ctx, title.empty() ? L"Drawer" : title, style, title_fg,
              panel.left + pad, panel.top + 14.0f * s,
              (float)m_panel_rect.w - pad * 2.0f - 28.0f * s,
              26.0f * s, 1.1f, DWRITE_TEXT_ALIGNMENT_LEADING,
              DWRITE_PARAGRAPH_ALIGNMENT_CENTER, DWRITE_WORD_WRAPPING_NO_WRAP);

    if (closable) {
        Color close_fg = m_hover_part == PartClose ? t->accent : t->text_secondary;
        float cx = (float)m_close_rect.x + m_close_rect.w * 0.5f;
        float cy = (float)m_close_rect.y + m_close_rect.h * 0.5f;
        float cs = 6.0f * s;
        ctx.rt->DrawLine(D2D1::Point2F(cx - cs, cy - cs), D2D1::Point2F(cx + cs, cy + cs),
                         ctx.get_brush(close_fg), 1.5f * s);
        ctx.rt->DrawLine(D2D1::Point2F(cx + cs, cy - cs), D2D1::Point2F(cx - cs, cy + cs),
                         ctx.get_brush(close_fg), 1.5f * s);
    }

    ctx.rt->DrawLine(D2D1::Point2F(panel.left, panel.top + header_h),
                     D2D1::Point2F(panel.right, panel.top + header_h),
                     ctx.get_brush(border), 1.0f);
    draw_text(ctx, text, style, body_fg,
              panel.left + pad, panel.top + header_h + 16.0f * s,
              (float)m_panel_rect.w - pad * 2.0f,
              (float)m_panel_rect.h - header_h - 32.0f * s);

    ctx.rt->SetTransform(saved);
    m_panel_rect = old_panel;
    m_close_rect = old_close;
}

void Drawer::on_mouse_move(int x, int y) {
    Part part = part_at(x, y);
    if (part != m_hover_part) {
        m_hover_part = part;
        invalidate();
    }
}

void Drawer::on_mouse_leave() {
    m_hover_part = PartNone;
    m_press_part = PartNone;
    invalidate();
}

void Drawer::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y);
    invalidate();
}

void Drawer::on_mouse_up(int x, int y, MouseButton) {
    Part part = part_at(x, y);
    if (m_press_part == PartClose && part == PartClose) {
        close_drawer(2);
    } else if (m_press_part == PartMask && part == PartMask && close_on_mask) {
        close_drawer(5);
    }
    m_press_part = PartNone;
    m_hover_part = part;
    invalidate();
}

void Drawer::on_key_down(int vk, int) {
    if (closable && vk == VK_ESCAPE) {
        close_drawer(3);
    }
}
