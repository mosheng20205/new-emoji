#pragma once
#include "element_base.h"

class Watermark : public Element {
public:
    std::wstring content;
    int gap_x = 150;
    int gap_y = 92;
    float rotation = -18.0f;
    unsigned alpha = 0;
    int container_id = 0;
    bool overlay = true;
    bool pass_through = true;
    int z_index = 0;
    int tile_count_x = 0;
    int tile_count_y = 0;

    const wchar_t* type_name() const override { return L"Watermark"; }
    void paint(RenderContext& ctx) override;

    void set_content(const std::wstring& value);
    void set_gap(int x, int y);
    void set_options(int x, int y, int rotation_degrees, int alpha_value);
    void set_layer_options(int target_container_id, int overlay_enabled, int pointer_passthrough, int layer_z_index);
};
