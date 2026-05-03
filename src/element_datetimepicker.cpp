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

static void dtp_clamp_time_parts(int& h, int& m) {
    if (h < 0) h = 0; else if (h > 23) h = 23;
    if (m < 0) m = 0; else if (m > 59) m = 59;
}

static long long dtp_datetime_key(int yyyymmdd, int hhmm) {
    return (long long)yyyymmdd * 10000LL + (long long)dtp_normalize_hhmm(hhmm);
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
    return range_select ? (std::max)(bounds.w, 800) : (std::max)(bounds.w, 420);
}

int DateTimePicker::popup_height() const {
    return 38 + visible_row_count() * 28 + (range_select ? 86 : 54);
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
    range_start_date = 0; range_start_time = 0;
    range_end_date = 0; range_end_time = 0;
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

void DateTimePicker::set_default_time(int h, int m) {
    dtp_clamp_time_parts(h, m);
    default_hour = h;
    default_minute = m;
    default_start_hour = h;
    default_start_minute = m;
    default_end_hour = h;
    default_end_minute = m;
    invalidate();
}

void DateTimePicker::set_range_default_time(int start_hour, int start_minute, int end_hour, int end_minute) {
    dtp_clamp_time_parts(start_hour, start_minute);
    dtp_clamp_time_parts(end_hour, end_minute);
    default_start_hour = start_hour;
    default_start_minute = start_minute;
    default_end_hour = end_hour;
    default_end_minute = end_minute;
    default_hour = start_hour;
    default_minute = start_minute;
    invalidate();
}

void DateTimePicker::set_shortcuts(const std::vector<DateShortcut>& items) {
    shortcuts = items;
    invalidate();
}

void DateTimePicker::set_selection_range(int start_date, int start_time, int end_date, int end_time, bool enabled) {
    range_select = enabled;
    range_start_date = 0;
    range_start_time = 0;
    range_end_date = 0;
    range_end_time = 0;
    if (enabled && start_date > 0) {
        int y = 0, m = 0, d = 0;
        dtp_from_date_value(start_date, &y, &m, &d);
        range_start_date = dtp_date_value(y, m, d);
        range_start_time = dtp_normalize_hhmm(start_time);
        year = y; month = m; day = d;
        hour = range_start_time / 100;
        minute = range_start_time % 100;
        has_value = true;
    }
    if (enabled && end_date > 0) {
        int y = 0, m = 0, d = 0;
        dtp_from_date_value(end_date, &y, &m, &d);
        range_end_date = dtp_date_value(y, m, d);
        range_end_time = dtp_normalize_hhmm(end_time);
    }
    if (range_start_date > 0 && range_end_date > 0 &&
        dtp_datetime_key(range_start_date, range_start_time) > dtp_datetime_key(range_end_date, range_end_time)) {
        std::swap(range_start_date, range_end_date);
        std::swap(range_start_time, range_end_time);
    }
    ensure_selected_visible();
    invalidate();
}

void DateTimePicker::get_selection_range(int& start_date, int& start_time, int& end_date, int& end_time, bool& enabled) const {
    start_date = range_start_date;
    start_time = range_start_time;
    end_date = range_end_date;
    end_time = range_end_time;
    enabled = range_select;
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

int DateTimePicker::range_default_time(bool is_end) const {
    return dtp_normalize_hhmm((is_end ? default_end_hour : default_start_hour) * 100 +
                             (is_end ? default_end_minute : default_start_minute));
}

std::wstring DateTimePicker::display_text() const {
    auto fmt_dt = [&](int date_val, int time_val) -> std::wstring {
        if (date_val <= 0) return L"";
        int y = 0, m = 0, d = 0;
        dtp_from_date_value(date_val, &y, &m, &d);
        int h = time_val > 0 ? time_val / 100 : 0;
        int mi = time_val > 0 ? time_val % 100 : 0;
        wchar_t buf[48];
        if (date_format == 1)
            swprintf_s(buf, L"%04d年%02d月%02d日 %02d时%02d分", y, m, d, h, mi);
        else
            swprintf_s(buf, L"%04d-%02d-%02d %02d:%02d", y, m, d, h, mi);
        return buf;
    };

    if (range_select) {
        std::wstring s = range_start_date > 0 ? fmt_dt(range_start_date, range_start_time)
            : (start_placeholder.empty() ? L"开始日期时间" : start_placeholder);
        s += range_separator;
        s += range_end_date > 0 ? fmt_dt(range_end_date, range_end_time)
            : (end_placeholder.empty() ? L"结束日期时间" : end_placeholder);
        return s;
    }

    if (!has_value) return L"请选择日期时间";
    return fmt_dt(date_value(), time_value());
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
    if (m_end_hour_scroll < 0) m_end_hour_scroll = 0;
    if (m_end_hour_scroll > hour_max) m_end_hour_scroll = hour_max;
    if (m_end_minute_scroll < 0) m_end_minute_scroll = 0;
    if (m_end_minute_scroll > minute_max) m_end_minute_scroll = minute_max;
}

void DateTimePicker::ensure_time_visible(int hhmm, int& hour_scroll, int& minute_scroll) {
    int rows = visible_row_count();
    int next_time = dtp_normalize_hhmm(hhmm);
    int next_hour = next_time / 100;
    int next_minute = next_time % 100;
    if (next_hour < hour_scroll) hour_scroll = next_hour;
    if (next_hour >= hour_scroll + rows) hour_scroll = next_hour - rows + 1;
    int step = dtp_minute_step(minute_step);
    int minute_index = next_minute / step;
    if (minute_index < minute_scroll) minute_scroll = minute_index;
    if (minute_index >= minute_scroll + rows) minute_scroll = minute_index - rows + 1;
}

void DateTimePicker::ensure_selected_visible() {
    if (range_select) {
        int start_time = range_start_date > 0 ? range_start_time : range_default_time(false);
        int end_time = range_end_date > 0 ? range_end_time : range_default_time(true);
        ensure_time_visible(start_time, m_hour_scroll, m_minute_scroll);
        ensure_time_visible(end_time, m_end_hour_scroll, m_end_minute_scroll);
    } else {
        ensure_time_visible(hour * 100 + minute, m_hour_scroll, m_minute_scroll);
    }
    clamp_scroll();
}

void DateTimePicker::scroll_part(Part part, int rows) {
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

bool DateTimePicker::select_step(Part part, int delta) {
    if (range_select && (part == PartHour || part == PartMinute || part == PartHourEnd || part == PartMinuteEnd)) {
        bool is_end = part == PartHourEnd || part == PartMinuteEnd;
        int current_date = is_end ? (range_end_date > 0 ? range_end_date : (range_start_date > 0 ? range_start_date : date_value()))
                                  : (range_start_date > 0 ? range_start_date : date_value());
        int current_time = is_end ? (range_end_date > 0 ? range_end_time : (range_start_date > 0 ? range_start_time : time_value()))
                                  : (range_start_date > 0 ? range_start_time : time_value());
        if (current_date <= 0) current_date = dtp_date_value(year, month, day);
        if (current_time < 0) current_time = range_default_time(is_end);
        current_time = dtp_normalize_hhmm(current_time);
        int base_hour = current_time / 100;
        int base_minute = current_time % 100;
        if (part == PartHour || part == PartHourEnd) {
            int next = base_hour + delta;
            while (next >= 0 && next <= 23) {
                if (can_select_range_datetime(part, current_date, next, base_minute)) {
                    if (is_end) {
                        range_end_date = current_date;
                        range_end_time = next * 100 + base_minute;
                    } else {
                        range_start_date = current_date;
                        range_start_time = next * 100 + base_minute;
                    }
                    m_active_part = part;
                    has_value = true;
                    ensure_selected_visible();
                    invalidate();
                    return true;
                }
                next += delta > 0 ? 1 : -1;
            }
        } else {
            int step = dtp_minute_step(minute_step);
            int index = base_minute / step + delta;
            while (index >= 0 && index < minute_row_count()) {
                int next = index * step;
                if (next <= 59 && can_select_range_datetime(part, current_date, base_hour, next)) {
                    if (is_end) {
                        range_end_date = current_date;
                        range_end_time = base_hour * 100 + next;
                    } else {
                        range_start_date = current_date;
                        range_start_time = base_hour * 100 + next;
                    }
                    m_active_part = part;
                    has_value = true;
                    ensure_selected_visible();
                    invalidate();
                    return true;
                }
                index += delta > 0 ? 1 : -1;
            }
        }
        return false;
    }

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

bool DateTimePicker::can_select_range_datetime(Part part, int yyyymmdd, int next_hour, int next_minute) const {
    if (!can_select_date(yyyymmdd)) return false;
    int v = dtp_normalize_hhmm(next_hour * 100 + next_minute);
    if (v < effective_min_time(yyyymmdd) || v > effective_max_time(yyyymmdd)) return false;
    if (!range_select) return true;
    long long next_key = dtp_datetime_key(yyyymmdd, v);
    if ((part == PartDay || part == PartHour || part == PartMinute) && range_end_date > 0 &&
        next_key > dtp_datetime_key(range_end_date, range_end_time)) {
        return false;
    }
    if ((part == PartDayEnd || part == PartHourEnd || part == PartMinuteEnd) && range_start_date > 0 &&
        next_key < dtp_datetime_key(range_start_date, range_start_time)) {
        return false;
    }
    return true;
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
    if (range_select) {
        int half = pw / 2;
        int date_w = (pw - 36) / 2 - 60;
        if (date_w < 200) date_w = 200;
        if (y >= py + 38) return PartNone;
        if (x >= 10 && x < 48) return PartPrev;
        if (x >= half + date_w - 34 && x < half + date_w - 6) return PartNext;
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
    int py = popup_y(), pw = popup_width(), ph = popup_height();
    if (x < 0 || x >= pw || y < py || y >= py + ph) {
        if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
        return PartNone;
    }
    bool is_right = range_select && x >= pw / 2;
    float ox = is_right ? (float)(pw / 2) : 0.0f;
    float pw2 = (float)(pw / 2);
    int lx = x - (int)ox;
    Part day_part = is_right ? PartDayEnd : PartDay;
    Part hour_part = is_right ? PartHourEnd : PartHour;
    Part minute_part = is_right ? PartMinuteEnd : PartMinute;
    int p_year = is_right ? (month < 12 ? year : year + 1) : year;
    int p_month = is_right ? (month < 12 ? month + 1 : 1) : month;

    int date_w = range_select ? (pw - 36) / 2 - 60 : 276;
    if (date_w < 200) date_w = 200;
    int time_x_offset = date_w + 6;

    float local_y = (float)(y - py);
    if (lx < date_w) {
        float grid_top = 62.0f;
        float grid_h = (float)ph - (range_select ? 116.0f : 118.0f);
        if (local_y >= grid_top && grid_h > 0) {
            float cell_w = ((float)date_w - 24.0f) / 7.0f;
            float cell_h = grid_h / 6.0f;
            int col = (int)((lx - 12.0f) / cell_w);
            int row = (int)((local_y - grid_top) / cell_h);
            if (col >= 0 && col < 7 && row >= 0 && row < 6) {
                int next_day = row * 7 + col - dtp_first_weekday(p_year, p_month) + 1;
                if (next_day >= 1 && next_day <= dtp_days_in_month(p_year, p_month)) {
                    int cur_date = dtp_date_value(p_year, p_month, next_day);
                    int default_time = is_right
                        ? (range_end_date > 0 ? range_end_time : range_default_time(true))
                        : (range_start_date > 0 ? range_start_time : range_default_time(false));
                    if (range_select) {
                        if (!can_select_range_datetime(day_part, cur_date, default_time / 100, default_time % 100)) return PartNone;
                    } else if (!can_select_date(cur_date)) {
                        return PartNone;
                    }
                    if (value) *value = next_day;
                    return day_part;
                }
            }
        }
    } else if (lx >= time_x_offset) {
        int time_col_w = (int)(pw2 - date_w - 12) / 2;
        if (time_col_w <= 0 || lx >= time_x_offset + time_col_w * 2) return PartNone;
        int row_h = 28, rows_y = py + 38;
        int row = (y - rows_y) / row_h;
        if (row >= 0 && row < visible_row_count()) {
            if (lx < time_x_offset + time_col_w) {
                int h = (is_right ? m_end_hour_scroll : m_hour_scroll) + row;
                if (h < 0 || h > 23) return PartNone;
                if (value) *value = h;
                return hour_part;
            }
            int m = ((is_right ? m_end_minute_scroll : m_minute_scroll) + row) * dtp_minute_step(minute_step);
            if (m > 59) return PartNone;
            if (value) *value = m;
            return minute_part;
        }
    }
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
            p == PartDayEnd || p == PartHourEnd || p == PartMinuteEnd ||
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
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF, fg = t->text_primary, muted = t->text_secondary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFEAF2FF;
    int py = popup_y(), pw = popup_width(), ph = popup_height();

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f, rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);

    auto draw_panel = [&](int panel_idx, int p_year, int p_month, int selected_date, int sel_hour, int sel_minute,
                           Part day_part, Part hour_part, Part minute_part) {
        float ox = panel_idx == 0 ? 0.0f : (float)(pw / 2);
        float pw2 = (float)(pw / 2);
        int date_w = range_select ? (pw - 36) / 2 - 60 : 276;
        if (date_w < 200) date_w = 200;
        int time_col_w = (int)(pw2 - date_w - 12) / 2;

        if (panel_idx > 0)
            ctx.rt->DrawLine(D2D1::Point2F(ox, (float)py), D2D1::Point2F(ox, (float)(py + ph)), ctx.get_brush(t->border_default), 2.0f);

        wchar_t title[32]; swprintf_s(title, L"%04d-%02d", p_year, p_month);
        if (!range_select || panel_idx == 0) {
            dtp_draw_text(ctx, L"\u2039", style, muted, ox + 10, (float)py, 28.0f, 38.0f, 1.2f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
        }
        if (!range_select || panel_idx == 1) {
            dtp_draw_text(ctx, L"\u203a", style, muted, ox + date_w - 34, (float)py, 28.0f, 38.0f, 1.2f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
        }
        dtp_draw_text(ctx, title, style, fg, ox + 12, (float)py, (float)date_w - 24, 38.0f, 1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

        static const wchar_t* weeks[] = { L"\u65e5", L"\u4e00", L"\u4e8c", L"\u4e09", L"\u56db", L"\u4e94", L"\u516d" };
        float cell_w = ((float)date_w - 24.0f) / 7.0f;
        for (int i = 0; i < 7; ++i)
            dtp_draw_text(ctx, weeks[i], style, muted, ox + 12 + cell_w * i, (float)py + 38, cell_w, 24.0f, 0.82f);

        float grid_top = (float)py + 62.0f;
        float grid_h = (float)ph - (range_select ? 116.0f : 118.0f);
        float cell_h = grid_h / 6.0f;
        int start = dtp_first_weekday(p_year, p_month);
        int max_day = dtp_days_in_month(p_year, p_month);
        for (int d = 1; d <= max_day; ++d) {
            int pos = start + d - 1;
            float x = ox + 12 + cell_w * (pos % 7);
            float y = grid_top + cell_h * (pos / 7);
            int cur_date = dtp_date_value(p_year, p_month, d);
            bool ok = range_select
                ? can_select_range_datetime(day_part, cur_date, sel_hour, sel_minute)
                : can_select_date(cur_date);
            bool sel = has_value && selected_date > 0 && cur_date == selected_date;
            bool in_range = range_select && range_start_date > 0 && range_end_date > 0 &&
                cur_date > range_start_date && cur_date < range_end_date;
            bool hot = ok && m_hover_part == day_part && m_hover_value == d;
            if (in_range) {
                D2D1_RECT_F rr = { x + 2, y + 5, x + cell_w - 2, y + cell_h - 5 };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(dark ? 0xFF2D3B55 : 0xFFE8F2FF));
            }
            if (sel || hot) {
                D2D1_RECT_F rr = { x + 3, y + 2, x + cell_w - 3, y + cell_h - 2 };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(sel ? t->accent : hover_bg));
            }
            wchar_t buf[8]; swprintf_s(buf, L"%d", d);
            dtp_draw_text(ctx, buf, style, ok ? (sel ? 0xFFFFFFFF : fg) : muted, x, y, cell_w, cell_h, 0.90f);
        }

        float tx = ox + date_w + 6;
        int row_h = 28, rows = visible_row_count(), step = dtp_minute_step(minute_step);
        int time_date = selected_date > 0 ? selected_date : dtp_date_value(p_year, p_month, 1);
        dtp_draw_text(ctx, L"\u65f6", style, muted, tx, (float)py, (float)time_col_w, 38.0f, 0.9f);
        dtp_draw_text(ctx, L"\u5206", style, muted, tx + time_col_w, (float)py, (float)time_col_w, 38.0f, 0.9f);
        for (int r = 0; r < rows; ++r) {
            int h = (panel_idx == 1 && range_select ? m_end_hour_scroll : m_hour_scroll) + r;
            int m = ((panel_idx == 1 && range_select ? m_end_minute_scroll : m_minute_scroll) + r) * step;
            float yr = (float)(py + 38 + r * row_h);
            bool vh = h >= 0 && h < 24 && (range_select
                ? can_select_range_datetime(hour_part, time_date, h, sel_minute)
                : can_select_time(h, sel_minute));
            bool vm = m <= 59 && (range_select
                ? can_select_range_datetime(minute_part, time_date, sel_hour, m)
                : can_select_time(sel_hour, m));
            bool sh = sel_hour == h, sm = sel_minute == m;
            bool hh = vh && m_hover_part == hour_part && m_hover_value == h;
            bool hm = vm && m_hover_part == minute_part && m_hover_value == m;
            if (vh && (hh || sh))
                ctx.rt->FillRectangle(D2D1::RectF(tx + 2, yr + 1, tx + time_col_w - 2, yr + row_h - 1),
                    ctx.get_brush(sh ? dtp_with_alpha(t->accent, 0x33) : t->button_hover));
            if (vm && (hm || sm))
                ctx.rt->FillRectangle(D2D1::RectF(tx + time_col_w + 2, yr + 1, tx + time_col_w * 2 - 2, yr + row_h - 1),
                    ctx.get_brush(sm ? dtp_with_alpha(t->accent, 0x33) : t->button_hover));
            wchar_t hb[8], mb[8];
            if (h < 24) { swprintf_s(hb, L"%02d", h); dtp_draw_text(ctx, hb, style, vh ? (sh ? t->accent : fg) : muted, tx, yr, (float)time_col_w, (float)row_h, 0.90f); }
            if (m <= 59) { swprintf_s(mb, L"%02d", m); dtp_draw_text(ctx, mb, style, vm ? (sm ? t->accent : fg) : muted, tx + time_col_w, yr, (float)time_col_w, (float)row_h, 0.90f); }
        }
    };

    if (range_select) {
        int start_year = year, start_month = month;
        int end_year = year, end_month = month + 1;
        if (end_month > 12) { end_month = 1; ++end_year; }
        int start_time = range_start_date > 0 ? range_start_time : range_default_time(false);
        int end_time = range_end_date > 0 ? range_end_time : range_default_time(true);
        draw_panel(0, start_year, start_month, range_start_date, start_time / 100, start_time % 100,
                   PartDay, PartHour, PartMinute);
        draw_panel(1, end_year, end_month, range_end_date, end_time / 100, end_time % 100,
                   PartDayEnd, PartHourEnd, PartMinuteEnd);
    } else {
        draw_panel(0, year, month, date_value(), hour, minute, PartDay, PartHour, PartMinute);
    }

    float footer_y = (float)(py + ph) - 42.0f;
    ctx.rt->DrawLine(D2D1::Point2F(12, footer_y), D2D1::Point2F((float)pw - 12, footer_y), ctx.get_brush(t->border_default), 1.0f);
    auto draw_btn = [&](float l, float r, const wchar_t* label, Color c, bool hot) {
        D2D1_RECT_F br = { l, footer_y + 7, r, footer_y + 35 };
        ctx.rt->FillRoundedRectangle(ROUNDED(br, 4.0f, 4.0f), ctx.get_brush(hot ? (dark ? 0xFF313244 : 0xFFEAF2FF) : bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(br, 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);
        dtp_draw_text(ctx, label, style, c, l, footer_y + 7, r - l, 28.0f, 0.85f);
    };
    draw_btn(12, 85, L"\U0001f4cd \u4eca\u5929", m_hover_part == PartToday ? t->accent : muted, m_hover_part == PartToday);
    draw_btn(95, 182, L"\u23f1 \u5f53\u524d\u65f6\u95f4", m_hover_part == PartNow ? t->accent : muted, m_hover_part == PartNow);
    draw_btn((float)pw - 82, (float)pw - 12, L"\u6e05\u7a7a", m_hover_part == PartClear ? t->accent : muted, m_hover_part == PartClear);

    ctx.rt->SetTransform(saved);
}

void DateTimePicker::on_mouse_move(int x, int y) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p != PartDay && p != PartDayEnd && p != PartHour && p != PartHourEnd && p != PartMinute && p != PartMinuteEnd) {
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
        if (range_select) {
            bool is_end = (p == PartDayEnd || p == PartHourEnd || p == PartMinuteEnd);
            if (p == PartDay || p == PartDayEnd) {
                bool is_right_panel = x >= popup_width() / 2;
                int p_year = is_right_panel ? (month < 12 ? year : year + 1) : year;
                int p_month = is_right_panel ? (month < 12 ? month + 1 : 1) : month;
                int cur_date = dtp_date_value(p_year, p_month, value);
                int default_time = range_default_time(is_end);
                int candidate_time = is_end
                    ? (range_end_date > 0 ? range_end_time : default_time)
                    : (range_start_date > 0 ? range_start_time : default_time);
                if (can_select_range_datetime(p, cur_date, candidate_time / 100, candidate_time % 100)) {
                    if (is_end) {
                        range_end_date = cur_date;
                        range_end_time = candidate_time;
                        m_active_part = PartDayEnd;
                    } else {
                        range_start_date = cur_date;
                        range_start_time = candidate_time;
                        range_end_date = 0; range_end_time = 0;
                        m_active_part = PartDay;
                    }
                    has_value = true;
                }
            } else {
                int cur_time = 0;
                bool valid_time = false;
                int cur_date = is_end ? (range_end_date > 0 ? range_end_date : (range_start_date > 0 ? range_start_date : date_value()))
                                      : (range_start_date > 0 ? range_start_date : date_value());
                if (cur_date <= 0) cur_date = dtp_date_value(year, month, day);
                if (p == PartHour || p == PartHourEnd) {
                    int cur_min = is_end ? (range_end_date > 0 ? range_end_time % 100 : range_default_time(true) % 100)
                                         : (range_start_date > 0 ? range_start_time % 100 : range_default_time(false) % 100);
                    if (can_select_range_datetime(p, cur_date, value, cur_min)) {
                        cur_time = value * 100 + cur_min;
                        valid_time = true;
                    }
                } else if (p == PartMinute || p == PartMinuteEnd) {
                    int cur_hour = is_end ? (range_end_date > 0 ? range_end_time / 100 : range_default_time(true) / 100)
                                          : (range_start_date > 0 ? range_start_time / 100 : range_default_time(false) / 100);
                    if (can_select_range_datetime(p, cur_date, cur_hour, value)) {
                        cur_time = cur_hour * 100 + value;
                        valid_time = true;
                    }
                }
                if (valid_time) {
                    if (is_end) {
                        range_end_date = cur_date;
                        range_end_time = cur_time;
                        m_active_part = p;
                    } else {
                        range_start_date = cur_date;
                        range_start_time = cur_time;
                        m_active_part = p;
                    }
                    has_value = true;
                }
            }
            if (range_start_date > 0 && range_end_date > 0) {
                if (dtp_datetime_key(range_start_date, range_start_time) > dtp_datetime_key(range_end_date, range_end_time)) {
                    range_end_date = 0;
                    range_end_time = 0;
                }
            }
        } else {
            if (p == PartDay && can_select_date(dtp_date_value(year, month, value))) {
                set_datetime(year, month, value, hour, minute);
                m_active_part = PartDay;
            } else if (p == PartHour && can_select_time(value, minute)) {
                hour = value; has_value = true; m_active_part = PartHour;
                ensure_selected_visible();
            } else if (p == PartMinute && can_select_time(hour, value)) {
                minute = value; has_value = true; m_active_part = PartMinute;
                ensure_selected_visible();
            }
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
        if (open && range_select) {
            if (m_active_part == PartMinuteEnd) m_active_part = PartHourEnd;
            else if (m_active_part == PartHourEnd) m_active_part = PartMinute;
            else if (m_active_part == PartMinute) m_active_part = PartHour;
            else if (m_active_part == PartHour) m_active_part = PartDay;
            else m_active_part = PartDay;
            ensure_selected_visible();
        } else if (open && m_active_part != PartDay) {
            m_active_part = m_active_part == PartMinute ? PartHour : PartDay;
            ensure_selected_visible();
        } else {
            select_step(PartDay, -1);
        }
    } else if (vk == VK_RIGHT) {
        if (open && range_select) {
            if (m_active_part == PartDay) m_active_part = PartHour;
            else if (m_active_part == PartHour) m_active_part = PartMinute;
            else if (m_active_part == PartMinute) m_active_part = PartHourEnd;
            else if (m_active_part == PartHourEnd) m_active_part = PartMinuteEnd;
            else m_active_part = PartMinuteEnd;
            ensure_selected_visible();
        } else if (open && m_active_part != PartMinute) {
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
        if (open && (m_active_part == PartHour || m_active_part == PartMinute ||
                     m_active_part == PartHourEnd || m_active_part == PartMinuteEnd)) {
            scroll_part(m_active_part, -visible_row_count());
            select_step(m_active_part, -visible_row_count());
        } else {
            move_month(-1);
        }
    } else if (vk == VK_NEXT) {
        if (open && (m_active_part == PartHour || m_active_part == PartMinute ||
                     m_active_part == PartHourEnd || m_active_part == PartMinuteEnd)) {
            scroll_part(m_active_part, visible_row_count());
            select_step(m_active_part, visible_row_count());
        } else {
            move_month(1);
        }
    } else if (vk == VK_HOME) {
        if (range_select && (m_active_part == PartHour || m_active_part == PartMinute ||
                             m_active_part == PartHourEnd || m_active_part == PartMinuteEnd)) {
            Part part = m_active_part;
            bool is_end = part == PartHourEnd || part == PartMinuteEnd;
            bool is_hour_part = part == PartHour || part == PartHourEnd;
            int current_date = is_end ? (range_end_date > 0 ? range_end_date : (range_start_date > 0 ? range_start_date : date_value()))
                                      : (range_start_date > 0 ? range_start_date : date_value());
            int current_time = is_end ? (range_end_date > 0 ? range_end_time : range_default_time(true))
                                      : (range_start_date > 0 ? range_start_time : range_default_time(false));
            if (current_date <= 0) current_date = dtp_date_value(year, month, day);
            current_time = dtp_normalize_hhmm(current_time);
            int current_hour = current_time / 100;
            int current_minute = current_time % 100;
            if (is_hour_part) {
                for (int h = 0; h <= 23; ++h) {
                    if (can_select_range_datetime(part, current_date, h, current_minute)) {
                        if (is_end) { range_end_date = current_date; range_end_time = h * 100 + current_minute; }
                        else { range_start_date = current_date; range_start_time = h * 100 + current_minute; }
                        break;
                    }
                }
            } else {
                int step = dtp_minute_step(minute_step);
                for (int i = 0; i < minute_row_count(); ++i) {
                    int m = i * step;
                    if (can_select_range_datetime(part, current_date, current_hour, m)) {
                        if (is_end) { range_end_date = current_date; range_end_time = current_hour * 100 + m; }
                        else { range_start_date = current_date; range_start_time = current_hour * 100 + m; }
                        break;
                    }
                }
            }
        } else if (m_active_part == PartHour) {
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
        if (range_select && (m_active_part == PartHour || m_active_part == PartMinute ||
                             m_active_part == PartHourEnd || m_active_part == PartMinuteEnd)) {
            Part part = m_active_part;
            bool is_end = part == PartHourEnd || part == PartMinuteEnd;
            bool is_hour_part = part == PartHour || part == PartHourEnd;
            int current_date = is_end ? (range_end_date > 0 ? range_end_date : (range_start_date > 0 ? range_start_date : date_value()))
                                      : (range_start_date > 0 ? range_start_date : date_value());
            int current_time = is_end ? (range_end_date > 0 ? range_end_time : range_default_time(true))
                                      : (range_start_date > 0 ? range_start_time : range_default_time(false));
            if (current_date <= 0) current_date = dtp_date_value(year, month, day);
            current_time = dtp_normalize_hhmm(current_time);
            int current_hour = current_time / 100;
            int current_minute = current_time % 100;
            if (is_hour_part) {
                for (int h = 23; h >= 0; --h) {
                    if (can_select_range_datetime(part, current_date, h, current_minute)) {
                        if (is_end) { range_end_date = current_date; range_end_time = h * 100 + current_minute; }
                        else { range_start_date = current_date; range_start_time = h * 100 + current_minute; }
                        break;
                    }
                }
            } else {
                int step = dtp_minute_step(minute_step);
                for (int i = minute_row_count() - 1; i >= 0; --i) {
                    int m = i * step;
                    if (can_select_range_datetime(part, current_date, current_hour, m)) {
                        if (is_end) { range_end_date = current_date; range_end_time = current_hour * 100 + m; }
                        else { range_start_date = current_date; range_start_time = current_hour * 100 + m; }
                        break;
                    }
                }
            }
        } else if (m_active_part == PartHour) {
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
