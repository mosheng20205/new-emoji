#include "element_timepicker.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwchar>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static int normalize_hhmm(int value) {
    int h = value / 100;
    int m = value % 100;
    if (h < 0) h = 0;
    if (h > 23) h = 23;
    if (m < 0) m = 0;
    if (m > 59) m = 59;
    return h * 100 + m;
}

static int minute_step_from_value(int value) {
    if (value < 1) return 1;
    if (value > 30) return 30;
    return value;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

int TimePicker::popup_width() const {
    return (std::max)(bounds.w, 220);
}

int TimePicker::popup_height() const {
    return 36 + visible_row_count() * row_height() + 12;
}

int TimePicker::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

int TimePicker::row_height() const {
    return 30;
}

int TimePicker::visible_row_count() const {
    return 8;
}

int TimePicker::hour_row_count() const {
    return 24;
}

int TimePicker::minute_row_count() const {
    return (59 / minute_step_from_value(step_minutes)) + 1;
}

void TimePicker::clamp_scroll() {
    int hour_max = (std::max)(0, hour_row_count() - visible_row_count());
    int minute_max = (std::max)(0, minute_row_count() - visible_row_count());
    if (m_hour_scroll < 0) m_hour_scroll = 0;
    if (m_hour_scroll > hour_max) m_hour_scroll = hour_max;
    if (m_minute_scroll < 0) m_minute_scroll = 0;
    if (m_minute_scroll > minute_max) m_minute_scroll = minute_max;
}

void TimePicker::ensure_selected_visible() {
    int visible_rows = visible_row_count();
    if (hour < m_hour_scroll) m_hour_scroll = hour;
    if (hour >= m_hour_scroll + visible_rows) m_hour_scroll = hour - visible_rows + 1;
    int step = minute_step_from_value(step_minutes);
    int minute_index = minute / step;
    if (minute_index < m_minute_scroll) m_minute_scroll = minute_index;
    if (minute_index >= m_minute_scroll + visible_rows) {
        m_minute_scroll = minute_index - visible_rows + 1;
    }
    clamp_scroll();
}

void TimePicker::scroll_part(Part part, int rows) {
    if (part == PartHour) {
        m_hour_scroll += rows;
        m_active_part = PartHour;
    } else if (part == PartMinute) {
        m_minute_scroll += rows;
        m_active_part = PartMinute;
    }
    clamp_scroll();
    invalidate();
}

bool TimePicker::select_step(Part part, int delta) {
    if (part == PartHour) {
        int next = hour + delta;
        while (next >= 0 && next <= 23) {
            if (can_select_time(next, minute)) {
                hour = next;
                m_active_part = PartHour;
                ensure_selected_visible();
                invalidate();
                return true;
            }
            next += delta > 0 ? 1 : -1;
        }
    } else if (part == PartMinute) {
        int step = minute_step_from_value(step_minutes);
        int index = minute / step + delta;
        int count = minute_row_count();
        while (index >= 0 && index < count) {
            int next = index * step;
            if (next <= 59 && can_select_time(hour, next)) {
                minute = next;
                m_active_part = PartMinute;
                ensure_selected_visible();
                invalidate();
                return true;
            }
            index += delta > 0 ? 1 : -1;
        }
    }
    return false;
}

bool TimePicker::can_select_time(int next_hour, int next_minute) const {
    int v = normalize_hhmm(next_hour * 100 + next_minute);
    return v >= min_time && v <= max_time;
}

void TimePicker::set_time(int next_hour, int next_minute) {
    if (next_hour < 0) next_hour = 0;
    if (next_hour > 23) next_hour = 23;
    if (next_minute < 0) next_minute = 0;
    if (next_minute > 59) next_minute = 59;
    int step = minute_step_from_value(step_minutes);
    next_minute = ((next_minute + step / 2) / step) * step;
    if (next_minute > 59) next_minute = (59 / step) * step;
    int next_value = normalize_hhmm(next_hour * 100 + next_minute);
    if (next_value < min_time) next_value = min_time;
    if (next_value > max_time) next_value = max_time;
    hour = next_value / 100;
    minute = next_value % 100;
    ensure_selected_visible();
    invalidate();
}

void TimePicker::set_range(int min_hhmm, int max_hhmm) {
    min_time = normalize_hhmm(min_hhmm);
    max_time = normalize_hhmm(max_hhmm);
    if (min_time > max_time) std::swap(min_time, max_time);
    set_time(hour, minute);
}

void TimePicker::set_options(int next_step_minutes, int next_time_format) {
    step_minutes = minute_step_from_value(next_step_minutes);
    time_format = next_time_format;
    set_time(hour, minute);
}

void TimePicker::set_open(bool next_open) {
    open = next_open;
    if (open) ensure_selected_visible();
    invalidate();
}

void TimePicker::set_scroll(int next_hour_scroll, int next_minute_scroll) {
    m_hour_scroll = next_hour_scroll;
    m_minute_scroll = next_minute_scroll;
    clamp_scroll();
    invalidate();
}

void TimePicker::get_scroll(int& next_hour_scroll, int& next_minute_scroll) const {
    next_hour_scroll = m_hour_scroll;
    next_minute_scroll = m_minute_scroll;
}

int TimePicker::value() const {
    return hour * 100 + minute;
}

bool TimePicker::is_open() const {
    return open;
}

std::wstring TimePicker::display_text() const {
    wchar_t buf[16];
    if (time_format == 1) {
        swprintf_s(buf, L"%02d\u65F6%02d\u5206", hour, minute);
    } else {
        swprintf_s(buf, L"%02d:%02d", hour, minute);
    }
    return buf;
}

TimePicker::Part TimePicker::part_at(int x, int y, int* value) const {
    if (value) *value = -1;
    if (!open) {
        if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
        return PartNone;
    }
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    if (x >= 0 && x < pw && y >= py && y < py + ph) {
        int col_w = pw / 2;
        int local_y = y - py - 36;
        if (local_y >= 0) {
            int row = local_y / row_height();
            if (row >= 0 && row < visible_row_count()) {
                if (x < col_w) {
                    int h = m_hour_scroll + row;
                    if (h < 0 || h > 23) return PartNone;
                    if (value) *value = h;
                    return PartHour;
                }
                int m = (m_minute_scroll + row) * minute_step_from_value(step_minutes);
                if (m > 59) return PartNone;
                if (value) *value = m;
                return PartMinute;
            }
        }
    }
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

Element* TimePicker::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* TimePicker::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    int value = -1;
    Part p = part_at(lx, ly, &value);
    return (p == PartHour || p == PartMinute) ? this : nullptr;
}

void TimePicker::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = open || has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    draw_text(ctx, display_text(), style, fg,
              (float)style.pad_left, 0.0f,
              (float)bounds.w - style.pad_left - style.pad_right - 26.0f, (float)bounds.h,
              DWRITE_TEXT_ALIGNMENT_LEADING);
    draw_text(ctx, L"⏱", style, t->text_secondary,
              (float)bounds.w - style.pad_right - 26.0f, 0.0f, 26.0f, (float)bounds.h);

    ctx.rt->SetTransform(saved);
}

