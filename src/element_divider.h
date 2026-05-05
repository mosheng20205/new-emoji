#pragma once
#include "element_base.h"

class Divider : public Element {
public:
    int direction = 0; // 0 horizontal, 1 vertical
    int content_position = 1; // 0 left/top, 1 center, 2 right/bottom
    int line_style = 0; // 0 solid, 1 dashed, 2 dotted, 3 double
    float line_width = 1.0f;
    bool dashed = false;
    int line_margin = 0;
    int text_gap = 8;
    std::wstring content_icon;

    const wchar_t* type_name() const override { return L"Divider"; }
    void apply_dpi_scale(float scale) override;
    void paint(RenderContext& ctx) override;

    void set_direction(int value);
    void set_content_position(int value);
    void set_options(int new_direction, int position, Color color, float width, int dash, const std::wstring& label);
    void get_options(int& out_direction, int& position, Color& color, float& width, int& dash) const;
    void set_spacing(int margin, int gap);
    void get_spacing(int& margin, int& gap) const;
    void set_line_style(int value);
    void set_content(const std::wstring& icon, const std::wstring& label);
    void get_content(std::wstring& icon, std::wstring& label) const;

private:
    float logical_line_width = 1.0f;
    int logical_line_margin = 0;
    int logical_text_gap = 8;
    std::wstring display_text() const;
};
