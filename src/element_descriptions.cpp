#include "element_descriptions.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

static Color mix_desc_color(Color a, Color b, float t) {
    if (t <= 0.0f) return a;
    if (t >= 1.0f) return b;
    auto mix = [t](unsigned ca, unsigned cb) -> unsigned {
        return (unsigned)std::lround((float)ca + ((float)cb - (float)ca) * t);
    };
    unsigned aa = (a >> 24) & 0xFF, ar = (a >> 16) & 0xFF, ag = (a >> 8) & 0xFF, ab = a & 0xFF;
    unsigned ba = (b >> 24) & 0xFF, br = (b >> 16) & 0xFF, bg = (b >> 8) & 0xFF, bb = b & 0xFF;
    return (mix(aa, ba) << 24) | (mix(ar, br) << 16) | (mix(ag, bg) << 8) | mix(ab, bb);
}

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_desc_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                           float font_size, Color color, float x, float y, float w, float h,
                           DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                           DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_NO_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

static Color tag_bg_for(int type, bool dark) {
    switch (type) {
    case 1: return dark ? 0xFF1F3A2A : 0xFFEAF8EF;
    case 2: return dark ? 0xFF243247 : 0xFFEAF2FF;
    case 3: return dark ? 0xFF443725 : 0xFFFFF7E7;
    case 4: return dark ? 0xFF46282B : 0xFFFFEEEE;
    default: return dark ? 0xFF30364C : 0xFFF3F4F6;
    }
}

static Color tag_fg_for(int type, bool dark) {
    switch (type) {
    case 1: return dark ? 0xFFE6F7EC : 0xFF16723A;
    case 2: return dark ? 0xFFEAF2FF : 0xFF2F6FD6;
    case 3: return dark ? 0xFFFFE4B5 : 0xFF9A5B00;
    case 4: return dark ? 0xFFFFD9DD : 0xFFB4232A;
    default: return dark ? 0xFFEAF0FF : 0xFF34435A;
    }
}

static Color variant_color(int variant, const Theme* t) {
    switch (variant) {
    case 1: return t->accent;
    case 2: return 0xFF16A34A;
    case 3: return 0xFFF59E0B;
    case 4: return 0xFFDC2626;
    case 6: return 0xFF0EA5E9;
    default: return t->button_bg;
    }
}

void Descriptions::set_items(const std::vector<std::pair<std::wstring, std::wstring>>& values) {
    items = values;
    rich_items.clear();
    for (const auto& value : values) {
        DescriptionItem item;
        item.label = value.first;
        item.content = value.second;
        rich_items.push_back(item);
    }
    invalidate();
}

void Descriptions::set_rich_items(const std::vector<DescriptionItem>& values) {
    rich_items = values;
    items.clear();
    for (const auto& value : values) {
        items.push_back({ value.label, value.content });
    }
    invalidate();
}

void Descriptions::set_columns(int value) {
    if (value < 1) value = 1;
    if (value > 4) value = 4;
    columns = value;
    invalidate();
}

void Descriptions::set_bordered(bool value) {
    bordered = value;
    invalidate();
}

void Descriptions::set_options(int column_count, bool has_border, int label_width_value,
                               int min_row_height_value, bool wrap) {
    set_columns(column_count);
    bordered = has_border;
    if (label_width_value < 48) label_width_value = 48;
    if (label_width_value > 220) label_width_value = 220;
    label_width = label_width_value;
    if (min_row_height_value < 24) min_row_height_value = 24;
    if (min_row_height_value > 120) min_row_height_value = 120;
    min_row_height = min_row_height_value;
    wrap_values = wrap;
    invalidate();
}

void Descriptions::set_advanced_options(bool responsive_value, bool last_item_span_value) {
    responsive = responsive_value;
    last_item_span = last_item_span_value;
    invalidate();
}

void Descriptions::set_layout(int direction_value, int size_value, int column_count, bool has_border) {
    direction = direction_value == 1 ? 1 : 0;
    if (size_value < 0) size_value = 0;
    if (size_value > 3) size_value = 3;
    size = size_value;
    set_columns(column_count);
    bordered = has_border;
    invalidate();
}

void Descriptions::set_colors(Color border, Color label_bg, Color content_bg,
                              Color label_fg, Color content_fg, Color title_fg) {
    custom_border = border;
    custom_label_bg = label_bg;
    custom_content_bg = content_bg;
    custom_label_fg = label_fg;
    custom_content_fg = content_fg;
    custom_title_fg = title_fg;
    invalidate();
}

