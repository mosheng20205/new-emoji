#include "element_input.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include "utf8_helpers.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
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

static void draw_text_block(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                            Color color, float x, float y, float w, float h,
                            bool wrap, DWRITE_PARAGRAPH_ALIGNMENT valign) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(valign);
    layout->SetWordWrapping(wrap ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static float measure_text_width(RenderContext& ctx, const std::wstring& text, const ElementStyle& style) {
    if (text.empty()) return 0.0f;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, 4096.0f, 256.0f);
    if (!layout) return 0.0f;
    apply_emoji_font_fallback(layout, text);
    DWRITE_TEXT_METRICS tm{};
    float width = 0.0f;
    if (SUCCEEDED(layout->GetMetrics(&tm))) {
        width = tm.widthIncludingTrailingWhitespace;
    }
    layout->Release();
    return width;
}

static IDWriteTextLayout* create_hit_text_layout(const std::wstring& text, const ElementStyle& style) {
    if (!g_dwrite_factory || text.empty()) return nullptr;

    IDWriteTextFormat* fmt = nullptr;
    HRESULT hr = g_dwrite_factory->CreateTextFormat(
        style.font_name.c_str(), nullptr,
        DWRITE_FONT_WEIGHT_NORMAL, DWRITE_FONT_STYLE_NORMAL, DWRITE_FONT_STRETCH_NORMAL,
        style.font_size, L"", &fmt);
    if (FAILED(hr) || !fmt) return nullptr;

    IDWriteTextLayout* layout = nullptr;
    hr = g_dwrite_factory->CreateTextLayout(
        text.c_str(), static_cast<UINT32>(text.size()),
        fmt, 4096.0f, 256.0f, &layout);
    fmt->Release();
    if (FAILED(hr) || !layout) return nullptr;

    apply_emoji_font_fallback(layout, text);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    return layout;
}

static float measure_text_width_for_hit(const std::wstring& text, const ElementStyle& style) {
    IDWriteTextLayout* layout = create_hit_text_layout(text, style);
    if (!layout) return 0.0f;

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
    text = value;
    invalidate();
    notify_text_changed();
}

void Input::set_placeholder(const std::wstring& next_placeholder) {
    placeholder = next_placeholder;
    invalidate();
}

void Input::set_affixes(const std::wstring& next_prefix, const std::wstring& next_suffix) {
    prefix = next_prefix;
    suffix = next_suffix;
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
    invalidate();
}

void Input::set_max_length(int next_max_length) {
    max_length = (std::max)(0, next_max_length);
    if (max_length > 0 && (int)value.size() > max_length) {
        value.resize(max_length);
        if (m_cursor_pos > (int)value.size()) m_cursor_pos = (int)value.size();
        text = value;
        notify_text_changed();
    }
    invalidate();
}

void Input::get_state(int& cursor, int& length) const {
    cursor = m_cursor_pos;
    length = (int)value.size();
}

Rect Input::clear_rect() const {
    int size = (std::min)(22, (std::max)(16, bounds.h - 12));
    return { bounds.w - style.pad_right - size, (bounds.h - size) / 2, size, size };
}

int Input::char_width() const {
    int cw = (int)(style.font_size * 0.62f + 0.5f);
    return cw < 6 ? 6 : cw;
}

int Input::xpos_to_char(int x) const {
    float prefix_w = 0.0f;
    if (!prefix.empty()) {
        prefix_w = measure_text_width_for_hit(prefix, style) + 10.0f;
        if (prefix_w <= 10.0f) {
            prefix_w = (float)(prefix.size() * char_width() + 10);
        }
    }

    float local_x = (float)x - (float)style.pad_left - prefix_w;
    if (local_x <= 0.0f || value.empty()) return 0;

    IDWriteTextLayout* layout = create_hit_text_layout(value, style);
    if (!layout) {
        int idx = (int)((local_x + char_width() / 2.0f) / (float)char_width());
        if (idx < 0) idx = 0;
        if (idx > (int)value.size()) idx = (int)value.size();
        return idx;
    }

    DWRITE_TEXT_METRICS tm{};
    if (SUCCEEDED(layout->GetMetrics(&tm)) && local_x >= tm.widthIncludingTrailingWhitespace) {
        layout->Release();
        return (int)value.size();
    }

    BOOL is_trailing = FALSE;
    BOOL is_inside = FALSE;
    DWRITE_HIT_TEST_METRICS htm{};
    int pos = 0;
    if (SUCCEEDED(layout->HitTestPoint(local_x, style.font_size * 0.5f,
                                       &is_trailing, &is_inside, &htm))) {
        pos = (int)htm.textPosition + (is_trailing ? (int)htm.length : 0);
    }
    layout->Release();

    if (pos < 0) pos = 0;
    if (pos > (int)value.size()) pos = (int)value.size();
    return pos;
}

int Input::char_to_xpos(int index) const {
    int prefix_w = prefix.empty() ? 0 : (int)(prefix.size() * char_width() + 10);
    if (index < 0) index = 0;
    if (index > (int)value.size()) index = (int)value.size();
    return style.pad_left + prefix_w + index * char_width();
}

