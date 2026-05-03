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
    return range_select ? (std::max)(bounds.w, 460) : (std::max)(bounds.w, 220);
}

int TimePicker::popup_height() const {
    int base = 36 + visible_row_count() * row_height() + 12;
    return base;
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
    if (m_end_hour_scroll < 0) m_end_hour_scroll = 0;
    if (m_end_hour_scroll > hour_max) m_end_hour_scroll = hour_max;
    if (m_end_minute_scroll < 0) m_end_minute_scroll = 0;
    if (m_end_minute_scroll > minute_max) m_end_minute_scroll = minute_max;
}

void TimePicker::ensure_time_visible(int time_value, int& hour_scroll, int& minute_scroll) {
    int visible_rows = visible_row_count();
    int next_hour = normalize_hhmm(time_value) / 100;
    int next_minute = normalize_hhmm(time_value) % 100;
    if (next_hour < hour_scroll) hour_scroll = next_hour;
    if (next_hour >= hour_scroll + visible_rows) hour_scroll = next_hour - visible_rows + 1;
    int step = minute_step_from_value(step_minutes);
    int minute_index = next_minute / step;
    if (minute_index < minute_scroll) minute_scroll = minute_index;
    if (minute_index >= minute_scroll + visible_rows) {
        minute_scroll = minute_index - visible_rows + 1;
    }
}

void TimePicker::ensure_selected_visible() {
    if (range_select) {
        ensure_time_visible(range_start_has_value ? range_start : value(), m_hour_scroll, m_minute_scroll);
        int end_value = range_end_has_value ? range_end : (range_start_has_value ? range_start : value());
        ensure_time_visible(end_value, m_end_hour_scroll, m_end_minute_scroll);
    } else {
        ensure_time_visible(value(), m_hour_scroll, m_minute_scroll);
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
    } else if (part == PartHourEnd) {
        m_end_hour_scroll += rows;
        m_active_part = PartHourEnd;
    } else if (part == PartMinuteEnd) {
        m_end_minute_scroll += rows;
        m_active_part = PartMinuteEnd;
    }
    clamp_scroll();
    invalidate();
}

