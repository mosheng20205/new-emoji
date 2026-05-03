#include "element_transfer.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      float scale = 1.0f) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

float Transfer::row_height() const {
    return (std::max)(style.font_size * 2.15f, 30.0f);
}

Rect Transfer::left_rect() const {
    int gap = 56;
    int panel_w = (bounds.w - style.pad_left - style.pad_right - gap) / 2;
    if (panel_w < 80) panel_w = 80;
    return { style.pad_left, style.pad_top, panel_w, bounds.h - style.pad_top - style.pad_bottom };
}

Rect Transfer::right_rect() const {
    Rect l = left_rect();
    int gap = 56;
    return { l.x + l.w + gap, l.y, l.w, l.h };
}

Rect Transfer::move_right_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 10, l.y + l.h / 2 - 70, 36, 28 };
}

Rect Transfer::move_left_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 10, l.y + l.h / 2 + 8, 36, 28 };
}

Rect Transfer::move_all_right_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 10, l.y + l.h / 2 - 34, 36, 28 };
}

Rect Transfer::move_all_left_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 10, l.y + l.h / 2 + 44, 36, 28 };
}

void Transfer::set_items(const std::vector<std::wstring>& left, const std::vector<std::wstring>& right) {
    left_items = left;
    right_items = right;
    left_disabled.assign(left_items.size(), false);
    right_disabled.assign(right_items.size(), false);
    left_selected = left_items.empty() ? -1 : 0;
    right_selected = right_items.empty() ? -1 : 0;
    invalidate();
}

void Transfer::move_selected_right() {
    if (left_selected < 0 || left_selected >= (int)left_items.size()) return;
    if (is_disabled(0, left_selected)) return;
    right_items.push_back(left_items[left_selected]);
    right_disabled.push_back(left_disabled[left_selected]);
    left_items.erase(left_items.begin() + left_selected);
    left_disabled.erase(left_disabled.begin() + left_selected);
    if (left_selected >= (int)left_items.size()) left_selected = (int)left_items.size() - 1;
    right_selected = (int)right_items.size() - 1;
    normalize_state();
    invalidate();
}

void Transfer::move_selected_left() {
    if (right_selected < 0 || right_selected >= (int)right_items.size()) return;
    if (is_disabled(1, right_selected)) return;
    left_items.push_back(right_items[right_selected]);
    left_disabled.push_back(right_disabled[right_selected]);
    right_items.erase(right_items.begin() + right_selected);
    right_disabled.erase(right_disabled.begin() + right_selected);
    if (right_selected >= (int)right_items.size()) right_selected = (int)right_items.size() - 1;
    left_selected = (int)left_items.size() - 1;
    normalize_state();
    invalidate();
}

void Transfer::move_all_right() {
    auto visible = rendered_indices(0);
    for (int n = (int)visible.size() - 1; n >= 0; --n) {
        int i = visible[n];
        if (is_disabled(0, i)) continue;
        right_items.push_back(left_items[i]);
        right_disabled.push_back(left_disabled[i]);
        left_items.erase(left_items.begin() + i);
        left_disabled.erase(left_disabled.begin() + i);
    }
    normalize_state();
    invalidate();
}

void Transfer::move_all_left() {
    auto visible = rendered_indices(1);
    for (int n = (int)visible.size() - 1; n >= 0; --n) {
        int i = visible[n];
        if (is_disabled(1, i)) continue;
        left_items.push_back(right_items[i]);
        left_disabled.push_back(right_disabled[i]);
        right_items.erase(right_items.begin() + i);
        right_disabled.erase(right_disabled.begin() + i);
    }
    normalize_state();
    invalidate();
}

void Transfer::set_left_selected(int index) {
    if (left_items.empty()) {
        left_selected = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)left_items.size()) index = (int)left_items.size() - 1;
        left_selected = is_disabled(0, index) ? -1 : index;
    }
    invalidate();
}

void Transfer::set_right_selected(int index) {
    if (right_items.empty()) {
        right_selected = -1;
    } else {
        if (index < 0) index = 0;
        if (index >= (int)right_items.size()) index = (int)right_items.size() - 1;
        right_selected = is_disabled(1, index) ? -1 : index;
    }
    invalidate();
}

void Transfer::set_filters(const std::wstring& left, const std::wstring& right) {
    left_filter = left;
    right_filter = right;
    if (left_selected >= 0 && !matches_filter(0, left_selected)) left_selected = -1;
    if (right_selected >= 0 && !matches_filter(1, right_selected)) right_selected = -1;
    invalidate();
}

