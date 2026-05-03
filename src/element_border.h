#pragma once
#include "element_panel.h"

class Border : public Panel {
public:
    int sides = 15; // 1 top, 2 right, 4 bottom, 8 left
    std::wstring title;
    bool dashed = false;

    const wchar_t* type_name() const override { return L"Border"; }
    void paint(RenderContext& ctx) override;
    void set_options(int side_mask, Color color, float width, float radius, const std::wstring& new_title);
    void get_options(int& side_mask, Color& color, float& width, float& radius) const;
    void set_dashed(bool value);
};
