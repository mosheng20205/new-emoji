#include "element_datetimepicker.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwchar>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static bool dtp_leap_year(int y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

static int dtp_days_in_month(int y, int m) {
    static const int days[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (m == 2) return dtp_leap_year(y) ? 29 : 28;
    if (m < 1 || m > 12) return 30;
    return days[m - 1];
}

static int dtp_first_weekday(int y, int m) {
    if (m < 3) {
        m += 12;
        --y;
    }
    int k = y % 100;
    int j = y / 100;
    int h = (1 + (13 * (m + 1)) / 5 + k + k / 4 + j / 4 + 5 * j) % 7;
    return (h + 6) % 7;
}

static Color dtp_with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static int dtp_date_value(int y, int m, int d) {
    return y * 10000 + m * 100 + d;
}

static int dtp_normalize_hhmm(int value) {
    int h = value / 100;
    int m = value % 100;
    if (h < 0) h = 0;
    if (h > 23) h = 23;
    if (m < 0) m = 0;
    if (m > 59) m = 59;
    return h * 100 + m;
}

static int dtp_minute_step(int value) {
    if (value < 1) return 1;
    if (value > 30) return 30;
    return value;
}

static void dtp_from_date_value(int value, int* y, int* m, int* d) {
    int yy = value / 10000;
    int mm = (value / 100) % 100;
    int dd = value % 100;
    if (yy < 1900) yy = 1900;
    if (yy > 2099) yy = 2099;
    if (mm < 1) mm = 1;
    if (mm > 12) mm = 12;
    int max_day = dtp_days_in_month(yy, mm);
    if (dd < 1) dd = 1;
    if (dd > max_day) dd = max_day;
    if (y) *y = yy;
    if (m) *m = mm;
    if (d) *d = dd;
}

static void dtp_draw_text(RenderContext& ctx, const std::wstring& text,
                          const ElementStyle& style, Color color,
                          float x, float y, float w, float h,
                          float scale = 1.0f,
                          DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                          DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name,
                                          style.font_size * scale, w, h);
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

int DateTimePicker::popup_width() const {
    return (std::max)(bounds.w, 420);
}

int DateTimePicker::popup_height() const {
    return 38 + visible_row_count() * 28 + 54;
}

int DateTimePicker::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

void DateTimePicker::set_datetime(int next_year, int next_month, int next_day,
                                  int next_hour, int next_minute) {
    if (next_year < 1900) next_year = 1900;
    if (next_year > 2099) next_year = 2099;
    if (next_month < 1) next_month = 1;
    if (next_month > 12) next_month = 12;
    int max_day = dtp_days_in_month(next_year, next_month);
    if (next_day < 1) next_day = 1;
    if (next_day > max_day) next_day = max_day;
    if (next_hour < 0) next_hour = 0;
    if (next_hour > 23) next_hour = 23;
    if (next_minute < 0) next_minute = 0;
    if (next_minute > 59) next_minute = 59;
    int step = dtp_minute_step(minute_step);
    next_minute = ((next_minute + step / 2) / step) * step;
    if (next_minute > 59) next_minute = (59 / step) * step;
    int next_date = dtp_date_value(next_year, next_month, next_day);
    if (min_date > 0 && next_date < min_date) {
        dtp_from_date_value(min_date, &next_year, &next_month, &next_day);
    } else if (max_date > 0 && next_date > max_date) {
        dtp_from_date_value(max_date, &next_year, &next_month, &next_day);
    }
    int next_time = dtp_normalize_hhmm(next_hour * 100 + next_minute);
    int min_for_date = effective_min_time(dtp_date_value(next_year, next_month, next_day));
    int max_for_date = effective_max_time(dtp_date_value(next_year, next_month, next_day));
    if (next_time < min_for_date) next_time = min_for_date;
    if (next_time > max_for_date) next_time = max_for_date;
    year = next_year;
    month = next_month;
    day = next_day;
    hour = next_time / 100;
    minute = next_time % 100;
    has_value = true;
    ensure_selected_visible();
    invalidate();
}

void DateTimePicker::set_range(int min_yyyymmdd, int max_yyyymmdd, int min_hhmm, int max_hhmm) {
    min_date = min_yyyymmdd > 0 ? min_yyyymmdd : 0;
    max_date = max_yyyymmdd > 0 ? max_yyyymmdd : 0;
    if (min_date > 0 && max_date > 0 && min_date > max_date) std::swap(min_date, max_date);
    min_time = dtp_normalize_hhmm(min_hhmm);
    max_time = dtp_normalize_hhmm(max_hhmm);
    if (min_time > max_time) std::swap(min_time, max_time);
    if (has_value) set_datetime(year, month, day, hour, minute);
}

void DateTimePicker::set_options(int today_yyyymmdd, bool next_show_today,
                                 int next_minute_step, int next_date_format) {
    today_value = today_yyyymmdd;
    show_today = next_show_today;
    minute_step = dtp_minute_step(next_minute_step);
    date_format = next_date_format;
    if (has_value) set_datetime(year, month, day, hour, minute);
    clamp_scroll();
}

void DateTimePicker::set_open(bool next_open) {
    open = next_open;
    if (open) ensure_selected_visible();
    invalidate();
}

void DateTimePicker::clear_datetime() {
    has_value = false;
    open = false;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    invalidate();
}

void DateTimePicker::select_today() {
    int target = today_value > 0 ? today_value : date_value();
    if (!can_select_date(target)) return;
    int y = 0, m = 0, d = 0;
    dtp_from_date_value(target, &y, &m, &d);
    set_datetime(y, m, d, hour, minute);
    open = false;
}

void DateTimePicker::select_now() {
    SYSTEMTIME st;
    GetLocalTime(&st);
    int today = dtp_date_value((int)st.wYear, (int)st.wMonth, (int)st.wDay);
    if (!can_select_date(today)) {
        today = date_value();
    }
    int y = 0, m = 0, d = 0;
    dtp_from_date_value(today, &y, &m, &d);
    set_datetime(y, m, d, (int)st.wHour, (int)st.wMinute);
    open = false;
}

void DateTimePicker::set_scroll(int next_hour_scroll, int next_minute_scroll) {
    m_hour_scroll = next_hour_scroll;
    m_minute_scroll = next_minute_scroll;
    clamp_scroll();
    invalidate();
}

void DateTimePicker::get_scroll(int& next_hour_scroll, int& next_minute_scroll) const {
    next_hour_scroll = m_hour_scroll;
    next_minute_scroll = m_minute_scroll;
}

void DateTimePicker::move_month(int delta) {
    int next_year = year;
    int next_month = month + delta;
    while (next_month < 1) {
        next_month += 12;
        --next_year;
    }
    while (next_month > 12) {
        next_month -= 12;
        ++next_year;
    }
    bool old_has_value = has_value;
    set_datetime(next_year, next_month, day, hour, minute);
    has_value = old_has_value;
    invalidate();
}

int DateTimePicker::date_value() const {
    return has_value ? (year * 10000 + month * 100 + day) : 0;
}

int DateTimePicker::time_value() const {
    return has_value ? (hour * 100 + minute) : -1;
}

bool DateTimePicker::is_open() const {
    return open;
}

bool DateTimePicker::can_select_date(int yyyymmdd) const {
    if (yyyymmdd <= 0) return false;
    if (min_date > 0 && yyyymmdd < min_date) return false;
    if (max_date > 0 && yyyymmdd > max_date) return false;
    return true;
}

bool DateTimePicker::can_select_time(int next_hour, int next_minute) const {
    int v = dtp_normalize_hhmm(next_hour * 100 + next_minute);
    int current_date = dtp_date_value(year, month, day);
    return v >= effective_min_time(current_date) && v <= effective_max_time(current_date);
}

std::wstring DateTimePicker::display_text() const {
    if (!has_value) {
        return L"请选择日期时间";
    }
    wchar_t buf[32];
    if (date_format == 1) {
        swprintf_s(buf, L"%04d\u5E74%02d\u6708%02d\u65E5 %02d\u65F6%02d\u5206",
                   year, month, day, hour, minute);
    } else {
        swprintf_s(buf, L"%04d-%02d-%02d %02d:%02d", year, month, day, hour, minute);
    }
    return buf;
}

int DateTimePicker::minute_row_count() const {
    return (59 / dtp_minute_step(minute_step)) + 1;
}

int DateTimePicker::visible_row_count() const {
    return 8;
}

int DateTimePicker::hour_row_count() const {
    return 24;
}

void DateTimePicker::clamp_scroll() {
    int hour_max = (std::max)(0, hour_row_count() - visible_row_count());
    int minute_max = (std::max)(0, minute_row_count() - visible_row_count());
    if (m_hour_scroll < 0) m_hour_scroll = 0;
    if (m_hour_scroll > hour_max) m_hour_scroll = hour_max;
    if (m_minute_scroll < 0) m_minute_scroll = 0;
    if (m_minute_scroll > minute_max) m_minute_scroll = minute_max;
}

void DateTimePicker::ensure_selected_visible() {
    int rows = visible_row_count();
    if (hour < m_hour_scroll) m_hour_scroll = hour;
    if (hour >= m_hour_scroll + rows) m_hour_scroll = hour - rows + 1;
    int step = dtp_minute_step(minute_step);
    int minute_index = minute / step;
    if (minute_index < m_minute_scroll) m_minute_scroll = minute_index;
    if (minute_index >= m_minute_scroll + rows) m_minute_scroll = minute_index - rows + 1;
    clamp_scroll();
}

void DateTimePicker::scroll_part(Part part, int rows) {
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

bool DateTimePicker::select_step(Part part, int delta) {
    if (part == PartDay) {
        int next = date_value();
        if (next <= 0) next = dtp_date_value(year, month, day);
        int y = 0, m = 0, d = 0;
        dtp_from_date_value(next, &y, &m, &d);
        d += delta;
        while (d < 1) {
            --m;
            if (m < 1) { m = 12; --y; }
            d += dtp_days_in_month(y, m);
        }
        while (d > dtp_days_in_month(y, m)) {
            d -= dtp_days_in_month(y, m);
            ++m;
            if (m > 12) { m = 1; ++y; }
        }
        int next_date = dtp_date_value(y, m, d);
        if (!can_select_date(next_date)) return false;
        set_datetime(y, m, d, hour, minute);
        m_active_part = PartDay;
        return true;
    }
    if (part == PartHour) {
        int next = hour + delta;
        while (next >= 0 && next <= 23) {
            if (can_select_time(next, minute)) {
                hour = next;
                has_value = true;
                m_active_part = PartHour;
                ensure_selected_visible();
                invalidate();
                return true;
            }
            next += delta > 0 ? 1 : -1;
        }
    } else if (part == PartMinute) {
        int step = dtp_minute_step(minute_step);
        int index = minute / step + delta;
        while (index >= 0 && index < minute_row_count()) {
            int next = index * step;
            if (next <= 59 && can_select_time(hour, next)) {
                minute = next;
                has_value = true;
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

int DateTimePicker::effective_min_time(int yyyymmdd) const {
    (void)yyyymmdd;
    return min_time;
}

int DateTimePicker::effective_max_time(int yyyymmdd) const {
    (void)yyyymmdd;
    return max_time;
}

DateTimePicker::Part DateTimePicker::header_part_at(int x, int y) const {
    if (!open) return PartNone;
    int py = popup_y();
    int ph = popup_height();
    int pw = popup_width();
    if (x < 0 || x >= pw || y < py || y >= py + ph) return PartNone;
    if (y >= py + ph - 42) {
        if (x >= 10 && x < 94) return PartToday;
        if (x >= 102 && x < 204) return PartNow;
        if (x >= pw - 94 && x < pw - 10) return PartClear;
        return PartNone;
    }
    if (x >= 276 || y >= py + 38) return PartNone;
    if (x >= 10 && x < 48) return PartPrev;
    if (x >= 228 && x < 266) return PartNext;
    return PartNone;
}

DateTimePicker::Part DateTimePicker::part_at(int x, int y, int* value) const {
    if (value) *value = -1;
    if (!open) {
        if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
        return PartNone;
    }

    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    if (x >= 0 && x < pw && y >= py && y < py + ph) {
        int date_w = 276;
        int time_x = date_w + 12;
        float local_y = (float)(y - py);

        if (x < date_w) {
            float header_h = 38.0f;
            float week_h = 26.0f;
            float grid_top = header_h + week_h;
            float grid_h = (float)ph - grid_top - 54.0f;
            if (local_y >= grid_top && grid_h > 0.0f) {
                float cell_w = ((float)date_w - 24.0f) / 7.0f;
                float cell_h = grid_h / 6.0f;
                int col = (int)((x - 12.0f) / cell_w);
                int row = (int)((local_y - grid_top) / cell_h);
                if (col >= 0 && col < 7 && row >= 0 && row < 6) {
                    int next_day = row * 7 + col - dtp_first_weekday(year, month) + 1;
                    int max_day = dtp_days_in_month(year, month);
                    if (next_day >= 1 && next_day <= max_day) {
                        if (!can_select_date(dtp_date_value(year, month, next_day))) return PartNone;
                        if (value) *value = next_day;
                        return PartDay;
                    }
                }
            }
        } else if (x >= time_x) {
            int time_w = pw - time_x - 10;
            int col_w = time_w / 2;
            int row_h = 28;
            int rows_y = py + 38;
            int row = (y - rows_y) / row_h;
            if (row >= 0 && row < visible_row_count()) {
                if (x < time_x + col_w) {
                    int h = m_hour_scroll + row;
                    if (h < 0 || h > 23) return PartNone;
                    if (value) *value = h;
                    return PartHour;
                }
                int m = (m_minute_scroll + row) * dtp_minute_step(minute_step);
                if (m > 59) return PartNone;
                if (value) *value = m;
                return PartMinute;
            }
        }
    }

    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

Element* DateTimePicker::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* DateTimePicker::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    int value = -1;
    Part p = part_at(lx, ly, &value);
    return (p == PartDay || p == PartHour || p == PartMinute ||
            header_part_at(lx, ly) != PartNone) ? this : nullptr;
}

void DateTimePicker::paint(RenderContext& ctx) {
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
    dtp_draw_text(ctx, display_text(), style, fg,
                  (float)style.pad_left, 0.0f,
                  (float)bounds.w - style.pad_left - style.pad_right - 28.0f,
                  (float)bounds.h, 1.0f, DWRITE_FONT_WEIGHT_NORMAL,
                  DWRITE_TEXT_ALIGNMENT_LEADING);
    dtp_draw_text(ctx, L"🗓", style, t->text_secondary,
                  (float)bounds.w - style.pad_right - 26.0f, 0.0f,
                  26.0f, (float)bounds.h);

    ctx.rt->SetTransform(saved);
}

void DateTimePicker::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFEAF2FF;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    int date_w = 276;
    int time_x = date_w + 12;
    int time_w = pw - time_x - 10;

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);
    ctx.rt->DrawLine(D2D1::Point2F((float)date_w, (float)py),
                     D2D1::Point2F((float)date_w, (float)(py + ph)),
                     ctx.get_brush(t->border_default), 1.0f);

    wchar_t title[32];
    swprintf_s(title, L"%04d-%02d", year, month);
    dtp_draw_text(ctx, L"‹", style, muted, 10.0f, (float)py, 38.0f, 38.0f,
                  1.25f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    dtp_draw_text(ctx, L"›", style, muted, 228.0f, (float)py, 38.0f, 38.0f,
                  1.25f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    dtp_draw_text(ctx, title, style, fg, 12.0f, (float)py, (float)date_w - 24.0f, 38.0f,
                  1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    static const wchar_t* weeks[] = { L"日", L"一", L"二", L"三", L"四", L"五", L"六" };
    float cell_w = ((float)date_w - 24.0f) / 7.0f;
    for (int i = 0; i < 7; ++i) {
        dtp_draw_text(ctx, weeks[i], style, muted, 12.0f + cell_w * (float)i,
                      (float)py + 38.0f, cell_w, 26.0f, 0.9f);
    }

    float grid_top = (float)py + 64.0f;
    float grid_h = (float)ph - 118.0f;
    float cell_h = grid_h / 6.0f;
    int start = dtp_first_weekday(year, month);
    int max_day = dtp_days_in_month(year, month);
    for (int d = 1; d <= max_day; ++d) {
        int pos = start + d - 1;
        int row = pos / 7;
        int col = pos % 7;
        float x = 12.0f + cell_w * (float)col;
        float y = grid_top + cell_h * (float)row;
        int current_value = dtp_date_value(year, month, d);
        bool selectable = can_select_date(current_value);
        bool selected = has_value && d == day;
        bool today = show_today && today_value > 0 && current_value == today_value;
        bool hot = selectable && m_hover_part == PartDay && m_hover_value == d;
        if (today) {
            D2D1_RECT_F rr = { x + 5.0f, y + 4.0f, x + cell_w - 5.0f, y + cell_h - 4.0f };
            ctx.rt->DrawRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                ctx.get_brush(t->accent), 1.0f);
        }
        if (selected || hot) {
            D2D1_RECT_F rr = { x + 4.0f, y + 3.0f, x + cell_w - 4.0f, y + cell_h - 3.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                ctx.get_brush(selected ? t->accent : hover_bg));
        }
        wchar_t buf[8];
        swprintf_s(buf, L"%d", d);
        Color text_color = selectable ? (selected ? 0xFFFFFFFF : fg) : muted;
        dtp_draw_text(ctx, buf, style, text_color, x, y, cell_w, cell_h, 0.96f);
    }

    int col_w = time_w / 2;
    int row_h = 28;
    dtp_draw_text(ctx, L"小时", style, muted, (float)time_x, (float)py,
                  (float)col_w, 38.0f, 0.9f);
    dtp_draw_text(ctx, L"分钟", style, muted, (float)(time_x + col_w), (float)py,
                  (float)col_w, 38.0f, 0.9f);
    int rows = visible_row_count();
    int step = dtp_minute_step(minute_step);
    for (int r = 0; r < rows; ++r) {
        int h = m_hour_scroll + r;
        int m = (m_minute_scroll + r) * step;
        float y = (float)(py + 38 + r * row_h);
        bool valid_h = h >= 0 && h < 24 && can_select_time(h, minute);
        bool valid_m = m <= 59 && can_select_time(hour, m);
        bool hot_h = valid_h && m_hover_part == PartHour && m_hover_value == h;
        bool hot_m = valid_m && m_hover_part == PartMinute && m_hover_value == m;
        if (valid_h && (hot_h || hour == h)) {
            D2D1_RECT_F row = { (float)time_x + 2.0f, y + 1.0f,
                (float)(time_x + col_w) - 2.0f, y + (float)row_h - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(hour == h ? dtp_with_alpha(t->accent, 0x33) : t->button_hover));
        }
        if (valid_m && (hot_m || minute == m)) {
            D2D1_RECT_F row = { (float)(time_x + col_w) + 2.0f, y + 1.0f,
                (float)(time_x + time_w) - 2.0f, y + (float)row_h - 1.0f };
            ctx.rt->FillRectangle(row, ctx.get_brush(minute == m ? dtp_with_alpha(t->accent, 0x33) : t->button_hover));
        }
        wchar_t hbuf[8], mbuf[8];
        if (h < 24) {
            swprintf_s(hbuf, L"%02d", h);
            dtp_draw_text(ctx, hbuf, style, valid_h ? (hour == h ? t->accent : fg) : t->text_secondary,
                          (float)time_x, y, (float)col_w, (float)row_h);
        }
        if (m <= 59) {
            swprintf_s(mbuf, L"%02d", m);
            dtp_draw_text(ctx, mbuf, style, valid_m ? (minute == m ? t->accent : fg) : t->text_secondary,
                          (float)(time_x + col_w), y, (float)col_w, (float)row_h);
        }
    }

    float footer_y = (float)(py + ph - 42);
    ctx.rt->DrawLine(D2D1::Point2F(10.0f, footer_y),
                     D2D1::Point2F((float)pw - 10.0f, footer_y),
                     ctx.get_brush(t->border_default), 1.0f);
    D2D1_RECT_F today_rect = { 10.0f, footer_y + 7.0f, 94.0f, footer_y + 35.0f };
    D2D1_RECT_F now_rect = { 102.0f, footer_y + 7.0f, 204.0f, footer_y + 35.0f };
    D2D1_RECT_F clear_rect = { (float)pw - 94.0f, footer_y + 7.0f, (float)pw - 10.0f, footer_y + 35.0f };
    auto draw_footer_button = [&](D2D1_RECT_F r, Part part, const wchar_t* text, Color color) {
        ctx.rt->FillRoundedRectangle(ROUNDED(r, 4.0f, 4.0f),
            ctx.get_brush(m_hover_part == part ? hover_bg : bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(r, 4.0f, 4.0f),
            ctx.get_brush(t->border_default), 1.0f);
        dtp_draw_text(ctx, text, style, color, r.left, r.top, r.right - r.left, r.bottom - r.top, 0.88f);
    };
    draw_footer_button(today_rect, PartToday, L"📍 今天", can_select_date(today_value) ? t->accent : muted);
    draw_footer_button(now_rect, PartNow, L"⏱ 当前时间", t->accent);
    draw_footer_button(clear_rect, PartClear, L"清空", muted);

    ctx.rt->SetTransform(saved);
}

void DateTimePicker::on_mouse_move(int x, int y) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p != PartDay && p != PartHour && p != PartMinute) {
        p = header_part_at(x, y);
        if (p != PartToday && p != PartNow && p != PartClear) {
            p = PartNone;
            value = -1;
        }
    }
    if (p != m_hover_part || value != m_hover_value) {
        m_hover_part = p;
        m_hover_value = value;
        invalidate();
    }
}

void DateTimePicker::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_part = PartNone;
    m_hover_value = -1;
    m_press_part = PartNone;
    m_press_value = -1;
    invalidate();
}

void DateTimePicker::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = header_part_at(x, y);
    m_press_value = -1;
    if (m_press_part == PartNone) {
        m_press_part = part_at(x, y, &m_press_value);
    }
    pressed = true;
    invalidate();
}

void DateTimePicker::on_mouse_up(int x, int y, MouseButton) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p == PartMain && m_press_part == PartMain) {
        open = !open;
        if (open) ensure_selected_visible();
    } else if (m_press_part == PartPrev && header_part_at(x, y) == PartPrev) {
        move_month(-1);
    } else if (m_press_part == PartNext && header_part_at(x, y) == PartNext) {
        move_month(1);
    } else if (m_press_part == PartToday && header_part_at(x, y) == PartToday) {
        select_today();
    } else if (m_press_part == PartNow && header_part_at(x, y) == PartNow) {
        select_now();
    } else if (m_press_part == PartClear && header_part_at(x, y) == PartClear) {
        clear_datetime();
    } else if (p == m_press_part && value == m_press_value) {
        if (p == PartDay && can_select_date(dtp_date_value(year, month, value))) {
            set_datetime(year, month, value, hour, minute);
            m_active_part = PartDay;
        } else if (p == PartHour && can_select_time(value, minute)) {
            hour = value;
            has_value = true;
            m_active_part = PartHour;
            ensure_selected_visible();
        } else if (p == PartMinute && can_select_time(hour, value)) {
            minute = value;
            has_value = true;
            m_active_part = PartMinute;
            ensure_selected_visible();
        }
    }
    m_press_part = PartNone;
    m_press_value = -1;
    pressed = false;
    invalidate();
}

void DateTimePicker::on_mouse_wheel(int x, int y, int delta) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p != PartHour && p != PartMinute) p = m_active_part;
    if (p == PartHour || p == PartMinute) {
        scroll_part(p, delta > 0 ? -3 : 3);
    }
}