void Input::insert_text(const std::wstring& s) {
    if (s.empty()) return;
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
    invalidate();
    notify_text_changed();
}

void Input::delete_char_before() {
    if (m_cursor_pos <= 0 || value.empty()) return;
    value.erase(m_cursor_pos - 1, 1);
    --m_cursor_pos;
    text = value;
    invalidate();
    notify_text_changed();
}

void Input::delete_char_after() {
    if (m_cursor_pos < 0 || m_cursor_pos >= (int)value.size()) return;
    value.erase(m_cursor_pos, 1);
    text = value;
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
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    if (validate_state == 1) border = 0xFF16A34A;
    else if (validate_state == 2) border = 0xFFE6A23C;
    else if (validate_state == 3) border = 0xFFEF4444;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F field = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(field, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), has_focus ? 1.5f : 1.0f);

    float x = (float)style.pad_left;
    if (!prefix.empty()) {
        float pw = measure_text_width(ctx, prefix, style);
        draw_text(ctx, prefix, style, t->text_secondary, x, 0.0f, pw + 4.0f, (float)bounds.h);
        x += pw + 10.0f;
    }

    Rect clear = clear_rect();
    float suffix_w = suffix.empty() ? 0.0f : measure_text_width(ctx, suffix, style) + 10.0f;
    bool show_clear = clearable && !value.empty();
    float clear_reserved = show_clear ? (float)clear.w + 8.0f : 0.0f;
    float right_reserved = suffix_w + clear_reserved;
    float text_w = (float)bounds.w - x - (float)style.pad_right - right_reserved;
    if (text_w < 1.0f) text_w = 1.0f;
    std::wstring masked;
    if (password && !value.empty()) masked.assign(value.size(), L'*');
    const std::wstring& display = value.empty() ? placeholder : (password ? masked : value);
    float text_y = multiline ? (float)style.pad_top : 0.0f;
    float text_h = multiline
        ? (float)bounds.h - (float)style.pad_top - (float)style.pad_bottom
        : (float)bounds.h;
    if (text_h < 1.0f) text_h = (float)bounds.h;
    draw_text_block(ctx, display, style, value.empty() ? t->text_secondary : fg,
                    x, text_y, text_w, text_h,
                    multiline, multiline ? DWRITE_PARAGRAPH_ALIGNMENT_NEAR : DWRITE_PARAGRAPH_ALIGNMENT_CENTER);

    if (has_focus) {
        std::wstring caret_text = value;
        if (m_cursor_pos > 0 && m_cursor_pos < (int)value.size()) {
            caret_text = value.substr(0, m_cursor_pos);
        } else if (m_cursor_pos <= 0) {
            caret_text.clear();
        }
        float caret_x = x + measure_text_width(ctx, caret_text, style);
        if (caret_x < x) caret_x = x;
        if (caret_x > x + text_w) caret_x = x + text_w;
        if (!multiline) {
            ctx.rt->DrawLine(D2D1::Point2F(caret_x, 8.0f),
                             D2D1::Point2F(caret_x, (float)bounds.h - 8.0f),
                             ctx.get_brush(fg), 1.4f);
        }
    }

    if (!suffix.empty()) {
        float suffix_right = (float)bounds.w - (float)style.pad_right - clear_reserved;
        draw_text(ctx, suffix, style, t->text_secondary,
                  suffix_right - suffix_w,
                  0.0f, suffix_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_TRAILING);
    }

    if (show_clear) {
        D2D1_ELLIPSE ellipse = D2D1::Ellipse(
            D2D1::Point2F((float)clear.x + clear.w * 0.5f, (float)clear.y + clear.h * 0.5f),
            clear.w * 0.5f, clear.h * 0.5f);
        ctx.rt->FillEllipse(ellipse, ctx.get_brush(with_alpha(t->text_secondary, hovered ? 0x66 : 0x44)));
        draw_text(ctx, L"x", style, bg, (float)clear.x, (float)clear.y,
                  (float)clear.w, (float)clear.h, DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    ctx.rt->SetTransform(saved);
}

void Input::on_mouse_down(int x, int y, MouseButton) {
    if (!enabled || readonly) return;
    m_press_clear = clearable && !value.empty() && clear_rect().contains(x, y);
    pressed = true;
    if (!m_press_clear) m_cursor_pos = xpos_to_char(x);
    invalidate();
}

void Input::on_mouse_up(int x, int y, MouseButton) {
    if (m_press_clear && clear_rect().contains(x, y)) {
        set_value(L"");
        m_cursor_pos = 0;
    }
    m_press_clear = false;
    pressed = false;
    invalidate();
}

void Input::on_key_down(int vk, int) {
    if (!enabled || readonly) return;
    if (vk == VK_LEFT) {
        if (m_cursor_pos > 0) --m_cursor_pos;
    } else if (vk == VK_RIGHT) {
        if (m_cursor_pos < (int)value.size()) ++m_cursor_pos;
    } else if (vk == VK_HOME) {
        m_cursor_pos = 0;
    } else if (vk == VK_END) {
        m_cursor_pos = (int)value.size();
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
    invalidate();
}
