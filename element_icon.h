#pragma once
#include "element_text.h"

class Icon : public Text {
public:
    float icon_scale = 1.25f;
    float rotation = 0.0f;

    const wchar_t* type_name() const override { return L"Icon"; }
    Icon();

protected:
    Color text_color(const Theme* theme) const override;
    float font_scale() const override { return icon_scale; }
    float rotation_degrees() const override { return rotation; }
};
