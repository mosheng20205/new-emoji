#include "element_treeselect.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color ts_with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void ts_draw_text(RenderContext& ctx, const std::wstring& text,
                         const ElementStyle& style, Color color,
                         float x, float y, float w, float h,
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

int TreeSelect::popup_width() const {
    return (std::max)(bounds.w, 280);
}

int TreeSelect::popup_height() const {
    return searchable ? 250 : 220;
}

int TreeSelect::popup_y() const {
    int ph = popup_height();
    if (parent && bounds.y + bounds.h + ph + 6 > parent->bounds.h && bounds.y > ph + 6) {
        return -ph - 4;
    }
    return bounds.h + 4;
}

int TreeSelect::row_height() const {
    int h = (int)(style.font_size * 2.1f);
    return h < 30 ? 30 : h;
}

void TreeSelect::set_items(const std::vector<TreeViewItem>& values) {
    items = values;
    if (items.empty()) selected_index = -1;
    else if (selected_index < 0 || selected_index >= (int)items.size()) selected_index = 0;
    sync_single_from_multi();
    invalidate();
}

void TreeSelect::set_selected_index(int value) {
    if (items.empty()) selected_index = -1;
    else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        selected_index = value;
        if (!multiple) selected_indices = { selected_index };
    }
    invalidate();
}

void TreeSelect::set_open(bool next_open) {
    open = next_open;
    invalidate();
}

bool TreeSelect::is_open() const {
    return open;
}

void TreeSelect::set_options(bool next_multiple, bool next_clearable, bool next_searchable) {
    multiple = next_multiple;
    clearable = next_clearable;
    searchable = next_searchable;
    if (!multiple && selected_indices.size() > 1) {
        selected_indices = selected_index >= 0 ? std::vector<int>{ selected_index } : std::vector<int>{};
    } else if (multiple && selected_indices.empty() && selected_index >= 0) {
        selected_indices = { selected_index };
    }
    invalidate();
}

void TreeSelect::set_search_text(const std::wstring& value) {
    search_text = value;
    m_hover_index = -1;
    if (!search_text.empty()) open = true;
    invalidate();
}

void TreeSelect::clear_selection() {
    selected_index = -1;
    selected_indices.clear();
    invalidate();
}

void TreeSelect::set_selected_items(const std::vector<int>& indices) {
    selected_indices.clear();
    for (int index : indices) {
        if (index >= 0 && index < (int)items.size() &&
            std::find(selected_indices.begin(), selected_indices.end(), index) == selected_indices.end()) {
            selected_indices.push_back(index);
        }
    }
    sync_single_from_multi();
    invalidate();
}

int TreeSelect::selected_count() const {
    return multiple ? (int)selected_indices.size() : (selected_index >= 0 ? 1 : 0);
}

int TreeSelect::selected_item(int position) const {
    if (multiple) {
        if (position < 0 || position >= (int)selected_indices.size()) return -1;
        return selected_indices[position];
    }
    return position == 0 ? selected_index : -1;
}

int TreeSelect::matched_count() const {
    int count = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_rendered_item(i)) ++count;
    }
    return count;
}

void TreeSelect::set_item_expanded(int index, bool expanded) {
    if (index < 0 || index >= (int)items.size()) return;
    if (!has_children(index)) return;
    items[index].expanded = expanded;
    invalidate();
}

void TreeSelect::toggle_item_expanded(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    set_item_expanded(index, !items[index].expanded);
}

bool TreeSelect::get_item_expanded(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].expanded;
}

bool TreeSelect::has_children(int index) const {
    if (index < 0 || index + 1 >= (int)items.size()) return false;
    return items[index + 1].level > items[index].level;
}

bool TreeSelect::is_visible_item(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    int level = items[index].level;
    for (int i = index - 1; i >= 0; --i) {
        if (items[i].level < level) {
            if (!items[i].expanded) return false;
            level = items[i].level;
        }
    }
    return true;
}

bool TreeSelect::matches_filter(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    if (search_text.empty()) return true;
    return items[index].label.find(search_text) != std::wstring::npos;
}

bool TreeSelect::is_rendered_item(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    if (!matches_filter(index)) return false;
    return search_text.empty() ? is_visible_item(index) : true;
}

int TreeSelect::item_at(int x, int y) const {
    if (!open) return -1;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();
    if (x < 0 || x >= pw || y < py || y >= py + ph) return -1;
    int cy = py + style.pad_top + (searchable ? row_height() : 0);
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_rendered_item(i)) continue;
        if (y >= cy && y < cy + row_height()) return i;
        cy += row_height();
        if (cy >= py + ph - style.pad_bottom) break;
    }
    return -1;
}

