#include "element_timeselect.h"
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

static int hhmm_to_minutes(int value) {
    int v = normalize_hhmm(value);
    return (v / 100) * 60 + (v % 100);
}

static int minutes_to_hhmm(int value) {
    if (value < 0) value = 0;
    if (value > 23 * 60 + 59) value = 23 * 60 + 59;
    return (value / 60) * 100 + (value % 60);
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

int TimeSelect::popup_width() const {
    return (std::max)(bounds.w, 220);
}

int TimeSelect::popup_height() const {
    return 36 + visible_row_count() * row_height() + 12;
}

int TimeSelect::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

int TimeSelect::row_height() const {
    return 28;
}

int TimeSelect::visible_row_count() const {
    return 10;
}

int TimeSelect::candidate_count() const {
    int start = hhmm_to_minutes(min_time);
    int end = hhmm_to_minutes(max_time);
    if (end < start) return 0;
    return ((end - start) / minute_step_from_value(step_minutes)) + 1;
}

int TimeSelect::group_count() const {
    int count = 0;
    int last_group = -1;
    for (int i = 0; i < candidate_count(); ++i) {
        int h = option_minutes(i) / 60;
        int group = h < 6 ? 0 : (h < 12 ? 1 : (h < 18 ? 2 : 3));
        if (group != last_group) {
            ++count;
            last_group = group;
        }
    }
    return count;
}

int TimeSelect::total_row_count() const {
    return candidate_count() + group_count();
}

int TimeSelect::option_minutes(int index) const {
    int count = candidate_count();
    if (index < 0) index = 0;
    if (index >= count) index = count - 1;
    int start = hhmm_to_minutes(min_time);
    return start + index * minute_step_from_value(step_minutes);
}

int TimeSelect::option_value(int index) const {
    return minutes_to_hhmm(option_minutes(index));
}

int TimeSelect::row_option_index(int row, bool* is_group) const {
    if (is_group) *is_group = false;
    if (row < 0) return -1;
    int visual_row = 0;
    int last_group = -1;
    for (int i = 0; i < candidate_count(); ++i) {
        int h = option_minutes(i) / 60;
        int group = h < 6 ? 0 : (h < 12 ? 1 : (h < 18 ? 2 : 3));
        if (group != last_group) {
            if (visual_row == row) {
                if (is_group) *is_group = true;
                return -1;
            }
            ++visual_row;
            last_group = group;
        }
        if (visual_row == row) return i;
        ++visual_row;
    }
    return -1;
}

int TimeSelect::selected_option_index() const {
    int current = hhmm_to_minutes(value());
    for (int i = 0; i < candidate_count(); ++i) {
        if (option_minutes(i) == current) return i;
    }
    return 0;
}

void TimeSelect::clamp_scroll() {
    int max_scroll = (std::max)(0, total_row_count() - visible_row_count());
    if (m_scroll < 0) m_scroll = 0;
    if (m_scroll > max_scroll) m_scroll = max_scroll;
}

void TimeSelect::ensure_selected_visible() {
    int target = selected_option_index();
    m_active_index = target;
    int visual_row = 0;
    int last_group = -1;
    for (int i = 0; i < candidate_count(); ++i) {
        int h = option_minutes(i) / 60;
        int group = h < 6 ? 0 : (h < 12 ? 1 : (h < 18 ? 2 : 3));
        if (group != last_group) {
            ++visual_row;
            last_group = group;
        }
        if (i == target) break;
        ++visual_row;
    }
    if (visual_row < m_scroll) m_scroll = visual_row;
    if (visual_row >= m_scroll + visible_row_count()) {
        m_scroll = visual_row - visible_row_count() + 1;
    }
    clamp_scroll();
}

bool TimeSelect::select_option_index(int index) {
    int count = candidate_count();
    if (index < 0 || index >= count) return false;
    int hhmm = option_value(index);
    if (!can_select_time(hhmm / 100, hhmm % 100)) return false;
    hour = hhmm / 100;
    minute = hhmm % 100;
    m_active_index = index;
    ensure_selected_visible();
    invalidate();
    return true;
}

bool TimeSelect::select_step(int delta) {
    return select_option_index(selected_option_index() + delta);
}

bool TimeSelect::can_select_time(int next_hour, int next_minute) const {
    int v = normalize_hhmm(next_hour * 100 + next_minute);
    return v >= min_time && v <= max_time;
}

void TimeSelect::set_time(int next_hour, int next_minute) {
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

void TimeSelect::set_range(int min_hhmm, int max_hhmm) {
    min_time = normalize_hhmm(min_hhmm);
    max_time = normalize_hhmm(max_hhmm);
    if (min_time > max_time) std::swap(min_time, max_time);
    set_time(hour, minute);
}

void TimeSelect::set_options(int next_step_minutes, int next_time_format) {
    step_minutes = minute_step_from_value(next_step_minutes);
    time_format = next_time_format;
    set_time(hour, minute);
    clamp_scroll();
}

void TimeSelect::set_open(bool next_open) {
    open = next_open;
    if (open) ensure_selected_visible();
    invalidate();
}

void TimeSelect::set_scroll(int next_scroll) {
    m_scroll = next_scroll;
    clamp_scroll();
    invalidate();
}

int TimeSelect::scroll() const {
    return m_scroll;
}

int TimeSelect::active_index() const {
    return m_active_index;
}

int TimeSelect::value() const {
    return hour * 100 + minute;
}

bool TimeSelect::is_open() const {
    return open;
}

std::wstring TimeSelect::display_text() const {
    wchar_t buf[16];
    if (time_format == 1) {
        swprintf_s(buf, L"%02d\u65F6%02d\u5206", hour, minute);
    } else {
        swprintf_s(buf, L"%02d:%02d", hour, minute);
    }
    return buf;
}

std::wstring TimeSelect::group_text(int minutes) const {
    int h = minutes / 60;
    if (h < 6) return L"🌙 凌晨";
    if (h < 12) return L"🌤 上午";
    if (h < 18) return L"☀ 下午";
    return L"🌆 晚上";
}

std::wstring TimeSelect::option_text(int hhmm) const {
    wchar_t buf[32];
    int h = hhmm / 100;
    int m = hhmm % 100;
    if (time_format == 1) {
        swprintf_s(buf, L"%02d时%02d分", h, m);
    } else {
        swprintf_s(buf, L"%02d:%02d", h, m);
    }
    return buf;
}

TimeSelect::Part TimeSelect::part_at(int x, int y, int* value) const {
    if (value) *value = -1;
    if (!open) {
        if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
        return PartNone;
    }
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    if (x >= 0 && x < pw && y >= py && y < py + ph) {
        int local_y = y - py - 36;
        if (local_y >= 0) {
            int row = local_y / row_height();
            if (row >= 0 && row < visible_row_count()) {
                bool is_group = false;
                int index = row_option_index(m_scroll + row, &is_group);
                if (!is_group && index >= 0) {
                    if (value) *value = index;
                    return PartOption;
                }
            }
        }
    }
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

Element* TimeSelect::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* TimeSelect::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    int value = -1;
    Part p = part_at(lx, ly, &value);
    return (p == PartOption) ? this : nullptr;
}

void TimeSelect::paint(RenderContext& ctx) {
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
    draw_text(ctx, L"˅", style, t->text_secondary,
              (float)bounds.w - style.pad_right - 26.0f, 0.0f, 26.0f, (float)bounds.h);

    ctx.rt->SetTransform(saved);
}

void TimeSelect::paint_overlay(RenderContext& ctx) {
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
    int rh = row_height();

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    draw_text(ctx, L"候选时间", style, t->text_secondary, 0.0f, (float)py, (float)pw, 36.0f);
    ctx.rt->DrawLine(D2D1::Point2F(0.0f, (float)py + 36.0f),
                     D2D1::Point2F((float)pw, (float)py + 36.0f),
                     ctx.get_brush(t->border_default), 1.0f);

    int rows = visible_row_count();
    for (int r = 0; r < rows; ++r) {
        bool is_group = false;
        int index = row_option_index(m_scroll + r, &is_group);
        float y = (float)(py + 36 + r * rh);
        if (is_group) {
            int next_index = row_option_index(m_scroll + r + 1);
            int minutes = next_index >= 0 ? option_minutes(next_index) : 0;
            D2D1_RECT_F group_bg = { 0.0f, y, (float)pw, y + (float)rh };
            ctx.rt->FillRectangle(group_bg, ctx.get_brush(dark ? 0xFF1F2130 : 0xFFF4F6FA));
            draw_text(ctx, group_text(minutes), style, t->text_secondary,
                      12.0f, y, (float)pw - 24.0f, (float)rh, DWRITE_TEXT_ALIGNMENT_LEADING);
            continue;
        }
        if (index < 0) continue;
        int hhmm = option_value(index);
        bool selected = index == selected_option_index();
        bool hot = m_hover_part == PartOption && m_hover_value == index;
        if (selected || hot) {
            D2D1_RECT_F row = { 4.0f, y + 2.0f, (float)pw - 4.0f, y + (float)rh - 2.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
                ctx.get_brush(selected ? with_alpha(t->accent, 0x33) : t->button_hover));
        }
        draw_text(ctx, option_text(hhmm), style, selected ? t->accent : fg,
                  16.0f, y, (float)pw - 68.0f, (float)rh, DWRITE_TEXT_ALIGNMENT_LEADING);
        if (selected) {
            draw_text(ctx, L"✓", style, t->accent,
                      (float)pw - 44.0f, y, 28.0f, (float)rh);
        }
    }

    wchar_t hint[32];
    swprintf_s(hint, L"%d/%d", (std::min)(m_scroll + 1, (std::max)(1, total_row_count())),
               (std::max)(1, total_row_count()));
    draw_text(ctx, hint, style, t->text_secondary,
              (float)pw - 68.0f, (float)(py + ph - 12), 56.0f, 10.0f);

    ctx.rt->SetTransform(saved);
}

void TimeSelect::on_mouse_move(int x, int y) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p != PartOption) {
        p = PartNone;
        value = -1;
    }
    if (p != m_hover_part || value != m_hover_value) {
        m_hover_part = p;
        m_hover_value = value;
        invalidate();
    }
}

