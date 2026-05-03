#include "element_daterangepicker.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwchar>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static bool leap_year(int y) { return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0); }
static int days_in_month(int y, int m) {
    static const int days[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (m == 2) return leap_year(y) ? 29 : 28;
    if (m < 1 || m > 12) return 30; return days[m - 1];
}
static int first_weekday(int y, int m) {
    if (m < 3) { m += 12; --y; }
    return ((1 + (13 * (m + 1)) / 5 + (y % 100) + (y % 100) / 4 + (y / 100) / 4 + 5 * (y / 100)) % 7 + 6) % 7;
}
static int date_value(int y, int m, int d) { return y * 10000 + m * 100 + d; }
static void from_value(int v, int* y, int* m, int* d) {
    if (y) *y = v / 10000;
    if (m) *m = (v / 100) % 100;
    if (d) *d = v % 100;
    if (y && *y < 1900) *y = 1900;
    if (y && *y > 2099) *y = 2099;
    if (m && *m < 1) *m = 1;
    if (m && *m > 12) *m = 12;
    if (d && y && m) { int maxd = days_in_month(*y, *m); if (*d < 1) *d = 1; if (*d > maxd) *d = maxd; }
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f, DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0 || h <= 0) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(align); layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout, ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

int DateRangePicker::popup_width() const { return (std::max)(bounds.w, 600); }
int DateRangePicker::popup_height() const { return 320; }
int DateRangePicker::panel_width() const { return (popup_width() - 36) / 2; }

int DateRangePicker::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) return -ph - 4;
    return bounds.h + 4;
}

void DateRangePicker::set_value(int start, int end) {
    if (can_select(start)) range_start = start; else range_start = 0;
    if (can_select(end)) range_end = end; else range_end = 0;
    if (range_start > 0 && range_end > 0 && range_start > range_end) std::swap(range_start, range_end);
    if (range_start > 0) { from_value(range_start, &year, &month, nullptr); }
    open = false; invalidate();
}

void DateRangePicker::set_range(int min_yyyymmdd, int max_yyyymmdd) {
    min_value = min_yyyymmdd > 0 ? min_yyyymmdd : 0;
    max_value = max_yyyymmdd > 0 ? max_yyyymmdd : 0;
    if (min_value > 0 && max_value > 0 && min_value > max_value) std::swap(min_value, max_value);
    if (!can_select(range_start)) range_start = 0;
    if (!can_select(range_end)) range_end = 0;
    invalidate();
}

void DateRangePicker::set_options(int today, int fmt) { today_value = today; date_format = fmt; invalidate(); }
void DateRangePicker::set_open(bool next_open) { open = next_open; invalidate(); }

void DateRangePicker::clear_value() {
    range_start = 0; range_end = 0; open = false; invalidate();
}

bool DateRangePicker::can_select(int v) const {
    if (v <= 0) return false;
    if (min_value > 0 && v < min_value) return false;
    if (max_value > 0 && v > max_value) return false;
    if (disabled_date_cb && disabled_date_cb(id, v) != 0) return false;
    return true;
}

void DateRangePicker::move_month(int delta) {
    month += delta;
    while (month < 1) { month += 12; --year; }
    while (month > 12) { month -= 12; ++year; }
    invalidate();
}

std::wstring DateRangePicker::fmt_date(int val) const {
    int y, m, d; from_value(val, &y, &m, &d);
    wchar_t buf[32];
    if (date_format == 1) swprintf_s(buf, L"%04d年%02d月%02d日", y, m, d);
    else swprintf_s(buf, L"%04d-%02d-%02d", y, m, d);
    return buf;
}

std::wstring DateRangePicker::display_text() const {
    if (range_start > 0 && range_end > 0)
        return fmt_date(range_start) + range_separator + fmt_date(range_end);
    if (range_start > 0)
        return fmt_date(range_start) + range_separator + end_placeholder;
    return start_placeholder;
}

// ── Paint ────────────────────────────────────────────────────────────

void DateRangePicker::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0 || !ctx.rt) return;
    D2D1_MATRIX_3X2_F saved; ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = open || has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float r = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, r, r), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), r, r),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);
    DWRITE_TEXT_ALIGNMENT al = text_align == 1 ? DWRITE_TEXT_ALIGNMENT_CENTER :
                                text_align == 2 ? DWRITE_TEXT_ALIGNMENT_TRAILING : DWRITE_TEXT_ALIGNMENT_LEADING;
    draw_text(ctx, display_text(), style, fg, (float)style.pad_left, 0.0f,
              (float)bounds.w - style.pad_left - style.pad_right - 26.0f, (float)bounds.h, 1.0f, DWRITE_FONT_WEIGHT_NORMAL, al);
    draw_text(ctx, L"📅", style, t->text_secondary, (float)bounds.w - style.pad_right - 26.0f, 0.0f, 26.0f, (float)bounds.h);
    ctx.rt->SetTransform(saved);
}

