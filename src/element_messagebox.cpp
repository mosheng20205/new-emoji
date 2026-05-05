#include "element_messagebox.h"
#include "emoji_fallback.h"
#include "element_rich_text.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <map>
#include <regex>
#include <vector>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

std::map<UINT_PTR, MessageBoxElement*> g_messagebox_timer_map;

static int round_px(float v) {
    return (int)std::lround(v);
}

static bool contains_rect(const Rect& r, int x, int y) {
    return x >= r.x && x < r.x + r.w && y >= r.y && y < r.y + r.h;
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static bool is_high_surrogate(wchar_t ch) {
    return ch >= 0xD800 && ch <= 0xDBFF;
}

static bool is_low_surrogate(wchar_t ch) {
    return ch >= 0xDC00 && ch <= 0xDFFF;
}

static IDWriteTextLayout* create_hit_text_layout(const std::wstring& text,
                                                 const ElementStyle& style,
                                                 float width, float height) {
    if (!g_dwrite_factory || width <= 0.0f || height <= 0.0f) return nullptr;
    IDWriteTextFormat* fmt = nullptr;
    HRESULT hr = g_dwrite_factory->CreateTextFormat(
        style.font_name.c_str(), nullptr,
        DWRITE_FONT_WEIGHT_NORMAL, DWRITE_FONT_STYLE_NORMAL, DWRITE_FONT_STRETCH_NORMAL,
        style.font_size, L"", &fmt);
    if (FAILED(hr) || !fmt) return nullptr;

    IDWriteTextLayout* layout = nullptr;
    hr = g_dwrite_factory->CreateTextLayout(
        text.c_str(), static_cast<UINT32>(text.size()), fmt, width, height, &layout);
    fmt->Release();
    if (FAILED(hr) || !layout) return nullptr;

    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    return layout;
}

static float measure_text_width_for_hit(const std::wstring& text, const ElementStyle& style) {
    if (text.empty()) return 0.0f;
    IDWriteTextLayout* layout = create_hit_text_layout(text, style, 4096.0f, 512.0f);
    if (!layout) return 0.0f;
    DWRITE_TEXT_METRICS tm{};
    float width = 0.0f;
    if (SUCCEEDED(layout->GetMetrics(&tm))) {
        width = tm.widthIncludingTrailingWhitespace;
    }
    layout->Release();
    return width;
}

static Color feedback_color(const Theme* t, int type) {
    switch (type) {
    case 1: return 0xFF67C23A;
    case 2: return 0xFFE6A23C;
    case 3: return 0xFFF56C6C;
    default: return t->accent;
    }
}

static std::wstring feedback_icon(int type) {
    switch (type) {
    case 1: return L"✓";
    case 2: return L"!";
    case 3: return L"×";
    default: return L"i";
    }
}

MessageBoxElement::~MessageBoxElement() {
    stop_timer();
}

float MessageBoxElement::scale() const {
    float s = style.font_size / 14.0f;
    if (s < 0.75f) s = 0.75f;
    return s;
}

void MessageBoxElement::layout(const Rect& available) {
    bounds = available;
    update_layout();
}

void MessageBoxElement::update_layout() {
    float s = scale();
    int margin = round_px(24.0f * s);
    int dialog_w = round_px(420.0f * s);
    int dialog_h = round_px((prompt ? 284.0f : 220.0f) * s);
    int min_w = round_px(280.0f * s);

    int max_w = bounds.w - margin * 2;
    if (max_w < min_w) max_w = bounds.w > 0 ? bounds.w : min_w;
    if (max_w < dialog_w) dialog_w = max_w;
    if (dialog_w < min_w && bounds.w >= min_w) dialog_w = min_w;
    if (dialog_w > bounds.w) dialog_w = bounds.w;

    int max_h = bounds.h - margin * 2;
    if (max_h > 0 && max_h < dialog_h) dialog_h = max_h;
    if (dialog_h > bounds.h) dialog_h = bounds.h;

    m_dialog_rect = {
        (bounds.w - dialog_w) / 2,
        (bounds.h - dialog_h) / 2,
        dialog_w,
        dialog_h
    };
    if (m_dialog_rect.x < 0) m_dialog_rect.x = 0;
    if (m_dialog_rect.y < 0) m_dialog_rect.y = 0;

    int pad = round_px(20.0f * s);
    int close_size = round_px(28.0f * s);
    m_close_rect = {
        m_dialog_rect.x + m_dialog_rect.w - pad - close_size + round_px(4.0f * s),
        m_dialog_rect.y + round_px(14.0f * s),
        close_size,
        close_size
    };

    int button_w = round_px(88.0f * s);
    int button_h = round_px(32.0f * s);
    int gap = round_px(10.0f * s);
    int bottom = m_dialog_rect.y + m_dialog_rect.h - pad - button_h;
    int right = m_dialog_rect.x + m_dialog_rect.w - pad;
    m_confirm_rect = { right - button_w, bottom, button_w, button_h };
    m_cancel_rect = show_cancel
        ? Rect{ m_confirm_rect.x - gap - button_w, bottom, button_w, button_h }
        : Rect{ 0, 0, 0, 0 };
    m_input_rect = prompt
        ? Rect{ m_dialog_rect.x + pad, m_confirm_rect.y - round_px(62.0f * s),
                m_dialog_rect.w - pad * 2, round_px(34.0f * s) }
        : Rect{ 0, 0, 0, 0 };
}

MessageBoxElement::Part MessageBoxElement::part_at(int x, int y) const {
    if (contains_rect(m_close_rect, x, y)) return PartClose;
    if (contains_rect(m_confirm_rect, x, y)) return PartConfirm;
    if (show_cancel && contains_rect(m_cancel_rect, x, y)) return PartCancel;
    return PartNone;
}

void MessageBoxElement::request_result(Result result) {
    if (m_close_requested || !owner_hwnd) return;
    if (confirm_loading) return;
    last_action = (int)result;
    if (result == ResultConfirm && prompt && !validate_prompt()) {
        invalidate();
        return;
    }
    if (result == ResultConfirm && before_close_delay_ms > 0 && !confirm_loading) {
        start_before_close();
        return;
    }
    m_close_requested = true;
    PostMessageW(owner_hwnd, WM_USER + 110, (WPARAM)id, (LPARAM)result);
}

bool MessageBoxElement::validate_prompt() {
    if (!prompt || input_pattern.empty()) return true;
    try {
        std::wregex re(input_pattern);
        if (std::regex_match(input_value, re)) {
            input_error_visible = false;
            return true;
        }
    } catch (...) {
        return true;
    }
    if (input_error.empty()) input_error = L"输入内容格式不正确";
    input_error_visible = true;
    return false;
}

void MessageBoxElement::set_before_close(int delay_ms, const std::wstring& loading) {
    before_close_delay_ms = (std::max)(0, delay_ms);
    loading_text = loading;
    invalidate();
}

void MessageBoxElement::set_input(const std::wstring& value, const std::wstring& placeholder,
                                  const std::wstring& pattern, const std::wstring& error) {
    input_value = value;
    input_placeholder = placeholder;
    input_pattern = pattern;
    input_error = error;
    input_error_visible = false;
    prompt = true;
    m_input_cursor_pos = (int)input_value.size();
    m_input_select_anchor = m_input_cursor_pos;
    clear_input_selection();
    m_input_focused = has_focus || m_input_focused;
    invalidate();
}

void MessageBoxElement::set_options(int type, bool centered, bool rich_text, bool distinguish) {
    box_type = (std::max)(0, (std::min)(3, type));
    center = centered;
    rich = rich_text;
    distinguish_cancel_and_close = distinguish;
    invalidate();
}

void MessageBoxElement::start_before_close() {
    if (!owner_hwnd) return;
    confirm_loading = true;
    timer_elapsed_ms = 0;
    m_timer_id = 0xF000 + (UINT_PTR)id;
    SetTimer(owner_hwnd, m_timer_id, 50, nullptr);
    g_messagebox_timer_map[m_timer_id] = this;
    invalidate();
}

void MessageBoxElement::tick(int elapsed_ms) {
    if (!confirm_loading) return;
    timer_elapsed_ms += (std::max)(1, elapsed_ms);
    if (timer_elapsed_ms >= before_close_delay_ms) {
        stop_timer();
        confirm_loading = false;
        m_close_requested = true;
        PostMessageW(owner_hwnd, WM_USER + 110, (WPARAM)id, (LPARAM)ResultConfirm);
    } else {
        invalidate();
    }
}

void MessageBoxElement::stop_timer() {
    if (m_timer_id && owner_hwnd) KillTimer(owner_hwnd, m_timer_id);
    if (m_timer_id) g_messagebox_timer_map.erase(m_timer_id);
    m_timer_id = 0;
}

bool MessageBoxElement::wants_text_cursor_at(int x, int y) const {
    return prompt && !confirm_loading && contains_rect(m_input_rect, x, y);
}

void MessageBoxElement::input_text_rect(float& x, float& y, float& w, float& h) const {
    float s = scale();
    x = (float)m_input_rect.x + 10.0f * s;
    y = (float)m_input_rect.y;
    w = (float)m_input_rect.w - 20.0f * s;
    h = (float)m_input_rect.h;
    if (w < 1.0f) w = 1.0f;
    if (h < 1.0f) h = 1.0f;
}

int MessageBoxElement::clamp_input_pos(int pos) const {
    int len = (int)input_value.size();
    if (pos < 0) pos = 0;
    if (pos > len) pos = len;
    if (pos > 0 && pos < len &&
        is_high_surrogate(input_value[(size_t)pos - 1]) &&
        is_low_surrogate(input_value[(size_t)pos])) {
        pos += 1;
    }
    if (pos > len) pos = len;
    return pos;
}

int MessageBoxElement::previous_input_pos(int pos) const {
    pos = clamp_input_pos(pos);
    if (pos <= 0) return 0;
    int prev = pos - 1;
    if (prev > 0 &&
        is_low_surrogate(input_value[(size_t)prev]) &&
        is_high_surrogate(input_value[(size_t)prev - 1])) {
        --prev;
    }
    return prev;
}

int MessageBoxElement::next_input_pos(int pos) const {
    pos = clamp_input_pos(pos);
    int len = (int)input_value.size();
    if (pos >= len) return len;
    int next = pos + 1;
    if (pos + 1 < len &&
        is_high_surrogate(input_value[(size_t)pos]) &&
        is_low_surrogate(input_value[(size_t)pos + 1])) {
        next = pos + 2;
    }
    return next > len ? len : next;
}

int MessageBoxElement::input_x_to_char(int x) const {
    if (input_value.empty()) return 0;

    float text_x = 0.0f, text_y = 0.0f, text_w = 0.0f, text_h = 0.0f;
    input_text_rect(text_x, text_y, text_w, text_h);
    float local_x = (float)x - text_x;
    if (local_x <= 0.0f) return 0;

    float full_w = measure_text_width_for_hit(input_value, style);
    if (local_x >= full_w) return (int)input_value.size();

    IDWriteTextLayout* layout = create_hit_text_layout(input_value, style, text_w, text_h);
    if (!layout) {
        int approx = (int)std::lround(local_x / (style.font_size * 0.62f));
        return clamp_input_pos(approx);
    }

    BOOL trailing = FALSE;
    BOOL inside = FALSE;
    DWRITE_HIT_TEST_METRICS hm{};
    int pos = 0;
    if (SUCCEEDED(layout->HitTestPoint(local_x, text_h * 0.5f, &trailing, &inside, &hm))) {
        pos = (int)hm.textPosition + (trailing ? (int)hm.length : 0);
    }
    layout->Release();
    return clamp_input_pos(pos);
}

float MessageBoxElement::input_char_to_x(int index) const {
    float text_x = 0.0f, text_y = 0.0f, text_w = 0.0f, text_h = 0.0f;
    input_text_rect(text_x, text_y, text_w, text_h);
    index = clamp_input_pos(index);
    if (index <= 0 || input_value.empty()) return text_x;

    IDWriteTextLayout* layout = create_hit_text_layout(input_value, style, text_w, text_h);
    if (!layout) {
        return text_x + measure_text_width_for_hit(input_value.substr(0, (size_t)index), style);
    }

    float px = 0.0f;
    float py = 0.0f;
    DWRITE_HIT_TEST_METRICS hm{};
    UINT32 len = (UINT32)input_value.size();
    UINT32 text_pos = (UINT32)index;
    BOOL trailing = FALSE;
    if (text_pos >= len && len > 0) {
        text_pos = len - 1;
        trailing = TRUE;
    }
    if (FAILED(layout->HitTestTextPosition(text_pos, trailing, &px, &py, &hm))) {
        px = measure_text_width_for_hit(input_value.substr(0, (size_t)index), style);
    }
    layout->Release();

    float caret_x = text_x + px;
    if (caret_x < text_x) caret_x = text_x;
    if (caret_x > text_x + text_w) caret_x = text_x + text_w;
    return caret_x;
}

bool MessageBoxElement::has_input_selection() const {
    return m_input_sel_start >= 0 && m_input_sel_end >= 0 &&
           m_input_sel_start != m_input_sel_end;
}

void MessageBoxElement::normalized_input_selection(int& start, int& end) const {
    start = m_input_sel_start;
    end = m_input_sel_end;
    if (start > end) std::swap(start, end);
    start = clamp_input_pos(start);
    end = clamp_input_pos(end);
    if (start > end) std::swap(start, end);
}

void MessageBoxElement::clear_input_selection() {
    m_input_sel_start = -1;
    m_input_sel_end = -1;
}

void MessageBoxElement::delete_input_selection() {
    if (!has_input_selection()) return;
    int start = 0;
    int end = 0;
    normalized_input_selection(start, end);
    if (end <= start) {
        clear_input_selection();
        return;
    }
    input_value.erase((size_t)start, (size_t)(end - start));
    m_input_cursor_pos = start;
    m_input_select_anchor = start;
    clear_input_selection();
    input_error_visible = false;
}

void MessageBoxElement::select_all_input() {
    m_input_cursor_pos = (int)input_value.size();
    if (input_value.empty()) {
        clear_input_selection();
    } else {
        m_input_sel_start = 0;
        m_input_sel_end = (int)input_value.size();
        m_input_select_anchor = 0;
    }
    m_input_focused = true;
    invalidate();
}

void MessageBoxElement::move_input_cursor_to(int pos, bool extend) {
    pos = clamp_input_pos(pos);
    if (extend) {
        if (!has_input_selection()) m_input_select_anchor = m_input_cursor_pos;
        m_input_cursor_pos = pos;
        m_input_sel_start = m_input_select_anchor;
        m_input_sel_end = m_input_cursor_pos;
        if (m_input_sel_start == m_input_sel_end) clear_input_selection();
    } else {
        m_input_cursor_pos = pos;
        m_input_select_anchor = pos;
        clear_input_selection();
    }
    m_input_focused = true;
    invalidate();
}

std::wstring MessageBoxElement::selected_input_text() const {
    if (!has_input_selection()) return L"";
    int start = 0;
    int end = 0;
    normalized_input_selection(start, end);
    if (end <= start) return L"";
    return input_value.substr((size_t)start, (size_t)(end - start));
}

void MessageBoxElement::copy_input_selection_to_clipboard() const {
    std::wstring selected = selected_input_text();
    if (selected.empty() || !owner_hwnd) return;
    if (!OpenClipboard(owner_hwnd)) return;
    EmptyClipboard();
    size_t bytes = (selected.size() + 1) * sizeof(wchar_t);
    HGLOBAL mem = GlobalAlloc(GMEM_MOVEABLE, bytes);
    if (mem) {
        void* ptr = GlobalLock(mem);
        if (ptr) {
            std::memcpy(ptr, selected.c_str(), bytes);
            GlobalUnlock(mem);
            SetClipboardData(CF_UNICODETEXT, mem);
            mem = nullptr;
        }
        if (mem) GlobalFree(mem);
    }
    CloseClipboard();
}

void MessageBoxElement::cut_input_selection_to_clipboard() {
    if (confirm_loading || !has_input_selection()) return;
    copy_input_selection_to_clipboard();
    delete_input_selection();
    invalidate();
}

void MessageBoxElement::paste_input_from_clipboard() {
    if (confirm_loading || !owner_hwnd) return;
    if (!OpenClipboard(owner_hwnd)) return;
    HANDLE data = GetClipboardData(CF_UNICODETEXT);
    if (data) {
        wchar_t* text_ptr = (wchar_t*)GlobalLock(data);
        if (text_ptr) {
            insert_input_text(text_ptr);
            GlobalUnlock(data);
        }
    }
    CloseClipboard();
}

void MessageBoxElement::show_input_context_menu(int x, int y) {
    if (!owner_hwnd) return;
    HMENU menu = CreatePopupMenu();
    if (!menu) return;

    bool can_copy = has_input_selection();
    bool can_edit = !confirm_loading;
    bool can_paste = can_edit && IsClipboardFormatAvailable(CF_UNICODETEXT);
    AppendMenuW(menu, can_copy ? MF_STRING : (MF_STRING | MF_GRAYED), 1, L"复制");
    AppendMenuW(menu, (can_copy && can_edit) ? MF_STRING : (MF_STRING | MF_GRAYED), 2, L"剪切");
    AppendMenuW(menu, can_paste ? MF_STRING : (MF_STRING | MF_GRAYED), 3, L"粘贴");
    AppendMenuW(menu, MF_SEPARATOR, 0, nullptr);
    AppendMenuW(menu, input_value.empty() ? (MF_STRING | MF_GRAYED) : MF_STRING, 4, L"全选");

    int abs_x = 0;
    int abs_y = 0;
    get_absolute_pos(abs_x, abs_y);
    POINT pt{ abs_x + x, abs_y + y };
    ClientToScreen(owner_hwnd, &pt);
    SetForegroundWindow(owner_hwnd);
    int cmd = TrackPopupMenu(menu, TPM_RETURNCMD | TPM_RIGHTBUTTON,
                             pt.x, pt.y, 0, owner_hwnd, nullptr);
    DestroyMenu(menu);

    if (cmd == 1) copy_input_selection_to_clipboard();
    else if (cmd == 2) cut_input_selection_to_clipboard();
    else if (cmd == 3) paste_input_from_clipboard();
    else if (cmd == 4) select_all_input();
    invalidate();
}

void MessageBoxElement::insert_input_text(const std::wstring& s) {
    if (s.empty() || confirm_loading) return;
    if (has_input_selection()) delete_input_selection();
    m_input_cursor_pos = clamp_input_pos(m_input_cursor_pos);
    input_value.insert((size_t)m_input_cursor_pos, s);
    m_input_cursor_pos += (int)s.size();
    m_input_cursor_pos = clamp_input_pos(m_input_cursor_pos);
    m_input_select_anchor = m_input_cursor_pos;
    clear_input_selection();
    input_error_visible = false;
    invalidate();
}

void MessageBoxElement::delete_input_char_before() {
    if (confirm_loading) return;
    if (has_input_selection()) {
        delete_input_selection();
        invalidate();
        return;
    }
    int start = previous_input_pos(m_input_cursor_pos);
    if (start == m_input_cursor_pos) return;
    input_value.erase((size_t)start, (size_t)(m_input_cursor_pos - start));
    m_input_cursor_pos = start;
    m_input_select_anchor = start;
    input_error_visible = false;
    invalidate();
}

void MessageBoxElement::delete_input_char_after() {
    if (confirm_loading) return;
    if (has_input_selection()) {
        delete_input_selection();
        invalidate();
        return;
    }
    int end = next_input_pos(m_input_cursor_pos);
    if (end == m_input_cursor_pos) return;
    input_value.erase((size_t)m_input_cursor_pos, (size_t)(end - m_input_cursor_pos));
    m_input_select_anchor = m_input_cursor_pos;
    input_error_visible = false;
    invalidate();
}

void MessageBoxElement::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    update_layout();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();
    float radius = 8.0f * s;

    D2D1_RECT_F overlay = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRectangle(overlay, ctx.get_brush(dark ? 0x99000000 : 0x66000000));

    D2D1_RECT_F dialog = {
        (float)m_dialog_rect.x,
        (float)m_dialog_rect.y,
        (float)(m_dialog_rect.x + m_dialog_rect.w),
        (float)(m_dialog_rect.y + m_dialog_rect.h)
    };

    Color dialog_bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color border = dark ? 0xFF45475A : 0xFFE4E7ED;
    Color title_fg = dark ? t->text_primary : 0xFF303133;
    Color body_fg = dark ? t->text_secondary : 0xFF606266;
    Color close_fg = (m_hover_part == PartClose) ? t->accent : (dark ? 0xFFA6ADC8 : 0xFF909399);
    Color accent = feedback_color(t, box_type);

    ctx.rt->FillRoundedRectangle(ROUNDED(dialog, radius, radius), ctx.get_brush(dialog_bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(dialog.left + 0.5f, dialog.top + 0.5f,
        dialog.right - 0.5f, dialog.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

    float pad = 20.0f * s;
    float title_h = 28.0f * s;
    float title_x = (float)m_dialog_rect.x + pad;
    float title_y = (float)m_dialog_rect.y + 18.0f * s;
    float title_w = (float)m_dialog_rect.w - pad * 2.0f - 24.0f * s;

    if (!title.empty()) {
        auto* layout = ctx.create_text_layout(title, style.font_name, style.font_size * 1.14f,
                                              title_w, title_h);
        if (layout) {
            apply_emoji_font_fallback(layout, title);
            layout->SetTextAlignment(center ? DWRITE_TEXT_ALIGNMENT_CENTER : DWRITE_TEXT_ALIGNMENT_LEADING);
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            ctx.rt->DrawTextLayout(D2D1::Point2F(title_x, title_y), layout,
                ctx.get_brush(title_fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    float cx = (float)m_close_rect.x + (float)m_close_rect.w * 0.5f;
    float cy = (float)m_close_rect.y + (float)m_close_rect.h * 0.5f;
    float cs = 6.5f * s;
    auto* close_br = ctx.get_brush(close_fg);
    ctx.rt->DrawLine(D2D1::Point2F(cx - cs, cy - cs), D2D1::Point2F(cx + cs, cy + cs), close_br, 1.6f * s);
    ctx.rt->DrawLine(D2D1::Point2F(cx + cs, cy - cs), D2D1::Point2F(cx - cs, cy + cs), close_br, 1.6f * s);

    float body_x = (float)m_dialog_rect.x + pad;
    float body_y = title_y + title_h + 8.0f * s;
    float body_w = (float)m_dialog_rect.w - pad * 2.0f;
    float body_bottom = prompt ? (float)m_input_rect.y - 8.0f * s
                               : (float)(m_confirm_rect.y - round_px(18.0f * s));
    float body_h = body_bottom - body_y;
    if (body_h < 24.0f * s) body_h = 24.0f * s;

    if (box_type > 0) {
        float icon_d = 22.0f * s;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(body_x + icon_d * 0.5f, body_y + icon_d * 0.55f),
            icon_d * 0.5f, icon_d * 0.5f), ctx.get_brush(accent));
        draw_rich_text(ctx, feedback_icon(box_type), style, 0xFFFFFFFF, body_x, body_y,
                       icon_d, icon_d, false, DWRITE_TEXT_ALIGNMENT_CENTER, false, 0.9f);
        body_x += icon_d + 10.0f * s;
        body_w -= icon_d + 10.0f * s;
    }
    if (!text.empty()) {
        draw_rich_text(ctx, text, style, body_fg, body_x, body_y, body_w, body_h, rich,
                       center ? DWRITE_TEXT_ALIGNMENT_CENTER : DWRITE_TEXT_ALIGNMENT_LEADING, true);
    }

    if (prompt) {
        D2D1_RECT_F input_r = { (float)m_input_rect.x, (float)m_input_rect.y,
            (float)m_input_rect.right(), (float)m_input_rect.bottom() };
        Color input_border = input_error_visible ? 0xFFF56C6C : (dark ? 0xFF585B70 : 0xFFDCDFE6);
        ctx.rt->FillRoundedRectangle(ROUNDED(input_r, 4.0f * s, 4.0f * s),
                                     ctx.get_brush(dark ? 0xFF1E2030 : 0xFFFFFFFF));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(input_r.left + 0.5f, input_r.top + 0.5f,
            input_r.right - 0.5f, input_r.bottom - 0.5f), 4.0f * s, 4.0f * s),
            ctx.get_brush(input_border), 1.0f);
        std::wstring shown = input_value.empty() ? input_placeholder : input_value;
        bool showing_placeholder = input_value.empty();
        float text_x = 0.0f, text_y = 0.0f, text_w = 0.0f, text_h = 0.0f;
        input_text_rect(text_x, text_y, text_w, text_h);
        auto* layout = ctx.create_text_layout(shown, style.font_name, style.font_size, text_w, text_h);
        if (layout) {
            apply_emoji_font_fallback(layout, shown);
            layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);

            if (!showing_placeholder && has_input_selection()) {
                int sel_start = 0;
                int sel_end = 0;
                normalized_input_selection(sel_start, sel_end);
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
                                text_x + hm.left,
                                text_y + hm.top,
                                text_x + hm.left + hm.width,
                                text_y + hm.top + hm.height
                            };
                            ctx.rt->FillRectangle(sel_rect, ctx.get_brush(sel_color));
                        }
                    }
                }
            }

            ctx.rt->DrawTextLayout(D2D1::Point2F(text_x, text_y), layout,
                ctx.get_brush(showing_placeholder ? t->text_secondary : title_fg),
                D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
        if (m_input_focused && !confirm_loading) {
            float caret_x = input_char_to_x(m_input_cursor_pos);
            ctx.rt->DrawLine(D2D1::Point2F(caret_x, input_r.top + 7.0f * s),
                             D2D1::Point2F(caret_x, input_r.bottom - 7.0f * s),
                             ctx.get_brush(title_fg), 1.3f * s);
        }
        if (input_error_visible && !input_error.empty()) {
            draw_rich_text(ctx, input_error, style, 0xFFF56C6C, input_r.left, input_r.bottom + 4.0f * s,
                           input_r.right - input_r.left, 18.0f * s, false, DWRITE_TEXT_ALIGNMENT_LEADING, false, 0.9f);
        }
    }

    if (show_cancel) {
        draw_button(ctx, m_cancel_rect, cancel_text, false,
                    m_hover_part == PartCancel, m_press_part == PartCancel);
    }
    draw_button(ctx, m_confirm_rect, confirm_loading && !loading_text.empty() ? loading_text : confirm_text, true,
                m_hover_part == PartConfirm, m_press_part == PartConfirm);

    ctx.rt->SetTransform(saved);
}

