#include "element_infobox.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static Color infobox_accent_for_type(int type, const Theme* t) {
    if (type == 1) return 0xFF16A34A;
    if (type == 2) return 0xFFF59E0B;
    if (type == 3) return 0xFFDC2626;
    return t->accent;
}

static std::wstring infobox_icon_for_type(int type) {
    if (type == 1) return L"✓";
    if (type == 2) return L"!";
    if (type == 3) return L"×";
    return L"i";
}

bool InfoBox::close_hit(int x, int y) const {
    if (!closable) return false;
    int size = (std::max)(18, (int)(style.font_size * 1.6f));
    int left = bounds.w - style.pad_right - size;
    int top = style.pad_top;
    return x >= left && x < left + size && y >= top && y < top + size;
}

Element* InfoBox::hit_test(int x, int y) {
    if (!visible || !enabled || !closable) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    return close_hit(lx, ly) ? this : nullptr;
}

void InfoBox::on_mouse_up(int x, int y, MouseButton btn) {
    Element::on_mouse_up(x, y, btn);
    if (btn == MouseButton::Left && close_hit(x, y)) {
        closed = true;
        invalidate();
    }
}

void InfoBox::set_texts(const std::wstring& new_header, const std::wstring& new_body) {
    header = new_header;
    text = new_body;
    closed = false;
    invalidate();
}

void InfoBox::set_options(int type, int close_enabled, Color accent, const std::wstring& icon) {
    info_type = (std::max)(0, (std::min)(3, type));
    closable = close_enabled != 0;
    mouse_passthrough = !closable;
    accent_color = accent;
    icon_text = icon;
    invalidate();
}

void InfoBox::set_closed(bool value) {
    closed = value;
    invalidate();
}

bool InfoBox::is_closed() const {
    return closed;
}

static int estimated_line_count(const std::wstring& value, int chars_per_line) {
    if (value.empty()) return 0;
    if (chars_per_line < 1) chars_per_line = 1;
    int lines = 1;
    int current = 0;
    for (wchar_t ch : value) {
        if (ch == L'\n') {
            lines++;
            current = 0;
            continue;
        }
        current++;
        if (current >= chars_per_line) {
            lines++;
            current = 0;
        }
    }
    return lines;
}

int InfoBox::preferred_height() const {
    int pad_y = style.pad_top + style.pad_bottom;
    int icon_h = (std::max)(18, (int)(style.font_size * 2.0f));
    int close_reserved = closable ? (int)(style.font_size * 2.0f) : 0;
    int text_w = bounds.w - style.pad_left * 3 - icon_h - style.pad_right - close_reserved;
    int chars_per_line = text_w > 0 ? (int)(text_w / (style.font_size * 0.58f)) : 12;
    int header_lines = estimated_line_count(header, chars_per_line);
    int body_lines = estimated_line_count(text, chars_per_line);
    int header_h = header_lines > 0 ? (int)(header_lines * style.font_size * 1.45f) : 0;
    int body_h = body_lines > 0 ? (int)(body_lines * style.font_size * 1.35f) : 0;
    int gap = header_h > 0 && body_h > 0 ? 4 : 0;
    return (std::max)(pad_y + icon_h, pad_y + header_h + gap + body_h);
}

