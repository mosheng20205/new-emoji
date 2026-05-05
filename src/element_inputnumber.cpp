#include "element_inputnumber.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <climits>
#include <cmath>
#include <cwctype>
#include <map>

static std::map<UINT_PTR, InputNumber*> g_input_number_repeat_map;

static int round_px(float v) {
    return (int)std::lround(v);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING) {
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

InputNumber::~InputNumber() {
    stop_repeat();
}

int InputNumber::spin_width() const {
    int w = round_px(style.font_size * 1.8f);
    if (w < 26) w = 26;
    if (bounds.w > 0 && w > bounds.w / 3) w = bounds.w / 3;
    return w;
}

int InputNumber::scale_factor() const {
    int factor = 1;
    for (int i = 0; i < precision; ++i) factor *= 10;
    return factor;
}

int InputNumber::clamp_value(int v) const {
    return (std::max)(min_value, (std::min)(max_value, v));
}

void InputNumber::set_range(int min_v, int max_v) {
    if (min_v > max_v) std::swap(min_v, max_v);
    if (min_v == max_v) max_v = min_v + 1;
    min_value = min_v;
    max_value = max_v;
    set_value(value);
}

void InputNumber::set_step(int new_step) {
    if (new_step == 0) new_step = 1;
    if (new_step < 0) new_step = -new_step;
    step = new_step;
}

void InputNumber::set_value(int new_value) {
    if (step_strictly && step > 1) {
        int offset = new_value - min_value;
        int rounded = ((offset + step / 2) / step) * step;
        new_value = min_value + rounded;
    }
    int next = clamp_value(new_value);
    bool changed = value != next;
    if (changed) value = next;
    if (m_editing && !m_edit_buffer.empty() && m_edit_buffer != L"-") {
        m_edit_buffer = format_value(value);
    }
    last_input_valid = true;
    invalidate();
    if (changed) notify_value_changed();
}

void InputNumber::set_step_strictly(bool strict) {
    step_strictly = strict;
    if (strict) {
        int aligned = min_value + ((value - min_value) / step) * step;
        if (aligned < min_value) aligned = min_value;
        if (aligned > max_value) aligned = max_value - ((max_value - min_value) % step);
        if (aligned != value) set_value(aligned);
    }
}

void InputNumber::set_precision(int new_precision) {
    if (new_precision < 0) new_precision = 0;
    if (new_precision > 4) new_precision = 4;
    precision = new_precision;
    if (m_editing) m_edit_buffer = format_value(value);
    invalidate();
}

bool InputNumber::set_value_from_text(const std::wstring& value_text) {
    m_edit_buffer = value_text;
    int parsed = value;
    if (!parse_edit_buffer(parsed)) {
        last_input_valid = false;
        invalidate();
        return false;
    }
    m_editing = false;
    m_replace_on_next_char = true;
    set_value(parsed);
    last_input_valid = true;
    return true;
}

bool InputNumber::can_step(int delta) const {
    if (delta > 0) return value < max_value;
    if (delta < 0) return value > min_value;
    return false;
}

InputNumber::Part InputNumber::part_at(int x, int y) const {
    if (x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return PartNone;
    int sw = spin_width();
    if (x >= bounds.w - sw) {
        return y < bounds.h / 2 ? PartUp : PartDown;
    }
    return PartMain;
}

void InputNumber::step_by(int delta) {
    if (!can_step(delta)) return;
    set_value(value + delta);
    if (m_editing) {
        m_edit_buffer = format_value(value);
        m_replace_on_next_char = true;
    }
}

void CALLBACK InputNumber::repeat_timer(HWND, UINT, UINT_PTR id, DWORD) {
    auto it = g_input_number_repeat_map.find(id);
    if (it != g_input_number_repeat_map.end() && it->second) {
        it->second->step_by(it->second->m_repeat_delta);
    }
}

void InputNumber::start_repeat(int delta) {
    stop_repeat();
    if (!owner_hwnd || delta == 0 || !can_step(delta)) return;
    m_repeat_delta = delta;
    m_repeat_timer = SetTimer(owner_hwnd, 0, 180, repeat_timer);
    if (m_repeat_timer) g_input_number_repeat_map[m_repeat_timer] = this;
}

void InputNumber::stop_repeat() {
    if (m_repeat_timer && owner_hwnd) {
        KillTimer(owner_hwnd, m_repeat_timer);
        g_input_number_repeat_map.erase(m_repeat_timer);
    }
    m_repeat_timer = 0;
    m_repeat_delta = 0;
}

void InputNumber::start_edit() {
    m_editing = true;
    m_edit_buffer = format_value(value);
    m_replace_on_next_char = true;
    invalidate();
}

bool InputNumber::parse_edit_buffer(int& out) const {
    if (m_edit_buffer.empty() || m_edit_buffer == L"-") return false;
    int sign = 1;
    size_t i = 0;
    if (m_edit_buffer[0] == L'-') {
        sign = -1;
        i = 1;
    } else if (m_edit_buffer[0] == L'+') {
        i = 1;
    }
    long long whole = 0;
    long long frac = 0;
    int frac_digits = 0;
    bool seen_digit = false;
    bool seen_dot = false;
    for (; i < m_edit_buffer.size(); ++i) {
        wchar_t ch = m_edit_buffer[i];
        if (ch == L'.') {
            if (seen_dot || precision == 0) return false;
            seen_dot = true;
            continue;
        }
        if (!iswdigit(ch)) return false;
        seen_digit = true;
        int digit = ch - L'0';
        if (seen_dot) {
            if (frac_digits >= precision) return false;
            frac = frac * 10 + digit;
            ++frac_digits;
        } else {
            whole = whole * 10 + digit;
        }
    }
    if (!seen_digit) return false;
    int factor = scale_factor();
    while (frac_digits < precision) {
        frac *= 10;
        ++frac_digits;
    }
    long long scaled = (whole * factor + frac) * sign;
    if (scaled > INT_MAX || scaled < INT_MIN) return false;
    out = clamp_value((int)scaled);
    return true;
}

void InputNumber::commit_edit() {
    if (!m_editing) return;
    int parsed = value;
    if (parse_edit_buffer(parsed)) {
        set_value(parsed);
        last_input_valid = true;
    } else {
        last_input_valid = false;
    }
    m_edit_buffer = format_value(value);
    m_editing = false;
    m_replace_on_next_char = true;
    invalidate();
}

std::wstring InputNumber::format_value(int v) const {
    if (precision <= 0) return std::to_wstring(v);
    int factor = scale_factor();
    int abs_v = v < 0 ? -v : v;
    int whole = abs_v / factor;
    int frac = abs_v % factor;
    std::wstring result = v < 0 ? L"-" : L"";
    result += std::to_wstring(whole);
    result += L".";
    std::wstring frac_text = std::to_wstring(frac);
    while ((int)frac_text.size() < precision) frac_text.insert(frac_text.begin(), L'0');
    result += frac_text;
    return result;
}

std::wstring InputNumber::display_value() const {
    return m_editing ? m_edit_buffer : format_value(value);
}

void InputNumber::notify_value_changed() {
    if (value_cb) value_cb(id, value, min_value, max_value);
}

void InputNumber::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    if (!last_input_valid) border = 0xFFE53935;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    if (!enabled) {
        bool dark = is_dark_theme_for_window(owner_hwnd);
        bg = dark ? 0xFF2A2D3A : 0xFFE5E7EB;
        border = dark ? 0xFF3A3D4C : 0xFFD1D5DB;
        fg = t->text_muted;
    }
    float r = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(rect, r, r), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), r, r),
        ctx.get_brush(border), has_focus ? 1.5f : 1.0f);

    int sw = spin_width();
    float spinner_x = (float)(bounds.w - sw);
    ctx.rt->DrawLine(D2D1::Point2F(spinner_x, 1.0f),
                     D2D1::Point2F(spinner_x, (float)bounds.h - 1.0f),
                     ctx.get_brush(t->border_default), 1.0f);
    ctx.rt->DrawLine(D2D1::Point2F(spinner_x, (float)bounds.h * 0.5f),
                     D2D1::Point2F((float)bounds.w - 1.0f, (float)bounds.h * 0.5f),
                     ctx.get_brush(t->border_default), 1.0f);

    D2D1_RECT_F up_rect = { spinner_x + 1.0f, 1.0f, (float)bounds.w - 1.0f, (float)bounds.h * 0.5f };
    D2D1_RECT_F down_rect = { spinner_x + 1.0f, (float)bounds.h * 0.5f, (float)bounds.w - 1.0f, (float)bounds.h - 1.0f };
    if (enabled && (m_hover_part == PartUp || m_press_part == PartUp)) {
        ctx.rt->FillRectangle(up_rect, ctx.get_brush(m_press_part == PartUp ? t->button_press : t->button_hover));
    }
    if (enabled && (m_hover_part == PartDown || m_press_part == PartDown)) {
        ctx.rt->FillRectangle(down_rect, ctx.get_brush(m_press_part == PartDown ? t->button_press : t->button_hover));
    }

    float label_w = text.empty() ? 0.0f : (float)((std::min)(round_px(bounds.w * 0.34f), round_px(120.0f * style.font_size / 14.0f)));
    float pad_l = (float)style.pad_left;
    float pad_r = (float)style.pad_right;
    if (!text.empty()) {
        draw_text(ctx, text, style, t->text_secondary, pad_l, 0.0f, label_w, (float)bounds.h);
    }

    float value_x = pad_l + label_w + (label_w > 0.0f ? 6.0f : 0.0f);
    float value_w = spinner_x - value_x - pad_r;
    if (value_w < 1.0f) value_w = 1.0f;
    draw_text(ctx, display_value(), style, fg, value_x, 0.0f, value_w, (float)bounds.h,
              DWRITE_TEXT_ALIGNMENT_CENTER);

    Color arrow = (m_hover_part == PartUp || m_hover_part == PartDown) ? t->accent : t->text_secondary;
    draw_text(ctx, L"▲", style, arrow, spinner_x, 0.0f, (float)sw, (float)bounds.h * 0.5f,
              DWRITE_TEXT_ALIGNMENT_CENTER);
    draw_text(ctx, L"▼", style, arrow, spinner_x, (float)bounds.h * 0.5f, (float)sw, (float)bounds.h * 0.5f,
              DWRITE_TEXT_ALIGNMENT_CENTER);

    ctx.rt->SetTransform(saved);
}

