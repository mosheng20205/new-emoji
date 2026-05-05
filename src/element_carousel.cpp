#include "element_carousel.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <map>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

std::map<UINT_PTR, Carousel*> g_carousel_timer_map;

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static float rect_width(const D2D1_RECT_F& r) {
    return r.right - r.left;
}

static float rect_height(const D2D1_RECT_F& r) {
    return r.bottom - r.top;
}

static D2D1_RECT_F rect_from_rect(const Rect& r) {
    return D2D1::RectF((float)r.x, (float)r.y, (float)(r.x + r.w), (float)(r.y + r.h));
}

static D2D1_RECT_F inset_rect(D2D1_RECT_F r, float x, float y) {
    r.left += x;
    r.right -= x;
    r.top += y;
    r.bottom -= y;
    if (r.right < r.left) r.right = r.left;
    if (r.bottom < r.top) r.bottom = r.top;
    return r;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

Carousel::~Carousel() {
    if (m_timer_id && owner_hwnd) {
        KillTimer(owner_hwnd, m_timer_id);
    }
    if (m_timer_id) {
        g_carousel_timer_map.erase(m_timer_id);
    }
    m_timer_id = 0;
}

void CALLBACK Carousel::carousel_timer(HWND, UINT, UINT_PTR id, DWORD) {
    auto it = g_carousel_timer_map.find(id);
    if (it != g_carousel_timer_map.end() && it->second) {
        it->second->tick(33);
    }
}

void Carousel::ensure_timer() {
    if (m_timer_id || !owner_hwnd) return;
    m_timer_id = 0xC000 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 33, nullptr);
    if (m_timer_id) g_carousel_timer_map[m_timer_id] = this;
}

void Carousel::stop_timer_if_idle() {
    bool animating = transition_progress < 100;
    if (m_timer_id && owner_hwnd && !autoplay && !animating) {
        KillTimer(owner_hwnd, m_timer_id);
        g_carousel_timer_map.erase(m_timer_id);
        m_timer_id = 0;
    }
}

void Carousel::set_items(const std::vector<std::wstring>& values) {
    items = values;
    if (items.empty()) {
        active_index = -1;
        previous_index = -1;
        transition_progress = 100;
        transition_elapsed_ms = transition_ms;
    } else {
        set_active_index_with_action(active_index < 0 ? 0 : active_index, 0, 0);
    }
}

void Carousel::set_active_index(int index) {
    set_active_index_with_action(index, 1, index >= active_index ? 1 : -1);
}

void Carousel::set_active_index_with_action(int index, int action, int direction_hint) {
    int old_index = active_index;
    int next_index = index;
    if (items.empty()) {
        active_index = -1;
        previous_index = -1;
    } else {
        if (loop) {
            int count = (int)items.size();
            while (next_index < 0) next_index += count;
            while (next_index >= count) next_index -= count;
        }
        if (next_index < 0) next_index = 0;
        if (next_index >= (int)items.size()) next_index = (int)items.size() - 1;
        active_index = next_index;
    }
    if (old_index != active_index) {
        start_transition(old_index, active_index, action, direction_hint);
    } else if (action != 0) {
        last_action = action;
    }
    autoplay_elapsed_ms = 0;
    invalidate();
}

void Carousel::start_transition(int old_index, int new_index, int action, int direction_hint) {
    previous_index = old_index >= 0 ? old_index : new_index;
    last_action = action;
    ++change_count;
    transition_direction = direction_hint < 0 ? -1 : 1;
    transition_elapsed_ms = 0;
    transition_progress = transition_ms <= 0 ? 100 : 0;
    if (transition_progress < 100) ensure_timer();
}

void Carousel::set_indicator_position(int value) {
    indicator_position = value == 1 ? 1 : 0;
    invalidate();
}

void Carousel::set_options(int loop_enabled, int indicator_pos, int arrows_visible, int indicators_visible) {
    loop = loop_enabled != 0;
    indicator_position = indicator_pos == 1 ? 1 : 0;
    show_indicators = indicators_visible != 0;
    show_arrows = arrows_visible != 0;
    arrow_mode = show_arrows ? 1 : 2;
    set_active_index(active_index);
    invalidate();
}