void Transfer::set_item_disabled(int side, int index, bool disabled) {
    auto& flags = side == 1 ? right_disabled : left_disabled;
    const auto& data = side == 1 ? right_items : left_items;
    if (index < 0 || index >= (int)data.size()) return;
    if ((int)flags.size() < (int)data.size()) flags.resize(data.size(), false);
    flags[index] = disabled;
    if (disabled) {
        if (side == 1 && right_selected == index) right_selected = -1;
        if (side != 1 && left_selected == index) left_selected = -1;
    }
    invalidate();
}

bool Transfer::get_item_disabled(int side, int index) const {
    return is_disabled(side, index);
}

int Transfer::left_count() const {
    return (int)left_items.size();
}

int Transfer::right_count() const {
    return (int)right_items.size();
}

int Transfer::matched_count(int side) const {
    return (int)rendered_indices(side).size();
}

int Transfer::disabled_count(int side) const {
    const auto& data = side == 1 ? right_items : left_items;
    int count = 0;
    for (int i = 0; i < (int)data.size(); ++i) {
        if (is_disabled(side, i)) ++count;
    }
    return count;
}

bool Transfer::matches_filter(int side, int index) const {
    const auto& data = side == 1 ? right_items : left_items;
    const auto& filter = side == 1 ? right_filter : left_filter;
    if (index < 0 || index >= (int)data.size()) return false;
    return filter.empty() || data[index].find(filter) != std::wstring::npos;
}

bool Transfer::is_disabled(int side, int index) const {
    const auto& data = side == 1 ? right_items : left_items;
    const auto& flags = side == 1 ? right_disabled : left_disabled;
    if (index < 0 || index >= (int)data.size()) return true;
    return index < (int)flags.size() && flags[index];
}

std::vector<int> Transfer::rendered_indices(int side) const {
    const auto& data = side == 1 ? right_items : left_items;
    std::vector<int> indices;
    for (int i = 0; i < (int)data.size(); ++i) {
        if (matches_filter(side, i)) indices.push_back(i);
    }
    return indices;
}

void Transfer::normalize_state() {
    left_disabled.resize(left_items.size(), false);
    right_disabled.resize(right_items.size(), false);
    if (left_selected >= (int)left_items.size() || is_disabled(0, left_selected)) left_selected = -1;
    if (right_selected >= (int)right_items.size() || is_disabled(1, right_selected)) right_selected = -1;
    if (left_selected < 0) {
        for (int i : rendered_indices(0)) {
            if (!is_disabled(0, i)) { left_selected = i; break; }
        }
    }
    if (right_selected < 0) {
        for (int i : rendered_indices(1)) {
            if (!is_disabled(1, i)) { right_selected = i; break; }
        }
    }
}

Transfer::Part Transfer::hit_part(int x, int y, int& index) const {
    index = -1;
    if (move_right_rect().contains(x, y)) return PartMoveRight;
    if (move_left_rect().contains(x, y)) return PartMoveLeft;
    if (move_all_right_rect().contains(x, y)) return PartMoveAllRight;
    if (move_all_left_rect().contains(x, y)) return PartMoveAllLeft;

    float header_h = (std::max)(style.font_size * 2.4f, 34.0f);
    float rh = row_height();
    Rect l = left_rect();
    Rect r = right_rect();
    if (l.contains(x, y) && y >= l.y + header_h) {
        int pos = (int)((y - l.y - header_h) / rh);
        auto visible = rendered_indices(0);
        index = pos >= 0 && pos < (int)visible.size() ? visible[pos] : -1;
        return index >= 0 ? PartLeftItem : PartNone;
    }
    if (r.contains(x, y) && y >= r.y + header_h) {
        int pos = (int)((y - r.y - header_h) / rh);
        auto visible = rendered_indices(1);
        index = pos >= 0 && pos < (int)visible.size() ? visible[pos] : -1;
        return index >= 0 ? PartRightItem : PartNone;
    }
    return PartNone;
}