void InputNumber::on_mouse_move(int x, int y) {
    if (!enabled) return;
    Part p = part_at(x, y);
    if (p != m_hover_part) {
        m_hover_part = p;
        invalidate();
    }
}

void InputNumber::on_mouse_down(int x, int y, MouseButton) {
    if (!enabled) return;
    m_press_part = part_at(x, y);
    if (m_press_part == PartMain && !m_editing) start_edit();
    if (m_press_part == PartUp) {
        step_by(step);
        m_spun_on_press = true;
        start_repeat(step);
    } else if (m_press_part == PartDown) {
        step_by(-step);
        m_spun_on_press = true;
        start_repeat(-step);
    } else {
        m_spun_on_press = false;
    }
    invalidate();
}

void InputNumber::on_mouse_up(int x, int y, MouseButton) {
    Part release_part = part_at(x, y);
    if (!m_spun_on_press && m_press_part == release_part) {
        if (release_part == PartUp) step_by(step);
        else if (release_part == PartDown) step_by(-step);
    }
    m_press_part = PartNone;
    m_spun_on_press = false;
    stop_repeat();
    invalidate();
}

void InputNumber::on_key_down(int vk, int) {
    if (!enabled) return;
    switch (vk) {
    case VK_UP:
    case VK_RIGHT:
        step_by(step);
        break;
    case VK_DOWN:
    case VK_LEFT:
        step_by(-step);
        break;
    case VK_PRIOR:
        step_by(step * 10);
        break;
    case VK_NEXT:
        step_by(-step * 10);
        break;
    case VK_HOME:
        set_value(min_value);
        break;
    case VK_END:
        set_value(max_value);
        break;
    case VK_RETURN:
        commit_edit();
        break;
    case VK_ESCAPE:
        m_editing = false;
        m_edit_buffer = format_value(value);
        last_input_valid = true;
        invalidate();
        break;
    case VK_BACK:
        if (m_editing) {
            if (m_replace_on_next_char) {
                m_edit_buffer.clear();
                m_replace_on_next_char = false;
            } else if (!m_edit_buffer.empty()) {
                m_edit_buffer.pop_back();
            }
            int parsed = value;
            if (parse_edit_buffer(parsed)) {
                set_value(parsed);
                last_input_valid = true;
            } else {
                last_input_valid = false;
            }
            invalidate();
        }
        break;
    default:
        break;
    }
}