void Carousel::set_behavior(int trigger, int arrows, int dir, int type, int pause) {
    trigger_mode = trigger == 0 ? 0 : 1;
    if (arrows < 0) arrows = 0;
    if (arrows > 2) arrows = 2;
    arrow_mode = arrows;
    show_arrows = arrow_mode != 2;
    direction = dir == 1 ? 1 : 0;
    carousel_type = type == 1 ? 1 : 0;
    pause_on_hover = pause != 0;
    invalidate();
}

void Carousel::set_visual(Color text, int alpha, int font_size, Color odd, Color even,
                          Color panel, Color active_dot, Color inactive_dot, int card_scale) {
    text_color = text;
    if (alpha < 0) alpha = 0;
    if (alpha > 255) alpha = 255;
    text_alpha = alpha;
    if (font_size < 0) font_size = 0;
    if (font_size > 96) font_size = 96;
    text_font_size = font_size;
    odd_bg = odd;
    even_bg = even;
    panel_bg = panel;
    active_indicator = active_dot;
    inactive_indicator = inactive_dot;
    if (card_scale < 40) card_scale = 40;
    if (card_scale > 100) card_scale = 100;
    card_scale_percent = card_scale;
    invalidate();
}

void Carousel::set_autoplay(int enabled, int interval) {
    autoplay = enabled != 0;
    if (interval < 500) interval = 500;
    if (interval > 60000) interval = 60000;
    interval_ms = interval;
    autoplay_elapsed_ms = 0;
    if (autoplay) ensure_timer();
    else stop_timer_if_idle();
    invalidate();
}

void Carousel::set_animation(int duration_ms) {
    if (duration_ms < 0) duration_ms = 0;
    if (duration_ms > 3000) duration_ms = 3000;
    transition_ms = duration_ms;
    if (transition_ms == 0) {
        transition_elapsed_ms = 0;
        transition_progress = 100;
    } else if (transition_progress >= 100) {
        transition_elapsed_ms = transition_ms;
    }
    stop_timer_if_idle();
    invalidate();
}

void Carousel::advance(int delta) {
    if (delta == 0) delta = 1;
    set_active_index_with_action(active_index + delta, delta < 0 ? 2 : 3, delta < 0 ? -1 : 1);
}

void Carousel::tick(int elapsed_ms) {
    if (elapsed_ms <= 0) elapsed_ms = 33;

    bool needs_paint = false;
    if (transition_progress < 100) {
        transition_elapsed_ms += elapsed_ms;
        if (transition_ms <= 0 || transition_elapsed_ms >= transition_ms) {
            transition_elapsed_ms = transition_ms;
            transition_progress = 100;
        } else {
            transition_progress = (transition_elapsed_ms * 100) / transition_ms;
        }
        needs_paint = true;
    }

    if (autoplay && items.size() > 1 && !(pause_on_hover && hovered)) {
        autoplay_elapsed_ms += elapsed_ms;
        if (autoplay_elapsed_ms >= interval_ms) {
            int steps = autoplay_elapsed_ms / interval_ms;
            autoplay_elapsed_ms = autoplay_elapsed_ms % interval_ms;
            for (int i = 0; i < steps; ++i) {
                int before = active_index;
                set_active_index_with_action(active_index + 1, 6, 1);
                if (active_index != before) ++autoplay_tick;
            }
            needs_paint = true;
        }
    }

    if (needs_paint) invalidate();
    stop_timer_if_idle();
}

bool Carousel::arrows_visible() const {
    return arrow_mode == 1 || (arrow_mode == 0 && hovered);
}

Rect Carousel::prev_rect() const {
    int size = (std::min)(36, (std::max)(26, (direction == 1 ? bounds.w : bounds.h) / 6));
    if (direction == 1) {
        return { (bounds.w - size) / 2, 12, size, size };
    }
    return { 12, (bounds.h - size) / 2, size, size };
}

Rect Carousel::next_rect() const {
    int size = (std::min)(36, (std::max)(26, (direction == 1 ? bounds.w : bounds.h) / 6));
    if (direction == 1) {
        return { (bounds.w - size) / 2, bounds.h - size - 12, size, size };
    }
    return { bounds.w - size - 12, (bounds.h - size) / 2, size, size };
}

