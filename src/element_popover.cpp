#include "element_popover.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include "theme.h"
#include <algorithm>
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

static int old_popover_to_advanced(int placement) {
    if (placement == 0) return 7;
    if (placement == 1) return 10;
    if (placement == 2) return 1;
    return 4;
}

static int popup_side(int advanced) {
    if (advanced >= 0 && advanced <= 2) return 0;
    if (advanced >= 3 && advanced <= 5) return 1;
    if (advanced >= 6 && advanced <= 8) return 2;
    return 3;
}

static int popup_align(int advanced) {
    int pos = advanced % 3;
    return pos == 0 ? -1 : (pos == 2 ? 1 : 0);
}

float Popover::scale() const {
    float s = style.font_size / 14.0f;
    return s < 0.75f ? 0.75f : s;
}

void Popover::set_title(const std::wstring& value) {
    title = value;
    last_action = 1;
    invalidate();
}

void Popover::set_content(const std::wstring& value) {
    content = value;
    last_action = 1;
    invalidate();
}

void Popover::set_placement(int value) {
    if (value < 0) value = 0;
    if (value > 3) value = 3;
    placement = value;
    advanced_placement = old_popover_to_advanced(value);
    use_advanced_placement = false;
    last_action = 1;
    invalidate();
}

void Popover::set_open(bool value) {
    apply_open(value, 1);
}

void Popover::set_options(int new_placement, int is_open, int width, int height, int closable) {
    set_placement(new_placement);
    popup_width = width > 120 ? width : 250;
    popup_height = height > 80 ? height : 132;
    close_enabled = closable != 0;
    apply_open(is_open != 0, 1);
}

void Popover::set_behavior(int trigger, int outside_close, int arrow, int new_offset) {
    if (trigger < 0) trigger = 0;
    if (trigger > 3) trigger = 3;
    trigger_mode = trigger;
    close_on_outside = outside_close != 0;
    show_arrow = arrow != 0;
    offset = new_offset >= 0 ? new_offset : 8;
    last_action = 1;
    invalidate();
}

void Popover::trigger_open(bool value, int action) {
    apply_open(value, action);
}

void Popover::notify_action(int action) {
    if (action_cb) action_cb(id, open ? 1 : 0, close_count, action);
}

void Popover::apply_open(bool value, int action) {
    if (open != value) {
        open = value;
        if (open) {
            ++open_count;
            focus_part = 1;
        } else {
            ++close_count;
            close_hover = false;
            popup_pressed = false;
            focus_part = 0;
        }
        notify_action(action);
    }
    last_action = action;
    invalidate();
}

bool Popover::in_trigger(int x, int y) const {
    return x >= 0 && y >= 0 && x < bounds.w && y < bounds.h;
}

bool Popover::in_popup(int x, int y) const {
    return popup_rect.contains(x, y);
}

bool Popover::in_close(int x, int y) const {
    return has_close_button() && close_rect.contains(x, y);
}

Element* Popover::hit_test(int x, int y) {
    if (!visible || !enabled) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    if (in_trigger(lx, ly)) return this;
    return nullptr;
}

Element* Popover::hit_test_overlay(int x, int y) {
    if (!visible || !enabled || !open) return nullptr;
    int lx = x - bounds.x;
    int ly = y - bounds.y;
    update_popup_rect();
    for (auto it = children.rbegin(); it != children.rend(); ++it) {
        if (!(*it)->visible) continue;
        Element* hit = (*it)->hit_test(lx, ly);
        if (hit) return hit;
    }
    return this;
}

void Popover::update_popup_rect() {
    float s = scale();
    int gap = round_px((float)offset * s);
    int pw = round_px((float)popup_width * s);
    int ph = round_px((float)popup_height * s);
    int x = (bounds.w - pw) / 2;
    int y = bounds.h + gap;
    int active = use_advanced_placement ? advanced_placement : old_popover_to_advanced(placement);
    int side = popup_side(active);
    int align = popup_align(active);
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
    close_rect = {
        popup_rect.x + popup_rect.w - round_px(32.0f * s),
        popup_rect.y + round_px(8.0f * s),
        round_px(24.0f * s),
        round_px(24.0f * s)
    };
    if (Element* slot = content_parent()) {
        int pad = round_px(14.0f * s);
        Rect body = {
            popup_rect.x + pad,
            popup_rect.y + round_px(44.0f * s),
            popup_rect.w - pad * 2,
            popup_rect.h - round_px(56.0f * s)
        };
        if (body.w < 0) body.w = 0;
        if (body.h < 0) body.h = 0;
        slot->layout(body);
    }
}

