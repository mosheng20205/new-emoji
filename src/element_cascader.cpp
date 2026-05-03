#include "element_cascader.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

static int round_px(float v) {
    return (int)std::lround(v);
}

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

static bool path_starts_with(const std::vector<std::wstring>& path,
                             const std::vector<std::wstring>& prefix) {
    if (prefix.size() > path.size()) return false;
    for (size_t i = 0; i < prefix.size(); ++i) {
        if (path[i] != prefix[i]) return false;
    }
    return true;
}

int Cascader::row_height() const {
    int h = round_px(style.font_size * 1.9f);
    return h < 28 ? 28 : h;
}

int Cascader::column_width() const {
    int w = round_px(150.0f * style.font_size / 14.0f);
    return w < 120 ? 120 : w;
}

int Cascader::level_count() const {
    if (search_active()) return 1;
    int max_level = 1;
    for (const auto& opt : options) {
        if ((int)opt.parts.size() > max_level) max_level = (int)opt.parts.size();
    }
    int active_levels = (int)active_path.size() + 1;
    if (active_levels > max_level) active_levels = max_level;
    if (active_levels < 1) active_levels = 1;
    return active_levels;
}

int Cascader::menu_width() const {
    if (search_active()) return (std::max)(bounds.w, column_width() * 2);
    return column_width() * level_count();
}

int Cascader::menu_height() const {
    int rows = 1;
    if (search_active()) {
        rows = (int)matching_options().size();
        if (rows < 1) rows = 1;
        if (rows > 7) rows = 7;
        return rows * row_height();
    }
    for (int i = 0; i < level_count(); ++i) {
        rows = (std::max)(rows, (int)values_at_level(i).size());
    }
    if (rows > 7) rows = 7;
    return rows * row_height();
}

int Cascader::menu_y() const {
    int mh = menu_height();
    if (parent && bounds.y + bounds.h + mh + 6 > parent->bounds.h && bounds.y > mh + 6) {
        return -mh - 4;
    }
    return bounds.h + 4;
}

bool Cascader::search_active() const {
    return searchable && !search_text.empty();
}

std::wstring Cascader::join_path(const std::vector<std::wstring>& path) const {
    std::wstring text;
    for (size_t i = 0; i < path.size(); ++i) {
        if (i > 0) text += L" / ";
        text += path[i];
    }
    return text;
}

std::vector<CascaderOption> Cascader::matching_options() const {
    std::vector<CascaderOption> result;
    for (const auto& opt : options) {
        if (search_text.empty() || join_path(opt.parts).find(search_text) != std::wstring::npos) {
            result.push_back(opt);
        }
    }
    return result;
}

std::vector<std::wstring> Cascader::values_at_level(int level) const {
    if (search_active() && level == 0) {
        std::vector<std::wstring> values;
        for (const auto& opt : matching_options()) values.push_back(join_path(opt.parts));
        return values;
    }
    std::vector<std::wstring> values;
    std::vector<std::wstring> prefix;
    for (int i = 0; i < level && i < (int)active_path.size(); ++i) {
        prefix.push_back(active_path[i]);
    }
    for (const auto& opt : options) {
        if ((int)opt.parts.size() <= level) continue;
        if (!path_starts_with(opt.parts, prefix)) continue;
        const auto& value = opt.parts[level];
        if (std::find(values.begin(), values.end(), value) == values.end()) {
            values.push_back(value);
        }
    }
    return values;
}

bool Cascader::has_children(const std::vector<std::wstring>& path) const {
    for (const auto& opt : options) {
        if (opt.parts.size() > path.size() && path_starts_with(opt.parts, path)) return true;
    }
    return false;
}

bool Cascader::is_leaf_path(const std::vector<std::wstring>& path) const {
    for (const auto& opt : options) {
        if (opt.parts.size() == path.size() && path_starts_with(opt.parts, path)) return true;
    }
    return !has_children(path);
}

std::wstring Cascader::display_text() const {
    const auto& parts = selected_path.empty() ? active_path : selected_path;
    if (parts.empty()) return L"请选择";
    std::wstring text;
    for (size_t i = 0; i < parts.size(); ++i) {
        if (i > 0) text += L" / ";
        text += parts[i];
    }
    return text;
}

