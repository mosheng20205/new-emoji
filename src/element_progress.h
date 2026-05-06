#pragma once
#include "element_base.h"
#include <utility>
#include <vector>

class Progress : public Element {
public:
    int percentage = 0;
    int status = 0;
    bool show_text = true;
    bool text_inside = false;
    int progress_type = 0;
    int stroke_width = 0;
    int text_format = 0;
    bool striped = false;
    Color fill_color = 0;
    Color track_color = 0;
    Color text_color = 0;
    std::vector<std::pair<Color, int>> color_stops;
    std::wstring complete_text = L"\u6EE1";
    std::wstring text_template;

    const wchar_t* type_name() const override { return L"Progress"; }
    void paint(RenderContext& ctx) override;

    void set_percentage(int value);
    void set_status(int value);
    void set_show_text(bool value);
    void set_text_inside(bool value);
    void set_options(int type_value, int stroke_width_value, bool show_text_value);
    void set_format_options(int text_format_value, bool striped_value);
    void set_colors(Color fill, Color track, Color text);
    void set_color_stops(const std::vector<std::pair<Color, int>>& stops);
    void set_complete_text(const std::wstring& value);
    void set_text_template(const std::wstring& value);
};