void Transfer::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color header_bg = dark ? 0xFF2B2E42 : 0xFFF5F7FA;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFEAF2FF;
    Color selected_bg = with_alpha(t->accent, dark ? 0x44 : 0x22);

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    auto draw_panel = [&](const Rect& p, const std::wstring& title,
                          const std::vector<std::wstring>& data, int selected, Part part, int side) {
        float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
        D2D1_RECT_F rect = { (float)p.x, (float)p.y, (float)(p.x + p.w), (float)(p.y + p.h) };
        ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
            rect.right - 0.5f, rect.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

        float header_h = (std::max)(style.font_size * 2.4f, 34.0f);
        D2D1_RECT_F header = { rect.left, rect.top, rect.right, rect.top + header_h };
        ctx.rt->FillRectangle(header, ctx.get_brush(header_bg));
        ctx.rt->DrawLine(D2D1::Point2F(rect.left, rect.top + header_h),
                         D2D1::Point2F(rect.right, rect.top + header_h),
                         ctx.get_brush(border), 1.0f);
        std::wstring title_text = title + L"  " + std::to_wstring(matched_count(side)) + L"/" + std::to_wstring((int)data.size());
        draw_text(ctx, title_text, style, fg, rect.left + 12.0f, rect.top, (float)p.w - 24.0f, header_h);

        float rh = row_height();
        auto visible = rendered_indices(side);
        int row_index = 0;
        for (int i : visible) {
            float y = rect.top + header_h + rh * (float)row_index++;
            if (y >= rect.bottom) break;
            bool sel = i == selected;
            bool hot = m_hover_part == part && i == m_hover_index;
            bool disabled = is_disabled(side, i);
            if (sel || hot) {
                D2D1_RECT_F row = { rect.left + 6.0f, y + 2.0f, rect.right - 6.0f, y + rh - 2.0f };
                ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
                    ctx.get_brush(sel ? selected_bg : hover_bg));
            }
            Color row_color = disabled ? muted : (sel ? t->accent : fg);
            std::wstring prefix = disabled ? L"🚫 " : L"";
            draw_text(ctx, prefix + data[i], style, row_color,
                      rect.left + 14.0f, y, (float)p.w - 28.0f, rh);
        }
        if (visible.empty()) {
            draw_text(ctx, L"🫥 没有匹配项", style, muted,
                      rect.left, rect.top + header_h + 12.0f, (float)p.w, rh,
                      DWRITE_TEXT_ALIGNMENT_CENTER);
        }
    };

    Rect l = left_rect();
    Rect r = right_rect();
    draw_panel(l, left_filter.empty() ? L"源列表" : L"源列表 🔎 " + left_filter,
               left_items, left_selected, PartLeftItem, 0);
    draw_panel(r, right_filter.empty() ? L"目标列表" : L"目标列表 🔎 " + right_filter,
               right_items, right_selected, PartRightItem, 1);

    auto draw_button = [&](const Rect& b, const std::wstring& label, bool enabled, bool hot) {
        Color bbg = enabled ? t->button_bg : (dark ? 0xFF252738 : 0xFFE9ECF2);
        if (enabled && hot) bbg = t->button_hover;
        Color bfg = enabled ? t->text_primary : t->text_muted;
        D2D1_RECT_F rr = { (float)b.x, (float)b.y, (float)(b.x + b.w), (float)(b.y + b.h) };
        ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(bbg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rr.left + 0.5f, rr.top + 0.5f,
            rr.right - 0.5f, rr.bottom - 0.5f), 4.0f, 4.0f), ctx.get_brush(border), 1.0f);
        draw_text(ctx, label, style, bfg, rr.left, rr.top, (float)b.w, (float)b.h,
                  DWRITE_TEXT_ALIGNMENT_CENTER);
    };
    auto has_movable = [&](int side) {
        for (int i : rendered_indices(side)) {
            if (!is_disabled(side, i)) return true;
        }
        return false;
    };
    draw_button(move_right_rect(), L">", left_selected >= 0 && !is_disabled(0, left_selected), m_hover_part == PartMoveRight);
    draw_button(move_all_right_rect(), L">>", has_movable(0), m_hover_part == PartMoveAllRight);
    draw_button(move_left_rect(), L"<", right_selected >= 0 && !is_disabled(1, right_selected), m_hover_part == PartMoveLeft);
    draw_button(move_all_left_rect(), L"<<", has_movable(1), m_hover_part == PartMoveAllLeft);

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Transfer::on_mouse_move(int x, int y) {
    int index = -1;
    Part part = hit_part(x, y, index);
    if (part != m_hover_part || index != m_hover_index) {
        m_hover_part = part;
        m_hover_index = index;
        invalidate();
    }
}

void Transfer::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_part = PartNone;
    m_press_part = PartNone;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void Transfer::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_part = hit_part(x, y, m_press_index);
    invalidate();
}

void Transfer::on_mouse_up(int x, int y, MouseButton) {
    int index = -1;
    Part part = hit_part(x, y, index);
    if (part == m_press_part) {
        if (part == PartLeftItem && !is_disabled(0, index)) left_selected = index;
        else if (part == PartRightItem && !is_disabled(1, index)) right_selected = index;
        else if (part == PartMoveRight) move_selected_right();
        else if (part == PartMoveLeft) move_selected_left();
        else if (part == PartMoveAllRight) move_all_right();
        else if (part == PartMoveAllLeft) move_all_left();
    }
    pressed = false;
    m_press_part = PartNone;
    m_press_index = -1;
    m_hover_part = part;
    m_hover_index = index;
    invalidate();
}
