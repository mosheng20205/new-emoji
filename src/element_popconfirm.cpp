#include "element_popconfirm.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static void keep_rect_inside_parent(const Element* el, Rect& r, int margin) {
    if (!el || !el->parent) return;
    int min_x = margin - el->bounds.x;
    int min_y = margin - el->bounds.y;
    int max_x = el->parent->bounds.w - el->bounds.x - r.w - margin;
    int max_y = el->parent->bounds.h - el->bounds.y - r.h - margin;
    if (max_x < min_x) max_x = min_x;
    if (max_y < min_y) max_y = min_y;
    if (r.x < min_x) r.x = min_x;
    if (r.x > max_x) r.x = max_x;
    if (r.y < min_y) r.y = min_y;
    if (r.y > max_y) r.y = max_y;
}

static void draw_text(RenderContext& ctx, const std::wstring& text, const ElementStyle& style,
                      Color color, float x, float y, float w, float h,
                      float font_scale = 1.0f,
                      DWRITE_TEXT_ALIGNMENT align = DWRITE_TEXT_ALIGNMENT_LEADING,
                      DWRITE_PARAGRAPH_ALIGNMENT paragraph = DWRITE_PARAGRAPH_ALIGNMENT_NEAR,
                      DWRITE_WORD_WRAPPING wrap = DWRITE_WORD_WRAPPING_WRAP) {
    if (text.empty() || w <= 0.0f || h <= 0.0f) return;
    auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size * font_scale, w, h);
    if (!layout) return;
    apply_emoji_font_fallback(layout, text);
    layout->SetTextAlignment(align);
    layout->SetParagraphAlignment(paragraph);
    layout->SetWordWrapping(wrap);
    ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
        ctx.get_brush(color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
    layout->Release();
}

void Popconfirm::set_buttons(const std::wstring& confirm, const std::wstring& cancel) {
    confirm_text = confirm;
    cancel_text = cancel;
    result_action = 1;
    last_action = 1;
    invalidate();
}

void Popconfirm::reset_result() {
    last_result = -1;
    result_action = 1;
    last_action = 1;
    invalidate();
}

void Popconfirm::choose_result(int result, int action) {
    last_result = result ? 1 : 0;
    if (last_result == 1) ++confirm_count;
    else ++cancel_count;
    result_action = action;
    apply_open(false, action);
    if (result_cb) result_cb(id, last_result, confirm_count + cancel_count, action);
}

void Popconfirm::update_popup_rect() {
    float s = scale();
    int gap = round_px(8.0f * s);
    int pw = round_px((float)(popup_width > 120 ? popup_width : 286) * s);
    int ph = round_px((float)(popup_height > 80 ? popup_height : 146) * s);
    int x = (bounds.w - pw) / 2;
    int y = bounds.h + gap;
    if (placement == 0) {
        x = -pw - gap;
        y = (bounds.h - ph) / 2;
    } else if (placement == 1) {
        x = bounds.w + gap;
        y = (bounds.h - ph) / 2;
    } else if (placement == 2) {
        x = (bounds.w - pw) / 2;
        y = -ph - gap;
    }
    popup_rect = { x, y, pw, ph };
    keep_rect_inside_parent(this, popup_rect, round_px(6.0f * s));

    int button_w = round_px(76.0f * s);
    int button_h = round_px(30.0f * s);
    int pad = round_px(14.0f * s);
    int gap_btn = round_px(8.0f * s);
    int by = popup_rect.y + popup_rect.h - pad - button_h;
    confirm_rect = {
        popup_rect.x + popup_rect.w - pad - button_w,
        by,
        button_w,
        button_h
    };
    cancel_rect = {
        confirm_rect.x - gap_btn - button_w,
        by,
        button_w,
        button_h
    };
}

Popconfirm::ButtonPart Popconfirm::button_at(int x, int y) const {
    if (confirm_rect.contains(x, y)) return ButtonConfirm;
    if (cancel_rect.contains(x, y)) return ButtonCancel;
    return ButtonNone;
}

