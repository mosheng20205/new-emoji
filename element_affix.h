#pragma once
#include "element_base.h"

class Affix : public Element {
public:
    std::wstring title;
    std::wstring body;
    int offset = 0;
    int scroll_position = 0;
    int container_id = 0;
    int placeholder_height = 0;
    int fixed_z_index = 10;
    int fixed_top = 0;
    bool fixed = false;

    const wchar_t* type_name() const override { return L"Affix"; }
    void paint(RenderContext& ctx) override;
    void on_mouse_enter() override;
    void on_mouse_leave() override;

    void set_title(const std::wstring& value);
    void set_body(const std::wstring& value);
    void set_offset(int value);
    void set_state(int scroll, int offset_value);
    void set_options(int scroll, int offset_value, int target_container_id, int placeholder, int z_index);
    int is_fixed() const { return fixed ? 1 : 0; }
};
