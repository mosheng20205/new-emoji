#include "element_collapse.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>
#include <cwchar>
#include <sstream>

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP,
                      DWRITE_PARAGRAPH_ALIGNMENT paragraph = DWRITE_PARAGRAPH_ALIGNMENT_CENTER) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(paragraph);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static std::wstring collapse_json_escape(const std::wstring& value) {
    std::wstring out;
    out.reserve(value.size() + 8);
    for (wchar_t ch : value) {
        switch (ch) {
        case L'\\': out += L"\\\\"; break;
        case L'"': out += L"\\\""; break;
        case L'\n': out += L"\\n"; break;
        case L'\r': out += L"\\r"; break;
        case L'\t': out += L"\\t"; break;
        default:
            if (ch < 32) {
                wchar_t buf[8];
                swprintf_s(buf, L"\\u%04X", (unsigned)ch);
                out += buf;
            } else {
                out += ch;
            }
            break;
        }
    }
    return out;
}

static std::wstring index_set_json(const std::set<int>& values) {
    std::wstringstream ss;
    ss << L"[";
    bool first = true;
    for (int value : values) {
        if (!first) ss << L",";
        first = false;
        ss << value;
    }
    ss << L"]";
    return ss.str();
}

float Collapse::header_height() const {
    return (std::max)(style.font_size * 2.65f, 36.0f);
}

float Collapse::body_height(int index, float body_width) const {
    if (index < 0 || index >= (int)items.size()) return 0.0f;
    const std::wstring& body = items[(size_t)index].body;
    int wrap_chars = (std::max)(12, (int)std::floor(body_width / (std::max)(style.font_size * 0.9f, 1.0f)));
    int lines = 1;
    int column = 0;
    for (wchar_t ch : body) {
        if (ch == L'\r') continue;
        if (ch == L'\n') {
            ++lines;
            column = 0;
            continue;
        }
        ++column;
        if (column >= wrap_chars) {
            ++lines;
            column = 0;
        }
    }
    float line_h = style.font_size * 1.55f;
    return (std::max)(style.font_size * 3.2f, 24.0f + line_h * (float)lines);
}

void Collapse::sync_legacy_active() {
    if (m_active_indices.empty()) {
        active_index = -1;
    } else if (m_active_indices.find(active_index) == m_active_indices.end()) {
        active_index = *m_active_indices.begin();
    }
    if (items.empty()) {
        focus_index = -1;
    } else if (focus_index < 0 || focus_index >= (int)items.size() || is_disabled(focus_index)) {
        focus_index = active_index >= 0 ? active_index : next_enabled_index(0, 1);
    }
}

void Collapse::normalize_active_indices() {
    for (auto it = m_active_indices.begin(); it != m_active_indices.end();) {
        if (*it < 0 || *it >= (int)items.size() || is_disabled(*it)) {
            it = m_active_indices.erase(it);
        } else {
            ++it;
        }
    }
    if (accordion && m_active_indices.size() > 1) {
        int keep = m_active_indices.find(active_index) != m_active_indices.end()
            ? active_index : *m_active_indices.begin();
        m_active_indices.clear();
        m_active_indices.insert(keep);
    }
    sync_legacy_active();
}

void Collapse::set_items(const std::vector<CollapseItem>& values) {
    items = values;
    if (items.empty()) {
        m_active_indices.clear();
        active_index = -1;
        focus_index = -1;
    } else {
        if (active_index >= (int)items.size()) active_index = (int)items.size() - 1;
        if (active_index >= 0 && m_active_indices.empty()) m_active_indices.insert(active_index);
    }
    for (auto it = disabled_indices.begin(); it != disabled_indices.end();) {
        if (*it < 0 || *it >= (int)items.size()) it = disabled_indices.erase(it);
        else ++it;
    }
    normalize_active_indices();
    invalidate();
}

