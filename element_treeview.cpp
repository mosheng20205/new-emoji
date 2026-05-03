#include "element_treeview.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

float TreeView::row_height() const {
    return (std::max)(style.font_size * 2.25f, 30.0f);
}

void TreeView::set_items(const std::vector<TreeViewItem>& values) {
    items = values;
    if (items.empty()) selected_index = -1;
    else if (selected_index >= (int)items.size()) selected_index = 0;
    if (selected_index >= 0 && !is_visible_item(selected_index)) selected_index = first_visible_index();
    invalidate();
}

void TreeView::set_selected_index(int value) {
    if (items.empty()) selected_index = -1;
    else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        selected_index = value;
        if (!is_visible_item(selected_index)) selected_index = first_visible_index();
    }
    invalidate();
}

void TreeView::set_options(bool show_checkbox, bool keyboard_navigation, bool lazy_mode) {
    m_show_checkbox = show_checkbox;
    m_keyboard_navigation = keyboard_navigation;
    m_lazy_mode = lazy_mode;
    invalidate();
}

void TreeView::set_item_expanded(int index, bool expanded) {
    if (index < 0 || index >= (int)items.size()) return;
    if (!has_children(index)) return;
    if (expanded && m_lazy_mode && items[index].lazy) request_lazy_load(index);
    items[index].expanded = expanded;
    if (!is_visible_item(selected_index)) selected_index = index;
    invalidate();
}

void TreeView::toggle_item_expanded(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    set_item_expanded(index, !items[index].expanded);
}

bool TreeView::get_item_expanded(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].expanded;
}

void TreeView::set_item_checked(int index, bool checked) {
    if (index < 0 || index >= (int)items.size()) return;
    items[index].checked = checked;
    invalidate();
}

bool TreeView::get_item_checked(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].checked;
}

void TreeView::set_item_lazy(int index, bool lazy) {
    if (index < 0 || index >= (int)items.size()) return;
    items[index].lazy = lazy;
    items[index].loading = false;
    if (!lazy && m_last_lazy_index == index) m_last_lazy_index = -1;
    invalidate();
}

bool TreeView::get_item_lazy(int index) const {
    if (index < 0 || index >= (int)items.size()) return false;
    return items[index].lazy;
}

bool TreeView::has_children(int index) const {
    if (index < 0 || index + 1 >= (int)items.size()) return false;
    return items[index + 1].level > items[index].level;
}

bool TreeView::is_visible_item(int index) const {
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

int TreeView::visible_count() const {
    int count = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_visible_item(i)) ++count;
    }
    return count;
}

int TreeView::checked_count() const {
    int count = 0;
    for (const auto& item : items) {
        if (item.checked) ++count;
    }
    return count;
}

int TreeView::lazy_count() const {
    int count = 0;
    for (const auto& item : items) {
        if (item.lazy) ++count;
    }
    return count;
}

int TreeView::item_at(int x, int y) const {
    if (x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    float rh = row_height();
    float cy = (float)style.pad_top;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_visible_item(i)) continue;
        if (y >= cy && y < cy + rh) return i;
        cy += rh;
    }
    return -1;
}

bool TreeView::is_checkbox_hit(int index, int x) const {
    if (!m_show_checkbox || index < 0 || index >= (int)items.size()) return false;
    float indent = (float)items[index].level * 18.0f;
    float ax = (float)style.pad_left + 10.0f + indent;
    float box_x = ax + 16.0f;
    return x >= (int)box_x - 3 && x <= (int)box_x + 19;
}

int TreeView::first_visible_index() const {
    for (int i = 0; i < (int)items.size(); ++i) {
        if (is_visible_item(i)) return i;
    }
    return -1;
}

int TreeView::last_visible_index() const {
    for (int i = (int)items.size() - 1; i >= 0; --i) {
        if (is_visible_item(i)) return i;
    }
    return -1;
}

int TreeView::next_visible_index(int from, int delta) const {
    if (items.empty()) return -1;
    if (from < 0) return first_visible_index();
    int i = from + delta;
    while (i >= 0 && i < (int)items.size()) {
        if (is_visible_item(i)) return i;
        i += delta;
    }
    return from;
}

int TreeView::parent_index(int index) const {
    if (index <= 0 || index >= (int)items.size()) return -1;
    int level = items[index].level;
    for (int i = index - 1; i >= 0; --i) {
        if (items[i].level < level) return i;
    }
    return -1;
}

void TreeView::request_lazy_load(int index) {
    if (index < 0 || index >= (int)items.size()) return;
    m_last_lazy_index = index;
    items[index].loading = true;
}