void InputNumber::on_char(wchar_t ch) {
    if (!enabled) return;
    if (!m_editing) start_edit();
    if (ch == L'-' && min_value < 0) {
        if (m_replace_on_next_char) {
            m_edit_buffer.clear();
            m_replace_on_next_char = false;
        }
        if (m_edit_buffer.empty()) m_edit_buffer.push_back(ch);
    } else if (ch == L'.' && precision > 0) {
        if (m_replace_on_next_char) {
            m_edit_buffer.clear();
            m_replace_on_next_char = false;
        }
        if (m_edit_buffer.find(L'.') == std::wstring::npos) {
            if (m_edit_buffer.empty() || m_edit_buffer == L"-") m_edit_buffer += L"0";
            m_edit_buffer.push_back(ch);
        }
    } else if (iswdigit(ch)) {
        if (m_replace_on_next_char) {
            m_edit_buffer.clear();
            m_replace_on_next_char = false;
        }
        m_edit_buffer.push_back(ch);
    } else {
        return;
    }

    int parsed = value;
    if (parse_edit_buffer(parsed)) {
        set_value(parsed);
        last_input_valid = true;
    } else {
        last_input_valid = false;
    }
    invalidate();
}

void InputNumber::on_focus() {
    if (!enabled) return;
    has_focus = true;
    start_edit();
}

void InputNumber::on_blur() {
    has_focus = false;
    stop_repeat();
    commit_edit();
}