void Collapse::set_active_index(int value) {
    int old = active_index;
    m_active_indices.clear();
    if (items.empty()) {
        active_index = -1;
        focus_index = -1;
    } else {
        if (value < -1) value = -1;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        if (is_disabled(value)) value = next_enabled_index(value, 1);
        if (value >= 0) {
            m_active_indices.insert(value);
            focus_index = value;
        }
    }
    sync_legacy_active();
    if (animated && old != active_index) begin_animation(active_index);
    invalidate();
}

void Collapse::set_active_indices(const std::set<int>& values) {
    int old = active_index;
    m_active_indices.clear();
    for (int value : values) {
        if (value >= 0 && value < (int)items.size() && !is_disabled(value)) {
            m_active_indices.insert(value);
            if (accordion) break;
        }
    }
    normalize_active_indices();
    if (!m_active_indices.empty()) focus_index = active_index;
    if (animated && old != active_index) begin_animation(active_index);
    invalidate();
}

void Collapse::set_accordion(bool value) {
    accordion = value;
    normalize_active_indices();
    invalidate();
}

void Collapse::set_options(bool accordion_value, bool allow_collapse_value,
                           const std::set<int>& disabled, bool animated_value) {
    int old = active_index;
    accordion = accordion_value;
    allow_collapse = allow_collapse_value;
    animated = animated_value;
    disabled_indices.clear();
    for (int index : disabled) {
        if (index >= 0 && index < (int)items.size()) disabled_indices.insert(index);
    }
    normalize_active_indices();
    if (m_active_indices.empty() && old >= 0) {
        int replacement = next_enabled_index(old, 1);
        if (replacement >= 0) m_active_indices.insert(replacement);
    }
    normalize_active_indices();
    invalidate();
}

void Collapse::begin_animation(int index) {
    m_anim_index = index;
    m_anim_start = GetTickCount64();
}

float Collapse::animation_progress(int index) const {
    if (!animated || m_anim_index != index || m_anim_start == 0) return 1.0f;
    ULONGLONG elapsed = GetTickCount64() - m_anim_start;
    float p = (float)elapsed / (float)kAnimDurationMs;
    if (p >= 1.0f) return 1.0f;
    if (p < 0.0f) return 0.0f;
    return 1.0f - (1.0f - p) * (1.0f - p);
}

bool Collapse::is_disabled(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[(size_t)index].disabled || disabled_indices.find(index) != disabled_indices.end();
}

bool Collapse::is_active(int index) const {
    return m_active_indices.find(index) != m_active_indices.end();
}

int Collapse::next_enabled_index(int start, int direction) const {
    if (items.empty()) return -1;
    int count = (int)items.size();
    if (direction == 0) direction = 1;
    int idx = start;
    for (int step = 0; step < count; ++step) {
        if (idx < 0) idx = count - 1;
        if (idx >= count) idx = 0;
        if (!is_disabled(idx)) return idx;
        idx += direction > 0 ? 1 : -1;
    }
    return -1;
}

