#include "element_panel.h"
#include "render_context.h"
#include <cmath>

#define ROUNDED(r, rx, ry) D2D1_ROUNDED_RECT{ (r), (rx), (ry) }

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

void Panel::layout(const Rect& available) {
    bounds = available;
    Rect content = content_rect();
    for (auto& ch : children) {
        if (ch->visible) {
            if (auto* panel = dynamic_cast<Panel*>(ch.get())) {
                if (panel->fill_parent) {
                    panel->layout(content);
                    continue;
                }
            }
            Rect child_bounds = current_scaled_bounds(ch.get());
            if (layout_children_in_content) {
                child_bounds.x += content.x;
                child_bounds.y += content.y;
            }
            ch->layout(child_bounds);
        }
    }
}

void Panel::set_layout_options(bool fill, bool content_layout) {
    fill_parent = fill;
    layout_children_in_content = content_layout;
    invalidate();
}