void Popconfirm::draw_button(RenderContext& ctx, const Rect& r, const std::wstring& label,
                             bool primary, bool hot, bool down, bool focused) {
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();
    Color bg = primary ? t->accent : (dark ? 0xFF242637 : 0xFFFFFFFF);
    Color border = primary ? t->accent : t->border_default;
    Color fg = primary ? 0xFFFFFFFF : t->text_primary;
    if (hot) {
        bg = primary ? (down ? 0xFF5C8FE6 : 0xFF79A8F5) : (dark ? 0xFF313244 : 0xFFEAF2FF);
        border = primary ? bg : t->accent;
        fg = primary ? 0xFFFFFFFF : t->accent;
    }

    D2D1_RECT_F rect = {
        (float)r.x,
        (float)r.y,
        (float)(r.x + r.w),
        (float)(r.y + r.h)
    };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, 4.0f * s, 4.0f * s), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), 4.0f * s, 4.0f * s),
        ctx.get_brush(border), 1.0f);
    if (focused) {
        ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 2.5f, rect.top + 2.5f,
            rect.right - 2.5f, rect.bottom - 2.5f), 3.0f * s, 3.0f * s),
            ctx.get_brush(primary ? 0xFFFFFFFF : t->accent), 1.0f);
    }
    draw_text(ctx, label, style, fg, rect.left, rect.top, (float)r.w, (float)r.h,
              1.0f, DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
              DWRITE_WORD_WRAPPING_NO_WRAP);
}

void Popconfirm::draw_popup_content(RenderContext& ctx, const Rect& content_rect) {
    const Theme* t = theme_for_window(owner_hwnd);
    float s = scale();
    float icon_d = 20.0f * s;
    float ix = (float)content_rect.x;
    float iy = (float)content_rect.y + 1.0f * s;
    ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(ix + icon_d * 0.5f, iy + icon_d * 0.5f),
                                      icon_d * 0.5f, icon_d * 0.5f),
                        ctx.get_brush(0xFFE6A23C));
    draw_text(ctx, L"!", style, 0xFFFFFFFF, ix, iy, icon_d, icon_d,
              0.92f, DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
              DWRITE_WORD_WRAPPING_NO_WRAP);

    draw_text(ctx, content.empty() ? L"Are you sure?" : content, style, t->text_secondary,
              ix + icon_d + 8.0f * s, (float)content_rect.y,
              (float)content_rect.w - icon_d - 8.0f * s,
              (float)content_rect.h - 44.0f * s);

    draw_button(ctx, cancel_rect, cancel_text, false,
                hover_button == ButtonCancel, press_button == ButtonCancel,
                has_focus && focus_part == 2);
    draw_button(ctx, confirm_rect, confirm_text, true,
                hover_button == ButtonConfirm, press_button == ButtonConfirm,
                has_focus && focus_part == 3);
}

void Popconfirm::on_mouse_move(int x, int y) {
    update_popup_rect();
    ButtonPart hot = open ? button_at(x, y) : ButtonNone;
    if (hot != hover_button) {
        hover_button = hot;
        invalidate();
    }
}

void Popconfirm::on_mouse_leave() {
    Popover::on_mouse_leave();
    hover_button = ButtonNone;
    press_button = ButtonNone;
    invalidate();
}

void Popconfirm::on_mouse_down(int x, int y, MouseButton btn) {
    update_popup_rect();
    press_button = open ? button_at(x, y) : ButtonNone;
    Popover::on_mouse_down(x, y, btn);
}

void Popconfirm::on_mouse_up(int x, int y, MouseButton) {
    update_popup_rect();
    ButtonPart release = open ? button_at(x, y) : ButtonNone;
    if (press_button != ButtonNone && press_button == release) {
        choose_result(release == ButtonConfirm ? 1 : 0, 2);
    } else if (trigger_pressed && in_trigger(x, y)) {
        apply_open(!open, 2);
    } else if (open && !in_popup(x, y) && !in_trigger(x, y)) {
        apply_open(false, 2);
    }
    press_button = ButtonNone;
    trigger_pressed = false;
    popup_pressed = false;
    invalidate();
}

void Popconfirm::on_key_down(int vk, int) {
    if (vk == VK_ESCAPE) {
        choose_result(0, 3);
    } else if (vk == VK_TAB && open) {
        if (focus_part == 2) focus_part = 3;
        else if (focus_part == 3) focus_part = 1;
        else focus_part = 2;
        invalidate();
    } else if (vk == VK_LEFT || vk == VK_RIGHT) {
        if (open) {
            focus_part = focus_part == 3 ? 2 : 3;
            invalidate();
        }
    } else if (vk == VK_RETURN || vk == VK_SPACE) {
        if (!open) {
            apply_open(true, 3);
        } else if (focus_part == 2) {
            choose_result(0, 3);
        } else {
            choose_result(1, 3);
        }
    }
}