int Collapse::header_at(int x, int y) const {
    if (x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    float hh = header_height();
    float cy = (float)style.pad_top;
    float body_w = (std::max)(0.0f, (float)bounds.w - (float)style.pad_left - (float)style.pad_right - 42.0f);
    for (int i = 0; i < (int)items.size(); ++i) {
        if (y >= cy && y < cy + hh) return is_disabled(i) ? -1 : i;
        cy += hh;
        if (is_active(i)) cy += body_height(i, body_w);
    }
    return -1;
}

void Collapse::toggle_index(int index) {
    if (index < 0 || index >= (int)items.size() || is_disabled(index)) return;
    int old = active_index;
    if (accordion) {
        if (is_active(index) && allow_collapse) {
            m_active_indices.clear();
        } else {
            m_active_indices.clear();
            m_active_indices.insert(index);
        }
    } else {
        if (is_active(index)) {
            if (allow_collapse) m_active_indices.erase(index);
        } else {
            m_active_indices.insert(index);
        }
    }
    focus_index = index;
    normalize_active_indices();
    if (animated && old != active_index && is_active(active_index)) begin_animation(active_index);
    if (animated && is_active(index)) begin_animation(index);
    invalidate();
}

void Collapse::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF1E1E2E : 0xFFFFFFFF);
    Color panel_bg = dark ? 0xFF242637 : 0xFFFAFAFA;
    Color hover_bg = dark ? 0xFF2B2E42 : 0xFFF5F7FA;
    Color focus_bg = dark ? 0xFF202A44 : 0xFFF0F7FF;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = t->text_secondary;
    Color accent = t->accent;
    Color disabled_fg = t->text_muted;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);
    ctx.rt->FillRectangle(clip, ctx.get_brush(bg));

    float left = (float)style.pad_left;
    float right = (float)bounds.w - (float)style.pad_right;
    if (right < left) right = left;
    float hh = header_height();
    float y = (float)style.pad_top;

    for (int i = 0; i < (int)items.size(); ++i) {
        if (y >= bounds.h) break;
        bool active = is_active(i);
        bool disabled = is_disabled(i);
        D2D1_RECT_F header = { left, y, right, (std::min)(y + hh, (float)bounds.h) };
        if (i == focus_index && !disabled) {
            ctx.rt->FillRectangle(header, ctx.get_brush(focus_bg));
        }
        if (i == m_hover_index || i == m_press_index) {
            ctx.rt->FillRectangle(header, ctx.get_brush(hover_bg));
        }
        ctx.rt->DrawLine(D2D1::Point2F(left, y),
                         D2D1::Point2F(right, y),
                         ctx.get_brush(border), 1.0f);

        float arrow_x = left + 10.0f;
        float arrow_y = y + hh * 0.5f;
        auto* arrow_br = ctx.get_brush(disabled ? disabled_fg : (active ? accent : t->text_secondary));
        if (active) {
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x - 4.0f, arrow_y - 2.0f),
                             D2D1::Point2F(arrow_x, arrow_y + 3.0f), arrow_br, 1.5f);
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x, arrow_y + 3.0f),
                             D2D1::Point2F(arrow_x + 5.0f, arrow_y - 3.0f), arrow_br, 1.5f);
        } else {
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x - 2.0f, arrow_y - 5.0f),
                             D2D1::Point2F(arrow_x + 3.0f, arrow_y), arrow_br, 1.5f);
            ctx.rt->DrawLine(D2D1::Point2F(arrow_x + 3.0f, arrow_y),
                             D2D1::Point2F(arrow_x - 2.0f, arrow_y + 5.0f), arrow_br, 1.5f);
        }

        float text_x = left + 28.0f;
        if (!items[(size_t)i].icon.empty()) {
            draw_text(ctx, items[(size_t)i].icon, style, disabled ? disabled_fg : accent,
                      text_x, y, 24.0f, hh, 1.0f, DWRITE_FONT_WEIGHT_NORMAL);
            text_x += 28.0f;
        }
        float suffix_w = items[(size_t)i].suffix.empty()
            ? 0.0f : (std::min)(150.0f, (std::max)(34.0f, 16.0f + (float)items[(size_t)i].suffix.size() * style.font_size * 0.8f));
        if (suffix_w > 0.0f) {
            draw_text(ctx, items[(size_t)i].suffix, style, disabled ? disabled_fg : t->text_secondary,
                      right - suffix_w - 10.0f, y, suffix_w, hh, 0.92f,
                      DWRITE_FONT_WEIGHT_NORMAL);
        }
        draw_text(ctx, items[(size_t)i].title.empty() ? L"Collapse Item" : items[(size_t)i].title, style,
                  disabled ? disabled_fg : (active ? accent : title_fg),
                  text_x, y, (std::max)(0.0f, right - text_x - suffix_w - 18.0f), hh,
                  1.0f, active ? DWRITE_FONT_WEIGHT_SEMI_BOLD : DWRITE_FONT_WEIGHT_NORMAL);
        y += hh;

        if (active && y < bounds.h) {
            float full_body_h = body_height(i, right - left - 42.0f);
            float progress = animation_progress(i);
            float current_body_h = full_body_h * progress;
            D2D1_RECT_F body = { left, y, right, (std::min)(y + current_body_h, (float)bounds.h) };
            ctx.rt->FillRectangle(body, ctx.get_brush(panel_bg));
            D2D1_RECT_F body_clip = { left, y, right, (std::min)(y + current_body_h, (float)bounds.h) };
            ctx.push_clip(body_clip);
            draw_text(ctx, items[(size_t)i].body, style, body_fg,
                      left + 28.0f, y + 10.0f, right - left - 42.0f, full_body_h - 18.0f,
                      0.95f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_WORD_WRAPPING_WRAP,
                      DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
            ctx.pop_clip();
            if (progress < 1.0f) invalidate();
            y += current_body_h;
        }
    }

    ctx.rt->DrawLine(D2D1::Point2F(left, (std::min)(y, (float)bounds.h - 1.0f)),
                     D2D1::Point2F(right, (std::min)(y, (float)bounds.h - 1.0f)),
                     ctx.get_brush(border), 1.0f);
    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Collapse::on_mouse_move(int x, int y) {
    int idx = header_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Collapse::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Collapse::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_index = header_at(x, y);
    invalidate();
}

