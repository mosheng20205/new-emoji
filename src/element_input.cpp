#include "element_input.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <vector>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static int scale_int_value(int value, float scale) {
    return (int)std::lround((float)value * scale);
}

static float scale_float_value(float value, float scale) {
    return value * scale;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT valign = DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                      bool wrap = false) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(valign);
    layout->SetWordWrapping(wrap ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static float measure_text_width_for_hit(const std::wstring& text, const ElementStyle& style) {
    if (!g_dwrite_factory || text.empty()) return 0.0f;
    IDWriteTextFormat* fmt = nullptr;
    HRESULT hr = g_dwrite_factory->CreateTextFormat(
        style.font_name.c_str(), nullptr,
        DWRITE_FONT_WEIGHT_NORMAL, DWRITE_FONT_STYLE_NORMAL, DWRITE_FONT_STRETCH_NORMAL,
        style.font_size, L"", &fmt);
    if (FAILED(hr) || !fmt) return 0.0f;

    IDWriteTextLayout* layout = nullptr;
    hr = g_dwrite_factory->CreateTextLayout(
        text.c_str(), static_cast<UINT32>(text.size()),
        fmt, 4096.0f, 512.0f, &layout);
    fmt->Release();
    if (FAILED(hr) || !layout) return 0.0f;

    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    DWRITE_TEXT_METRICS tm{};
    float width = 0.0f;
    if (SUCCEEDED(layout->GetMetrics(&tm))) {
        width = tm.widthIncludingTrailingWhitespace;
    }
    layout->Release();
    return width;
}

void Input::set_value(const std::wstring& next_value) {
    value = next_value;
    if (max_length > 0 && (int)value.size() > max_length) value.resize(max_length);
    m_cursor_pos = (int)value.size();
    clear_selection();
    text = value;
    update_autosize_height();
    invalidate();
    notify_text_changed();
}

void Input::set_placeholder(const std::wstring& next_placeholder) {
    placeholder = next_placeholder;
    update_autosize_height();
    invalidate();
}

void Input::set_affixes(const std::wstring& next_prefix, const std::wstring& next_suffix) {
    prefix = next_prefix;
    suffix = next_suffix;
    invalidate();
}

void Input::set_icons(const std::wstring& next_prefix_icon, const std::wstring& next_suffix_icon) {
    prefix_icon = next_prefix_icon;
    suffix_icon = next_suffix_icon;
    invalidate();
}

void Input::set_clearable(bool next_clearable) {
    clearable = next_clearable;
    invalidate();
}

void Input::set_options(bool next_readonly, bool next_password, bool next_multiline, int next_validate_state) {
    readonly = next_readonly;
    password = next_password;
    multiline = next_multiline;
    validate_state = (std::max)(0, (std::min)(3, next_validate_state));
    if (!password) {
        m_password_visible = false;
        m_press_password_toggle = false;
    }
    update_autosize_height();
    invalidate();
}

void Input::set_visual_options(int next_size, bool next_show_password_toggle,
                               bool next_show_word_limit, bool next_autosize,
                               int next_min_rows, int next_max_rows) {
    if (next_size < 0) next_size = 0;
    if (next_size > 3) next_size = 3;
    size = next_size;
    show_password_toggle = next_show_password_toggle;
    show_word_limit = next_show_word_limit;
    autosize = next_autosize;
    min_rows = (std::max)(0, next_min_rows);
    max_rows = (std::max)(0, next_max_rows);
    if (max_rows > 0 && min_rows > max_rows) min_rows = max_rows;
    apply_size_preset();
    update_autosize_height();
    invalidate();
}

void Input::set_max_length(int next_max_length) {
    max_length = (std::max)(0, next_max_length);
    if (max_length > 0 && (int)value.size() > max_length) {
        value.resize(max_length);
        if (m_cursor_pos > (int)value.size()) m_cursor_pos = (int)value.size();
        if (m_sel_start > (int)value.size()) m_sel_start = (int)value.size();
        if (m_sel_end > (int)value.size()) m_sel_end = (int)value.size();
        text = value;
        notify_text_changed();
    }
    invalidate();
}

void Input::set_context_menu_enabled(bool next_enabled) {
    context_menu_enabled = next_enabled;
    invalidate();
}

void Input::set_selection(int start, int end) {
    int len = (int)value.size();
    if (start < 0) start = 0;
    if (end < 0) end = 0;
    if (start > len) start = len;
    if (end > len) end = len;
    m_cursor_pos = end;
    if (start == end) {
        clear_selection();
    } else {
        m_sel_start = start;
        m_sel_end = end;
        m_select_anchor = start;
    }
    invalidate();
}

void Input::get_selection(int& start, int& end) const {
    if (!has_selection()) {
        start = m_cursor_pos;
        end = m_cursor_pos;
        return;
    }
    normalized_selection(start, end);
}

void Input::get_state(int& cursor, int& length) const {
    cursor = m_cursor_pos;
    length = (int)value.size();
}

std::wstring Input::display_text() const {
    if (value.empty()) return placeholder;
    if (password && !m_password_visible) {
        return std::wstring(value.size(), L'*');
    }
    return value;
}

std::wstring Input::word_limit_text() const {
    int length = (int)value.size();
    if (max_length > 0) return std::to_wstring(length) + L"/" + std::to_wstring(max_length);
    return std::to_wstring(length);
}

int Input::effective_rows() const {
    std::wstring content = value.empty() ? placeholder : value;
    if (content.empty()) return 1;

    int rows = 1;
    int max_line_len = 0;
    int current_len = 0;
    for (wchar_t ch : content) {
        if (ch == L'\n') {
            ++rows;
            max_line_len = (std::max)(max_line_len, current_len);
            current_len = 0;
        } else {
            ++current_len;
        }
    }
    max_line_len = (std::max)(max_line_len, current_len);

    int available_width = bounds.w - style.pad_left - style.pad_right;
    LayoutMetrics metrics = compute_metrics();
    available_width = (int)std::lround(metrics.text_w);
    int approx_chars_per_line = (std::max)(1, available_width / (std::max)(6, char_width()));
    if (approx_chars_per_line > 0) {
        int wrapped_rows = 0;
        current_len = 0;
        for (wchar_t ch : content) {
            if (ch == L'\n') {
                wrapped_rows += (std::max)(1, (current_len + approx_chars_per_line - 1) / approx_chars_per_line);
                current_len = 0;
            } else {
                ++current_len;
            }
        }
        wrapped_rows += (std::max)(1, (current_len + approx_chars_per_line - 1) / approx_chars_per_line);
        rows = (std::max)(rows, wrapped_rows);
    }

    if (min_rows > 0) rows = (std::max)(rows, min_rows);
    if (max_rows > 0) rows = (std::min)(rows, max_rows);
    if (rows < 1) rows = 1;
    return rows;
}

int Input::autosize_height_for_width(int) const {
    int rows = effective_rows();
    float line_h = style.font_size * 1.45f;
    int text_height = (int)std::lround(line_h * rows);
    int counter_h = show_word_limit ? (int)std::lround(style.font_size + 8.0f) : 0;
    int result = style.pad_top + text_height + style.pad_bottom + counter_h + 10;
    int minimum = size == 3 ? 28 : (size == 2 ? 32 : 36);
    if (result < minimum) result = minimum;
    return result;
}

void Input::apply_size_preset() {
    if (!has_logical_style) return;
    ElementStyle preset = logical_style;
    preset.corner_radius = 4.0f;
    if (size == 3) {
        preset.font_size = 12.0f;
        preset.pad_left = 8;
        preset.pad_right = 8;
        preset.pad_top = multiline ? 6 : 0;
        preset.pad_bottom = multiline ? 6 : 0;
    } else if (size == 2) {
        preset.font_size = 13.0f;
        preset.pad_left = 10;
        preset.pad_right = 10;
        preset.pad_top = multiline ? 7 : 0;
        preset.pad_bottom = multiline ? 7 : 0;
    } else {
        preset.font_size = 14.0f;
        preset.pad_left = 12;
        preset.pad_right = 12;
        preset.pad_top = multiline ? 8 : 0;
        preset.pad_bottom = multiline ? 8 : 0;
    }
    logical_style = preset;
    float scale = 1.0f;
    if (has_logical_bounds) {
        if (logical_bounds.w > 0 && bounds.w > 0) {
            scale = (float)bounds.w / (float)logical_bounds.w;
        } else if (logical_bounds.h > 0 && bounds.h > 0) {
            scale = (float)bounds.h / (float)logical_bounds.h;
        }
    }
    style = preset;
    style.border_width = scale_float_value(preset.border_width, scale);
    style.corner_radius = scale_float_value(preset.corner_radius, scale);
    style.pad_left = scale_int_value(preset.pad_left, scale);
    style.pad_top = scale_int_value(preset.pad_top, scale);
    style.pad_right = scale_int_value(preset.pad_right, scale);
    style.pad_bottom = scale_int_value(preset.pad_bottom, scale);
    style.font_size = scale_float_value(preset.font_size, scale);
}

void Input::update_autosize_height() {
    if (!(autosize && multiline)) return;
    if (bounds.w <= 0) return;
    bounds.h = autosize_height_for_width(bounds.w);
}

void Input::layout(const Rect& available) {
    bounds = available;
    apply_size_preset();
    if (autosize && multiline) {
        bounds.h = autosize_height_for_width(bounds.w);
    }
}

Input::LayoutMetrics Input::compute_metrics() const {
    LayoutMetrics m{};
    float x = (float)style.pad_left;
    float inner_h = (float)bounds.h;
    float icon_gap = 8.0f;

    if (!prefix_icon.empty()) {
        m.prefix_icon_w = measure_text_width_for_hit(prefix_icon, style) + 4.0f;
        m.prefix_icon_x = x;
        x += m.prefix_icon_w + icon_gap;
    }
    if (!prefix.empty()) {
        m.prefix_text_w = measure_text_width_for_hit(prefix, style) + 4.0f;
        m.prefix_text_x = x;
        x += m.prefix_text_w + icon_gap;
    }

    float right = (float)bounds.w - (float)style.pad_right;
    m.show_word_limit = show_word_limit && (max_length > 0 || !value.empty() || multiline);
    if (m.show_word_limit) {
        m.word_limit_w = measure_text_width_for_hit(word_limit_text(), style) + 6.0f;
        m.word_limit_x = right - m.word_limit_w;
        right -= m.word_limit_w + 8.0f;
    }

    m.show_clear = clearable && !value.empty() && enabled && !readonly;
    if (m.show_clear) {
        int clear_size = (std::min)(22, (std::max)(16, bounds.h - 14));
        m.clear_rect = { (int)std::lround(right - clear_size), (bounds.h - clear_size) / 2, clear_size, clear_size };
        right = (float)m.clear_rect.x - 8.0f;
    }

    m.show_password_toggle = password && show_password_toggle;
    if (m.show_password_toggle) {
        float pw = measure_text_width_for_hit(m_password_visible ? L"🙈" : L"👁", style) + 8.0f;
        int w = (int)std::lround((std::max)(18.0f, pw));
        m.password_rect = { (int)std::lround(right - w), (bounds.h - 20) / 2, w, 20 };
        right = (float)m.password_rect.x - 8.0f;
    }

    m.show_suffix_icon = !suffix_icon.empty();
    if (m.show_suffix_icon) {
        m.suffix_icon_w = measure_text_width_for_hit(suffix_icon, style) + 4.0f;
        m.suffix_icon_x = right - m.suffix_icon_w;
        m.suffix_icon_rect = {
            (int)std::lround(m.suffix_icon_x),
            (bounds.h - (int)std::lround(style.font_size + 6.0f)) / 2,
            (int)std::lround(m.suffix_icon_w),
            (int)std::lround(style.font_size + 6.0f)
        };
        right = m.suffix_icon_x - icon_gap;
    }

    if (!suffix.empty()) {
        m.suffix_text_w = measure_text_width_for_hit(suffix, style) + 4.0f;
        m.suffix_text_x = right - m.suffix_text_w;
        right = m.suffix_text_x - icon_gap;
    }

    m.text_x = x;
    m.text_y = multiline ? (float)style.pad_top : 0.0f;
    m.text_h = multiline
        ? (float)bounds.h - (float)style.pad_top - (float)style.pad_bottom - (m.show_word_limit ? style.font_size + 8.0f : 0.0f)
        : inner_h;
    if (m.text_h < style.font_size + 4.0f) m.text_h = style.font_size + 4.0f;
    m.text_w = right - x;
    if (m.text_w < 1.0f) m.text_w = 1.0f;
    return m;
}

int Input::char_width() const {
    int cw = (int)(style.font_size * 0.62f + 0.5f);
    return cw < 6 ? 6 : cw;
}

int Input::xpos_to_char(int x) const {
    LayoutMetrics metrics = compute_metrics();
    float local_x = (float)x - metrics.text_x;
    if (local_x <= 0.0f || value.empty()) return 0;
    int idx = (int)((local_x + char_width() / 2.0f) / (float)char_width());
    if (idx < 0) idx = 0;
    if (idx > (int)value.size()) idx = (int)value.size();
    return idx;
}

int Input::char_to_xpos(int index) const {
    LayoutMetrics metrics = compute_metrics();
    if (index < 0) index = 0;
    if (index > (int)value.size()) index = (int)value.size();
    return (int)std::lround(metrics.text_x + index * char_width());
}

bool Input::has_selection() const {
    return m_sel_start >= 0 && m_sel_end >= 0 && m_sel_start != m_sel_end;
}

void Input::normalized_selection(int& start, int& end) const {
    start = m_sel_start;
    end = m_sel_end;
    if (start > end) std::swap(start, end);
    int len = (int)value.size();
    if (start < 0) start = 0;
    if (end < 0) end = 0;
    if (start > len) start = len;
    if (end > len) end = len;
}

void Input::clear_selection() {
    m_sel_start = -1;
    m_sel_end = -1;
}

void Input::delete_selection() {
    if (!has_selection()) return;
    int start = 0;
    int end = 0;
    normalized_selection(start, end);
    if (end <= start) {
        clear_selection();
        return;
    }
    value.erase(start, end - start);
    m_cursor_pos = start;
    clear_selection();
    text = value;
    update_autosize_height();
    invalidate();
    notify_text_changed();
}

void Input::select_all() {
    m_cursor_pos = (int)value.size();
    if (value.empty()) {
        clear_selection();
    } else {
        m_sel_start = 0;
        m_sel_end = (int)value.size();
        m_select_anchor = 0;
    }
    invalidate();
}

void Input::move_cursor_to(int pos, bool extend) {
    int len = (int)value.size();
    if (pos < 0) pos = 0;
    if (pos > len) pos = len;
    if (extend) {
        if (!has_selection()) m_select_anchor = m_cursor_pos;
        m_cursor_pos = pos;
        m_sel_start = m_select_anchor;
        m_sel_end = m_cursor_pos;
        if (m_sel_start == m_sel_end) clear_selection();
    } else {
        m_cursor_pos = pos;
        clear_selection();
        m_select_anchor = m_cursor_pos;
    }
}

std::wstring Input::selected_text() const {
    if (!has_selection()) return L"";
    int start = 0;
    int end = 0;
    normalized_selection(start, end);
    if (end <= start) return L"";
    return value.substr(start, end - start);
}

void Input::copy_selection_to_clipboard() const {
    if (password && !m_password_visible) return;
    std::wstring sel = selected_text();
    if (sel.empty()) return;
    if (!OpenClipboard(owner_hwnd)) return;
    EmptyClipboard();
    size_t bytes = (sel.size() + 1) * sizeof(wchar_t);
    HGLOBAL mem = GlobalAlloc(GMEM_MOVEABLE, bytes);
    if (mem) {
        void* ptr = GlobalLock(mem);
        if (ptr) {
            memcpy(ptr, sel.c_str(), bytes);
            GlobalUnlock(mem);
            SetClipboardData(CF_UNICODETEXT, mem);
            mem = nullptr;
        }
        if (mem) GlobalFree(mem);
    }
    CloseClipboard();
}

void Input::cut_selection_to_clipboard() {
    if (readonly || !enabled || !has_selection()) return;
    if (password && !m_password_visible) return;
    copy_selection_to_clipboard();
    delete_selection();
}

void Input::paste_from_clipboard() {
    if (readonly || !enabled) return;
    if (!OpenClipboard(owner_hwnd)) return;
    HANDLE data = GetClipboardData(CF_UNICODETEXT);
    if (data) {
        wchar_t* text_ptr = (wchar_t*)GlobalLock(data);
        if (text_ptr) {
            insert_text(text_ptr);
            GlobalUnlock(data);
        }
    }
    CloseClipboard();
}

void Input::show_context_menu(int x, int y) {
    if (!context_menu_enabled || !owner_hwnd) return;
    HMENU menu = CreatePopupMenu();
    if (!menu) return;

    bool can_copy = has_selection() && !(password && !m_password_visible);
    bool can_edit = enabled && !readonly;
    AppendMenuW(menu, can_copy ? MF_STRING : (MF_STRING | MF_GRAYED), 1, L"复制");
    AppendMenuW(menu, (can_copy && can_edit) ? MF_STRING : (MF_STRING | MF_GRAYED), 2, L"剪切");
    AppendMenuW(menu, can_edit ? MF_STRING : (MF_STRING | MF_GRAYED), 3, L"粘贴");
    AppendMenuW(menu, MF_SEPARATOR, 0, nullptr);
    AppendMenuW(menu, value.empty() ? (MF_STRING | MF_GRAYED) : MF_STRING, 4, L"全选");

    int abs_x = 0;
    int abs_y = 0;
    get_absolute_pos(abs_x, abs_y);
    POINT pt{ abs_x + x, abs_y + y };
    ClientToScreen(owner_hwnd, &pt);
    SetForegroundWindow(owner_hwnd);
    int cmd = TrackPopupMenu(menu, TPM_RETURNCMD | TPM_RIGHTBUTTON,
                             pt.x, pt.y, 0, owner_hwnd, nullptr);
    DestroyMenu(menu);

    if (cmd == 1) copy_selection_to_clipboard();
    else if (cmd == 2) cut_selection_to_clipboard();
    else if (cmd == 3) paste_from_clipboard();
    else if (cmd == 4) select_all();
}

void Input::insert_text(const std::wstring& s) {
    if (s.empty()) return;
    if (has_selection()) delete_selection();
    if (m_cursor_pos < 0) m_cursor_pos = 0;
    if (m_cursor_pos > (int)value.size()) m_cursor_pos = (int)value.size();
    std::wstring next = s;
    if (max_length > 0) {
        int remaining = max_length - (int)value.size();
        if (remaining <= 0) return;
        if ((int)next.size() > remaining) next.resize(remaining);
    }
    value.insert(m_cursor_pos, next);
    m_cursor_pos += (int)next.size();
    text = value;
    update_autosize_height();
    invalidate();
    notify_text_changed();
}

void Input::delete_char_before() {
    if (has_selection()) {
        delete_selection();
        return;
    }
    if (m_cursor_pos <= 0 || value.empty()) return;
    value.erase(m_cursor_pos - 1, 1);
    --m_cursor_pos;
    text = value;
    update_autosize_height();
    invalidate();
    notify_text_changed();
}

void Input::delete_char_after() {
    if (has_selection()) {
        delete_selection();
        return;
    }
    if (m_cursor_pos < 0 || m_cursor_pos >= (int)value.size()) return;
    value.erase(m_cursor_pos, 1);
    text = value;
    update_autosize_height();
    invalidate();
    notify_text_changed();
}

void Input::notify_text_changed() {
    if (!text_cb) return;
    std::string utf8 = wide_to_utf8(value);
    text_cb(id, reinterpret_cast<const unsigned char*>(utf8.data()), (int)utf8.size());
}

void Input::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool disabled = !enabled;
    Color bg = disabled ? t->button_bg : (style.bg_color ? style.bg_color : t->edit_bg);
    Color border = disabled ? t->border_default : (has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border));
    if (!disabled) {
        if (validate_state == 1) border = 0xFF16A34A;
        else if (validate_state == 2) border = 0xFFE6A23C;
        else if (validate_state == 3) border = 0xFFEF4444;
    }
    Color fg = disabled ? t->text_muted : (style.fg_color ? style.fg_color : t->text_primary);
    Color hint = disabled ? t->text_muted : t->text_secondary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F field = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(field, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), has_focus && !disabled ? 1.5f : 1.0f);

    LayoutMetrics metrics = compute_metrics();
    if (!prefix_icon.empty()) {
        draw_text(ctx, prefix_icon, style, hint, metrics.prefix_icon_x, 0.0f,
                  metrics.prefix_icon_w, (float)bounds.h);
    }
    if (!prefix.empty()) {
        draw_text(ctx, prefix, style, hint, metrics.prefix_text_x, 0.0f,
                  metrics.prefix_text_w, (float)bounds.h);
    }

    std::wstring shown = display_text();
    bool showing_placeholder = value.empty();
    if (!shown.empty() && metrics.text_w > 0.0f && metrics.text_h > 0.0f) {
        auto* layout = ctx.create_text_layout(shown, style.font_name, style.font_size,
                                              metrics.text_w, metrics.text_h);
        if (layout) {
            apply_emoji_font_fallback(layout, shown);
            layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            layout->SetParagraphAlignment(multiline
                ? DWRITE_PARAGRAPH_ALIGNMENT_NEAR
                : DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            layout->SetWordWrapping(multiline ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);

            if (!showing_placeholder && has_selection()) {
                int sel_start = 0;
                int sel_end = 0;
                normalized_selection(sel_start, sel_end);
                UINT32 range_len = (UINT32)(sel_end - sel_start);
                if (range_len > 0) {
                    std::vector<DWRITE_HIT_TEST_METRICS> hit_metrics((std::max)(1u, range_len + 4));
                    UINT32 actual_count = 0;
                    HRESULT hr = layout->HitTestTextRange(
                        (UINT32)sel_start, range_len, 0.0f, 0.0f,
                        hit_metrics.data(), (UINT32)hit_metrics.size(), &actual_count);
                    if (hr == E_NOT_SUFFICIENT_BUFFER && actual_count > hit_metrics.size()) {
                        hit_metrics.resize(actual_count);
                        hr = layout->HitTestTextRange(
                            (UINT32)sel_start, range_len, 0.0f, 0.0f,
                            hit_metrics.data(), (UINT32)hit_metrics.size(), &actual_count);
                    }
                    if (SUCCEEDED(hr)) {
                        Color sel_color = with_alpha(t->accent, 0x66);
                        for (UINT32 i = 0; i < actual_count && i < hit_metrics.size(); ++i) {
                            const auto& hm = hit_metrics[i];
                            D2D1_RECT_F sel_rect = {
                                metrics.text_x + hm.left,
                                metrics.text_y + hm.top,
                                metrics.text_x + hm.left + hm.width,
                                metrics.text_y + hm.top + hm.height
                            };
                            ctx.rt->FillRectangle(sel_rect, ctx.get_brush(sel_color));
                        }
                    }
                }
            }

            ctx.rt->DrawTextLayout(D2D1::Point2F(metrics.text_x, metrics.text_y), layout,
                ctx.get_brush(showing_placeholder ? hint : fg),
                D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    if (has_focus && !disabled && !multiline) {
        std::wstring caret_prefix = display_text();
        if (m_cursor_pos <= 0) {
            caret_prefix.clear();
        } else if (m_cursor_pos < (int)caret_prefix.size()) {
            caret_prefix = caret_prefix.substr(0, m_cursor_pos);
        }
        float caret_x = metrics.text_x + measure_text_width_for_hit(caret_prefix, style);
        if (caret_x < metrics.text_x) caret_x = metrics.text_x;
        if (caret_x > metrics.text_x + metrics.text_w) caret_x = metrics.text_x + metrics.text_w;
        ctx.rt->DrawLine(D2D1::Point2F(caret_x, 8.0f),
                         D2D1::Point2F(caret_x, (float)bounds.h - 8.0f),
                         ctx.get_brush(fg), 1.4f);
    }

    if (!suffix.empty()) {
        draw_text(ctx, suffix, style, hint, metrics.suffix_text_x, 0.0f,
                  metrics.suffix_text_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_TRAILING);
    }
    if (metrics.show_suffix_icon) {
        draw_text(ctx, suffix_icon, style, hint, metrics.suffix_icon_x, 0.0f,
                  metrics.suffix_icon_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    if (metrics.show_password_toggle) {
        draw_text(ctx, m_password_visible ? L"🙈" : L"👁", style,
                  disabled ? t->text_muted : hint,
                  (float)metrics.password_rect.x, 0.0f,
                  (float)metrics.password_rect.w, (float)bounds.h,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    if (metrics.show_clear) {
        D2D1_ELLIPSE ellipse = D2D1::Ellipse(
            D2D1::Point2F((float)metrics.clear_rect.x + metrics.clear_rect.w * 0.5f,
                          (float)metrics.clear_rect.y + metrics.clear_rect.h * 0.5f),
            metrics.clear_rect.w * 0.5f, metrics.clear_rect.h * 0.5f);
        ctx.rt->FillEllipse(ellipse, ctx.get_brush(with_alpha(t->text_secondary, hovered ? 0x66 : 0x44)));
        draw_text(ctx, L"×", style, bg,
                  (float)metrics.clear_rect.x, (float)metrics.clear_rect.y,
                  (float)metrics.clear_rect.w, (float)metrics.clear_rect.h,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    if (metrics.show_word_limit) {
        float y = multiline ? (float)bounds.h - style.pad_bottom - style.font_size - 4.0f : 0.0f;
        draw_text(ctx, word_limit_text(), style, hint,
                  metrics.word_limit_x, y,
                  metrics.word_limit_w, multiline ? style.font_size + 8.0f : (float)bounds.h,
                  DWRITE_TEXT_ALIGNMENT_TRAILING,
                  multiline ? DWRITE_PARAGRAPH_ALIGNMENT_NEAR : DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    }

    ctx.rt->SetTransform(saved);
}

void Input::on_mouse_down(int x, int y, MouseButton btn) {
    if (!enabled) return;
    if (btn != MouseButton::Left) return;
    LayoutMetrics metrics = compute_metrics();
    m_press_clear = !readonly && metrics.show_clear && metrics.clear_rect.contains(x, y);
    m_press_password_toggle = metrics.show_password_toggle && metrics.password_rect.contains(x, y);
    pressed = true;
    if (!m_press_clear && !m_press_password_toggle) {
        m_cursor_pos = xpos_to_char(x);
        m_select_anchor = m_cursor_pos;
        m_drag_selecting = true;
        clear_selection();
    }
    invalidate();
}

void Input::on_mouse_up(int x, int y, MouseButton btn) {
    if (btn == MouseButton::Right) {
        if (enabled && context_menu_enabled) {
            if (!has_selection()) {
                m_cursor_pos = xpos_to_char(x);
                m_select_anchor = m_cursor_pos;
            }
            show_context_menu(x, y);
            invalidate();
        }
        return;
    }
    LayoutMetrics metrics = compute_metrics();
    if (m_press_clear && metrics.clear_rect.contains(x, y)) {
        set_value(L"");
        m_cursor_pos = 0;
    } else if (m_press_password_toggle && metrics.password_rect.contains(x, y)) {
        m_password_visible = !m_password_visible;
    }
    m_press_clear = false;
    m_press_password_toggle = false;
    m_drag_selecting = false;
    pressed = false;
    invalidate();
}

void Input::on_mouse_move(int x, int) {
    if (!enabled || !m_drag_selecting) return;
    int pos = xpos_to_char(x);
    m_cursor_pos = pos;
    m_sel_start = m_select_anchor;
    m_sel_end = pos;
    if (m_sel_start == m_sel_end) clear_selection();
    invalidate();
}

void Input::on_key_down(int vk, int mods) {
    if (!enabled) return;
    bool shift = (mods & KeyMod::Shift) != 0;
    bool ctrl = (mods & KeyMod::Control) != 0;
    if (ctrl) {
        if (vk == 'A') {
            select_all();
            return;
        }
        if (vk == 'C') {
            copy_selection_to_clipboard();
            invalidate();
            return;
        }
        if (vk == 'X') {
            cut_selection_to_clipboard();
            return;
        }
        if (vk == 'V') {
            paste_from_clipboard();
            return;
        }
    }
    if (vk == VK_LEFT) {
        if (!shift && has_selection()) {
            int start = 0, end = 0;
            normalized_selection(start, end);
            move_cursor_to(start, false);
        } else {
            move_cursor_to(m_cursor_pos - 1, shift);
        }
    } else if (vk == VK_RIGHT) {
        if (!shift && has_selection()) {
            int start = 0, end = 0;
            normalized_selection(start, end);
            move_cursor_to(end, false);
        } else {
            move_cursor_to(m_cursor_pos + 1, shift);
        }
    } else if (vk == VK_HOME) {
        move_cursor_to(0, shift);
    } else if (vk == VK_END) {
        move_cursor_to((int)value.size(), shift);
    } else if (readonly) {
        // Navigation and selection are allowed on readonly inputs, editing is not.
    } else if (vk == VK_BACK) {
        delete_char_before();
    } else if (vk == VK_DELETE) {
        delete_char_after();
    }
    invalidate();
}

void Input::on_char(wchar_t ch) {
    if (!enabled || readonly) return;
    if (ch == L'\r' || ch == L'\n') {
        if (multiline) insert_text(L"\n");
        return;
    }
    if (ch < 32) return;
    insert_text(std::wstring(1, ch));
}

void Input::on_focus() {
    has_focus = true;
    if (m_cursor_pos > (int)value.size()) m_cursor_pos = (int)value.size();
    invalidate();
}

void Input::on_blur() {
    has_focus = false;
    pressed = false;
    m_press_clear = false;
    m_press_password_toggle = false;
    m_drag_selecting = false;
    invalidate();
}
