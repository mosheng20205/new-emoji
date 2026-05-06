#include "element_transfer.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cwctype>
#include <set>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static std::wstring lower_copy(const std::wstring& text) {
    std::wstring out = text;
    std::transform(out.begin(), out.end(), out.begin(),
        [](wchar_t ch) { return (wchar_t)towlower(ch); });
    return out;
}

static void replace_all(std::wstring& text, const std::wstring& key, const std::wstring& value) {
    if (key.empty()) return;
    size_t pos = 0;
    while ((pos = text.find(key, pos)) != std::wstring::npos) {
        text.replace(pos, key.size(), value);
        pos += value.size();
    }
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

static TransferItem simple_item(const std::wstring& text, int index) {
    TransferItem item;
    item.key = text.empty() ? std::to_wstring(index) : text;
    item.label = text;
    item.value = item.key;
    return item;
}

float Transfer::row_height() const {
    return (std::max)(style.font_size * 2.25f, 32.0f);
}

float Transfer::header_height() const {
    return (std::max)(style.font_size * 2.6f, 38.0f);
}

float Transfer::filter_height() const {
    return filterable ? 40.0f : 0.0f;
}

float Transfer::footer_height() const {
    return show_footer ? 40.0f : 0.0f;
}

Rect Transfer::left_rect() const {
    int gap = 132;
    int panel_w = (bounds.w - style.pad_left - style.pad_right - gap) / 2;
    if (panel_w < 120) panel_w = 120;
    return { style.pad_left, style.pad_top, panel_w, bounds.h - style.pad_top - style.pad_bottom };
}

Rect Transfer::right_rect() const {
    Rect l = left_rect();
    int gap = 132;
    return { l.x + l.w + gap, l.y, l.w, l.h };
}

Rect Transfer::move_right_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 12, l.y + l.h / 2 - 70, 108, 30 };
}

Rect Transfer::move_left_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 12, l.y + l.h / 2 + 8, 108, 30 };
}

Rect Transfer::move_all_right_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 12, l.y + l.h / 2 - 34, 108, 30 };
}

Rect Transfer::move_all_left_rect() const {
    Rect l = left_rect();
    return { l.x + l.w + 12, l.y + l.h / 2 + 44, 108, 30 };
}

Rect Transfer::filter_rect(int side) const {
    Rect p = side == 1 ? right_rect() : left_rect();
    int margin = 10;
    return { p.x + margin, p.y + (int)header_height() + 6, p.w - margin * 2, 28 };
}

Rect Transfer::footer_rect(int side) const {
    Rect p = side == 1 ? right_rect() : left_rect();
    return { p.x, p.y + p.h - (int)footer_height(), p.w, (int)footer_height() };
}

float Transfer::rows_top(int) const {
    return header_height() + filter_height();
}

float Transfer::rows_bottom(int side) const {
    Rect p = side == 1 ? right_rect() : left_rect();
    return (float)p.h - footer_height();
}

void Transfer::set_items(const std::vector<std::wstring>& left, const std::vector<std::wstring>& right) {
    left_items.clear();
    right_items.clear();
    for (int i = 0; i < (int)left.size(); ++i) left_items.push_back(simple_item(left[i], i));
    for (int i = 0; i < (int)right.size(); ++i) right_items.push_back(simple_item(right[i], i));
    left_selected = left_items.empty() ? -1 : 0;
    right_selected = right_items.empty() ? -1 : 0;
    normalize_state();
    invalidate();
}

void Transfer::set_data_ex(const std::vector<TransferItem>& items, const std::vector<std::wstring>& target_keys) {
    std::set<std::wstring> target(target_keys.begin(), target_keys.end());
    left_items.clear();
    right_items.clear();
    for (const auto& source : items) {
        TransferItem item = source;
        if (item.label.empty()) item.label = !item.desc.empty() ? item.desc : item.key;
        if (item.key.empty()) item.key = !item.value.empty() ? item.value : item.label;
        if (item.value.empty()) item.value = item.key;
        bool in_target = target.count(item.key) || target.count(item.value) || target.count(item.label);
        if (in_target) right_items.push_back(item);
        else left_items.push_back(item);
    }
    left_selected = left_items.empty() ? -1 : 0;
    right_selected = right_items.empty() ? -1 : 0;
    normalize_state();
    invalidate();
}

