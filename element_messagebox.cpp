#include "element_messagebox.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static bool contains_rect(const Rect& r, int x, int y) {
    return x >= r.x && x < r.x + r.w && y >= r.y && y < r.y + r.h;
}

float MessageBoxElement::scale() const {
    float s = style.font_size / 14.0f;
    if (s < 0.75f) s = 0.75f;
    return s;
}

void MessageBoxElement::layout(const Rect& available) {
    bounds = available;
    update_layout();
}

void MessageBoxElement::update_layout() {
    float s = scale();
    int margin = round_px(24.0f * s);
    int dialog_w = round_px(420.0f * s);
    int dialog_h = round_px(220.0f * s);
    int min_w = round_px(280.0f * s);

    int max_w = bounds.w - margin * 2;
    if (max_w < min_w) max_w = bounds.w > 0 ? bounds.w : min_w;
    if (max_w < dialog_w) dialog_w = max_w;
    if (dialog_w < min_w && bounds.w >= min_w) dialog_w = min_w;
    if (dialog_w > bounds.w) dialog_w = bounds.w;

    int max_h = bounds.h - margin * 2;
    if (max_h > 0 && max_h < dialog_h) dialog_h = max_h;
    if (dialog_h > bounds.h) dialog_h = bounds.h;

    m_dialog_rect = {
        (bounds.w - dialog_w) / 2,
        (bounds.h - dialog_h) / 2,
        dialog_w,
        dialog_h
    };
    if (m_dialog_rect.x < 0) m_dialog_rect.x = 0;
    if (m_dialog_rect.y < 0) m_dialog_rect.y = 0;

    int pad = round_px(20.0f * s);
    int close_size = round_px(28.0f * s);
    m_close_rect = {
        m_dialog_rect.x + m_dialog_rect.w - pad - close_size + round_px(4.0f * s),
        m_dialog_rect.y + round_px(14.0f * s),
        close_size,
        close_size
    };

    int button_w = round_px(88.0f * s);
    int button_h = round_px(32.0f * s);
    int gap = round_px(10.0f * s);
    int bottom = m_dialog_rect.y + m_dialog_rect.h - pad - button_h;
    int right = m_dialog_rect.x + m_dialog_rect.w - pad;
    m_confirm_rect = { right - button_w, bottom, button_w, button_h };
    m_cancel_rect = show_cancel
        ? Rect{ m_confirm_rect.x - gap - button_w, bottom, button_w, button_h }
        : Rect{ 0, 0, 0, 0 };
}

MessageBoxElement::Part MessageBoxElement::part_at(int x, int y) const {
    if (contains_rect(m_close_rect, x, y)) return PartClose;
    if (contains_rect(m_confirm_rect, x, y)) return PartConfirm;
    if (show_cancel && contains_rect(m_cancel_rect, x, y)) return PartCancel;
    return PartNone;
}

void MessageBoxElement::request_result(Result result) {
    if (m_close_requested || !owner_hwnd) return;
    m_close_requested = true;
    PostMessageW(owner_hwnd, WM_USER + 110, (WPARAM)id, (LPARAM)result);
}

