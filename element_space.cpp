#include "element_space.h"

void Space::set_size(int w, int h) {
    if (w < 0) w = 0;
    if (h < 0) h = 0;
    set_logical_bounds({ logical_bounds.x, logical_bounds.y, w, h });
    invalidate();
}

void Space::get_size(int& w, int& h) const {
    const Rect& r = has_logical_bounds ? logical_bounds : bounds;
    w = r.w;
    h = r.h;
}