void Popover::draw_trigger(RenderContext& ctx) {
    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    Color bg = style.bg_color ? style.bg_color : (dark ? 0xFF313244 : 0xFFFFFFFF);
    Color border = style.border_color ? style.border_color : (open || hovered ? t->accent : t->border_default);
    Color fg = style.fg_color ? style.fg_color : t->text_primary;
    float radius = style.corner_radius > 0.0f ? style.corner_radius : 4.0f * scale();

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(0.5f, 0.5f,
        (float)bounds.w - 0.5f, (float)bounds.h - 0.5f), radius, radius),
        ctx.get_brush(has_focus && focus_part == 0 ? t->accent : border), has_focus && focus_part == 0 ? 2.0f : 1.0f);
    draw_text(ctx, text.empty() ? L"弹出框" : text, style, fg,
              (float)style.pad_left, 0.0f,
              (float)bounds.w - style.pad_left - style.pad_right,
              (float)bounds.h, 1.0f,
              DWRITE_TEXT_ALIGNMENT_CENTER, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
              DWRITE_WORD_WRAPPING_NO_WRAP);
}

void Popover::draw_popup_content(RenderContext& ctx, const Rect& content_rect) {
    if (has_content_slot()) {
        if (Element* slot = content_parent()) slot->paint(ctx);
        return;
    }
    const Theme* t = theme_for_window(owner_hwnd);
    draw_text(ctx, content, style, t->text_secondary,
              (float)content_rect.x, (float)content_rect.y,
              (float)content_rect.w, (float)content_rect.h);
}

void Popover::draw_popup(RenderContext& ctx) {
    if (!open) return;
    update_popup_rect();

    const Theme* t = theme_for_window(owner_hwnd);
    bool dark = is_dark_theme_for_window(owner_hwnd);
    float s = scale();
    Color bg = dark ? 0xFF242637 : 0xFFFFFFFF;
    Color border = t->border_default;
    float radius = 6.0f * s;

    D2D1_RECT_F rect = {
        (float)popup_rect.x,
        (float)popup_rect.y,
        (float)(popup_rect.x + popup_rect.w),
        (float)(popup_rect.y + popup_rect.h)
    };
    if (show_arrow) draw_arrow(ctx, bg, border);
    ctx.rt->FillRoundedRectangle(ROUNDED(rect, radius, radius), ctx.get_brush(bg));
    ctx.rt->DrawRoundedRectangle(ROUNDED(D2D1::RectF(rect.left + 0.5f, rect.top + 0.5f,
        rect.right - 0.5f, rect.bottom - 0.5f), radius, radius), ctx.get_brush(border), 1.0f);

    float pad = 14.0f * s;
    draw_text(ctx, title.empty() ? L"弹出框" : title, style, t->text_primary,
              rect.left + pad, rect.top + 10.0f * s,
              (float)popup_rect.w - pad * 2.0f - (has_close_button() ? 22.0f * s : 0.0f),
              24.0f * s, 1.04f,
              DWRITE_TEXT_ALIGNMENT_LEADING, DWRITE_PARAGRAPH_ALIGNMENT_CENTER,
              DWRITE_WORD_WRAPPING_NO_WRAP);

    if (has_close_button()) {
        Color close_fg = close_hover ? t->accent : t->text_secondary;
        if (has_focus && focus_part == 2) {
            D2D1_RECT_F focus = {
                (float)close_rect.x + 2.0f * s,
                (float)close_rect.y + 2.0f * s,
                (float)(close_rect.x + close_rect.w) - 2.0f * s,
                (float)(close_rect.y + close_rect.h) - 2.0f * s
            };
            ctx.rt->DrawRoundedRectangle(ROUNDED(focus, 4.0f * s, 4.0f * s),
                                         ctx.get_brush(t->accent), 1.0f * s);
        }
        float cx = (float)close_rect.x + close_rect.w * 0.5f;
        float cy = (float)close_rect.y + close_rect.h * 0.5f;
        float cs = 5.5f * s;
        ctx.rt->DrawLine(D2D1::Point2F(cx - cs, cy - cs), D2D1::Point2F(cx + cs, cy + cs),
                         ctx.get_brush(close_fg), 1.3f * s);
        ctx.rt->DrawLine(D2D1::Point2F(cx + cs, cy - cs), D2D1::Point2F(cx - cs, cy + cs),
                         ctx.get_brush(close_fg), 1.3f * s);
    }

    Rect body = {
        popup_rect.x + round_px(pad),
        popup_rect.y + round_px(44.0f * s),
        popup_rect.w - round_px(pad * 2.0f),
        popup_rect.h - round_px(56.0f * s)
    };
    draw_popup_content(ctx, body);
}