void TimePicker::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    int col_w = pw / 2;
    int rh = row_height();

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    draw_text(ctx, L"小时", style, t->text_secondary, 0.0f, (float)py, (float)col_w, 36.0f);
    draw_text(ctx, L"分钟", style, t->text_secondary, (float)col_w, (float)py, (float)col_w, 36.0f);
    ctx.rt->DrawLine(D2D1::Point2F((float)col_w, (float)py),
                     D2D1::Point2F((float)col_w, (float)(py + ph)),
                     ctx.get_brush(t->border_default), 1.0f);
    ctx.rt->DrawLine(D2D1::Point2F(0.0f, (float)py + 36.0f),
                     D2D1::Point2F((float)pw, (float)py + 36.0f),
                     ctx.get_brush(t->border_default), 1.0f);

    int rows = visible_row_count();
    int step = minute_step_from_value(step_minutes);
    for (int r = 0; r < rows; ++r) {
        int h = m_hour_scroll + r;
        int m = (m_minute_scroll + r) * step;
        float y = (float)(py + 36 + r * rh);
        bool valid_h = h >= 0 && h < 24 && can_select_time(h, minute);
        bool valid_m = m <= 59 && can_select_time(hour, m);
        if (valid_h && ((m_hover_part == PartHour && m_hover_value == h) || hour == h)) {
            D2D1_RECT_F row = { 2.0f, y + 1.0f, (float)col_w - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(hour == h ? with_alpha(t->accent, 0x33) : t->button_hover));
        } else if (m_active_part == PartHour && hour == h) {
            D2D1_RECT_F row = { 2.0f, y + 1.0f, (float)col_w - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->DrawRectangle(row, ctx.get_brush(t->accent), 1.0f);
        }
        if (valid_m && ((m_hover_part == PartMinute && m_hover_value == m) || minute == m)) {
            D2D1_RECT_F row = { (float)col_w + 2.0f, y + 1.0f, (float)pw - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(minute == m ? with_alpha(t->accent, 0x33) : t->button_hover));
        } else if (m_active_part == PartMinute && minute == m) {
            D2D1_RECT_F row = { (float)col_w + 2.0f, y + 1.0f, (float)pw - 2.0f, y + (float)rh - 1.0f };
            ctx.rt->DrawRectangle(row, ctx.get_brush(t->accent), 1.0f);
        }
        wchar_t hbuf[8], mbuf[8];
        if (h < 24) {
            swprintf_s(hbuf, L"%02d", h);
            draw_text(ctx, hbuf, style, valid_h ? (hour == h ? t->accent : fg) : t->text_secondary,
                      0.0f, y, (float)col_w, (float)rh);
        }
        if (m <= 59) {
            swprintf_s(mbuf, L"%02d", m);
            draw_text(ctx, mbuf, style, valid_m ? (minute == m ? t->accent : fg) : t->text_secondary,
                      (float)col_w, y, (float)col_w, (float)rh);
        }
    }

    wchar_t hhint[32], mhint[32];
    swprintf_s(hhint, L"%d/%d", m_hour_scroll + 1, hour_row_count());
    swprintf_s(mhint, L"%d/%d", m_minute_scroll + 1, minute_row_count());
    draw_text(ctx, hhint, style, t->text_secondary,
              8.0f, (float)(py + ph - 12), (float)col_w - 16.0f, 10.0f);
    draw_text(ctx, mhint, style, t->text_secondary,
              (float)col_w + 8.0f, (float)(py + ph - 12), (float)col_w - 16.0f, 10.0f);

    ctx.rt->SetTransform(saved);
}

