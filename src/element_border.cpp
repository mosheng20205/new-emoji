#include "element_border.h"
#include "emoji_fallback.h"
#include "factory.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

void Border::set_options(int side_mask, Color color, float width, float radius, const std::wstring& new_title) {
    sides = side_mask <= 0 ? 15 : (side_mask & 15);
    title = new_title;
    if (has_logical_style) {
        logical_style.border_color = color;
        logical_style.border_width = width > 0.0f ? width : 1.0f;
        logical_style.corner_radius = radius >= 0.0f ? radius : 0.0f;
    } else {
        style.border_color = color;
        style.border_width = width > 0.0f ? width : 1.0f;
        style.corner_radius = radius >= 0.0f ? radius : 0.0f;
    }
    invalidate();
}

void Border::get_options(int& side_mask, Color& color, float& width, float& radius) const {
    const ElementStyle& s = has_logical_style ? logical_style : style;
    side_mask = sides;
    color = s.border_color;
    width = s.border_width;
    radius = s.corner_radius;
}

void Border::set_dashed(bool value) {
    dashed = value;
    invalidate();
}

void Border::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    const Theme* t = theme_for_window(owner_hwnd);
    Color bg = style.bg_color;
    Color border = style.border_color ? style.border_color : t->border_default;
    float bw = style.border_width > 0 ? style.border_width : 1.0f;
    float radius = style.corner_radius > 0 ? style.corner_radius : 4.0f;

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    if (bg) ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));

    for (auto& ch : children) {
        if (ch->visible) ch->paint(ctx);
    }

    auto* border_brush = ctx.get_brush(border);
    ID2D1StrokeStyle* stroke_style = nullptr;
    if (dashed && g_d2d_factory) {
        D2D1_STROKE_STYLE_PROPERTIES props = D2D1::StrokeStyleProperties();
        props.dashStyle = D2D1_DASH_STYLE_DASH;
        g_d2d_factory->CreateStrokeStyle(props, nullptr, 0, &stroke_style);
    }
    D2D1_RECT_F br = { bw * 0.5f, bw * 0.5f,
                       (float)bounds.w - bw * 0.5f, (float)bounds.h - bw * 0.5f };
    if (sides == 15) {
        ctx.rt->DrawRoundedRectangle(ROUNDED(br, radius, radius), border_brush, bw, stroke_style);
    } else {
        if (sides & 1) ctx.rt->DrawLine(D2D1::Point2F(0, bw * 0.5f), D2D1::Point2F((float)bounds.w, bw * 0.5f), border_brush, bw, stroke_style);
        if (sides & 2) ctx.rt->DrawLine(D2D1::Point2F((float)bounds.w - bw * 0.5f, 0), D2D1::Point2F((float)bounds.w - bw * 0.5f, (float)bounds.h), border_brush, bw, stroke_style);
        if (sides & 4) ctx.rt->DrawLine(D2D1::Point2F(0, (float)bounds.h - bw * 0.5f), D2D1::Point2F((float)bounds.w, (float)bounds.h - bw * 0.5f), border_brush, bw, stroke_style);
        if (sides & 8) ctx.rt->DrawLine(D2D1::Point2F(bw * 0.5f, 0), D2D1::Point2F(bw * 0.5f, (float)bounds.h), border_brush, bw, stroke_style);
    }
    if (stroke_style) stroke_style->Release();

    if (!title.empty()) {
        float text_w = (std::min)((float)bounds.w - 24.0f, (float)title.size() * style.font_size * 0.75f + 24.0f);
        float text_h = (std::max)(22.0f, style.font_size * 1.55f);
        float text_x = (float)style.pad_left;
        D2D1_RECT_F cover = { text_x - 4.0f, 0.0f, text_x + text_w + 4.0f, text_h };
        Color cover_color = bg ? bg : t->panel_bg;
        ctx.rt->FillRectangle(cover, ctx.get_brush(cover_color));
        auto* layout = ctx.create_text_layout(title, style.font_name, style.font_size, text_w, text_h);
        if (layout) {
            apply_emoji_font_fallback(layout, title);
            layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            ctx.rt->DrawTextLayout(D2D1::Point2F(text_x, 0.0f), layout,
                ctx.get_brush(style.fg_color ? style.fg_color : t->text_secondary),
                D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