void Descriptions::set_extra(const std::wstring& emoji, const std::wstring& value,
                             bool visible_value, int variant_value) {
    extra_emoji = emoji;
    extra_text = value;
    extra_visible = visible_value;
    if (variant_value < 0) variant_value = 0;
    if (variant_value > 6) variant_value = 6;
    extra_variant = variant_value;
    extra_hovered = false;
    extra_pressed = false;
    invalidate();
}

int Descriptions::effective_columns() const {
    int cols = (std::max)(1, columns);
    if (!responsive) return cols;
    int content_w = bounds.w - style.pad_left - style.pad_right;
    if (content_w < 360) return 1;
    if (content_w < 620) return (std::min)(cols, 2);
    return cols;
}

float Descriptions::scaled_font_size() const {
    float fs = style.font_size;
    if (size == 1) fs *= 0.96f;
    else if (size == 2) fs *= 0.90f;
    else if (size == 3) fs *= 0.84f;
    return (std::max)(9.0f, fs);
}

int Descriptions::scaled_min_row_height() const {
    float factor = 1.0f;
    if (size == 1) factor = 0.92f;
    else if (size == 2) factor = 0.80f;
    else if (size == 3) factor = 0.70f;
    return (std::max)(20, (int)std::lround((float)min_row_height * factor));
}

bool Descriptions::point_in_extra(int x, int y) const {
    if (!extra_visible) return false;
    D2D1_RECT_F rect = extra_rect;
    if (rect.right <= rect.left || rect.bottom <= rect.top) {
        float font_size = scaled_font_size();
        float title_h = text.empty() ? font_size * 2.0f : font_size * 2.0f;
        std::wstring extra = extra_emoji + extra_text;
        float ew = (std::max)(64.0f, (float)extra.length() * font_size * 0.72f + 24.0f);
        float eh = (std::max)(24.0f, font_size * 1.8f);
        rect = {
            (float)bounds.w - (float)style.pad_right - ew,
            (std::max)(2.0f, (title_h - eh) * 0.5f),
            (float)bounds.w - (float)style.pad_right,
            (std::max)(2.0f, (title_h - eh) * 0.5f) + eh
        };
    }
    bool in_button = (float)x >= rect.left && (float)x < rect.right &&
                     (float)y >= rect.top && (float)y < rect.bottom;
    float title_h = (std::max)(32.0f, scaled_font_size() * 2.4f);
    bool in_title_action_zone = x >= bounds.w - 150 && x < bounds.w && y >= 0 && (float)y < title_h;
    return in_button || in_title_action_zone;
}

bool Descriptions::accepts_input() const {
    if (!enabled) return false;
    return !extra_visible || extra_pressed;
}

void Descriptions::on_mouse_move(int x, int y) {
    bool next = point_in_extra(x, y);
    if (next != extra_hovered) {
        extra_hovered = next;
        invalidate();
    }
}

void Descriptions::on_mouse_leave() {
    Element::on_mouse_leave();
    extra_hovered = false;
    extra_pressed = false;
    invalidate();
}

void Descriptions::on_mouse_down(int x, int y, MouseButton btn) {
    if (btn == MouseButton::Left && point_in_extra(x, y)) {
        extra_pressed = true;
    } else if (!extra_visible) {
        Element::on_mouse_down(x, y, btn);
    }
    invalidate();
}

void Descriptions::on_mouse_up(int x, int y, MouseButton btn) {
    if (btn == MouseButton::Left && extra_pressed && point_in_extra(x, y)) {
        ++extra_click_count;
    }
    extra_pressed = false;
    pressed = false;
    invalidate();
}

