#include "element_card.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static int scale_int(int value, float scale) {
    return (int)std::lround((float)value * scale);
}

static CardBodyStyle scale_body_style(const CardBodyStyle& value, float scale) {
    CardBodyStyle out = value;
    out.pad_left = scale_int(value.pad_left, scale);
    out.pad_top = scale_int(value.pad_top, scale);
    out.pad_right = scale_int(value.pad_right, scale);
    out.pad_bottom = scale_int(value.pad_bottom, scale);
    out.font_size = value.font_size * scale;
    out.item_gap = scale_int(value.item_gap, scale);
    out.item_padding_y = scale_int(value.item_padding_y, scale);
    return out;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_WRAP,
                      DWRITE_PARAGRAPH_ALIGNMENT paragraph = DWRITE_PARAGRAPH_ALIGNMENT_NEAR) {
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

void Card::apply_dpi_scale(float scale) {
    Element::apply_dpi_scale(scale);
    body_style = scale_body_style(logical_body_style, scale);
}

void Card::set_title(const std::wstring& value) {
    title = value;
    invalidate();
}

void Card::set_body(const std::wstring& value) {
    body = value;
    text = value;
    invalidate();
}

void Card::set_footer(const std::wstring& value) {
    footer = value;
    invalidate();
}

void Card::set_items(const std::vector<std::wstring>& values) {
    items = values;
    invalidate();
}

void Card::set_body_style(const CardBodyStyle& value) {
    logical_body_style = value;
    invalidate();
}

void Card::set_actions(const std::vector<std::wstring>& values) {
    actions = values;
    action_index = -1;
    hover_action = -1;
    press_action = -1;
    invalidate();
}

void Card::reset_action() {
    action_index = -1;
    invalidate();
}

void Card::set_shadow(int value) {
    if (value < 0) value = 0;
    if (value > 2) value = 2;
    shadow = value;
    invalidate();
}

void Card::set_options(int shadow_value, bool hoverable_value) {
    hoverable = hoverable_value;
    set_shadow(shadow_value);
}

float Card::footer_height() const {
    if (footer.empty() && actions.empty()) return 0.0f;
    return (std::max)(style.font_size * 2.7f, 38.0f);
}

int Card::action_at(int x, int y) const {
    float fh = footer_height();
    if (fh <= 0.0f || actions.empty()) return -1;
    float footer_top = (float)bounds.h - fh;
    if ((float)y < footer_top || y >= bounds.h) return -1;

    float right = (float)bounds.w - (float)style.pad_right;
    float gap = 8.0f;
    for (int i = (int)actions.size() - 1; i >= 0; --i) {
        float aw = (std::max)(style.font_size * (float)actions[i].size() * 0.58f + 24.0f, 54.0f);
        D2D1_RECT_F r = { right - aw, footer_top + 7.0f, right, (float)bounds.h - 7.0f };
        if ((float)x >= r.left && (float)x <= r.right && (float)y >= r.top && (float)y <= r.bottom) {
            return i;
        }
        right -= aw + gap;
    }
    return -1;
}

Element* Card::hit_test(int x, int y) {
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    bool inside = visible && lx >= 0 && lx < bounds.w && ly >= 0 && ly < bounds.h;
    if (hoverable && hovered != inside) {
        hovered = inside;
        if (shadow == 2) invalidate();
    }
    return Element::hit_test(x, y);
}

void Card::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = t->text_secondary;
    Color footer_fg = t->text_muted;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f;

    D2D1_RECT_F clip = { -8.0f, -8.0f, (float)bounds.w + 8.0f, (float)bounds.h + 8.0f };
    ctx.push_clip(clip);

    bool show_shadow = shadow == 1 || (shadow == 2 && hovered);
    if (show_shadow) {
        Color shadow_color = dark ? 0x66000000 : 0x22000000;
        for (int i = 3; i >= 1; --i) {
            float off = (float)i;
            D2D1_RECT_F sr = { off, off + 1.0f, (float)bounds.w + off, (float)bounds.h + off + 1.0f };
            ctx.rt->FillRoundedRectangle(ROUNDED(sr, radius, radius),
                ctx.get_brush(with_alpha(shadow_color, (unsigned)(0x16 / i + 0x08))));
        }
    }

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));

    float pad_x = (float)style.pad_left;
    float content_w = (float)bounds.w - style.pad_left - style.pad_right;
    if (content_w < 1.0f) content_w = 1.0f;
    float header_h = title.empty() ? 0.0f : (std::max)(style.font_size * 2.9f, 40.0f);
    if (!title.empty()) {
        draw_text(ctx, title, style, title_fg,
                  pad_x, 0.0f, content_w, header_h,
                  1.04f, DWRITE_FONT_WEIGHT_SEMI_BOLD, DWRITE_WORD_WRAPPING_NO_WRAP,
                  DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
        ctx.rt->DrawLine(D2D1::Point2F(0.0f, header_h),
                         D2D1::Point2F((float)bounds.w, header_h),
                         ctx.get_brush(border), 1.0f);
    }

    float footer_h = footer_height();
    float body_x = (float)body_style.pad_left;
    float body_top = title.empty() ? (float)body_style.pad_top : header_h + (float)body_style.pad_top;
    float body_w = (float)bounds.w - body_style.pad_left - body_style.pad_right;
    float body_h = (float)bounds.h - body_top - body_style.pad_bottom - footer_h;
    if (body_w < 1.0f) body_w = 1.0f;
    if (body_h < 1.0f) body_h = 1.0f;

    ElementStyle body_text_style = style;
    body_text_style.font_size = body_style.font_size > 0.0f ? body_style.font_size : style.font_size;
    if (!items.empty()) {
        float row_text_h = (std::max)(body_text_style.font_size * 1.45f, body_text_style.font_size + 6.0f);
        float row_h = row_text_h + (float)body_style.item_padding_y * 2.0f;
        float y = body_top;
        for (size_t i = 0; i < items.size() && y < body_top + body_h; ++i) {
            float available_h = (std::min)(row_h, body_top + body_h - y);
            draw_text(ctx, items[i], body_text_style, body_fg,
                      body_x, y + (float)body_style.item_padding_y,
                      body_w, (std::max)(1.0f, available_h - (float)body_style.item_padding_y * 2.0f),
                      1.0f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_WORD_WRAPPING_NO_WRAP,
                      DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            y += row_h;
            if (body_style.divider && i + 1 < items.size() && y < body_top + body_h) {
                ctx.rt->DrawLine(D2D1::Point2F(body_x, y),
                                 D2D1::Point2F(body_x + body_w, y),
                                 ctx.get_brush(with_alpha(border, 0xAA)), 1.0f);
            }
            y += (float)body_style.item_gap;
        }
    } else {
        draw_text(ctx, body.empty() ? text : body, body_text_style, body_fg,
                  body_x, body_top, body_w, body_h, 1.0f);
    }

    if (footer_h > 0.0f) {
        float footer_top = (float)bounds.h - footer_h;
        ctx.rt->DrawLine(D2D1::Point2F(0.0f, footer_top),
                         D2D1::Point2F((float)bounds.w, footer_top),
                         ctx.get_brush(border), 1.0f);
        float actions_w = 0.0f;
        for (const auto& action : actions) {
            actions_w += (std::max)(style.font_size * (float)action.size() * 0.58f + 24.0f, 54.0f) + 8.0f;
        }
        if (actions_w > 0.0f) actions_w -= 8.0f;
        float footer_text_w = (std::max)(1.0f, content_w - actions_w - 12.0f);
        draw_text(ctx, footer, style, footer_fg,
                  pad_x, footer_top, footer_text_w, footer_h,
                  0.92f, DWRITE_FONT_WEIGHT_NORMAL, DWRITE_WORD_WRAPPING_NO_WRAP,
                  DWRITE_PARAGRAPH_ALIGNMENT_CENTER);

        float right = (float)bounds.w - (float)style.pad_right;
        float gap = 8.0f;
        for (int i = (int)actions.size() - 1; i >= 0; --i) {
            float aw = (std::max)(style.font_size * (float)actions[i].size() * 0.58f + 24.0f, 54.0f);
            D2D1_RECT_F ar = { right - aw, footer_top + 7.0f, right, (float)bounds.h - 7.0f };
            Color action_bg = i == press_action ? t->accent :
                              (i == hover_action ? (dark ? 0xFF3A4E73 : 0xFFE8F2FF) : (dark ? 0xFF2B2E42 : 0xFFF5F7FA));
            Color action_fg = (i == press_action || i == hover_action) ? 0xFFFFFFFF : t->accent;
            ctx.rt->FillRoundedRectangle(ROUNDED(ar, 4.0f, 4.0f), ctx.get_brush(action_bg));
            ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(ar.left + 0.5f, ar.top + 0.5f,
                ar.right - 0.5f, ar.bottom - 0.5f), 4.0f, 4.0f), ctx.get_brush(t->accent), 1.0f);
            draw_text(ctx, actions[i], style, action_fg,
                      ar.left + 10.0f, ar.top, aw - 20.0f, ar.bottom - ar.top,
                      0.9f, DWRITE_FONT_WEIGHT_SEMI_BOLD, DWRITE_WORD_WRAPPING_NO_WRAP,
                      DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            right -= aw + gap;
        }
    }

    D2D1_RECT_F content_clip = { 0.0f, 0.0f, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(content_clip);
    for (auto& ch : children) {
        if (ch->visible) ch->paint(ctx);
    }
    ctx.pop_clip();

    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), style.border_width > 0.0f ? style.border_width : 1.0f);

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Card::on_mouse_move(int x, int y) {
    int idx = action_at(x, y);
    if (idx != hover_action) {
        hover_action = idx;
        invalidate();
    }
}

void Card::on_mouse_down(int x, int y, MouseButton) {
    pressed = true;
    press_action = action_at(x, y);
    invalidate();
}

void Card::on_mouse_up(int x, int y, MouseButton) {
    int idx = action_at(x, y);
    if (idx >= 0 && idx == press_action) {
        action_index = idx;
        if (click_cb) click_cb(id);
    }
    pressed = false;
    press_action = -1;
    hover_action = idx;
    invalidate();
}

void Card::on_mouse_enter() {
    if (!hoverable) return;
    hovered = true;
    if (shadow == 2) invalidate();
}

void Card::on_mouse_leave() {
    if (!hoverable) return;
    hovered = false;
    pressed = false;
    hover_action = -1;
    press_action = -1;
    if (shadow == 2) invalidate();
}
