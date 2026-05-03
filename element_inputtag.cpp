#include "element_inputtag.h"
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

static float measure_text_width(RenderContext& ctx, const std::wstring& text, const ElementStyle& style) {
    if (text.empty()) return 0.0f;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, 4096.0f, 256.0f);
    if (!layout) return 0.0f;
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

void InputTag::set_tags(const std::vector<std::wstring>& values) {
    tags.clear();
    for (const auto& value : values) {
        if (value.empty()) continue;
        if (!allow_duplicates && std::find(tags.begin(), tags.end(), value) != tags.end()) continue;
        if (max_count > 0 && (int)tags.size() >= max_count) break;
        tags.push_back(value);
    }
    sync_text();
    invalidate();
    notify_changed();
}

void InputTag::set_input_value(const std::wstring& value) {
    input_value = value;
    m_cursor_pos = (int)input_value.size();
    invalidate();
}

void InputTag::set_placeholder(const std::wstring& value) {
    placeholder = value;
    invalidate();
}

void InputTag::set_options(int next_max_count, bool next_allow_duplicates) {
    max_count = (std::max)(0, next_max_count);
    allow_duplicates = next_allow_duplicates;
    if (max_count > 0 && (int)tags.size() > max_count) {
        tags.resize(max_count);
        sync_text();
        notify_changed();
    }
    invalidate();
}

bool InputTag::add_tag(const std::wstring& value) {
    bool added = false;
    if (!value.empty()) {
        bool exists = std::find(tags.begin(), tags.end(), value) != tags.end();
        bool can_add = (max_count <= 0 || (int)tags.size() < max_count) && (allow_duplicates || !exists);
        if (can_add) {
            tags.push_back(value);
            added = true;
        }
    }
    input_value.clear();
    m_cursor_pos = 0;
    if (added) {
        sync_text();
        notify_changed();
    }
    invalidate();
    return added;
}

bool InputTag::remove_tag(int index) {
    if (index < 0 || index >= (int)tags.size()) return false;
    tags.erase(tags.begin() + index);
    sync_text();
    notify_changed();
    invalidate();
    return true;
}

bool InputTag::remove_last_tag() {
    if (tags.empty()) return false;
    return remove_tag((int)tags.size() - 1);
}

int InputTag::tag_width(const std::wstring& tag) const {
    int base = (int)(tag.size() * (style.font_size * 0.90f)) + 52;
    return base < 88 ? 88 : base;
}

Rect InputTag::tag_rect(int index) const {
    int x = style.pad_left;
    int y = style.pad_top;
    for (int i = 0; i < index && i < (int)tags.size(); ++i) {
        x += tag_width(tags[i]) + 8;
        if (x > bounds.w - 120) {
            x = style.pad_left;
            y += 34;
        }
    }
    return { x, y, tag_width(tags[index]), 28 };
}

Rect InputTag::close_rect(int index) const {
    Rect r = tag_rect(index);
    return { r.x + r.w - 22, r.y + 6, 14, 14 };
}

Rect InputTag::input_rect() const {
    int x = style.pad_left;
    int y = style.pad_top;
    for (int i = 0; i < (int)tags.size(); ++i) {
        int tw = tag_width(tags[i]);
        if (x + tw > bounds.w - style.pad_right - 96) {
            x = style.pad_left;
            y += 34;
        }
        x += tw + 8;
    }

    int input_y = tags.empty() ? style.pad_top : y + 36;
    int input_w = bounds.w - style.pad_left - style.pad_right;
    if (input_w < 40) input_w = 40;
    return { style.pad_left, input_y, input_w, 24 };
}

int InputTag::close_at(int x, int y) const {
    for (int i = 0; i < (int)tags.size(); ++i) {
        if (close_rect(i).contains(x, y)) return i;
    }
    return -1;
}

int InputTag::normalized_cursor() const {
    int pos = m_cursor_pos;
    if (pos < 0) pos = 0;
    if (pos > (int)input_value.size()) pos = (int)input_value.size();
    return pos;
}

