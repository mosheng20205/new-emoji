#include "element_calendar.h"
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
    return (h + 6) % 7; // 0 Sunday
}

static int calendar_value(int y, int m, int d) {
    return y * 10000 + m * 100 + d;
}

static void calendar_from_value(int value, int* y, int* m, int* d) {
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

void Calendar::set_date(int next_year, int next_month, int next_day) {
    if (next_year < 1900) next_year = 1900;
    if (next_year > 2099) next_year = 2099;
    if (next_month < 1) next_month = 1;
    if (next_month > 12) next_month = 12;
    int max_day = days_in_month(next_year, next_month);
    if (next_day < 1) next_day = 1;
    if (next_day > max_day) next_day = max_day;
    int next_value = calendar_value(next_year, next_month, next_day);
    if (min_value > 0 && next_value < min_value) {
        calendar_from_value(min_value, &next_year, &next_month, &next_day);
    }
    if (max_value > 0 && next_value > max_value) {
        calendar_from_value(max_value, &next_year, &next_month, &next_day);
    }
    year = next_year;
    month = next_month;
    selected_day = next_day;
    invalidate();
}

void Calendar::set_range(int min_yyyymmdd, int max_yyyymmdd) {
    min_value = min_yyyymmdd > 0 ? min_yyyymmdd : 0;
    max_value = max_yyyymmdd > 0 ? max_yyyymmdd : 0;
    if (min_value > 0 && max_value > 0 && min_value > max_value) {
        std::swap(min_value, max_value);
    }
    set_date(year, month, selected_day);
}

void Calendar::set_options(int today_yyyymmdd, bool next_show_today) {
    today_value = today_yyyymmdd;
    show_today = next_show_today;
    invalidate();
}

void Calendar::set_selection_range(int start_yyyymmdd, int end_yyyymmdd, bool enabled) {
    range_select = enabled;
    range_start = can_select(start_yyyymmdd) ? start_yyyymmdd : 0;
    range_end = can_select(end_yyyymmdd) ? end_yyyymmdd : 0;
    if (range_start > 0 && range_end > 0 && range_start > range_end) {
        std::swap(range_start, range_end);
    }
    invalidate();
}

void Calendar::get_selection_range(int& start_yyyymmdd, int& end_yyyymmdd, bool& enabled) const {
    start_yyyymmdd = range_start;
    end_yyyymmdd = range_end;
    enabled = range_select;
}

void Calendar::move_month(int delta) {
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
    set_date(next_year, next_month, selected_day);
}

static int add_days_simple(int value, int delta) {
    int y = 0, m = 0, d = 0;
    calendar_from_value(value, &y, &m, &d);
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
    return calendar_value(y, m, d);
}

int Calendar::value() const {
    return year * 10000 + month * 100 + selected_day;
}

bool Calendar::can_select(int yyyymmdd) const {
    if (yyyymmdd <= 0) return false;
    if (min_value > 0 && yyyymmdd < min_value) return false;
    if (max_value > 0 && yyyymmdd > max_value) return false;
    return true;
}

int Calendar::day_value(int day) const {
    return calendar_value(year, month, day);
}

Calendar::Part Calendar::header_part_at(int x, int y) const {
    float header_h = (std::max)(style.font_size * 2.8f, 38.0f);
    if (y < style.pad_top || y >= style.pad_top + header_h) return PartNone;
    float left = (float)style.pad_left;
    float right = (float)bounds.w - style.pad_right;
    float btn_w = (std::max)(header_h, 36.0f);
    if (x >= left && x < left + btn_w) return PartPrev;
    if (x >= right - btn_w && x < right) return PartNext;
    return PartNone;
}

int Calendar::day_at(int x, int y) const {
    float header_h = (std::max)(style.font_size * 2.8f, 38.0f);
    float week_h = (std::max)(style.font_size * 1.9f, 26.0f);
    float grid_top = (float)style.pad_top + header_h + week_h;
    float grid_h = (float)bounds.h - grid_top - style.pad_bottom;
    if (grid_h <= 0.0f || x < style.pad_left || x >= bounds.w - style.pad_right || y < grid_top) return 0;
    float cell_w = ((float)bounds.w - style.pad_left - style.pad_right) / 7.0f;
    float cell_h = grid_h / 6.0f;
    int col = (int)((x - style.pad_left) / cell_w);
    int row = (int)((y - grid_top) / cell_h);
    if (col < 0 || col > 6 || row < 0 || row > 5) return 0;
    int day = row * 7 + col - first_weekday(year, month) + 1;
    int max_day = days_in_month(year, month);
    if (day < 1 || day > max_day) return 0;
    return can_select(day_value(day)) ? day : 0;
}

void Calendar::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFEAF2FF;
    Color accent = t->accent;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float header_h = (std::max)(style.font_size * 2.8f, 38.0f);
    float week_h = (std::max)(style.font_size * 1.9f, 26.0f);
    wchar_t title[32];
    swprintf_s(title, L"%04d-%02d", year, month);
    draw_text(ctx, L"‹", style, muted,
              (float)style.pad_left, (float)style.pad_top,
              header_h, header_h, 1.35f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, L"›", style, muted,
              (float)bounds.w - style.pad_right - header_h, (float)style.pad_top,
              header_h, header_h, 1.35f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, title, style, fg,
              (float)style.pad_left, (float)style.pad_top,
              (float)bounds.w - style.pad_left - style.pad_right, header_h,
              1.08f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    static const wchar_t* weeks[] = { L"日", L"一", L"二", L"三", L"四", L"五", L"六" };
    float left = (float)style.pad_left;
    float grid_w = (float)bounds.w - style.pad_left - style.pad_right;
    float cell_w = grid_w / 7.0f;
    float week_top = (float)style.pad_top + header_h;
    for (int i = 0; i < 7; ++i) {
        draw_text(ctx, weeks[i], style, muted, left + cell_w * (float)i, week_top, cell_w, week_h, 0.9f);
    }

    float grid_top = week_top + week_h;
    float grid_h = (float)bounds.h - grid_top - style.pad_bottom;
    if (grid_h < 1.0f) grid_h = 1.0f;
    float cell_h = grid_h / 6.0f;
    int start = first_weekday(year, month);
    int max_day = days_in_month(year, month);
    for (int day = 1; day <= max_day; ++day) {
        int pos = start + day - 1;
        int row = pos / 7;
        int col = pos % 7;
        float x = left + cell_w * (float)col;
        float y = grid_top + cell_h * (float)row;
        bool selected = day == selected_day;
        bool in_range = false;
        int cur_value = day_value(day);
        if (range_select && range_start > 0) {
            if (range_end > 0) in_range = cur_value >= range_start && cur_value <= range_end;
            else in_range = cur_value == range_start;
        }
        bool selectable = can_select(day_value(day));
        bool today = show_today && today_value > 0 && day_value(day) == today_value;
        bool hot = selectable && day == m_hover_day;
        if (today) {
            D2D1_RECT_F rr = { x + 5.0f, y + 4.0f, x + cell_w - 5.0f, y + cell_h - 4.0f };
            ctx.rt->DrawRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                ctx.get_brush(accent), 1.0f);
        }
        if (in_range && !selected) {
            D2D1_RECT_F rr = { x + 2.0f, y + 5.0f, x + cell_w - 2.0f, y + cell_h - 5.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                ctx.get_brush(dark ? 0xFF2D3B55 : 0xFFE8F2FF));
        }
        if (selected || hot) {
            D2D1_RECT_F rr = { x + 4.0f, y + 3.0f, x + cell_w - 4.0f, y + cell_h - 3.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f),
                ctx.get_brush(selected ? accent : hover_bg));
        }
        wchar_t buf[8];
        swprintf_s(buf, L"%d", day);
        Color text_color = selectable ? (selected ? 0xFFFFFFFF : fg) : muted;
        draw_text(ctx, buf, style, text_color, x, y, cell_w, cell_h, 0.96f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Calendar::on_mouse_move(int x, int y) {
    int day = day_at(x, y);
    if (day != m_hover_day) {
        m_hover_day = day;
        invalidate();
    }
}

void Calendar::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_day = 0;
    m_press_day = 0;
    invalidate();
}

void Calendar::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_part = header_part_at(x, y);
    m_press_day = day_at(x, y);
    if (m_press_day > 0) m_press_part = PartDay;
    invalidate();
}

