#pragma once
#include "element_panel.h"
#include <map>

class Layout : public Panel {
public:
    enum Orientation {
        Horizontal = 0,
        Vertical = 1
    };

    int orientation = Horizontal;
    int gap = 8;
    bool stretch_cross_axis = true;
    int cross_align = 0; // 0 start, 1 center, 2 end
    bool wrap_items = false;

    const wchar_t* type_name() const override { return L"Layout"; }
    void layout(const Rect& available) override;
    void apply_dpi_scale(float scale) override;
    void set_logical_gap(int value) { logical_gap = value; gap = value; }
    void set_options(int new_orientation, int new_gap, int stretch, int align, int wrap);
    int get_logical_gap() const { return logical_gap; }
    void set_child_weight(int child_id, int weight);
    int get_child_weight(int child_id) const;

private:
    int logical_gap = 8;
    std::map<int, int> child_weights;
};