void MessageBoxElement::draw_button(RenderContext& ctx, const Rect& r, const std::wstring& label,
                             bool primary, bool hot, bool down) {
    if (r.w <= 0 || r.h <= 0) return;

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();
    float radius = 4.0f * s;

    Color bg = primary ? t->accent : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = primary ? t->accent : (dark ? 0xFF585B70 : 0xFFDCDFE6);
    Color fg = primary ? 0xFFFFFFFF : (dark ? t->text_primary : 0xFF606266);

    if (primary && hot) bg = down ? 0xFF5C8FE6 : 0xFF79A8F5;
    if (!primary && hot) {
        bg = dark ? 0xFF313244 : 0xFFEAF2FF;
        border = t->accent;
        fg = t->accent;
    }

    D2D1_RECT_F rect = {
        (float)r.x,
        (float)r.y,
        (float)(r.x + r.w),
        (float)(r.y + r.h)
    };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

    auto* layout = ctx.create_text_layout(label, style.font_name, style.font_size,
                                          (float)r.w, (float)r.h);
    if (layout) {
        apply_emoji_font_fallback(layout, label);
        layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
        layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
        ctx.rt->DrawTextLayout(D2D1::Point2F((float)r.x, (float)r.y), layout,
            ctx.get_brush(fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
        layout->Release();
    }
}

void MessageBoxElement::on_mouse_move(int x, int y) {
    if (prompt && m_input_drag_selecting) {
        SetCursor(LoadCursorW(nullptr, IDC_IBEAM));
        move_input_cursor_to(input_x_to_char(x), true);
        return;
    }
    Part old = m_hover_part;
    m_hover_part = part_at(x, y);
    if (wants_text_cursor_at(x, y)) {
        SetCursor(LoadCursorW(nullptr, IDC_IBEAM));
    }
    if (m_hover_part != old) invalidate();
}

void MessageBoxElement::on_mouse_leave() {
    m_hover_part = PartNone;
    m_press_part = PartNone;
    if (!m_input_drag_selecting) invalidate();
}

void MessageBoxElement::on_mouse_down(int x, int y, MouseButton btn) {
    if (btn == MouseButton::Left && wants_text_cursor_at(x, y)) {
        SetCursor(LoadCursorW(nullptr, IDC_IBEAM));
        m_input_focused = true;
        m_input_cursor_pos = input_x_to_char(x);
        m_input_select_anchor = m_input_cursor_pos;
        m_input_drag_selecting = true;
        clear_input_selection();
        m_press_part = PartNone;
        invalidate();
        return;
    }
    m_press_part = part_at(x, y);
    invalidate();
}

void MessageBoxElement::on_mouse_up(int x, int y, MouseButton btn) {
    if (btn == MouseButton::Right) {
        if (wants_text_cursor_at(x, y)) {
            SetCursor(LoadCursorW(nullptr, IDC_IBEAM));
            m_input_focused = true;
            if (!has_input_selection()) {
                m_input_cursor_pos = input_x_to_char(x);
                m_input_select_anchor = m_input_cursor_pos;
            }
            show_input_context_menu(x, y);
        }
        return;
    }
    if (m_input_drag_selecting) {
        m_input_drag_selecting = false;
        move_input_cursor_to(input_x_to_char(x), true);
        invalidate();
        return;
    }
    Part release_part = part_at(x, y);
    Part clicked = (m_press_part != PartNone && m_press_part == release_part) ? m_press_part : PartNone;
    m_press_part = PartNone;
    m_hover_part = release_part;
    invalidate();

    switch (clicked) {
    case PartConfirm: request_result(ResultConfirm); break;
    case PartCancel:  request_result(ResultCancel); break;
    case PartClose:   request_result(distinguish_cancel_and_close ? ResultClose :
                                     (show_cancel ? ResultCancel : ResultClose)); break;
    default: break;
    }
}

void MessageBoxElement::on_key_down(int vk, int mods) {
    if (prompt) {
        bool shift = (mods & KeyMod::Shift) != 0;
        bool ctrl = (mods & KeyMod::Control) != 0;
        if (ctrl) {
            if (vk == 'A') {
                select_all_input();
                return;
            }
            if (vk == 'C') {
                copy_input_selection_to_clipboard();
                invalidate();
                return;
            }
            if (vk == 'X') {
                cut_input_selection_to_clipboard();
                return;
            }
            if (vk == 'V') {
                paste_input_from_clipboard();
                return;
            }
        }
        if (vk == VK_LEFT) {
            if (!shift && has_input_selection()) {
                int start = 0, end = 0;
                normalized_input_selection(start, end);
                move_input_cursor_to(start, false);
            } else {
                move_input_cursor_to(previous_input_pos(m_input_cursor_pos), shift);
            }
            return;
        }
        if (vk == VK_RIGHT) {
            if (!shift && has_input_selection()) {
                int start = 0, end = 0;
                normalized_input_selection(start, end);
                move_input_cursor_to(end, false);
            } else {
                move_input_cursor_to(next_input_pos(m_input_cursor_pos), shift);
            }
            return;
        }
        if (vk == VK_HOME) {
            move_input_cursor_to(0, shift);
            return;
        }
        if (vk == VK_END) {
            move_input_cursor_to((int)input_value.size(), shift);
            return;
        }
        if (vk == VK_BACK) {
            delete_input_char_before();
            return;
        }
        if (vk == VK_DELETE) {
            delete_input_char_after();
            return;
        }
    }
    if (vk == VK_RETURN) {
        request_result(ResultConfirm);
    } else if (vk == VK_ESCAPE) {
        request_result(distinguish_cancel_and_close ? ResultClose :
                       (show_cancel ? ResultCancel : ResultClose));
    }
}

void MessageBoxElement::on_char(wchar_t ch) {
    if (!prompt || confirm_loading) return;
    if (ch >= 32 && ch != 127) {
        insert_input_text(std::wstring(1, ch));
    }
}

void MessageBoxElement::on_focus() {
    has_focus = true;
    if (prompt) {
        m_input_focused = true;
        m_input_cursor_pos = clamp_input_pos(m_input_cursor_pos);
        m_input_select_anchor = m_input_cursor_pos;
    }
    invalidate();
}

void MessageBoxElement::on_blur() {
    has_focus = false;
    pressed = false;
    m_press_part = PartNone;
    m_input_drag_selecting = false;
    m_input_focused = false;
    invalidate();
}