void Transfer::move_indices(int from_side, std::vector<int> indices) {
    auto& from = from_side == 1 ? right_items : left_items;
    auto& to = from_side == 1 ? left_items : right_items;
    std::sort(indices.begin(), indices.end());
    indices.erase(std::unique(indices.begin(), indices.end()), indices.end());

    std::vector<TransferItem> moving;
    for (int i : indices) {
        if (i >= 0 && i < (int)from.size() && !from[i].disabled) moving.push_back(from[i]);
    }
    if (moving.empty()) return;
    for (auto& item : moving) {
        item.checked = false;
        to.push_back(item);
    }
    for (int n = (int)indices.size() - 1; n >= 0; --n) {
        int i = indices[n];
        if (i >= 0 && i < (int)from.size() && !from[i].disabled) from.erase(from.begin() + i);
    }
    if (from_side == 1) {
        right_selected = right_items.empty() ? -1 : (std::min)(right_selected, (int)right_items.size() - 1);
        left_selected = (int)left_items.size() - 1;
    } else {
        left_selected = left_items.empty() ? -1 : (std::min)(left_selected, (int)left_items.size() - 1);
        right_selected = (int)right_items.size() - 1;
    }
    normalize_state();
    invalidate();
}

void Transfer::move_selected_right() {
    std::vector<int> indices;
    if (multiple && any_checked(0)) {
        for (int i = 0; i < (int)left_items.size(); ++i) {
            if (left_items[i].checked) indices.push_back(i);
        }
    } else if (left_selected >= 0) {
        indices.push_back(left_selected);
    }
    move_indices(0, indices);
}

void Transfer::move_selected_left() {
    std::vector<int> indices;
    if (multiple && any_checked(1)) {
        for (int i = 0; i < (int)right_items.size(); ++i) {
            if (right_items[i].checked) indices.push_back(i);
        }
    } else if (right_selected >= 0) {
        indices.push_back(right_selected);
    }
    move_indices(1, indices);
}

void Transfer::move_all_right() {
    move_indices(0, rendered_indices(0));
}

void Transfer::move_all_left() {
    move_indices(1, rendered_indices(1));
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
    normalize_state();
    invalidate();
}

void Transfer::set_item_disabled(int side, int index, bool disabled) {
    auto& data = side == 1 ? right_items : left_items;
    if (index < 0 || index >= (int)data.size()) return;
    data[index].disabled = disabled;
    if (disabled) {
        data[index].checked = false;
        if (side == 1 && right_selected == index) right_selected = -1;
        if (side != 1 && left_selected == index) left_selected = -1;
    }
    normalize_state();
    invalidate();
}

bool Transfer::get_item_disabled(int side, int index) const {
    return is_disabled(side, index);
}

void Transfer::set_checked_keys(const std::vector<std::wstring>& left_keys,
                                const std::vector<std::wstring>& right_keys) {
    std::set<std::wstring> left_set(left_keys.begin(), left_keys.end());
    std::set<std::wstring> right_set(right_keys.begin(), right_keys.end());
    for (auto& item : left_items) {
        std::wstring key = primary_key(item);
        item.checked = !item.disabled && (left_set.count(key) || left_set.count(item.value) || left_set.count(item.label));
    }
    for (auto& item : right_items) {
        std::wstring key = primary_key(item);
        item.checked = !item.disabled && (right_set.count(key) || right_set.count(item.value) || right_set.count(item.label));
    }
    invalidate();
}

void Transfer::set_options(bool filterable_value, bool multiple_value, bool show_footer_value,
                           bool show_select_all_value, bool show_count_value, int render_mode_value) {
    filterable = filterable_value;
    multiple = multiple_value;
    show_footer = show_footer_value;
    show_select_all = show_select_all_value;
    show_count = show_count_value;
    render_mode = render_mode_value;
    if (!multiple) {
        for (auto& item : left_items) item.checked = false;
        for (auto& item : right_items) item.checked = false;
    }
    invalidate();
}

void Transfer::set_titles(const std::wstring& left, const std::wstring& right) {
    if (!left.empty()) left_title = left;
    if (!right.empty()) right_title = right;
    invalidate();
}

