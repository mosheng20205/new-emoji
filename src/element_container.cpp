#include "element_container.h"
#include "emoji_fallback.h"
#include "render_context.h"
#include <algorithm>
#include <cmath>

static Rect current_scaled_bounds(const Element* el) {
    if (!el || !el->has_logical_bounds) return el ? el->bounds : Rect{};
    float sx = el->logical_bounds.w != 0
        ? (float)el->bounds.w / (float)el->logical_bounds.w : 1.0f;
    float sy = el->logical_bounds.h != 0
        ? (float)el->bounds.h / (float)el->logical_bounds.h : sx;
    Rect r;
    r.x = (int)std::lround((float)el->logical_bounds.x * sx);
    r.y = (int)std::lround((float)el->logical_bounds.y * sy);
    r.w = (int)std::lround((float)el->logical_bounds.w * sx);
    r.h = (int)std::lround((float)el->logical_bounds.h * sy);
    return r;
}

static bool is_flex_child(Element* el, int direction) {
    if (dynamic_cast<Main*>(el)) return true;
    if (dynamic_cast<Container*>(el)) return true;
    Rect r = current_scaled_bounds(el);
    return direction == 1 ? r.w <= 0 : r.h <= 0;
}

static bool is_header_or_footer(Element* el) {
    return dynamic_cast<Header*>(el) || dynamic_cast<Footer*>(el);
}

void Container::layout(const Rect& available) {
    if (!flow_enabled) {
        Panel::layout(available);
        return;
    }

    bounds = available;
    Rect content = content_rect();
    int direction = flow_direction;
    if (direction == 0) {
        direction = 1;
        for (auto& ch : children) {
            if (ch->visible && is_header_or_footer(ch.get())) {
                direction = 2;
                break;
            }
        }
    }
    actual_direction = direction == 2 ? 2 : 1;

    int visible_count = 0;
    int fixed_main = 0;
    int flex_count = 0;
    for (auto& ch : children) {
        if (!ch->visible) continue;
        visible_count++;
        if (is_flex_child(ch.get(), actual_direction)) {
            flex_count++;
        } else {
            Rect r = current_scaled_bounds(ch.get());
            fixed_main += actual_direction == 1 ? r.w : r.h;
        }
    }

    int available_main = actual_direction == 1 ? content.w : content.h;
    int gap_total = visible_count > 1 ? flow_gap * (visible_count - 1) : 0;
    int remaining = (std::max)(0, available_main - fixed_main - gap_total);
    int remaining_flex = flex_count;
    int cursor = actual_direction == 1 ? content.x : content.y;

    for (auto& ch : children) {
        if (!ch->visible) continue;

        Rect r = current_scaled_bounds(ch.get());
        bool flex = is_flex_child(ch.get(), actual_direction);
        int main_size = actual_direction == 1 ? r.w : r.h;
        if (flex) {
            if (remaining_flex <= 1) {
                main_size = remaining;
            } else {
                main_size = remaining / remaining_flex;
            }
            remaining -= main_size;
            remaining_flex--;
        }

        if (actual_direction == 1) {
            r.x = cursor;
            r.y = content.y;
            r.w = (std::max)(0, main_size);
            r.h = content.h;
            cursor += r.w + flow_gap;
        } else {
            r.x = content.x;
            r.y = cursor;
            r.w = content.w;
            r.h = (std::max)(0, main_size);
            cursor += r.h + flow_gap;
        }
        ch->layout(r);
    }
}

void Container::set_flow_options(int enabled, int direction, int gap) {
    flow_enabled = enabled != 0 ? 1 : 0;
    flow_direction = (std::max)(0, (std::min)(2, direction));
    logical_flow_gap = (std::max)(0, gap);
    flow_gap = logical_flow_gap;
    actual_direction = flow_enabled ? actual_direction : 0;
    invalidate();
}

void Container::apply_dpi_scale(float scale) {
    Panel::apply_dpi_scale(scale);
    flow_gap = (int)std::lround((float)logical_flow_gap * scale);
}