Rect Carousel::indicator_rect(int index) const {
    int count = (int)items.size();
    int dot_w = 22;
    int dot_h = 6;
    int gap = 8;
    if (direction == 1) {
        dot_w = 6;
        dot_h = 22;
        int total_h = count * dot_h + (count - 1) * gap;
        int x = indicator_position == 1 ? bounds.w - 18 : bounds.w - 30;
        int y = (bounds.h - total_h) / 2 + index * (dot_h + gap);
        return { x, y, dot_w, dot_h };
    }
    int total_w = count * dot_w + (count - 1) * gap;
    int x = (bounds.w - total_w) / 2 + index * (dot_w + gap);
    int y = indicator_position == 1 ? bounds.h - 18 : bounds.h - 30;
    return { x, y, dot_w, dot_h };
}

int Carousel::neighbor_index(int delta) const {
    if (items.empty() || active_index < 0) return -1;
    int count = (int)items.size();
    int index = active_index + delta;
    if (loop) {
        while (index < 0) index += count;
        while (index >= count) index -= count;
        return index;
    }
    return (index >= 0 && index < count) ? index : -1;
}

Rect Carousel::item_rect(int index) const {
    if (carousel_type != 1 || index < 0 || index >= (int)items.size() || active_index < 0) {
        return { 0, 0, 0, 0 };
    }
    int prev = neighbor_index(-1);
    int next = neighbor_index(1);
    int active_w = (std::max)(80, bounds.w * 56 / 100);
    int active_h = (std::max)(60, bounds.h - 72);
    int side_w = active_w * card_scale_percent / 100;
    int side_h = active_h * card_scale_percent / 100;
    int cx = bounds.w / 2;
    int cy = (bounds.h - 30) / 2;
    if (index == active_index) {
        return { cx - active_w / 2, cy - active_h / 2, active_w, active_h };
    }
    if (index == prev) {
        return { cx - active_w / 2 - side_w / 2 - 18, cy - side_h / 2, side_w, side_h };
    }
    if (index == next && next != prev) {
        return { cx + active_w / 2 - side_w / 2 + 18, cy - side_h / 2, side_w, side_h };
    }
    return { 0, 0, 0, 0 };
}

Color Carousel::item_bg_color(int index, const Theme* t, bool dark) const {
    Color fallback = panel_bg ? panel_bg : with_alpha(t->accent, dark ? 0x32 : 0x22);
    if (index < 0) return fallback;
    Color custom = (index % 2 == 0) ? odd_bg : even_bg;
    return custom ? custom : fallback;
}

Color Carousel::text_color_value(const Theme* t) const {
    Color base = text_color ? text_color : (style.fg_color ? style.fg_color : t->text_primary);
    return with_alpha(base, (unsigned)text_alpha);
}

Carousel::Part Carousel::part_at(int x, int y, int* index) const {
    if (index) *index = -1;
    if (arrows_visible()) {
        if (prev_rect().contains(x, y)) return PartPrev;
        if (next_rect().contains(x, y)) return PartNext;
    }
    if (show_indicators) {
        for (int i = 0; i < (int)items.size(); ++i) {
            if (indicator_rect(i).contains(x, y)) {
                if (index) *index = i;
                return PartIndicator;
            }
        }
    }
    if (carousel_type == 1) {
        for (int i = 0; i < (int)items.size(); ++i) {
            Rect r = item_rect(i);
            if (r.w > 0 && r.h > 0 && r.contains(x, y)) {
                if (index) *index = i;
                return PartCardItem;
            }
        }
    }
    return PartNone;
}