void Calendar::on_mouse_up(int x, int y, MouseButton) {
    int day = day_at(x, y);
    Part header_part = header_part_at(x, y);
    if (m_press_part == PartPrev && header_part == PartPrev) {
        move_month(-1);
    } else if (m_press_part == PartNext && header_part == PartNext) {
        move_month(1);
    } else if (m_press_part == PartDay && day > 0 && day == m_press_day) {
        selected_day = day;
        int selected_value = day_value(day);
        if (range_select) {
            if (range_start == 0 || (range_start > 0 && range_end > 0)) {
                range_start = selected_value;
                range_end = 0;
            } else {
                range_end = selected_value;
                if (range_start > range_end) std::swap(range_start, range_end);
            }
        }
    }
    pressed = false;
    m_press_day = 0;
    m_press_part = PartNone;
    m_hover_day = day;
    invalidate();
}

void Calendar::on_key_down(int vk, int) {
    int current = value();
    int next = current;
    if (vk == VK_LEFT) next = add_days_simple(current, -1);
    else if (vk == VK_RIGHT) next = add_days_simple(current, 1);
    else if (vk == VK_UP) next = add_days_simple(current, -7);
    else if (vk == VK_DOWN) next = add_days_simple(current, 7);
    else if (vk == VK_PRIOR) { move_month(-1); return; }
    else if (vk == VK_NEXT) { move_month(1); return; }
    else if (vk == VK_HOME) next = calendar_value(year, month, 1);
    else if (vk == VK_END) next = calendar_value(year, month, days_in_month(year, month));
    else return;
    if (!can_select(next)) return;
    int y = 0, m = 0, d = 0;
    calendar_from_value(next, &y, &m, &d);
    set_date(y, m, d);
}