void Collapse::on_mouse_up(int x, int y, MouseButton) {
    int idx = header_at(x, y);
    if (idx >= 0 && idx == m_press_index) {
        toggle_index(idx);
    }
    pressed = false;
    m_press_index = -1;
    m_hover_index = idx;
    invalidate();
}

void Collapse::on_key_down(int vk, int) {
    if (items.empty()) return;
    if (focus_index < 0 || focus_index >= (int)items.size() || is_disabled(focus_index)) {
        focus_index = active_index >= 0 ? active_index : next_enabled_index(0, 1);
    }
    if (vk == VK_UP) focus_index = next_enabled_index(focus_index - 1, -1);
    else if (vk == VK_DOWN) focus_index = next_enabled_index(focus_index + 1, 1);
    else if (vk == VK_HOME) focus_index = next_enabled_index(0, 1);
    else if (vk == VK_END) focus_index = next_enabled_index((int)items.size() - 1, -1);
    else if (vk == VK_RETURN || vk == VK_SPACE) toggle_index(focus_index);
    invalidate();
}

std::wstring Collapse::active_indices_text() const {
    std::wstringstream ss;
    bool first = true;
    for (int value : m_active_indices) {
        if (!first) ss << L",";
        first = false;
        ss << value;
    }
    return ss.str();
}

int Collapse::active_count() const {
    return (int)m_active_indices.size();
}

std::wstring Collapse::state_json() const {
    std::set<int> disabled;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_disabled(i)) disabled.insert(i);
    }
    std::wstringstream ss;
    ss << L"{";
    ss << L"\"itemCount\":" << items.size() << L",";
    ss << L"\"activeIndex\":" << active_index << L",";
    ss << L"\"activeIndices\":" << index_set_json(m_active_indices) << L",";
    ss << L"\"activeCount\":" << m_active_indices.size() << L",";
    ss << L"\"focusIndex\":" << focus_index << L",";
    ss << L"\"accordion\":" << (accordion ? L"true" : L"false") << L",";
    ss << L"\"allowCollapse\":" << (allow_collapse ? L"true" : L"false") << L",";
    ss << L"\"animated\":" << (animated ? L"true" : L"false") << L",";
    ss << L"\"disabledIndices\":" << index_set_json(disabled) << L",";
    ss << L"\"items\":[";
    for (size_t i = 0; i < items.size(); ++i) {
        if (i > 0) ss << L",";
        ss << L"{";
        ss << L"\"title\":\"" << collapse_json_escape(items[i].title) << L"\",";
        ss << L"\"icon\":\"" << collapse_json_escape(items[i].icon) << L"\",";
        ss << L"\"suffix\":\"" << collapse_json_escape(items[i].suffix) << L"\",";
        ss << L"\"disabled\":" << (is_disabled((int)i) ? L"true" : L"false") << L",";
        ss << L"\"active\":" << (is_active((int)i) ? L"true" : L"false");
        ss << L"}";
    }
    ss << L"]";
    ss << L"}";
    return ss.str();
}
