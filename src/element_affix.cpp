#include "element_affix.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color with_alpha(Color color, unsigned alpha) {
    return (color & 0x00FFFFFF) | ((alpha & 0xFF) << 24);
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float scale = 1.0f,
                      DWRITE_FONT_WEIGHT weight = DWRITE_FONT_WEIGHT_NORMAL) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetFontWeight(weight, DWRITE_TEXT_RANGE{ 0, (UINT32)text.size() });
    layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
    layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
    layout->SetWordWrapping(DWRITE_WORD_WRAPPING_NO_WRAP);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Affix::set_title(const std::wstring& value) {
    title = value;
    invalidate();
}

void Affix::set_body(const std::wstring& value) {
    body = value;
    invalidate();
}

void Affix::set_offset(int value) {
    offset = value < 0 ? 0 : value;
    fixed = scroll_position >= offset;
    fixed_top = fixed ? offset : bounds.y;
    invalidate();
}

void Affix::set_state(int scroll, int offset_value) {
    set_options(scroll, offset_value, container_id, placeholder_height, fixed_z_index);
}

void Affix::set_options(int scroll, int offset_value, int target_container_id, int placeholder, int z_index) {
    scroll_position = scroll < 0 ? 0 : scroll;
    offset = offset_value < 0 ? 0 : offset_value;
    container_id = target_container_id < 0 ? 0 : target_container_id;
    placeholder_height = placeholder < 0 ? 0 : placeholder;
    fixed_z_index = z_index < 0 ? 0 : z_index;
    fixed = scroll_position >= offset;
    fixed_top = fixed ? offset : bounds.y;
    invalidate();
}

void Affix::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF242637 : 0xFFFFFFFF);
    if (fixed && !style.bg_color) bg = dark ? 0xFF2D3146 : 0xFFFFFFFF;
    Color border = style.border_color ? style.border_color : t->border_default;
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = t->text_secondary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 6.0f;

    D2D1_RECT_F clip = { -6.0f, -6.0f, (float)bounds.w + 6.0f, (float)bounds.h + 6.0f };
    ctx.push_clip(clip);

    if (hovered) {
        D2D1_RECT_F shadow = { 2.0f, 3.0f, (float)bounds.w + 2.0f, (float)bounds.h + 3.0f };
        ctx.rt->FillRoundedRectangle(ROUNDED(shadow, radius, radius), ctx.get_brush(0x22000000));
    }

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(border), 1.0f);

    D2D1_RECT_F rail = { 0.0f, 0.0f, 5.0f, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rail, radius, radius), ctx.get_brush(t->accent));

    float x = (float)style.pad_left;
    float w = (float)bounds.w - style.pad_left - style.pad_right;
    draw_text(ctx, title.empty() ? L"Affix 固定区域" : title, style, title_fg,
              x, 10.0f, w, (float)bounds.h * 0.42f, 1.04f, DWRITE_FONT_WEIGHT_SEMI_BOLD);
    draw_text(ctx, body.empty() ? L"内容保持在指定位置" : body, style, body_fg,
              x, (float)bounds.h * 0.48f, w, (float)bounds.h * 0.4f, 0.95f);

    if (offset > 0 || fixed) {
        std::wstring label = fixed ? L"已固定" : (L"阈值 " + std::to_wstring(offset));
        D2D1_RECT_F tag = { (float)bounds.w - 86.0f, 10.0f, (float)bounds.w - 12.0f, 34.0f };
        ctx.rt->FillRoundedRectangle(ROUNDED(tag, 4.0f, 4.0f), ctx.get_brush(with_alpha(t->accent, 0x22)));
        draw_text(ctx, label, style, t->accent, tag.left + 6.0f, tag.top, tag.right - tag.left - 12.0f, tag.bottom - tag.top, 0.85f);
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}

void Affix::on_mouse_enter() {
    hovered = true;
    invalidate();
}

void Affix::on_mouse_leave() {
    hovered = false;
    pressed = false;
    invalidate();
}