int InputTag::xpos_to_cursor(int x) const {
    Rect input = input_rect();
    float local_x = (float)(x - input.x);
    if (local_x <= 0.0f || input_value.empty()) return 0;

    IDWriteTextLayout* layout = create_hit_text_layout(input_value, style);
    if (!layout) {
        int cw = (int)(style.font_size * 0.62f + 0.5f);
        if (cw < 6) cw = 6;
        int idx = (int)((local_x + cw / 2.0f) / (float)cw);
        if (idx < 0) idx = 0;
        if (idx > (int)input_value.size()) idx = (int)input_value.size();
        return idx;
    }

    DWRITE_TEXT_METRICS tm{};
    if (SUCCEEDED(layout->GetMetrics(&tm)) && local_x >= tm.widthIncludingTrailingWhitespace) {
        layout->Release();
        return (int)input_value.size();
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
    if (pos > (int)input_value.size()) pos = (int)input_value.size();
    return pos;
}

void InputTag::commit_input() {
    if (!input_value.empty()) add_tag(input_value);
    invalidate();
}

void InputTag::sync_text() {
    text.clear();
    for (size_t i = 0; i < tags.size(); ++i) {
        if (i > 0) text += L"|";
        text += tags[i];
    }
}

void InputTag::notify_changed() {
    if (!change_cb) return;
    std::string utf8 = wide_to_utf8(text);
    change_cb(id, reinterpret_cast<const unsigned char*>(utf8.data()), (int)utf8.size());
}

void InputTag::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : t->edit_bg;
    Color border = has_focus ? t->edit_focus : (style.border_color ? style.border_color : t->edit_border);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), has_focus ? 1.5f : 1.0f);

    int x = style.pad_left;
    int y = style.pad_top;
    for (int i = 0; i < (int)tags.size(); ++i) {
        int tw = tag_width(tags[i]);
        if (x + tw > bounds.w - style.pad_right - 96) {
            x = style.pad_left;
            y += 34;
        }
        D2D1_RECT_F chip = { (float)x, (float)y, (float)(x + tw), (float)(y + 28) };
        ctx.rt->FillRoundedRectangle(ROUNDED(chip, 14.0f, 14.0f),
            ctx.get_brush(with_alpha(t->accent, dark ? 0x26 : 0x18)));
        ctx.rt->DrawRoundedRectangle(ROUNDED(chip, 14.0f, 14.0f),
            ctx.get_brush(with_alpha(t->accent, dark ? 0x42 : 0x30)), 1.0f);
        draw_text(ctx, tags[i], style, fg, chip.left + 12.0f, chip.top, chip.right - chip.left - 38.0f, 28.0f);
        D2D1_RECT_F close = { chip.right - 22.0f, chip.top + 7.0f, chip.right - 8.0f, chip.top + 21.0f };
        ctx.rt->FillEllipse(D2D1::Ellipse(
            D2D1::Point2F((close.left + close.right) * 0.5f, (close.top + close.bottom) * 0.5f), 6.0f, 6.0f),
            ctx.get_brush(with_alpha(t->text_secondary, 0x46)));
        draw_text(ctx, L"x", style, bg, close.left, close.top, close.right - close.left, close.bottom - close.top,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
        x += tw + 8;
    }

    Rect input = input_rect();
    int input_x = input.x;
    int input_y = input.y;
    float input_w = (float)input.w;
    if (input_w < 40.0f) input_w = 40.0f;
    const std::wstring& display = input_value.empty() ? placeholder : input_value;
    draw_text(ctx, display, style, input_value.empty() ? t->text_secondary : fg,
              (float)input_x, (float)input_y, input_w, 24.0f);

    if (has_focus) {
        int cursor = normalized_cursor();
        std::wstring caret_text = cursor <= 0 ? L"" : input_value.substr(0, cursor);
        float caret_x = (float)input_x + measure_text_width(ctx, caret_text, style);
        float max_x = (float)bounds.w - (float)style.pad_right;
        if (caret_x > max_x) caret_x = max_x;
        ctx.rt->DrawLine(D2D1::Point2F(caret_x, (float)input_y + 4.0f),
                         D2D1::Point2F(caret_x, (float)input_y + 24.0f),
                         ctx.get_brush(fg), 1.4f);
    }

    ctx.rt->SetTransform(saved);
}

void InputTag::on_mouse_down(int x, int y, MouseButton) {
    m_press_close = close_at(x, y);
    if (m_press_close < 0) {
        m_cursor_pos = xpos_to_cursor(x);
    }
    pressed = true;
    invalidate();
}

void InputTag::on_mouse_up(int x, int y, MouseButton) {
    int idx = close_at(x, y);
    if (idx >= 0 && idx == m_press_close) {
        remove_tag(idx);
    }
    m_press_close = -1;
    pressed = false;
    invalidate();
}

void InputTag::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        commit_input();
    } else if (vk == VK_LEFT) {
        if (m_cursor_pos > 0) --m_cursor_pos;
    } else if (vk == VK_RIGHT) {
        if (m_cursor_pos < (int)input_value.size()) ++m_cursor_pos;
    } else if (vk == VK_HOME) {
        m_cursor_pos = 0;
    } else if (vk == VK_END) {
        m_cursor_pos = (int)input_value.size();
    } else if (vk == VK_BACK) {
        if (!input_value.empty() && m_cursor_pos > 0) {
            input_value.erase(m_cursor_pos - 1, 1);
            --m_cursor_pos;
        }
        else remove_last_tag();
    } else if (vk == VK_DELETE) {
        if (!input_value.empty() && m_cursor_pos < (int)input_value.size()) {
            input_value.erase(m_cursor_pos, 1);
        }
    } else if (vk == VK_ESCAPE) {
        input_value.clear();
        m_cursor_pos = 0;
    }
    invalidate();
}

void InputTag::on_char(wchar_t ch) {
    if (ch == L',' || ch == L';') {
        commit_input();
        return;
    }
    if (ch <= 32 || ch == L'\r' || ch == L'\n') return;
    m_cursor_pos = normalized_cursor();
    input_value.insert(m_cursor_pos, 1, ch);
    ++m_cursor_pos;
    invalidate();
}

void InputTag::on_focus() {
    has_focus = true;
    m_cursor_pos = normalized_cursor();
    invalidate();
}

void InputTag::on_blur() {
    has_focus = false;
    commit_input();
}
