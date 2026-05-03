#pragma once
#include "element_base.h"
#include <vector>

struct TourStep {
    std::wstring title;
    std::wstring body;
};

class Tour : public Element {
public:
    std::vector<TourStep> steps;
    int active_index = 0;
    bool open = true;
    bool mask = true;
    Rect target_rect;
    bool has_target = false;
    int target_element_id = 0;
    bool mask_passthrough = false;
    bool close_on_mask = true;
    int last_action = 0;
    int change_count = 0;

    const wchar_t* type_name() const override { return L"Tour"; }
    void paint(RenderContext& ctx) override;
    Element* hit_test(int x, int y) override;
    void on_mouse_down(int x, int y, MouseButton btn) override;
    void on_mouse_up(int x, int y, MouseButton btn) override;
    void on_key_down(int vk, int mods) override;

    void set_steps(const std::vector<TourStep>& values);
    void set_active_index(int value);
    void set_open(bool value);
    void set_options(bool is_open, bool show_mask, int target_x, int target_y, int target_w, int target_h);
    void set_target_element(int element_id, const Rect& rect);
    void set_mask_behavior(bool passthrough, bool close_when_clicked);

private:
    enum Part {
        PartNone,
        PartPrev,
        PartNext,
        PartClose,
        PartMask
    };

    Part m_press_part = PartNone;

    Part part_at(int x, int y) const;
};