void TimePicker::on_mouse_move(int x, int y) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p != PartHour && p != PartMinute) {
        p = PartNone;
        value = -1;
    }
    if (p != m_hover_part || value != m_hover_value) {
        m_hover_part = p;
        m_hover_value = value;
        invalidate();
    }
}

void TimePicker::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_part = PartNone;
    m_hover_value = -1;
    m_press_part = PartNone;
    m_press_value = -1;
    invalidate();
}

void TimePicker::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_value);
    pressed = true;
    invalidate();
}

void TimePicker::on_mouse_up(int x, int y, MouseButton) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p == PartMain && m_press_part == PartMain) {
        open = !open;
        if (open) ensure_selected_visible();
    } else if (p == m_press_part && value == m_press_value) {
        if (p == PartHour && can_select_time(value, minute)) {
            hour = value;
            m_active_part = PartHour;
        } else if (p == PartMinute && can_select_time(hour, value)) {
            minute = value;
            m_active_part = PartMinute;
        }
        ensure_selected_visible();
    }
    m_press_part = PartNone;
    m_press_value = -1;
    pressed = false;
    invalidate();
}

void TimePicker::on_mouse_wheel(int x, int y, int delta) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p != PartHour && p != PartMinute) p = m_active_part;
    int rows = delta > 0 ? -3 : 3;
    scroll_part(p, rows);
}

void TimePicker::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        open = !open;
        if (open) ensure_selected_visible();
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_LEFT) {
        m_active_part = PartHour;
        ensure_selected_visible();
    } else if (vk == VK_RIGHT) {
        m_active_part = PartMinute;
        ensure_selected_visible();
    } else if (vk == VK_UP) {
        if (open) select_step(m_active_part, -1);
        else set_time(hour, minute - minute_step_from_value(step_minutes));
    } else if (vk == VK_DOWN) {
        if (open) select_step(m_active_part, 1);
        else set_time(hour, minute + minute_step_from_value(step_minutes));
    } else if (vk == VK_PRIOR) {
        if (open) {
            scroll_part(m_active_part, -visible_row_count());
            select_step(m_active_part, -visible_row_count());
        }
    } else if (vk == VK_NEXT) {
        if (open) {
            scroll_part(m_active_part, visible_row_count());
            select_step(m_active_part, visible_row_count());
        }
    } else if (vk == VK_HOME) {
        if (m_active_part == PartHour) {
            for (int h = 0; h <= 23; ++h) {
                if (can_select_time(h, minute)) { hour = h; break; }
            }
        } else {
            int step = minute_step_from_value(step_minutes);
            for (int i = 0; i < minute_row_count(); ++i) {
                int m = i * step;
                if (can_select_time(hour, m)) { minute = m; break; }
            }
        }
        ensure_selected_visible();
    } else if (vk == VK_END) {
        if (m_active_part == PartHour) {
            for (int h = 23; h >= 0; --h) {
                if (can_select_time(h, minute)) { hour = h; break; }
            }
        } else {
            int step = minute_step_from_value(step_minutes);
            for (int i = minute_row_count() - 1; i >= 0; --i) {
                int m = i * step;
                if (can_select_time(hour, m)) { minute = m; break; }
            }
        }
        ensure_selected_visible();
    }
    invalidate();
}

void TimePicker::on_blur() {
    has_focus = false;
    open = false;
    m_hover_part = PartNone;
    m_hover_value = -1;
    m_press_part = PartNone;
    invalidate();
}
