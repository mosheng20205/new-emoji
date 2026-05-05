#include "element_datepicker.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwchar>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static bool leap_year(int y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

static int days_in_month(int y, int m) {
    static const int days[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (m == 2) return leap_year(y) ? 29 : 28;
    if (m < 1 || m > 12) return 30;
    return days[m - 1];
}

static int first_weekday(int y, int m) {
    if (m < 3) {
        m += 12;
        --y;
    }
    int k = y % 100;
    int j = y / 100;
    int h = (1 + (13 * (m + 1)) / 5 + k + k / 4 + j / 4 + 5 * j) % 7;
    return (h + 6) % 7;
}

static int datepicker_value(int y, int m, int d) {
    return y * 10000 + m * 100 + d;
}

static void datepicker_from_value(int value, int* y, int* m, int* d) {
    int yy = value / 10000;
    int mm = (value / 100) % 100;
    int dd = value % 100;
    if (yy < 1900) yy = 1900;
    if (yy > 2099) yy = 2099;
    if (mm < 1) mm = 1;
    if (mm > 12) mm = 12;
    int max_day = days_in_month(yy, mm);
    if (dd < 1) dd = 1;
    if (dd > max_day) dd = max_day;
    if (y) *y = yy;
    if (m) *m = mm;
    if (d) *d = dd;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
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

int DatePicker::popup_width() const {
    return (std::max)(bounds.w, 300);
}

int DatePicker::popup_height() const {
    return 318;
}

int DatePicker::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

void DatePicker::set_date(int next_year, int next_month, int next_day) {
    if (next_year < 1900) next_year = 1900;
    if (next_year > 2099) next_year = 2099;
    if (next_month < 1) next_month = 1;
    if (next_month > 12) next_month = 12;
    int max_day = days_in_month(next_year, next_month);
    if (next_day < 1) next_day = 1;
    if (next_day > max_day) next_day = max_day;
    int next_value = datepicker_value(next_year, next_month, next_day);
    if (min_value > 0 && next_value < min_value) {
        datepicker_from_value(min_value, &next_year, &next_month, &next_day);
    } else if (max_value > 0 && next_value > max_value) {
        datepicker_from_value(max_value, &next_year, &next_month, &next_day);
    }
    year = next_year;
    month = next_month;
    selected_day = next_day;
    has_value = true;
    invalidate();
}

void DatePicker::set_range(int min_yyyymmdd, int max_yyyymmdd) {
    min_value = min_yyyymmdd > 0 ? min_yyyymmdd : 0;
    max_value = max_yyyymmdd > 0 ? max_yyyymmdd : 0;
    if (min_value > 0 && max_value > 0 && min_value > max_value) {
        std::swap(min_value, max_value);
    }
    if (has_value) {
        set_date(year, month, selected_day);
    }
    if (range_start > 0 && !can_select(range_start)) range_start = 0;
    if (range_end > 0 && !can_select(range_end)) range_end = 0;
    if (range_start > 0 && range_end > 0 && range_start > range_end) {
        std::swap(range_start, range_end);
    }
}

void DatePicker::set_options(int today_yyyymmdd, bool next_show_today, int next_date_format) {
    today_value = today_yyyymmdd;
    show_today = next_show_today;
    date_format = next_date_format;
    invalidate();
}

void DatePicker::set_open(bool next_open) {
    open = next_open;
    invalidate();
}

void DatePicker::clear_date() {
    has_value = false;
    range_start = 0;
    range_end = 0;
    open = false;
    m_hover_day = 0;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    invalidate();
}

void DatePicker::select_today() {
    int target = today_value > 0 ? today_value : value();
    if (!can_select(target)) return;
    int y = 0;
    int m = 0;
    int d = 0;
    datepicker_from_value(target, &y, &m, &d);
    set_date(y, m, d);
    if (range_select) {
        range_start = target;
        range_end = target;
    }
    open = false;
    invalidate();
}

void DatePicker::set_selection_range(int start_yyyymmdd, int end_yyyymmdd, bool enabled) {
    range_select = enabled;
    range_start = can_select(start_yyyymmdd) ? start_yyyymmdd : 0;
    range_end = can_select(end_yyyymmdd) ? end_yyyymmdd : 0;
    if (range_start > 0 && range_end > 0 && range_start > range_end) {
        std::swap(range_start, range_end);
    }
    int target = range_end > 0 ? range_end : range_start;
    if (target > 0) {
        int y = 0;
        int m = 0;
        int d = 0;
        datepicker_from_value(target, &y, &m, &d);
        year = y;
        month = m;
        selected_day = d;
        has_value = true;
    }
    invalidate();
}

void DatePicker::get_selection_range(int& start_yyyymmdd, int& end_yyyymmdd, bool& enabled) const {
    start_yyyymmdd = range_start;
    end_yyyymmdd = range_end;
    enabled = range_select;
}

void DatePicker::move_month(int delta) {
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
    set_date(next_year, next_month, selected_day);
    has_value = old_has_value;
    invalidate();
}

static int add_days_simple(int value, int delta) {
    int y = 0;
    int m = 0;
    int d = 0;
    datepicker_from_value(value, &y, &m, &d);
    d += delta;
    while (d < 1) {
        --m;
        if (m < 1) { m = 12; --y; }
        d += days_in_month(y, m);
    }
    while (d > days_in_month(y, m)) {
        d -= days_in_month(y, m);
        ++m;
        if (m > 12) { m = 1; ++y; }
    }
    return datepicker_value(y, m, d);
}

int DatePicker::value() const {
    return has_value ? (year * 10000 + month * 100 + selected_day) : 0;
}

bool DatePicker::is_open() const {
    return open;
}

bool DatePicker::can_select(int yyyymmdd) const {
    if (yyyymmdd <= 0) return false;
    if (min_value > 0 && yyyymmdd < min_value) return false;
    if (max_value > 0 && yyyymmdd > max_value) return false;
    if (disabled_date_cb && disabled_date_cb(id, yyyymmdd) != 0) return false;
    return true;
}

void DatePicker::set_multi_select(bool enabled) {
    multi_select = enabled;
    if (!enabled) selected_dates.clear();
    range_select = false;
    invalidate();
}

void DatePicker::set_mode(int m) {
    if (m < 0) m = 0; else if (m > 3) m = 3;
    picker_mode = m;
    invalidate();
}

int DatePicker::mode() const { return picker_mode; }

void DatePicker::set_shortcuts(const std::vector<DateShortcut>& items) {
    shortcuts = items;
    invalidate();
}

int DatePicker::day_value(int day) const {
    return datepicker_value(year, month, day);
}

std::wstring DatePicker::display_text() const {
    if (range_select) {
        auto fmtv = [&](int val) -> std::wstring {
            if (val <= 0) return L"";
            int y = 0, m = 0, d = 0;
            datepicker_from_value(val, &y, &m, &d);
            wchar_t buf[32];
            if (date_format == 1) swprintf_s(buf, L"%04d年%02d月%02d日", y, m, d);
            else swprintf_s(buf, L"%04d-%02d-%02d", y, m, d);
            return buf;
        };
        std::wstring s = range_start > 0 ? fmtv(range_start) : (start_placeholder.empty() ? L"开始日期" : start_placeholder);
        s += range_separator;
        s += range_end > 0 ? fmtv(range_end) : (end_placeholder.empty() ? L"结束日期" : end_placeholder);
        return s;
    }
    if (!has_value) {
        return placeholder;
    }
    wchar_t buf[32];
    if (date_format == 1) {
        swprintf_s(buf, L"%04d\u5E74%02d\u6708%02d\u65E5", year, month, selected_day);
    } else {
        swprintf_s(buf, L"%04d-%02d-%02d", year, month, selected_day);
    }
    return buf;
}

DatePicker::Part DatePicker::header_part_at(int x, int y) const {
    if (!open) return PartNone;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    if (x < 0 || x >= pw || y < py || y >= py + ph) return PartNone;
    if (y >= py + ph - 42) {
        if (x >= 12 && x < 102) return PartToday;
        if (x >= pw - 102 && x < pw - 12) return PartClear;
        return PartNone;
    }
    if (y >= py + 42) return PartNone;
    if (x >= 12 && x < 54) return PartPrev;
    if (x >= pw - 54 && x < pw - 12) return PartNext;
    return PartNone;
}

int DatePicker::day_at(int x, int y) const {
    if (!open) return 0;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    if (x < 0 || x >= pw || y < py || y >= py + ph) return 0;
    float local_y = (float)(y - py);
    float header_h = 42.0f;
    float week_h = 28.0f;
    float grid_top = header_h + week_h;
    float footer_h = 42.0f;
    float grid_h = (float)ph - grid_top - footer_h - 12.0f;
    if (local_y < grid_top || grid_h <= 0.0f) return 0;
    float cell_w = ((float)pw - 24.0f) / 7.0f;
    float cell_h = grid_h / 6.0f;
    int col = (int)((x - 12.0f) / cell_w);
    int row = (int)((local_y - grid_top) / cell_h);
    if (col < 0 || col > 6 || row < 0 || row > 5) return 0;
    int day = row * 7 + col - first_weekday(year, month) + 1;
    int max_day = days_in_month(year, month);
    if (day < 1 || day > max_day) return 0;
    return can_select(day_value(day)) ? day : 0;
}

Element* DatePicker::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (open && day_at(lx, ly) > 0) return this;
    if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    return nullptr;
}

Element* DatePicker::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return (day_at(lx, ly) > 0 || header_part_at(lx, ly) != PartNone) ? this : nullptr;
}

