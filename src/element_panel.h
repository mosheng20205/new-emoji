#pragma once
#include "element_base.h"

class Panel : public Element {
public:
    bool fill_parent = false;  // If true, fills parent's content rect
    bool layout_children_in_content = false;

    const wchar_t* type_name() const override { return L"Panel"; }
    void layout(const Rect& available) override;
    void set_layout_options(bool fill, bool content_layout);
    // paint uses base Element::paint() with transform
};