void InfoBox::paint(RenderContext& ctx) {
    if (!visible || closed || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF232634 : 0xFFEAF2FF);
    Color border = style.border_color ? style.border_color : (dark ? 0xFF3A4253 : 0xFFC8D6EF);
    Color title_fg = style.fg_color ? style.fg_color : t->text_primary;
    Color body_fg = style.fg_color ? style.fg_color : (dark ? 0xFFD7DCEB : 0xFF5C5F77);
    Color accent = accent_color ? accent_color : infobox_accent_for_type(info_type, t);

    float r = style.corner_radius > 0 ? style.corner_radius : 8.0f;
    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };

    ctx.push_clip(rect);

    auto* bg_br = ctx.get_brush(bg);
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, r, r), bg_br);

    auto* border_br = ctx.get_brush(border);
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), r, r), border_br, 1.0f);

    float pad_l = (float)style.pad_left;
    float pad_t = (float)style.pad_top;
    float pad_r = (float)style.pad_right;
    float pad_b = (float)style.pad_bottom;
    float content_h = (float)bounds.h - pad_t - pad_b;
    if (content_h < 1.0f) content_h = 1.0f;

    float icon_d = style.font_size * 2.0f;
    if (icon_d < 18.0f) icon_d = 18.0f;
    if (icon_d > content_h) icon_d = content_h;

    float icon_x = pad_l;
    float icon_y = pad_t + (content_h - icon_d) * 0.5f;
    if (icon_y < pad_t) icon_y = pad_t;

    Color icon_fill = (accent & 0x00FFFFFF) | 0x33000000;
    auto* icon_fill_br = ctx.get_brush(icon_fill);
    auto* accent_br = ctx.get_brush(accent);
    D2D1_ELLIPSE icon_shape = D2D1::Ellipse(
        D2D1::Point2F(icon_x + icon_d * 0.5f, icon_y + icon_d * 0.5f),
        icon_d * 0.5f, icon_d * 0.5f);
    ctx.rt->FillEllipse(icon_shape, icon_fill_br);
    ctx.rt->DrawEllipse(icon_shape, accent_br, 1.0f);

    std::wstring icon_label = icon_text.empty() ? infobox_icon_for_type(info_type) : icon_text;
    auto* icon_layout = ctx.create_text_layout(
        icon_label, style.font_name, style.font_size * 1.15f, icon_d, icon_d);
    if (icon_layout) {
        apply_emoji_font_fallback(icon_layout, icon_label);
        icon_layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
        icon_layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
        ctx.rt->DrawTextLayout(D2D1::Point2F(icon_x, icon_y), icon_layout,
            ctx.get_brush(0xFFFFFFFF), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
        icon_layout->Release();
    }

    float text_x = icon_x + icon_d + pad_l;
    float close_reserved = closable ? style.font_size * 2.0f : 0.0f;
    float max_w = (float)bounds.w - text_x - pad_r - close_reserved;
    if (max_w < 1.0f) max_w = 1.0f;

    float title_h = 0.0f;
    if (!header.empty()) {
        auto* title_layout = ctx.create_text_layout(
            header, style.font_name, style.font_size * 1.10f, max_w, (float)bounds.h);
        if (title_layout) {
            title_layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            title_layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
            title_layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
            DWRITE_TEXT_METRICS tm;
            if (SUCCEEDED(title_layout->GetMetrics(&tm))) title_h = tm.height;
            ctx.rt->DrawTextLayout(D2D1::Point2F(text_x, pad_t), title_layout,
                ctx.get_brush(title_fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            title_layout->Release();
        }
    }

    float body_y = pad_t + title_h;
    if (!header.empty()) body_y += 2.0f;
    float body_h = (float)bounds.h - body_y - pad_b;
    if (body_h < 1.0f) body_h = 1.0f;

    if (!text.empty()) {
        auto* body_layout = ctx.create_text_layout(
            text, style.font_name, style.font_size, max_w, body_h);
        if (body_layout) {
            body_layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            body_layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
            body_layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
            ctx.rt->DrawTextLayout(D2D1::Point2F(text_x, body_y), body_layout,
                ctx.get_brush(body_fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            body_layout->Release();
        }
    }

    if (closable) {
        float size = (std::max)(18.0f, style.font_size * 1.6f);
        float close_x = (float)bounds.w - pad_r - size;
        float close_y = pad_t;
        auto* close_layout = ctx.create_text_layout(L"×", style.font_name, style.font_size, size, size);
        if (close_layout) {
            close_layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
            close_layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            ctx.rt->DrawTextLayout(D2D1::Point2F(close_x, close_y), close_layout,
                ctx.get_brush(t->text_muted), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            close_layout->Release();
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