void DateTimePicker::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        open = !open;
        if (open) ensure_selected_visible();
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_DELETE || vk == VK_BACK) {
        clear_datetime();
        return;
    } else if (vk == 'T') {
        select_today();
        return;
    } else if (vk == 'N') {
        select_now();
        return;
    } else if (vk == VK_LEFT) {
        if (open && m_active_part != PartDay) {
            m_active_part = m_active_part == PartMinute ? PartHour : PartDay;
            ensure_selected_visible();
        } else {
            select_step(PartDay, -1);
        }
    } else if (vk == VK_RIGHT) {
        if (open && m_active_part != PartMinute) {
            m_active_part = m_active_part == PartDay ? PartHour : PartMinute;
            ensure_selected_visible();
        } else {
            select_step(PartDay, 1);
        }
    } else if (vk == VK_UP) {
        select_step(open ? m_active_part : PartMinute, -1);
    } else if (vk == VK_DOWN) {
        select_step(open ? m_active_part : PartMinute, 1);
    } else if (vk == VK_PRIOR) {
        if (open && (m_active_part == PartHour || m_active_part == PartMinute)) {
            scroll_part(m_active_part, -visible_row_count());
            select_step(m_active_part, -visible_row_count());
        } else {
            move_month(-1);
        }
    } else if (vk == VK_NEXT) {
        if (open && (m_active_part == PartHour || m_active_part == PartMinute)) {
            scroll_part(m_active_part, visible_row_count());
            select_step(m_active_part, visible_row_count());
        } else {
            move_month(1);
        }
    } else if (vk == VK_HOME) {
        if (m_active_part == PartHour) {
            for (int h = 0; h <= 23; ++h) {
                if (can_select_time(h, minute)) { hour = h; break; }
            }
        } else if (m_active_part == PartMinute) {
            int step = dtp_minute_step(minute_step);
            for (int i = 0; i < minute_row_count(); ++i) {
                int m = i * step;
                if (can_select_time(hour, m)) { minute = m; break; }
            }
        } else {
            set_datetime(year, month, 1, hour, minute);
        }
        has_value = true;
        ensure_selected_visible();
    } else if (vk == VK_END) {
        if (m_active_part == PartHour) {
            for (int h = 23; h >= 0; --h) {
                if (can_select_time(h, minute)) { hour = h; break; }
            }
        } else if (m_active_part == PartMinute) {
            int step = dtp_minute_step(minute_step);
            for (int i = minute_row_count() - 1; i >= 0; --i) {
                int m = i * step;
                if (can_select_time(hour, m)) { minute = m; break; }
            }
        } else {
            set_datetime(year, month, dtp_days_in_month(year, month), hour, minute);
        }
        has_value = true;
        ensure_selected_visible();
    }
    invalidate();
}

void DateTimePicker::on_blur() {
    has_focus = false;
    open = false;
    m_hover_part = PartNone;
    m_hover_value = -1;
    m_press_part = PartNone;
    invalidate();
}