void DatePicker::paint(RenderContext& ctx) {
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
    DWRITE_TEXT_ALIGNMENT align = text_align == 1 ? DWRITE_TEXT_ALIGNMENT_CENTER :
                                  text_align == 2 ? DWRITE_TEXT_ALIGNMENT_TRAILING :
                                  DWRITE_TEXT_ALIGNMENT_LEADING;
    draw_text(ctx, display_text(), style, fg,
              (float)style.pad_left, 0.0f,
              (float)bounds.w - style.pad_left - style.pad_right - 26.0f, (float)bounds.h,
              1.0f, DWRITE_FONT_WEIGHT_NORMAL, align);
    draw_text(ctx, L"📅", style, t->text_secondary,
              (float)bounds.w - style.pad_right - 26.0f, 0.0f, 26.0f, (float)bounds.h);

    ctx.rt->SetTransform(saved);
}

void DatePicker::paint_overlay(RenderContext& ctx) {
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

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    wchar_t title[32];
    if (picker_mode == 0) swprintf_s(title, L"%04d 年 %02d 月", year, month);
    else if (picker_mode == 1) swprintf_s(title, L"%04d 年", year);
    else if (picker_mode == 2) {
        int decade = (year / 10) * 10;
        swprintf_s(title, L"%d - %d", decade, decade + 9);
    }
    draw_text(ctx, L"‹", style, muted, 12.0f, (float)py, 42.0f, 42.0f,
              1.3f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, L"›", style, muted, (float)pw - 54.0f, (float)py, 42.0f, 42.0f,
              1.3f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, title, style, fg, 12.0f, (float)py, (float)pw - 24.0f, 42.0f,
              1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    // Range selection hint
    if (range_select && picker_mode == 0) {
        std::wstring hint;
        if (range_start > 0 && range_end == 0) hint = end_placeholder.empty() ? L"请点击结束日期" : end_placeholder;
        else if (range_start == 0) hint = start_placeholder.empty() ? L"请点击开始日期" : start_placeholder;
        if (!hint.empty()) {
            draw_text(ctx, hint, style, t->accent, 12.0f, (float)py + 42.0f, (float)pw - 24.0f, 20.0f, 0.8f);
        }
    }

    float grid_top = range_select ? (float)py + 76.0f : (float)py + 56.0f;
    float footer_h = 42.0f;
    float grid_h = (float)ph - (grid_top - (float)py) - footer_h;

    if (picker_mode == 0) {
        // ── date grid ──
        static const wchar_t* weeks[] = { L"日", L"一", L"二", L"三", L"四", L"五", L"六" };
        float cell_w = ((float)pw - 24.0f) / 7.0f;
        for (int i = 0; i < 7; ++i) {
            draw_text(ctx, weeks[i], style, muted, 12.0f + cell_w * (float)i, (float)py + 42.0f,
                      cell_w, 28.0f, 0.9f);
        }
        grid_top = (float)py + 70.0f;
        grid_h = (float)ph - 82.0f - footer_h;
        float cell_h = grid_h / 6.0f;
        int start = first_weekday(year, month);
        int max_day = days_in_month(year, month);
        for (int day = 1; day <= max_day; ++day) {
            int pos = start + day - 1;
            int row = pos / 7;
            int col = pos % 7;
            float x = 12.0f + cell_w * (float)col;
            float y = grid_top + cell_h * (float)row;
            bool selectable = can_select(day_value(day));
            int cur_value = day_value(day);
            bool selected = has_value && day == selected_day;
            if (multi_select && std::find(selected_dates.begin(), selected_dates.end(), cur_value) != selected_dates.end())
                selected = true;
            bool in_range = false;
            if (range_select && range_start > 0) {
                if (range_end > 0) in_range = cur_value >= range_start && cur_value <= range_end;
                else in_range = cur_value == range_start;
            }
            bool today = show_today && today_value > 0 && cur_value == today_value;
            bool hot = selectable && day == m_hover_day;
            if (today) {
                D2D1_RECT_F rr = { x + 5.0f, y + 4.0f, x + cell_w - 5.0f, y + cell_h - 4.0f };
                ctx.rt->DrawRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                    ctx.get_brush(t->accent), 1.0f);
            }
            if (in_range && !selected) {
                D2D1_RECT_F rr = { x + 2.0f, y + 5.0f, x + cell_w - 2.0f, y + cell_h - 5.0f };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                    ctx.get_brush(dark ? 0xFF2D3B55 : 0xFFE8F2FF));
            }
            if (selected || hot) {
                D2D1_RECT_F rr = { x + 4.0f, y + 3.0f, x + cell_w - 4.0f, y + cell_h - 3.0f };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                    ctx.get_brush(selected ? t->accent : hover_bg));
            }
            wchar_t buf[8];
            swprintf_s(buf, L"%d", day);
            Color text_color = selectable ? (selected ? 0xFFFFFFFF : fg) : muted;
            draw_text(ctx, buf, style, text_color, x, y, cell_w, cell_h, 0.96f);
        }
    } else if (picker_mode == 1) {
        // ── month grid (3×4) ──
        static const wchar_t* months[] = { L"1月", L"2月", L"3月", L"4月", L"5月", L"6月",
                                           L"7月", L"8月", L"9月", L"10月", L"11月", L"12月" };
        float cell_w = ((float)pw - 24.0f) / 4.0f;
        float cell_h = grid_h / 3.0f;
        for (int i = 0; i < 12; ++i) {
            int row = i / 4;
            int col = i % 4;
            float x = 12.0f + cell_w * (float)col;
            float y = grid_top + cell_h * (float)row;
            bool sel = has_value && month == (i + 1);
            bool hot = m_hover_day == (i + 1);
            if (sel || hot) {
                D2D1_RECT_F rr = { x + 4.0f, y + 3.0f, x + cell_w - 4.0f, y + cell_h - 3.0f };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                    ctx.get_brush(sel ? t->accent : hover_bg));
            }
            draw_text(ctx, months[i], style, sel ? 0xFFFFFFFF : fg, x, y, cell_w, cell_h, 1.0f);
        }
    } else if (picker_mode == 2) {
        // ── year grid (3×4 decade) ──
        int decade = (year / 10) * 10;
        float cell_w = ((float)pw - 24.0f) / 4.0f;
        float cell_h = grid_h / 3.0f;
        for (int i = 0; i < 12; ++i) {
            int row = i / 4;
            int col = i % 4;
            float x = 12.0f + cell_w * (float)col;
            float y = grid_top + cell_h * (float)row;
            int yyyy = decade + i;
            bool sel = has_value && year == yyyy;
            bool hot = m_hover_day == yyyy;
            if (sel || hot) {
                D2D1_RECT_F rr = { x + 4.0f, y + 3.0f, x + cell_w - 4.0f, y + cell_h - 3.0f };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                    ctx.get_brush(sel ? t->accent : hover_bg));
            }
            wchar_t buf[8];
            swprintf_s(buf, L"%d", yyyy);
            draw_text(ctx, buf, style, sel ? 0xFFFFFFFF : fg, x, y, cell_w, cell_h, 1.0f);
        }
    }

    float footer_y = (float)(py + ph) - footer_h;
    ctx.rt->DrawLine(D2D1::Point2F(12.0f, footer_y),
        D2D1::Point2F((float)pw - 12.0f, footer_y),
        ctx.get_brush(t->border_default), 1.0f);

    // Render shortcuts or default today/clear buttons
    if (!shortcuts.empty()) {
        float btn_w = (float)(pw - 24) / (float)shortcuts.size();
        if (btn_w > 120.0f) btn_w = 120.0f;
        float total_w = btn_w * (float)shortcuts.size();
        float start_x = ((float)pw - total_w) * 0.5f;
        for (size_t i = 0; i < shortcuts.size(); ++i) {
            float bx = start_x + btn_w * (float)i;
            D2D1_RECT_F br = { bx, footer_y + 7.0f, bx + btn_w - 4.0f, footer_y + 35.0f };
            bool hovered = (int)m_hover_part >= PartToday && (int)(m_hover_part - PartToday) == (int)i;
            Color btn_bg = hovered ? (dark ? 0xFF313244 : 0xFFEAF2FF) : bg;
            ctx.rt->FillRoundedRectangle(ROUNDED(br, 4.0f, 4.0f), ctx.get_brush(btn_bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(br, 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);
            draw_text(ctx, shortcuts[i].text, style, t->accent,
                      bx, footer_y + 7.0f, btn_w - 4.0f, 28.0f, 0.85f);
        }
    } else {
        Color today_bg = m_hover_part == PartToday ? hover_bg : bg;
        Color clear_bg = m_hover_part == PartClear ? hover_bg : bg;
        D2D1_RECT_F today_rect = { 12.0f, footer_y + 7.0f, 102.0f, footer_y + 35.0f };
        D2D1_RECT_F clear_rect = { (float)pw - 102.0f, footer_y + 7.0f, (float)pw - 12.0f, footer_y + 35.0f };
        ctx.rt->FillRoundedRectangle(ROUNDED(today_rect, 4.0f, 4.0f), ctx.get_brush(today_bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(today_rect, 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);
        ctx.rt->FillRoundedRectangle(ROUNDED(clear_rect, 4.0f, 4.0f), ctx.get_brush(clear_bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(clear_rect, 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);
        draw_text(ctx, L"📍 今天", style, can_select(today_value) ? t->accent : muted,
                  today_rect.left, today_rect.top, today_rect.right - today_rect.left, today_rect.bottom - today_rect.top, 0.88f);
        draw_text(ctx, L"清空", style, muted,
                  clear_rect.left, clear_rect.top, clear_rect.right - clear_rect.left, clear_rect.bottom - clear_rect.top, 0.88f);
    }

    ctx.rt->SetTransform(saved);
}

void DatePicker::on_mouse_move(int x, int y) {
    int day = day_at(x, y);
    Part part = day > 0 ? PartDay : header_part_at(x, y);
    if (day != m_hover_day || part != m_hover_part) {
        m_hover_day = day;
        m_hover_part = part;
        invalidate();
    }
}

void DatePicker::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_day = 0;
    m_press_day = 0;
    m_hover_part = PartNone;
    invalidate();
}

void DatePicker::on_mouse_down(int x, int y, MouseButton) {
    m_press_day = day_at(x, y);
    m_press_part = m_press_day > 0 ? PartDay : header_part_at(x, y);
    if (m_press_part == PartNone && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        m_press_part = PartMain;
    }
    m_hover_part = m_press_part;
    pressed = true;
    invalidate();
}

void DatePicker::on_mouse_up(int x, int y, MouseButton) {
    int day = day_at(x, y);
    if (m_press_part == PartMain && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        if (open && m_press_part == PartMain && header_part_at(x, y) == PartNone) {
            // Click on title area -> cycle mode
            int py = popup_y();
            int pw_val = popup_width();
            if (x >= 0 && x < pw_val && y >= py && y < py + 42) {
                picker_mode = (picker_mode + 1) % 3;
            } else {
                open = false;
            }
        } else {
            open = !open;
        }
    } else if (m_press_part == PartPrev && header_part_at(x, y) == PartPrev) {
        move_month(-1);
    } else if (m_press_part == PartNext && header_part_at(x, y) == PartNext) {
        move_month(1);
    } else if (m_press_part == PartToday && header_part_at(x, y) == PartToday) {
        select_today();
    } else if (m_press_part == PartClear && header_part_at(x, y) == PartClear) {
        clear_date();
    } else if (m_press_part == PartDay && day > 0 && day == m_press_day) {
        selected_day = day;
        has_value = true;
        if (multi_select) {
            int cur = day_value(day);
            auto it = std::find(selected_dates.begin(), selected_dates.end(), cur);
            if (it != selected_dates.end()) selected_dates.erase(it);
            else selected_dates.push_back(cur);
            std::sort(selected_dates.begin(), selected_dates.end());
        } else if (range_select) {
            int selected_value = day_value(day);
            if (range_start == 0 || (range_start > 0 && range_end > 0)) {
                range_start = selected_value;
                range_end = 0;
            } else {
                range_end = selected_value;
                if (range_start > range_end) std::swap(range_start, range_end);
                open = false;
            }
        } else {
            open = false;
        }
    }
    m_press_part = PartNone;
    m_press_day = 0;
    pressed = false;
    m_hover_day = day;
    m_hover_part = day > 0 ? PartDay : header_part_at(x, y);
    invalidate();
}

void DatePicker::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        open = !open;
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_DELETE || vk == VK_BACK) {
        clear_date();
        return;
    } else if (vk == 'T') {
        select_today();
        return;
    } else if (vk == VK_LEFT) {
        int next = add_days_simple(has_value ? value() : datepicker_value(year, month, selected_day), -1);
        if (can_select(next)) {
            int y = 0, m = 0, d = 0;
            datepicker_from_value(next, &y, &m, &d);
            set_date(y, m, d);
        }
    } else if (vk == VK_RIGHT) {
        int next = add_days_simple(has_value ? value() : datepicker_value(year, month, selected_day), 1);
        if (can_select(next)) {
            int y = 0, m = 0, d = 0;
            datepicker_from_value(next, &y, &m, &d);
            set_date(y, m, d);
        }
    } else if (vk == VK_UP) {
        int next = add_days_simple(has_value ? value() : datepicker_value(year, month, selected_day), -7);
        if (can_select(next)) {
            int y = 0, m = 0, d = 0;
            datepicker_from_value(next, &y, &m, &d);
            set_date(y, m, d);
        }
    } else if (vk == VK_DOWN) {
        int next = add_days_simple(has_value ? value() : datepicker_value(year, month, selected_day), 7);
        if (can_select(next)) {
            int y = 0, m = 0, d = 0;
            datepicker_from_value(next, &y, &m, &d);
            set_date(y, m, d);
        }
    } else if (vk == VK_HOME) {
        set_date(year, month, 1);
    } else if (vk == VK_END) {
        set_date(year, month, days_in_month(year, month));
    } else if (vk == VK_PRIOR) {
        move_month(-1);
    } else if (vk == VK_NEXT) {
        move_month(1);
    }
    invalidate();
}

void DatePicker::on_blur() {
    has_focus = false;
    open = false;
    m_hover_day = 0;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    invalidate();
}