void Popover::draw_arrow(RenderContext& ctx, Color bg, Color) {
    float s = scale();
    float size = 10.0f * s;
    float cx = (float)popup_rect.x + popup_rect.w * 0.5f;
    float cy = (float)popup_rect.y + popup_rect.h * 0.5f;
    int active = use_advanced_placement ? advanced_placement : old_popover_to_advanced(placement);
    int side = popup_side(active);
    if (side == 2) cx = (float)popup_rect.x + popup_rect.w;
    else if (side == 3) cx = (float)popup_rect.x;
    else if (side == 0) cy = (float)popup_rect.y + popup_rect.h;
    else cy = (float)popup_rect.y;

    D2D1_RECT_F diamond = {
        cx - size * 0.5f, cy - size * 0.5f,
        cx + size * 0.5f, cy + size * 0.5f
    };
    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Rotation(45.0f, D2D1::Point2F(cx, cy)));
    ctx.rt->FillRectangle(diamond, ctx.get_brush(bg));
    ctx.rt->SetTransform(saved);
}

void Popover::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));
    draw_trigger(ctx);
    ctx.rt->SetTransform(saved);
}

void Popover::paint_overlay(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));
    draw_popup(ctx);
    ctx.rt->SetTransform(saved);
}

void Popover::on_mouse_enter() {
    hovered = true;
    if (trigger_mode == 1) apply_open(true, 2);
    invalidate();
}

void Popover::on_mouse_move(int x, int y) {
    update_popup_rect();
    if (trigger_mode == 1 && open && !in_trigger(x, y) && !in_popup(x, y)) {
        apply_open(false, 2);
        return;
    }
    bool hot = open && in_close(x, y);
    if (hot != close_hover) {
        close_hover = hot;
        invalidate();
    }
}

void Popover::on_mouse_leave() {
    hovered = false;
    trigger_pressed = false;
    popup_pressed = false;
    close_hover = false;
    if (trigger_mode == 1 && open) apply_open(false, 2);
    invalidate();
}

void Popover::on_mouse_down(int x, int y, MouseButton) {
    update_popup_rect();
    trigger_pressed = in_trigger(x, y);
    popup_pressed = open && in_popup(x, y);
    invalidate();
}

void Popover::on_mouse_up(int x, int y, MouseButton) {
    update_popup_rect();
    if (trigger_mode == 0 && trigger_pressed && in_trigger(x, y)) {
        apply_open(!open, 2);
    } else if (open && close_on_outside && !in_popup(x, y) && !in_trigger(x, y)) {
        apply_open(false, 2);
    } else if (popup_pressed && in_close(x, y)) {
        apply_open(false, 2);
    }
    trigger_pressed = false;
    popup_pressed = false;
    invalidate();
}

void Popover::on_key_down(int vk, int) {
    if (vk == VK_ESCAPE) {
        apply_open(false, 3);
    } else if (vk == VK_TAB && open) {
        if (has_close_button()) {
            focus_part = focus_part == 2 ? 1 : 2;
        } else {
            focus_part = focus_part == 1 ? 0 : 1;
        }
        invalidate();
    } else if ((vk == VK_RETURN || vk == VK_SPACE) && trigger_mode != 3) {
        if (open && focus_part == 2 && has_close_button()) {
            apply_open(false, 3);
        } else {
            apply_open(!open, 3);
        }
    }
}

void Popover::on_focus() {
    Element::on_focus();
    focus_part = open ? 1 : 0;
    if (trigger_mode == 2) apply_open(true, 4);
}

void Popover::on_blur() {
    Element::on_blur();
    close_hover = false;
    popup_pressed = false;
    if (trigger_mode == 2) apply_open(false, 4);
    invalidate();
}

Element* Popover::content_parent() {
    if (content_parent_id <= 0) return nullptr;
    for (auto& ch : children) {
        if (ch && ch->id == content_parent_id) return ch.get();
    }
    return nullptr;
}

bool Popover::has_content_slot() const {
    if (content_parent_id <= 0) return false;
    for (const auto& ch : children) {
        if (ch && ch->id == content_parent_id) {
            for (const auto& item : ch->children) {
                if (item && item->visible) return true;
            }
        }
    }
    return false;
}