void Carousel::paint_normal(RenderContext& ctx, const Theme* t, bool dark,
                            const D2D1_RECT_F& hero, const ElementStyle& text_style, Color fg) {
    Color item_bg = item_bg_color(active_index, t, dark);
    ctx.rt->FillRoundedRectangle(ROUNDED(hero, 5.0f, 5.0f), ctx.get_brush(item_bg));

    std::wstring label = (active_index >= 0 && active_index < (int)items.size())
        ? items[active_index] : L"\u6682\u65E0\u8F6E\u64AD\u5185\u5BB9";
    float font_scale = text_font_size > 0 ? 1.0f : 1.18f;
    if (transition_progress < 100 && previous_index >= 0 && previous_index < (int)items.size()) {
        float p = transition_progress / 100.0f;
        float travel = direction == 1 ? rect_height(hero) * 0.24f : rect_width(hero) * 0.24f;
        float old_dx = direction == 1 ? 0.0f : -travel * p * (float)transition_direction;
        float old_dy = direction == 1 ? -travel * p * (float)transition_direction : 0.0f;
        float new_dx = direction == 1 ? 0.0f : travel * (1.0f - p) * (float)transition_direction;
        float new_dy = direction == 1 ? travel * (1.0f - p) * (float)transition_direction : 0.0f;
        Color old_color = with_alpha(fg, (unsigned)((fg >> 24) * (1.0f - p)));
        Color new_color = with_alpha(fg, (unsigned)(0x99 + ((fg >> 24) - 0x99) * p));
        draw_text(ctx, items[previous_index], text_style, old_color,
                  hero.left + 18.0f + old_dx, hero.top + old_dy,
                  rect_width(hero) - 36.0f, rect_height(hero), font_scale);
        draw_text(ctx, label, text_style, new_color,
                  hero.left + 18.0f + new_dx, hero.top + new_dy,
                  rect_width(hero) - 36.0f, rect_height(hero), font_scale);
    } else {
        draw_text(ctx, label, text_style, fg, hero.left + 18.0f, hero.top,
                  rect_width(hero) - 36.0f, rect_height(hero), font_scale);
    }
}

void Carousel::paint_card(RenderContext& ctx, const Theme* t, bool dark,
                          const D2D1_RECT_F&, const ElementStyle& text_style, Color fg) {
    int prev = neighbor_index(-1);
    int next = neighbor_index(1);
    int order[3] = { prev, next, active_index };
    for (int n = 0; n < 3; ++n) {
        int index = order[n];
        if (index < 0 || index >= (int)items.size()) continue;
        if (n == 1 && index == prev) continue;
        Rect r = item_rect(index);
        if (r.w <= 0 || r.h <= 0) continue;
        D2D1_RECT_F rr = rect_from_rect(r);
        bool active = index == active_index;
        Color fill = item_bg_color(index, t, dark);
        if (!active) fill = with_alpha(fill, dark ? 0xBB : 0xDD);
        ctx.rt->FillRoundedRectangle(ROUNDED(rr, active ? 7.0f : 5.0f, active ? 7.0f : 5.0f),
                                     ctx.get_brush(fill));
        ctx.rt->DrawRoundedRectangle(ROUNDED(inset_rect(rr, 0.5f, 0.5f), 6.0f, 6.0f),
            ctx.get_brush(active ? (active_indicator ? active_indicator : t->accent) : with_alpha(t->text_secondary, 0x66)),
            active ? 1.4f : 1.0f);
        Color color = active ? fg : with_alpha(fg, (unsigned)((fg >> 24) * 0.68f));
        draw_text(ctx, items[index], text_style, color,
                  rr.left + 18.0f, rr.top, rect_width(rr) - 36.0f, rect_height(rr),
                  text_font_size > 0 ? 1.0f : (active ? 1.08f : 0.96f));
    }
}