// ── Paint Overlay ────────────────────────────────────────────────────

void DateRangePicker::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || !ctx.rt) return;
    D2D1_MATRIX_3X2_F saved; ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation((float)bounds.x, (float)bounds.y));
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF, fg = t->text_primary, muted = t->text_secondary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFEAF2FF;
    int py = popup_y(), pw = popup_width(), ph = popup_height();
    int pw2 = panel_width();

    // Background
    D2D1_RECT_F outer = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(outer, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, (float)py + 0.5f, (float)pw - 0.5f, (float)(py + ph) - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    // ── Left panel: start month ──
    int left_month = month, left_year = year;
    wchar_t title_l[32]; swprintf_s(title_l, L"%04d年%02d月", left_year, left_month);
    draw_text(ctx, L"‹", style, muted, 12.0f, (float)py, 42.0f, 42.0f, 1.3f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, title_l, style, fg, 42.0f, (float)py, (float)pw2 - 54.0f, 42.0f, 1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    // Right panel: next month
    int right_month = month + 1, right_year = year;
    if (right_month > 12) { right_month = 1; ++right_year; }
    wchar_t title_r[32]; swprintf_s(title_r, L"%04d年%02d月", right_year, right_month);
    draw_text(ctx, L"›", style, muted, (float)pw - 54.0f, (float)py, 42.0f, 42.0f, 1.3f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, title_r, style, fg, (float)pw2 + 24.0f, (float)py, (float)pw2 - 36.0f, 42.0f, 1.0f, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    // Separator
    ctx.rt->DrawLine(D2D1::Point2F((float)pw2 + 12.0f, (float)py + 4.0f),
                     D2D1::Point2F((float)pw2 + 12.0f, (float)(py + ph) - 46.0f),
                     ctx.get_brush(t->border_default), 1.0f);

    // Weekday headers
    static const wchar_t* weeks[] = { L"日", L"一", L"二", L"三", L"四", L"五", L"六" };
    float cell_w = ((float)pw2 - 24.0f) / 7.0f;
    for (int panel = 0; panel < 2; ++panel) {
        float ox = panel == 0 ? 12.0f : (float)pw2 + 24.0f;
        for (int i = 0; i < 7; ++i)
            draw_text(ctx, weeks[i], style, muted, ox + cell_w * i, (float)py + 42.0f, cell_w, 26.0f, 0.85f);
    }

    // Day grids
    float grid_top = (float)py + 68.0f;
    float grid_h = (float)ph - 68.0f - 42.0f;
    float cell_h = grid_h / 6.0f;

    for (int panel = 0; panel < 2; ++panel) {
        int pyear = panel == 0 ? left_year : right_year;
        int pmonth = panel == 0 ? left_month : right_month;
        float ox = panel == 0 ? 12.0f : (float)pw2 + 24.0f;
        int start = first_weekday(pyear, pmonth);
        int max_day = days_in_month(pyear, pmonth);
        for (int day = 1; day <= max_day; ++day) {
            int pos = start + day - 1;
            float x = ox + cell_w * (pos % 7);
            float y = grid_top + cell_h * (pos / 7);
            int cur_val = date_value(pyear, pmonth, day);
            bool sel = cur_val == range_start || cur_val == range_end;
            bool in_range = range_start > 0 && range_end > 0 && cur_val > range_start && cur_val < range_end;
            bool hot = (int)m_hover_panel == panel && m_hover_day == day;
            bool ok = can_select(cur_val);

            if (in_range) {
                D2D1_RECT_F rr = { x + 2, y + 5, x + cell_w - 2, y + cell_h - 5 };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(dark ? 0xFF2D3B55 : 0xFFE8F2FF));
            }
            if (sel || hot) {
                D2D1_RECT_F rr = { x + 4, y + 3, x + cell_w - 4, y + cell_h - 3 };
                ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(sel ? t->accent : hover_bg));
            }
            wchar_t buf[8]; swprintf_s(buf, L"%d", day);
            Color tc = ok ? (sel ? 0xFFFFFFFF : fg) : muted;
            draw_text(ctx, buf, style, tc, x, y, cell_w, cell_h, 0.92f);
        }
    }

    // Footer
    float footer_y = (float)(py + ph) - 42.0f;
    ctx.rt->DrawLine(D2D1::Point2F(12.0f, footer_y), D2D1::Point2F((float)pw - 12.0f, footer_y), ctx.get_brush(t->border_default), 1.0f);
    if (!shortcuts.empty()) {
        float btn_w = (std::min)(120.0f, (float)(pw - 24) / (float)shortcuts.size());
        float total_w = btn_w * (float)shortcuts.size();
        float sx = ((float)pw - total_w) * 0.5f;
        for (size_t i = 0; i < shortcuts.size(); ++i) {
            bool hov = m_hover_part == PartShortcut && (int)i == m_hover_day;
            D2D1_RECT_F br = { sx + btn_w * i, footer_y + 7, sx + btn_w * (i + 1) - 4, footer_y + 35 };
            ctx.rt->FillRoundedRectangle(ROUNDED(br, 4.0f, 4.0f), ctx.get_brush(hov ? (dark ? 0xFF313244 : 0xFFEAF2FF) : bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(br, 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);
            draw_text(ctx, shortcuts[i].text, style, t->accent, br.left, br.top, br.right - br.left, br.bottom - br.top, 0.82f);
        }
    } else {
        D2D1_RECT_F today_br = { 12.0f, footer_y + 7, 90.0f, footer_y + 35 };
        ctx.rt->FillRoundedRectangle(ROUNDED(today_br, 4.0f, 4.0f), ctx.get_brush(m_hover_part == PartToday ? (dark ? 0xFF313244 : 0xFFEAF2FF) : bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(today_br, 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);
        draw_text(ctx, L"📍 今天", style, t->accent, 12, footer_y + 7, 78, 28.0f, 0.85f);
        D2D1_RECT_F clear_br = { (float)pw - 90, footer_y + 7, (float)pw - 12, footer_y + 35 };
        ctx.rt->FillRoundedRectangle(ROUNDED(clear_br, 4.0f, 4.0f), ctx.get_brush(m_hover_part == PartClear ? (dark ? 0xFF313244 : 0xFFEAF2FF) : bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(clear_br, 4.0f, 4.0f), ctx.get_brush(t->border_default), 1.0f);
        draw_text(ctx, L"清空", style, muted, (float)pw - 90, footer_y + 7, 78, 28.0f, 0.85f);
    }
    ctx.rt->SetTransform(saved);
}

// ── Hit test ─────────────────────────────────────────────────────────

Element* DateRangePicker::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x, ly = y - bounds.y;
    if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    return nullptr;
}

Element* DateRangePicker::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x, ly = y - bounds.y;
    int py = popup_y(), pw = popup_width(), ph = popup_height();
    if (lx < 0 || lx >= pw || ly < py || ly >= py + ph) return nullptr;
    return this;
}

// ── Mouse ────────────────────────────────────────────────────────────

int DateRangePicker::hover_day() const { return m_hover_day; }

void DateRangePicker::on_mouse_move(int x, int y) {
    if (!open) { m_hover_part = PartNone; m_hover_day = 0; return; }
    int lx = x - bounds.x, ly = y - bounds.y;
    int py = popup_y(), pw = popup_width(), ph = popup_height();
    int pw2 = panel_width();
    float cell_w = ((float)pw2 - 24.0f) / 7.0f;
    float grid_top = (float)py + 68.0f;
    float cell_h = ((float)ph - 68.0f - 42.0f) / 6.0f;

    // Footer check
    float fy = (float)(py + ph) - 42.0f;
    if (ly >= fy) {
        if (!shortcuts.empty()) {
            float btn_w = (std::min)(120.0f, (float)(pw - 24) / (float)shortcuts.size());
            float total_w = btn_w * (float)shortcuts.size();
            float sx = ((float)pw - total_w) * 0.5f;
            m_hover_part = PartNone; m_hover_day = 0;
            for (size_t i = 0; i < shortcuts.size(); ++i) {
                if (lx >= sx + btn_w * i && lx < sx + btn_w * (i + 1)) { m_hover_part = PartShortcut; m_hover_day = (int)i; break; }
            }
        } else {
            if (lx >= 12 && lx < 90) m_hover_part = PartToday;
            else if (lx >= pw - 90 && lx < pw - 12) m_hover_part = PartClear;
            else m_hover_part = PartNone;
        }
        invalidate(); return;
    }

    // Day grid
    for (int panel = 0; panel < 2; ++panel) {
        float ox = panel == 0 ? 12.0f : (float)pw2 + 24.0f;
        int pyear = panel == 0 ? year : (month < 12 ? year : year + 1);
        int pmonth = panel == 0 ? month : (month < 12 ? month + 1 : 1);
        int start = first_weekday(pyear, pmonth);
        int max_day = days_in_month(pyear, pmonth);
        for (int day = 1; day <= max_day; ++day) {
            int pos = start + day - 1;
            float dx = ox + cell_w * (pos % 7);
            float dy = grid_top + cell_h * (pos / 7);
            if (lx >= dx && lx < dx + cell_w && ly >= dy && ly < dy + cell_h) {
                m_hover_panel = panel; m_hover_day = day; m_hover_part = PartDay; invalidate(); return;
            }
        }
    }
    m_hover_part = PartNone; m_hover_day = 0; invalidate();
}

void DateRangePicker::on_mouse_leave() { m_hover_part = PartNone; m_hover_day = 0; invalidate(); }
void DateRangePicker::on_mouse_down(int x, int y, MouseButton) {
    int lx = x - bounds.x, ly = y - bounds.y;
    m_press_part = PartNone; m_press_day = 0; m_press_panel = 0;
    if (!open) {
        if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) m_press_part = PartMain;
        return;
    }
    int py = popup_y(), pw = popup_width(), ph = popup_height();
    int pw2 = panel_width();
    // Check prev/next
    if (ly >= py && ly < py + 42) {
        if (lx >= 12 && lx < 42) m_press_part = PartPrev;
        else if (lx >= pw - 42 && lx < pw - 12) m_press_part = PartNext;
        else return;
    }
    // Check footer
    float fy = (float)(py + ph) - 42.0f;
    if (ly >= fy) {
        if (!shortcuts.empty()) {
            float btn_w = (std::min)(120.0f, (float)(pw - 24) / (float)shortcuts.size());
            float total_w = btn_w * (float)shortcuts.size();
            float sx = ((float)pw - total_w) * 0.5f;
            for (size_t i = 0; i < shortcuts.size(); ++i) {
                if (lx >= sx + btn_w * i && lx < sx + btn_w * (i + 1)) { m_press_part = PartShortcut; m_press_day = (int)i; break; }
            }
        } else {
            if (lx >= 12 && lx < 90) m_press_part = PartToday;
            else if (lx >= pw - 90 && lx < pw - 12) m_press_part = PartClear;
        }
        return;
    }
    // Day grid
    float cell_w = ((float)pw2 - 24.0f) / 7.0f;
    float grid_top = (float)py + 68.0f;
    float cell_h = ((float)ph - 68.0f - 42.0f) / 6.0f;
    for (int panel = 0; panel < 2; ++panel) {
        float ox = panel == 0 ? 12.0f : (float)pw2 + 24.0f;
        int pyear = panel == 0 ? year : (month < 12 ? year : year + 1);
        int pmonth = panel == 0 ? month : (month < 12 ? month + 1 : 1);
        int start = first_weekday(pyear, pmonth);
        int max_day = days_in_month(pyear, pmonth);
        for (int day = 1; day <= max_day; ++day) {
            int pos = start + day - 1;
            float dx = ox + cell_w * (pos % 7);
            float dy = grid_top + cell_h * (pos / 7);
            if (lx >= dx && lx < dx + cell_w && ly >= dy && ly < dy + cell_h) {
                int cur = date_value(pyear, pmonth, day);
                if (can_select(cur)) { m_press_part = PartDay; m_press_day = day; m_press_panel = panel; }
                return;
            }
        }
    }
}

void DateRangePicker::on_mouse_up(int x, int y, MouseButton) {
    int lx = x - bounds.x, ly = y - bounds.y;
    if (m_press_part == PartMain && lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) { open = !open; m_picking_end = false; }
    else if (m_press_part == PartPrev) move_month(-1);
    else if (m_press_part == PartNext) move_month(1);
    else if (m_press_part == PartToday) { open = false; invalidate(); }
    else if (m_press_part == PartClear) { clear_value(); }
    else if (m_press_part == PartShortcut) {
        if (m_press_day >= 0 && (size_t)m_press_day < shortcuts.size()) {
            auto& sc = shortcuts[m_press_day];
            if (sc.yyyymmdd_end > 0) set_value(sc.yyyymmdd, sc.yyyymmdd_end);
            else set_value(sc.yyyymmdd, sc.yyyymmdd);
            open = false;
        }
    }
    else if (m_press_part == PartDay) {
        int pyear = m_press_panel == 0 ? year : (month < 12 ? year : year + 1);
        int pmonth = m_press_panel == 0 ? month : (month < 12 ? month + 1 : 1);
        int cur = date_value(pyear, pmonth, m_press_day);
        if (can_select(cur)) {
            if (range_start == 0 || (range_start > 0 && range_end > 0)) {
                range_start = cur; range_end = 0; m_picking_end = true;
            } else {
                range_end = cur;
                if (range_start > range_end) std::swap(range_start, range_end);
                open = false; m_picking_end = false;
            }
        }
    }
    m_press_part = PartNone; m_press_day = 0; m_press_panel = 0;
    invalidate();
}

// ── Keyboard ─────────────────────────────────────────────────────────

void DateRangePicker::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) open = !open;
    else if (vk == VK_ESCAPE) open = false;
    else if (vk == VK_LEFT) move_month(-1);
    else if (vk == VK_RIGHT) move_month(1);
    invalidate();
}

void DateRangePicker::on_blur() { open = false; invalidate(); }
