#pragma once
#include "element_base.h"

class Progress : public Element {
public:
    int percentage = 0;
    int status = 0;
    bool show_text = true;
    int progress_type = 0;
    int stroke_width = 0;
    int text_format = 0;
    bool striped = false;

    const wchar_t* type_name() const override { return L"Progress"; }
    void paint(RenderContext& ctx) override;

    void set_percentage(int value);
    void set_status(int value);
    void set_show_text(bool value);
    void set_options(int type_value, int stroke_width_value, bool show_text_value);
    void set_format_options(int text_format_value, bool striped_value);
};
