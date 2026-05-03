#pragma once
#include "element_base.h"

class Divider : public Element {
public:
    int direction = 0; // 0 horizontal, 1 vertical
    int content_position = 1; // 0 left/top, 1 center, 2 right/bottom
    float line_width = 1.0f;
    bool dashed = false;
    int line_margin = 0;
    int text_gap = 8;

    const wchar_t* type_name() const override { return L"Divider"; }
    void paint(RenderContext& ctx) override;

    void set_direction(int value);
    void set_content_position(int value);
    void set_options(int new_direction, int position, Color color, float width, int dash, const std::wstring& label);
    void get_options(int& out_direction, int& position, Color& color, float& width, int& dash) const;
    void set_spacing(int margin, int gap);
    void get_spacing(int& margin, int& gap) const;
};
