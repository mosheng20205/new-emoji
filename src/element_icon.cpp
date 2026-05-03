#include "element_icon.h"

Icon::Icon() {
    horizontal_align = 1;
    vertical_align = 1;
    wrap = false;
    ellipsis = false;
}

Color Icon::text_color(const Theme* theme) const {
    return style.fg_color ? style.fg_color : theme->accent;
}