void Carousel::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = panel_bg ? panel_bg : (style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFF5F7FA));
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = text_color_value(t);
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;

    ElementStyle text_style = style;
    if (text_font_size > 0) text_style.font_size = (float)text_font_size;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    D2D1_RECT_F hero;
    if (direction == 1) {
        float indicator_space = show_indicators && indicator_position == 1 ? 34.0f : 0.0f;
        hero = { 16.0f, 16.0f, (float)bounds.w - 18.0f - indicator_space, (float)bounds.h - 16.0f };
    } else {
        float indicator_space = show_indicators && indicator_position == 1 ? 28.0f : 44.0f;
        hero = { 16.0f, 16.0f, (float)bounds.w - 16.0f, (float)bounds.h - indicator_space };
    }
    if (carousel_type == 1) {
        paint_card(ctx, t, dark, hero, text_style, fg);
    } else {
        paint_normal(ctx, t, dark, hero, text_style, fg);
    }

    if (!items.empty()) {
        if (autoplay) {
            std::wstring auto_text = L"\u25B6 \u81EA\u52A8\u64AD\u653E " +
                                     std::to_wstring(interval_ms / 1000) + L"\u79D2";
            draw_text(ctx, auto_text, text_style, t->text_secondary, 22.0f, 22.0f,
                      (float)bounds.w - 44.0f, 24.0f, 0.82f,
                      DWRITE_TEXT_ALIGNMENT_TRAILING);
        }
        if (transition_progress < 100 && carousel_type == 0) {
            D2D1_RECT_F bar = { hero.left + 22.0f, hero.bottom - 8.0f,
                                hero.left + 22.0f + (rect_width(hero) - 44.0f) * (transition_progress / 100.0f),
                                hero.bottom - 4.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(bar, 2.0f, 2.0f),
                                         ctx.get_brush(active_indicator ? active_indicator : t->accent));
        }
    }

    auto draw_button = [&](const Rect& r, const std::wstring& text, Part part) {
        D2D1_RECT_F rr = rect_from_rect(r);
        Color b = m_hover_part == part ? t->button_hover : with_alpha(0xFF000000, dark ? 0x44 : 0x18);
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F((rr.left + rr.right) * 0.5f, (rr.top + rr.bottom) * 0.5f),
            (rr.right - rr.left) * 0.5f, (rr.bottom - rr.top) * 0.5f), ctx.get_brush(b));
        draw_text(ctx, text, text_style, 0xFFFFFFFF, rr.left, rr.top, rect_width(rr), rect_height(rr));
    };
    if (arrows_visible()) {
        draw_button(prev_rect(), direction == 1 ? L"^" : L"<", PartPrev);
        draw_button(next_rect(), direction == 1 ? L"v" : L">", PartNext);
    }

    if (show_indicators) {
        for (int i = 0; i < (int)items.size(); ++i) {
            Rect d = indicator_rect(i);
            D2D1_RECT_F rr = rect_from_rect(d);
            Color active_dot = active_indicator ? active_indicator : t->accent;
            Color inactive_dot = inactive_indicator ? inactive_indicator : with_alpha(t->text_secondary, 0x66);
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, 3.0f, 3.0f),
                ctx.get_brush(i == active_index ? active_dot : inactive_dot));
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Carousel::on_mouse_move(int x, int y) {
    hovered = true;
    int idx = -1;
    Part part = part_at(x, y, &idx);
    if (trigger_mode == 0 && part == PartIndicator && idx >= 0 && idx != active_index) {
        set_active_index_with_action(idx, 4, idx >= active_index ? 1 : -1);
    }
    if (part != m_hover_part || idx != m_hover_index) {
        m_hover_part = part;
        m_hover_index = idx;
        invalidate();
    }
}

void Carousel::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Carousel::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_index);
    pressed = true;
    invalidate();
}

void Carousel::on_mouse_up(int x, int y, MouseButton) {
    int idx = -1;
    Part p = part_at(x, y, &idx);
    if (p == m_press_part) {
        if (p == PartPrev) set_active_index_with_action(active_index - 1, 2, -1);
        else if (p == PartNext) set_active_index_with_action(active_index + 1, 3, 1);
        else if (p == PartIndicator && trigger_mode == 1) set_active_index_with_action(idx, 4, idx >= active_index ? 1 : -1);
        else if (p == PartCardItem && idx >= 0 && idx != active_index) set_active_index_with_action(idx, 4, idx >= active_index ? 1 : -1);
    }
    m_press_part = PartNone;
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Carousel::on_key_down(int vk, int) {
    if (direction == 1) {
        if (vk == VK_UP) set_active_index_with_action(active_index - 1, 5, -1);
        else if (vk == VK_DOWN) set_active_index_with_action(active_index + 1, 5, 1);
    } else {
        if (vk == VK_LEFT) set_active_index_with_action(active_index - 1, 5, -1);
        else if (vk == VK_RIGHT) set_active_index_with_action(active_index + 1, 5, 1);
    }
    if (vk == VK_HOME) set_active_index_with_action(0, 5, -1);
    else if (vk == VK_END) set_active_index_with_action((int)items.size() - 1, 5, 1);
}