std::wstring TreeSelect::selected_text() const {
    if (multiple) {
        if (selected_indices.empty()) return L"请选择";
        if (selected_indices.size() == 1) {
            int index = selected_indices[0];
            if (index >= 0 && index < (int)items.size()) return items[index].label;
        }
        return L"已选择 " + std::to_wstring(selected_indices.size()) + L" 项";
    }
    if (selected_index >= 0 && selected_index < (int)items.size()) return items[selected_index].label;
    return L"请选择";
}

void TreeSelect::sync_single_from_multi() {
    if (!selected_indices.empty()) {
        selected_index = selected_indices[0];
    } else if (selected_index >= 0 && selected_index < (int)items.size()) {
        if (multiple) selected_indices = { selected_index };
    } else {
        selected_index = items.empty() ? -1 : 0;
        if (multiple && selected_index >= 0) selected_indices = { selected_index };
    }
}

bool TreeSelect::is_selected_multi(int index) const {
    if (multiple) {
        return std::find(selected_indices.begin(), selected_indices.end(), index) != selected_indices.end();
    }
    return index == selected_index;
}

void TreeSelect::toggle_selected_multi(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    if (!multiple) {
        selected_index = index;
        selected_indices = { index };
        return;
    }
    auto it = std::find(selected_indices.begin(), selected_indices.end(), index);
    if (it == selected_indices.end()) selected_indices.push_back(index);
    else selected_indices.erase(it);
    selected_index = selected_indices.empty() ? -1 : selected_indices[0];
}

int TreeSelect::first_rendered_index() const {
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_rendered_item(i)) return i;
    }
    return -1;
}

int TreeSelect::next_rendered_index(int from, int delta) const {
    if (items.empty()) return -1;
    if (from < 0) return first_rendered_index();
    int i = from + delta;
    while (i >= 0 && i < (int)items.size()) {
        if (is_rendered_item(i)) return i;
        i += delta;
    }
    return from;
}

Element* TreeSelect::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (item_at(lx, ly) >= 0) return this;
    if (lx >= 0 && ly >= 0 && lx < bounds.w && ly < bounds.h) return this;
    return nullptr;
}

Element* TreeSelect::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return item_at(lx, ly) >= 0 ? this : nullptr;
}

void TreeSelect::paint(RenderContext& ctx) {
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

    float arrow_w = 24.0f;
    float clear_w = (clearable && selected_count() > 0) ? 22.0f : 0.0f;
    ts_draw_text(ctx, selected_text(), style, fg,
                 (float)style.pad_left, 0.0f,
                 (float)bounds.w - style.pad_left - style.pad_right - arrow_w - clear_w,
                 (float)bounds.h);
    if (clear_w > 0.0f) {
        ts_draw_text(ctx, L"×", style, t->text_secondary,
                     (float)bounds.w - style.pad_right - arrow_w - clear_w, 0.0f,
                     clear_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    ts_draw_text(ctx, open ? L"⌃" : L"⌄", style, t->text_secondary,
                 (float)bounds.w - style.pad_right - arrow_w, 0.0f,
                 arrow_w, (float)bounds.h, DWRITE_TEXT_ALIGNMENT_CENTER);

    ctx.rt->SetTransform(saved);
}

void TreeSelect::paint_overlay(RenderContext& ctx) {
    if (!visible || !open || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFF5F7FA;
    int py = popup_y();
    int pw = popup_width();
    int ph = popup_height();

    D2D1_RECT_F rect = { 0, (float)py, (float)pw, (float)(py + ph) };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f, 4.0f), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f, 4.0f),
        ctx.get_brush(t->border_default), 1.0f);

    int cy = py + style.pad_top;
    int rh = row_height();
    if (searchable) {
        D2D1_RECT_F search_rect = {
            (float)style.pad_left + 6.0f, (float)cy + 4.0f,
            (float)pw - style.pad_right - 6.0f, (float)(cy + rh - 4)
        };
        ctx.rt->FillRoundedRectangle(ROUNDED(search_rect, 4.0f, 4.0f),
            ctx.get_brush(dark ? 0xFF1D1F2E : 0xFFF7F8FA));
        ctx.rt->DrawRoundedRectangle(ROUNDED(search_rect, 4.0f, 4.0f),
            ctx.get_brush(t->border_default), 1.0f);
        std::wstring hint = search_text.empty() ? L"🔍 搜索节点" : L"🔍 " + search_text;
        ts_draw_text(ctx, hint, style, search_text.empty() ? t->text_secondary : fg,
                     search_rect.left + 10.0f, (float)cy,
                     search_rect.right - search_rect.left - 20.0f, (float)rh);
        cy += rh;
    }

    int rendered = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_rendered_item(i)) continue;
        ++rendered;
        if (cy + rh > py + ph - style.pad_bottom) break;
        bool selected = is_selected_multi(i);
        bool hot = i == m_hover_index;
        D2D1_RECT_F row = { (float)style.pad_left, (float)cy,
            (float)pw - style.pad_right, (float)(cy + rh) };
        if (selected || hot) {
            ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
                ctx.get_brush(selected ? ts_with_alpha(t->accent, 0x33) : hover_bg));
        }
        float indent = (float)items[i].level * 18.0f;
        float x = (float)style.pad_left + 8.0f + indent;
        if (has_children(i)) {
            ts_draw_text(ctx, items[i].expanded ? L"⌄" : L"›", style, t->text_secondary,
                         x, (float)cy, 16.0f, (float)rh, DWRITE_TEXT_ALIGNMENT_CENTER);
            x += 18.0f;
        } else {
            x += 18.0f;
        }
        if (multiple) {
            D2D1_RECT_F cb = D2D1::RectF(x, (float)cy + rh * 0.5f - 7.0f,
                x + 14.0f, (float)cy + rh * 0.5f + 7.0f);
            ctx.rt->FillRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f),
                ctx.get_brush(selected ? t->accent : bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f),
                ctx.get_brush(selected ? t->accent : t->border_default), 1.1f);
            if (selected) {
                auto* br = ctx.get_brush(0xFFFFFFFF);
                float mid = (float)cy + rh * 0.5f;
                ctx.rt->DrawLine(D2D1::Point2F(x + 3.0f, mid),
                    D2D1::Point2F(x + 6.0f, mid + 3.5f), br, 1.6f);
                ctx.rt->DrawLine(D2D1::Point2F(x + 6.0f, mid + 3.5f),
                    D2D1::Point2F(x + 11.0f, mid - 4.0f), br, 1.6f);
            }
            x += 22.0f;
        }
        ts_draw_text(ctx, items[i].label, style, selected ? t->accent : fg,
                     x, (float)cy, (float)pw - x - style.pad_right, (float)rh);
        cy += rh;
    }
    if (rendered == 0) {
        ts_draw_text(ctx, L"🫥 没有匹配的节点", style, t->text_secondary,
                     0.0f, (float)cy + 12.0f, (float)pw, (float)rh,
                     DWRITE_TEXT_ALIGNMENT_CENTER);
    }

    ctx.rt->SetTransform(saved);
}

