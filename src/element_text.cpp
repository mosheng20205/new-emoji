#include "element_text.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>

void Text::set_options(int align, int valign, int wrap_text, int ellipsis_text) {
    horizontal_align = (std::max)(0, (std::min)(2, align));
    vertical_align = (std::max)(0, (std::min)(2, valign));
    wrap = wrap_text != 0;
    ellipsis = ellipsis_text != 0;
    invalidate();
}

void Text::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    D2D1_MATRIX_3X2_F local = saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y);
    if (rotation_degrees() != 0.0f) {
        local = local * D2D1::Matrix3x2F::Rotation(
            rotation_degrees(), D2D1::Point2F((float)bounds.w * 0.5f, (float)bounds.h * 0.5f));
    }
    ctx.rt->SetTransform(local);

    const Theme* t = theme_for_window(owner_hwnd);
    if (style.bg_color) {
        D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
        ctx.rt->FillRectangle(rect, ctx.get_brush(style.bg_color));
    }

    if (!text.empty()) {
        float x = (float)style.pad_left;
        float y = (float)style.pad_top;
        float w = (float)(bounds.w - style.pad_left - style.pad_right);
        float h = (float)(bounds.h - style.pad_top - style.pad_bottom);
        if (w < 1.0f) w = 1.0f;
        if (h < 1.0f) h = 1.0f;

        auto* layout = ctx.create_text_layout(text, style.font_name,
                                              style.font_size * font_scale(), w, h);
        if (layout) {
            apply_emoji_font_fallback(layout, text);
            DWRITE_TEXT_RANGE range = { 0, (UINT32)text.size() };
            layout->SetUnderline(underline(), range);
            layout->SetWordWrapping(wrap ? DWRITE_WORD_WRAPPING_WRAP : DWRITE_WORD_WRAPPING_NO_WRAP);
            if (ellipsis) {
                DWRITE_TRIMMING trimming = {};
                trimming.granularity = DWRITE_TRIMMING_GRANULARITY_CHARACTER;
                IDWriteInlineObject* sign = nullptr;
                if (ctx.dwrite && SUCCEEDED(ctx.dwrite->CreateEllipsisTrimmingSign(layout, &sign))) {
                    layout->SetTrimming(&trimming, sign);
                    sign->Release();
                } else {
                    layout->SetTrimming(&trimming, nullptr);
                }
            }
            DWRITE_TEXT_ALIGNMENT text_align = DWRITE_TEXT_ALIGNMENT_LEADING;
            if (horizontal_align == 1) text_align = DWRITE_TEXT_ALIGNMENT_CENTER;
            if (horizontal_align == 2) text_align = DWRITE_TEXT_ALIGNMENT_TRAILING;
            DWRITE_PARAGRAPH_ALIGNMENT para_align = DWRITE_PARAGRAPH_ALIGNMENT_NEAR;
            if (vertical_align == 1) para_align = DWRITE_PARAGRAPH_ALIGNMENT_CENTER;
            if (vertical_align == 2) para_align = DWRITE_PARAGRAPH_ALIGNMENT_FAR;
            layout->SetTextAlignment(text_align);
            layout->SetParagraphAlignment(para_align);
            ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
                ctx.get_brush(text_color(t)), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    ctx.rt->SetTransform(saved);
}

Color Text::text_color(const Theme* theme) const {
    return style.fg_color ? style.fg_color : theme->text_primary;
}
