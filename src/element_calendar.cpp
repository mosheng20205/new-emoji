#include "element_calendar.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cstdlib>
#include <cwchar>
#include <cwctype>
#include <map>
#include <sstream>

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

static int weekday_from_value(int value) {
    int y = 0, m = 0, d = 0;
    calendar_from_value(value, &y, &m, &d);
    int first = first_weekday(y, m);
    return (first + d - 1) % 7;
}

static std::wstring lower_text(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(),
        [](wchar_t ch) { return (wchar_t)std::towlower(ch); });
    return value;
}

static std::wstring trim_text(const std::wstring& value) {
    size_t first = value.find_first_not_of(L" \t\r\n");
    if (first == std::wstring::npos) return L"";
    size_t last = value.find_last_not_of(L" \t\r\n");
    return value.substr(first, last - first + 1);
}

static bool bool_text(const std::wstring& value, bool fallback = false) {
    std::wstring v = lower_text(trim_text(value));
    if (v.empty()) return fallback;
    if (v == L"1" || v == L"true" || v == L"yes" || v == L"on") return true;
    if (v == L"0" || v == L"false" || v == L"no" || v == L"off") return false;
    return _wtoi(v.c_str()) != 0;
}

static int int_text(const std::wstring& value, int fallback = 0) {
    std::wstring v = trim_text(value);
    if (v.empty()) return fallback;
    return _wtoi(v.c_str());
}

static Color color_text(const std::wstring& value, Color fallback = 0) {
    std::wstring v = trim_text(value);
    if (v.empty()) return fallback;
    int base = 10;
    if (v[0] == L'#') {
        v = v.substr(1);
        base = 16;
    } else if (v.size() > 2 && v[0] == L'0' && (v[1] == L'x' || v[1] == L'X')) {
        v = v.substr(2);
        base = 16;
    }
    wchar_t* end = nullptr;
    unsigned long parsed = std::wcstoul(v.c_str(), &end, base);
    if (!end || *end != L'\0') return fallback;
    Color color = (Color)parsed;
    if (base == 16 && v.size() <= 6) color |= 0xFF000000;
    return color;
}

static std::vector<std::wstring> split_escaped(const std::wstring& s, wchar_t sep) {
    std::vector<std::wstring> out;
    std::wstring cur;
    bool esc = false;
    for (wchar_t ch : s) {
        if (esc) {
            if (ch == L'n') cur.push_back(L'\n');
            else if (ch == L't') cur.push_back(L'\t');
            else cur.push_back(ch);
            esc = false;
        } else if (ch == L'\\') {
            esc = true;
        } else if (ch == sep) {
            out.push_back(cur);
            cur.clear();
        } else {
            cur.push_back(ch);
        }
    }
    out.push_back(cur);
    return out;
}

static std::map<std::wstring, std::wstring> parse_kv(const std::wstring& line) {
    std::map<std::wstring, std::wstring> kv;
    int unnamed = 0;
    for (const auto& field : split_escaped(line, L'\t')) {
        if (field.empty()) continue;
        size_t pos = field.find(L'=');
        if (pos == std::wstring::npos) kv[L"$" + std::to_wstring(unnamed++)] = field;
        else kv[lower_text(field.substr(0, pos))] = field.substr(pos + 1);
    }
    return kv;
}

static std::wstring kv_get(const std::map<std::wstring, std::wstring>& kv,
                           const std::wstring& key,
                           const std::wstring& fallback = L"") {
    auto it = kv.find(lower_text(key));
    return it == kv.end() ? fallback : it->second;
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
    D2D1_RECT_F clip = { x, y, x + w, y + h };
    ctx.push_clip(clip);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    ctx.pop_clip();
    layout->Release();
}

static std::wstring date_label(int value, int mode) {
    int y = 0, m = 0, d = 0;
    calendar_from_value(value, &y, &m, &d);
    wchar_t buf[32];
    if (mode == 1) swprintf_s(buf, L"%02d-%02d", m, d);
    else if (mode == 2) swprintf_s(buf, L"%04d-%02d-%02d", y, m, d);
    else swprintf_s(buf, L"%d", d);
    return buf;
}