void MessageBoxElement::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;
    update_layout();

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();
    float radius = 8.0f * s;

    D2D1_RECT_F overlay = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRectangle(overlay, ctx.get_brush(dark ? 0x99000000 : 0x66000000));

    D2D1_RECT_F dialog = {
        (float)m_dialog_rect.x,
        (float)m_dialog_rect.y,
        (float)(m_dialog_rect.x + m_dialog_rect.w),
        (float)(m_dialog_rect.y + m_dialog_rect.h)
    };

    Color dialog_bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color border = dark ? 0xFF45475A : 0xFFE4E7ED;
    Color title_fg = dark ? t->text_primary : 0xFF303133;
    Color body_fg = dark ? t->text_secondary : 0xFF606266;
    Color close_fg = (m_hover_part == PartClose) ? t->accent : (dark ? 0xFFA6ADC8 : 0xFF909399);

    ctx.rt->FillRoundedRectangle(ROUNDED(dialog, radius, radius), ctx.get_brush(dialog_bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(dialog.left + 0.5f, dialog.top + 0.5f,
        dialog.right - 0.5f, dialog.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

    float pad = 20.0f * s;
    float title_h = 28.0f * s;
    float title_x = (float)m_dialog_rect.x + pad;
    float title_y = (float)m_dialog_rect.y + 18.0f * s;
    float title_w = (float)m_dialog_rect.w - pad * 2.0f - 24.0f * s;

    if (!title.empty()) {
        auto* layout = ctx.create_text_layout(title, style.font_name, style.font_size * 1.14f,
                                              title_w, title_h);
        if (layout) {
            apply_emoji_font_fallback(layout, title);
            layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
            ctx.rt->DrawTextLayout(D2D1::Point2F(title_x, title_y), layout,
                ctx.get_brush(title_fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    float cx = (float)m_close_rect.x + (float)m_close_rect.w * 0.5f;
    float cy = (float)m_close_rect.y + (float)m_close_rect.h * 0.5f;
    float cs = 6.5f * s;
    auto* close_br = ctx.get_brush(close_fg);
    ctx.rt->DrawLine(D2D1::Point2F(cx - cs, cy - cs), D2D1::Point2F(cx + cs, cy + cs), close_br, 1.6f * s);
    ctx.rt->DrawLine(D2D1::Point2F(cx + cs, cy - cs), D2D1::Point2F(cx - cs, cy + cs), close_br, 1.6f * s);

    float body_x = (float)m_dialog_rect.x + pad;
    float body_y = title_y + title_h + 8.0f * s;
    float body_w = (float)m_dialog_rect.w - pad * 2.0f;
    float body_h = (float)(m_confirm_rect.y - round_px(18.0f * s)) - body_y;
    if (body_h < 24.0f * s) body_h = 24.0f * s;

    if (!text.empty()) {
        auto* body_layout = ctx.create_text_layout(text, style.font_name, style.font_size,
                                                   body_w, body_h);
        if (body_layout) {
            apply_emoji_font_fallback(body_layout, text);
            body_layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_LEADING);
            body_layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_NEAR);
            body_layout->SetWordWrapping(DWRITE_WORD_WRAPPING_WRAP);
            ctx.rt->DrawTextLayout(D2D1::Point2F(body_x, body_y), body_layout,
                ctx.get_brush(body_fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            body_layout->Release();
        }
    }

    if (show_cancel) {
        draw_button(ctx, m_cancel_rect, cancel_text, false,
                    m_hover_part == PartCancel, m_press_part == PartCancel);
    }
    draw_button(ctx, m_confirm_rect, confirm_text, true,
                m_hover_part == PartConfirm, m_press_part == PartConfirm);

    ctx.rt->SetTransform(saved);
}

void MessageBoxElement::draw_button(RenderContext& ctx, const Rect& r, const std::wstring& label,
                             bool primary, bool hot, bool down) {
    if (r.w <= 0 || r.h <= 0) return;

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();
    float radius = 4.0f * s;

    Color bg = primary ? t->accent : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = primary ? t->accent : (dark ? 0xFF585B70 : 0xFFDCDFE6);
    Color fg = primary ? 0xFFFFFFFF : (dark ? t->text_primary : 0xFF606266);

    if (primary && hot) bg = down ? 0xFF5C8FE6 : 0xFF79A8F5;
    if (!primary && hot) {
        bg = dark ? 0xFF313244 : 0xFFEAF2FF;
        border = t->accent;
        fg = t->accent;
    }

    D2D1_RECT_F rect = {
        (float)r.x,
        (float)r.y,
        (float)(r.x + r.w),
        (float)(r.y + r.h)
    };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

    auto* layout = ctx.create_text_layout(label, style.font_name, style.font_size,
                                          (float)r.w, (float)r.h);
    if (layout) {
        apply_emoji_font_fallback(layout, label);
        layout->SetTextAlignment(DWRITE_TEXT_ALIGNMENT_CENTER);
        layout->SetParagraphAlignment(DWRITE_PARAGRAPH_ALIGNMENT_CENTER);
        ctx.rt->DrawTextLayout(D2D1::Point2F((float)r.x, (float)r.y), layout,
            ctx.get_brush(fg), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
        layout->Release();
    }
}

void MessageBoxElement::on_mouse_move(int x, int y) {
    Part old = m_hover_part;
    m_hover_part = part_at(x, y);
    if (m_hover_part != old) invalidate();
}

void MessageBoxElement::on_mouse_leave() {
    m_hover_part = PartNone;
    m_press_part = PartNone;
    invalidate();
}

void MessageBoxElement::on_mouse_down(int x, int y, MouseButton) {
    m_press_part = part_at(x, y);
    invalidate();
}

void MessageBoxElement::on_mouse_up(int x, int y, MouseButton) {
    Part release_part = part_at(x, y);
    Part clicked = (m_press_part != PartNone && m_press_part == release_part) ? m_press_part : PartNone;
    m_press_part = PartNone;
    m_hover_part = release_part;
    invalidate();

    switch (clicked) {
    case PartConfirm: request_result(ResultConfirm); break;
    case PartCancel:  request_result(ResultCancel); break;
    case PartClose:   request_result(show_cancel ? ResultCancel : ResultClose); break;
    default: break;
    }
}

void MessageBoxElement::on_key_down(int vk, int) {
    if (vk == VK_RETURN) {
        request_result(ResultConfirm);
    } else if (vk == VK_ESCAPE) {
        request_result(show_cancel ? ResultCancel : ResultClose);
    }
}