bool TimePicker::select_step(Part part, int delta) {
    if (range_select && (part == PartHour || part == PartMinute || part == PartHourEnd || part == PartMinuteEnd)) {
        bool is_end = part == PartHourEnd || part == PartMinuteEnd;
        int current = is_end ? (range_end_has_value ? range_end : (range_start_has_value ? range_start : value()))
                             : (range_start_has_value ? range_start : value());
        int base_hour = current / 100;
        int base_minute = current % 100;
        if (part == PartHour || part == PartHourEnd) {
            int next = base_hour + delta;
            while (next >= 0 && next <= 23) {
                if (can_select_range_time(part, next, base_minute)) {
                    if (is_end) {
                        range_end = next * 100 + base_minute;
                        range_end_has_value = true;
                    } else {
                        range_start = next * 100 + base_minute;
                        range_start_has_value = true;
                    }
                    m_active_part = part;
                    ensure_selected_visible();
                    invalidate();
                    return true;
                }
                next += delta > 0 ? 1 : -1;
            }
        } else {
            int step = minute_step_from_value(step_minutes);
            int index = base_minute / step + delta;
            int count = minute_row_count();
            while (index >= 0 && index < count) {
                int next = index * step;
                if (next <= 59 && can_select_range_time(part, base_hour, next)) {
                    if (is_end) {
                        range_end = base_hour * 100 + next;
                        range_end_has_value = true;
                    } else {
                        range_start = base_hour * 100 + next;
                        range_start_has_value = true;
                    }
                    m_active_part = part;
                    ensure_selected_visible();
                    invalidate();
                    return true;
                }
                index += delta > 0 ? 1 : -1;
            }
        }
        return false;
    }

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

bool TimePicker::can_select_range_time(Part part, int next_hour, int next_minute) const {
    int v = normalize_hhmm(next_hour * 100 + next_minute);
    if (v < min_time || v > max_time) return false;
    if (!range_select) return true;
    if ((part == PartHour || part == PartMinute) && range_end_has_value && v > range_end) return false;
    if ((part == PartHourEnd || part == PartMinuteEnd) && range_start_has_value && v < range_start) return false;
    return true;
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
    if (range_start_has_value) {
        if (range_start < min_time) range_start = min_time;
        if (range_start > max_time) range_start = max_time;
    }
    if (range_end_has_value) {
        if (range_end < min_time) range_end = min_time;
        if (range_end > max_time) range_end = max_time;
    }
    if (range_start_has_value && range_end_has_value && range_start > range_end) {
        std::swap(range_start, range_end);
    }
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

void TimePicker::set_selection_range(int start_hhmm, int end_hhmm, bool enabled) {
    range_select = enabled;
    range_start_has_value = enabled;
    range_end_has_value = enabled;
    range_start = normalize_hhmm(start_hhmm);
    range_end = normalize_hhmm(end_hhmm);
    if (range_start_has_value) {
        if (range_start < min_time) range_start = min_time;
        if (range_start > max_time) range_start = max_time;
    }
    if (range_end_has_value) {
        if (range_end < min_time) range_end = min_time;
        if (range_end > max_time) range_end = max_time;
    }
    if (range_start_has_value && range_end_has_value && range_start > range_end) {
        std::swap(range_start, range_end);
    }
    ensure_selected_visible();
    invalidate();
}

int TimePicker::value() const {
    return hour * 100 + minute;
}

bool TimePicker::is_open() const {
    return open;
}

std::wstring TimePicker::display_text() const {
    auto fmt_t = [&](int v) -> std::wstring {
        if (v < 0) return L"";
        int h = v / 100, m = v % 100;
        wchar_t buf[16];
        if (time_format == 1) swprintf_s(buf, L"%02d时%02d分", h, m);
        else swprintf_s(buf, L"%02d:%02d", h, m);
        return buf;
    };

    if (range_select) {
        std::wstring s = range_start_has_value ? fmt_t(range_start)
            : (start_placeholder.empty() ? L"开始时间" : start_placeholder);
        s += range_separator;
        s += range_end_has_value ? fmt_t(range_end)
            : (end_placeholder.empty() ? L"结束时间" : end_placeholder);
        return s;
    }

    return fmt_t(hour * 100 + minute);
}

TimePicker::Part TimePicker::part_at(int x, int y, int* value) const {
    if (value) *value = -1;
    if (!open) {
        if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
        return PartNone;
    }
    int py = popup_y(), pw = popup_width(), ph = popup_height();
    if (x < 0 || x >= pw || y < py || y >= py + ph) {
        if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
        return PartNone;
    }
    int cols = range_select ? 4 : 2;
    int col_w = pw / cols;
    int local_y = y - py - 36;
    if (local_y < 0) return PartNone;
    int row = local_y / row_height();
    if (row < 0 || row >= visible_row_count()) return PartNone;
    int col = x / col_w;
    if (col < 0 || col >= cols) return PartNone;
    int step_val = minute_step_from_value(step_minutes);

    if (range_select) {
        if (col == 0) { // start hour
            int h = m_hour_scroll + row; if (h < 0 || h > 23) return PartNone;
            if (value) *value = h; return PartHour;
        } else if (col == 1) { // start minute
            int m = (m_minute_scroll + row) * step_val; if (m > 59) return PartNone;
            if (value) *value = m; return PartMinute;
        } else if (col == 2) { // end hour
            int h = m_end_hour_scroll + row; if (h < 0 || h > 23) return PartNone;
            if (value) *value = h; return PartHourEnd;
        } else { // end minute
            int m = (m_end_minute_scroll + row) * step_val; if (m > 59) return PartNone;
            if (value) *value = m; return PartMinuteEnd;
        }
    } else {
        if (col == 0) {
            int h = m_hour_scroll + row; if (h < 0 || h > 23) return PartNone;
            if (value) *value = h; return PartHour;
        } else {
            int m = (m_minute_scroll + row) * step_val; if (m > 59) return PartNone;
            if (value) *value = m; return PartMinute;
        }
    }
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
    return (p == PartHour || p == PartMinute || p == PartHourEnd || p == PartMinuteEnd) ? this : nullptr;
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
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    int py = popup_y(), pw = popup_width(), ph = popup_height();
    int col_w = pw / (range_select ? 4 : 2);
    int rh = row_height();
    int rows = visible_row_count();
    int step = minute_step_from_value(step_minutes);

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);

    auto draw_col = [&](int col_index, const wchar_t* header, int scroll, int selected_val,
                         bool is_hour, int row_count, int other_part_selected, Part hover_part) {
        float col_x = (float)(col_index * col_w);
        float grid_top = (float)py + 36.0f;
        draw_text(ctx, header, style, muted, col_x, (float)py, (float)col_w, 36.0f);
        for (int r = 0; r < rows; ++r) {
            int val = is_hour ? (scroll + r) : ((scroll + r) * step);
            if ((is_hour && val >= 24) || (!is_hour && val > 59)) continue;
            float y = grid_top + (float)(r * rh);
            bool valid = range_select
                ? (is_hour ? can_select_range_time(hover_part, val, other_part_selected)
                           : can_select_range_time(hover_part, other_part_selected, val))
                : (is_hour ? can_select_time(val, other_part_selected)
                           : can_select_time(other_part_selected, val));
            bool sel = (val == selected_val);
            bool hot = (m_hover_part == hover_part) && m_hover_value == val;
            if (sel || hot) {
                D2D1_RECT_F row = { col_x + 2.0f, y + 1.0f, col_x + (float)col_w - 2.0f, y + (float)rh - 1.0f };
                ctx.rt->FillRectangle(row, ctx.get_brush(sel ? with_alpha(t->accent, 0x33) : t->button_hover));
            }
            wchar_t buf[8];
            swprintf_s(buf, L"%02d", val);
            draw_text(ctx, buf, style, valid ? (sel ? t->accent : fg) : muted,
                      col_x, y, (float)col_w, (float)rh);
        }
    };

    if (range_select) {
        // "开始时间" section
        draw_text(ctx, L"开始时间", style, t->accent, 0, (float)py, (float)(col_w * 2), 36.0f);
        ctx.rt->DrawLine(D2D1::Point2F(0, (float)py + 36.0f), D2D1::Point2F((float)(col_w * 2), (float)py + 36.0f),
                         ctx.get_brush(t->border_default), 1.0f);
        int start_value = range_start_has_value ? range_start : value();
        int end_value = range_end_has_value ? range_end : (range_start_has_value ? range_start : value());
        draw_col(0, L"时", m_hour_scroll, start_value / 100, true, 24,
                 start_value % 100, PartHour);
        draw_col(1, L"分", m_minute_scroll, start_value % 100, false, minute_row_count(),
                 start_value / 100, PartMinute);

        // Separator
        ctx.rt->DrawLine(D2D1::Point2F((float)(col_w * 2), (float)py),
                         D2D1::Point2F((float)(col_w * 2), (float)(py + ph)), ctx.get_brush(t->border_default), 1.5f);

        // "结束时间" section
        draw_text(ctx, L"结束时间", style, t->accent, (float)(col_w * 2), (float)py, (float)(col_w * 2), 36.0f);
        ctx.rt->DrawLine(D2D1::Point2F((float)(col_w * 2), (float)py + 36.0f),
                         D2D1::Point2F((float)pw, (float)py + 36.0f), ctx.get_brush(t->border_default), 1.0f);
        draw_col(2, L"时", m_end_hour_scroll, end_value / 100, true, 24,
                 end_value % 100, PartHourEnd);
        draw_col(3, L"分", m_end_minute_scroll, end_value % 100, false, minute_row_count(),
                 end_value / 100, PartMinuteEnd);
    } else {
        draw_text(ctx, L"小时", style, muted, 0, (float)py, (float)col_w, 36.0f);
        draw_text(ctx, L"分钟", style, muted, (float)col_w, (float)py, (float)col_w, 36.0f);
        ctx.rt->DrawLine(D2D1::Point2F(0, (float)py + 36.0f), D2D1::Point2F((float)pw, (float)py + 36.0f),
                         ctx.get_brush(t->border_default), 1.0f);
        draw_col(0, L"时", m_hour_scroll, hour, true, 24, minute, PartHour);
        draw_col(1, L"分", m_minute_scroll, minute, false, minute_row_count(), hour, PartMinute);
    }

    ctx.rt->SetTransform(saved);
}

void TimePicker::on_mouse_move(int x, int y) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p != PartHour && p != PartMinute && p != PartHourEnd && p != PartMinuteEnd) {
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
        if (range_select) {
            int start_value = range_start_has_value ? range_start : this->value();
            int end_value = range_end_has_value ? range_end : (range_start_has_value ? range_start : this->value());
            if (p == PartHour && can_select_range_time(p, value, start_value % 100)) {
                range_start = value * 100 + (start_value % 100);
                range_start_has_value = true;
                m_active_part = PartHour;
            } else if (p == PartMinute && can_select_range_time(p, start_value / 100, value)) {
                range_start = (start_value / 100) * 100 + value;
                range_start_has_value = true;
                m_active_part = PartMinute;
            } else if (p == PartHourEnd && can_select_range_time(p, value, end_value % 100)) {
                range_end = value * 100 + (end_value % 100);
                range_end_has_value = true;
                m_active_part = PartHourEnd;
            } else if (p == PartMinuteEnd && can_select_range_time(p, end_value / 100, value)) {
                range_end = (end_value / 100) * 100 + value;
                range_end_has_value = true;
                m_active_part = PartMinuteEnd;
            }
        } else {
            if (p == PartHour && can_select_time(value, minute)) {
                hour = value; m_active_part = PartHour;
            } else if (p == PartMinute && can_select_time(hour, value)) {
                minute = value; m_active_part = PartMinute;
            }
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
    bool time_part = p == PartHour || p == PartMinute || p == PartHourEnd || p == PartMinuteEnd;
    if (!time_part && !range_select) {
        p = m_active_part;
        time_part = p == PartHour || p == PartMinute;
    }
    if (!time_part && range_select &&
        (m_active_part == PartHour || m_active_part == PartMinute ||
         m_active_part == PartHourEnd || m_active_part == PartMinuteEnd)) {
        p = m_active_part;
        time_part = true;
    }
    if (time_part) {
        int rows = delta > 0 ? -3 : 3;
        scroll_part(p, rows);
    }
}

void TimePicker::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        open = !open;
        if (open) ensure_selected_visible();
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_LEFT) {
        if (range_select) {
            if (m_active_part == PartMinuteEnd) m_active_part = PartHourEnd;
            else if (m_active_part == PartHourEnd) m_active_part = PartMinute;
            else if (m_active_part == PartMinute) m_active_part = PartHour;
            else m_active_part = PartHour;
        } else {
            m_active_part = PartHour;
        }
        ensure_selected_visible();
    } else if (vk == VK_RIGHT) {
        if (range_select) {
            if (m_active_part == PartHour) m_active_part = PartMinute;
            else if (m_active_part == PartMinute) m_active_part = PartHourEnd;
            else if (m_active_part == PartHourEnd) m_active_part = PartMinuteEnd;
            else m_active_part = PartMinuteEnd;
        } else {
            m_active_part = PartMinute;
        }
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
        if (range_select && (m_active_part == PartHour || m_active_part == PartMinute ||
                             m_active_part == PartHourEnd || m_active_part == PartMinuteEnd)) {
            Part part = m_active_part;
            bool is_hour_part = part == PartHour || part == PartHourEnd;
            bool is_end = part == PartHourEnd || part == PartMinuteEnd;
            int current = is_end ? (range_end_has_value ? range_end : (range_start_has_value ? range_start : value()))
                                 : (range_start_has_value ? range_start : value());
            int current_hour = current / 100;
            int current_minute = current % 100;
            if (is_hour_part) {
                for (int h = 0; h <= 23; ++h) {
                    if (can_select_range_time(part, h, current_minute)) {
                        if (is_end) { range_end = h * 100 + current_minute; range_end_has_value = true; }
                        else { range_start = h * 100 + current_minute; range_start_has_value = true; }
                        break;
                    }
                }
            } else {
                int step = minute_step_from_value(step_minutes);
                for (int i = 0; i < minute_row_count(); ++i) {
                    int m = i * step;
                    if (can_select_range_time(part, current_hour, m)) {
                        if (is_end) { range_end = current_hour * 100 + m; range_end_has_value = true; }
                        else { range_start = current_hour * 100 + m; range_start_has_value = true; }
                        break;
                    }
                }
            }
        } else if (m_active_part == PartHour) {
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
        if (range_select && (m_active_part == PartHour || m_active_part == PartMinute ||
                             m_active_part == PartHourEnd || m_active_part == PartMinuteEnd)) {
            Part part = m_active_part;
            bool is_hour_part = part == PartHour || part == PartHourEnd;
            bool is_end = part == PartHourEnd || part == PartMinuteEnd;
            int current = is_end ? (range_end_has_value ? range_end : (range_start_has_value ? range_start : value()))
                                 : (range_start_has_value ? range_start : value());
            int current_hour = current / 100;
            int current_minute = current % 100;
            if (is_hour_part) {
                for (int h = 23; h >= 0; --h) {
                    if (can_select_range_time(part, h, current_minute)) {
                        if (is_end) { range_end = h * 100 + current_minute; range_end_has_value = true; }
                        else { range_start = h * 100 + current_minute; range_start_has_value = true; }
                        break;
                    }
                }
            } else {
                int step = minute_step_from_value(step_minutes);
                for (int i = minute_row_count() - 1; i >= 0; --i) {
                    int m = i * step;
                    if (can_select_range_time(part, current_hour, m)) {
                        if (is_end) { range_end = current_hour * 100 + m; range_end_has_value = true; }
                        else { range_start = current_hour * 100 + m; range_start_has_value = true; }
                        break;
                    }
                }
            }
        } else if (m_active_part == PartHour) {
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
