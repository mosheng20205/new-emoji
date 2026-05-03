#pragma once
#include "element_base.h"

class Badge : public Element {
public:
    std::wstring value;
    int max_value = 99;
    bool dot = false;
    bool hidden = false;
    bool show_zero = true;
    int offset_x = 0;
    int offset_y = 0;
    int placement = 0;
    bool standalone = false;

    const wchar_t* type_name() const override { return L"Badge"; }
    void paint(RenderContext& ctx) override;

    void set_value(const std::wstring& value_text);
    void set_max_value(int value);
    void set_dot(bool value);
    void set_options(bool dot_value, bool show_zero_value, int offset_x_value, int offset_y_value);
    void set_layout_options(int placement_value, bool standalone_value);
    bool is_hidden() const;

private:
    std::wstring display_value() const;
    Rect badge_rect(const std::wstring& badge_text) const;
};
