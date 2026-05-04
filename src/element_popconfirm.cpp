#include "element_popconfirm.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

static int round_px(float v) {
    return (int)std::lround(v);
}

static const Element* root_element(const Element* el) {
    const Element* root = el;
    while (root && root->parent) root = root->parent;
    return root;
}

static void keep_rect_inside_root(const Element* el, Rect& r, int margin) {
    if (!el) return;
    const Element* root = root_element(el);
    if (!root) return;

    int abs_x = 0, abs_y = 0;
    el->get_absolute_pos(abs_x, abs_y);
    int root_x = 0, root_y = 0;
    root->get_absolute_pos(root_x, root_y);

    int min_x = root_x + margin;
    int min_y = root_y + margin;
    int max_x = root_x + root->bounds.w - r.w - margin;
    int max_y = root_y + root->bounds.h - r.h - margin;
    if (max_x < min_x) max_x = min_x;
    if (max_y < min_y) max_y = min_y;

    int popup_x = abs_x + r.x;
    int popup_y = abs_y + r.y;
    if (popup_x < min_x) popup_x = min_x;
    if (popup_x > max_x) popup_x = max_x;
    if (popup_y < min_y) popup_y = min_y;
    if (popup_y > max_y) popup_y = max_y;

    r.x = popup_x - abs_x;
    r.y = popup_y - abs_y;
}

static int old_popconfirm_to_advanced(int placement) {
    if (placement == 0) return 7;
    if (placement == 1) return 10;
    if (placement == 2) return 1;
    return 4;
}

static int popconfirm_side(int advanced) {
    if (advanced >= 0 && advanced <= 2) return 0;
    if (advanced >= 3 && advanced <= 5) return 1;
    if (advanced >= 6 && advanced <= 8) return 2;
    return 3;
}

static int popconfirm_align(int advanced) {
    int pos = advanced % 3;
    return pos == 0 ? -1 : (pos == 2 ? 1 : 0);
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

void Popconfirm::set_icon(const std::wstring& icon, Color color, bool visible) {
    icon_text = icon.empty() ? L"!" : icon;
    icon_color = color ? color : 0xFFE6A23C;
    show_icon = visible;
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
    int gap = round_px((float)offset * s);
    int pw = round_px((float)(popup_width > 120 ? popup_width : 286) * s);
    int ph = round_px((float)(popup_height > 80 ? popup_height : 146) * s);
    int x = (bounds.w - pw) / 2;
    int y = bounds.h + gap;
    int active = use_advanced_placement ? advanced_placement : old_popconfirm_to_advanced(placement);
    int side = popconfirm_side(active);
    int align = popconfirm_align(active);
    if (side == 2) {
        x = -pw - gap;
        y = (bounds.h - ph) / 2;
    } else if (side == 3) {
        x = bounds.w + gap;
        y = (bounds.h - ph) / 2;
    } else if (side == 0) {
        x = (bounds.w - pw) / 2;
        y = -ph - gap;
    }
    if (side == 0 || side == 1) {
        if (align < 0) x = 0;
        else if (align > 0) x = bounds.w - pw;
    } else {
        if (align < 0) y = 0;
        else if (align > 0) y = bounds.h - ph;
    }
    popup_rect = { x, y, pw, ph };
    keep_rect_inside_root(this, popup_rect, round_px(6.0f * s));

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
    float ix = (float)content_rect.x;
    float iy = (float)content_rect.y + 1.0f * s;
    float text_x = ix;
    float text_w = (float)content_rect.w;
    if (show_icon) {
        float icon_d = 20.0f * s;
        ctx.rt->FillEllipse(D2D1::Ellipse(D2D1::Point2F(ix + icon_d * 0.5f, iy + icon_d * 0.5f),
                                          icon_d * 0.5f, icon_d * 0.5f),
                            ctx.get_brush(icon_color));
        draw_text(ctx, icon_text, style, 0xFFFFFFFF, ix, iy, icon_d, icon_d,
                  0.92f, DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
                  DWRITE_WORD_WRAPPING_NO_WRAP);
        text_x = ix + icon_d + 8.0f * s;
        text_w = (float)content_rect.w - icon_d - 8.0f * s;
    }

    draw_text(ctx, content.empty() ? L"确定继续吗？" : content, style, t->text_secondary,
              text_x, (float)content_rect.y,
              text_w,
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
    } else if (trigger_mode == 0 && trigger_pressed && in_trigger(x, y)) {
        apply_open(!open, 2);
    } else if (open && close_on_outside && !in_popup(x, y) && !in_trigger(x, y)) {
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