void Transfer::set_button_texts(const std::wstring& left, const std::wstring& right) {
    if (!left.empty()) move_left_text = left;
    if (!right.empty()) move_right_text = right;
    invalidate();
}

void Transfer::set_format(const std::wstring& no_checked, const std::wstring& has_checked) {
    if (!no_checked.empty()) no_checked_format = no_checked;
    if (!has_checked.empty()) has_checked_format = has_checked;
    invalidate();
}

void Transfer::set_item_template(const std::wstring& templ) {
    item_template = templ.empty() ? L"{label}" : templ;
    invalidate();
}

void Transfer::set_footer_texts(const std::wstring& left, const std::wstring& right) {
    if (!left.empty()) left_footer_text = left;
    if (!right.empty()) right_footer_text = right;
    invalidate();
}

void Transfer::set_filter_placeholder(const std::wstring& text) {
    if (!text.empty()) filter_placeholder = text;
    invalidate();
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

int Transfer::checked_count(int side) const {
    const auto& data = side == 1 ? right_items : left_items;
    int count = 0;
    for (const auto& item : data) {
        if (item.checked) ++count;
    }
    return count;
}

bool Transfer::any_checked(int side) const {
    return checked_count(side) > 0;
}

std::wstring Transfer::primary_key(const TransferItem& item) const {
    if (!item.key.empty()) return item.key;
    if (!item.value.empty()) return item.value;
    return item.label;
}

std::wstring Transfer::value_keys_text() const {
    std::wstring result;
    for (const auto& item : right_items) {
        if (!result.empty()) result += L"|";
        result += primary_key(item);
    }
    return result;
}

std::wstring Transfer::text_value(int text_type) const {
    switch (text_type) {
    case 0: return left_title;
    case 1: return right_title;
    case 2: return move_left_text;
    case 3: return move_right_text;
    case 4: return no_checked_format;
    case 5: return has_checked_format;
    case 6: return item_template;
    case 7: return left_footer_text;
    case 8: return right_footer_text;
    case 9: return filter_placeholder;
    default: return value_keys_text();
    }
}

std::wstring Transfer::display_text(const TransferItem& item) const {
    if (item_template != L"{label}") {
        std::wstring out = item_template;
        replace_all(out, L"{key}", item.key);
        replace_all(out, L"{label}", item.label);
        replace_all(out, L"{value}", item.value);
        replace_all(out, L"{desc}", item.desc);
        replace_all(out, L"{pinyin}", item.pinyin);
        return out;
    }
    if (render_mode == 1) return primary_key(item) + L" - " + item.label;
    if (render_mode == 2 && !item.desc.empty()) return item.label + L" · " + item.desc;
    return item.label;
}

std::wstring Transfer::side_format_text(int side) const {
    int checked = checked_count(side);
    int total = side == 1 ? right_count() : left_count();
    std::wstring text = checked > 0 ? has_checked_format : no_checked_format;
    replace_all(text, L"${checked}", std::to_wstring(checked));
    replace_all(text, L"${total}", std::to_wstring(total));
    replace_all(text, L"${matched}", std::to_wstring(matched_count(side)));
    return text;
}

bool Transfer::matches_filter(int side, int index) const {
    const auto& data = side == 1 ? right_items : left_items;
    const auto& filter = side == 1 ? right_filter : left_filter;
    if (index < 0 || index >= (int)data.size()) return false;
    if (filter.empty()) return true;
    std::wstring query = lower_copy(filter);
    const TransferItem& item = data[index];
    std::wstring haystack = lower_copy(
        item.key + L" " + item.label + L" " + item.value + L" " + item.desc + L" " + item.pinyin);
    return haystack.find(query) != std::wstring::npos;
}

bool Transfer::is_disabled(int side, int index) const {
    const auto& data = side == 1 ? right_items : left_items;
    if (index < 0 || index >= (int)data.size()) return true;
    return data[index].disabled;
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

void Transfer::toggle_item_checked(int side, int index) {
    auto& data = side == 1 ? right_items : left_items;
    if (index < 0 || index >= (int)data.size() || data[index].disabled) return;
    if (!multiple) {
        if (side == 1) right_selected = index;
        else left_selected = index;
        return;
    }
    data[index].checked = !data[index].checked;
    if (side == 1) right_selected = index;
    else left_selected = index;
}

void Transfer::set_all_checked(int side, bool checked) {
    auto& data = side == 1 ? right_items : left_items;
    for (int i : rendered_indices(side)) {
        if (!data[i].disabled) data[i].checked = checked;
    }
    invalidate();
}

Transfer::Part Transfer::hit_part(int x, int y, int& index) const {
    index = -1;
    if (move_right_rect().contains(x, y)) return PartMoveRight;
    if (move_left_rect().contains(x, y)) return PartMoveLeft;
    if (move_all_right_rect().contains(x, y)) return PartMoveAllRight;
    if (move_all_left_rect().contains(x, y)) return PartMoveAllLeft;

    Rect l = left_rect();
    Rect r = right_rect();
    if (filterable && filter_rect(0).contains(x, y)) return PartLeftFilter;
    if (filterable && filter_rect(1).contains(x, y)) return PartRightFilter;
    if (show_footer && footer_rect(0).contains(x, y)) return PartLeftFooter;
    if (show_footer && footer_rect(1).contains(x, y)) return PartRightFooter;
    if (multiple && show_select_all && l.contains(x, y) && y < l.y + header_height()) return PartLeftSelectAll;
    if (multiple && show_select_all && r.contains(x, y) && y < r.y + header_height()) return PartRightSelectAll;

    float rh = row_height();
    if (l.contains(x, y)) {
        float top = (float)l.y + rows_top(0);
        float bottom = (float)l.y + rows_bottom(0);
        if (y >= top && y < bottom) {
            int pos = (int)((y - top) / rh);
            auto visible = rendered_indices(0);
            index = pos >= 0 && pos < (int)visible.size() ? visible[pos] : -1;
            return index >= 0 ? PartLeftItem : PartNone;
        }
    }
    if (r.contains(x, y)) {
        float top = (float)r.y + rows_top(1);
        float bottom = (float)r.y + rows_bottom(1);
        if (y >= top && y < bottom) {
            int pos = (int)((y - top) / rh);
            auto visible = rendered_indices(1);
            index = pos >= 0 && pos < (int)visible.size() ? visible[pos] : -1;
            return index >= 0 ? PartRightItem : PartNone;
        }
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
    Color input_bg = dark ? 0xFF202233 : 0xFFFFFFFF;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    Color muted = t->text_secondary;
    Color hover_bg = dark ? 0xFF313244 : 0xFFEAF2FF;
    Color selected_bg = with_alpha(t->accent, dark ? 0x44 : 0x22);
    Color checked_bg = with_alpha(t->accent, dark ? 0x66 : 0x33);

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    auto draw_checkbox = [&](float x, float y, bool checked, bool disabled) {
        D2D1_RECT_F box = { x, y, x + 15.0f, y + 15.0f };
        Color fill = checked ? t->accent : (disabled ? (dark ? 0xFF2A2C38 : 0xFFF0F2F5) : input_bg);
        Color stroke = disabled ? t->text_muted : (checked ? t->accent : border);
        ctx.rt->FillRoundedRectangle(ROUNDED(box, 3.0f, 3.0f), ctx.get_brush(fill));
        ctx.rt->DrawRoundedRectangle(ROUNDED(box, 3.0f, 3.0f), ctx.get_brush(stroke), 1.0f);
        if (checked) {
            draw_text(ctx, L"✓", style, 0xFFFFFFFF, x, y - 1.0f, 15.0f, 15.0f,
                      DWRITE_TEXT_ALIGNMENT_CENTER, 0.92f);
        }
    };

    auto draw_panel = [&](const Rect& p, const std::wstring& title,
                          const std::vector<TransferItem>& data, int selected, Part part, int side) {
        float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;
        D2D1_RECT_F rect = { (float)p.x, (float)p.y, (float)(p.x + p.w), (float)(p.y + p.h) };
        ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
            rect.right - 0.5f, rect.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

        float hh = header_height();
        D2D1_RECT_F header = { rect.left, rect.top, rect.right, rect.top + hh };
        ctx.rt->FillRectangle(header, ctx.get_brush(header_bg));
        ctx.rt->DrawLine(D2D1::Point2F(rect.left, rect.top + hh),
                         D2D1::Point2F(rect.right, rect.top + hh),
                         ctx.get_brush(border), 1.0f);

        if (multiple && show_select_all) {
            bool all_checked = true;
            bool has_enabled = false;
            for (int i : rendered_indices(side)) {
                if (!is_disabled(side, i)) {
                    has_enabled = true;
                    if (!data[i].checked) all_checked = false;
                }
            }
            draw_checkbox(rect.left + 12.0f, rect.top + (hh - 15.0f) / 2.0f,
                          has_enabled && all_checked, !has_enabled);
        }

        float title_x = rect.left + (multiple && show_select_all ? 36.0f : 12.0f);
        std::wstring title_text = title;
        if (show_count) title_text += L"  " + side_format_text(side);
        draw_text(ctx, title_text, style, fg, title_x, rect.top, (float)p.w - (title_x - rect.left) - 12.0f, hh);

        if (filterable) {
            Rect f = filter_rect(side);
            D2D1_RECT_F fr = { (float)f.x, (float)f.y, (float)(f.x + f.w), (float)(f.y + f.h) };
            ctx.rt->FillRoundedRectangle(ROUNDED(fr, 4.0f, 4.0f), ctx.get_brush(input_bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(fr, 4.0f, 4.0f),
                ctx.get_brush(m_active_filter_side == side ? t->accent : border), 1.0f);
            const std::wstring& value = side == 1 ? right_filter : left_filter;
            draw_text(ctx, value.empty() ? filter_placeholder : L"🔎 " + value, style,
                      value.empty() ? muted : fg, fr.left + 10.0f, fr.top, fr.right - fr.left - 20.0f, fr.bottom - fr.top);
        }

        float rh = row_height();
        auto visible = rendered_indices(side);
        int row_index = 0;
        float top = rect.top + rows_top(side);
        float bottom = rect.top + rows_bottom(side);
        for (int i : visible) {
            float y = top + rh * (float)row_index++;
            if (y + 2.0f >= bottom) break;
            bool sel = i == selected;
            bool hot = m_hover_part == part && i == m_hover_index;
            bool disabled = is_disabled(side, i);
            bool checked = data[i].checked;
            if (sel || hot || checked) {
                D2D1_RECT_F row = { rect.left + 6.0f, y + 2.0f, rect.right - 6.0f, y + rh - 2.0f };
                ctx.rt->FillRoundedRectangle(ROUNDED(row, 4.0f, 4.0f),
                    ctx.get_brush(checked ? checked_bg : (sel ? selected_bg : hover_bg)));
            }
            float text_x = rect.left + 14.0f;
            if (multiple) {
                draw_checkbox(rect.left + 14.0f, y + (rh - 15.0f) / 2.0f, checked, disabled);
                text_x = rect.left + 38.0f;
            }
            Color row_color = disabled ? muted : (sel ? t->accent : fg);
            std::wstring prefix = disabled ? L"🚫 " : L"";
            draw_text(ctx, prefix + display_text(data[i]), style, row_color,
                      text_x, y, rect.right - text_x - 12.0f, rh);
        }
        if (visible.empty()) {
            draw_text(ctx, L"🫥 没有匹配项", style, muted,
                      rect.left, top + 12.0f, (float)p.w, rh,
                      DWRITE_TEXT_ALIGNMENT_CENTER);
        }
        if (show_footer) {
            Rect f = footer_rect(side);
            D2D1_RECT_F footer = { (float)f.x, (float)f.y, (float)(f.x + f.w), (float)(f.y + f.h) };
            ctx.rt->FillRectangle(footer, ctx.get_brush(header_bg));
            ctx.rt->DrawLine(D2D1::Point2F(footer.left, footer.top),
                             D2D1::Point2F(footer.right, footer.top), ctx.get_brush(border), 1.0f);
            draw_text(ctx, side == 1 ? right_footer_text : left_footer_text, style, fg,
                      footer.left + 12.0f, footer.top, footer.right - footer.left - 24.0f, footer.bottom - footer.top);
        }
    };

    Rect l = left_rect();
    Rect r = right_rect();
    draw_panel(l, left_title, left_items, left_selected, PartLeftItem, 0);
    draw_panel(r, right_title, right_items, right_selected, PartRightItem, 1);

    auto has_movable = [&](int side) {
        for (int i : rendered_indices(side)) {
            if (!is_disabled(side, i)) return true;
        }
        return false;
    };
    auto can_move_selected = [&](int side) {
        if (multiple && any_checked(side)) return true;
        int selected = side == 1 ? right_selected : left_selected;
        return selected >= 0 && !is_disabled(side, selected);
    };
    auto draw_button = [&](const Rect& b, const std::wstring& label, bool enabled, bool hot) {
        Color bbg = enabled ? t->button_bg : (dark ? 0xFF252738 : 0xFFE9ECF2);
        if (enabled && hot) bbg = t->button_hover;
        Color bfg = enabled ? t->text_primary : t->text_muted;
        D2D1_RECT_F rr = { (float)b.x, (float)b.y, (float)(b.x + b.w), (float)(b.y + b.h) };
        ctx.rt->FillRoundedRectangle(ROUNDED(rr, 4.0f, 4.0f), ctx.get_brush(bbg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rr.left + 0.5f, rr.top + 0.5f,
            rr.right - 0.5f, rr.bottom - 0.5f), 4.0f, 4.0f), ctx.get_brush(border), 1.0f);
        draw_text(ctx, label, style, bfg, rr.left, rr.top, (float)b.w, (float)b.h,
                  DWRITE_TEXT_ALIGNMENT_CENTER, 0.9f);
    };

    draw_button(move_right_rect(), move_right_text, can_move_selected(0), m_hover_part == PartMoveRight);
    draw_button(move_all_right_rect(), L"全部右移", has_movable(0), m_hover_part == PartMoveAllRight);
    draw_button(move_left_rect(), move_left_text, can_move_selected(1), m_hover_part == PartMoveLeft);
    draw_button(move_all_left_rect(), L"全部左移", has_movable(1), m_hover_part == PartMoveAllLeft);

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
    auto toggle_visible = [this](int side) {
        const auto& data = side == 1 ? right_items : left_items;
        int selectable = 0;
        int checked = 0;
        for (int i : rendered_indices(side)) {
            if (i < 0 || i >= (int)data.size() || data[i].disabled) continue;
            ++selectable;
            if (data[i].checked) ++checked;
        }
        set_all_checked(side, selectable > 0 && checked < selectable);
    };
    if (part == m_press_part) {
        if (part == PartLeftItem && !is_disabled(0, index)) toggle_item_checked(0, index);
        else if (part == PartRightItem && !is_disabled(1, index)) toggle_item_checked(1, index);
        else if (part == PartMoveRight) move_selected_right();
        else if (part == PartMoveLeft) move_selected_left();
        else if (part == PartMoveAllRight) move_all_right();
        else if (part == PartMoveAllLeft) move_all_left();
        else if (part == PartLeftFilter) m_active_filter_side = 0;
        else if (part == PartRightFilter) m_active_filter_side = 1;
        else if (part == PartLeftSelectAll) toggle_visible(0);
        else if (part == PartRightSelectAll) toggle_visible(1);
    }
    pressed = false;
    m_press_part = PartNone;
    m_press_index = -1;
    m_hover_part = part;
    m_hover_index = index;
    invalidate();
}

void Transfer::on_key_down(int vk, int) {
    if (m_active_filter_side < 0) return;
    std::wstring& filter = m_active_filter_side == 1 ? right_filter : left_filter;
    if (vk == VK_BACK && !filter.empty()) {
        filter.pop_back();
        normalize_state();
        invalidate();
    } else if (vk == VK_ESCAPE) {
        filter.clear();
        normalize_state();
        invalidate();
    } else if (vk == VK_RETURN) {
        if (m_active_filter_side == 0) move_selected_right();
        else move_selected_left();
    }
}

void Transfer::on_char(wchar_t ch) {
    if (m_active_filter_side < 0) return;
    if (ch < 32 || ch == 127) return;
    std::wstring& filter = m_active_filter_side == 1 ? right_filter : left_filter;
    filter.push_back(ch);
    normalize_state();
    invalidate();
}

void Transfer::on_blur() {
    has_focus = false;
    m_active_filter_side = -1;
    invalidate();
}
