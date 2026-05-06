#include "element_statistic.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cwchar>
#include <iomanip>
#include <map>
#include <sstream>

std::map<UINT_PTR, Statistic*> g_statistic_timer_map;

static long long now_unix_ms() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

static float measure_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                          float font_size, DWRITE_FONT_WEIGHT weight) {
    if (text.empty()) return 0.0f;
    auto* layout = ctx.create_text_layout(text, style.font_name, font_size, 4096.0f, 96.0f);
    if (!layout) return 0.0f;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    DWRITE_TEXT_METRICS metrics{};
    layout->GetMetrics(&metrics);
    layout->Release();
    return metrics.widthIncludingTrailingWhitespace;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_size,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, font_size, w, h);
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

static std::wstring format_duration(long long remaining, const std::wstring& format) {
    if (remaining < 0) remaining = 0;
    long long total_seconds = remaining / 1000;
    long long days = total_seconds / 86400;
    long long hours_total = total_seconds / 3600;
    long long hours = (total_seconds / 3600) % 24;
    long long minutes = (total_seconds / 60) % 60;
    long long seconds = total_seconds % 60;

    std::wostringstream ss;
    if (format == L"HH:mm:ss") {
        ss << std::setw(2) << std::setfill(L'0') << hours_total << L":"
           << std::setw(2) << minutes << L":"
           << std::setw(2) << seconds;
    } else if (format == L"DD天HH小时mm分钟") {
        ss << days << L"天"
           << std::setw(2) << std::setfill(L'0') << hours << L"小时"
           << std::setw(2) << minutes << L"分钟";
    } else {
        if (days > 0) ss << days << L"天 ";
        ss << std::setw(2) << std::setfill(L'0') << hours << L"小时"
           << std::setw(2) << minutes << L"分钟"
           << std::setw(2) << seconds << L"秒";
    }
    return ss.str();
}

Statistic::~Statistic() {
    stop_timer();
}

void Statistic::set_title(const std::wstring& next_value) {
    title = next_value;
    invalidate();
}

void Statistic::set_value(const std::wstring& next_value) {
    value = next_value;
    text = next_value;
    mode = ModeNumber;
    stop_timer();
    wchar_t* end = nullptr;
    double parsed = std::wcstod(value.c_str(), &end);
    if (end != value.c_str()) {
        target_value = parsed;
        reset_animation();
    }
    invalidate();
}

void Statistic::set_prefix(const std::wstring& next_value) {
    prefix = next_value;
    invalidate();
}

void Statistic::set_suffix(const std::wstring& next_value) {
    suffix = next_value;
    invalidate();
}

void Statistic::set_format(const std::wstring& title_value,
                           const std::wstring& prefix_value,
                           const std::wstring& suffix_value) {
    title = title_value;
    prefix = prefix_value;
    suffix = suffix_value;
    invalidate();
}

void Statistic::set_options(int precision_value, bool animated_value) {
    set_number_options(precision_value, animated_value, group_separator,
                       group_separator_char, decimal_separator_char);
}

void Statistic::set_number_options(int precision_value, bool animated_value,
                                   bool group_separator_value,
                                   wchar_t group_separator_value_char,
                                   wchar_t decimal_separator_value_char) {
    if (precision_value < -1) precision_value = -1;
    if (precision_value > 6) precision_value = 6;
    precision = precision_value;
    animated = animated_value;
    group_separator = group_separator_value;
    group_separator_char = group_separator_value_char ? group_separator_value_char : L',';
    decimal_separator_char = decimal_separator_value_char ? decimal_separator_value_char : L'.';
    reset_animation();
    invalidate();
}

void Statistic::set_affix_options(const std::wstring& prefix_value,
                                  const std::wstring& suffix_value,
                                  Color prefix_color_value,
                                  Color suffix_color_value,
                                  Color value_color_value,
                                  bool suffix_clickable_value) {
    prefix = prefix_value;
    suffix = suffix_value;
    prefix_color = prefix_color_value;
    suffix_color = suffix_color_value;
    value_color = value_color_value;
    suffix_clickable = suffix_clickable_value;
    invalidate();
}

void Statistic::set_display_text(const std::wstring& text_value) {
    display_text = text_value;
    mode = ModeText;
    stop_timer();
    invalidate();
}