void TreeSelect::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void TreeSelect::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    m_press_part = PartNone;
    invalidate();
}

void TreeSelect::on_mouse_down(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (idx >= 0) {
        m_press_part = PartItem;
        m_press_index = idx;
    } else if (x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        m_press_part = PartMain;
        m_press_index = -1;
    } else {
        m_press_part = PartNone;
        m_press_index = -1;
    }
    pressed = true;
    invalidate();
}

void TreeSelect::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (m_press_part == PartMain && x >= 0 && y >= 0 && x < bounds.w && y < bounds.h) {
        float clear_left = (float)bounds.w - style.pad_right - 46.0f;
        float clear_right = clear_left + 22.0f;
        if (clearable && selected_count() > 0 && x >= clear_left && x <= clear_right) {
            clear_selection();
        } else {
            open = !open;
        }
    } else if (m_press_part == PartItem && idx >= 0 && idx == m_press_index) {
        if (has_children(idx)) {
            items[idx].expanded = !items[idx].expanded;
        } else {
            toggle_selected_multi(idx);
            if (!multiple) open = false;
        }
    }
    pressed = false;
    m_press_part = PartNone;
    m_press_index = -1;
    m_hover_index = idx;
    invalidate();
}

void TreeSelect::on_key_down(int vk, int) {
    if (searchable && open && vk == VK_BACK) {
        if (!search_text.empty()) search_text.pop_back();
    } else if (clearable && vk == VK_DELETE) {
        clear_selection();
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        if (open && selected_index >= 0 && !has_children(selected_index) && vk == VK_SPACE) {
            toggle_selected_multi(selected_index);
        } else if (open && selected_index >= 0 && has_children(selected_index) && vk == VK_RETURN) {
            items[selected_index].expanded = !items[selected_index].expanded;
        } else {
            open = !open;
        }
    } else if (vk == VK_ESCAPE) {
        if (!search_text.empty()) search_text.clear();
        open = false;
    } else if (vk == VK_DOWN) {
        int next = next_rendered_index(selected_index, 1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_UP) {
        int next = next_rendered_index(selected_index, -1);
        if (next >= 0) set_selected_index(next);
    } else if (vk == VK_HOME) {
        int first = first_rendered_index();
        if (first >= 0) set_selected_index(first);
    } else if (vk == VK_END) {
        int last = selected_index;
        for (int i = 0; i < (int)items.size(); ++i) {
            if (is_rendered_item(i)) last = i;
        }
        if (last >= 0) set_selected_index(last);
    }
    invalidate();
}

void TreeSelect::on_char(wchar_t ch) {
    if (!searchable) return;
    if (!open) open = true;
    if (ch >= 32 && ch != 127) {
        search_text.push_back(ch);
        invalidate();
    }
}

void TreeSelect::on_blur() {
    has_focus = false;
    open = false;
    m_hover_index = -1;
    m_press_part = PartNone;
    invalidate();
}
