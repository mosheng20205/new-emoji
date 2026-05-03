#pragma once
#include "element_base.h"
#include "theme.h"

class Text : public Element {
public:
    Text() { mouse_passthrough = true; }
    int horizontal_align = 0; // 0 left, 1 center, 2 right
    int vertical_align = 0;   // 0 top, 1 center, 2 bottom
    bool wrap = true;
    bool ellipsis = false;

    const wchar_t* type_name() const override { return L"Text"; }
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override { return nullptr; }

    void set_options(int align, int valign, int wrap_text, int ellipsis_text);

protected:
    virtual Color text_color(const Theme* theme) const;
    virtual float font_scale() const { return 1.0f; }
    virtual bool underline() const { return false; }
    virtual float rotation_degrees() const { return 0.0f; }
};