void Statistic::set_countdown(long long target_unix_ms, const std::wstring& format_value) {
    mode = ModeCountdown;
    countdown_target_ms = target_unix_ms;
    countdown_format = format_value;
    countdown_paused = false;
    pause_remaining_ms = 0;
    countdown_finished = remaining_ms() <= 0;
    if (!countdown_finished) ensure_timer();
    else stop_timer();
    invalidate();
}

void Statistic::set_countdown_paused(bool paused_value) {
    if (mode != ModeCountdown) return;
    if (paused_value == countdown_paused) return;
    if (paused_value) {
        pause_remaining_ms = remaining_ms();
        countdown_paused = true;
        stop_timer();
    } else {
        countdown_paused = false;
        countdown_target_ms = now_unix_ms() + pause_remaining_ms;
        countdown_finished = pause_remaining_ms <= 0;
        if (!countdown_finished) ensure_timer();
    }
    invalidate();
}

void Statistic::add_countdown_time(long long delta_ms) {
    if (mode != ModeCountdown) return;
    if (countdown_paused) {
        pause_remaining_ms = (std::max)(0LL, pause_remaining_ms + delta_ms);
        countdown_finished = pause_remaining_ms <= 0;
    } else {
        countdown_target_ms += delta_ms;
        countdown_finished = remaining_ms() <= 0;
    }
    if (!countdown_finished && !countdown_paused) ensure_timer();
    invalidate();
}

void Statistic::tick(int) {
    if (mode != ModeCountdown || countdown_paused) {
        stop_timer();
        return;
    }
    maybe_finish_countdown();
    if (countdown_finished) {
        stop_timer();
        return;
    }
    invalidate();
}

long long Statistic::remaining_ms() const {
    if (mode != ModeCountdown) return 0;
    if (countdown_paused) return (std::max)(0LL, pause_remaining_ms);
    return (std::max)(0LL, countdown_target_ms - now_unix_ms());
}

void Statistic::reset_animation() {
    if (!animated) {
        display_value = target_value;
        anim_start = 0;
        return;
    }
    anim_start = GetTickCount64();
}

std::wstring Statistic::display_number() const {
    if (precision < 0) return value.empty() ? text : value;
    double shown = display_value;
    std::wostringstream ss;
    ss << std::fixed << std::setprecision(precision) << shown;
    std::wstring out = ss.str();

    size_t dot = out.find(L'.');
    size_t integer_end = dot == std::wstring::npos ? out.size() : dot;
    size_t sign_offset = (!out.empty() && out[0] == L'-') ? 1 : 0;

    if (group_separator) {
        for (size_t i = integer_end; i > sign_offset + 3; i -= 3) {
            out.insert(i - 3, 1, group_separator_char);
        }
    }
    if (decimal_separator_char != L'.' && dot != std::wstring::npos) {
        out[dot] = decimal_separator_char;
    }
    return out;
}

std::wstring Statistic::display_value_text() const {
    if (mode == ModeText) return display_text;
    if (mode == ModeCountdown) return display_countdown();
    return display_number();
}

std::wstring Statistic::display_countdown() const {
    return format_duration(remaining_ms(), countdown_format);
}

void Statistic::ensure_timer() {
    if (m_timer_id || !owner_hwnd || mode != ModeCountdown || countdown_paused || countdown_finished) return;
    m_timer_id = 0xE000 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 200, nullptr);
    if (m_timer_id) g_statistic_timer_map[m_timer_id] = this;
}

void Statistic::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_statistic_timer_map.erase(m_timer_id);
    m_timer_id = 0;
}

bool Statistic::suffix_hit(int x, int y) const {
    return suffix_clickable && !suffix.empty() && m_suffix_rect.contains(x, y);
}

void Statistic::maybe_finish_countdown() {
    if (mode != ModeCountdown || countdown_paused || countdown_finished) return;
    if (remaining_ms() > 0) return;
    countdown_finished = true;
    if (finish_cb) finish_cb(id);
    invalidate();
}

void Statistic::on_mouse_move(int x, int y) {
    bool next_hover = suffix_hit(x, y);
    if (next_hover != m_suffix_hover) {
        m_suffix_hover = next_hover;
        invalidate();
    }
}