void Cascader::set_options(const std::vector<CascaderOption>& values) {
    options = values;
    if (active_path.empty() && !options.empty() && !options[0].parts.empty()) {
        active_path = { options[0].parts[0] };
    }
    if (selected_path.empty()) selected_path = active_path;
    invalidate();
}

void Cascader::set_selected_path(const std::vector<std::wstring>& path) {
    selected_path = path;
    active_path = path;
    if (lazy_mode && !active_path.empty() && has_children(active_path) && !is_leaf_path(active_path)) {
        last_lazy_level = (int)active_path.size();
    }
    invalidate();
}

void Cascader::set_open(bool next_open) {
    open = next_open && !options.empty();
    invalidate();
}

void Cascader::set_advanced_options(bool next_searchable, bool next_lazy_mode) {
    searchable = next_searchable;
    lazy_mode = next_lazy_mode;
    invalidate();
}

void Cascader::set_search_text(const std::wstring& text) {
    search_text = text;
    if (!search_text.empty()) open = true;
    invalidate();
}

bool Cascader::is_open() const {
    return open;
}

int Cascader::option_count() const {
    return (int)options.size();
}

int Cascader::selected_depth() const {
    return (int)selected_path.size();
}

int Cascader::active_level_count() const {
    return level_count();
}

int Cascader::matched_count() const {
    return search_active() ? (int)matching_options().size() : option_count();
}

Cascader::Part Cascader::part_at(int x, int y, int* col, int* row) const {
    if (col) *col = -1;
    if (row) *row = -1;
    if (!open) {
        if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
        return PartNone;
    }
    int my = menu_y();
    int mw = menu_width();
    int mh = menu_height();
    if (x >= 0 && y >= my && x < mw && y < my + mh) {
        int c = x / column_width();
        if (search_active()) c = 0;
        int r = (y - my) / row_height();
        if (c >= 0 && c < level_count()) {
            auto values = values_at_level(c);
            if (r >= 0 && r < (int)values.size()) {
                if (col) *col = c;
                if (row) *row = r;
                return PartOption;
            }
        }
    }
    if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) return PartMain;
    return PartNone;
}

Element* Cascader::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return part_at(lx, ly) != PartNone ? this : nullptr;
}

Element* Cascader::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    int c = -1, r = -1;
    return part_at(lx, ly, &c, &r) == PartOption ? this : nullptr;
}

void Cascader::paint(RenderContext& ctx) {
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
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(0.5f, 0.5f, (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), open || has_focus ? 1.5f : 1.0f);

    draw_text(ctx, display_text(), style, selected_path.empty() ? t->text_secondary : fg,
              (float)style.pad_left, 0.0f,
              (float)bounds.w - style.pad_left - style.pad_right - 24.0f, (float)bounds.h);
    draw_text(ctx, open ? L"▲" : L"▼", style, t->text_secondary,
              (float)bounds.w - style.pad_right - 24.0f, 0.0f, 24.0f, (float)bounds.h,
              DWRITE_TEXT_ALIGNMENT_CENTER);

    ctx.rt->SetTransform(saved);
}

