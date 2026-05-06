#include "element_steps.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFFu) | ((alpha & 0xFFu) << 24);
}

static int normalize_steps_status(int value, int fallback) {
    return (value >= 0 && value <= 3) ? value : fallback;
}

static Color steps_success_color(HWND hwnd) {
    return is_dark_theme_for_window(hwnd) ? 0xFF73D13D : 0xFF67C23A;
}

static Color steps_status_color(HWND hwnd, const Theme* t, int status, Color muted) {
    if (status == 3) return 0xFFE5484D;
    if (status == 2) return steps_success_color(hwnd);
    if (status == 1) return t->accent;
    return muted;
}

static std::wstring mapped_steps_icon(const std::wstring& icon) {
    if (icon == L"el-icon-edit") return L"\u270F\uFE0F";
    if (icon == L"el-icon-upload") return L"\u2B06\uFE0F";
    if (icon == L"el-icon-picture") return L"\U0001F5BC\uFE0F";
    if (icon == L"el-icon-check") return L"✓";
    if (icon == L"el-icon-close") return L"!";
    return icon;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_CENTER,
                      bool wrap = false) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(wrap ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Steps::set_items(const std::vector<std::wstring>& values) {
    items = values;
    descriptions.assign(items.size(), L"");
    icons.assign(items.size(), L"");
    statuses.assign(items.size(), 0);
    activate_index(active_index, 1);
}

void Steps::set_step_items(const std::vector<std::pair<std::wstring, std::wstring>>& values) {
    items.clear();
    descriptions.clear();
    for (const auto& value : values) {
        items.push_back(value.first);
        descriptions.push_back(value.second);
    }
    icons.assign(items.size(), L"");
    statuses.assign(items.size(), 0);
    activate_index(active_index, 1);
}

void Steps::set_icon_items(const std::vector<StepsVisualItem>& values) {
    items.clear();
    descriptions.clear();
    icons.clear();
    for (const auto& value : values) {
        items.push_back(value.title);
        descriptions.push_back(value.description);
        icons.push_back(value.icon);
    }
    statuses.assign(items.size(), 0);
    activate_index(active_index, 1);
}

void Steps::set_active_index(int value) {
    activate_index(value, 1);
}

void Steps::activate_index(int value, int action) {
    if (items.empty()) {
        active_index = -1;
    } else {
        if (value < 0) value = 0;
        if (value >= (int)items.size()) value = (int)items.size() - 1;
        active_index = value;
    }
    if ((int)statuses.size() < (int)items.size()) statuses.resize(items.size(), 0);
    for (int i = 0; i < (int)items.size(); ++i) {
        if (statuses[i] == 3) continue;
        statuses[i] = i < active_index ? finish_status : (i == active_index ? process_status : 0);
    }
    ++change_count;
    last_action = action;
    if (change_cb) change_cb(id, active_index, (int)items.size(), last_action);
    invalidate();
}

void Steps::set_direction(int value) {
    direction = value == 1 ? 1 : 0;
    last_action = 1;
    invalidate();
}

void Steps::set_options(int space_value, bool align_center_value, bool simple_value,
                        int finish_status_value, int process_status_value) {
    int old_finish = finish_status;
    int old_process = process_status;
    space = (std::max)(0, space_value);
    align_center = align_center_value;
    simple = simple_value;
    finish_status = normalize_steps_status(finish_status_value, 2);
    process_status = normalize_steps_status(process_status_value, 1);
    if ((int)statuses.size() < (int)items.size()) statuses.resize(items.size(), 0);
    for (int i = 0; i < (int)items.size(); ++i) {
        int old_auto = i < active_index ? old_finish : (i == active_index ? old_process : 0);
        if (statuses[i] == old_auto) {
            statuses[i] = i < active_index ? finish_status : (i == active_index ? process_status : 0);
        }
    }
    last_action = 1;
    invalidate();
}

void Steps::set_statuses(const std::vector<int>& values) {
    statuses.assign(items.size(), 0);
    for (int i = 0; i < (int)items.size() && i < (int)values.size(); ++i) {
        int s = values[i];
        statuses[i] = (s >= 0 && s <= 3) ? s : 0;
    }
    last_action = 1;
    invalidate();
}

int Steps::status_at(int index) const {
    if (index < 0 || index >= (int)items.size()) return 0;
    if (index < (int)statuses.size()) return statuses[index];
    if (index < active_index) return finish_status;
    if (index == active_index) return process_status;
    return 0;
}

int Steps::failed_count() const {
    int count = 0;
    for (int i = 0; i < (int)items.size(); ++i) {
        if (status_at(i) == 3) ++count;
    }
    return count;
}

std::wstring Steps::icon_at(int index) const {
    if (index < 0 || index >= (int)icons.size() || icons[index].empty()) return L"";
    return mapped_steps_icon(icons[index]);
}

int Steps::step_at(int x, int y) const {
    if (items.empty() || x < 0 || y < 0 || x >= bounds.w || y >= bounds.h) return -1;
    if (direction == 1) {
        float usable_h = (float)bounds.h - style.pad_top - style.pad_bottom;
        if (usable_h <= 0.0f) return -1;
        int idx = (int)(((float)y - style.pad_top) / (usable_h / (float)items.size()));
        return (idx >= 0 && idx < (int)items.size()) ? idx : -1;
    }
    float usable = (float)bounds.w - style.pad_left - style.pad_right;
    if (usable <= 0.0f) return -1;
    float segment = space > 0 ? (float)space : usable / (float)items.size();
    if (segment <= 0.0f) return -1;
    int idx = (int)(((float)x - style.pad_left) / segment);
    return (idx >= 0 && idx < (int)items.size()) ? idx : -1;
}

void Steps::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    Color success = steps_success_color(owner_hwnd);
    Color normal = style.fg_color ? style.fg_color : t->text_secondary;
    Color muted = t->text_muted;
    Color border = style.border_color ? style.border_color : t->border_default;
    float circle = (std::max)(22.0f, style.font_size * 1.65f);

    ctx.push_clip({ 0, 0, (float)bounds.w, (float)bounds.h });

    auto is_done_status = [&](int st) {
        return st == finish_status || st == 2;
    };
    auto step_color = [&](int st) {
        return steps_status_color(owner_hwnd, t, st, muted);
    };
    auto marker_for = [&](int i, int st) {
        std::wstring icon = icon_at(i);
        if (!icon.empty()) return icon;
        if (st == 3) return std::wstring(L"!");
        if (is_done_status(st)) return std::wstring(L"✓");
        return std::to_wstring(i + 1);
    };

    if (direction == 1) {
        float usable_h = (float)bounds.h - style.pad_top - style.pad_bottom;
        float segment_h = items.empty() ? usable_h : usable_h / (float)items.size();
        float cx = (float)style.pad_left + circle * 0.5f + 4.0f;
        for (int i = 0; i < (int)items.size(); ++i) {
            float step_y = (float)style.pad_top + segment_h * (float)i + segment_h * 0.5f;
            if (i < (int)items.size() - 1) {
                float ny = (float)style.pad_top + segment_h * (float)(i + 1) + segment_h * 0.5f;
                ctx.rt->DrawLine(D2D1::Point2F(cx, step_y + circle * 0.62f),
                                 D2D1::Point2F(cx, ny - circle * 0.62f),
                                 ctx.get_brush(is_done_status(status_at(i)) ? success : border), 2.0f);
            }
        }
        for (int i = 0; i < (int)items.size(); ++i) {
            float step_y = (float)style.pad_top + segment_h * (float)i + segment_h * 0.5f;
            int st = status_at(i);
            bool is_active = st == process_status || i == active_index;
            bool hot = i == m_hover_index;
            Color c = step_color(st);
            Color fill = is_active ? c : (hot ? t->button_hover : 0);
            D2D1_ELLIPSE e = D2D1::Ellipse(D2D1::Point2F(cx, step_y), circle * 0.5f, circle * 0.5f);
            if (fill) ctx.rt->FillEllipse(e, ctx.get_brush(fill));
            ctx.rt->DrawEllipse(e, ctx.get_brush(c), is_active ? 2.0f : 1.3f);
            std::wstring label = marker_for(i, st);
            draw_text(ctx, label, style, is_active ? 0xFFFFFFFF : c,
                      cx - circle * 0.5f, step_y - circle * 0.5f, circle, circle, 0.9f);
            float text_x = cx + circle * 0.8f;
            draw_text(ctx, items[i], style, is_active ? c : normal,
                      text_x, step_y - 22.0f, (float)bounds.w - text_x - style.pad_right,
                      22.0f, 0.94f, DWRITE_TEXT_ALIGNMENT_LEADING);
            if (i < (int)descriptions.size() && !descriptions[i].empty()) {
                draw_text(ctx, descriptions[i], style, muted,
                          text_x, step_y + 1.0f, (float)bounds.w - text_x - style.pad_right,
                          (std::max)(22.0f, segment_h * 0.42f), 0.82f, DWRITE_TEXT_ALIGNMENT_LEADING, true);
            }
        }
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }

    float left = (float)style.pad_left;
    float usable = (float)bounds.w - style.pad_left - style.pad_right;
    float segment = items.empty() ? usable : (space > 0 ? (float)space : usable / (float)items.size());
    if (space > 0 && align_center) {
        float total = segment * (float)items.size();
        if (total < usable) left += (usable - total) * 0.5f;
    }

    if (simple) {
        float top = 6.0f;
        float row_h = (std::max)(34.0f, (float)bounds.h - 12.0f);
        bool dark = is_dark_theme_for_window(owner_hwnd);
        Color simple_bg = dark ? with_alpha(t->button_bg, 0x80) : 0xFFF5F7FA;
        Color simple_border = dark ? with_alpha(border, 0xAA) : border;
        ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, top, (float)bounds.w - 0.5f, top + row_h),
                                            6.0f, 6.0f), ctx.get_brush(simple_bg));
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, top, (float)bounds.w - 0.5f, top + row_h),
                                            6.0f, 6.0f), ctx.get_brush(simple_border), 1.0f);
        for (int i = 0; i < (int)items.size(); ++i) {
            float item_x = left + segment * (float)i;
            float item_w = (std::min)(segment, (float)bounds.w - item_x - style.pad_right);
            if (item_w <= 18.0f) continue;
            int st = status_at(i);
            bool is_active = st == process_status || i == active_index;
            bool hot = i == m_hover_index;
            Color c = step_color(st);
            Color fill = is_active ? with_alpha(c, dark ? 0x36 : 0x18)
                         : (hot ? with_alpha(t->accent, dark ? 0x22 : 0x12) : 0);
            if (fill) {
                ctx.rt->FillRoundedRectangle(ROUNDED(D2D1::RectF(item_x + 2.0f, top + 4.0f,
                                                                 item_x + item_w - 6.0f, top + row_h - 4.0f),
                                                    5.0f, 5.0f), ctx.get_brush(fill));
            }
            std::wstring marker = marker_for(i, st);
            draw_text(ctx, marker, style, c, item_x + 12.0f, top + 5.0f, 28.0f, row_h - 10.0f,
                      0.95f, DWRITE_TEXT_ALIGNMENT_CENTER);
            float text_x = item_x + 44.0f;
            float text_w = item_w - 66.0f;
            if (i < (int)items.size() - 1) text_w -= 16.0f;
            draw_text(ctx, items[i], style, is_active ? t->text_primary : normal,
                      text_x, top + 5.0f, text_w, row_h - 10.0f, 0.95f,
                      DWRITE_TEXT_ALIGNMENT_LEADING);
            if (i < (int)items.size() - 1) {
                float ax = item_x + item_w - 18.0f;
                float cy = top + row_h * 0.5f;
                ctx.rt->DrawLine(D2D1::Point2F(ax - 4.0f, cy - 7.0f),
                                 D2D1::Point2F(ax + 3.0f, cy),
                                 ctx.get_brush(muted), 1.4f);
                ctx.rt->DrawLine(D2D1::Point2F(ax + 3.0f, cy),
                                 D2D1::Point2F(ax - 4.0f, cy + 7.0f),
                                 ctx.get_brush(muted), 1.4f);
            }
        }
        ctx.pop_clip();
        ctx.rt->SetTransform(saved);
        return;
    }

    float cy = circle * 0.5f + 4.0f;
    auto cx_for = [&](int i) {
        float slot_left = left + segment * (float)i;
        if (space > 0 && !align_center) return slot_left + circle * 0.5f + 4.0f;
        return slot_left + segment * 0.5f;
    };
    for (int i = 0; i < (int)items.size(); ++i) {
        float cx = cx_for(i);
        if (i < (int)items.size() - 1) {
            float nx = cx_for(i + 1);
            ctx.rt->DrawLine(D2D1::Point2F(cx + circle * 0.6f, cy),
                             D2D1::Point2F(nx - circle * 0.6f, cy),
                             ctx.get_brush(is_done_status(status_at(i)) ? success : border), 2.0f);
        }
    }

    for (int i = 0; i < (int)items.size(); ++i) {
        float cx = cx_for(i);
        float slot_left = left + segment * (float)i;
        float slot_w = (std::min)(segment, (float)bounds.w - slot_left - style.pad_right);
        int st = status_at(i);
        bool is_active = st == process_status || i == active_index;
        bool hot = i == m_hover_index;
        Color c = step_color(st);
        Color fill = is_active ? c : (hot ? t->button_hover : 0);
        D2D1_ELLIPSE e = D2D1::Ellipse(D2D1::Point2F(cx, cy), circle * 0.5f, circle * 0.5f);
        if (fill) ctx.rt->FillEllipse(e, ctx.get_brush(fill));
        ctx.rt->DrawEllipse(e, ctx.get_brush(c), is_active ? 2.0f : 1.3f);
        std::wstring label = marker_for(i, st);
        draw_text(ctx, label, style, is_active ? 0xFFFFFFFF : c,
                  cx - circle * 0.5f, cy - circle * 0.5f, circle, circle, 0.9f);
        draw_text(ctx, items[i], style, is_active ? c : normal,
                  slot_left + 2.0f, cy + circle * 0.55f,
                  slot_w - 4.0f, 24.0f, 0.92f);
        if (i < (int)descriptions.size() && !descriptions[i].empty()) {
            draw_text(ctx, descriptions[i], style, muted,
                      slot_left + 2.0f, cy + circle * 0.55f + 22.0f,
                      slot_w - 4.0f, (float)bounds.h - cy - circle * 0.55f - 22.0f,
                      0.78f, DWRITE_TEXT_ALIGNMENT_CENTER, true);
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Steps::on_mouse_move(int x, int y) {
    int idx = step_at(x, y);
    if (idx != m_hover_index) {
        m_hover_index = idx;
        invalidate();
    }
}

void Steps::on_mouse_leave() {
    m_hover_index = -1;
    m_press_index = -1;
    hovered = false;
    invalidate();
}

void Steps::on_mouse_down(int x, int y, MouseButton) {
    m_press_index = step_at(x, y);
    pressed = true;
    invalidate();
}

void Steps::on_mouse_up(int x, int y, MouseButton) {
    int idx = step_at(x, y);
    if (idx >= 0 && idx == m_press_index) {
        last_clicked_index = idx;
        ++click_count;
        activate_index(idx, 2);
    }
    m_press_index = -1;
    pressed = false;
    invalidate();
}

void Steps::on_key_down(int vk, int) {
    if (vk == VK_LEFT || vk == VK_UP) activate_index(active_index - 1, 3);
    else if (vk == VK_RIGHT || vk == VK_DOWN) activate_index(active_index + 1, 3);
    else if (vk == VK_HOME) activate_index(0, 3);
    else if (vk == VK_END) activate_index((int)items.size() - 1, 3);
}