void Statistic::on_mouse_leave() {
    Element::on_mouse_leave();
    m_suffix_hover = false;
    m_suffix_down = false;
}

void Statistic::on_mouse_down(int x, int y, MouseButton btn) {
    Element::on_mouse_down(x, y, btn);
    if (btn == MouseButton::Left && suffix_hit(x, y)) {
        m_suffix_down = true;
        invalidate();
    }
}

void Statistic::on_mouse_up(int x, int y, MouseButton btn) {
    Element::on_mouse_up(x, y, btn);
    bool clicked_suffix = btn == MouseButton::Left && m_suffix_down && suffix_hit(x, y);
    m_suffix_down = false;
    if (clicked_suffix) {
        ++suffix_click_count;
        if (suffix_click_cb) suffix_click_cb(id);
    }
    invalidate();
}

void Statistic::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    if (mode == ModeCountdown) {
        maybe_finish_countdown();
        if (!countdown_finished && !countdown_paused) ensure_timer();
    }

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = t->text_secondary;
    Color main_fg = value_color ? value_color : (style.fg_color ? style.fg_color : t->text_primary);
    Color pre_fg = prefix_color ? prefix_color : main_fg;
    Color suf_fg = suffix_color ? suffix_color : main_fg;
    Color accent = t->accent;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ rect, radius, radius }, ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(D2D1_ROUNDED_RECT{
        D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f),
        radius, radius }, ctx.get_brush(border), 1.0f);

    float x = (float)style.pad_left;
    float y = (float)style.pad_top;
    float w = (float)bounds.w - style.pad_left - style.pad_right;
    if (w < 1.0f) w = 1.0f;
    float title_h = (std::max)(style.font_size * 1.45f, 20.0f);
    draw_text(ctx, title.empty() ? L"📊 统计数值" : title, style, title_fg,
              x, y, w, title_h, style.font_size * 0.92f);

    if (mode == ModeNumber && precision >= 0 && animated && anim_start != 0) {
        ULONGLONG elapsed = GetTickCount64() - anim_start;
        float p = (std::min)(1.0f, (float)elapsed / 320.0f);
        display_value = target_value * (1.0 - (1.0 - p) * (1.0 - p));
        if (p < 1.0f) invalidate();
    } else if (mode == ModeNumber && precision >= 0) {
        display_value = target_value;
    }

    std::wstring core = display_value_text();
    float value_h = (float)bounds.h - y - title_h - style.pad_bottom;
    if (value_h < style.font_size * 2.0f) value_h = style.font_size * 2.0f;
    float value_font = style.font_size * (bounds.w < 150 ? 1.42f : 1.78f);
    if (mode == ModeCountdown && core.size() > 10) value_font = style.font_size * 1.42f;
    float value_y = y + title_h + 2.0f;

    float prefix_w = measure_text(ctx, prefix, style, value_font, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    float core_w = measure_text(ctx, core, style, value_font, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    float suffix_w = measure_text(ctx, suffix, style, value_font, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    float total_w = prefix_w + core_w + suffix_w;
    float start_x = x + (std::max)(0.0f, (w - total_w) * 0.5f);
    if (total_w > w) start_x = x;

    draw_text(ctx, prefix, style, pre_fg, start_x, value_y, prefix_w + 4.0f, value_h,
              value_font, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, core, style, main_fg, start_x + prefix_w, value_y,
              (std::max)(1.0f, w - prefix_w - suffix_w), value_h,
              value_font, DWRITE_FONT_WEIGHT_SEMI_BOLD);

    float suffix_x = start_x + prefix_w + core_w;
    Color actual_suffix_color = (suffix_clickable && m_suffix_hover) ? accent : suf_fg;
    draw_text(ctx, suffix, style, actual_suffix_color, suffix_x, value_y, suffix_w + 6.0f, value_h,
              value_font, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    m_suffix_rect = { (int)std::floor(suffix_x), (int)std::floor(value_y),
                      (int)std::ceil(suffix_w + 8.0f), (int)std::ceil(value_h) };

    ctx.rt->FillRectangle(D2D1::RectF(0.0f, 0.0f, 4.0f, (float)bounds.h),
                          ctx.get_brush(accent));

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