void Cascader::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color menu_bg = is_dark_theme_for_window(owner_hwnd) ? 0xFF242637 : 0xFFFFFFFF;
    int my = menu_y();
    int cw = column_width();
    int rh = row_height();
    int mw = menu_width();
    int mh = menu_height();
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F menu = { 0, (float)my, (float)mw, (float)(my + mh) };
    ctx.rt->FillRoundedRectangle(D2D1::RoundedRect(menu, radius, radius), ctx.get_brush(menu_bg));
    ctx.rt->DrawRoundedRectangle(
        D2D1::RoundedRect(D2D1::RectF(menu.left + 0.5f, menu.top + 0.5f,
                                      menu.right - 0.5f, menu.bottom - 0.5f), radius, radius),
        ctx.get_brush(t->border_default), 1.0f);

    for (int c = 1; c < level_count(); ++c) {
        float x = (float)(c * cw);
        ctx.rt->DrawLine(D2D1::Point2F(x, (float)my), D2D1::Point2F(x, (float)(my + mh)),
                         ctx.get_brush(t->border_default), 1.0f);
    }

    for (int c = 0; c < level_count(); ++c) {
        auto values = values_at_level(c);
        for (int r = 0; r < (int)values.size() && r < 7; ++r) {
            float x = (float)(c * cw);
            float y = (float)(my + r * rh);
            std::vector<std::wstring> path;
            if (search_active()) {
                auto matches = matching_options();
                if (r < (int)matches.size()) path = matches[r].parts;
            } else {
                for (int i = 0; i < c && i < (int)active_path.size(); ++i) path.push_back(active_path[i]);
                path.push_back(values[r]);
            }
            bool selected = !search_active() && c < (int)active_path.size() && active_path[c] == values[r];
            bool hot = c == m_hover_col && r == m_hover_row;
            if (selected || hot) {
                D2D1_RECT_F row = { x + 2.0f, y + 1.0f, x + (float)cw - 2.0f, y + (float)rh - 1.0f };
                ctx.rt->FillRectangle(row, ctx.get_brush(selected ? with_alpha(t->accent, 0x33) : t->button_hover));
            }
            draw_text(ctx, values[r], style, selected ? t->accent : fg,
                      x + style.pad_left, y, (float)cw - style.pad_left - 24.0f, (float)rh);
            if (!search_active() && has_children(path)) {
                draw_text(ctx, L">", style, t->text_secondary, x + (float)cw - 22.0f, y, 18.0f, (float)rh,
                          DWRITE_TEXT_ALIGNMENT_CENTER);
                if (lazy_mode && c + 1 == last_lazy_level) {
                    draw_text(ctx, L"⏳", style, t->text_secondary, x + (float)cw - 42.0f, y, 18.0f, (float)rh,
                              DWRITE_TEXT_ALIGNMENT_CENTER);
                }
            }
        }
    }

    ctx.rt->SetTransform(saved);
}

void Cascader::on_mouse_move(int x, int y) {
    int c = -1, r = -1;
    Part p = part_at(x, y, &c, &r);
    if (p != PartOption) {
        c = -1;
        r = -1;
    }
    if (c != m_hover_col || r != m_hover_row) {
        m_hover_col = c;
        m_hover_row = r;
        invalidate();
    }
}

void Cascader::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_col = -1;
    m_hover_row = -1;
    m_press_col = -1;
    m_press_row = -1;
    invalidate();
}

void Cascader::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y, &m_press_col, &m_press_row);
    pressed = true;
    invalidate();
}

void Cascader::on_mouse_up(int x, int y, MouseButton) {
    int c = -1, r = -1;
    Part p = part_at(x, y, &c, &r);
    if (p == PartMain && m_press_part == PartMain) {
        open = !open;
    } else if (p == PartOption && m_press_part == PartOption && c == m_press_col && r == m_press_row) {
        if (search_active()) {
            auto matches = matching_options();
            if (r >= 0 && r < (int)matches.size()) {
                selected_path = matches[r].parts;
                active_path = selected_path;
                open = false;
            }
            m_press_part = PartNone;
            m_press_col = -1;
            m_press_row = -1;
            pressed = false;
            invalidate();
            return;
        }
        auto values = values_at_level(c);
        if (r >= 0 && r < (int)values.size()) {
            if ((int)active_path.size() > c) active_path.resize(c);
            active_path.push_back(values[r]);
            if (is_leaf_path(active_path)) {
                selected_path = active_path;
                open = false;
            } else if (lazy_mode) {
                last_lazy_level = (int)active_path.size();
            }
        }
    }
    m_press_part = PartNone;
    m_press_col = -1;
    m_press_row = -1;
    pressed = false;
    invalidate();
}

void Cascader::on_key_down(int vk, int) {
    if (vk == VK_RETURN || vk == VK_SPACE) {
        open = !open;
    } else if (vk == VK_ESCAPE) {
        open = false;
    }
    invalidate();
}

void Cascader::on_blur() {
    has_focus = false;
    open = false;
    m_hover_col = -1;
    m_hover_row = -1;
    m_press_part = PartNone;
    invalidate();
}
