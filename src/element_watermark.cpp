#include "element_watermark.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Watermark::set_content(const std::wstring& value) {
    content = value;
    text = value;
    invalidate();
}

void Watermark::set_gap(int x, int y) {
    gap_x = (std::max)(60, x);
    gap_y = (std::max)(40, y);
    invalidate();
}

void Watermark::set_options(int x, int y, int rotation_degrees, int alpha_value) {
    set_gap(x, y);
    rotation = (float)(std::max)(-90, (std::min)(90, rotation_degrees));
    alpha = (unsigned)(std::max)(0, (std::min)(255, alpha_value));
    invalidate();
}

void Watermark::set_layer_options(int target_container_id, int overlay_enabled, int pointer_passthrough, int layer_z_index) {
    container_id = target_container_id < 0 ? 0 : target_container_id;
    overlay = overlay_enabled != 0;
    pass_through = pointer_passthrough != 0;
    mouse_passthrough = pass_through;
    z_index = layer_z_index < 0 ? 0 : layer_z_index;
    invalidate();
}

void Watermark::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    unsigned effective_alpha = alpha ? alpha : (is_dark_theme_for_window(owner_hwnd) ? 0x42 : 0x36);
    Color color = style.fg_color ? style.fg_color : with_alpha(t->text_muted, effective_alpha);
    std::wstring label = content.empty() ? L"💧 水印" : content;

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_MATRIX_3X2_F local;
    ctx.rt->GetTransform(&local);
    float text_w = (std::min)(180.0f, (std::max)(90.0f, (float)label.size() * style.font_size * 0.82f + 24.0f));
    float text_h = (std::max)(24.0f, style.font_size * 1.8f);
    tile_count_x = gap_x > 0 ? (bounds.w + gap_x * 2 + gap_x - 1) / gap_x : 0;
    tile_count_y = gap_y > 0 ? (bounds.h + gap_y * 2 + gap_y - 1) / gap_y : 0;
    for (int y = -gap_y; y < bounds.h + gap_y; y += gap_y) {
        for (int x = -gap_x; x < bounds.w + gap_x; x += gap_x) {
            float cx = (float)x + text_w * 0.5f;
            float cy = (float)y + text_h * 0.5f;
            ctx.rt->SetTransform(local * D2D1::Matrix3x2F::Rotation(rotation, D2D1::Point2F(cx, cy)));
            draw_text(ctx, label, style, color, (float)x, (float)y, text_w, text_h);
        }
    }
    ctx.rt->SetTransform(local);

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