ContainerRegion::ContainerRegion(int role) {
    region_role = role;
    fill_parent = false;
    layout_children_in_content = true;
    style.fg_color = 0xFF333333;
    style.pad_left = 0;
    style.pad_top = 0;
    style.pad_right = 0;
    style.pad_bottom = 0;

    if (role == HeaderRole || role == FooterRole) style.bg_color = 0xFFB3C0D1;
    else if (role == AsideRole) style.bg_color = 0xFFD3DCE6;
    else style.bg_color = 0xFFE9EEF3;
}

void ContainerRegion::set_text_options(int align, int valign) {
    horizontal_align = (std::max)(0, (std::min)(2, align));
    vertical_align = (std::max)(0, (std::min)(2, valign));
    invalidate();
}

void ContainerRegion::paint(RenderContext& ctx) {
    if (!visible || bounds.w <= 0 || bounds.h <= 0) return;

    D2D1_MATRIX_3X2_F saved;
    ctx.rt->GetTransform(&saved);
    ctx.rt->SetTransform(saved * D2D1::Matrix3x2F::Translation(
        (float)bounds.x, (float)bounds.y));

    D2D1_RECT_F clip = { 0, 0, (float)bounds.w, (float)bounds.h };
    ctx.push_clip(clip);

    D2D1_RECT_F rect = { 0, 0, (float)bounds.w, (float)bounds.h };
    if (style.bg_color != 0) {
        auto* br = ctx.get_brush(style.bg_color);
        if (style.corner_radius > 0) {
            ctx.rt->FillRoundedRectangle(
                D2D1::RoundedRect(rect, style.corner_radius, style.corner_radius), br);
        } else {
            ctx.rt->FillRectangle(rect, br);
        }
    }

    if (!text.empty()) {
        float x = (float)style.pad_left;
        float y = (float)style.pad_top;
        float w = (float)(bounds.w - style.pad_left - style.pad_right);
        float h = (float)(bounds.h - style.pad_top - style.pad_bottom);
        if (w < 1.0f) w = 1.0f;
        if (h < 1.0f) h = 1.0f;

        auto* layout = ctx.create_text_layout(text, style.font_name, style.font_size, w, h);
        if (layout) {
            apply_emoji_font_fallback(layout, text);
            DWRITE_TEXT_ALIGNMENT text_align = DWRITE_TEXT_ALIGNMENT_LEADING;
            if (horizontal_align == 1) text_align = DWRITE_TEXT_ALIGNMENT_CENTER;
            if (horizontal_align == 2) text_align = DWRITE_TEXT_ALIGNMENT_TRAILING;
            DWRITE_PARAGRAPH_ALIGNMENT para_align = DWRITE_PARAGRAPH_ALIGNMENT_NEAR;
            if (vertical_align == 1) para_align = DWRITE_PARAGRAPH_ALIGNMENT_CENTER;
            if (vertical_align == 2) para_align = DWRITE_PARAGRAPH_ALIGNMENT_FAR;
            layout->SetTextAlignment(text_align);
            layout->SetParagraphAlignment(para_align);
            ctx.rt->DrawTextLayout(D2D1::Point2F(x, y), layout,
                ctx.get_brush(style.fg_color), D2D1_DRAW_TEXT_OPTIONS_ENABLE_COLOR_FONT);
            layout->Release();
        }
    }

    for (auto& ch : children) {
        if (ch->visible) ch->paint(ctx);
    }

    if (style.border_width > 0 && style.border_color != 0) {
        auto* br = ctx.get_brush(style.border_color);
        float hw = style.border_width * 0.5f;
        D2D1_RECT_F border_rect = { hw, hw, (float)bounds.w - hw, (float)bounds.h - hw };
        if (style.corner_radius > 0) {
            ctx.rt->DrawRoundedRectangle(
                D2D1::RoundedRect(border_rect, style.corner_radius, style.corner_radius), br, style.border_width);
        } else {
            ctx.rt->DrawRectangle(border_rect, br, style.border_width);
        }
    }

    ctx.pop_clip();
    ctx.rt->SetTransform(saved);
}
