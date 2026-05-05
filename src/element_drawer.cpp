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

static Element* child_by_id(Element& el, int id) {
    if (id <= 0) return nullptr;
    for (auto& ch : el.children) {
        if (ch && ch->id == id) return ch.get();
    }
    return nullptr;
}

static const Element* child_by_id_const(const Element& el, int id) {
    if (id <= 0) return nullptr;
    for (const auto& ch : el.children) {
        if (ch && ch->id == id) return ch.get();
    }
    return nullptr;
}

static bool child_has_visible_content(const Element& el, int id) {
    const Element* child = child_by_id_const(el, id);
    if (!child) return false;
    for (const auto& ch : child->children) {
        if (ch && ch->visible) return true;
    }
    return false;
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
    if (value) {
        close_pending = false;
        pending_close_action = 0;
    }
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
    if (size > 0) {
        size_mode = 0;
        size_value = size;
        set_logical_bounds({ logical_bounds.x, logical_bounds.y, size, size });
    }
    if (open) {
        close_pending = false;
        pending_close_action = 0;
    }
    animation_progress = open ? 0 : 100;
    last_action = 1;
    if (open) ensure_timer();
    else stop_timer();
    invalidate();
}

void Drawer::set_advanced_options(bool show_header_value, bool show_close_value,
                                  bool close_on_escape_value, int content_padding_value,
                                  int footer_height_value, int size_mode_value,
                                  int size_value_value) {
    show_header = show_header_value;
    show_close = show_close_value;
    close_on_escape = close_on_escape_value;
    if (content_padding_value >= 0) content_padding = content_padding_value;
    if (footer_height_value >= 0) footer_height = footer_height_value;
    size_mode = size_mode_value == 1 ? 1 : 0;
    if (size_value_value > 0) {
        size_value = size_value_value;
        if (size_mode == 0) {
            set_logical_bounds({ logical_bounds.x, logical_bounds.y,
                                 size_value_value, size_value_value });
        }
    }
    last_action = 1;
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
    if (before_close_cb) {
        int allow = before_close_cb(id, action);
        if (!allow) {
            close_pending = true;
            pending_close_action = action;
            last_action = action;
            invalidate();
            return;
        }
    }
    visible = false;
    animation_progress = 0;
    close_pending = false;
    pending_close_action = 0;
    last_action = action;
    ++close_count;
    stop_timer();
    if (close_cb) close_cb(id, close_count, placement, last_action);
    invalidate();
}

void Drawer::confirm_pending_close(bool allow) {
    if (!close_pending) return;
    int action = pending_close_action ? pending_close_action : 4;
    close_pending = false;
    pending_close_action = 0;
    if (allow) {
        visible = false;
        animation_progress = 0;
        last_action = action;
        ++close_count;
        stop_timer();
        if (close_cb) close_cb(id, close_count, placement, last_action);
    } else {
        last_action = 1;
    }
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
    Rect content = content_rect_in_drawer();
    Rect footer = footer_rect_in_drawer();
    for (auto& ch : children) {
        if (!ch || !ch->visible) continue;
        if (ch->id == content_parent_id) {
            ch->layout(content);
        } else if (ch->id == footer_parent_id) {
            ch->layout(footer);
        } else {
            ch->layout(ch->bounds);
        }
    }
}

