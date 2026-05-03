#include "element_layout.h"
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

void Layout::layout(const Rect& available) {
    bounds = available;
    Rect content = content_rect();
    int visible_count = 0;
    int fixed_main = 0;
    int total_weight = 0;
    if (!wrap_items) {
        for (auto& ch : children) {
            if (!ch->visible) continue;
            visible_count++;
            int weight = get_child_weight(ch->id);
            if (weight > 0) total_weight += weight;
            else {
                Rect source = current_scaled_bounds(ch.get());
                fixed_main += orientation == Horizontal ? source.w : source.h;
            }
        }
    }
    int available_main = orientation == Horizontal ? content.w : content.h;
    int gap_total = visible_count > 1 ? gap * (visible_count - 1) : 0;
    int remaining_main = (std::max)(0, available_main - fixed_main - gap_total);
    int remaining_weight = total_weight;
    int remaining_weight_main = remaining_main;
    int cursor = (orientation == Horizontal) ? content.x : content.y;
    int line_cursor = (orientation == Horizontal) ? content.y : content.x;
    int line_extent = 0;

    for (auto& ch : children) {
        if (!ch->visible) continue;

        Rect r = current_scaled_bounds(ch.get());
        int weight = !wrap_items ? get_child_weight(ch->id) : 0;
        if (weight > 0 && total_weight > 0) {
            int weighted = 0;
            if (remaining_weight <= weight) {
                weighted = remaining_weight_main;
            } else {
                weighted = (int)std::lround((double)remaining_weight_main * (double)weight / (double)remaining_weight);
            }
            remaining_weight_main -= weighted;
            remaining_weight -= weight;
            if (orientation == Horizontal) r.w = (std::max)(0, weighted);
            else r.h = (std::max)(0, weighted);
        }
        if (orientation == Horizontal) {
            if (wrap_items && cursor > content.x && cursor + r.w > content.x + content.w) {
                cursor = content.x;
                line_cursor += line_extent + gap;
                line_extent = 0;
            }
            r.x = cursor;
            r.y = line_cursor;
            if (stretch_cross_axis) {
                r.h = wrap_items && line_extent > 0 ? line_extent : content.h;
            } else if (cross_align == 1) {
                r.y += (std::max)(0, content.h - r.h) / 2;
            } else if (cross_align == 2) {
                r.y += (std::max)(0, content.h - r.h);
            }
            cursor += r.w + gap;
            line_extent = (std::max)(line_extent, r.h);
        } else {
            if (wrap_items && cursor > content.y && cursor + r.h > content.y + content.h) {
                cursor = content.y;
                line_cursor += line_extent + gap;
                line_extent = 0;
            }
            r.x = content.x;
            r.y = cursor;
            if (stretch_cross_axis) {
                r.w = wrap_items && line_extent > 0 ? line_extent : content.w;
            } else if (cross_align == 1) {
                r.x += (std::max)(0, content.w - r.w) / 2;
            } else if (cross_align == 2) {
                r.x += (std::max)(0, content.w - r.w);
            }
            cursor += r.h + gap;
            line_extent = (std::max)(line_extent, r.w);
        }

        ch->layout(r);
    }
}

void Layout::set_options(int new_orientation, int new_gap, int stretch, int align, int wrap) {
    orientation = new_orientation == 1 ? Vertical : Horizontal;
    set_logical_gap((std::max)(0, new_gap));
    stretch_cross_axis = stretch != 0;
    cross_align = (std::max)(0, (std::min)(2, align));
    wrap_items = wrap != 0;
    invalidate();
}

void Layout::set_child_weight(int child_id, int weight) {
    if (weight <= 0) child_weights.erase(child_id);
    else child_weights[child_id] = weight;
    invalidate();
}

int Layout::get_child_weight(int child_id) const {
    auto it = child_weights.find(child_id);
    return it == child_weights.end() ? 0 : it->second;
}

void Layout::apply_dpi_scale(float scale) {
    Panel::apply_dpi_scale(scale);
    gap = (int)std::lround((float)logical_gap * scale);
}