void Descriptions::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float font_size = scaled_font_size();
    Color fg = custom_content_fg ? custom_content_fg : (style.fg_color ? style.fg_color : t->text_primary);
    Color title_fg = custom_title_fg ? custom_title_fg : fg;
    Color label_fg = custom_label_fg ? custom_label_fg : t->text_secondary;
    Color border = custom_border ? custom_border : (style.border_color ? style.border_color : t->border_default);
    Color label_bg = custom_label_bg ? custom_label_bg : (style.bg_color ? style.bg_color : (dark ? 0xFF282A3A : 0xFFF5F7FA));
    Color content_bg = custom_content_bg;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    float title_h = text.empty() ? 0.0f : font_size * 2.0f;
    extra_rect = { 0, 0, 0, 0 };
    float title_right_pad = 0.0f;
    if (extra_visible) {
        std::wstring extra = extra_emoji + extra_text;
        float ew = (std::max)(64.0f, (float)extra.length() * font_size * 0.72f + 24.0f);
        float eh = (std::max)(24.0f, font_size * 1.8f);
        extra_rect = {
            (float)bounds.w - (float)style.pad_right - ew,
            (std::max)(2.0f, (title_h - eh) * 0.5f),
            (float)bounds.w - (float)style.pad_right,
            (std::max)(2.0f, (title_h - eh) * 0.5f) + eh
        };
        title_right_pad = ew + 10.0f;
        Color btn = variant_color(extra_variant, t);
        if (extra_hovered) btn = mix_desc_color(btn, dark ? 0xFFFFFFFF : 0xFF000000, dark ? 0.10f : 0.06f);
        if (extra_pressed) btn = mix_desc_color(btn, dark ? 0xFFFFFFFF : 0xFF000000, dark ? 0.16f : 0.10f);
        ctx.rt->FillRoundedRectangle(
            D2D1_ROUNDED_RECT{ extra_rect, 5.0f, 5.0f },
            ctx.get_brush(btn));
        draw_desc_text(ctx, extra, style, font_size * 0.92f, 0xFFFFFFFF,
                       extra_rect.left + 8.0f, extra_rect.top,
                       extra_rect.right - extra_rect.left - 16.0f,
                       extra_rect.bottom - extra_rect.top,
                       DWRITE_TEXT_ALIGNMENT_CENTER);
    }
    if (!text.empty()) {
        draw_desc_text(ctx, text, style, font_size, title_fg, (float)style.pad_left, 0.0f,
                       (float)bounds.w - style.pad_left - style.pad_right - title_right_pad, title_h);
    }

    const auto& values = rich_items;
    int count = (int)values.size();
    int cols = effective_columns();
    struct Placement { int row; int col; int span; };
    std::vector<Placement> placements;
    placements.reserve((size_t)count);
    int row = 0;
    int col = 0;
    for (int i = 0; i < count; ++i) {
        int span = values[i].span < 1 ? 1 : values[i].span;
        if (span > cols) span = cols;
        if (last_item_span && i == count - 1 && values[i].span <= 1 && col != 0) span = cols - col;
        if (col + span > cols) {
            ++row;
            col = 0;
        }
        placements.push_back({ row, col, span });
        col += span;
        if (col >= cols) {
            ++row;
            col = 0;
        }
    }
    int rows = placements.empty() ? 1 : placements.back().row + 1;

    float top = title_h + 2.0f;
    float grid_h = (float)bounds.h - top - (float)style.pad_bottom;
    if (grid_h < 1.0f) grid_h = 1.0f;
    float row_h = grid_h / (float)rows;
    float min_h = (std::max)((float)scaled_min_row_height(), font_size * (direction == 1 ? 3.2f : 1.8f));
    if (row_h < min_h) row_h = min_h;
    float cell_w = ((float)bounds.w - style.pad_left - style.pad_right) / (float)cols;
    float left = (float)style.pad_left;

    for (int i = 0; i < count; ++i) {
        const auto& item = values[i];
        const auto& p = placements[(size_t)i];
        float x = left + cell_w * (float)p.col;
        float y = top + row_h * (float)p.row;
        if (y >= bounds.h) break;
        float h = (std::min)(row_h, (float)bounds.h - y);
        float current_cell_w = cell_w * (float)p.span;
        D2D1_RECT_F cell = { x, y, x + current_cell_w, y + h };
        if (item.content_bg || content_bg) {
            ctx.rt->FillRectangle(cell, ctx.get_brush(item.content_bg ? item.content_bg : content_bg));
        }
        if (bordered) ctx.rt->DrawRectangle(cell, ctx.get_brush(border), 1.0f);

        std::wstring label = item.label_icon.empty() ? item.label : item.label_icon + L" " + item.label;
        Color item_label_fg = item.label_fg ? item.label_fg : label_fg;
        Color item_content_fg = item.content_fg ? item.content_fg : fg;

        if (direction == 1) {
            float label_h = (std::max)(font_size * 1.8f, h * 0.42f);
            D2D1_RECT_F label_rect = { x, y, x + current_cell_w, y + label_h };
            D2D1_RECT_F content_rect = { x, y + label_h, x + current_cell_w, y + h };
            if (bordered || item.label_bg || custom_label_bg) {
                ctx.rt->FillRectangle(label_rect, ctx.get_brush(item.label_bg ? item.label_bg : label_bg));
            }
            if (bordered) {
                ctx.rt->DrawLine(D2D1::Point2F(x, y + label_h),
                                 D2D1::Point2F(x + current_cell_w, y + label_h),
                                 ctx.get_brush(border), 1.0f);
            }
            draw_desc_text(ctx, label, style, font_size, item_label_fg,
                           x + 8.0f, y, current_cell_w - 16.0f, label_h);
            if (item.content_type == 1) {
                float tag_w = (std::max)(46.0f, (float)item.content.length() * font_size * 0.72f + 18.0f);
                float tag_h = (std::max)(20.0f, font_size * 1.55f);
                float tx = content_rect.left + 8.0f;
                if (item.content_align == 1) tx = content_rect.left + ((content_rect.right - content_rect.left) - tag_w) * 0.5f;
                else if (item.content_align == 2) tx = content_rect.right - tag_w - 8.0f;
                float ty = content_rect.top + ((content_rect.bottom - content_rect.top) - tag_h) * 0.5f;
                D2D1_RECT_F tag = { tx, ty, tx + tag_w, ty + tag_h };
                ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ tag, 4.0f, 4.0f }, ctx.get_brush(tag_bg_for(item.tag_type, dark)));
                ctx.rt->DrawRoundedRectangle(D2D1_ROUNDED_RECT{ tag, 4.0f, 4.0f }, ctx.get_brush(with_alpha(tag_fg_for(item.tag_type, dark), 0x66)), 1.0f);
                draw_desc_text(ctx, item.content, style, font_size * 0.88f, tag_fg_for(item.tag_type, dark),
                               tag.left + 8.0f, tag.top, tag_w - 16.0f, tag_h, DWRITE_TEXT_ALIGNMENT_CENTER);
            } else {
                DWRITE_TEXT_ALIGNMENT align = item.content_align == 1 ? DWRITE_TEXT_ALIGNMENT_CENTER :
                    (item.content_align == 2 ? DWRITE_TEXT_ALIGNMENT_TRAILING : DWRITE_TEXT_ALIGNMENT_LEADING);
                draw_desc_text(ctx, item.content, style, font_size, item_content_fg,
                               content_rect.left + 8.0f, content_rect.top,
                               content_rect.right - content_rect.left - 16.0f,
                               content_rect.bottom - content_rect.top, align,
                               wrap_values ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);
            }
        } else {
            float label_w = (std::min)(current_cell_w * 0.48f, (float)label_width * font_size / 14.0f);
            D2D1_RECT_F label_rect = { x, y, x + label_w, y + h };
            D2D1_RECT_F content_rect = { x + label_w, y, x + current_cell_w, y + h };
            if (bordered || item.label_bg || custom_label_bg) {
                ctx.rt->FillRectangle(label_rect, ctx.get_brush(item.label_bg ? item.label_bg : label_bg));
            }
            if (bordered) {
                ctx.rt->DrawLine(D2D1::Point2F(x + label_w, y),
                                 D2D1::Point2F(x + label_w, y + h),
                                 ctx.get_brush(border), 1.0f);
            }
            draw_desc_text(ctx, label, style, font_size, item_label_fg,
                           x + 8.0f, y, label_w - 12.0f, h);
            if (item.content_type == 1) {
                float available_w = content_rect.right - content_rect.left - 16.0f;
                float tag_w = (std::min)((std::max)(46.0f, (float)item.content.length() * font_size * 0.72f + 18.0f), available_w);
                float tag_h = (std::max)(20.0f, font_size * 1.55f);
                float tx = content_rect.left + 8.0f;
                if (item.content_align == 1) tx = content_rect.left + ((content_rect.right - content_rect.left) - tag_w) * 0.5f;
                else if (item.content_align == 2) tx = content_rect.right - tag_w - 8.0f;
                float ty = content_rect.top + ((content_rect.bottom - content_rect.top) - tag_h) * 0.5f;
                D2D1_RECT_F tag = { tx, ty, tx + tag_w, ty + tag_h };
                ctx.rt->FillRoundedRectangle(D2D1_ROUNDED_RECT{ tag, 4.0f, 4.0f }, ctx.get_brush(tag_bg_for(item.tag_type, dark)));
                ctx.rt->DrawRoundedRectangle(D2D1_ROUNDED_RECT{ tag, 4.0f, 4.0f }, ctx.get_brush(with_alpha(tag_fg_for(item.tag_type, dark), 0x66)), 1.0f);
                draw_desc_text(ctx, item.content, style, font_size * 0.88f, tag_fg_for(item.tag_type, dark),
                               tag.left + 8.0f, tag.top, tag_w - 16.0f, tag_h, DWRITE_TEXT_ALIGNMENT_CENTER);
            } else {
                DWRITE_TEXT_ALIGNMENT align = item.content_align == 1 ? DWRITE_TEXT_ALIGNMENT_CENTER :
                    (item.content_align == 2 ? DWRITE_TEXT_ALIGNMENT_TRAILING : DWRITE_TEXT_ALIGNMENT_LEADING);
                draw_desc_text(ctx, item.content, style, font_size, item_content_fg,
                               content_rect.left + 8.0f, content_rect.top,
                               content_rect.right - content_rect.left - 16.0f,
                               content_rect.bottom - content_rect.top, align,
                               wrap_values ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);
            }
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