void Drawer::update_layout() {
    float s = scale();
    int default_side = round_px(300.0f * s);
    int base_w = size_value > 0 ? size_value : logical_bounds.w;
    int base_h = size_value > 0 ? size_value : logical_bounds.h;
    int panel_w = base_w > 0 ? round_px((float)base_w * s) : default_side;
    int panel_h = base_h > 0 ? round_px((float)base_h * s) : default_side;

    if (placement == 0 || placement == 1) {
        if (size_mode == 1 && size_value > 0) {
            int pct = (std::max)(10, (std::min)(100, size_value));
            panel_w = round_px((float)bounds.w * (float)pct / 100.0f);
        }
        if (panel_w > bounds.w) panel_w = bounds.w;
        panel_h = bounds.h;
        int x = placement == 0 ? 0 : bounds.w - panel_w;
        m_panel_rect = { x, 0, panel_w, panel_h };
    } else {
        panel_w = bounds.w;
        if (size_mode == 1 && size_value > 0) {
            int pct = (std::max)(10, (std::min)(100, size_value));
            panel_h = round_px((float)bounds.h * (float)pct / 100.0f);
        }
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

Rect Drawer::footer_rect_in_drawer() const {
    if (!child_has_visible_content(*this, footer_parent_id)) return {};
    float s = scale();
    int footer_h = round_px((float)(footer_height > 0 ? footer_height : 58) * s);
    int pad = round_px((float)content_padding * s);
    Rect r = {
        m_panel_rect.x + pad,
        m_panel_rect.y + m_panel_rect.h - footer_h,
        m_panel_rect.w - pad * 2,
        footer_h
    };
    if (r.w < 0) r.w = 0;
    if (r.h < 0) r.h = 0;
    return r;
}

Rect Drawer::content_rect_in_drawer() const {
    float s = scale();
    int pad = round_px((float)content_padding * s);
    int header_h = show_header ? round_px(54.0f * s) : 0;
    int top_gap = show_header ? round_px(16.0f * s) : pad;
    int footer_h = footer_rect_in_drawer().h;
    Rect r = {
        m_panel_rect.x + pad,
        m_panel_rect.y + header_h + top_gap,
        m_panel_rect.w - pad * 2,
        m_panel_rect.h - header_h - top_gap - pad - footer_h
    };
    if (r.w < 0) r.w = 0;
    if (r.h < 0) r.h = 0;
    return r;
}

Drawer::Part Drawer::part_at(int x, int y) const {
    if (show_header && show_close && closable && m_close_rect.contains(x, y)) return PartClose;
    if (m_panel_rect.contains(x, y)) return PartPanel;
    return modal ? PartMask : PartNone;
}

Element* Drawer::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    Part part = part_at(lx, ly);
    if (part == PartPanel) {
        for (auto it = children.rbegin(); it != children.rend(); ++it) {
            if (!(*it)->visible) continue;
            Element* hit = (*it)->hit_test(lx, ly);
            if (hit) return hit;
        }
    }
    return part != PartNone ? this : nullptr;
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

    float pad = (float)content_padding * s;
    float header_h = 54.0f * s;
    int dx = panel_rect.x - m_panel_rect.x;
    int dy = panel_rect.y - m_panel_rect.y;
    Rect old_panel = m_panel_rect;
    Rect old_close = m_close_rect;
    m_panel_rect = panel_rect;
    m_close_rect.x += dx;
    m_close_rect.y += dy;
    if (Element* content_el = child_by_id(*this, content_parent_id)) {
        if (content_el->visible) content_el->layout(content_rect_in_drawer());
    }
    if (Element* footer_el = child_by_id(*this, footer_parent_id)) {
        if (footer_el->visible) footer_el->layout(footer_rect_in_drawer());
    }

    if (show_header) {
        draw_text(ctx, title.empty() ? L"抽屉" : title, style, title_fg,
                  panel.left + pad, panel.top + 14.0f * s,
                  (float)m_panel_rect.w - pad * 2.0f - (show_close ? 28.0f * s : 0.0f),
                  26.0f * s, 1.1f, DWRITE_TEXT_ALIGNMENT_LEADING,
                  DWRITE_PARAGRAPH_ALIGNMENT_CENTER, DWRITE_WORD_WRAPPING_NO_WRAP);
    }

    if (show_header && show_close && closable) {
        Color close_fg = m_hover_part == PartClose ? t->accent : t->text_secondary;
        float cx = (float)m_close_rect.x + m_close_rect.w * 0.5f;
        float cy = (float)m_close_rect.y + m_close_rect.h * 0.5f;
        float cs = 6.0f * s;
        ctx.rt->DrawLine(D2D1::Point2F(cx - cs, cy - cs), D2D1::Point2F(cx + cs, cy + cs),
                         ctx.get_brush(close_fg), 1.5f * s);
        ctx.rt->DrawLine(D2D1::Point2F(cx + cs, cy - cs), D2D1::Point2F(cx - cs, cy + cs),
                         ctx.get_brush(close_fg), 1.5f * s);
    }

    if (show_header) {
        ctx.rt->DrawLine(D2D1::Point2F(panel.left, panel.top + header_h),
                         D2D1::Point2F(panel.right, panel.top + header_h),
                         ctx.get_brush(border), 1.0f);
    }

    bool has_content_slot = child_has_visible_content(*this, content_parent_id);
    bool has_footer_slot = child_has_visible_content(*this, footer_parent_id);
    Rect content = content_rect_in_drawer();
    if (!has_content_slot) {
        draw_text(ctx, text, style, body_fg,
                  (float)content.x, (float)content.y,
                  (float)content.w, (float)content.h);
    }

    if (Element* content_el = child_by_id(*this, content_parent_id)) {
        if (content_el->visible) content_el->paint(ctx);
    }

    if (has_footer_slot) {
        Rect footer = footer_rect_in_drawer();
        ctx.rt->DrawLine(D2D1::Point2F((float)m_panel_rect.x, (float)footer.y),
                         D2D1::Point2F((float)(m_panel_rect.x + m_panel_rect.w), (float)footer.y),
                         ctx.get_brush(border), 1.0f);
        if (Element* footer_el = child_by_id(*this, footer_parent_id)) {
            if (footer_el->visible) footer_el->paint(ctx);
        }
    }

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
    if (close_on_escape && closable && vk == VK_ESCAPE) {
        close_drawer(3);
    }
}