void TimeSelect::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_part = PartNone;
    m_hover_value = -1;
    m_press_part = PartNone;
    m_press_value = -1;
    invalidate();
}

void TimeSelect::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_value);
    pressed = true;
    invalidate();
}

void TimeSelect::on_mouse_up(int x, int y, MouseButton) {
    int value = -1;
    Part p = part_at(x, y, &value);
    if (p == PartMain && m_press_part == PartMain) {
        open = !open;
        if (open) ensure_selected_visible();
    } else if (p == m_press_part && value == m_press_value) {
        if (p == PartOption) {
            select_option_index(value);
            open = false;
        }
    }
    m_press_part = PartNone;
    m_press_value = -1;
    pressed = false;
    invalidate();
}

void TimeSelect::on_mouse_wheel(int, int, int delta) {
    m_scroll += delta > 0 ? -3 : 3;
    clamp_scroll();
    invalidate();
}

void TimeSelect::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        open = !open;
        if (open) ensure_selected_visible();
    } else if (vk == VK_ESCAPE) {
        open = false;
    } else if (vk == VK_UP) {
        if (open) select_step(-1);
        else set_time(hour, minute - minute_step_from_value(step_minutes));
    } else if (vk == VK_DOWN) {
        if (open) select_step(1);
        else set_time(hour, minute + minute_step_from_value(step_minutes));
    } else if (vk == VK_PRIOR) {
        if (open) {
            m_scroll -= visible_row_count();
            clamp_scroll();
            select_step(-visible_row_count());
        }
    } else if (vk == VK_NEXT) {
        if (open) {
            m_scroll += visible_row_count();
            clamp_scroll();
            select_step(visible_row_count());
        }
    } else if (vk == VK_HOME) {
        select_option_index(0);
    } else if (vk == VK_END) {
        select_option_index(candidate_count() - 1);
    }
    invalidate();
}

void TimeSelect::on_blur() {
    has_focus = false;
    open = false;
    m_hover_part = PartNone;
    m_hover_value = -1;
    m_press_part = PartNone;
    invalidate();
}