void TreeView::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color selected_bg = with_alpha(t->accent, dark ? 0x44 : 0x22);
    Color hover_bg = dark ? 0xFF313244 : 0xFFF5F7FA;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    float rh = row_height();
    float y = (float)style.pad_top;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (!is_visible_item(i)) continue;
        if (y >= bounds.h - style.pad_bottom) break;

        bool selected = i == selected_index;
        bool hot = i == m_hover_index;
        D2D1_RECT_F row = { (float)style.pad_left, y,
            (float)bounds.w - style.pad_right, (std::min)(y + rh, (float)bounds.h - style.pad_bottom) };
        if (selected || hot) {
            ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
                ctx.get_brush(selected ? selected_bg : hover_bg));
        }

        float indent = (float)items[i].level * 18.0f;
        float ax = (float)style.pad_left + 10.0f + indent;
        float ay = y + rh * 0.5f;
        if (has_children(i)) {
            auto* br = ctx.get_brush(muted);
            if (items[i].expanded) {
                ctx.rt->DrawLine(D2D1::Point2F(ax - 4.0f, ay - 2.0f), D2D1::Point2F(ax, ay + 3.0f), br, 1.4f);
                ctx.rt->DrawLine(D2D1::Point2F(ax, ay + 3.0f), D2D1::Point2F(ax + 5.0f, ay - 3.0f), br, 1.4f);
            } else {
                ctx.rt->DrawLine(D2D1::Point2F(ax - 2.0f, ay - 5.0f), D2D1::Point2F(ax + 3.0f, ay), br, 1.4f);
                ctx.rt->DrawLine(D2D1::Point2F(ax + 3.0f, ay), D2D1::Point2F(ax - 2.0f, ay + 5.0f), br, 1.4f);
            }
        }

        float text_x = ax + 14.0f;
        if (m_show_checkbox) {
            float box_x = ax + 16.0f;
            D2D1_RECT_F cb = D2D1::RectF(box_x, ay - 7.0f, box_x + 14.0f, ay + 7.0f);
            Color cb_border = items[i].checked ? t->accent : border;
            ctx.rt->FillRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f),
                ctx.get_brush(items[i].checked ? t->accent : bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(cb, 3.0f, 3.0f),
                ctx.get_brush(cb_border), 1.2f);
            if (items[i].checked) {
                auto* br = ctx.get_brush(0xFFFFFFFF);
                ctx.rt->DrawLine(D2D1::Point2F(box_x + 3.2f, ay),
                    D2D1::Point2F(box_x + 6.0f, ay + 3.5f), br, 1.7f);
                ctx.rt->DrawLine(D2D1::Point2F(box_x + 6.0f, ay + 3.5f),
                    D2D1::Point2F(box_x + 11.0f, ay - 4.0f), br, 1.7f);
            }
            text_x = box_x + 22.0f;
        }

        if (m_lazy_mode && items[i].lazy) {
            std::wstring badge = items[i].loading ? L"加载中..." : L"待加载";
            draw_text(ctx, badge, style, muted,
                      (float)bounds.w - style.pad_right - 70.0f, y,
                      64.0f, rh);
        }

        draw_text(ctx, items[i].label, style, selected ? t->accent : fg,
                  text_x, y, (float)bounds.w - text_x - 22.0f, rh);
        y += rh;
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void TreeView::on_mouse_move(int x, int y) {
    int idx = item_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void TreeView::on_mouse_leave() {
    hovered = false;
    pressed = false;
    m_hover_index = -1;
    m_press_index = -1;
    invalidate();
}

void TreeView::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    m_press_index = item_at(x, y);
    invalidate();
}

void TreeView::on_mouse_up(int x, int y, MouseButton) {
    int idx = item_at(x, y);
    if (idx >= 0 && idx == m_press_index) {
        selected_index = idx;
        if (is_checkbox_hit(idx, x)) {
            items[idx].checked = !items[idx].checked;
        } else if (has_children(idx)) {
            if (!items[idx].expanded && m_lazy_mode && items[idx].lazy) request_lazy_load(idx);
            items[idx].expanded = !items[idx].expanded;
            if (!is_visible_item(selected_index)) selected_index = idx;
        }
    }
    pressed = false;
    m_press_index = -1;
    m_hover_index = idx;
    invalidate();
}

void TreeView::on_key_down(int vk, int) {
    if (!m_keyboard_navigation || items.empty()) return;
    if (selected_index < 0 || !is_visible_item(selected_index)) {
        selected_index = first_visible_index();
        invalidate();
        return;
    }

    if (vk == VK_UP) selected_index = next_visible_index(selected_index, -1);
    else if (vk == VK_DOWN) selected_index = next_visible_index(selected_index, 1);
    else if (vk == VK_HOME) selected_index = first_visible_index();
    else if (vk == VK_END) selected_index = last_visible_index();
    else if (vk == VK_LEFT) {
        if (has_children(selected_index) && items[selected_index].expanded) {
            items[selected_index].expanded = false;
        } else {
            int parent = parent_index(selected_index);
            if (parent >= 0) selected_index = parent;
        }
    } else if (vk == VK_RIGHT) {
        if (has_children(selected_index)) {
            if (!items[selected_index].expanded) {
                if (m_lazy_mode && items[selected_index].lazy) request_lazy_load(selected_index);
                items[selected_index].expanded = true;
            } else {
                int child = next_visible_index(selected_index, 1);
                if (child != selected_index && parent_index(child) == selected_index) selected_index = child;
            }
        }
    } else if (vk == VK_SPACE && m_show_checkbox) {
        items[selected_index].checked = !items[selected_index].checked;
    } else if (vk == VK_RETURN && has_children(selected_index)) {
        if (!items[selected_index].expanded && m_lazy_mode && items[selected_index].lazy) {
            request_lazy_load(selected_index);
        }
        items[selected_index].expanded = !items[selected_index].expanded;
    } else {
        return;
    }
    invalidate();
}