static std::wstring full_date_label(int value) {
    int y = 0, m = 0, d = 0;
    calendar_from_value(value, &y, &m, &d);
    wchar_t buf[32];
    swprintf_s(buf, L"%04d-%02d-%02d", y, m, d);
    return buf;
}

static float fitted_text_scale(const std::wstring& text, const ElementStyle& style,
                               float available_width, float preferred_scale,
                               float min_scale = 0.58f) {
    if (text.empty() || available_width <= 0.0f || style.font_size <= 0.0f) return preferred_scale;
    float estimate = (float)text.size() * style.font_size * 0.58f;
    if (estimate <= 1.0f) return preferred_scale;
    float scale = (std::min)(preferred_scale, available_width / estimate);
    return (std::max)(min_scale, scale);
}

bool Calendar::display_range_enabled() const {
    return display_start > 0 && display_end > 0;
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

void Calendar::set_date_value(int yyyymmdd) {
    int y = 0, m = 0, d = 0;
    calendar_from_value(yyyymmdd, &y, &m, &d);
    set_date(y, m, d);
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

void Calendar::set_display_range(int start_yyyymmdd, int end_yyyymmdd) {
    if (start_yyyymmdd <= 0 || end_yyyymmdd <= 0) {
        display_start = 0;
        display_end = 0;
        invalidate();
        return;
    }
    display_start = start_yyyymmdd > 0 ? start_yyyymmdd : 0;
    display_end = end_yyyymmdd > 0 ? end_yyyymmdd : 0;
    if (display_start > 0 && display_end > 0 && display_start > display_end) {
        std::swap(display_start, display_end);
    }
    if (display_range_enabled() && value() < display_start) set_date_value(display_start);
    if (display_range_enabled() && value() > display_end) set_date_value(display_end);
    invalidate();
}

void Calendar::get_display_range(int& start_yyyymmdd, int& end_yyyymmdd) const {
    start_yyyymmdd = display_start;
    end_yyyymmdd = display_end;
}

void Calendar::set_cell_items(const std::wstring& spec) {
    cell_items_spec = spec;
    cell_items.clear();
    for (const auto& raw_line : split_escaped(spec, L'\n')) {
        std::wstring line = trim_text(raw_line);
        if (line.empty()) continue;
        auto kv = parse_kv(line);
        CalendarCellItem item;
        item.date = int_text(kv_get(kv, L"date", kv_get(kv, L"$0")), 0);
        if (item.date <= 0) continue;
        item.label = kv_get(kv, L"label");
        item.extra = kv_get(kv, L"extra");
        item.emoji = kv_get(kv, L"emoji");
        item.badge = kv_get(kv, L"badge");
        item.bg = color_text(kv_get(kv, L"bg"), 0);
        item.fg = color_text(kv_get(kv, L"fg"), 0);
        item.border = color_text(kv_get(kv, L"border"), 0);
        item.badge_bg = color_text(kv_get(kv, L"badge_bg"), 0);
        item.badge_fg = color_text(kv_get(kv, L"badge_fg"), 0);
        item.font_flags = int_text(kv_get(kv, L"font_flags"), 0);
        item.disabled = bool_text(kv_get(kv, L"disabled"), false);
        cell_items[item.date] = item;
    }
    invalidate();
}

void Calendar::clear_cell_items() {
    cell_items_spec.clear();
    cell_items.clear();
    invalidate();
}

void Calendar::set_visual_options(bool next_show_header, bool next_show_week_header,
                                  int next_label_mode, bool next_show_adjacent_days,
                                  float next_cell_radius) {
    show_header = next_show_header;
    show_week_header = next_show_week_header;
    label_mode = (std::max)(0, (std::min)(3, next_label_mode));
    show_adjacent_days = next_show_adjacent_days;
    cell_radius = (std::max)(0.0f, (std::min)(18.0f, next_cell_radius));
    invalidate();
}

void Calendar::get_visual_options(int& out_show_header, int& out_show_week_header,
                                  int& out_label_mode, int& out_show_adjacent_days,
                                  float& out_cell_radius) const {
    out_show_header = show_header ? 1 : 0;
    out_show_week_header = show_week_header ? 1 : 0;
    out_label_mode = label_mode;
    out_show_adjacent_days = show_adjacent_days ? 1 : 0;
    out_cell_radius = cell_radius;
}

void Calendar::set_state_colors(Color next_selected_bg, Color next_selected_fg,
                                Color next_range_bg, Color next_today_border,
                                Color next_hover_bg, Color next_disabled_fg,
                                Color next_adjacent_fg) {
    selected_bg = next_selected_bg;
    selected_fg = next_selected_fg;
    range_bg = next_range_bg;
    today_border = next_today_border;
    hover_bg = next_hover_bg;
    disabled_fg = next_disabled_fg;
    adjacent_fg = next_adjacent_fg;
    invalidate();
}

void Calendar::get_state_colors(Color& out_selected_bg, Color& out_selected_fg,
                                Color& out_range_bg, Color& out_today_border,
                                Color& out_hover_bg, Color& out_disabled_fg,
                                Color& out_adjacent_fg) const {
    out_selected_bg = selected_bg;
    out_selected_fg = selected_fg;
    out_range_bg = range_bg;
    out_today_border = today_border;
    out_hover_bg = hover_bg;
    out_disabled_fg = disabled_fg;
    out_adjacent_fg = adjacent_fg;
}

void Calendar::set_selected_marker(const std::wstring& marker) {
    selected_marker = marker;
    invalidate();
}

void Calendar::move_month(int delta) {
    if (display_range_enabled()) return;
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

int Calendar::value() const {
    return year * 10000 + month * 100 + selected_day;
}

bool Calendar::can_select(int yyyymmdd) const {
    if (yyyymmdd <= 0) return false;
    if (min_value > 0 && yyyymmdd < min_value) return false;
    if (max_value > 0 && yyyymmdd > max_value) return false;
    return true;
}

bool Calendar::can_interact(int yyyymmdd) const {
    if (!can_select(yyyymmdd)) return false;
    if (display_range_enabled() && (yyyymmdd < display_start || yyyymmdd > display_end)) return false;
    auto it = cell_items.find(yyyymmdd);
    if (it != cell_items.end() && it->second.disabled) return false;
    return true;
}

int Calendar::day_value(int day) const {
    return calendar_value(year, month, day);
}

std::vector<CalendarVisibleCell> Calendar::visible_cells() const {
    std::vector<CalendarVisibleCell> cells;
    cells.reserve(42);
    int start_value = 0;
    if (display_range_enabled()) {
        start_value = display_start;
    } else {
        int first = calendar_value(year, month, 1);
        start_value = add_days_simple(first, -first_weekday(year, month));
    }

    for (int i = 0; i < 42; ++i) {
        int cur = add_days_simple(start_value, i);
        int cy = 0, cm = 0, cd = 0;
        calendar_from_value(cur, &cy, &cm, &cd);
        CalendarVisibleCell cell;
        cell.date = cur;
        cell.year = cy;
        cell.month = cm;
        cell.day = cd;
        cell.current_month = display_range_enabled() ? true : (cy == year && cm == month);
        cell.display_range = !display_range_enabled() || (cur >= display_start && cur <= display_end);
        cell.selectable = can_interact(cur);
        cell.selected = (cur == value());
        cell.today = show_today && today_value > 0 && cur == today_value;
        cell.hot = cell.selectable && cur == m_hover_value;
        if (range_select && range_start > 0) {
            if (range_end > 0) cell.in_selection_range = cur >= range_start && cur <= range_end;
            else cell.in_selection_range = cur == range_start;
        }
        auto custom = cell_items.find(cur);
        if (custom != cell_items.end()) {
            cell.custom = &custom->second;
            if (custom->second.disabled) cell.selectable = false;
        }
        cells.push_back(cell);
    }
    return cells;
}

Calendar::Part Calendar::header_part_at(int x, int y) const {
    if (!show_header || display_range_enabled()) return PartNone;
    float header_h = (std::max)(style.font_size * 2.8f, 38.0f);
    if (y < style.pad_top || y >= style.pad_top + header_h) return PartNone;
    float left = (float)style.pad_left;
    float right = (float)bounds.w - style.pad_right;
    float btn_w = (std::max)(header_h, 36.0f);
    if (x >= left && x < left + btn_w) return PartPrev;
    if (x >= right - btn_w && x < right) return PartNext;
    return PartNone;
}

int Calendar::date_at(int x, int y) const {
    float header_h = show_header ? (std::max)(style.font_size * 2.8f, 38.0f) : 0.0f;
    float week_h = show_week_header ? (std::max)(style.font_size * 1.9f, 26.0f) : 0.0f;
    float grid_top = (float)style.pad_top + header_h + week_h;
    float grid_h = (float)bounds.h - grid_top - style.pad_bottom;
    if (grid_h <= 0.0f || x < style.pad_left || x >= bounds.w - style.pad_right || y < grid_top) return 0;
    float cell_w = ((float)bounds.w - style.pad_left - style.pad_right) / 7.0f;
    float cell_h = grid_h / 6.0f;
    int col = (int)((x - style.pad_left) / cell_w);
    int row = (int)((y - grid_top) / cell_h);
    if (col < 0 || col > 6 || row < 0 || row > 5) return 0;
    int index = row * 7 + col;
    auto cells = visible_cells();
    if (index < 0 || index >= (int)cells.size()) return 0;
    const auto& cell = cells[index];
    if (!cell.display_range) return 0;
    if (!show_adjacent_days && !cell.current_month) return 0;
    return cell.selectable ? cell.date : 0;
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
    Color hot_bg = hover_bg ? hover_bg : (dark ? 0xFF313244 : 0xFFEAF2FF);
    Color accent = t->accent;
    Color selected_color = selected_bg ? selected_bg : accent;
    Color selected_text = selected_fg ? selected_fg : 0xFFFFFFFF;
    Color range_color = range_bg ? range_bg : (dark ? 0xFF2D3B55 : 0xFFE8F2FF);
    Color today_color = today_border ? today_border : accent;
    Color disabled_color = disabled_fg ? disabled_fg : muted;
    Color adjacent_color = adjacent_fg ? adjacent_fg : (dark ? 0xFF747B9B : 0xFF9AA6BA);

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float header_h = show_header ? (std::max)(style.font_size * 2.8f, 38.0f) : 0.0f;
    float week_h = show_week_header ? (std::max)(style.font_size * 1.9f, 26.0f) : 0.0f;
    if (show_header) {
        std::wstring title;
        if (display_range_enabled()) {
            title = full_date_label(display_start) + L" \u81f3 " + full_date_label(display_end);
        } else {
            wchar_t title_buf[32];
            swprintf_s(title_buf, L"%04d-%02d", year, month);
            title = title_buf;
            draw_text(ctx, L"\u2039", style, muted,
                      (float)style.pad_left, (float)style.pad_top,
                      header_h, header_h, 1.35f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
            draw_text(ctx, L"\u203A", style, muted,
                      (float)bounds.w - style.pad_right - header_h, (float)style.pad_top,
                      header_h, header_h, 1.35f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
        }
        draw_text(ctx, title, style, fg,
                  (float)style.pad_left, (float)style.pad_top,
                  (float)bounds.w - style.pad_left - style.pad_right, header_h,
                  1.08f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    }

    static const wchar_t* weeks[] = {
        L"\u65E5", L"\u4E00", L"\u4E8C", L"\u4E09", L"\u56DB", L"\u4E94", L"\u516D"
    };
    float left = (float)style.pad_left;
    float grid_w = (float)bounds.w - style.pad_left - style.pad_right;
    float cell_w = grid_w / 7.0f;
    float week_top = (float)style.pad_top + header_h;
    int week_offset = display_range_enabled() ? weekday_from_value(display_start) : 0;
    if (show_week_header) {
        for (int i = 0; i < 7; ++i) {
            draw_text(ctx, weeks[(week_offset + i) % 7], style, muted,
                      left + cell_w * (float)i, week_top, cell_w, week_h, 0.9f);
        }
    }

    float grid_top = week_top + week_h;
    float grid_h = (float)bounds.h - grid_top - style.pad_bottom;
    if (grid_h < 1.0f) grid_h = 1.0f;
    float cell_h = grid_h / 6.0f;
    auto cells = visible_cells();
    for (int i = 0; i < (int)cells.size(); ++i) {
        const auto& cell = cells[i];
        if (!cell.display_range) continue;
        if (!show_adjacent_days && !cell.current_month) continue;

        int row = i / 7;
        int col = i % 7;
        float x = left + cell_w * (float)col;
        float y = grid_top + cell_h * (float)row;
        float inset_x = (std::min)(6.0f, cell_w * 0.12f);
        float inset_y = (std::min)(5.0f, cell_h * 0.14f);
        D2D1_RECT_F rr = { x + inset_x, y + inset_y, x + cell_w - inset_x, y + cell_h - inset_y };
        float cr = cell_radius > 0.0f ? cell_radius : 4.0f;

        if (cell.in_selection_range && !cell.selected) {
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, cr, cr), ctx.get_brush(range_color));
        }
        if (cell.today) {
            ctx.rt->DrawRoundedRectangle(ROUNDED(rr, cr, cr), ctx.get_brush(today_color), 1.0f);
        }
        if (cell.selected || cell.hot) {
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, cr, cr),
                ctx.get_brush(cell.selected ? selected_color : hot_bg));
        }
        if (cell.custom && (cell.custom->bg || cell.custom->disabled)) {
            Color cell_bg = cell.custom->bg ? cell.custom->bg : (dark ? 0xFF303442 : 0xFFF5F7FA);
            ctx.rt->FillRoundedRectangle(ROUNDED(rr, cr, cr), ctx.get_brush(cell_bg));
        }
        if (cell.custom && cell.custom->border) {
            ctx.rt->DrawRoundedRectangle(ROUNDED(rr, cr, cr), ctx.get_brush(cell.custom->border), 1.0f);
        }

        Color text_color = fg;
        if (!cell.selectable) text_color = disabled_color;
        else if (!cell.current_month && !display_range_enabled()) text_color = adjacent_color;
        if (cell.selected) text_color = selected_text;
        if (cell.custom && cell.custom->fg) text_color = cell.custom->fg;

        std::wstring label;
        if (label_mode == 3 && cell.custom && !cell.custom->label.empty()) label = cell.custom->label;
        else label = date_label(cell.date, label_mode);
        DWRITE_FONT_WEIGHT weight = (cell.custom && (cell.custom->font_flags & 1))
            ? DWRITE_FONT_WEIGHT_SEMI_BOLD : DWRITE_FONT_WEIGHT_NORMAL;

        bool has_extra = cell.custom && !cell.custom->extra.empty();
        bool has_emoji = cell.custom && !cell.custom->emoji.empty();
        bool has_badge = cell.custom && !cell.custom->badge.empty();
        bool rich_cell = has_extra || has_emoji || has_badge;
        bool compact_rich = rich_cell && (cell_w < 58.0f || cell_h < 54.0f);
        int adornment_count = (has_extra ? 1 : 0) + (has_emoji ? 1 : 0) + (has_badge ? 1 : 0);
        bool crowded_rich = compact_rich && (adornment_count >= 2 || (has_extra && cell.custom->extra.size() > 2));

        if (compact_rich && label.size() > 2) {
            label = date_label(cell.date, 0);
        }

        float content_left = rr.left + 2.0f;
        float content_top = rr.top + 1.0f;
        float content_w = (std::max)(1.0f, rr.right - rr.left - 4.0f);
        float content_h = (std::max)(1.0f, rr.bottom - rr.top - 2.0f);
        float label_h = rich_cell ? (compact_rich ? content_h * 0.58f : content_h * 0.44f) : content_h;
        float label_scale = fitted_text_scale(label, style, content_w, compact_rich ? 0.86f : 0.96f,
                                              compact_rich ? 0.48f : 0.58f);
        if (label_mode == 2) label_scale = (std::min)(label_scale, 0.68f);
        draw_text(ctx, label, style, text_color, content_left, content_top,
                  content_w, label_h, label_scale, weight);

        bool draw_marker = cell.selected && !selected_marker.empty();
        bool draw_emoji = has_emoji && (!crowded_rich || !draw_marker);
        bool draw_extra = has_extra && (!crowded_rich || (!has_emoji && !has_badge && cell_h >= 38.0f));

        if (draw_marker) {
            float mark_box = compact_rich ? 14.0f : 18.0f;
            float mark_scale = (std::min)(compact_rich ? 0.64f : 0.78f,
                fitted_text_scale(selected_marker, style, mark_box, compact_rich ? 0.64f : 0.78f, 0.46f));
            draw_text(ctx, selected_marker, style, text_color,
                      rr.right - mark_box - 2.0f, rr.top + 2.0f, mark_box, mark_box, mark_scale,
                      DWRITE_FONT_WEIGHT_SEMI_BOLD);
        }
        if (draw_emoji) {
            float emoji_box = compact_rich ? 14.0f : 18.0f;
            float emoji_scale = (std::min)(compact_rich ? 0.62f : 0.76f,
                fitted_text_scale(cell.custom->emoji, style, emoji_box, compact_rich ? 0.62f : 0.76f, 0.46f));
            draw_text(ctx, cell.custom->emoji, style, text_color,
                      rr.left + 2.0f, rr.top + 2.0f, emoji_box, emoji_box, emoji_scale,
                      DWRITE_FONT_WEIGHT_NORMAL);
        }
        if (draw_extra) {
            float extra_scale = fitted_text_scale(cell.custom->extra, style, content_w, compact_rich ? 0.56f : 0.72f,
                                                  compact_rich ? 0.44f : 0.52f);
            draw_text(ctx, cell.custom->extra, style,
                      cell.custom->fg ? cell.custom->fg : muted,
                      content_left, rr.top + content_h * 0.43f,
                      content_w, content_h * (compact_rich ? 0.34f : 0.32f), extra_scale,
                      DWRITE_FONT_WEIGHT_NORMAL);
        }
        if (has_badge) {
            float bw = (std::min)(content_w, (float)(cell.custom->badge.size() * (compact_rich ? 10 : 14) + 16));
            float bh = (std::min)(compact_rich ? 16.0f : 22.0f, content_h * (compact_rich ? 0.34f : 0.30f));
            D2D1_RECT_F br = { rr.left + (rr.right - rr.left - bw) * 0.5f, rr.bottom - bh - 2.0f,
                               rr.left + (rr.right - rr.left + bw) * 0.5f, rr.bottom - 2.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(br, bh * 0.45f, bh * 0.45f),
                ctx.get_brush(cell.custom->badge_bg ? cell.custom->badge_bg : selected_color));
            draw_text(ctx, cell.custom->badge, style,
                      cell.custom->badge_fg ? cell.custom->badge_fg : 0xFFFFFFFF,
                      br.left, br.top, br.right - br.left, br.bottom - br.top,
                      compact_rich ? 0.54f : 0.68f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Calendar::on_mouse_move(int x, int y) {
    int date = date_at(x, y);
    if (date != m_hover_value) {
        m_hover_value = date;
        invalidate();
    }
}

void Calendar::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_value = 0;
    m_press_value = 0;
    invalidate();
}

void Calendar::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_part = header_part_at(x, y);
    m_press_value = date_at(x, y);
    if (m_press_value > 0) m_press_part = PartDay;
    invalidate();
}

void Calendar::on_mouse_up(int x, int y, MouseButton) {
    int date = date_at(x, y);
    Part header_part = header_part_at(x, y);
    bool changed = false;
    if (m_press_part == PartPrev && header_part == PartPrev) {
        move_month(-1);
    } else if (m_press_part == PartNext && header_part == PartNext) {
        move_month(1);
    } else if (m_press_part == PartDay && date > 0 && date == m_press_value) {
        int old_value = value();
        set_date_value(date);
        changed = old_value != value();
        if (range_select) {
            if (range_start == 0 || (range_start > 0 && range_end > 0)) {
                range_start = date;
                range_end = 0;
            } else {
                range_end = date;
                if (range_start > range_end) std::swap(range_start, range_end);
            }
            changed = true;
        }
    }
    pressed = false;
    m_press_value = 0;
    m_press_part = PartNone;
    m_hover_value = date;
    invalidate();
    if (changed) invoke_change();
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
    else if (vk == VK_HOME) next = display_range_enabled() ? display_start : calendar_value(year, month, 1);
    else if (vk == VK_END) next = display_range_enabled() ? display_end : calendar_value(year, month, days_in_month(year, month));
    else return;
    if (!can_interact(next)) return;
    set_date_value(next);
    invoke_change();
}

void Calendar::invoke_change() {
    if (change_cb) change_cb(id, value(), range_start, range_end);
}
